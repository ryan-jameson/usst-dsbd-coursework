from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, deque
from dataclasses import asdict
from pathlib import Path

import cv2
import supervision as sv
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pc_host"))
sys.path.insert(0, str(ROOT / "基于机器视觉的运动场景识别" / "基于机器视觉的运动场景识别" / "基于机器视觉的运动场景识别" / "code"))

from commentary_event_selector import CommentaryObservation, FiveSecondCommentarySelector
from football_host import make_event
from football_offline_assets import ANNOTATED_VIDEO, OFFLINE_DEMO_DIR, REPORT_FILE, SOURCE_VIDEO, TIMELINE_FILE
from football_video_runner import BALL_ID, PLAYER_ID, REFEREE_ID, draw_radar, extract_pitch_points, make_features
from tactical_classification import TacticalClassifier


def draw_tracking(frame, detections: sv.Detections) -> None:
    for xyxy, class_id, track_id in zip(detections.xyxy, detections.class_id, detections.tracker_id):
        x1, y1, x2, y2 = map(int, xyxy)
        color = (0, 255, 255) if class_id == BALL_ID else (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"id {track_id}", (x1, max(15, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, .45, color, 1)


def extract_ball_center(detections: sv.Detections) -> tuple[int, int]:
    if len(detections) == 0:
        return -1, -1
    box = detections.xyxy[0]
    return int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2)


def process(args: argparse.Namespace) -> int:
    video = cv2.VideoCapture(str(args.source))
    if not video.isOpened():
        raise RuntimeError(f"cannot open source video: {args.source}")
    fps = video.get(cv2.CAP_PROP_FPS) or 30.0
    width, height = int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(1, int(round(fps)))
    output = args.annotated.with_suffix(".tmp.mp4")
    output.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError(f"cannot open output video: {output}")

    player_model, ball_model, pitch_model = YOLO(args.player_weights), YOLO(args.ball_weights), YOLO(args.pitch_weights)
    classifier = TacticalClassifier(args.tactical_model)
    tracker = sv.ByteTrack(minimum_consecutive_frames=3)
    history: deque[list[list[float]]] = deque(maxlen=16)
    selector = FiveSecondCommentarySelector()
    latest_detections = sv.Detections.empty()
    latest_ball_box = None
    latest_points: list[tuple[int, int]] = []
    latest_event = "new_match"
    previous_ball_x: int | None = None
    timeline = [make_event(1, 0, "new_match", "home", 0.90, 2, -1, -1)]
    event_counts: Counter[str] = Counter({"new_match": 1})
    frame_no = 0
    try:
        while True:
            ok, frame = video.read()
            if not ok:
                break
            frame_no += 1
            if frame_no % frame_interval == 0:
                player = sv.Detections.from_ultralytics(player_model(frame, imgsz=1280, verbose=False)[0])
                ball = sv.Detections.from_ultralytics(ball_model(frame, imgsz=640, verbose=False)[0])
                latest_ball_box = ball.xyxy[0].copy() if len(ball) > 0 else None
                latest_detections = tracker.update_with_detections(sv.Detections.merge([player, ball]))
                history.append(make_features(latest_detections, width, height))
                tactic, confidence = "阵地防守", 0.50
                if len(history) == 16:
                    result = classifier.predict(list(history))
                    tactic = result["tactical_class"]
                    confidence = max(result["probabilities"].values())
                bx, by = extract_ball_center(ball)
                ball_dx = 0.0 if bx < 0 or previous_ball_x is None else float(bx - previous_ball_x)
                if bx >= 0:
                    previous_ball_x = bx
                selector.observe(CommentaryObservation(tactic, confidence, bx, by, width, height, ball_dx))
                if frame_no % (frame_interval * 5) == 0 and frame_no < total_frames:
                    decision = selector.decide()
                    latest_event = decision.event
                    message_id = len(timeline) + 1
                    timestamp = int(frame_no / fps * 1000)
                    timeline.append(make_event(message_id, timestamp, decision.event, "home", decision.confidence,
                                               decision.danger, decision.ball_x, decision.ball_y))
                    event_counts[decision.event] += 1
                if frame_no % (frame_interval * 5) == 0:
                    keypoints = pitch_model(frame, verbose=False)[0]
                    raw_points = None
                    if keypoints.keypoints is not None and len(keypoints.keypoints.xy) > 0:
                        raw_points = keypoints.keypoints.xy[0].cpu().numpy()
                    latest_points = extract_pitch_points(raw_points)

            overlay = frame.copy()
            if len(latest_detections) > 0:
                draw_tracking(overlay, latest_detections)
                draw_radar(overlay, latest_detections)
            if latest_ball_box is not None:
                x1, y1, x2, y2 = map(int, latest_ball_box)
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 255), 2)
                cv2.putText(overlay, "ball", (x1, max(15, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, .45, (0, 255, 255), 1)
            for point in latest_points:
                cv2.circle(overlay, point, 3, (255, 0, 255), -1)
            cv2.putText(overlay, "Football Companion Offline Analysis", (12, 30), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 255, 0), 2)
            cv2.putText(overlay, f"Event: {latest_event}", (12, 58), cv2.FONT_HERSHEY_SIMPLEX, .65, (0, 230, 255), 2)
            writer.write(overlay)
            if frame_no % 150 == 0:
                print(f"[offline] rendered {frame_no}/{total_frames} event={latest_event}", flush=True)
    finally:
        writer.release()
        video.release()

    if len(timeline) != 12:
        raise RuntimeError(f"expected 12 events, got {len(timeline)}")
    output.replace(args.annotated)
    args.timeline.write_text(json.dumps({"timeline_version": 1, "source_video": args.source.name,
                                         "events": [asdict(event) for event in timeline]}, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report.write_text(json.dumps({"source_video": str(args.source), "total_frames": total_frames, "fps": fps,
                                       "analysis_frame_interval": frame_interval, "event_counts": dict(event_counts)}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[offline] wrote {args.annotated}", flush=True)
    print(f"[offline] wrote {args.timeline}", flush=True)
    return 0


def main() -> int:
    data = ROOT / "pc_host" / "third_party" / "roboflow_sports" / "examples" / "soccer" / "data"
    model = ROOT / "基于机器视觉的运动场景识别" / "基于机器视觉的运动场景识别" / "outputs" / "tactical_classifier_calibrated.pt"
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE_VIDEO)
    parser.add_argument("--annotated", type=Path, default=ANNOTATED_VIDEO)
    parser.add_argument("--timeline", type=Path, default=TIMELINE_FILE)
    parser.add_argument("--report", type=Path, default=REPORT_FILE)
    parser.add_argument("--player-weights", type=Path, default=data / "football-player-detection.pt")
    parser.add_argument("--ball-weights", type=Path, default=data / "football-ball-detection.pt")
    parser.add_argument("--pitch-weights", type=Path, default=data / "football-pitch-detection.pt")
    parser.add_argument("--tactical-model", type=Path, default=model)
    return process(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())

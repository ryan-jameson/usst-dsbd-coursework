from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
import supervision as sv
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pc_host"))
sys.path.insert(0, str(ROOT / "基于机器视觉的运动场景识别" / "基于机器视觉的运动场景识别" / "基于机器视觉的运动场景识别" / "code"))

from football_host import UsbSerialTransport, make_event
from tactical_classification import TacticalClassifier
from commentary_event_selector import CommentaryObservation, FiveSecondCommentarySelector


PLAYER_ID, GOALKEEPER_ID, BALL_ID, REFEREE_ID = 2, 1, 0, 3


def extract_pitch_points(raw_points: np.ndarray | None) -> list[tuple[int, int]]:
    if raw_points is None:
        return []
    return [(int(x), int(y)) for x, y in raw_points if x > 1 and y > 1]


def atomic_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.stem + ".tmp" + path.suffix)
    if not cv2.imwrite(str(temporary), image):
        raise RuntimeError(f"cannot write {temporary}")
    os.replace(temporary, path)


def make_features(detections: sv.Detections, width: int, height: int) -> list[list[float]]:
    nodes: list[list[float]] = []
    for xyxy, class_id, confidence in zip(detections.xyxy, detections.class_id, detections.confidence):
        x1, y1, x2, y2 = xyxy
        nodes.append([((x1 + x2) / 2) / width, ((y1 + y2) / 2) / height,
                      (x2 - x1) / width, (y2 - y1) / height,
                      float(class_id), float(confidence)])
    return (nodes + [[0.0] * 6 for _ in range(23)])[:23]


def draw_radar(frame: np.ndarray, detections: sv.Detections) -> None:
    h, w = frame.shape[:2]
    radar = np.full((h // 3, w // 3, 3), (37, 116, 64), dtype=np.uint8)
    cv2.rectangle(radar, (3, 3), (radar.shape[1] - 4, radar.shape[0] - 4), (255, 255, 255), 1)
    cv2.line(radar, (radar.shape[1] // 2, 3), (radar.shape[1] // 2, radar.shape[0] - 4), (255, 255, 255), 1)
    for xyxy, class_id in zip(detections.xyxy, detections.class_id):
        if class_id not in (PLAYER_ID, GOALKEEPER_ID, REFEREE_ID):
            continue
        x = int(((xyxy[0] + xyxy[2]) / 2) / w * (radar.shape[1] - 8)) + 4
        y = int(((xyxy[1] + xyxy[3]) / 2) / h * (radar.shape[0] - 8)) + 4
        color = (255, 80, 80) if class_id == REFEREE_ID else (80, 220, 255)
        cv2.circle(radar, (x, y), 4, color, -1)
    frame[h-radar.shape[0]-8:h-8, w-radar.shape[1]-8:w-8] = radar


def run(args: argparse.Namespace) -> int:
    video = cv2.VideoCapture(args.video)
    if not video.isOpened():
        raise RuntimeError(f"cannot open video: {args.video}")
    fps = video.get(cv2.CAP_PROP_FPS) or 30.0
    player_model, ball_model, pitch_model = YOLO(args.player_weights), YOLO(args.ball_weights), YOLO(args.pitch_weights)
    classifier = TacticalClassifier(args.tactical_model)
    tracker = sv.ByteTrack(minimum_consecutive_frames=3)
    history: deque[list[list[float]]] = deque(maxlen=16)
    selector = FiveSecondCommentarySelector()
    transport = None if args.dry_run else UsbSerialTransport(args.usb)
    preview = Path(args.preview_dir)
    frame_no = sent = 0
    last_dispatch_ms = -5000
    announced_match = False
    previous_ball_x: int | None = None
    selected_event = "waiting"
    try:
        while True:
            ok, frame = video.read()
            if not ok:
                break
            frame_no += 1
            # Product demo mode: analyze one frame per second; M55 receives the
            # stabilized tactical state every five seconds through EventGate.
            if frame_no % 30:
                continue
            player = sv.Detections.from_ultralytics(player_model(frame, imgsz=1280, verbose=False)[0])
            ball = sv.Detections.from_ultralytics(ball_model(frame, imgsz=640, verbose=False)[0])
            detections = sv.Detections.merge([player, ball])
            detections = tracker.update_with_detections(detections)
            h, w = frame.shape[:2]
            history.append(make_features(detections, w, h))
            tactic, confidence = "阵地防守", 0.5
            if len(history) == 16:
                result = classifier.predict(list(history))
                tactic = result["tactical_class"]
                confidence = max(result["probabilities"].values())
            overlay = frame.copy()
            for xyxy, class_id, track_id in zip(detections.xyxy, detections.class_id, detections.tracker_id):
                x1, y1, x2, y2 = map(int, xyxy)
                color = (0, 255, 255) if class_id == BALL_ID else (0, 255, 0)
                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
                cv2.putText(overlay, f"id {track_id}", (x1, max(15, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, .45, color, 1)
            if frame_no % 150 == 0:
                keypoints = pitch_model(frame, verbose=False)[0]
                raw_points = None
                if keypoints.keypoints is not None and len(keypoints.keypoints.xy) > 0:
                    raw_points = keypoints.keypoints.xy[0].cpu().numpy()
                for point in extract_pitch_points(raw_points):
                    cv2.circle(overlay, point, 3, (255, 0, 255), -1)
            draw_radar(overlay, detections)
            cv2.putText(overlay, "Football tactical analysis", (12, 30), cv2.FONT_HERSHEY_SIMPLEX, .7, (0, 255, 0), 2)
            ball_xy = next((box for box, cid in zip(detections.xyxy, detections.class_id) if cid == BALL_ID), None)
            bx, by = (-1, -1) if ball_xy is None else (int((ball_xy[0]+ball_xy[2])/2), int((ball_xy[1]+ball_xy[3])/2))
            ball_dx = 0.0 if bx < 0 or previous_ball_x is None else float(bx - previous_ball_x)
            if bx >= 0:
                previous_ball_x = bx
            selector.observe(CommentaryObservation(tactic, confidence, bx, by, w, h, ball_dx))
            now_ms = int(frame_no / fps * 1000)
            if now_ms - last_dispatch_ms >= 5000:
                sent += 1
                if not announced_match:
                    outgoing = make_event(sent, now_ms, "new_match", "home", 0.90, 4, bx, by)
                    announced_match = True
                    selector.decide()
                else:
                    decision = selector.decide()
                    outgoing = make_event(sent, now_ms, decision.event, "home", decision.confidence,
                                          decision.danger, decision.ball_x, decision.ball_y)
                if transport:
                    transport.send_event(outgoing)
                selected_event = outgoing.event
                last_dispatch_ms = now_ms
            cv2.putText(overlay, f"Event: {selected_event}", (12, 58), cv2.FONT_HERSHEY_SIMPLEX, .65, (0, 230, 255), 2)
            atomic_image(preview / "latest_source.jpg", frame)
            atomic_image(preview / "latest_overlay.jpg", overlay)
            print("@vision-status " + json.dumps({"frame": frame_no, "total_frames": 1800, "source": "", "overlay": "", "tactic": tactic, "event": selected_event, "events_sent": sent, "acks": sent}, ensure_ascii=False), flush=True)
    finally:
        video.release()
        if transport:
            transport.close()
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True); p.add_argument("--player-weights", required=True); p.add_argument("--ball-weights", required=True); p.add_argument("--pitch-weights", required=True); p.add_argument("--tactical-model", required=True); p.add_argument("--preview-dir", required=True); p.add_argument("--usb", default="COM10"); p.add_argument("--dry-run", action="store_true")
    return run(p.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())

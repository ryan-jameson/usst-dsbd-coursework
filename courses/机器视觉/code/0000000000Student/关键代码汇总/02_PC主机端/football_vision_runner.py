from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VISION_CODE = ROOT / "基于机器视觉的运动场景识别" / "基于机器视觉的运动场景识别" / "基于机器视觉的运动场景识别" / "code"
sys.path.insert(0, str(VISION_CODE))
sys.path.insert(0, str(ROOT / "pc_host"))
sys.path.insert(0, str(ROOT / "tools"))

from football_host import UsbSerialTransport, make_event

from vision_event_mapper import EventGate, EventMapper


COCO_TO_FOOTBALL = {
    0: "player",
    32: "ball",
}

PLAYER_COLORS = {
    "home": (0, 0, 255),
    "away": (255, 0, 0),
    "unknown": (128, 128, 128),
}


class FootballDetectorCOCO:
    def __init__(self, model_path: str, conf: float = 0.25, iou: float = 0.5):
        from ultralytics import YOLO
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"model not found: {model_path}")
        self.model = YOLO(model_path)
        self.conf = conf
        self.iou = iou

    def detect(self, image):
        results = self.model(image, conf=self.conf, iou=self.iou, verbose=False)
        detections = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                cls = int(box.cls[0].item())
                if cls not in COCO_TO_FOOTBALL:
                    continue
                conf = float(box.conf[0].item())
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                x1, y1, x2, y2 = map(int, xyxy)
                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "class": COCO_TO_FOOTBALL[cls],
                    "class_id": cls,
                    "confidence": conf,
                    "center": [(x1 + x2) // 2, (y1 + y2) // 2],
                })
        return detections

    def draw(self, image, detections):
        import cv2
        vis = image.copy()
        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            if d["class"] == "ball":
                color = (255, 255, 0)
            else:
                color = (0, 255, 0)
            cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
            label = f"{d['class']}: {d['confidence']:.2f}"
            cv2.putText(vis, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return vis


class FootballTrackerLight:
    def __init__(self, max_age: int = 5, iou_threshold: float = 0.3):
        self.tracks: dict = {}
        self.next_id = 0
        self.max_age = max_age
        self.iou_threshold = iou_threshold
        self._prev_dets: list[dict] = []

    def _iou(self, a, b):
        x1 = max(a[0], b[0]); y1 = max(a[1], b[1])
        x2 = min(a[2], b[2]); y2 = min(a[3], b[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        area_b = (b[2] - b[0]) * (b[3] - b[1])
        union = area_a + area_b - inter
        return inter / union if union > 0 else 0

    def update(self, detections: list[dict]) -> list[dict]:
        for tid in list(self.tracks.keys()):
            self.tracks[tid]["age"] += 1
            if self.tracks[tid]["age"] > self.max_age:
                del self.tracks[tid]

        if not detections:
            return list(self.tracks.values())

        if not self.tracks:
            for d in detections:
                tid = self.next_id
                self.next_id += 1
                self.tracks[tid] = {
                    "id": tid, "bbox": d["bbox"], "class": d["class"],
                    "center": d["center"], "confidence": d["confidence"],
                    "age": 0, "trail": [(d["center"][0], d["center"][1])],
                }
            return list(self.tracks.values())

        track_ids = list(self.tracks.keys())
        n = len(track_ids)
        m = len(detections)
        import numpy as np
        iou_matrix = np.zeros((n, m))
        for i, tid in enumerate(track_ids):
            for j, d in enumerate(detections):
                iou_matrix[i, j] = self._iou(self.tracks[tid]["bbox"], d["bbox"])

        from scipy.optimize import linear_sum_assignment
        matched: set = set()
        row_idx, col_idx = linear_sum_assignment(-iou_matrix)
        for r, c in zip(row_idx, col_idx):
            if iou_matrix[r, c] > self.iou_threshold:
                tid = track_ids[r]
                d = detections[c]
                self.tracks[tid]["bbox"] = d["bbox"]
                self.tracks[tid]["center"] = d["center"]
                self.tracks[tid]["confidence"] = d["confidence"]
                self.tracks[tid]["class"] = d["class"]
                self.tracks[tid]["age"] = 0
                self.tracks[tid]["trail"].append((d["center"][0], d["center"][1]))
                if len(self.tracks[tid]["trail"]) > 30:
                    self.tracks[tid]["trail"] = self.tracks[tid]["trail"][-30:]
                matched.add(c)

        for j, d in enumerate(detections):
            if j not in matched:
                tid = self.next_id
                self.next_id += 1
                self.tracks[tid] = {
                    "id": tid, "bbox": d["bbox"], "class": d["class"],
                    "center": d["center"], "confidence": d["confidence"],
                    "age": 0, "trail": [(d["center"][0], d["center"][1])],
                }

        return list(self.tracks.values())


class VisionRunner:
    def __init__(
        self,
        images_dir: str,
        detector_weights: str,
        usb_port: str = "",
        fps: int = 5,
        dry_run: bool = False,
        save_overlay: str | None = None,
        preview_dir: str | None = None,
        max_frames: int = 0,
    ) -> None:
        import cv2  # noqa
        self.images_dir = Path(images_dir)
        if not self.images_dir.is_dir():
            raise FileNotFoundError(f"images directory not found: {images_dir}")
        self.jpg_files = sorted(
            [f for f in self.images_dir.iterdir() if f.suffix.lower() == ".jpg"]
        )
        if not self.jpg_files:
            raise FileNotFoundError(f"no JPG files in {images_dir}")

        self.detector_weights = detector_weights
        self.usb_port = usb_port
        self.fps = max(1, min(10, fps))
        self.dry_run = dry_run
        self.save_overlay = Path(save_overlay) if save_overlay else None
        self.preview_dir = Path(preview_dir) if preview_dir else None
        self.max_frames = max_frames

        self._transport: UsbSerialTransport | None = None
        self._event_gate = EventGate()
        self._event_mapper = EventMapper()
        self._message_id = 0
        self._sent_count = 0
        self._ack_count = 0

        if self.save_overlay:
            self.save_overlay.mkdir(parents=True, exist_ok=True)
        if self.preview_dir:
            self.preview_dir.mkdir(parents=True, exist_ok=True)

        self._detector = FootballDetectorCOCO(model_path=self.detector_weights)
        self._tracker = FootballTrackerLight()
        print(f"[vision] COCO detector loaded: {self.detector_weights}")
        print(f"[vision] images: {len(self.jpg_files)} JPGs, mode=rule")

    def _infer_team(self, detections: list[dict], image_width: int) -> str:
        players = [d for d in detections if d["class"] == "player"]
        if not players:
            return "unknown"
        mid = image_width // 2
        left = sum(1 for p in players if p["center"][0] < mid)
        right = len(players) - left
        if left > right * 1.2:
            return "home"
        if right > left * 1.2:
            return "away"
        return "unknown"

    def _rule_classify(self, tracks: list[dict], image_shape) -> dict:
        h, w = image_shape[:2]
        mid_x = w // 2
        mid_y = h // 2

        players = [t for t in tracks if t["class"] == "player"]
        ball = next((t for t in tracks if t["class"] == "ball"), None)

        if not players:
            return {"tactical_class": "阵地防守", "method": "rule", "probabilities": {"rule": 0.85}}

        left_players = [p for p in players if p["center"][0] < mid_x]
        right_players = [p for p in players if p["center"][0] >= mid_x]

        right_invasion = sum(1 for p in left_players if p["center"][0] > mid_x * 0.8)
        left_invasion = sum(1 for p in right_players if p["center"][0] < mid_x * 1.2)

        total_invaders = right_invasion + left_invasion
        active_half_ratio = total_invaders / len(players) if players else 0

        if ball:
            bx, by = ball["center"]
            nearby_players = sum(
                1 for p in players
                if abs(p["center"][0] - bx) < 80 and abs(p["center"][1] - by) < 80
            )
            ball_in_defensive = bx < mid_x * 0.3 or bx > mid_x * 1.7
            ball_stationary = (
                len(ball.get("trail", [])) >= 3
                and abs(ball["trail"][-1][0] - ball["trail"][-3][0]) < 10
                and abs(ball["trail"][-1][1] - ball["trail"][-3][1]) < 10
            )
            if ball_stationary and nearby_players >= 3:
                return {"tactical_class": "定位球", "method": "rule", "probabilities": {"rule": 0.90}}
            if nearby_players >= 5 and ball_in_defensive:
                return {"tactical_class": "阵地防守", "method": "rule", "probabilities": {"rule": 0.82}}

        if active_half_ratio > 0.35:
            return {"tactical_class": "阵地进攻", "method": "rule", "probabilities": {"rule": 0.80}}

        speeds = []
        for t in tracks:
            trail = t.get("trail", [])
            if len(trail) >= 3:
                dx = trail[-1][0] - trail[-3][0]
                dy = trail[-1][1] - trail[-3][1]
                speeds.append((dx * dx + dy * dy) ** 0.5)

        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            if avg_speed > 12:
                return {"tactical_class": "快速反击", "method": "rule", "probabilities": {"rule": 0.80}}

        return {"tactical_class": "阵地防守", "method": "rule", "probabilities": {"rule": 0.85}}

    def _open_transport(self) -> UsbSerialTransport:
        return UsbSerialTransport(self.usb_port)

    @staticmethod
    def _atomic_write_image(path: Path, image) -> None:
        import cv2

        temporary = path.with_name(path.stem + ".tmp" + path.suffix)
        if not cv2.imwrite(str(temporary), image):
            raise RuntimeError(f"cannot write preview image: {temporary}")
        os.replace(temporary, path)

    def run(self) -> int:
        import cv2
        import numpy as np

        total_frames = len(self.jpg_files)
        if self.max_frames and self.max_frames < total_frames:
            total_frames = self.max_frames

        frame_interval_s = 1.0 / self.fps
        tick_start = time.monotonic()
        report_lines: list[dict] = []
        consecutive_fail = 0

        if not self.dry_run:
            self._transport = self._open_transport()

        for frame_index, jpg_path in enumerate(self.jpg_files[:total_frames]):
            tick_now = time.monotonic()
            expected_elapsed = frame_index * frame_interval_s
            sleep_s = expected_elapsed - (tick_now - tick_start)
            if sleep_s > 0:
                time.sleep(sleep_s)

            image = cv2.imread(str(jpg_path))
            if image is None:
                consecutive_fail += 1
                if consecutive_fail > 10:
                    print("[vision] too many consecutive read failures, exiting")
                    break
                continue
            consecutive_fail = 0

            t0 = time.perf_counter()
            detections = self._detector.detect(image)
            tracks = self._tracker.update(detections)
            tactical_pred = self._rule_classify(tracks, image.shape)
            t1 = time.perf_counter()

            tactical_class = tactical_pred["tactical_class"]
            method = tactical_pred.get("method", "rule")
            probs = tactical_pred.get("probabilities", {})
            confidence = max(probs.values()) if probs else 0.85

            team = self._infer_team(detections, image.shape[1])
            ball = next((d for d in detections if d["class"] == "ball"), None)
            ball_x = int(ball["center"][0]) if ball else -1
            ball_y = int(ball["center"][1]) if ball else -1

            event_ms = int(frame_index / self.fps * 1000)
            candidate = self._event_mapper.map(
                tactical_class, confidence, team, ball_x, ball_y, method
            )
            gated = self._event_gate.filter(candidate, float(event_ms))

            n_players = sum(1 for d in detections if d["class"] == "player")
            n_balls = sum(1 for d in detections if d["class"] == "ball")
            entry = {
                "frame": frame_index + 1,
                "file": jpg_path.name,
                "detections": len(detections),
                "players": n_players,
                "balls": n_balls,
                "tracks": len(tracks),
                "tactical_class": tactical_class,
                "method": method,
                "confidence": round(confidence, 4),
                "inference_ms": round((t1 - t0) * 1000, 1),
                "event": gated.event if gated else "",
                "team": gated.team if gated else "",
                "danger": gated.danger if gated else 0,
            }
            report_lines.append(entry)

            prefix = "MATCH" if gated else "----"
            print(
                f"[vision] {prefix} frame={frame_index+1:04d} tactic={tactical_class} "
                f"team={team} players={n_players} ball={'Y' if ball else 'N'} "
                f"inf={(t1-t0)*1000:.0f}ms"
            )

            vis = None
            if self.save_overlay or self.preview_dir:
                vis = self._detector.draw(image, detections)
                cv2.putText(vis, f"{tactical_class} [{method}] team={team}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                if self._tracker._prev_dets:
                    for t in self._tracker.tracks.values():
                        if "trail" in t and len(t["trail"]) >= 2:
                            pts = np.array(t["trail"], np.int32)
                            cv2.polylines(vis, [pts], False, (0, 140, 255), 1)
                if self.save_overlay:
                    out_path = self.save_overlay / f"frame_{frame_index+1:04d}.jpg"
                    cv2.imwrite(str(out_path), vis)

            preview_source = ""
            preview_overlay = ""
            if self.preview_dir and vis is not None:
                source_path = self.preview_dir / "latest_source.jpg"
                overlay_path = self.preview_dir / "latest_overlay.jpg"
                self._atomic_write_image(source_path, image)
                self._atomic_write_image(overlay_path, vis)
                preview_source = str(source_path)
                preview_overlay = str(overlay_path)

            if gated:
                self._sent_count += 1
                if not self.dry_run and self._transport:
                    self._message_id += 1
                    event = make_event(
                        message_id=self._message_id,
                        timestamp=event_ms,
                        event_name=gated.event,
                        team=gated.team,
                        confidence=gated.confidence,
                        danger=gated.danger,
                        ball_x=gated.ball_x,
                        ball_y=gated.ball_y,
                    )
                    self._transport.send_event(event)
                    self._ack_count += 1
                    print(f"  [usb] sent #{event.message_id} {event.event} danger={event.danger}")

            print("@vision-status " + json.dumps({
                "frame": frame_index + 1,
                "total_frames": total_frames,
                "source": preview_source,
                "overlay": preview_overlay,
                "tactic": tactical_class,
                "events_sent": self._sent_count,
                "acks": self._ack_count,
            }, ensure_ascii=False), flush=True)

        self._write_report(report_lines)

        if self._transport:
            self._transport.close()

        print(f"\n[vision] done: {total_frames} frames, {self._sent_count} events sent, {self._ack_count} ACKed")
        return 0

    def _write_report(self, lines: list[dict]) -> None:
        report_dir = Path("pc_host") / "outputs"
        report_dir.mkdir(parents=True, exist_ok=True)

        jsonl_path = report_dir / "vision_report.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

        csv_path = report_dir / "vision_report.csv"
        if lines:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(lines[0].keys()))
                writer.writeheader()
                writer.writerows(lines)

        print(f"[vision] JSONL: {jsonl_path}")
        print(f"[vision] CSV: {csv_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Football Vision Runner (COCO + rule-based)")
    parser.add_argument("--images", required=True)
    parser.add_argument("--detector-weights", required=True)
    parser.add_argument("--usb", default="")
    parser.add_argument("--fps", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--save-overlay", default=None)
    parser.add_argument("--preview-dir", default=None)
    parser.add_argument("--max-frames", type=int, default=0)

    args = parser.parse_args()
    if not args.dry_run and not args.usb:
        parser.error("--usb is required unless --dry-run is set")

    runner = VisionRunner(
        images_dir=args.images,
        detector_weights=args.detector_weights,
        usb_port=args.usb,
        fps=args.fps,
        dry_run=args.dry_run,
        save_overlay=args.save_overlay,
        preview_dir=args.preview_dir,
        max_frames=args.max_frames,
    )
    return runner.run()


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from football_video_support import VideoClipSpec


def create_match_clip(source: Path, target: Path, spec: VideoClipSpec) -> int:
    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise RuntimeError(f"cannot open source video: {source}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if fps <= 0 or width <= 0 or height <= 0:
        capture.release()
        raise RuntimeError(f"invalid source video metadata: {source}")

    target.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(target), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
    )
    if not writer.isOpened():
        capture.release()
        raise RuntimeError(f"cannot create target video: {target}")

    capture.set(cv2.CAP_PROP_POS_FRAMES, spec.start_frame(fps))
    written = 0
    for _ in range(spec.frame_count(fps)):
        ok, frame = capture.read()
        if not ok:
            break
        writer.write(frame)
        written += 1

    writer.release()
    capture.release()
    if written == 0:
        raise RuntimeError("source video ended before the requested clip")
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a continuous football match clip")
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--start-seconds", type=int, default=600)
    parser.add_argument("--duration-seconds", type=int, default=60)
    args = parser.parse_args()

    written = create_match_clip(
        Path(args.source),
        Path(args.target),
        VideoClipSpec(args.start_seconds, args.duration_seconds),
    )
    print(f"created {written} frames: {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

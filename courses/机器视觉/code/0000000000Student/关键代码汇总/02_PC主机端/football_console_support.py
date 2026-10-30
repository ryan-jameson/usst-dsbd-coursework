from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BHA_MU_FRAMES_DIR = (
    ROOT
    / "基于机器视觉的运动场景识别"
    / "基于机器视觉的运动场景识别"
    / "基于机器视觉的运动场景识别"
    / "Soccer"
    / "S_BHA vs MU"
)


@dataclass(frozen=True)
class VisionStatus:
    frame: int
    total_frames: int
    source: str
    overlay: str
    tactic: str
    events_sent: int
    acks: int


@dataclass(frozen=True)
class VisionCommandOptions:
    images_dir: Path
    weights: Path
    usb_port: str
    fps: int
    max_frames: int
    dry_run: bool
    save_overlay: bool
    preview_dir: Path


def count_jpg_frames(folder: Path) -> int:
    if not folder.is_dir():
        return 0
    return sum(
        1 for item in folder.iterdir()
        if item.is_file() and item.suffix.lower() == ".jpg"
    )


def parse_vision_status(line: str) -> VisionStatus | None:
    prefix = "@vision-status "
    if not line.startswith(prefix):
        return None

    try:
        data = json.loads(line[len(prefix):])
        return VisionStatus(
            frame=int(data["frame"]),
            total_frames=int(data["total_frames"]),
            source=str(data["source"]),
            overlay=str(data["overlay"]),
            tactic=str(data["tactic"]),
            events_sent=int(data["events_sent"]),
            acks=int(data["acks"]),
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def build_vision_command(
    python_executable: str,
    runner_script: Path,
    options: VisionCommandOptions,
) -> list[str]:
    command = [
        python_executable,
        "-u",
        str(runner_script),
        "--images",
        str(options.images_dir),
        "--detector-weights",
        str(options.weights),
        "--fps",
        str(options.fps),
        "--preview-dir",
        str(options.preview_dir),
    ]
    if options.max_frames > 0:
        command.extend(["--max-frames", str(options.max_frames)])
    if options.dry_run:
        command.append("--dry-run")
    else:
        command.extend(["--usb", options.usb_port])
    if options.save_overlay:
        command.extend(["--save-overlay", str(options.preview_dir.parent / "overlays")])
    return command


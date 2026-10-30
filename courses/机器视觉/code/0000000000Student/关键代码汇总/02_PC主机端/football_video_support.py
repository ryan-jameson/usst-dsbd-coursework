from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VideoClipSpec:
    start_seconds: int
    duration_seconds: int

    def start_frame(self, fps: float) -> int:
        return int(self.start_seconds * fps)

    def frame_count(self, fps: float) -> int:
        return int(self.duration_seconds * fps)


@dataclass(frozen=True)
class VideoCommandOptions:
    video_path: Path
    player_weights: Path
    ball_weights: Path
    pitch_weights: Path
    tactical_model: Path
    usb_port: str
    preview_dir: Path
    dry_run: bool


def build_video_command(
    python_executable: str,
    runner_script: Path,
    options: VideoCommandOptions,
) -> list[str]:
    command = [
        python_executable,
        "-u",
        str(runner_script),
        "--video",
        str(options.video_path),
        "--player-weights",
        str(options.player_weights),
        "--ball-weights",
        str(options.ball_weights),
        "--pitch-weights",
        str(options.pitch_weights),
        "--tactical-model",
        str(options.tactical_model),
        "--preview-dir",
        str(options.preview_dir),
    ]
    if options.dry_run:
        command.append("--dry-run")
    else:
        command.extend(["--usb", options.usb_port])
    return command

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from pc_host.football_console_support import (
    BHA_MU_FRAMES_DIR,
    VisionCommandOptions,
    build_vision_command,
    count_jpg_frames,
    parse_vision_status,
)
from pc_host.football_video_support import VideoClipSpec, VideoCommandOptions, build_video_command
from pc_host.football_playback_clock import frame_index_at


class FootballConsoleSupportTests(unittest.TestCase):
    def test_count_jpg_frames_ignores_non_jpg_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "000001.jpg").write_bytes(b"x")
            (root / "000002.JPG").write_bytes(b"x")
            (root / "note.txt").write_text("x", encoding="utf-8")

            self.assertEqual(count_jpg_frames(root), 2)

    def test_parse_vision_status(self) -> None:
        status = parse_vision_status(
            '@vision-status {"frame":4,"total_frames":451,'
            '"source":"a.jpg","overlay":"b.jpg","tactic":"pressing",'
            '"events_sent":1,"acks":1}'
        )

        self.assertIsNotNone(status)
        assert status is not None
        self.assertEqual((status.frame, status.total_frames, status.tactic),
                         (4, 451, "pressing"))

    def test_build_vision_command_uses_local_images_and_preview(self) -> None:
        options = VisionCommandOptions(
            images_dir=Path("frames"),
            weights=Path("yolov8n.pt"),
            usb_port="",
            fps=5,
            max_frames=20,
            dry_run=True,
            save_overlay=True,
            preview_dir=Path("preview"),
        )

        command = build_vision_command("python", Path("runner.py"), options)

        self.assertIn("--dry-run", command)
        self.assertEqual(command[command.index("--preview-dir") + 1], "preview")
        self.assertNotIn("--video", command)

    def test_repository_default_has_451_frames(self) -> None:
        self.assertEqual(count_jpg_frames(BHA_MU_FRAMES_DIR), 451)

    def test_vision_runner_help_exposes_preview_directory(self) -> None:
        runner = Path(__file__).with_name("football_vision_runner.py")
        result = subprocess.run(
            [sys.executable, str(runner), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--preview-dir", result.stdout)

    def test_gui_is_wired_to_offline_player_and_dual_video_playback(self) -> None:
        source = Path(__file__).with_name("football_gui.py").read_text(encoding="utf-8")

        self.assertIn("football_offline_player.py", source)
        self.assertIn("SOURCE_VIDEO", source)
        self.assertIn("MANUAL_YOLO_VIDEO", source)
        self.assertIn("_overlay_capture", source)
        self.assertIn("Start Demo", source)

    def test_gui_uses_fixed_demo_configuration(self) -> None:
        source = Path(__file__).with_name("football_gui.py").read_text(encoding="utf-8")

        self.assertIn("M55 USB Port", source)
        self.assertNotIn("Provision M55", source)
        self.assertNotIn("start_provision", source)
        self.assertNotIn("YOLO Weights", source)

    def test_demo_gui_defaults_to_com10_and_live_usb(self) -> None:
        source = Path(__file__).with_name("football_gui.py").read_text(encoding="utf-8")

        self.assertIn('StringVar(value="COM10")', source)
        self.assertIn("BooleanVar(value=False)", source)
        self.assertIn("Start Demo", source)

    def test_demo_gui_has_process_tree_stop_fallback(self) -> None:
        source = Path(__file__).with_name("football_gui.py").read_text(encoding="utf-8")

        self.assertIn("taskkill", source)
        self.assertIn("_force_stop_process", source)

    def test_video_demo_command_uses_clip_and_default_com10(self) -> None:
        options = VideoCommandOptions(
            video_path=Path("football_demo_clip.mp4"),
            player_weights=Path("football-player-detection.pt"),
            ball_weights=Path("football-ball-detection.pt"),
            pitch_weights=Path("football-pitch-detection.pt"),
            tactical_model=Path("tactical_classifier_calibrated.pt"),
            usb_port="COM10",
            preview_dir=Path("preview"),
            dry_run=False,
        )

        command = build_video_command("python", Path("video_runner.py"), options)

        self.assertEqual(command[command.index("--usb") + 1], "COM10")
        self.assertEqual(command[command.index("--video") + 1], "football_demo_clip.mp4")
        self.assertIn("--tactical-model", command)

    def test_video_clip_spec_selects_a_60_second_match_segment(self) -> None:
        spec = VideoClipSpec(start_seconds=600, duration_seconds=60)

        self.assertEqual(spec.start_frame(30.0), 18000)
        self.assertEqual(spec.frame_count(30.0), 1800)

    def test_video_gui_plays_source_independently_of_analysis(self) -> None:
        source = Path(__file__).with_name("football_gui.py").read_text(encoding="utf-8")

        self.assertIn("_play_source_video", source)
        self.assertIn("self.root.after(33, self._play_source_video)", source)

    def test_gui_uses_clean_source_video_and_manual_event_transport(self) -> None:
        source = Path(__file__).with_name("football_gui.py").read_text(encoding="utf-8")

        self.assertIn("football_offline_player.py", source)
        self.assertIn("SOURCE_VIDEO", source)
        self.assertIn("VIDEO_PATH = SOURCE_VIDEO", source)
        self.assertIn("MANUAL_YOLO_VIDEO", source)
        self.assertIn("Original Match Video", source)
        self.assertNotIn("football_video_runner.py", source)

    def test_gui_synchronizes_videos_with_their_own_frame_rates(self) -> None:
        source = Path(__file__).with_name("football_gui.py").read_text(encoding="utf-8")

        self.assertIn("CAP_PROP_FPS", source)
        self.assertIn("_playback_started_at", source)
        self.assertIn("frame_index_at", source)

    def test_common_playback_clock_maps_one_time_to_each_video_rate(self) -> None:
        self.assertEqual(300, frame_index_at(10.0, 30.0, 1800))
        self.assertEqual(100, frame_index_at(10.0, 10.0, 600))


if __name__ == "__main__":
    unittest.main()

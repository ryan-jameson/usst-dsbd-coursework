import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import supervision as sv

from pc_host.football_commentary import summarize_event
from pc_host.football_offline_assets import (
    ANNOTATED_VIDEO,
    MANUAL_EVENT_VIDEO,
    MANUAL_TIMELINE_FILE,
    MANUAL_YOLO_VIDEO,
    SOURCE_VIDEO,
    due_events,
    load_timeline,
    playback_end_ms,
)
from pc_host.football_offline_preprocess import extract_ball_center


def payload(message_id: int, timestamp: int, event: str) -> dict[str, object]:
    return {
        "protocol_version": 1,
        "message_id": message_id,
        "event_type": "football_event",
        "timestamp": timestamp,
        "event": event,
        "team": "home",
        "confidence": 0.8,
        "danger": 3,
        "ball_x": 426,
        "ball_y": 240,
        "checksum": "",
    }


class OfflineAssetsTests(unittest.TestCase):
    def test_loads_utf8_timeline_in_timestamp_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "timeline.json"
            path.write_text(json.dumps({"events": [payload(2, 5000, "wide_attack"), payload(1, 0, "new_match")]}, ensure_ascii=False), encoding="utf-8")

            events = load_timeline(path)

        self.assertEqual([1, 2], [event.message_id for event in events])
        self.assertEqual("wide_attack", events[1].event)

    def test_due_events_never_resends_a_message_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "timeline.json"
            path.write_text(json.dumps({"events": [payload(1, 0, "new_match"), payload(2, 5000, "build_up")]}), encoding="utf-8")
            events = load_timeline(path)

        sent = {1}
        self.assertEqual([2], [event.message_id for event in due_events(events, 5500, sent)])
        self.assertEqual([], due_events(events, 5500, {1, 2}))

    def test_assets_use_fixed_source_and_annotated_paths(self) -> None:
        self.assertEqual("football_demo_clip.mp4", SOURCE_VIDEO.name)
        self.assertEqual("football_demo_annotated.mp4", ANNOTATED_VIDEO.name)

    def test_ball_point_uses_raw_detector_box(self) -> None:
        ball = sv.Detections(
            xyxy=np.array([[100, 200, 120, 240]], dtype=np.float32),
            class_id=np.array([0]),
            confidence=np.array([0.9]),
        )

        self.assertEqual((110, 220), extract_ball_center(ball))

    def test_manual_review_timeline_has_eight_confirmed_events(self) -> None:
        events = load_timeline(MANUAL_TIMELINE_FILE)

        self.assertTrue(MANUAL_EVENT_VIDEO.is_file())
        self.assertTrue(MANUAL_YOLO_VIDEO.is_file())
        self.assertEqual(8, len(events))
        self.assertEqual(["foul_committed", "free_kick_restart", "ball_out_touchline", "throw_in_restart",
                          "attacking_phase", "pass_into_penalty_area", "shot_on_target", "goalkeeper_save"],
                         [event.event for event in events])

    def test_playback_end_keeps_60_second_video_running_after_last_event(self) -> None:
        events = load_timeline(MANUAL_TIMELINE_FILE)

        self.assertEqual(60_000, playback_end_ms(events, 60_000))

    def test_manual_events_serialize_a_factual_chinese_commentary_summary(self) -> None:
        event = load_timeline(MANUAL_TIMELINE_FILE)[6]

        summary = summarize_event(event.event, event.team, event.danger, event.ball_x)
        payload = json.loads(event.to_football_event().to_payload().decode("utf-8"))

        self.assertIn("阿根廷", summary)
        self.assertIn("射正", summary)
        self.assertEqual(summary, payload["commentary"])


if __name__ == "__main__":
    unittest.main()

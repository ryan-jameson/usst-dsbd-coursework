from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from pc_host.football_host import FootballEvent
    from pc_host.football_commentary import summarize_event
except ModuleNotFoundError:
    from football_host import FootballEvent
    from football_commentary import summarize_event


ROOT = Path(__file__).resolve().parents[1]
OFFLINE_DEMO_DIR = ROOT / "pc_host" / "assets" / "offline_demo"
SOURCE_VIDEO = ROOT / "pc_host" / "assets" / "football_demo_clip.mp4"
ANNOTATED_VIDEO = OFFLINE_DEMO_DIR / "football_demo_annotated.mp4"
TIMELINE_FILE = OFFLINE_DEMO_DIR / "football_demo_timeline.json"
REPORT_FILE = OFFLINE_DEMO_DIR / "football_demo_report.json"
MANUAL_REVIEW_DIR = OFFLINE_DEMO_DIR / "manual_review"
MANUAL_YOLO_VIDEO = MANUAL_REVIEW_DIR / "football_yolo_tracking.mp4"
MANUAL_EVENT_VIDEO = MANUAL_REVIEW_DIR / "football_event_review.mp4"
MANUAL_TIMELINE_FILE = MANUAL_REVIEW_DIR / "football_manual_timeline.json"


@dataclass(frozen=True)
class OfflineTimelineEvent:
    protocol_version: int
    message_id: int
    event_type: str
    timestamp: int
    event: str
    team: str
    confidence: float
    danger: int
    ball_x: int
    ball_y: int
    checksum: str
    commentary: str = ""

    def to_football_event(self) -> FootballEvent:
        return FootballEvent(
            protocol_version=self.protocol_version,
            message_id=self.message_id,
            event_type=self.event_type,
            timestamp=self.timestamp,
            event=self.event,
            team=self.team,
            confidence=self.confidence,
            danger=self.danger,
            ball_x=self.ball_x,
            ball_y=self.ball_y,
            checksum=self.checksum,
            commentary=self.commentary or summarize_event(self.event, self.team, self.danger, self.ball_x),
        )


def _event_from_json(data: object) -> OfflineTimelineEvent:
    if not isinstance(data, dict):
        raise ValueError("timeline event must be an object")
    try:
        event = OfflineTimelineEvent(
            protocol_version=int(data["protocol_version"]),
            message_id=int(data["message_id"]),
            event_type=str(data["event_type"]),
            timestamp=int(data["timestamp"]),
            event=str(data["event"]),
            team=str(data["team"]),
            confidence=float(data["confidence"]),
            danger=int(data["danger"]),
            ball_x=int(data["ball_x"]),
            ball_y=int(data["ball_y"]),
            checksum=str(data["checksum"]),
            commentary=str(data.get("commentary", "")),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("timeline event has invalid FBP1 fields") from exc
    if event.protocol_version != 1 or not event.event or not event.event_type:
        raise ValueError("timeline event has an invalid protocol or event")
    return event


def load_timeline(path: Path = TIMELINE_FILE) -> list[OfflineTimelineEvent]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("events"), list):
        raise ValueError("timeline must contain an events array")
    events = sorted((_event_from_json(item) for item in data["events"]), key=lambda item: (item.timestamp, item.message_id))
    if len({item.message_id for item in events}) != len(events):
        raise ValueError("timeline message_id values must be unique")
    return events


def due_events(events: Iterable[OfflineTimelineEvent], elapsed_ms: int,
               sent_message_ids: set[int]) -> list[OfflineTimelineEvent]:
    return [event for event in events if event.timestamp <= elapsed_ms and event.message_id not in sent_message_ids]


def playback_end_ms(events: Iterable[OfflineTimelineEvent], requested_duration_ms: int = 0) -> int:
    """Keep playback alive until both the final event and requested video duration finish."""
    final_event_ms = max((event.timestamp for event in events), default=0)
    return max(final_event_ms, requested_duration_ms)

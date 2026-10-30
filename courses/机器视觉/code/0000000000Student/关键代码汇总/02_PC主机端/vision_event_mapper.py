from __future__ import annotations

import time
from dataclasses import dataclass


TACTIC_TO_EVENT = {
    "快速反击": ("counter_attack", 5, 3, 3.0),
    "定位球": ("set_piece", 4, 3, 5.0),
    "阵地进攻": ("build_up", 2, 3, 5.0),
    "阵地防守": ("defensive_block", 2, 5, 5.0),
    "边路进攻": ("wide_attack", 3, 3, 5.0),
    "中路渗透": ("central_penetration", 4, 3, 5.0),
    "高位逼抢": ("high_press", 4, 3, 5.0),
    "收缩防守": ("defensive_block", 2, 3, 5.0),
}


@dataclass
class VisionEvent:
    event: str
    team: str
    confidence: float
    danger: int
    ball_x: int
    ball_y: int
    method: str


class EventMapper:
    def __init__(self) -> None:
        self._goal_cooldowns: dict[str, float] = {}
        self._last_goal_team: str = ""
        self._last_goal_time: float = 0.0
        self._goal_frame_count: int = 0

    def map(self, tactical_class: str, confidence: float, team: str,
            ball_x: int, ball_y: int, method: str) -> VisionEvent | None:
        if tactical_class not in TACTIC_TO_EVENT:
            return None
        event_name, danger, _stable, _cooldown = TACTIC_TO_EVENT[tactical_class]
        return VisionEvent(
            event=event_name,
            team=team,
            confidence=confidence,
            danger=danger,
            ball_x=ball_x,
            ball_y=ball_y,
            method=method,
        )


class EventGate:
    def __init__(self) -> None:
        self._stable_name: str = ""
        self._stable_count: int = 0
        self._last_sent_ms: dict[str, float] = {}
        self._sent_event_ids: set[int] = set()

    def filter(self, candidate: VisionEvent | None, now_ms: float) -> VisionEvent | None:
        if candidate is None:
            return None

        min_conf = 0.30 if candidate.method == "rule" else 0.10
        if candidate.confidence < min_conf:
            return None

        rule = TACTIC_TO_EVENT.get(None)
        for chinese, (name, danger, stable, cooldown) in TACTIC_TO_EVENT.items():
            if name == candidate.event:
                rule = (name, danger, stable, cooldown)
                break

        if rule is None:
            return None

        name, danger, stable_frames, cooldown_s = rule

        if candidate.event != self._stable_name:
            self._stable_name = candidate.event
            self._stable_count = 0
        self._stable_count += 1

        if self._stable_count < stable_frames:
            return None

        last_ms = self._last_sent_ms.get(name, -99999999.0)
        if now_ms - last_ms < cooldown_s * 1000.0:
            return None

        self._last_sent_ms[name] = now_ms
        self._stable_count = 0
        return candidate

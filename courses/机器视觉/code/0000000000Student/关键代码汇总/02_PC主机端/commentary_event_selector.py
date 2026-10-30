from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


EVENT_RULES: dict[str, tuple[str, int]] = {
    "快速反击": ("counter_attack", 5),
    "定位球": ("set_piece", 4),
    "阵地进攻": ("build_up", 2),
    "阵地防守": ("defensive_block", 2),
    "边路进攻": ("wide_attack", 3),
    "中路渗透": ("central_penetration", 4),
    "高位逼抢": ("high_press", 4),
    "收缩防守": ("defensive_block", 2),
}


@dataclass(frozen=True)
class CommentaryObservation:
    tactic: str
    confidence: float
    ball_x: int
    ball_y: int
    frame_width: int
    frame_height: int
    ball_dx: float


@dataclass(frozen=True)
class CommentaryDecision:
    event: str
    confidence: float
    danger: int
    ball_x: int
    ball_y: int


class FiveSecondCommentarySelector:
    """Turns one-second vision observations into one safe five-second event."""

    def __init__(self) -> None:
        self._observations: list[CommentaryObservation] = []

    def observe(self, observation: CommentaryObservation) -> None:
        self._observations.append(observation)

    def decide(self) -> CommentaryDecision:
        if not self._observations:
            return CommentaryDecision("build_up", 0.10, 1, -1, -1)

        scores: dict[str, float] = defaultdict(float)
        latest = self._observations[-1]
        for observation in self._observations:
            event, _danger = self._event_for(observation)
            scores[event] += max(0.05, min(1.0, observation.confidence))

        event = max(scores, key=scores.get)
        confidence = min(1.0, scores[event] / len(self._observations))
        danger = self._danger_for(event, latest)
        self._observations.clear()
        return CommentaryDecision(event, confidence, danger, latest.ball_x, latest.ball_y)

    @staticmethod
    def _event_for(observation: CommentaryObservation) -> tuple[str, int]:
        if observation.confidence < 0.10:
            return "build_up", 1
        mapped = EVENT_RULES.get(observation.tactic)
        if mapped is not None:
            return mapped
        if observation.ball_dx and abs(observation.ball_dx) >= observation.frame_width * 0.18:
            return "counter_attack", 5
        return "build_up", 2

    @staticmethod
    def _danger_for(event: str, observation: CommentaryObservation) -> int:
        default = {
            "build_up": 2,
            "wide_attack": 3,
            "central_penetration": 4,
            "counter_attack": 5,
            "high_press": 4,
            "set_piece": 4,
            "shot": 5,
            "goal": 5,
            "defensive_block": 2,
            "transition_defense": 4,
        }.get(event, 2)
        if event in {"wide_attack", "central_penetration", "build_up"} and observation.frame_height > 0:
            if observation.ball_y >= 0 and observation.ball_y < observation.frame_height // 3:
                return min(5, default + 1)
        return default

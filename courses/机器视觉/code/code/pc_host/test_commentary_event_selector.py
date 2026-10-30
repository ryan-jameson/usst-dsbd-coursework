import unittest

from pc_host.commentary_event_selector import CommentaryObservation, FiveSecondCommentarySelector


def observe(selector: FiveSecondCommentarySelector, tactic: str, confidence: float,
            ball_x: int = 426, ball_y: int = 240, ball_dx: float = 0.0) -> None:
    selector.observe(CommentaryObservation(
        tactic=tactic,
        confidence=confidence,
        ball_x=ball_x,
        ball_y=ball_y,
        frame_width=852,
        frame_height=480,
        ball_dx=ball_dx,
    ))


class CommentaryEventSelectorTests(unittest.TestCase):
    def test_side_attack_becomes_wide_attack(self) -> None:
        selector = FiveSecondCommentarySelector()
        for _ in range(5):
            observe(selector, "边路进攻", 0.84, ball_x=120)

        decision = selector.decide()

        self.assertEqual("wide_attack", decision.event)
        self.assertEqual(3, decision.danger)
        self.assertGreaterEqual(decision.confidence, 0.80)

    def test_central_penetration_becomes_high_danger(self) -> None:
        selector = FiveSecondCommentarySelector()
        for _ in range(5):
            observe(selector, "中路渗透", 0.76, ball_x=420)

        decision = selector.decide()

        self.assertEqual("central_penetration", decision.event)
        self.assertEqual(4, decision.danger)

    def test_fast_transition_becomes_counter_attack(self) -> None:
        selector = FiveSecondCommentarySelector()
        for _ in range(5):
            observe(selector, "快速反击", 0.71, ball_x=610, ball_dx=190.0)

        decision = selector.decide()

        self.assertEqual("counter_attack", decision.event)
        self.assertEqual(5, decision.danger)

    def test_high_press_and_low_block_have_distinct_events(self) -> None:
        press = FiveSecondCommentarySelector()
        block = FiveSecondCommentarySelector()
        for _ in range(5):
            observe(press, "高位逼抢", 0.67)
            observe(block, "阵地防守", 0.78)

        self.assertEqual("high_press", press.decide().event)
        self.assertEqual("defensive_block", block.decide().event)

    def test_low_confidence_uses_safe_build_up_fallback(self) -> None:
        selector = FiveSecondCommentarySelector()
        for _ in range(5):
            observe(selector, "未知战术", 0.05, ball_x=430)

        decision = selector.decide()

        self.assertEqual("build_up", decision.event)
        self.assertLessEqual(decision.danger, 2)


if __name__ == "__main__":
    unittest.main()

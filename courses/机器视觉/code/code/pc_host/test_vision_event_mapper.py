import unittest

from pc_host.vision_event_mapper import EventGate, EventMapper


class VisionEventMapperTests(unittest.TestCase):
    def test_attack_class_maps_to_detailed_event(self) -> None:
        event = EventMapper().map("阵地进攻", 0.2, "home", 100, 200, "model")

        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event.event, "build_up")
        self.assertLessEqual(event.danger, 2)

    def test_side_and_central_classes_remain_distinct(self) -> None:
        mapper = EventMapper()
        side = mapper.map("边路进攻", 0.7, "home", 100, 200, "model")
        central = mapper.map("中路渗透", 0.7, "home", 426, 200, "model")

        assert side is not None and central is not None
        self.assertEqual("wide_attack", side.event)
        self.assertEqual("central_penetration", central.event)

    def test_low_confidence_model_event_can_trigger_after_stability(self) -> None:
        gate = EventGate()
        candidate = EventMapper().map("高位逼抢", 0.2, "home", 100, 200, "model")

        self.assertIsNone(gate.filter(candidate, 0))
        self.assertIsNone(gate.filter(candidate, 1000))
        self.assertIsNotNone(gate.filter(candidate, 2000))

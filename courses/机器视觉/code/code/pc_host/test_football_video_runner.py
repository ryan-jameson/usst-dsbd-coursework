import unittest

import numpy as np

from pc_host.football_video_runner import extract_pitch_points


class FootballVideoRunnerTests(unittest.TestCase):
    def test_extract_pitch_points_accepts_empty_model_result(self) -> None:
        self.assertEqual(extract_pitch_points(None), [])

    def test_extract_pitch_points_keeps_valid_points_only(self) -> None:
        points = extract_pitch_points(np.array([[0.0, 2.0], [10.0, 20.0]]))
        self.assertEqual(points, [(10, 20)])

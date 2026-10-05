"""Meaningful maths/input tests runnable without ROS: python tools/test_core.py."""
from pathlib import Path
import math
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'mobile_robot_ws/src/mobile_robot_control'),
                str(ROOT / 'mobile_robot_ws/src/mobile_robot_navigation')]
from mobile_robot_control.kinematics import wheel_speeds, ticks_to_radians, integrate_pose, limit_command
from mobile_robot_navigation.goals import validate_goal


class CoreTests(unittest.TestCase):
    def test_straight_motion(self):
        left, right = wheel_speeds(0.2, 0)
        self.assertAlmostEqual(left, 10 / 3)
        self.assertAlmostEqual(left, right)
        self.assertEqual(integrate_pose(0, 0, 0, 1, 1), (1, 0, 0))

    def test_rotation_sign_and_position(self):
        left, right = wheel_speeds(0, 0.8)
        self.assertLess(left, 0)
        self.assertGreater(right, 0)
        x, y, yaw = integrate_pose(0, 0, 0, -0.123 * math.pi / 2, 0.123 * math.pi / 2)
        self.assertAlmostEqual(x, 0)
        self.assertAlmostEqual(y, 0)
        self.assertAlmostEqual(yaw, math.pi / 2)

    def test_quarter_circle(self):
        # Radius 1 m, 90 degree arc; analytic endpoint is (1,1).
        turn = math.pi / 2
        x, y, yaw = integrate_pose(0, 0, 0, (1 - 0.123) * turn, (1 + 0.123) * turn)
        self.assertAlmostEqual(x, 1)
        self.assertAlmostEqual(y, 1)
        self.assertAlmostEqual(yaw, turn)

    def test_reverse_motion(self):
        x, y, _ = integrate_pose(0, 0, math.pi / 2, -1, -1)
        self.assertAlmostEqual(x, 0)
        self.assertAlmostEqual(y, -1)

    def test_encoder_resolution(self):
        self.assertAlmostEqual(ticks_to_radians(2048, 2048), 2 * math.pi)
        with self.assertRaises(ValueError):
            ticks_to_radians(1, 0)

    def test_limits_preserve_turning_radius(self):
        linear, angular = limit_command(1.0, 2.0)
        self.assertAlmostEqual(linear / angular, 0.5)
        self.assertLessEqual(abs(linear), 0.2)
        self.assertLessEqual(abs(angular), 0.8)
        self.assertLessEqual(max(map(abs, wheel_speeds(linear, angular))), 5.0)

    def test_invalid_velocity_stops(self):
        self.assertEqual(limit_command(float('nan'), 0), (0, 0))
        self.assertEqual(limit_command(0, float('inf')), (0, 0))

    def test_geometry_rejects_zero(self):
        with self.assertRaises(ValueError):
            wheel_speeds(1, 0, radius=0)

    def test_valid_goal(self):
        self.assertEqual(validate_goal({'x': 1, 'y': 2, 'theta': 0}), (1.0, 2.0, 0.0))

    def test_bad_goal(self):
        for value in (None, {}, {'x': True, 'y': 0, 'theta': 0},
                      {'x': float('nan'), 'y': 0, 'theta': 0},
                      {'x': '1', 'y': 0, 'theta': 0},
                      {'x': 1, 'y': 0, 'theta': 0, 'extra': 0}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_goal(value)


if __name__ == '__main__':
    unittest.main(verbosity=2)

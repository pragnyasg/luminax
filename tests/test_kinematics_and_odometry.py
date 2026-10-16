#!/usr/bin/env python3
"""
Unit Tests for LUMI Differential-Drive Kinematics & Odometry Computation.
"""

import math
import unittest


class TestDifferentialDriveKinematics(unittest.TestCase):
    def setUp(self):
        self.wheel_track = 0.32    # 32 cm
        self.wheel_radius = 0.04   # 4 cm
        self.encoder_cpr = 334.0   # Counts per rev

    def forward_kinematics(self, linear_v, angular_w):
        """v, w -> v_l, v_r"""
        v_l = linear_v - (angular_w * self.wheel_track / 2.0)
        v_r = linear_v + (angular_w * self.wheel_track / 2.0)
        return v_l, v_r

    def inverse_kinematics(self, v_l, v_r):
        """v_l, v_r -> v, w"""
        v = (v_r + v_l) / 2.0
        w = (v_r - v_l) / self.wheel_track
        return v, w

    def ticks_to_distance(self, delta_ticks):
        """Convert ticks to linear wheel displacement in meters."""
        circumference = 2.0 * math.pi * self.wheel_radius
        return (delta_ticks / self.encoder_cpr) * circumference

    def normalize_angle(self, angle):
        """Normalize angle to [-pi, pi]."""
        return math.atan2(math.sin(angle), math.cos(angle))

    def heading_to_quaternion(self, yaw):
        """Convert 2D planar heading yaw to quaternion (qz, qw)."""
        qz = math.sin(yaw / 2.0)
        qw = math.cos(yaw / 2.0)
        return qz, qw

    def test_pure_translation(self):
        """Pure forward translation should result in identical left and right wheel speeds."""
        v_cmd = 0.25
        w_cmd = 0.0
        v_l, v_r = self.forward_kinematics(v_cmd, w_cmd)
        self.assertAlmostEqual(v_l, 0.25)
        self.assertAlmostEqual(v_r, 0.25)

        # Inverse recovery
        v_rec, w_rec = self.inverse_kinematics(v_l, v_r)
        self.assertAlmostEqual(v_rec, 0.25)
        self.assertAlmostEqual(w_rec, 0.0)

    def test_pure_rotation(self):
        """In-place rotation should yield equal and opposite wheel speeds."""
        v_cmd = 0.0
        w_cmd = 1.0  # 1 rad/s counter-clockwise
        v_l, v_r = self.forward_kinematics(v_cmd, w_cmd)
        expected_speed = 1.0 * (self.wheel_track / 2.0)  # 0.16 m/s
        self.assertAlmostEqual(v_l, -expected_speed)
        self.assertAlmostEqual(v_r, expected_speed)

        v_rec, w_rec = self.inverse_kinematics(v_l, v_r)
        self.assertAlmostEqual(v_rec, 0.0)
        self.assertAlmostEqual(w_rec, 1.0)

    def test_combined_motion(self):
        """Curved arc motion with non-zero linear and angular velocities."""
        v_cmd = 0.20
        w_cmd = 0.50
        v_l, v_r = self.forward_kinematics(v_cmd, w_cmd)
        self.assertAlmostEqual(v_l, 0.20 - (0.50 * 0.16))
        self.assertAlmostEqual(v_r, 0.20 + (0.50 * 0.16))

        v_rec, w_rec = self.inverse_kinematics(v_l, v_r)
        self.assertAlmostEqual(v_rec, v_cmd)
        self.assertAlmostEqual(w_rec, w_cmd)

    def test_encoder_ticks_conversion(self):
        """One full revolution (334 ticks) should equal 2*pi*r meters."""
        dist = self.ticks_to_distance(334.0)
        expected = 2.0 * math.pi * 0.04
        self.assertAlmostEqual(dist, expected, places=3)

    def test_quaternion_normalization(self):
        """Unit quaternion constraint: qz^2 + qw^2 == 1 for planar rotation."""
        for angle in [0.0, math.pi / 4, math.pi / 2, math.pi, -math.pi / 3]:
            qz, qw = self.heading_to_quaternion(angle)
            norm_sq = qz**2 + qw**2
            self.assertAlmostEqual(norm_sq, 1.0, places=6)

    def test_angle_normalization(self):
        """Angles outside [-pi, pi] must be wrapped into [-pi, pi]."""
        self.assertAlmostEqual(self.normalize_angle(3 * math.pi), math.pi, places=5)
        self.assertAlmostEqual(self.normalize_angle(-3 * math.pi), -math.pi, places=5)
        self.assertAlmostEqual(self.normalize_angle(0.0), 0.0)


if __name__ == '__main__':
    unittest.main()

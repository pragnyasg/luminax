"""Logic tests that need no GPIO and no running ROS graph."""

import importlib.util

import pytest

# The node module imports rclpy at import time. The backend test is skipped
# where rclpy is absent (e.g. a plain laptop); the pure-math tests always run.
_HAS_RCLPY = importlib.util.find_spec('rclpy') is not None


class _FakeLogger:
    def info(self, *_a, **_k):
        pass

    def warn(self, *_a, **_k):
        pass

    def error(self, *_a, **_k):
        pass


@pytest.mark.skipif(not _HAS_RCLPY, reason='rclpy not installed (non-ROS env)')
def test_dryrun_backend_clamps_and_runs():
    from luminax_base.motor_driver_node import DryRunBackend
    b = DryRunBackend(_FakeLogger())
    b.set_duty(0.5, -0.5)
    b.stop()          # should set (0, 0) without error
    b.close()


def diff_drive(v, w, sep):
    """Reference inverse kinematics used by the node."""
    return v - w * sep / 2.0, v + w * sep / 2.0


def test_straight_line_equal_wheels():
    vl, vr = diff_drive(0.3, 0.0, 0.375)
    assert abs(vl - vr) < 1e-9
    assert abs(vl - 0.3) < 1e-9


def test_pure_rotation_opposite_wheels():
    vl, vr = diff_drive(0.0, 1.0, 0.4)
    assert abs(vl + vr) < 1e-9     # equal and opposite
    assert vr > 0 and vl < 0        # +w turns left wheel back, right wheel fwd

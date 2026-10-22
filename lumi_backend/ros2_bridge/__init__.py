"""
Robot Bridge Factory.
Instantiates ROS2Bridge when physical ROS 2 is active, or MockBridge for development mode.
"""

from __future__ import annotations

import logging
from lumi_backend.config import settings
from lumi_backend.ros2_bridge.bridge_interface import RobotBridgeBase
from lumi_backend.ros2_bridge.mock_adapter import MockBridge

logger = logging.getLogger(__name__)


def create_bridge() -> RobotBridgeBase:
    if not settings.dev_mode:
        try:
            from lumi_backend.ros2_bridge.ros2_adapter import HAS_RCLPY, ROS2Bridge
            if HAS_RCLPY:
                logger.info("Initializing Production ROS 2 Bridge adapter.")
                return ROS2Bridge()
            else:
                logger.warn("rclpy not detected on this system. Falling back to MockBridge.")
        except Exception as exc:
            logger.warn(f"Failed to load ROS 2 bridge: {exc}. Falling back to MockBridge.")

    logger.info("Initializing Deterministic MockBridge for development/testing.")
    return MockBridge()

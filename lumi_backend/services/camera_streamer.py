"""
Camera Streaming Service.
Relays live camera frames from robot bridge to HTTP MJPEG video stream and JPEG snapshots.
"""

from __future__ import annotations

import asyncio
import io
import time
from typing import AsyncGenerator, Optional
from PIL import Image, ImageDraw

from lumi_backend.ros2_bridge.bridge_interface import RobotBridgeBase


class CameraStreamService:
    def __init__(self, bridge: RobotBridgeBase) -> None:
        self.bridge = bridge

    def get_snapshot(self) -> bytes:
        frame = self.bridge.get_latest_camera_frame()
        if frame:
            return frame

        # Fallback offline camera placeholder image
        img = Image.new("RGB", (640, 480), color=(25, 20, 35))
        draw = ImageDraw.Draw(img)
        draw.text((220, 230), "LUMI CAMERA OFFLINE", fill=(220, 70, 70))
        draw.text((200, 260), "Waiting for camera connection...", fill=(180, 180, 200))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        return buf.getvalue()

    async def generate_mjpeg_stream(self, fps: float = 15.0) -> AsyncGenerator[bytes, None]:
        frame_interval = 1.0 / max(1.0, fps)
        while True:
            frame_bytes = self.get_snapshot()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
            await asyncio.sleep(frame_interval)

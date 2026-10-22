"""
WebSocket Connection Manager and Real-time Event Broadcaster.
Handles client connection tracking, ping-pong keepalives, and JSON event broadcasting.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Set

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        logger.info(f"Caregiver WebSocket client connected. Total clients: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self.active_connections.discard(websocket)
        logger.info(f"Caregiver WebSocket client disconnected. Remaining clients: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcasts payload to all connected clients, purging disconnected sockets."""
        if not self.active_connections:
            return

        payload_text = json.dumps(message)
        dead_connections: List[WebSocket] = []

        async with self._lock:
            for connection in self.active_connections:
                try:
                    await connection.send_text(payload_text)
                except Exception as exc:
                    logger.debug(f"Failed to send to WebSocket client: {exc}")
                    dead_connections.append(connection)

            for dead in dead_connections:
                self.active_connections.discard(dead)


ws_manager = WebSocketManager()

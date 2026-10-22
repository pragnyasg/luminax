"""
LUMI Caregiver Backend Application Entrypoint.
Orchestrates REST API, WebSocket event broadcasting, SQLite persistence, and Robot Bridge.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict

from fastapi import Depends, FastAPI, HTTPException, Header, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from lumi_backend.api.routes_camera import router as camera_router
from lumi_backend.api.routes_control import router as control_router
from lumi_backend.api.routes_emergencies import router as emergencies_router
from lumi_backend.api.routes_history import router as history_router
from lumi_backend.api.routes_medicines import router as medicines_router
from lumi_backend.api.routes_navigation import router as navigation_router
from lumi_backend.api.routes_people import router as people_router
from lumi_backend.api.routes_robot import router as robot_router
from lumi_backend.api.routes_voice import router as voice_router
from lumi_backend.api.websocket import ws_manager
from lumi_backend.config import settings
from lumi_backend.database import Database
from lumi_backend.ros2_bridge import create_bridge
from lumi_backend.services.camera_streamer import CameraStreamService
from lumi_backend.services.medicine_scheduler import MedicineSchedulerService
from lumi_backend.services.notification_service import NotificationManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("lumi_backend")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager initializing database, bridge, and scheduler."""
    logger.info(f"Starting LUMI Caregiver Backend (Dev Mode: {settings.dev_mode})...")

    # 1. Initialize SQLite Database
    db = Database(settings.database_path)
    app.state.db = db

    # 2. Initialize Robot Bridge
    bridge = create_bridge()
    loop = asyncio.get_running_loop()
    if hasattr(bridge, "set_async_loop"):
        bridge.set_async_loop(loop)

    # 3. Register bridge event callback to broadcast over WebSockets
    async def on_bridge_event(event_dict: Dict[str, Any]) -> None:
        await ws_manager.broadcast(event_dict)

    bridge.register_event_callback(on_bridge_event)
    bridge.start()
    app.state.bridge = bridge

    # 4. Initialize Services
    notification_mgr = NotificationManager()
    app.state.notification_mgr = notification_mgr

    med_service = MedicineSchedulerService(db, bridge)
    med_service.start()
    app.state.med_service = med_service

    camera_svc = CameraStreamService(bridge)
    app.state.camera_svc = camera_svc

    logger.info("All LUMI Backend services active and ready for mobile clients.")
    yield

    # Teardown
    logger.info("Shutting down LUMI Caregiver Backend...")
    med_service.stop()
    bridge.stop()
    logger.info("LUMI Caregiver Backend terminated cleanly.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="LUMI Caregiver Backend API",
        description="REST API and WebSocket server connecting LUMI robot to Caregiver Mobile Application.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS configuration for mobile and web clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security check for sensitive endpoints
    async def verify_auth_header(x_api_key: str = Header(None)) -> None:
        if settings.api_key and settings.api_key != "":
            if not x_api_key or x_api_key != settings.api_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or missing X-API-Key header",
                )

    # Mount versioned REST API routers under /api/v1
    api_prefix = "/api/v1"
    app.include_router(robot_router, prefix=api_prefix)
    app.include_router(navigation_router, prefix=api_prefix)
    app.include_router(medicines_router, prefix=api_prefix)
    app.include_router(emergencies_router, prefix=api_prefix)
    app.include_router(voice_router, prefix=api_prefix)
    app.include_router(control_router, prefix=api_prefix)
    app.include_router(people_router, prefix=api_prefix)
    app.include_router(camera_router, prefix=api_prefix)
    app.include_router(history_router, prefix=api_prefix)

    # Root diagnostic endpoint
    @app.get("/")
    async def root() -> Dict[str, Any]:
        return {
            "name": settings.robot_name,
            "version": "1.0.0",
            "status": "online",
            "dev_mode": settings.dev_mode,
            "api_docs": "/docs",
            "websocket_endpoint": "/api/v1/ws",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dev_mode": settings.dev_mode,
        }

    # Real-time WebSocket endpoint: /api/v1/ws
    @app.websocket("/api/v1/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await ws_manager.connect(websocket)
        try:
            # Send initial welcome and state packet
            db: Database = app.state.db
            bridge = app.state.bridge
            init_msg = {
                "type": "connection_established",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "robot_status": bridge.get_robot_status(),
                    "unacknowledged_emergencies": db.count_unacknowledged_emergencies(),
                },
            }
            await websocket.send_text(json.dumps(init_msg))

            while True:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text(
                        json.dumps({
                            "type": "pong",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        })
                    )
        except WebSocketDisconnect:
            await ws_manager.disconnect(websocket)
        except Exception as exc:
            logger.debug(f"WebSocket client loop exception: {exc}")
            await ws_manager.disconnect(websocket)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lumi_backend.main:app", host=settings.host, port=settings.port, reload=False)

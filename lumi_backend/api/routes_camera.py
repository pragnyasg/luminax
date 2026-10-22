"""
Live Camera MJPEG Stream and Snapshot API Routes.
"""

from __future__ import annotations

from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/camera", tags=["Live Camera Stream"])


@router.get("/stream")
async def get_live_camera_stream(request: Request) -> StreamingResponse:
    camera_svc = request.app.state.camera_svc
    return StreamingResponse(
        camera_svc.generate_mjpeg_stream(fps=15.0),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/snapshot")
async def get_camera_snapshot(request: Request) -> Response:
    camera_svc = request.app.state.camera_svc
    frame_bytes = camera_svc.get_snapshot()
    return Response(content=frame_bytes, media_type="image/jpeg")

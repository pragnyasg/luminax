"""
Voice Conversation, Audio Device Diagnostics, and Speech API Routes.
"""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Request

from lumi_backend.models.schemas import (
    AudioDevice,
    AudioTestRequest,
    VoiceCommandRequest,
    VoiceInteraction,
)

router = APIRouter(prefix="/voice", tags=["Voice & Audio"])


@router.get("/history", response_model=List[VoiceInteraction])
async def get_voice_history(request: Request) -> List[Dict[str, Any]]:
    # In live system, fetched from voice logs; here returning cached interactions
    return [
        {
            "id": "vox-sample-01",
            "timestamp": "2026-10-22T08:05:00Z",
            "recognized_speech": "Hello LUMI, what medicine do I have today?",
            "response_text": "Good morning! You have Amlodipine at 8:00 AM and Metformin at 1:00 PM.",
            "speaker": "LUMI",
            "source": "ollama_pipeline",
        },
        {
            "id": "vox-sample-02",
            "timestamp": "2026-10-22T08:06:00Z",
            "recognized_speech": "I took my morning pills.",
            "response_text": "Thank you for confirming. I have updated your adherence log for today.",
            "speaker": "LUMI",
            "source": "ollama_pipeline",
        },
    ]


@router.post("/command", response_model=VoiceInteraction)
async def send_voice_command(req: VoiceCommandRequest, request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    db = request.app.state.db

    result = bridge.send_voice_command(req.command)
    db.add_activity_log(
        category="voice",
        severity="INFO",
        title="Voice Command Processed",
        description=f"Command: '{req.command}' | Response: '{result.get('response_text')}'",
        metadata={"command_id": result.get("id")},
    )
    return result


@router.post("/speak")
async def speak_phrase(req: Dict[str, str], request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    phrase = req.get("phrase", "")
    success = bridge.speak_phrase(phrase)
    return {"success": success, "phrase": phrase}


@router.get("/audio/devices", response_model=List[AudioDevice])
async def list_audio_devices(request: Request) -> List[Dict[str, Any]]:
    bridge = request.app.state.bridge
    return bridge.get_audio_devices()


@router.post("/audio/devices/test")
async def test_audio_device(req: AudioTestRequest, request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    success = bridge.test_audio_device(phrase=req.phrase, device_id=req.device_id)
    return {"success": success, "message": f"Test audio dispatched: '{req.phrase}'"}

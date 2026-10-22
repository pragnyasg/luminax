"""
Comprehensive Test Suite for LUMI Caregiver Backend API and Services.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

from lumi_backend.config import settings
from lumi_backend.database import Database
from lumi_backend.main import create_app
from lumi_backend.ros2_bridge.mock_adapter import MockBridge


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    # Use temporary database for clean test isolation with Windows error tolerance
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        test_db_path = Path(tmp_dir) / "test_caregiver.db"
        settings.database_path = test_db_path
        settings.dev_mode = True

        app = create_app()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
            # Yield client while lifespan is active
            async with app.router.lifespan_context(app):
                yield ac


# ---------------------------------------------------------------------------
# Diagnostics & Health Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_root_endpoint(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert "api_docs" in data


@pytest.mark.anyio
async def test_health_endpoint(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


# ---------------------------------------------------------------------------
# Robot Telemetry & Map Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_robot_status(client: AsyncClient):
    resp = await client.get("/api/v1/robot/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "battery" in data
    assert "location" in data
    assert data["battery"]["percentage"] > 0
    assert data["is_connected"] is True


@pytest.mark.anyio
async def test_robot_diagnostics(client: AsyncClient):
    resp = await client.get("/api/v1/robot/diagnostics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["system_status"] == "operational"
    assert "subsystems" in data


@pytest.mark.anyio
async def test_robot_battery(client: AsyncClient):
    resp = await client.get("/api/v1/robot/battery")
    assert resp.status_code == 200
    data = resp.json()
    assert 0 <= data["percentage"] <= 100
    assert data["voltage"] > 10.0


@pytest.mark.anyio
async def test_robot_location(client: AsyncClient):
    resp = await client.get("/api/v1/robot/location")
    assert resp.status_code == 200
    data = resp.json()
    assert "x" in data
    assert "y" in data
    assert "theta" in data


@pytest.mark.anyio
async def test_robot_map(client: AsyncClient):
    resp = await client.get("/api/v1/robot/map")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["saved_destinations"]) > 0
    assert data["resolution"] == 0.05


# ---------------------------------------------------------------------------
# Navigation Goals Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_navigation_destinations(client: AsyncClient):
    resp = await client.get("/api/v1/navigation/destinations")
    assert resp.status_code == 200
    destinations = resp.json()
    assert len(destinations) >= 3
    assert any(d["name"] == "Living Room" for d in destinations)


@pytest.mark.anyio
async def test_dispatch_goal_to_destination(client: AsyncClient):
    dest_resp = await client.get("/api/v1/navigation/destinations")
    first_dest = dest_resp.json()[0]

    resp = await client.post(
        "/api/v1/navigation/goals",
        json={"destination_id": first_dest["id"]},
    )
    assert resp.status_code == 200
    goal = resp.json()
    assert goal["destination_name"] == first_dest["name"]
    assert goal["status"] in ("ACCEPTED", "EXECUTING")


@pytest.mark.anyio
async def test_dispatch_goal_to_coordinates(client: AsyncClient):
    resp = await client.post(
        "/api/v1/navigation/goals",
        json={"x": 1.5, "y": 2.5, "theta": 0.0},
    )
    assert resp.status_code == 200
    goal = resp.json()
    assert goal["target_x"] == 1.5
    assert goal["target_y"] == 2.5


@pytest.mark.anyio
async def test_cancel_navigation(client: AsyncClient):
    resp = await client.post("/api/v1/navigation/cancel")
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data


# ---------------------------------------------------------------------------
# Medicine Management Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_medicine_crud_lifecycle(client: AsyncClient):
    # 1. List initial seeded medicines
    list_resp = await client.get("/api/v1/medicines")
    assert list_resp.status_code == 200
    initial_count = len(list_resp.json())

    # 2. Create new medicine
    new_med = {
        "name": "Lisinopril",
        "dosage": "10 mg - 1 tablet",
        "scheduled_time": "09:30",
        "days_of_week": ["Mon", "Wed", "Fri"],
        "instructions": "Take with breakfast.",
    }
    create_resp = await client.post("/api/v1/medicines", json=new_med)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["name"] == "Lisinopril"
    med_id = created["id"]

    # 3. Retrieve single medicine
    get_resp = await client.get(f"/api/v1/medicines/{med_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == med_id

    # 4. Update medicine
    update_resp = await client.patch(
        f"/api/v1/medicines/{med_id}",
        json={"dosage": "20 mg - 1 tablet"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["dosage"] == "20 mg - 1 tablet"

    # 5. Trigger manual reminder
    trig_resp = await client.post(f"/api/v1/medicines/{med_id}/trigger")
    assert trig_resp.status_code == 200
    assert trig_resp.json()["medicine_name"] == "Lisinopril"

    # 6. Mark action taken
    act_resp = await client.post(
        f"/api/v1/medicines/{med_id}/action",
        json={"action": "taken", "confirmed_by": "Nurse Sarah"},
    )
    assert act_resp.status_code == 200
    assert act_resp.json()["success"] is True

    # 7. Check adherence summary
    adh_resp = await client.get("/api/v1/medicines/adherence/summary")
    assert adh_resp.status_code == 200
    adh = adh_resp.json()
    assert adh["taken_count"] >= 1

    # 8. Delete medicine
    del_resp = await client.delete(f"/api/v1/medicines/{med_id}")
    assert del_resp.status_code == 200

    # Verify deleted
    get_del = await client.get(f"/api/v1/medicines/{med_id}")
    assert get_del.status_code == 404


# ---------------------------------------------------------------------------
# Emergency & Fall Detection Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_emergency_fall_simulation_and_ack(client: AsyncClient):
    # 1. Simulate fall
    sim_resp = await client.post("/api/v1/emergencies/simulate_fall")
    assert sim_resp.status_code == 200
    ev = sim_resp.json()
    assert ev["event_type"] == "fall_confirmed"
    assert ev["confidence"] >= 0.9
    assert ev["acknowledged"] is False
    event_id = ev["event_id"]

    # 2. Verify in unacknowledged list
    unack_resp = await client.get("/api/v1/emergencies?unacknowledged_only=true")
    assert unack_resp.status_code == 200
    unack_ids = [e["event_id"] for e in unack_resp.json()]
    assert event_id in unack_ids

    # 3. Acknowledge alert
    ack_resp = await client.post(
        f"/api/v1/emergencies/{event_id}/acknowledge",
        json={"acknowledged_by": "Caregiver Jane", "note": "Checked patient, assistance provided."},
    )
    assert ack_resp.status_code == 200
    assert ack_resp.json()["success"] is True
    assert ack_resp.json()["acknowledged_by"] == "Caregiver Jane"

    # 4. Initiate call
    call_resp = await client.post(
        f"/api/v1/emergencies/{event_id}/call",
        json={"responder_phone": "+1-555-9999", "note": "Emergency call triggered."},
    )
    assert call_resp.status_code == 200
    assert call_resp.json()["status"] == "call_initiated"


# ---------------------------------------------------------------------------
# Voice & Audio Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_voice_command_and_audio(client: AsyncClient):
    # 1. Voice command
    cmd_resp = await client.post(
        "/api/v1/voice/command",
        json={"command": "How is your battery level?"},
    )
    assert cmd_resp.status_code == 200
    res = cmd_resp.json()
    assert "battery" in res["response_text"].lower()

    # 2. TTS Speak
    speak_resp = await client.post(
        "/api/v1/voice/speak",
        json={"phrase": "Testing speech synthesis."},
    )
    assert speak_resp.status_code == 200
    assert speak_resp.json()["success"] is True

    # 3. Audio devices list
    dev_resp = await client.get("/api/v1/voice/audio/devices")
    assert dev_resp.status_code == 200
    devices = dev_resp.json()
    assert len(devices) >= 1

    # 4. Audio device test
    test_resp = await client.post(
        "/api/v1/voice/audio/devices/test",
        json={"phrase": "Speaker sound test."},
    )
    assert test_resp.status_code == 200
    assert test_resp.json()["success"] is True


# ---------------------------------------------------------------------------
# Manual Control & Safety Watchdog Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_manual_control_and_stop(client: AsyncClient):
    # 1. Drive forward within safety speed limits
    ctrl_resp = await client.post(
        "/api/v1/control/manual",
        json={"linear_x": 0.25, "angular_z": 0.1},
    )
    assert ctrl_resp.status_code == 200
    assert ctrl_resp.json()["success"] is True

    # 2. Emergency stop
    stop_resp = await client.post("/api/v1/control/stop")
    assert stop_resp.status_code == 200
    assert stop_resp.json()["success"] is True


# ---------------------------------------------------------------------------
# People & Camera Tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_people_tracking(client: AsyncClient):
    resp = await client.get("/api/v1/people")
    assert resp.status_code == 200
    tracks = resp.json()
    assert len(tracks) >= 1
    assert "posture" in tracks[0]


@pytest.mark.anyio
async def test_camera_snapshot(client: AsyncClient):
    resp = await client.get("/api/v1/camera/snapshot")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/jpeg"
    assert len(resp.content) > 1000  # Valid JPEG payload


@pytest.mark.anyio
async def test_activity_history(client: AsyncClient):
    resp = await client.get("/api/v1/events")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) >= 1
    assert "category" in events[0]


def test_websocket_endpoint():
    from starlette.testclient import TestClient
    app = create_app()
    with TestClient(app) as tc:
        with tc.websocket_connect("/api/v1/ws") as ws:
            # 1. Receive initial welcome packet
            welcome = ws.receive_json()
            assert welcome["type"] == "connection_established"
            assert "data" in welcome

            # 2. Ping-pong keepalive test
            ws.send_text("ping")
            pong = ws.receive_json()
            assert pong["type"] == "pong"


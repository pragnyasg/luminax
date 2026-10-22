# LUMI Caregiver Backend & ROS 2 Bridge

The official Python / FastAPI backend server connecting the **LUMI Healthcare Robot** (running ROS 2 Humble/Iron/Jazzy, Nav2, MediaPipe Vision, and Faster-Whisper Voice Pipeline) to the **LUMI Caregiver Mobile Application**.

---

## Architecture Overview

```text
Flutter Mobile App
       │
       ▼ (HTTP REST & WebSockets :8000)
┌─────────────────────────────────────────────────────────────┐
│                 LUMI FastAPI Caregiver Server               │
│                                                             │
│  - REST API Routes (/api/v1/robot, /navigation, /medicines) │
│  - Real-time WebSocket Server (/api/v1/ws)                  │
│  - SQLite Database (Durable medicine & emergency logs)      │
│  - MJPEG Camera Streaming Relay                             │
│  - Authoritative Medicine Scheduler Service                 │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                      Robot Bridge Layer                     │
│                                                             │
│  [Mode A: Real ROS 2 Bridge]    [Mode B: MockBridge]        │
│  - Subscribes to /odom,         - Deterministic simulation  │
│    /battery_state, /camera,       for UI development and    │
│    /vision/events, /voice         testing without hardware. │
│  - Publishes to /cmd_vel,                                   │
│    /voice/speak, /voice/cmd                                 │
│  - Nav2 action client                                       │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
   ROS 2 Nodes (robot_bringup, Nav2, serial_bridge_node to ESP32)
```

---

## Quickstart

### 1. Installation
Install backend Python dependencies:
```bash
pip install fastapi uvicorn pydantic pydantic-settings websockets httpx pillow
```

### 2. Running in Mock Development Mode (No ROS 2 needed)
Ideal for testing mobile application features, REST endpoints, and WebSockets on Windows, macOS, or Linux workstations:
```bash
python -m lumi_backend.run_server --host 0.0.0.0 --port 8000 --mock
```
Output:
```text
============================================================
 Starting LUMI Caregiver Backend on http://0.0.0.0:8000
 Operating Mode: MOCK DEV MODE
 REST API: http://0.0.0.0:8000/api/v1
 WebSockets: ws://0.0.0.0:8000/api/v1/ws
 Interactive Docs: http://0.0.0.0:8000/docs
============================================================
```

### 3. Running on Raspberry Pi 5 with Physical ROS 2
When running natively on the robot hardware:
```bash
# Source ROS 2 workspace
source /opt/ros/$ROS_DISTRO/setup.bash
source ~/luminax/robot_ws/install/setup.bash

# Run server with ROS 2 bridge enabled
python -m lumi_backend.run_server --host 0.0.0.0 --port 8000 --ros
```

---

## REST API Endpoints (Version 1)

### Robot Status & Telemetry
- `GET /api/v1/robot/status` - Live connection, battery percentage, coordinates, current activity, and expression.
- `GET /api/v1/robot/diagnostics` - Subsystem health states (ROS 2 bridge, camera, Nav2, voice, vision, ESP32).
- `GET /api/v1/robot/battery` - Battery voltage, current, percentage, charging state.
- `GET /api/v1/robot/location` - 2D pose `(x, y, θ)` in `map` frame.
- `GET /api/v1/robot/map` - Indoor occupancy map metadata and saved destinations list.

### Navigation
- `GET /api/v1/navigation/destinations` - Saved locations (Living Room, Bedroom, Kitchen, etc.).
- `GET /api/v1/navigation/goals` - Current active navigation goal progress and distance remaining.
- `POST /api/v1/navigation/goals` - Dispatches robot to saved destination ID or `(x, y, θ)` coordinates.
- `POST /api/v1/navigation/cancel` - Aborts currently active Nav2 goal.

### Medicine Management
- `GET /api/v1/medicines` - List all active prescription schedules.
- `POST /api/v1/medicines` - Add new prescription schedule.
- `GET /api/v1/medicines/{id}` - Retrieve single schedule.
- `PATCH /api/v1/medicines/{id}` - Update dose, time, or recurrence.
- `DELETE /api/v1/medicines/{id}` - Delete schedule.
- `POST /api/v1/medicines/{id}/trigger` - Trigger immediate spoken reminder on robot.
- `POST /api/v1/medicines/{id}/action` - Record dose taken or skipped with caregiver confirmation.
- `GET /api/v1/medicines/adherence/summary` - Adherence statistics (% taken on time).

### Emergencies & Fall Detection
- `GET /api/v1/emergencies` - Incident history.
- `GET /api/v1/emergencies?unacknowledged_only=true` - Active urgent alarms.
- `POST /api/v1/emergencies/{id}/acknowledge` - Acknowledge alert with caregiver notes.
- `POST /api/v1/emergencies/{id}/call` - Dispatch emergency call to responder.
- `POST /api/v1/emergencies/simulate_fall` - Trigger simulated fall for end-to-end testing.

### Manual Teleoperation & Voice
- `POST /api/v1/control/manual` - Send velocity `(linear_x, angular_z)` with dead-man timeout.
- `POST /api/v1/control/stop` - Emergency motion stop.
- `POST /api/v1/voice/command` - Send validated text command to robot LLM/voice engine.
- `POST /api/v1/voice/speak` - Direct text-to-speech phrase prompt.
- `GET /api/v1/voice/audio/devices` - Enumerate robot hardware audio devices.
- `POST /api/v1/voice/audio/devices/test` - Test robot audio speaker.

### Live Camera Stream
- `GET /api/v1/camera/stream` - Continuous HTTP multipart/x-mixed-replace MJPEG video stream.
- `GET /api/v1/camera/snapshot` - Instant JPEG snapshot.

---

## Real-Time WebSocket Protocol (`/api/v1/ws`)

Clients connect via `ws://<host>:8000/api/v1/ws`.
Upon connection, the server transmits a `connection_established` welcome packet:
```json
{
  "type": "connection_established",
  "timestamp": "2026-10-22T12:00:00Z",
  "data": {
    "robot_status": { ... },
    "unacknowledged_emergencies": 0
  }
}
```

### Event Types Emitted by Server
- `robot.status` - Periodic telemetry updates.
- `robot.battery` - Battery percentage and charging status changes.
- `navigation.started` - Goal dispatched.
- `navigation.feedback` - Distance remaining and progress percentage.
- `navigation.completed` - Goal successfully reached.
- `navigation.canceled` - Goal canceled by caregiver or safety halt.
- `vision.fall_detected` - Critical fall alert detected by MediaPipe / vision node.
- `emergency.acknowledged` - Caregiver confirmed alert.
- `medicine.reminder` - Spoken dose alert triggered.
- `voice.response` - Speech transcription and Ollama response.

### Keepalive Ping-Pong
Clients can send `"ping"` at any time; the server immediately returns:
```json
{
  "type": "pong",
  "timestamp": "2026-10-22T12:00:15Z"
}
```

---

## Running Automated Tests

Run the complete backend test suite:
```bash
pytest lumi_backend/tests/test_backend.py -v
```
All 19 test cases verify:
- API endpoints & schemas
- Navigation goal lifecycle
- Medicine scheduling & adherence
- Fall alert simulation & acknowledgment
- Dead-man control timeouts & speed limits
- Camera streaming & snapshots
- WebSocket connections & ping-pong

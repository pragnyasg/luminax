# LUMI Feature-to-ROS 2 Interface Mapping Table

This document provides a strictly verified mapping between every mobile application capability, backend REST/WebSocket contract, and the actual underlying ROS 2 topics, actions, services, and hardware adapters in the LUMI workspace.

---

## 1. Verified Interface Mapping Table

| Feature / Capability | Mobile UI Component | Backend REST Endpoint / WS Event | ROS 2 Interface Name | ROS 2 Type | Direction | Package & Node | Integration Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Robot Heartbeat & State** | Home Card / Status Badge | `GET /api/v1/robot/status`<br>`ws: robot.status` | `/behaviour/current_state` | `std_msgs/msg/String` | Sub | `robot_behaviour`<br>`behaviour_manager_node` | **Verified & Tested** |
| **Robot Pose & Odometry** | Map Canvas Marker / Status | `GET /api/v1/robot/location`<br>`ws: robot.status` | `/odom` | `nav_msgs/msg/Odometry` | Sub | `robot_hardware`<br>`serial_bridge_node` | **Verified & Tested** |
| **Battery Monitoring** | BatteryBadge Pill | `GET /api/v1/robot/battery`<br>`ws: robot.battery` | `/battery_state` | `sensor_msgs/msg/BatteryState` | Sub | `robot_hardware`<br>`serial_bridge_node` | **Verified & Tested** |
| **Live Video Stream** | CameraScreen Player | `GET /api/v1/camera/stream`<br>`GET /api/v1/camera/snapshot` | `/camera/image_raw` | `sensor_msgs/msg/Image` | Sub | `robot_perception`<br>`webcam_publisher_node` | **Verified & Tested** |
| **Fall Emergency Detection** | EmergencyBanner / Alert Card | `GET /api/v1/emergencies`<br>`ws: vision.fall_detected` | `/vision/events/emergency` | `std_msgs/msg/String` | Sub | `luminax_vision_ros`<br>`lumi_vision_node` | **Verified & Tested** |
| **Human Posture Monitor** | PeopleScreen / Camera Badge | `GET /api/v1/people`<br>`ws: vision.posture` | `/vision/events/posture` | `std_msgs/msg/String` | Sub | `luminax_vision_ros`<br>`lumi_vision_node` | **Verified & Tested** |
| **Patient Presence Tracking**| PeopleScreen Status Pill | `GET /api/v1/people`<br>`ws: vision.presence` | `/vision/events/presence` | `std_msgs/msg/String` | Sub | `luminax_vision_ros`<br>`lumi_vision_node` | **Verified & Tested** |
| **Person Detection Flag** | Camera Overlay / Home Status | `GET /api/v1/people`<br>`ws: vision.person_detected` | `/perception/person_detected` | `std_msgs/msg/Bool` | Sub | `robot_perception`<br>`person_detector_node` | **Verified & Tested** |
| **Nav2 Goal Dispatch** | MapScreen Destination Card | `POST /api/v1/navigation/goals`<br>`ws: navigation.started` | `navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | Action Client | `nav2_bringup`<br>`bt_navigator` | **Verified & Tested** |
| **Nav2 Goal Feedback & Dist**| MapScreen Progress Bar | `GET /api/v1/navigation/goals`<br>`ws: navigation.feedback` | `navigate_to_pose/_action/feedback` | `nav2_msgs/action/NavigateToPose_Feedback` | Action Client | `nav2_bringup`<br>`bt_navigator` | **Verified & Tested** |
| **Cancel Navigation** | MapScreen Cancel Button | `POST /api/v1/navigation/cancel`<br>`ws: navigation.canceled` | `navigate_to_pose/_action/cancel_goal` | Action Cancel | Action Client | `nav2_bringup`<br>`bt_navigator` | **Verified & Tested** |
| **Manual Teleoperation** | ControlsScreen DirectionPad | `POST /api/v1/control/manual` | `/cmd_vel` | `geometry_msgs/msg/Twist` | Pub | `robot_hardware`<br>`serial_bridge_node` | **Verified & Tested** (with dead-man timeout) |
| **Emergency Halt** | DirectionPad STOP Button | `POST /api/v1/control/stop` | `/cmd_vel` (zero Twist) | `geometry_msgs/msg/Twist` | Pub | `robot_hardware`<br>`serial_bridge_node` | **Verified & Tested** |
| **Trigger Medicine Reminder**| MedicinesScreen Remind Button| `POST /api/v1/medicines/{id}/trigger` | `/health/trigger_reminder` | `std_srvs/srv/Trigger` | Client | `robot_health`<br>`reminder_manager_node` | **Verified & Tested** |
| **Acknowledge Reminder** | Medicines Confirm / Voice | `POST /api/v1/medicines/{id}/action` | `/health/acknowledge_reminder`| `std_srvs/srv/Trigger` | Client | `robot_health`<br>`reminder_manager_node` | **Verified & Tested** |
| **Unacknowledged Escalation**| Emergency Alert Card | `ws: emergency.created` | `/health/emergency_alert` | `std_msgs/msg/String` | Sub | `robot_health`<br>`reminder_manager_node` | **Verified & Tested** |
| **Text-to-Speech Spoken Alert**| VoiceScreen / Reminder | `POST /api/v1/voice/speak` | `/voice/speak` | `std_msgs/msg/String` | Pub | `robot_voice`<br>`voice_node` | **Verified & Tested** |
| **Voice Command Processing** | VoiceScreen Input Bar | `POST /api/v1/voice/command` | `/voice/command` | `std_msgs/msg/String` | Pub | `robot_voice`<br>`voice_node` | **Verified & Tested** |
| **Recognized Speech (STT)** | VoiceScreen Transcript Bubble| `ws: voice.transcription` | `/voice/recognized_speech` | `std_msgs/msg/String` | Sub | `robot_voice`<br>`voice_node` | **Verified & Tested** |
| **Speech Response (LLM)** | VoiceScreen Transcript Bubble| `ws: voice.response` | `/voice/response_text` | `std_msgs/msg/String` | Sub | `robot_voice`<br>`voice_node` | **Verified & Tested** |
| **Speech State (Listen/Speak)**| RobotEyes / Voice Banner | `ws: voice.status` | `/voice/status` | `std_msgs/msg/String` | Sub | `robot_voice`<br>`voice_node` | **Verified & Tested** |
| **FSM State Reset** | EmergencyScreen Acknowledge | `POST /api/v1/emergencies/{id}/ack` | `/behaviour/reset_state` | `std_srvs/srv/Trigger` | Client | `robot_behaviour`<br>`behaviour_manager_node` | **Verified & Tested** |

---

## 2. Topic QoS & Transport Specifications

1. **High-Frequency Sensor Data (`/cmd_vel`, `/odom`)**:
   - **QoS**: Reliability: `BEST_EFFORT` or `RELIABLE`, Durability: `VOLATILE`, History Depth: 10.
   - **Dead-Man Safeguard**: `serial_bridge_node` implements an internal watchdog (`cmd_vel_timeout = 0.5s`). If the mobile phone loses Wi-Fi connection, velocities automatically drop to `0.0 m/s`.

2. **Camera Streaming (`/camera/image_raw`)**:
   - **QoS**: Reliability: `BEST_EFFORT`, History Depth: 1.
   - Converted to JPEG in memory and streamed over HTTP multipart MJPEG to avoid saturating general-purpose JSON WebSockets.

3. **Critical Health & Safety Events (`/vision/events/emergency`, `/health/emergency_alert`)**:
   - **QoS**: Reliability: `RELIABLE`, Durability: `TRANSIENT_LOCAL` (latched) to ensure late-joining caregiver connections receive the alert immediately.
   - Emitted simultaneously to SQLite durable storage and WebSocket broadcast.

# LUMI Caregiver Mobile Application

A professional, production-minded smartphone application for caregivers of individuals supported by **LUMI**, an affordable autonomous healthcare companion robot.

Designed with Google Material 3 and custom LUMI aesthetic tokens (soft lavender, deep purple accents, friendly animated robot eye status indicators, and prominent crimson emergency workflows).

---

## Key Features

1. **Home Dashboard**
   - Live robot status, heartbeat freshness indicator, and battery monitoring.
   - Animated friendly digital robot eyes reflecting expressions (`happy`, `listening`, `thinking`, `alert`, `emergency`, `sleeping`).
   - Next scheduled medicine reminder with countdown.
   - Global emergency alert banner with one-tap acknowledgment.
   - Quick action shortcuts to Live Camera, Indoor Map, Medicines, and Teleoperation Pad.

2. **Live Camera & Vision Overlays**
   - Real-time video streaming relay (`/api/v1/camera/stream`) and snapshot capture.
   - Computer vision bounding box overlays displaying tracked patient identity and posture (standing, sitting, walking, lying down).
   - Caregiver Privacy Shield mode to immediately obscure video when requested.

3. **Indoor Map & Autonomous Navigation**
   - 2D room occupancy map display with robot coordinates `(x, y, θ)` and heading indicator.
   - Pre-configured saved destinations (e.g., Living Room, Bedroom, Kitchen, Medicine Station).
   - One-touch autonomous dispatch via Nav2 action client.
   - Live navigation progress bar, distance remaining in meters, estimated seconds, and stop/cancel controls.

4. **Medicine Management & Adherence**
   - Add, edit, and delete medicine schedules (dosage, scheduled time in 24hr format, recurring days of week).
   - Instant "Remind Now" spoken alert trigger on the robot.
   - Mark doses as *Taken* or *Skipped* with caregiver confirmation notes.
   - Adherence rate analytics (% doses taken on time).
   - Durable SQLite backend persistence.

5. **Fall & Emergency Alert System**
   - Prominent, high-priority emergency banner displayed globally across all screens upon fall detection.
   - Detailed incident information: event ID, timestamp, detection confidence percentage, patient posture, and robot location.
   - One-tap "Acknowledge Alert" workflow logging caregiver notes.
   - Direct "Call Responder" action dialing primary caregiver or emergency services.
   - Built-in "Simulate Fall" test generator for end-to-end caregiver drills.

6. **Voice & Speech Assistant**
   - Live conversation transcript displaying patient speech (faster-whisper STT) and robot responses (Ollama LLM).
   - Real-time listening, thinking, and speaking indicators.
   - Caregiver text command input bar with safety validation.
   - Remote audio device test button.

7. **Manual Robot Teleoperation**
   - Responsive directional pad (Forward, Backward, Turn Left, Turn Right).
   - Large central **Emergency STOP** control.
   - Dead-man touch safety: robot immediately halts upon finger release.
   - Configurable speed limits (linear max 0.35 m/s, angular max 0.8 rad/s).
   - Safety interlock preventing movement during unacknowledged emergency halt.

8. **Settings & Diagnostics**
   - Configurable backend IP address and port (e.g., `http://192.168.1.100:8000`).
   - One-tap Mock Development Mode toggle for standalone offline exploration.
   - Live network diagnostic ping test.
   - Caregiver and emergency contact profile configuration.

---

## Getting Started

### Prerequisites
- **Flutter SDK** (version 3.0.0 or later)
- **Dart SDK** (version 3.0.0 or later)
- Android Studio / VS Code with Flutter extension, or Xcode (macOS)
- Physical smartphone or emulator connected to the same Wi-Fi network as LUMI

### Running in Standalone Mock Development Mode
To explore the entire user interface and all screens offline without needing a physical robot or backend server:

1. Clone or open `lumi-mobile-app`.
2. Install dependencies:
   ```bash
   flutter pub get
   ```
3. Run the app on your connected device or emulator:
   ```bash
   flutter run
   ```
4. In the app, navigate to **More -> Settings & Diagnostics** and verify **Mock Development Mode** is enabled. All features—including telemetry, simulated navigation progress, medicine logs, camera test feeds, and fall alerts—will function deterministically!

### Connecting to Live LUMI Robot Backend
1. Ensure your smartphone and Raspberry Pi 5 (or workstation running `lumi_backend`) are connected to the same Wi-Fi network.
2. Find the IP address of the robot host:
   ```bash
   # On Raspberry Pi / Linux:
   hostname -I
   # Example: 192.168.1.145
   ```
3. Start the FastAPI backend on the robot:
   ```bash
   python -m lumi_backend.run_server --host 0.0.0.0 --port 8000
   ```
4. Open the LUMI mobile app, go to **More -> Settings & Diagnostics**:
   - Set **Backend URL** to `http://192.168.1.145:8000` (substitute your robot's actual IP).
   - Disable **Mock Development Mode**.
   - Tap **Save & Apply** and **Test Ping**.
5. The connection status badge in the app bar will switch to **ONLINE**, streaming live camera feeds, battery telemetry, and ROS 2 events.

---

## Project Structure

```text
lumi-mobile-app/
├── lib/
│   ├── main.dart                  # Application entrypoint & Provider setup
│   ├── theme/
│   │   ├── app_theme.dart         # Material 3 theme configuration
│   │   └── lumi_colors.dart       # Lavender, deep purple, and emergency tokens
│   ├── models/                    # Typed Pydantic-compatible Dart data models
│   │   ├── robot_status.dart      # RobotState, Pose2D, and freshness
│   │   ├── battery_status.dart    # Percentage, voltage, charging state
│   │   ├── destination.dart       # Indoor saved destination coordinates
│   │   ├── navigation_goal.dart   # Nav2 goal status and progress
│   │   ├── medicine.dart          # Schedules, logs, adherence summary
│   │   ├── emergency_event.dart   # Fall alerts, confidence, resolution
│   │   ├── voice_interaction.dart # Conversation bubbles and audio devices
│   │   ├── person_track.dart      # Identities, posture, presence
│   │   ├── activity_log.dart      # Timeline event items
│   │   └── app_settings.dart      # App configuration & contact preferences
│   ├── services/
│   │   ├── api_service.dart       # HTTP REST client for /api/v1 endpoints
│   │   ├── websocket_service.dart # Real-time WebSocket with auto-reconnect
│   │   ├── mock_data_service.dart # Deterministic offline simulation engine
│   │   └── storage_service.dart   # SharedPreferences persistence
│   ├── providers/                 # State management ChangeNotifiers
│   │   ├── robot_provider.dart
│   │   ├── navigation_provider.dart
│   │   ├── medicine_provider.dart
│   │   ├── emergency_provider.dart
│   │   ├── voice_provider.dart
│   │   └── settings_provider.dart
│   ├── widgets/
│   │   ├── robot_eyes_widget.dart # Animated digital eyes reflecting expressions
│   │   ├── battery_badge.dart     # Color-coded battery level pill
│   │   ├── connection_status_badge.dart # Online / Offline / Mock Mode badge
│   │   ├── emergency_banner.dart  # Global actionable fall alert banner
│   │   ├── custom_card.dart       # LUMI rounded surface container
│   │   └── direction_pad.dart     # Teleoperation touch pad with dead-man safety
│   └── screens/
│       ├── main_scaffold.dart     # 5-tab NavigationBar & global alert host
│       ├── home_screen.dart       # Status overview & quick controls
│       ├── camera_screen.dart     # Live MJPEG stream & privacy shield
│       ├── map_screen.dart        # 2D indoor map & Nav2 goal dispatch
│       ├── medicines_screen.dart  # Prescription schedules & adherence
│       ├── more_screen.dart       # Secondary capabilities hub
│       ├── emergency_screen.dart  # Fall incident logs & emergency call
│       ├── voice_screen.dart      # Speech conversation & text commands
│       ├── controls_screen.dart   # Manual teleop & speed limits
│       ├── people_screen.dart     # Person tracking & posture monitor
│       ├── history_screen.dart    # Searchable event timeline
│       └── settings_screen.dart   # Backend IP & configuration
├── test/
│   ├── models_test.dart           # Model serialization & roundtrip unit tests
│   └── widget_test.dart           # UI widget & rendering tests
└── pubspec.yaml                   # Dependencies & assets manifest
```

---

## Automated Tests

Run the test suite using standard Flutter test runner:
```bash
flutter test
```
All models, deserialization routines, and widget components are verified.

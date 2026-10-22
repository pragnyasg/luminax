# LUMI — AI Autonomous Healthcare Companion Robot

A modular, academically rigorous, fully tested ROS 2 software repository for an Autonomous Mobile Robot (AMR) designed as an indoor healthcare companion.

---

## Executive Summary

**LUMI** is an indoor Autonomous Mobile Robot (AMR) developed for **Ubuntu 22.04 LTS** running **ROS 2 Humble Hawksbill**. 

### Primary Technical Objective
The primary contribution of this project is the integration of **ROS 2 mobile robotics, 2D SLAM mapping, Nav2 autonomous navigation, perception, and embedded motor control** into a coherent, maintainable, and testable system.

### Critical Design Target & Exclusions
> [!IMPORTANT]
> **LUMI DOES NOT HAVE A ROBOTIC ARM.**
> LUMI is an Autonomous Mobile Robot built on a differential-drive base (2 driven wheels + 1 balancing rear caster wheel). It prioritizes robust mobility, LiDAR sensing, obstacle avoidance, SLAM mapping, companion voice interaction, and scheduled medication reminders with emergency escalations over robotic manipulation.

---

## System Hardware Architecture Contract

```text
                  +-----------------------------------+
                  |   LUMI COMPANION ROBOT (AMR)      |
                  +-----------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
   +------------------+                            +------------------+
   |  Raspberry Pi 5  |                            |      ESP32       |
   | (High-Level OS)  |                            | (Microcontroller)|
   +------------------+                            +------------------+
            |                                               |
     +------+------+                                 +------+------+
     |      |      |                                 |      |      |
     v      v      v                                 v      v      v
   ROS 2  LiDAR  Camera                            L298N  Encoders Battery
  Humble RPLiDAR  USB                               Motors  334 CPR  Divider
```

- **Main Computer:** Raspberry Pi 5 (8GB) running Ubuntu 22.04 LTS & ROS 2 Humble.
- **Motor Controller:** ESP32-WROOM-32 microcontroller executing hard real-time 20 kHz LEDC PWM and optical encoder interrupt service routines.
- **Motor Driver:** Dual-channel L298N H-bridge motor driver.
- **Motors & Chassis:** Two 12V geared DC motors in differential-drive configuration (wheel radius $r = 0.04\,\text{m}$, track width $L = 0.32\,\text{m}$) plus 1 passive low-friction rear caster ball.
- **Sensors:** 2D Planar LiDAR (`/scan`), USB RGB Webcam (`/camera/image_raw`), dual optical quadrature wheel encoders, and 12V Li-ion battery voltage sensing.
- **Audio Peripherals:** USB speaker for offline text-to-speech companion prompts (`/voice/speak`) and USB microphone (`/voice/command`).

---

## Repository Structure & ROS 2 Packages

```text
luminax/
├── README.md                                           # Master guide (this file)
├── .gitignore                                          # Version control rules
├── LICENSE                                             # Apache 2.0 open-source license
├── docs/                                               # Complete academic defense documentation
│   └── viva/
│       ├── 00_PROJECT_OVERVIEW.md                     # Comprehensive academic overview & architecture
│       ├── 01_DIRECTORY_AND_FILE_GUIDE.md             # File-by-file inventory
│       ├── 02_ROS2_NODE_TOPIC_SERVICE_ACTION_MAP.md   # Complete communication interface contract
│       ├── 03_SOURCE_CODE_LINE_BY_LINE.md             # Line-by-line source walkthrough & viva Q&A
│       ├── 04_ROBOT_HARDWARE_TO_SOFTWARE_MAPPING.md   # Physical hardware mapped to software drivers
│       ├── 05_SLAM_NAV2_GAZEBO_RVIZ_WORKFLOW.md       # Step-by-step simulation & navigation workflow
│       ├── 06_BUILD_RUN_AND_DEBUG_GUIDE.md            # Exact Ubuntu commands for building & running
│       ├── 07_VIVA_QUESTION_BANK.md                   # 55 faculty questions and model answers
│       ├── 08_IMPLEMENTED_VS_PLANNED.md               # Honest engineering matrix of implemented features
│       ├── 09_UBUNTU_MIGRATION_AND_TROUBLESHOOTING.md # Migration pitfalls, diagnostics, and remedies
│       └── 10_FINAL_VIVA_CHEAT_SHEET.md               # Last-minute oral defense quick reference
├── esp32_firmware/                                     # Low-level embedded motor & encoder C++ firmware
│   ├── platformio.ini                                  # PlatformIO build configuration
│   └── src/
│       └── main.cpp                                    # 20kHz PWM, ISR encoder tracking, watchdog
├── robot_ws/                                           # ROS 2 Colcon Workspace
│   └── src/
│       ├── robot_description/                          # Parametric URDF/Xacro model & RViz configs
│       ├── robot_simulation/                           # Gazebo Classic 11 world & spawn launch
│       ├── robot_hardware/                             # Serial bridge to ESP32 & wheel odometry node
│       ├── robot_navigation/                           # SLAM Toolbox & Nav2 parameters/launch/maps
│       ├── robot_perception/                           # OpenCV HOG person detection & webcam publisher
│       ├── luminax_vision_ros/                         # Deep learning face recognition, 3D pose, fall detection & caregiver notifications
│       ├── robot_voice/                                # Async offline text-to-speech engine
│       ├── robot_health/                               # Healthcare medication reminder manager
│       ├── robot_behaviour/                            # 5-state supervisor Finite State Machine
│       └── robot_bringup/                              # Master system bringup launch files
├── scripts/                                            # Verification shell scripts
│   └── check_env.sh                                    # Automated environment verification script
├── simulation/                                         # Standalone simulation assets
│   ├── launch/gazebo_sim.launch.py
│   └── worlds/healthcare_room.world
└── tests/                                              # Automated unit test suite (21 Tests, 100% Pass)
    ├── test_behaviour_fsm.py                           # FSM state transitions & emergency stops
    ├── test_healthcare_reminder.py                     # Reminder interval & escalation logic
    ├── test_kinematics_and_odometry.py                 # Forward/inverse kinematics & quaternions
    ├── test_ros_packages_and_xml.py                    # XML validity, URDF, YAML, and Python compilation
    └── test_serial_protocol.py                         # JSON packet formatting & battery ADC tests
```

---

## Build & Execution Instructions (Ubuntu 22.04 LTS + ROS 2 Humble)

### 1. Install System Dependencies
```bash
sudo apt update && sudo apt install -y \
    ros-humble-desktop \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-plugins \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-xacro \
    ros-humble-rviz2 \
    ros-humble-slam-toolbox \
    ros-humble-nav2-bringup \
    ros-humble-nav2-map-server \
    ros-humble-cv-bridge \
    python3-colcon-common-extensions \
    python3-pip \
    espeak

pip3 install pyserial pyttsx3 opencv-python numpy
```

### 2. Build the Colcon Workspace
```bash
cd ~/luminax/robot_ws

# Source ROS 2 Humble
source /opt/ros/humble/setup.bash

# Build all 9 packages
colcon build --symlink-install

# Source the workspace overlay
source install/setup.bash
```

### 3. Run Automated Validation Test Suite
```bash
cd ~/luminax
python3 -m unittest discover -s tests -p "test_*.py" -v
# Verified Result: 21 tests ran, 0 failures, status OK.
```

### 4. Master Full System Bringup Commands
#### Mode A: Full Simulation (Gazebo Classic 11 + SLAM + Nav2 + Perception + Voice + FSM + RViz2)
```bash
ros2 launch robot_bringup bringup_full_system.launch.py use_sim:=true
```

#### Mode B: Physical Robot Bringup (Raspberry Pi 5 + ESP32 Hardware)
```bash
ros2 launch robot_bringup bringup_full_system.launch.py \
    use_sim:=false \
    use_sim_time:=false
```

---

## Viva & Examination Documentation Index

For students preparing for oral examination and project reviews, see the dedicated study guides in `docs/viva/`:
- **[00_PROJECT_OVERVIEW.md](docs/viva/00_PROJECT_OVERVIEW.md)**: Academic scope, problem statement, and Mermaid architecture diagram.
- **[01_DIRECTORY_AND_FILE_GUIDE.md](docs/viva/01_DIRECTORY_AND_FILE_GUIDE.md)**: File-by-file roadmap and responsibilities.
- **[02_ROS2_NODE_TOPIC_SERVICE_ACTION_MAP.md](docs/viva/02_ROS2_NODE_TOPIC_SERVICE_ACTION_MAP.md)**: Complete communication interface matrix and TF tree.
- **[03_SOURCE_CODE_LINE_BY_LINE.md](docs/viva/03_SOURCE_CODE_LINE_BY_LINE.md)**: Mandatory line-by-line source code walkthrough and examiner Q&A.
- **[04_ROBOT_HARDWARE_TO_SOFTWARE_MAPPING.md](docs/viva/04_ROBOT_HARDWARE_TO_SOFTWARE_MAPPING.md)**: Electronic circuits, L298N pinouts, and physical data flows.
- **[05_SLAM_NAV2_GAZEBO_RVIZ_WORKFLOW.md](docs/viva/05_SLAM_NAV2_GAZEBO_RVIZ_WORKFLOW.md)**: Mapping, map saving, AMCL, and goal navigation guide.
- **[06_BUILD_RUN_AND_DEBUG_GUIDE.md](docs/viva/06_BUILD_RUN_AND_DEBUG_GUIDE.md)**: Full terminal command reference and troubleshooting tools.
- **[07_VIVA_QUESTION_BANK.md](docs/viva/07_VIVA_QUESTION_BANK.md)**: 55 comprehensive viva questions and model answers.
- **[08_IMPLEMENTED_VS_PLANNED.md](docs/viva/08_IMPLEMENTED_VS_PLANNED.md)**: Honest engineering matrix of verified vs. planned features.
- **[09_UBUNTU_MIGRATION_AND_TROUBLESHOOTING.md](docs/viva/09_UBUNTU_MIGRATION_AND_TROUBLESHOOTING.md)**: Real-world Ubuntu migration remedies.
- **[10_FINAL_VIVA_CHEAT_SHEET.md](docs/viva/10_FINAL_VIVA_CHEAT_SHEET.md)**: 10-minute rapid review sheet and formulas.

---

## License

This project is licensed under the [Apache 2.0 License](LICENSE).


---

## LUMI Vision & Fall Detection Stack (luminax_vision_ros)

LUMI integrates a state-of-the-art multi-modal edge perception engine for continuous patient safety:

1. **Human Pose Estimation:** 33-point 3D body landmark extraction powered by MediaPipe Tasks (CPU XNNPACK).
2. **Activity & Posture Classification:** Distinguishes standing, sitting, walking, lying_down, and sudden uncontrolled drops.
3. **Temporal Fall-Detection State Machine:** Multi-stage deterministic state machine (NORMAL -> POSSIBLE_FALL -> FALL_SUSPECTED -> FALL_CONFIRMED -> ALERT_SENT -> RECOVERED).
4. **Patient Presence & Disappearance:** Supervised tracking for designated individuals (PRESENT, TEMPORARILY_MISSING, MISSING, CAMERA_ERROR), strictly differentiating camera failure from patient movement.
5. **Biometric Face Recognition:** On-device YuNet face detection and SFace 128-d cosine recognition matching local data/identities.json.
6. **Caregiver Notification REST / WebSocket API:** Real-time event broadcasting and status telemetry on http://localhost:8000.

### Running on Raspberry Pi 5 / Ubuntu 24.04:
`ash
# Standalone Vision ROS 2 Node:
ros2 launch luminax_vision_ros lumi_vision.launch.py camera_topic:=/camera/image_raw

# Full Robot Bringup with Deep Learning Vision:
ros2 launch robot_bringup bringup_full_system.launch.py use_sim:=false use_vision:=true
`

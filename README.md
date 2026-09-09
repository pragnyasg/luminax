# Baymax-Inspired Autonomous Healthcare Companion Robot

A modular, educational, and clean ROS 2 software repository for an Autonomous Mobile Robot (AMR) designed as an indoor healthcare companion.

---

## Executive Summary

The **Baymax Healthcare Robot** is a university educational robotics project designed for **Ubuntu 22.04 LTS** running **ROS 2 Humble Hawksbill**. 

### Primary Technical Focus
The single most important technical objective of this project is **Reliable Autonomous Indoor Navigation**. 

### Critical Design Decision
> [!IMPORTANT]
> **THIS ROBOT DOES NOT HAVE ARMS.**
> It is an Autonomous Mobile Robot (AMR) built on a differential drive base. It prioritizes robust mobility, LiDAR sensing, obstacle avoidance, SLAM mapping, and interactive companion behaviors over complex robotic manipulation.

---

## Implementation Status

| Feature / Phase | Status | Package / Location | Notes |
| :--- | :--- | :--- | :--- |
| **Project Architecture & Docs** | `IMPLEMENTED NOW` | `documentation/` | Complete architectural guides & student study notes |
| **ROS 2 Colcon Workspace** | `IMPLEMENTED NOW` | `robot_ws/` | Standard ROS 2 Humble workspace layout |
| **URDF / Xacro Robot Model** | `IMPLEMENTED NOW` | `robot_ws/src/robot_description/urdf/` | Parametric 3D chassis, wheels, sensors, inertias |
| **RViz 3D Visualization** | `IMPLEMENTED NOW` | `robot_ws/src/robot_description/rviz/` | Pre-configured RViz display setup |
| **Robot Display Launch File** | `IMPLEMENTED NOW` | `robot_ws/src/robot_description/launch/` | ROS 2 launch file loading transforms & GUI |
| **Gazebo Simulation (Phase 4)** | `IMPLEMENTED NOW` | `simulation/` | Gazebo Classic 11 world & master launch setup |
| **Diff-Drive Plugins (Phase 4)** | `IMPLEMENTED NOW` | `robot_ws/src/robot_description/urdf/` | Gazebo plugins for `/cmd_vel`, `/scan`, `/camera/image_raw` |
| **Hardware Bridge Node (Phase 5)** | `IMPLEMENTED NOW` | `robot_ws/src/robot_hardware/` | `serial_bridge_node.py` translating `/cmd_vel` & `/odom` |
| **ESP32 Microcontroller Firmware** | `IMPLEMENTED NOW` | `esp32_firmware/` | C++ PWM motor control, optical encoders, JSON serial |
| **LiDAR Sensing (`/scan`) (Phase 6)** | `IMPLEMENTED NOW` | `robot_ws/src/robot_navigation/` | 2D LiDAR ray sensor & scan topic setup |
| **SLAM Mapping (Phase 7–8)** | `IMPLEMENTED NOW` | `robot_ws/src/robot_navigation/` | `slam_toolbox` mapping & map saver setup |
| **Nav2 Autonomous Navigation (Phase 9)** | `IMPLEMENTED NOW` | `robot_ws/src/robot_navigation/` | AMCL, DWB local planner, NavFn global planner |
| **Person Detection AI (Phases 10–11)** | `IMPLEMENTED NOW` | `robot_ws/src/robot_perception/` | OpenCV `person_detector_node` |
| **Voice Interaction (Phase 14)** | `IMPLEMENTED NOW` | `robot_ws/src/robot_voice/` | Offline TTS `voice_node` |
| **Healthcare Reminders (Phases 15–16)** | `IMPLEMENTED NOW` | `robot_ws/src/robot_health/` | `reminder_manager_node` medicine alerts |
| **Behavior Manager FSM (Phase 17)** | `IMPLEMENTED NOW` | `robot_ws/src/robot_behaviour/` | Finite State Machine companion manager |
| **Master System Bringup** | `IMPLEMENTED NOW` | `robot_ws/src/robot_bringup/` | `bringup_full_system.launch.py` master launch |

---

## Hardware Architecture

```
                  +-----------------------------------+
                  |  BAYMAX COMPANION ROBOT (AMR)     |
                  +-----------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
   +------------------+                            +------------------+
   |  Raspberry Pi 5  |                            |      ESP32       |
   | (Main Compute)   |                            | (Microcontroller)|
   +------------------+                            +------------------+
            |                                               |
     +------+------+                                 +------+------+
     |      |      |                                 |      |      |
     v      v      v                                 v      v      v
   ROS 2  LiDAR  Camera                            Motors Encoders Battery
```

- **Raspberry Pi 5**: High-level computation (ROS 2 Humble, SLAM, Nav2, Perception, Logic).
- **ESP32 Microcontroller**: Low-level execution (PWM motor control, encoder tick count, battery monitoring).
- **Differential Drive Chassis**: 2 driven wheels + 1 balancing rear caster wheel.
- **Sensors**: 2D LiDAR, RGB Camera, Optical Wheel Encoders.

---

## Directory Structure

```text
baymax_healthcare_robot/
├── README.md                          # Main project guide (this file)
├── .gitignore                         # ROS 2, Python, and OS ignore rules
├── LICENSE                            # Apache 2.0 open-source license
├── documentation/                     # Educational documentation for team & exams
│   ├── project_overview.md            # Vision, scope, and AMR concepts
│   ├── hardware_architecture.md       # RPi 5 + ESP32 pinouts and specs
│   ├── software_architecture.md       # Layered software architecture
│   ├── ros2_architecture.md           # ROS 2 node graph, topics, TF tree
│   ├── development_roadmap.md         # 20-Phase progressive roadmap
│   └── future_features.md             # Blueprints for AI & Voice modules
├── robot_ws/                          # ROS 2 Colcon Workspace
│   └── src/
│       ├── robot_description/         # URDF/Xacro model, RViz & Gazebo plugins
│       ├── robot_hardware/            # RPi 5 to ESP32 serial bridge & odometry
│       ├── robot_navigation/          # SLAM Toolbox & Nav2 parameters/launch
│       ├── robot_bringup/             # Master system bringup launch file
│       ├── robot_perception/          # OpenCV person detection node
│       ├── robot_behaviour/           # Finite State Machine behavior manager
│       ├── robot_health/              # Healthcare reminder manager node
│       └── robot_voice/               # Voice synthesis (TTS) & command node
├── esp32_firmware/                    # ESP32 motor & encoder C++ firmware
├── simulation/                        # Gazebo Classic 11 room world & launch
└── scripts/                           # Helper Linux setup scripts
```

---

## Build & Run Instructions (Ubuntu 22.04 + ROS 2 Humble)

### 1. Build the ROS 2 Workspace
```bash
# Navigate to the workspace
cd baymax_healthcare_robot/robot_ws

# Source ROS 2 Humble environment
source /opt/ros/humble/setup.bash

# Build all packages using colcon
colcon build --symlink-install

# Source the newly built overlay
source install/setup.bash
```

### 2. Launch Entire Baymax Companion Robot System!
```bash
ros2 launch robot_bringup bringup_full_system.launch.py
```

### 3. Individual Component Launches (Optional)
- **Gazebo Sim + SLAM Only**: `ros2 launch robot_navigation full_navigation.launch.py`
- **Nav2 Autonomous Navigation**: `ros2 launch robot_navigation navigation.launch.py`
- **Hardware Bridge Node**: `ros2 run robot_hardware serial_bridge_node`
- **Person Detector Node**: `ros2 run robot_perception person_detector_node`
- **Voice Node**: `ros2 run robot_voice voice_node`
- **Reminder Manager Node**: `ros2 run robot_health reminder_manager_node`
- **Behavior FSM Node**: `ros2 run robot_behaviour behaviour_manager_node`

---

## License

This project is released under the [Apache 2.0 License](LICENSE).

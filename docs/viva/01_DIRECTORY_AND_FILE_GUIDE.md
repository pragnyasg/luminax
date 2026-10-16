# 01 — LUMI Repository Directory & File Guide

```
========================================================================================
Project: LUMI — AI Autonomous Healthcare Companion Robot
Target Environment: Ubuntu 22.04 LTS | ROS 2 Humble Hawksbill
Purpose: Complete exhaustive breakdown of every authored file, script, and config.
========================================================================================
```

---

## 1. Complete Repository Directory Tree

```text
luminax/
├── .gitignore                                          # Version control filter for build, model, and OS artifacts
├── LICENSE                                             # Open-source Apache 2.0 license
├── README.md                                           # Master technical README & execution manual
├── documentation/                                      # High-level architecture & design records
│   ├── development_roadmap.md                         # Progressive milestone roadmap
│   ├── future_features.md                             # Specification for planned extensions
│   ├── hardware_architecture.md                       # Pinouts, power, and microcontroller wiring
│   ├── project_overview.md                            # Concept and educational AMR scope
│   ├── ros2_architecture.md                           # ROS 2 node graph, TF tree, and topics
│   └── software_architecture.md                       # Layered software architecture description
├── docs/                                               # Oral defense & examination documentation
│   └── viva/
│       ├── 00_PROJECT_OVERVIEW.md                     # Comprehensive academic overview & architecture
│       ├── 01_DIRECTORY_AND_FILE_GUIDE.md             # This document: file-by-file inventory
│       ├── 02_ROS2_NODE_TOPIC_SERVICE_ACTION_MAP.md   # Complete communication interface contract
│       ├── 03_SOURCE_CODE_LINE_BY_LINE.md             # Line-by-line source code walkthrough & viva Q&A
│       ├── 04_ROBOT_HARDWARE_TO_SOFTWARE_MAPPING.md   # Hardware components mapped to software drivers
│       ├── 05_SLAM_NAV2_GAZEBO_RVIZ_WORKFLOW.md       # Step-by-step simulation & navigation execution guide
│       ├── 06_BUILD_RUN_AND_DEBUG_GUIDE.md            # Exact Ubuntu commands for building & running
│       ├── 07_VIVA_QUESTION_BANK.md                   # 50+ detailed faculty questions and model answers
│       ├── 08_IMPLEMENTED_VS_PLANNED.md               # Honest engineering matrix of implemented features
│       ├── 09_UBUNTU_MIGRATION_AND_TROUBLESHOOTING.md # Migration pitfalls, diagnostics, and remedies
│       └── 10_FINAL_VIVA_CHEAT_SHEET.md               # Last-minute oral defense quick reference
├── esp32_firmware/                                     # Low-level embedded motor & encoder firmware
│   ├── platformio.ini                                  # PlatformIO build configuration for ESP32
│   ├── README.md                                       # Embedded subsystem guide & pin reference
│   └── src/
│       └── main.cpp                                    # ESP32 C++ firmware (LEDC PWM, ISR, JSON, Watchdog)
├── robot_ws/                                           # ROS 2 Colcon Workspace
│   └── src/
│       ├── robot_description/                          # Robot physical model, visual meshes, and TF
│       │   ├── package.xml                             # Ament package manifest
│       │   ├── setup.cfg & setup.py                    # Package build & installation rules
│       │   ├── README.md                               # Package summary
│       │   ├── launch/
│       │   │   └── display_robot.launch.py             # RViz2 standalone visualization launch
│       │   ├── rviz/
│       │   │   └── robot.rviz                          # Basic robot model & TF display setup
│       │   └── urdf/
│       │       └── healthcare_robot.urdf.xacro         # Parametric URDF model with Gazebo plugins
│       ├── robot_simulation/                           # Gazebo Classic 11 simulation package
│       │   ├── package.xml                             # Package manifest
│       │   ├── setup.cfg & setup.py                    # Build configuration with glob installers
│       │   ├── launch/
│       │   │   └── gazebo_sim.launch.py                # Launches gzserver, gzclient, spawns entity
│       │   └── worlds/
│       │       └── healthcare_room.world               # 3D testing environment with obstacles
│       ├── robot_hardware/                             # Hardware abstraction & serial bridge
│       │   ├── package.xml                             # Package manifest
│       │   ├── setup.cfg & setup.py                    # Build configuration (installs serial_bridge_node)
│       │   ├── README.md                               # Hardware bridge documentation
│       │   └── robot_hardware/
│       │       └── serial_bridge_node.py               # Serial protocol, odometry math, and /cmd_vel bridge
│       ├── robot_navigation/                           # SLAM and Nav2 configuration
│       │   ├── package.xml                             # Package manifest
│       │   ├── setup.cfg & setup.py                    # Build configuration (installs launch, config, maps)
│       │   ├── README.md                               # Navigation documentation
│       │   ├── config/
│       │   │   ├── nav2_params.yaml                    # Costmaps, DWB controller, NavFn parameters
│       │   │   └── slam_toolbox_params.yaml            # SLAM Toolbox online mapping parameters
│       │   ├── launch/
│       │   │   ├── full_navigation.launch.py           # Combined simulation + SLAM + Nav2 launch
│       │   │   ├── navigation.launch.py                # Nav2 stack bringup
│       │   │   └── slam.launch.py                      # SLAM Toolbox async node launch
│       │   ├── maps/
│       │   │   ├── sample_map.pgm                      # Grayscale 2D occupancy grid image
│       │   │   └── sample_map.yaml                     # Map metadata (resolution, origin, thresholds)
│       │   └── rviz/
│       │       └── navigation.rviz                     # Comprehensive Nav2/SLAM/LiDAR/Costmap RViz setup
│       ├── robot_perception/                           # Computer vision & human detection
│       │   ├── package.xml                             # Package manifest
│       │   ├── setup.cfg & setup.py                    # Build configuration
│       │   ├── README.md                               # Perception package overview
│       │   └── robot_perception/
│       │       ├── person_detector_node.py             # OpenCV HOG+SVM person detector & telemetry
│       │       └── webcam_publisher_node.py            # Physical USB webcam video publisher
│       ├── robot_voice/                                # Voice synthesis & speech output
│       │   ├── package.xml                             # Package manifest
│       │   ├── setup.cfg & setup.py                    # Build configuration
│       │   ├── README.md                               # Voice subsystem guide
│       │   └── robot_voice/
│       │       └── voice_node.py                       # Asynchronous non-blocking offline TTS node
│       ├── robot_health/                               # Healthcare workflows & medicine reminders
│       │   ├── package.xml                             # Package manifest
│       │   ├── setup.cfg & setup.py                    # Build configuration
│       │   ├── README.md                               # Healthcare subsystem guide
│       │   └── robot_health/
│       │       └── reminder_manager_node.py            # Medicine timers, escalation logic, Trigger services
│       ├── robot_behaviour/                            # High-level companion behavior supervisor
│       │   ├── package.xml                             # Package manifest
│       │   ├── setup.cfg & setup.py                    # Build configuration
│       │   ├── README.md                               # Behavior manager guide
│       │   └── robot_behaviour/
│       │       └── behaviour_manager_node.py           # 5-state FSM supervisor with emergency stops
│       └── robot_bringup/                              # Master system bringup
│           ├── package.xml                             # Package manifest
│           ├── setup.cfg & setup.py                    # Build configuration
│           ├── README.md                               # Bringup guide
│           └── launch/
│               └── bringup_full_system.launch.py       # Master launch file with sim/hardware parameters
├── scripts/                                            # Shell scripts for validation
│   ├── check_env.sh                                    # Validates Ubuntu version, ROS 2, packages, and python
│   └── README.md                                       # Script usage notes
├── simulation/                                         # Root simulation directory (synced with package)
│   ├── launch/
│   │   └── gazebo_sim.launch.py                        # Standalone Gazebo simulation launch
│   └── worlds/
│       └── healthcare_room.world                       # Gazebo SDF 1.6 indoor world
└── tests/                                              # Comprehensive automated unit test suite
    ├── test_behaviour_fsm.py                           # FSM state transition & emergency tests
    ├── test_healthcare_reminder.py                     # Reminder interval & escalation logic tests
    ├── test_kinematics_and_odometry.py                 # Forward/inverse kinematics & quaternion tests
    ├── test_ros_packages_and_xml.py                    # XML validity, URDF, YAML, and Python compilation
    └── test_serial_protocol.py                         # JSON packet formatting & battery ADC tests
```

---

## 2. Exhaustive File-by-File Technical Guide

### 2.1 Robot Description (`robot_ws/src/robot_description/`)
- **`urdf/healthcare_robot.urdf.xacro`**:
  - *Type:* Robot description format (XML/Xacro).
  - *Purpose:* Defines all links (`base_footprint`, `base_link`, `left_wheel_link`, `right_wheel_link`, `caster_wheel_link`, `lidar_link`, `camera_link`, `camera_optical_link`), physical dimensions, mass, rotational inertia tensors, visual meshes/colors, collision bounds, and Gazebo Classic plugins (`libgazebo_ros_diff_drive.so`, `libgazebo_ros_ray_sensor.so`, `libgazebo_ros_camera.so`).
  - *What Launches It:* `robot_state_publisher` inside `display_robot.launch.py`, `gazebo_sim.launch.py`, and `bringup_full_system.launch.py`.
  - *How to Test:* `python -m unittest tests/test_ros_packages_and_xml.py` or `xacro urdf/healthcare_robot.urdf.xacro`.
- **`launch/display_robot.launch.py`**:
  - *Type:* Python launch file.
  - *Purpose:* Pure visualization launch file. Starts `robot_state_publisher`, `joint_state_publisher_gui` (to manually move wheels with sliders), and opens RViz2.
  - *How to Test:* `ros2 launch robot_description display_robot.launch.py`.

### 2.2 Robot Simulation (`robot_ws/src/robot_simulation/`)
- **`launch/gazebo_sim.launch.py`**:
  - *Type:* Python launch file.
  - *Purpose:* Orchestrates Gazebo Classic 11 server (`gzserver`) with `healthcare_room.world`, spawns the robot at origin `(0, 0, 0.05)`, and runs RViz2.
  - *Parameters:* `world`, `gui` (default true), `use_sim_time` (default true), `use_rviz` (default true).
  - *How to Test:* `ros2 launch robot_simulation gazebo_sim.launch.py`.
- **`worlds/healthcare_room.world`**:
  - *Type:* Gazebo World SDF 1.6 XML.
  - *Purpose:* Enclosed simulation room with ODE physics configuration, sun illumination, ground plane, cylindrical pillars, wooden table obstacles, and perimeter walls to reflect LiDAR beams.

### 2.3 Robot Hardware & Microcontroller (`robot_ws/src/robot_hardware/` & `esp32_firmware/`)
- **`robot_hardware/serial_bridge_node.py`**:
  - *Type:* Executable Python ROS 2 Node.
  - *Purpose:* Bridges high-level ROS 2 velocity commands (`/cmd_vel`) to the ESP32 microcontroller over USB serial (`/dev/ttyUSB0` at 115200 baud). Translates encoder tick telemetry into metric wheel displacements, calculates Runge-Kutta forward kinematics odometry, broadcasts TF (`odom -> base_footprint`), and publishes `/odom` and `/battery_state`.
  - *Safety Feature:* Built-in 0.5s command watchdog halts wheels if navigation commands cease.
  - *How to Test:* `python -m unittest tests/test_serial_protocol.py` and `tests/test_kinematics_and_odometry.py`.
- **`esp32_firmware/src/main.cpp`**:
  - *Type:* Embedded C++ firmware for ESP32.
  - *Purpose:* Hard real-time motor controller. Generates 20 kHz ultrasonic PWM via ESP32 LEDC peripheral to eliminate audible coil whine. Listens to optical encoder Phase A/B interrupts using `IRAM_ATTR` ISRs. Reads 12V battery voltage via ADC with 4:1 voltage divider. Emits 20 Hz JSON telemetry. Includes a 500 ms safety timeout watchdog.

### 2.4 Robot Navigation (`robot_ws/src/robot_navigation/`)
- **`config/slam_toolbox_params.yaml`**:
  - *Type:* YAML parameter file.
  - *Purpose:* Configures SLAM Toolbox in online synchronous/asynchronous mapping mode. Sets frames (`map`, `odom`, `base_footprint`), scan topic (`/scan`), grid resolution (`0.05 m`), scan buffer, and loop closure matching thresholds.
- **`config/nav2_params.yaml`**:
  - *Type:* YAML parameter file.
  - *Purpose:* Comprehensive Nav2 parameter configuration for AMCL localization, NavFn global planner (A* grid search), DWB local controller (dynamic window obstacle avoidance), local costmap, global costmap, and recovery behavior servers.
- **`launch/slam.launch.py`**:
  - *Type:* Python launch file.
  - *Purpose:* Starts `slam_toolbox` node (`async_slam_toolbox_node`) with declared parameter `use_sim_time`.
- **`launch/navigation.launch.py`**:
  - *Type:* Python launch file.
  - *Purpose:* Includes `nav2_bringup/launch/bringup_launch.py` with `nav2_params.yaml` and designated map.
- **`launch/full_navigation.launch.py`**:
  - *Type:* Master navigation launch file.
  - *Purpose:* Starts Gazebo simulation, SLAM Toolbox, and Nav2 concurrently.
- **`rviz/navigation.rviz`**:
  - *Type:* RViz2 display configuration.
  - *Purpose:* Pre-configured with displays for RobotModel, TF, LaserScan (`/scan`), Odometry (`/odom`), Global Map (`/map`), Global Costmap, Local Costmap, Planned Path (`/plan`), and 2D Nav Goal tool.

### 2.5 Robot Perception (`robot_ws/src/robot_perception/`)
- **`robot_perception/person_detector_node.py`**:
  - *Type:* Executable Python ROS 2 Node.
  - *Purpose:* Subscribes to `/camera/image_raw`. Runs OpenCV Histogram of Oriented Gradients (HOG) + Linear SVM human detector. Computes bounding box center, normalized bearing (-1.0 to 1.0), and estimated distance in meters. Publishes `/perception/person_detected` (Bool), `/perception/person_count` (Int32), `/perception/detections` (JSON String), and `/perception/image_annotated` (Image).
- **`robot_perception/webcam_publisher_node.py`**:
  - *Type:* Executable Python ROS 2 Node.
  - *Purpose:* Direct hardware driver for USB webcams (`/dev/video0`). Captures 640x480 video at 30 FPS using OpenCV `VideoCapture` and publishes `sensor_msgs/msg/Image` on `/camera/image_raw` and `CameraInfo` on `/camera/camera_info`.

### 2.6 Healthcare & Companion Interaction (`robot_health/`, `robot_voice/`, `robot_behaviour/`)
- **`robot_health/reminder_manager_node.py`**:
  - *Type:* Executable Python ROS 2 Node.
  - *Purpose:* Implements periodic medicine reminder schedules. Dispatches voice reminders on `/voice/speak`. Monitors acknowledgment on `/voice/command`. If unacknowledged after `escalation_timeout` (30s), triggers emergency alert on `/health/emergency_alert`. Exposes Trigger services `/health/trigger_reminder` and `/health/acknowledge_reminder`.
- **`robot_voice/voice_node.py`**:
  - *Type:* Executable Python ROS 2 Node.
  - *Purpose:* Asynchronous voice synthesis node. Uses a thread-safe Queue and dedicated background worker thread running `pyttsx3` offline text-to-speech. Ensures the ROS 2 executor thread never blocks during speech playback.
- **`robot_behaviour/behaviour_manager_node.py`**:
  - *Type:* Executable Python ROS 2 Node.
  - *Purpose:* 5-state supervisor Finite State Machine (`IDLE`, `NAVIGATING`, `INTERACTING`, `REMINDER`, `EMERGENCY`). Manages contextual state transitions. In `EMERGENCY`, publishes explicit zero velocities on `/cmd_vel` to safely halt the robot.

### 2.7 System Bringup & Tests (`robot_bringup/` & `tests/`)
- **`robot_bringup/launch/bringup_full_system.launch.py`**:
  - *Type:* Master system orchestration launch file.
  - *Purpose:* Launches the entire integrated LUMI system with declared arguments `use_sim` (switches between Gazebo and ESP32 hardware bridge), `use_slam`, `use_nav2`, `use_perception`, `use_voice`, `use_health`, `use_behaviour`, and `use_rviz`.
- **`tests/test_*.py`**:
  - *Type:* Automated Python unit tests.
  - *Purpose:* Validates differential-drive kinematics, odometry integration, serial JSON protocol, behavior state transitions, reminder escalation logic, package manifests, and code compilation.

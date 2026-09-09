# Software Architecture

## 1. Modular Layered Architecture

The Baymax Healthcare Robot software stack is organized into five distinct abstraction layers to maintain modularity, testability, and clarity.

```text
===================================================================
                       APPLICATION LAYER
   Medicine Reminders | Voice Commands | Emergency Supervisor
===================================================================
                     BEHAVIOUR & DECISION LAYER
      Finite State Machine (IDLE / NAVIGATING / INTERACTING)
===================================================================
                 PERCEPTION & NAVIGATION LAYER
     SLAM Toolbox | Nav2 Stack | Person Detection | Costmaps
===================================================================
                     ROS 2 INTERFACE LAYER
       rclpy Nodes | /cmd_vel | /scan | /odom | /tf Tree
===================================================================
                     HARDWARE & DRIVER LAYER
        Serial Driver Node | ESP32 Firmware | Motor Driver
===================================================================
```

---

## 2. Package Organization & Responsibilities

| ROS 2 Package Name | Responsibility / Role | Key Files |
| :--- | :--- | :--- |
| **`robot_description`** | Defines 3D visual & collision geometry, joint limits, inertias, and RViz display setup. | `healthcare_robot.urdf.xacro`, `display_robot.launch.py`, `robot.rviz` |
| **`robot_bringup`** | Top-level launch configurations for simulation and real hardware operations. | Launch files starting hardware, sensors, & software stacks. |
| **`robot_navigation`** | Stores SLAM mapping configurations and Nav2 costmap/planner parameters. | `slam_toolbox_params.yaml`, `nav2_params.yaml` |
| **`robot_hardware`** | Hardware bridge for RPi-ESP32 serial connection, wheel odometry conversion, and `/cmd_vel` output. | `serial_bridge_node.py`, `wheel_odometry_node.py` |
| **`robot_perception`** | Camera stream receiver and lightweight person detection pipeline. | `person_detector_node.py` |
| **`robot_behaviour`** | High-level Finite State Machine managing high-level decisions. | `behaviour_manager_node.py` |
| **`robot_health`** | Scheduled medicine alerts and health interaction logic. | `reminder_manager_node.py` |
| **`robot_voice`** | Text-to-Speech (TTS) audio output and simple command parsing. | `voice_node.py` |

---

## 3. Data Flow Pipelines

### A. Navigation Velocity Pipeline
$$\text{Nav2 Planner} \longrightarrow \text{Topic: } \texttt{/cmd_vel} \longrightarrow \text{Hardware Node} \longrightarrow \text{Serial} \longrightarrow \text{ESP32} \longrightarrow \text{DC Motors}$$

### B. Odometry & Localization Pipeline
$$\text{Encoders} \longrightarrow \text{ESP32} \longrightarrow \text{Serial} \longrightarrow \text{Hardware Node} \longrightarrow \text{Topic: } \texttt{/odom} \longrightarrow \text{Nav2 / SLAM}$$

### C. LiDAR Perception Pipeline
$$\text{LiDAR Sensor} \longrightarrow \text{Driver Node} \longrightarrow \text{Topic: } \texttt{/scan} \longrightarrow \text{SLAM Toolbox / Nav2 Costmaps}$$

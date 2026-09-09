# Progressive 20-Phase Development Roadmap

To ensure high technical quality, modular clarity, and reliable results, the project progresses through 20 structured phases.

```text
  DESIGN & SIMULATION                HARDWARE & NAVIGATION               PERCEPTION & HIGHER LOGIC
+-----------------------+          +-----------------------+          +-----------------------+
| Phase 0: Docs & Arch  |          | Phase 4: Gazebo Sim   |          | Phase 10: Camera Stream|
| Phase 1: ROS 2 Setup  | -------> | Phase 5-6: ESP32/Odom | -------> | Phase 11-13: Vision AI|
| Phase 2: URDF / Xacro |          | Phase 7: LiDAR Setup  |          | Phase 14-17: Voice/FSM|
| Phase 3: RViz Launch  |          | Phase 8-9: SLAM/Nav2  |          | Phase 18-20: Deploy   |
+-----------------------+          +-----------------------+          +-----------------------+
```

---

## Roadmap Breakdown

### PHASE 0: Project Architecture & Documentation (`IMPLEMENTED NOW`)
- Define software architecture, package structures, hardware pinouts, and node graphs.

### PHASE 1: ROS 2 Project Structure (`IMPLEMENTED NOW`)
- Create ROS 2 colcon workspace `robot_ws/` with standard ROS 2 Humble package layouts.

### PHASE 2: URDF / Xacro Robot Description (`IMPLEMENTED NOW`)
- Model the differential drive robot (`base_footprint`, `base_link`, wheels, caster, sensors) in `healthcare_robot.urdf.xacro`.

### PHASE 3: RViz Visualization & Launch Setup (`IMPLEMENTED NOW`)
- Create ROS 2 Humble launch file (`display_robot.launch.py`) to launch `robot_state_publisher`, GUI sliders, and `rviz2`.

---

### PHASE 4: Gazebo Simulation Integration (`PLANNED LATER`)
- Add Gazebo classic differential drive motor plugin and LiDAR scanner plugin to the URDF model.

### PHASE 5: Low-Level ESP32 Firmware (`PLANNED LATER`)
- Develop ESP32 C++ firmware for motor PWM speed control, direction pins, and optical encoder counting.

### PHASE 6: Hardware Bridge & Wheel Odometry (`PLANNED LATER`)
- Create `serial_bridge_node.py` to read encoder telemetry over serial and publish `/odom` and `odom` -> `base_footprint` TF.

### PHASE 7: 2D LiDAR Range Sensor Setup (`PLANNED LATER`)
- Configure RPLiDAR / YDLIDAR ROS 2 driver to publish `/scan` `LaserScan` messages.

### PHASE 8: SLAM Mapping (`PLANNED LATER`)
- Configure `slam_toolbox` to generate and save 2D occupancy grid maps (`/map`).

### PHASE 9: Nav2 Autonomous Navigation (`PLANNED LATER`)
- Configure Nav2 costmaps, global planner, DWB local planner, and obstacle avoidance outputting to `/cmd_vel`.

---

### PHASE 10: Camera Stream Integration (`PLANNED LATER`)
- Connect USB camera to RPi 5 and publish `/camera/image_raw` using `v4l2_camera`.

### PHASE 11: Person Detection (`PLANNED LATER`)
- Implement lightweight pretrained MobileNet-SSD / YOLOv8-nano ROS 2 node (`person_detector_node.py`).

### PHASE 12: Face Recognition (Optional) (`PLANNED LATER`)
- Add low-priority face verification for registered test users.

### PHASE 13: Fall Detection (Optional) (`PLANNED LATER`)
- Add low-priority posture heuristics / MediaPipe pose estimation.

### PHASE 14: Voice Interface (`PLANNED LATER`)
- Implement offline Text-to-Speech (Pyttsx3) and keyword speech recognition.

### PHASE 15: Healthcare Reminder Manager (`PLANNED LATER`)
- Create timer-based node for scheduled medicine reminders and audio prompts.

### PHASE 16: Emergency Response Logic (`PLANNED LATER`)
- Create emergency check state logic ("Are you okay?" prompt with timer escalation).

### PHASE 17: Finite State Machine Behavior Manager (`PLANNED LATER`)
- Implement `behaviour_manager_node.py` coordinating high-level robot states (`IDLE`, `NAVIGATING`, `INTERACTING`, `REMINDER`, `EMERGENCY`).

---

### PHASE 18: Real Hardware System Assembly (`PLANNED LATER`)
- Wire RPi 5, ESP32, L298N driver, encoders, motors, and LiDAR on physical chassis.

### PHASE 19: Full System Integration & Benchmarking (`PLANNED LATER`)
- Conduct real-world navigation, mapping, and healthcare interaction tests inside target indoor environment.

### PHASE 20: Project Final Defense & Documentation Cleanup (`PLANNED LATER`)
- Finalize demonstration video, student presentation slides, and code comments for university evaluation.

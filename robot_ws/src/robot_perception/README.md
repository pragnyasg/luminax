# robot_perception ROS 2 Package (Implemented - Phase 10–11)

## 1. Package Purpose
The `robot_perception` package receives camera video frames (`/camera/image_raw`) and runs OpenCV human detection algorithms to determine if a patient or human companion is in front of the robot.

---

## 2. Package File Breakdown

```text
robot_perception/
├── package.xml                        # Manifest & OpenCV dependencies
├── setup.py                           # Python package setup file
├── setup.cfg                          # Script setup config
├── resource/
│   └── robot_perception               # Ament index marker
├── robot_perception/
│   ├── __init__.py
│   └── person_detector_node.py        # OpenCV person detection node
└── README.md                          # Package documentation (this file)
```

---

## 3. Node Details: `person_detector_node`

- **Subscribed Topic**: `/camera/image_raw` (`sensor_msgs/msg/Image`)
- **Published Topics**:
  - `/perception/person_detected` (`std_msgs/msg/Bool`): `True` when a person is detected in front of camera.
  - `/perception/image_annotated` (`sensor_msgs/msg/Image`): Camera stream with bounding boxes drawn around detected humans.

---

## 4. How to Build & Run in Ubuntu 22.04 + ROS 2 Humble

```bash
# 1. Build package
cd baymax_healthcare_robot/robot_ws
colcon build --packages-select robot_perception --symlink-install
source install/setup.bash

# 2. Run Person Detection Node
ros2 run robot_perception person_detector_node
```

# robot_health ROS 2 Package (Implemented - Phase 15–16)

## 1. Package Purpose
The `robot_health` package manages scheduled medicine reminders, patient acknowledgment logging, and emergency response checking for the Baymax Healthcare Robot.

---

## 2. Package File Breakdown

```text
robot_health/
├── package.xml                        # Manifest & dependencies
├── setup.py                           # Python package setup file
├── setup.cfg                          # Script setup config
├── resource/
│   └── robot_health                   # Ament index marker
├── robot_health/
│   ├── __init__.py
│   └── reminder_manager_node.py       # Healthcare reminder manager node
└── README.md                          # Package documentation (this file)
```

---

## 3. Node Details: `reminder_manager_node`

- **Published Topics**:
  - `/health/reminder_trigger` (`std_msgs/msg/String`): Fired when a medicine timer expires.
  - `/voice/speak` (`std_msgs/msg/String`): Triggers TTS audio prompt.
  - `/health/emergency_alert` (`std_msgs/msg/String`): Triggered if alerts remain unacknowledged.
- **Subscribed Topic**: `/voice/command` (`std_msgs/msg/String`): Patient voice feedback.

---

## 4. How to Build & Run in Ubuntu 22.04 + ROS 2 Humble

```bash
# 1. Build package
cd baymax_healthcare_robot/robot_ws
colcon build --packages-select robot_health --symlink-install
source install/setup.bash

# 2. Run Reminder Manager Node
ros2 run robot_health reminder_manager_node
```

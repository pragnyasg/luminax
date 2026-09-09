# robot_voice ROS 2 Package (Implemented - Phase 14)

## 1. Package Purpose
The `robot_voice` package handles text-to-speech (TTS) audio output and voice command processing for the Baymax Healthcare Robot.

---

## 2. Package File Breakdown

```text
robot_voice/
├── package.xml                        # Manifest & dependencies
├── setup.py                           # Python package setup file
├── setup.cfg                          # Script setup config
├── resource/
│   └── robot_voice                    # Ament index marker
├── robot_voice/
│   ├── __init__.py
│   └── voice_node.py                  # Offline TTS & voice node
└── README.md                          # Package documentation (this file)
```

---

## 3. Node Details: `voice_node`

- **Subscribed Topic**: `/voice/speak` (`std_msgs/msg/String`): Text string for Baymax to speak aloud.
- **Published Topic**: `/voice/command` (`std_msgs/msg/String`): Recognized spoken commands.

---

## 4. How to Build & Run in Ubuntu 22.04 + ROS 2 Humble

```bash
# 1. Build package
cd baymax_healthcare_robot/robot_ws
colcon build --packages-select robot_voice --symlink-install
source install/setup.bash

# 2. Run Voice Node
ros2 run robot_voice voice_node

# 3. Test Audio Output (In another terminal)
ros2 topic pub /voice/speak std_msgs/msg/String "data: 'Hello! I am Baymax, your personal healthcare companion.'" --once
```

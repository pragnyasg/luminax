# robot_behaviour ROS 2 Package (Implemented - Phase 17)

## 1. Package Purpose
The `robot_behaviour` package implements the **Finite State Machine (FSM)** behavior manager that coordinates perception inputs, healthcare reminders, voice commands, and navigation actions for the Baymax Healthcare Robot.

---

## 2. Package File Breakdown

```text
robot_behaviour/
├── package.xml                        # Manifest & dependencies
├── setup.py                           # Python package setup file
├── setup.cfg                          # Script setup config
├── resource/
│   └── robot_behaviour                # Ament index marker
├── robot_behaviour/
│   ├── __init__.py
│   └── behaviour_manager_node.py      # FSM companion behavior node
└── README.md                          # Package documentation (this file)
```

---

## 3. Finite State Machine (FSM) States

| State | Condition / Trigger | Robot Behavior |
| :--- | :--- | :--- |
| **`IDLE`** | Default rest state | Base station monitoring, battery sense. |
| **`NAVIGATING`** | Nav2 goal active | Moving along collision-free global path. |
| **`INTERACTING`** | `/perception/person_detected == True` | Greeting patient, offering companion assistance. |
| **`REMINDER`** | `/health/reminder_trigger` fired | Triggering medicine reminder audio prompts. |
| **`EMERGENCY`** | Unacknowledged reminder timeout | Escalating emergency safety check. |

---

## 4. How to Build & Run in Ubuntu 22.04 + ROS 2 Humble

```bash
# 1. Build package
cd baymax_healthcare_robot/robot_ws
colcon build --packages-select robot_behaviour --symlink-install
source install/setup.bash

# 2. Run Behavior Manager Node
ros2 run robot_behaviour behaviour_manager_node
```

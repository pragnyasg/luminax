# robot_bringup ROS 2 Package (Implemented - Master System Bringup)

## 1. Package Purpose
The `robot_bringup` package provides the master system launch file (`bringup_full_system.launch.py`) that brings up the entire software and simulation stack for the Baymax Healthcare Robot with a single ROS 2 launch command.

---

## 2. Package File Breakdown

```text
robot_bringup/
├── package.xml                        # Manifest & dependencies on all robot packages
├── setup.py                           # Python package setup file
├── setup.cfg                          # Script setup config
├── resource/
│   └── robot_bringup                  # Ament index marker
├── launch/
│   └── bringup_full_system.launch.py  # Master full system launch file
└── README.md                          # Package documentation (this file)
```

---

## 3. What Gets Started by `bringup_full_system.launch.py`

1. **Gazebo Classic 11 Simulation**: Starts room world and spawns robot chassis model.
2. **`robot_state_publisher`**: Processes Xacro parameters and publishes `/tf` coordinate transforms.
3. **`slam_toolbox`**: Performs live 2D online SLAM mapping.
4. **Nav2 Stack**: AMCL, DWB Local Planner, NavFn Global Planner, and Costmaps.
5. **`person_detector_node` (`robot_perception`)**: OpenCV camera person detection.
6. **`voice_node` (`robot_voice`)**: Offline TTS audio synthesis.
7. **`reminder_manager_node` (`robot_health`)**: Scheduled medicine alerts.
8. **`behaviour_manager_node` (`robot_behaviour`)**: Finite State Machine companion manager.
9. **RViz2**: Pre-configured 3D display visualization.

---

## 4. How to Launch Full System in Ubuntu 22.04 + ROS 2 Humble

```bash
# 1. Source ROS 2 Humble & Workspace
source /opt/ros/humble/setup.bash
cd baymax_healthcare_robot/robot_ws
colcon build --symlink-install
source install/setup.bash

# 2. Launch Entire Baymax Healthcare Robot System!
ros2 launch robot_bringup bringup_full_system.launch.py
```

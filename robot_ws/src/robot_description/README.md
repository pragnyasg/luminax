# robot_description ROS 2 Package

## 1. Package Purpose
The `robot_description` package holds the **URDF/Xacro 3D model**, kinematic definitions, sensor frame transformations, and RViz display configurations for the **Baymax Healthcare Robot**.

---

## 2. Package File Breakdown

```text
robot_description/
├── package.xml                        # Package metadata & ROS 2 dependencies
├── setup.py                           # Python package installation script
├── setup.cfg                          # Script directory configuration
├── resource/                          # Ament index resource marker
│   └── robot_description
├── robot_description/                 # Python module folder
│   └── __init__.py
├── urdf/
│   └── healthcare_robot.urdf.xacro    # Main parametric URDF description
├── launch/
│   └── display_robot.launch.py        # RViz & robot_state_publisher launch file
├── rviz/
│   └── robot.rviz                     # Saved RViz layout configuration
└── README.md                          # Package documentation (this file)
```

---

| Element | Type | Parent Link | Child Link | Description |
| :--- | :--- | :--- | :--- | :--- |
| `base_footprint` | Link | - | - | Ground level 2D reference frame ($Z=0$). |
| `base_footprint_joint` | Fixed | `base_footprint` | `base_link` | Raises chassis center by wheel radius ($0.0325\text{ m}$). |
| `base_link` | Link | - | - | Main chassis body with lower black plate, standoffs, and upper white deck. |
| `front_left_wheel_joint` | Continuous | `base_link` | `front_left_wheel_link` | Front-left driven wheel rotation along Y-axis ($R=32.5\text{ mm}$). |
| `front_right_wheel_joint` | Continuous | `base_link` | `front_right_wheel_link` | Front-right driven wheel rotation along Y-axis ($R=32.5\text{ mm}$). |
| `rear_left_wheel_joint` | Continuous | `base_link` | `rear_left_wheel_link` | Rear-left driven wheel rotation along Y-axis ($R=32.5\text{ mm}$). |
| `rear_right_wheel_joint` | Continuous | `base_link` | `rear_right_wheel_link` | Rear-right driven wheel rotation along Y-axis ($R=32.5\text{ mm}$). |
| `caster_wheel_joint` | Fixed | `base_link` | `caster_wheel_link` | Rear passive balancing support for simulation stability. |
| `lidar_joint` | Fixed | `base_link` | `lidar_link` | Slamtec RPLiDAR A1 laser scanner (scan plane at $Z=0.175\text{ m}$). |
| `camera_joint` | Fixed | `base_link` | `camera_link` | Companion head enclosure RGB camera sensor location ($Z=0.305\text{ m}$). |
| `camera_optical_joint` | Fixed | `camera_link` | `camera_optical_link` | Standard ROS REP-103 optical camera frame rotation. |

---

## 4. How to Build & Run in Ubuntu 22.04 + ROS 2 Humble

```bash
# 1. Source ROS 2 Humble
source /opt/ros/humble/setup.bash

# 2. Build from workspace root
cd baymax_healthcare_robot/robot_ws
colcon build --packages-select robot_description --symlink-install

# 3. Source workspace overlay
source install/setup.bash

# 4. Launch RViz Display
ros2 launch robot_description display_robot.launch.py
```

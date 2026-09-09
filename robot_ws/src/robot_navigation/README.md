# robot_navigation ROS 2 Package (Implemented - Phase 6–9)

## 1. Package Purpose
The `robot_navigation` package provides complete 2D SLAM mapping using **`slam_toolbox`**, map saving utilities, and autonomous goal navigation powered by **`Nav2`** for the Baymax Healthcare Robot.

---

## 2. Package File Breakdown

```text
robot_navigation/
├── package.xml                        # Package manifest & Nav2 / SLAM dependencies
├── setup.py                           # Python package setup file
├── setup.cfg                          # Script setup config
├── resource/
│   └── robot_navigation               # Ament index marker
├── config/
│   ├── slam_toolbox_params.yaml       # 2D SLAM mapping configuration
│   └── nav2_params.yaml               # Complete Nav2 parameter stack (AMCL, DWB, Costmaps)
├── launch/
│   ├── slam.launch.py                 # Launches slam_toolbox async mapping node
│   ├── navigation.launch.py           # Launches Nav2 stack with pre-saved map
│   └── full_navigation.launch.py      # Master one-command launch (Gazebo + SLAM + Nav2)
├── maps/
│   ├── sample_map.yaml                # Sample map metadata
│   └── sample_map.pgm                 # Sample map 2D grid image
└── README.md                          # Documentation (this file)
```

---

## 3. Key Concepts for Student Evaluation & Exams

### A. What is SLAM?
**SLAM** stands for *Simultaneous Localization and Mapping*. The robot uses 2D LiDAR laser scans (`/scan`) and wheel odometry (`/odom`) to build an occupancy grid map (`/map`) of an unknown indoor environment while simultaneously determining its own position within that map.

### B. What is Nav2?
**Nav2** is the official ROS 2 navigation framework. Given a goal pose in the map:
1. **Global Planner (`NavfnPlanner`)**: Computes a collision-free A* / Dijkstra path from the robot to the destination goal on the global map.
2. **Local Controller (`DWBLocalPlanner`)**: Computes smooth velocity commands (`/cmd_vel`) to steer the differential drive wheels while dynamically avoiding obstacles detected by LiDAR.
3. **Costmaps (`global_costmap` & `local_costmap`)**: 2D grid maps storing obstacle locations and safety inflation zones ($0.25\text{ m}$ radius around robot chassis).

---

## 4. How to Build & Run in Ubuntu 22.04 + ROS 2 Humble

### A. Run SLAM Mapping in Simulation
```bash
# 1. Source ROS 2 Humble
source /opt/ros/humble/setup.bash

# 2. Build workspace
cd baymax_healthcare_robot/robot_ws
colcon build --symlink-install
source install/setup.bash

# 3. Launch Master Gazebo Sim + SLAM
ros2 launch robot_navigation full_navigation.launch.py

# 4. Drive robot with teleop keyboard to explore room & build map
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### B. Save the Generated Map
```bash
ros2 run nav2_map_server map_saver_cli -f my_hospital_map
```

### C. Run Nav2 Autonomous Goal Navigation
```bash
ros2 launch robot_navigation navigation.launch.py map:=my_hospital_map.yaml
```
*In RViz2, click **2D Goal Pose** and click anywhere on the map to see the robot navigate autonomously!*

# Gazebo Simulation Environment (Implemented - Phase 4)

## 1. Simulation Overview
The `simulation/` directory contains Gazebo Classic 11 world models (`.world`) and master simulation launch files for the **Baymax Healthcare Robot**.

---

## 2. Directory Structure

```text
simulation/
├── worlds/
│   └── healthcare_room.world         # Indoor room SDF world with walls & obstacles
├── launch/
│   └── gazebo_sim.launch.py          # Master Gazebo launch file
└── README.md                         # Documentation (this file)
```

---

## 3. Simulation Features

1. **Differential Drive Motor Plugin (`libgazebo_ros_diff_drive.so`)**:
   - Subscribes to `/cmd_vel` (`geometry_msgs/msg/Twist`)
   - Drives wheels in Gazebo physics engine
   - Publishes `/odom` (`nav_msgs/msg/Odometry`) and `odom` -> `base_footprint` TF transform
2. **2D LiDAR Plugin (`libgazebo_ros_ray_sensor.so`)**:
   - Simulates 360-degree laser range scanner
   - Publishes `/scan` (`sensor_msgs/msg/LaserScan`) on frame `lidar_link`
3. **RGB Camera Plugin (`libgazebo_ros_camera.so`)**:
   - Simulates RGB video stream
   - Publishes `/camera/image_raw` (`sensor_msgs/msg/Image`) on frame `camera_optical_link`

---

## 4. How to Launch Simulation in Ubuntu 22.04 + ROS 2 Humble

```bash
# 1. Source ROS 2 Humble
source /opt/ros/humble/setup.bash

# 2. Build workspace
cd baymax_healthcare_robot/robot_ws
colcon build --symlink-install
source install/setup.bash

# 3. Launch Gazebo Simulation & RViz
ros2 launch simulation/launch/gazebo_sim.launch.py

# 4. Drive Robot with Teleop Keyboard (In another terminal)
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

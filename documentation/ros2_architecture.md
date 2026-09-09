# ROS 2 Computational & Spatial Architecture

## 1. Node & Topic Graph

The diagram below shows how ROS 2 nodes communicate over topics within the Baymax Healthcare Robot architecture:

```text
  +-----------------------+
  |    rplidar_node       |
  +-----------------------+
              |
              | Topic: /scan (sensor_msgs/msg/LaserScan)
              v
  +-----------------------+              +-----------------------+
  |     slam_toolbox      |------------->|      nav2_nodes       |
  +-----------------------+ Topic: /map  +-----------------------+
              |                                      |
              v                                      v
   TF: map -> odom                       Topic: /cmd_vel (geometry_msgs/msg/Twist)
                                                     |
                                                     v
                                         +-----------------------+
                                         |  serial_bridge_node   |
                                         +-----------------------+
                                                     |
                                                     | Serial USB (JSON)
                                                     v
                                         +-----------------------+
                                         |    ESP32 Firmware     |
                                         +-----------------------+
```

---

## 2. Standard ROS 2 Topic Specifications

| Topic Name | Message Type | Publisher Node | Subscriber Node | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `nav2` / `teleop` | `serial_bridge_node` | High-level linear and angular velocity commands. |
| `/odom` | `nav_msgs/msg/Odometry` | `serial_bridge_node` | `nav2` / `slam_toolbox` | Estimated robot pose and velocity computed from wheel encoders. |
| `/scan` | `sensor_msgs/msg/LaserScan` | `rplidar_node` | `nav2` / `slam_toolbox` | 2D 360-degree laser range scan array. |
| `/camera/image_raw` | `sensor_msgs/msg/Image` | `v4l2_camera` | `person_detector_node` | Uncompressed camera video frames. |
| `/tf` | `tf2_msgs/msg/TFMessage` | `robot_state_publisher` / `odom` | `rviz2` / `nav2` | Dynamic spatial coordinate frame transformations. |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | `robot_state_publisher` | `rviz2` / `nav2` | Fixed spatial transformations (e.g., base_link to lidar_link). |

---

## 3. TF (Transform) Coordinate Frame Tree

In ROS 2, spatial transforms connect sensor data to the robot chassis and global environment map according to standard **REP-105**:

```text
                            map (Global World Origin)
                             |
                             | (Published by SLAM / AMCL Localization)
                             v
                            odom (Odometry Origin)
                             |
                             | (Published by serial_bridge_node / Wheel Encoders)
                             v
                       base_footprint (Ground Level Projection)
                             |
                             | (Fixed Joint: Z offset = Wheel Radius)
                             v
                         base_link (Chassis Mechanical Origin)
                             |
         +-------------------+-------------------+-------------------+
         |                   |                   |                   |
         v                   v                   v                   v
   left_wheel_link    right_wheel_link   caster_wheel_link      lidar_link
  (Continuous Joint)  (Continuous Joint)    (Fixed Joint)      (Fixed Joint)
                                                                     |
                                                                     v
                                                                camera_link
                                                               (Fixed Joint)
                                                                     |
                                                                     v
                                                          camera_optical_link
                                                            (Fixed Joint)
```

### Explanation of Coordinate Frames for Student Exams:
- **`map`**: The world fixed frame. Its origin does not move.
- **`odom`**: A smooth, continuous local frame estimated from encoders. Drift occurs over long distances.
- **`base_footprint`**: The 2D projection of the robot chassis on the floor ($Z=0$).
- **`base_link`**: The center of the robot chassis 3D body.
- **`lidar_link`**: Position of the LiDAR scanner optical center relative to `base_link`.

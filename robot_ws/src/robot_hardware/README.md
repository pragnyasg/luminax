# robot_hardware ROS 2 Package (Implemented - Phase 5)

## 1. Package Purpose
The `robot_hardware` package manages the velocity command translation, USB serial communication with the **ESP32 microcontroller**, wheel encoder feedback processing, and **Odometry (`/odom`)** publishing for the Baymax Healthcare Robot.

---

## 2. Package File Breakdown

```text
robot_hardware/
├── package.xml                        # Package manifest & ROS 2 dependencies
├── setup.py                           # Python package installation script
├── setup.cfg                          # Script directory config
├── resource/
│   └── robot_hardware                 # Ament index resource marker
├── robot_hardware/
│   ├── __init__.py
│   └── serial_bridge_node.py          # Main ROS 2 serial bridge & odometry node
└── README.md                          # Package documentation (this file)
```

---

## 3. Node Details: `serial_bridge_node`

- **Subscribed Topic**: `/cmd_vel` (`geometry_msgs/msg/Twist`)
- **Published Topic**: `/odom` (`nav_msgs/msg/Odometry`)
- **Published TF**: `odom` -> `base_footprint`
- **Serial Communication**: JSON packet stream over USB Serial (`/dev/ttyUSB0` at 115200 baud).

### Kinematic Translation Formulas
$$\text{Left Wheel Velocity } (v_L) = v_{\text{linear}} - \frac{\omega_{\text{angular}} \cdot W}{2}$$
$$\text{Right Wheel Velocity } (v_R) = v_{\text{linear}} + \frac{\omega_{\text{angular}} \cdot W}{2}$$

---

## 4. How to Build & Run in Ubuntu 22.04 + ROS 2 Humble

```bash
# 1. Source ROS 2 Humble
source /opt/ros/humble/setup.bash

# 2. Build package
cd baymax_healthcare_robot/robot_ws
colcon build --packages-select robot_hardware --symlink-install

# 3. Source workspace overlay
source install/setup.bash

# 4. Launch Hardware Serial Bridge Node
ros2 run robot_hardware serial_bridge_node
```

*Note: If no ESP32 hardware is connected, the node automatically defaults to software loopback mode so students can test navigation logic without requiring physical motors.*

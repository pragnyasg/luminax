# 06 — LUMI Build, Run & Diagnostic Debugging Guide

```
========================================================================================
Project: LUMI — AI Autonomous Healthcare Companion Robot
Target Environment: Ubuntu 22.04 LTS | ROS 2 Humble Hawksbill
Execution Model: Colcon Build System with Symlink Install & Isolated Shell Tabs
========================================================================================
```

---

## 1. Prerequisites & System Dependencies

### 1.1 Ubuntu Version & ROS 2 Distribution
- **Target OS:** Ubuntu 22.04 LTS (Jammy Jellyfish).
- **Target ROS:** ROS 2 Humble Hawksbill (Desktop Install).

### 1.2 One-Command System Dependency Installation
Open terminal and execute:
```bash
sudo apt update && sudo apt install -y \
    ros-humble-desktop \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-plugins \
    ros-humble-robot-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-xacro \
    ros-humble-rviz2 \
    ros-humble-slam-toolbox \
    ros-humble-nav2-bringup \
    ros-humble-nav2-map-server \
    ros-humble-cv-bridge \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    espeak

# Install required Python modules
pip3 install pyserial pyttsx3 opencv-python numpy
```

---

## 2. Workspace Setup & Build Procedure

### 2.1 Workspace Directory Structure
Clone or locate the repository:
```bash
cd ~
git clone https://github.com/pragnyasg/luminax.git
cd ~/luminax/robot_ws
```

### 2.2 Initialize and Run rosdep
```bash
sudo rosdep init 2>/dev/null || true
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### 2.3 Colcon Build with Symlink Install
```bash
cd ~/luminax/robot_ws

# Clean build all 9 packages
colcon build --symlink-install
```
*Why `--symlink-install` matters:* In Python packages (`ament_python`), `--symlink-install` creates symbolic links from `install/` directly back to the source files in `src/`. When you adjust code or YAML parameters, the change is immediately active without needing to re-run `colcon build`!

### 2.4 Environment Sourcing
Always source the base ROS 2 distribution first, then your custom workspace overlay:
```bash
source /opt/ros/humble/setup.bash
source ~/luminax/robot_ws/install/setup.bash
```
*(Tip: Add both commands to the end of `~/.bashrc` to source automatically upon opening every new terminal).*

---

## 3. Standard Execution Commands

### Mode A: Full Simulation Bringup (One-Command Master Launch)
Launches Gazebo Classic 11 room world, spawns the LUMI differential base, starts SLAM mapping, launches Nav2 goal navigation, activates OpenCV person perception, runs the async voice node, and launches RViz2 with live map and laser scan overlays:
```bash
ros2 launch robot_bringup bringup_full_system.launch.py use_sim:=true
```

### Mode B: Physical Robot Bringup (Raspberry Pi 5 + ESP32 Hardware)
Runs directly on the onboard Raspberry Pi 5 connected to ESP32 via USB (`/dev/ttyUSB0`):
```bash
ros2 launch robot_bringup bringup_full_system.launch.py \
    use_sim:=false \
    use_sim_time:=false
```
*What happens:* Gazebo is bypassed. `serial_bridge_node` connects to `/dev/ttyUSB0` at 115200 baud, translates `/cmd_vel` to ESP32 motor commands, calculates odometry from encoder ticks, and broadcasts the `odom -> base_footprint` TF transform.

### Mode C: Standalone Computer Vision & Webcam Mode
To test human detection with a physical USB webcam without launching robotics simulation:
```bash
# Terminal 1: Launch USB Webcam Publisher
ros2 run robot_perception webcam_publisher_node --ros-args -p device_id:=0

# Terminal 2: Launch OpenCV Person Detector
ros2 run robot_perception person_detector_node

# Terminal 3: View Annotated Feed in RViz or rqt_image_view
ros2 run rqt_image_view rqt_image_view /perception/image_annotated
```

### Mode D: Pure URDF Robot Model Inspection in RViz2
To inspect the 3D Xacro links, joints, and slider controls:
```bash
ros2 launch robot_description display_robot.launch.py
```

---

## 4. Diagnostics & Troubleshooting Toolset

### 4.1 Checking the ROS 2 Computation Graph
```bash
# Graphical display of active nodes and topic connections
rqt_graph
```

### 4.2 Inspecting Active Topics & Data Streams
```bash
# List all active topics with their exact message types
ros2 topic list -t

# Check publisher rate of laser scan
ros2 topic hz /scan

# Print live telemetry from odometry
ros2 topic echo /odom

# Echo human detection flags
ros2 topic echo /perception/person_detected
```

### 4.3 Inspecting Coordinate Transforms (TF2)
```bash
# Generate visual PDF map of TF hierarchy
ros2 run tf2_tools view_frames

# Print real-time transform between odom and base_footprint
ros2 run tf2_ros tf2_echo odom base_footprint

# Check transform between map and base_link
ros2 run tf2_ros tf2_echo map base_link
```

### 4.4 Service Calls for Companion Testing
```bash
# Manually trigger a medicine reminder on demand
ros2 service call /health/trigger_reminder std_srvs/srv/Trigger

# Acknowledge an active reminder programmatically
ros2 service call /health/acknowledge_reminder std_srvs/srv/Trigger

# Reset FSM state back to IDLE
ros2 service call /behaviour/reset_state std_srvs/srv/Trigger

# Save current SLAM map
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap "{name: {data: 'my_map'}}"
```

---

## 5. Running the Automated Test Suite
To verify kinematics, odometry math, serial JSON protocols, behavior FSM, and XML package manifests:
```bash
cd ~/luminax
python3 -m unittest discover -s tests -p "test_*.py" -v
```
*Expected Result:* 21 tests ran, 0 failures, status `OK`.

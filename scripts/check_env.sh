#!/bin/bash
# Environment & Dependency Verification Script for Baymax Healthcare Robot
# Target Environment: Ubuntu 22.04 LTS + ROS 2 Humble Hawksbill

echo "=========================================================="
echo "  Checking Baymax Healthcare Robot Environment Setup     "
echo "=========================================================="

# 1. Check ROS 2 Humble Installation
if [ -z "$ROS_DISTRO" ]; then
    echo "[!] ROS 2 environment is not sourced."
    echo "    Please run: source /opt/ros/humble/setup.bash"
else
    echo "[OK] ROS 2 Distro detected: $ROS_DISTRO"
fi

# 2. Check Colcon Build Tool
if command -v colcon &> /dev/null; then
    echo "[OK] colcon build tool is installed."
else
    echo "[!] colcon is NOT installed. Install with: sudo apt install python3-colcon-common-extensions"
fi

# 3. Check Required ROS 2 Packages
echo "Checking required ROS 2 packages..."
PACKAGES=("robot_state_publisher" "joint_state_publisher_gui" "xacro" "rviz2" "gazebo_ros" "slam_toolbox" "nav2_bringup")

for pkg in "${PACKAGES[@]}"; do
    if ros2 pkg prefix "$pkg" &> /dev/null; then
        echo "  [OK] Package found: $pkg"
    else
        echo "  [!] Package MISSING: $pkg (Install via sudo apt install ros-humble-$pkg)"
    fi
done

echo "=========================================================="
echo "Environment check complete."
echo "=========================================================="

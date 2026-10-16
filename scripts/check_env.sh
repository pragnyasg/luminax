#!/bin/bash
# Environment & Dependency Verification Script for LUMI Healthcare Robot
# Target Environment: Ubuntu 22.04 LTS + ROS 2 Humble Hawksbill

echo "=========================================================="
echo "    LUMI AI Healthcare Companion Robot Environment Check  "
echo "=========================================================="

# 1. Check Ubuntu Version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "[INFO] Operating System: $NAME $VERSION"
fi

# 2. Check ROS 2 Humble Installation
if [ -z "$ROS_DISTRO" ]; then
    echo "[!] ROS 2 environment is not sourced."
    echo "    Please run: source /opt/ros/humble/setup.bash"
else
    echo "[OK] ROS 2 Distro detected: $ROS_DISTRO"
    if [ "$ROS_DISTRO" != "humble" ]; then
        echo "    [WARN] Project is tailored and certified for ROS 2 Humble."
    fi
fi

# 3. Check Colcon Build Tool
if command -v colcon &> /dev/null; then
    echo "[OK] colcon build tool is installed."
else
    echo "[!] colcon is NOT installed. Install via: sudo apt install python3-colcon-common-extensions"
fi

# 4. Check Required ROS 2 Core Packages
echo ""
echo "Checking required ROS 2 system packages..."
PACKAGES=(
    "robot_state_publisher"
    "joint_state_publisher_gui"
    "xacro"
    "rviz2"
    "gazebo_ros"
    "slam_toolbox"
    "nav2_bringup"
    "cv_bridge"
)

for pkg in "${PACKAGES[@]}"; do
    if ros2 pkg prefix "$pkg" &> /dev/null; then
        echo "  [OK] Package found: $pkg"
    else
        echo "  [!] Package MISSING: $pkg (Install via: sudo apt install ros-humble-${pkg//_/-})"
    fi
done

# 5. Check Python System Libraries
echo ""
echo "Checking required Python libraries..."
PYTHON_MODS=("serial" "pyttsx3" "cv2" "numpy")

for mod in "${PYTHON_MODS[@]}"; do
    if python3 -c "import $mod" &> /dev/null; then
        echo "  [OK] Python module found: $mod"
    else
        echo "  [!] Python module MISSING: $mod (Install via: pip install or apt)"
    fi
done

echo ""
echo "=========================================================="
echo "Environment check completed."
echo "=========================================================="

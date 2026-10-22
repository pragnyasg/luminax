#!/usr/bin/env bash
# =====================================================================
#  LUMINAX dependency installer  (Ubuntu 24.04 + ROS 2 Jazzy)
#  Run on the Raspberry Pi 5. Assumes ROS 2 Jazzy is already installed
#  (ros-jazzy-ros-base). Re-runnable (idempotent-ish).
# =====================================================================
set -euo pipefail

echo "==> Checking ROS 2 ..."
if ! command -v ros2 >/dev/null 2>&1; then
  echo "ROS 2 not found on PATH. Install ros-jazzy-ros-base and 'source /opt/ros/jazzy/setup.bash' first."
  exit 1
fi

echo "==> apt dependencies (binaries available for Jazzy) ..."
sudo apt update
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-rviz2 \
  ros-jazzy-slam-toolbox \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-nav2-map-server \
  ros-jazzy-teleop-twist-keyboard \
  ros-jazzy-tf2-tools \
  ros-jazzy-tf-transformations

echo "==> GPIO libraries for the Raspberry Pi 5 (RP1) ..."
# gpiozero + lgpio backend. On a non-Pi dev laptop these may be absent;
# the motor node will fall back to DRY-RUN if they are missing.
sudo apt install -y python3-gpiozero python3-lgpio || \
  echo "WARN: gpiozero/lgpio not installed (fine on a non-Pi machine)."

echo "==> rosdep ..."
sudo rosdep init 2>/dev/null || true
rosdep update || true

WS="$(cd "$(dirname "$0")" && pwd)"
SRC="$WS/src"

echo "==> Third-party SOURCE packages (not available as Jazzy apt binaries) ..."
cd "$SRC"

if [ ! -d sllidar_ros2 ]; then
  echo "   cloning sllidar_ros2 (RPLiDAR driver) ..."
  git clone https://github.com/Slamtec/sllidar_ros2.git
else
  echo "   sllidar_ros2 already present."
fi

if [ ! -d rf2o_laser_odometry ]; then
  echo "   cloning rf2o_laser_odometry (ros2 branch) ..."
  git clone -b ros2 https://github.com/MAPIRlab/rf2o_laser_odometry.git
else
  echo "   rf2o_laser_odometry already present."
fi

echo "==> rosdep install for the whole workspace ..."
cd "$WS"
rosdep install --from-paths src --ignore-src -r -y || \
  echo "WARN: some rosdep keys may be unresolved; see output above."

echo ""
echo "Done. Next:"
echo "  cd $WS && colcon build --symlink-install"
echo "  source install/setup.bash"

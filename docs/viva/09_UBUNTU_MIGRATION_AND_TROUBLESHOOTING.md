# 09 — Ubuntu Migration & Real-World Troubleshooting Guide

```
========================================================================================
Project: LUMI — AI Autonomous Healthcare Companion Robot
Target Environment: Ubuntu 22.04 LTS | ROS 2 Humble Hawksbill
Scope: Exhaustive troubleshooting manual for transitioning code from Windows to Ubuntu.
========================================================================================
```

---

## 1. Top 10 Ubuntu Migration Gotchas & Solutions

### Issue 1: "Command 'ros2' not found" or "Package '...' not found"
- **Symptom:**
  ```text
  bash: ros2: command not found
  # or
  Package 'robot_bringup' not found: "package 'robot_bringup' not found, searching: [...]"
  ```
- **Likely Cause:** The terminal shell has not sourced the ROS 2 underlay (`/opt/ros/humble/setup.bash`) or the workspace overlay (`install/setup.bash`).
- **Diagnostic Command:**
  ```bash
  echo "Distro: $ROS_DISTRO, Ament Prefix: $AMENT_PREFIX_PATH"
  ```
- **Safe Fix:**
  Source both environments:
  ```bash
  source /opt/ros/humble/setup.bash
  source ~/luminax/robot_ws/install/setup.bash
  ```
  Persist this by appending to `~/.bashrc`:
  ```bash
  echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
  echo "source ~/luminax/robot_ws/install/setup.bash" >> ~/.bashrc
  ```
- **Verification:** `ros2 pkg prefix robot_bringup` returns your workspace install path.

---

### Issue 2: Serial Port Permission Denied (`/dev/ttyUSB0`)
- **Symptom:**
  ```text
  [serial_bridge_node]: Could not open serial port /dev/ttyUSB0: [Errno 13] Permission denied: '/dev/ttyUSB0'
  ```
- **Likely Cause:** Under Linux, serial communication devices (`/dev/ttyUSB*` and `/dev/ttyACM*`) belong to the `dialout` group. By default, regular users lack read/write permissions.
- **Diagnostic Command:**
  ```bash
  ls -l /dev/ttyUSB0
  # Output: crw-rw---- 1 root dialout ...
  groups
  ```
- **Safe Fix:**
  Add your Linux user to the `dialout` group and grant temporary permissions:
  ```bash
  sudo usermod -a -G dialout $USER
  sudo chmod 666 /dev/ttyUSB0
  ```
  *(Log out and log back into Ubuntu for group changes to take permanent effect).*
- **Verification:** `python3 -c "import serial; s = serial.Serial('/dev/ttyUSB0', 115200); print('Serial Open OK!')"`

---

### Issue 3: Missing Gazebo Classic ROS Plugins (`libgazebo_ros_diff_drive.so`)
- **Symptom:**
  ```text
  [gzserver-1] [ERROR] [gazebo_ros_diff_drive]: Failed to load plugin libgazebo_ros_diff_drive.so: 
  libgazebo_ros_diff_drive.so: cannot open shared object file: No such file or directory
  ```
- **Likely Cause:** The ROS 2 to Gazebo Classic bridge plugins package is not installed.
- **Diagnostic Command:**
  ```bash
  dpkg -l | grep ros-humble-gazebo-plugins
  ```
- **Safe Fix:**
  Install Gazebo Classic ROS integration packages:
  ```bash
  sudo apt update && sudo apt install -y \
      ros-humble-gazebo-ros-pkgs \
      ros-humble-gazebo-plugins
  ```
- **Verification:** `locate libgazebo_ros_diff_drive.so` finds the library in `/opt/ros/humble/lib/`.

---

### Issue 4: Transform Extrapolation Errors in TF2
- **Symptom:**
  ```text
  [controller_server]: Lookup would require extrapolation into the past/future. 
  Requested time 12.456000 but earliest time in buffer is 14.120000.
  ```
- **Likely Cause:** Time synchronization mismatch. Gazebo publishes simulated time on `/clock`, while navigation nodes were started with `use_sim_time:=false` (reading system wall clock).
- **Diagnostic Command:**
  ```bash
  ros2 param get /controller_server use_sim_time
  ```
- **Safe Fix:**
  Always pass `use_sim_time:=true` to all navigation and simulation launch files:
  ```bash
  ros2 launch robot_bringup bringup_full_system.launch.py use_sim:=true use_sim_time:=true
  ```
- **Verification:** The error vanishes and the local costmap updates cleanly in RViz.

---

### Issue 5: Audio TTS Error (`libespeak.so.1` or `No module named pyttsx3`)
- **Symptom:**
  ```text
  [voice_node]: Could not initialize pyttsx3 engine: libespeak.so.1: cannot open shared object file
  ```
- **Likely Cause:** `pyttsx3` on Linux utilizes the open-source `espeak` multi-lingual software speech synthesizer backend, which is not installed by default on minimal Ubuntu installations.
- **Diagnostic Command:**
  ```bash
  which espeak
  ```
- **Safe Fix:**
  Install `espeak` and its shared C library:
  ```bash
  sudo apt update && sudo apt install -y espeak libespeak1
  pip3 install pyttsx3
  ```
- **Verification:** Test offline voice directly from the terminal:
  ```bash
  python3 -c "import pyttsx3; e = pyttsx3.init(); e.say('LUMI voice system operational'); e.runAndWait()"
  ```

---

### Issue 6: USB Camera Access Permissions (`/dev/video0`)
- **Symptom:**
  ```text
  [webcam_publisher_node]: Could not open video device index 0. Will retry...
  ```
- **Likely Cause:** Either the webcam is plugged into another USB port index (e.g., `/dev/video2`), or user lacks permissions in the `video` group.
- **Diagnostic Command:**
  ```bash
  v4l2-ctl --list-devices 2>/dev/null || ls -l /dev/video*
  ```
- **Safe Fix:**
  Add user to `video` group:
  ```bash
  sudo usermod -a -G video $USER
  ```
  If camera index is 2 or 4, pass the parameter when launching:
  ```bash
  ros2 run robot_perception webcam_publisher_node --ros-args -p device_id:=2
  ```
- **Verification:** Video feed appears on `/camera/image_raw`.

---

### Issue 7: Network Cross-Talk (Ghost Nodes from Other Student Teams)
- **Symptom:** You run `ros2 topic list` in the university lab and see hundreds of unknown topics or your robot moves unexpectedly without you sending commands!
- **Likely Cause:** By default, ROS 2 uses `ROS_DOMAIN_ID=0`. All computers on the same university Wi-Fi subnet broadcast discovery packets to Domain 0, merging everyone's robots into a single shared DDS graph!
- **Diagnostic Command:**
  ```bash
  echo $ROS_DOMAIN_ID
  ```
- **Safe Fix:**
  Assign your team a unique domain ID between 1 and 101 (e.g., Domain ID 42):
  ```bash
  export ROS_DOMAIN_ID=42
  echo "export ROS_DOMAIN_ID=42" >> ~/.bashrc
  ```
- **Verification:** `ros2 node list` now displays ONLY LUMI's nodes.

---

### Issue 8: Gazebo Black Screen or Crash under Wayland / Virtual Machines
- **Symptom:**
  ```text
  [gzclient-2] Could not connect to display :0
  # or Gazebo opens as a completely black window with 0 FPS
  ```
- **Likely Cause:** Ubuntu 22.04 defaults to Wayland display server, which sometimes causes OpenGL hardware acceleration issues with older Gazebo Classic releases, especially inside VirtualBox or VMware.
- **Diagnostic Command:**
  ```bash
  echo $XDG_SESSION_TYPE
  ```
- **Safe Fix:**
  Force software OpenGL rendering or X11 compatibility:
  ```bash
  export LIBGL_ALWAYS_SOFTWARE=1
  export GDK_BACKEND=x11
  # Launch Gazebo
  ros2 launch robot_simulation gazebo_sim.launch.py
  ```
  *(Or log out of Ubuntu, click the gear icon on the login screen, and select "Ubuntu on Xorg").*

---

### Issue 9: SLAM Map Not Showing in RViz2 (QoS Mismatch)
- **Symptom:** RViz2 displays status `Warn: No map received` on the Map display layer even though `slam_toolbox` is running.
- **Likely Cause:** In RViz2, the Map display's Durability policy is set to `Volatile` while SLAM Toolbox publishes with `Transient Local`.
- **Safe Fix:**
  In RViz2 left panel:
  1. Expand **Map**.
  2. Expand **Topic**.
  3. Change **Durability Policy** from `Volatile` to `Transient Local`.
  The occupancy map will immediately appear! (Note: Our `navigation.rviz` is already pre-configured with `Transient Local`).

---

### Issue 10: Colcon Build Ignores Python Changes
- **Symptom:** You modify `serial_bridge_node.py`, but running `ros2 run robot_hardware serial_bridge_node` executes the old code!
- **Likely Cause:** The workspace was built with plain `colcon build` rather than `--symlink-install`. Python files were copied into `install/` once at build time.
- **Safe Fix:**
  Always rebuild with:
  ```bash
  colcon build --symlink-install
  source install/setup.bash
  ```

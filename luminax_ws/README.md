# LUMINAX / LUMI — ROS 2 Jazzy Navigation Workspace

A ROS 2 **Jazzy** workspace for the LUMINAX healthcare companion robot's
**navigation base**: robot description, RPLiDAR driver, **laser odometry
(rf2o — no wheel encoders needed)**, a **Raspberry Pi 5 GPIO motor
controller**, SLAM mapping, and Nav2 autonomous navigation.

This matches the 7-step bring-up plan. **Perception, voice, display and the
caregiver app are intentionally not in this workspace** — this is the mobility
foundation you build those on later.

---

## ⚠️ Read before you power anything

- This code has **not** been run on ROS 2 or on your hardware — it can't be,
  from where it was generated. It has been checked only for **Python syntax,
  XML well-formedness and YAML validity**. Treat the first `colcon build` and
  every hardware step as a real test, not a formality.
- **A software watchdog is not an emergency stop.** You must wire a **physical
  latching e-stop that cuts motor power**. Do your first motor tests with the
  **wheels off the ground**.
- Every value marked `(MEASURE)` / `(EDIT)` in the URDF and YAML files is a
  placeholder. Wrong wheel radius, wheel separation or GPIO pins will cause
  wrong motion or damage. Confirm them first.

---

## What's in here

```
luminax_ws/
├── install_dependencies.sh         # apt + git clone of source deps
└── src/
    ├── luminax_description/         # URDF/xacro, TF, RViz config
    ├── luminax_base/                # motor_driver_node (cmd_vel -> GPIO)
    └── luminax_bringup/             # launch + config (lidar, rf2o, slam, nav2)
```

Two third-party packages are **cloned by the install script** (they are not
Jazzy apt binaries): `sllidar_ros2` (RPLiDAR driver) and `rf2o_laser_odometry`
(laser odometry, `ros2` branch).

---

## Step 1 — OS + ROS 2

- Raspberry Pi 5, **Ubuntu Server 24.04 (headless)**.
- Install **ROS 2 Jazzy** (`ros-jazzy-ros-base`) per the official docs.
- Laptop (same LAN) with ROS 2 Jazzy + RViz2 for visualization/teleop.

Put both machines on the **same `ROS_DOMAIN_ID`** so they see each other:

```bash
echo 'export ROS_DOMAIN_ID=17' >> ~/.bashrc   # same number on Pi and laptop
echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

## Build

```bash
cd ~/luminax_ws            # put this folder at ~/luminax_ws (or adjust paths)
./install_dependencies.sh  # apt deps + clones sllidar_ros2 & rf2o
colcon build --symlink-install
source install/setup.bash
```

---

## Step 2 — Robot description & TF

Measure the robot and edit `src/luminax_description/urdf/luminax.urdf.xacro`
(the `(MEASURE)` properties at the top: `wheel_radius`, `wheel_separation`,
`lidar_x/y/z`, `lidar_yaw`, `camera_z`, …).

Visualize (run RViz on the laptop):

```bash
ros2 launch luminax_description description.launch.py rviz:=true
```

You should see the robot model and the TF frames
`base_footprint → base_link → laser_frame` (+ camera/imu/wheels).

## Step 3 — LiDAR + laser odometry

Find the LiDAR's serial port (`ls /dev/ttyUSB*`), give it permission if needed
(`sudo usermod -aG dialout $USER` then re-login), then:

```bash
# LiDAR only — confirm /scan first
ros2 launch luminax_bringup lidar.launch.py serial_port:=/dev/ttyUSB0
ros2 topic hz /scan          # expect ~5.5–10 Hz for an A1

# Then laser odometry (publishes /odom + odom->base_footprint)
ros2 launch luminax_bringup rf2o.launch.py
ros2 topic echo /odom --once
```

> If the scan looks rotated 180°, set `lidar_yaw` to `3.14159` in the xacro and
> rebuild. `init_pose_from_topic` **must stay empty** in `config/rf2o.yaml`.

## Step 4 — Motor control (Pi 5 GPIO)

1. Set `driver_mode` in `src/luminax_base/config/base_params.yaml`:
   `dual_pwm` for BTS7960, `pwm_dir` for Cytron MDD10A.
2. Confirm the **BCM pin numbers** match your wiring.
3. **Test the logic first with no motors moving** (dry run):

   ```bash
   ros2 launch luminax_base base.launch.py use_hardware:=false
   ros2 run teleop_twist_keyboard teleop_twist_keyboard   # watch the [DRY-RUN] duty logs
   ```

4. **Wheels off the ground**, physical e-stop ready, then:

   ```bash
   ros2 launch luminax_base base.launch.py        # real GPIO
   ```

   - If a wheel spins the wrong way, set `invert_left` / `invert_right: true`.
   - Tune `max_wheel_speed` (m/s at full duty) by measuring real speed.
   - Angular velocity is capped at `0.5 rad/s` to keep rf2o odometry stable.

   The node **stops the motors if `/cmd_vel` goes quiet** for
   `cmd_vel_timeout` (0.5 s).

## Step 5 — TF tree + teleop

```bash
# On the robot — bring up description + lidar + rf2o + base together:
ros2 launch luminax_bringup robot.launch.py serial_port:=/dev/ttyUSB0

# On the laptop:
ros2 run tf2_tools view_frames          # produces frames.pdf
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Expected TF chain:
`odom → base_footprint → base_link → laser_frame`.
Drive gently (wheels still raised for the first check) and confirm the model
moves in RViz via rf2o feedback.

## Step 6 — Build a map (slam_toolbox)

```bash
# On the robot (brings the robot up too):
ros2 launch luminax_bringup slam.launch.py serial_port:=/dev/ttyUSB0

# On the laptop: RViz, Fixed Frame = map, drive slowly to map the space.
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Save:
ros2 run nav2_map_server map_saver_cli -f ~/luminax_ws/src/luminax_bringup/maps/home
```

## Step 7 — Autonomous navigation (Nav2)

Edit `src/luminax_bringup/config/nav2_params.yaml` `(EDIT)` values —
`robot_radius`, `inflation_radius`, velocity limits — to match the robot. Then:

```bash
ros2 launch luminax_bringup navigation.launch.py \
  map:=$HOME/luminax_ws/src/luminax_bringup/maps/home.yaml \
  serial_port:=/dev/ttyUSB0
```

In RViz2: **2D Pose Estimate** to seed AMCL, then **2D Goal Pose** to send the
robot to a target. Keep the e-stop in hand for the first autonomous runs.

---

## Verification status (what was and wasn't checked)

| Check | Status |
|---|---|
| Python syntax (`py_compile`) on all nodes/launch | ✅ done here |
| XML well-formed (URDF/xacro, package.xml) | ✅ done here |
| YAML valid (all configs) | ✅ done here |
| `colcon build` on ROS 2 Jazzy | ❌ you must run |
| LiDAR `/scan`, rf2o `/odom`, motor GPIO | ❌ hardware — you must run |
| SLAM / Nav2 on the real robot | ❌ you must run |

## Known design trade-offs

- **Laser-only odometry (rf2o)** needs no encoders but drifts in fast rotation
  and featureless spaces. Later, add wheel encoders and/or the IMU with
  `robot_localization` (EKF) to fuse `/odom` + IMU for robustness.
- The motor node is **open-loop** (commanded speed → PWM duty). Without encoder
  feedback the two wheels may not match exactly; expect to tune
  `max_wheel_speed`, `invert_*`, and possibly a per-wheel scale later.

## Troubleshooting

- **No `/scan`** → wrong `serial_port`, or no `dialout` permission.
- **TF errors / missing `odom`** → rf2o not running, or `/scan` empty.
- **Robot drifts in RViz when still** → normal small rf2o drift; slow down turns.
- **`sllidar_ros2` / `rf2o` not found** → re-run `install_dependencies.sh`,
  rebuild, re-`source install/setup.bash`.
- **Motor node logs `DRY-RUN` on the Pi** → `python3-lgpio`/`python3-gpiozero`
  missing, or `use_hardware:=false`.

# 10 — Last-Minute Final Viva Cheat Sheet

```
========================================================================================
Project: LUMI — AI Autonomous Healthcare Companion Robot
Target Environment: Ubuntu 22.04 LTS | ROS 2 Humble Hawksbill
Audience: 10-Minute Rapid Defense Review Before Facing Faculty & External Examiners
========================================================================================
```

---

## 1. Top 10 Core Formulas You Must Know By Heart

1. **Differential-Drive Forward Kinematics:**
   $$v_L = v_x - \frac{\omega_z \cdot L}{2}, \quad v_R = v_x + \frac{\omega_z \cdot L}{2}$$
   *(Where $L = 0.32\,\text{m}$ is wheel track, $v_x$ is linear speed, $\omega_z$ is yaw rate).*

2. **Inverse Kinematics (Wheel Speeds to Robot Twist):**
   $$v = \frac{v_R + v_L}{2}, \quad \omega = \frac{v_R - v_L}{L}$$

3. **Encoder Ticks to Linear Wheel Displacement:**
   $$\Delta d = \frac{\Delta\text{ticks}}{\text{CPR}} \times (2\pi r) = \frac{\Delta\text{ticks}}{334} \times (2\pi \times 0.04)$$

4. **Planar Odometry Midpoint Integration:**
   $$\Delta d = \frac{d_R + d_L}{2}, \quad \Delta\theta = \frac{d_R - d_L}{L}$$
   $$\Delta x = \Delta d \cos\left(\theta + \frac{\Delta\theta}{2}\right), \quad \Delta y = \Delta d \sin\left(\theta + \frac{\Delta\theta}{2}\right), \quad \theta_{\text{new}} = \theta + \Delta\theta$$

5. **2D Heading Yaw ($\theta$) to Quaternion ($q_z, q_w$):**
   $$q_x = 0, \quad q_y = 0, \quad q_z = \sin\left(\frac{\theta}{2}\right), \quad q_w = \cos\left(\frac{\theta}{2}\right)$$

6. **Monocular Visual Distance Approximation:**
   $$\text{Distance} \approx \frac{H_{\text{human}} \cdot f_{\text{pixels}}}{h_{\text{bbox\_pixels}}} \approx \frac{1.7 \cdot (0.8 \cdot w)}{h_{\text{bbox}}}$$

7. **Normalized Visual Bearing (-1.0 to 1.0):**
   $$\text{Bearing} = \frac{x_{\text{center}} - (w_{\text{frame}} / 2)}{w_{\text{frame}} / 2}$$

8. **Cylinder Inertia Tensor ($I_{zz}, I_{xx}$):**
   $$I_{zz} = \frac{1}{2} m r^2, \quad I_{xx} = I_{yy} = \frac{1}{12} m (3r^2 + h^2)$$

9. **Sphere Inertia Tensor (Caster Ball):**
   $$I = \frac{2}{5} m r^2$$

10. **12V Li-ion Battery Percentage Formula:**
    $$\text{Percentage} = \text{clamp}\left(\frac{V_{\text{bat}} - 10.5\,\text{V}}{12.6\,\text{V} - 10.5\,\text{V}}, 0.0, 1.0\right)$$

---

## 2. Essential ROS 2 CLI Commands Cheat Sheet

| Task | Exact Terminal Command |
| :--- | :--- |
| **Build Workspace** | `cd ~/luminax/robot_ws && colcon build --symlink-install` |
| **Source Environment** | `source /opt/ros/humble/setup.bash && source ~/luminax/robot_ws/install/setup.bash` |
| **Run Unit Tests** | `python3 -m unittest discover -s tests -p "test_*.py" -v` |
| **Master Simulation** | `ros2 launch robot_bringup bringup_full_system.launch.py use_sim:=true` |
| **Physical Hardware** | `ros2 launch robot_bringup bringup_full_system.launch.py use_sim:=false use_sim_time:=false` |
| **Inspect Active Topics** | `ros2 topic list -t` |
| **Check LiDAR Hz** | `ros2 topic hz /scan` |
| **Echo Odometry** | `ros2 topic echo /odom` |
| **Inspect TF Tree** | `ros2 run tf2_tools view_frames && evince frames.pdf` |
| **Echo Live Transform**| `ros2 run tf2_ros tf2_echo odom base_footprint` |
| **Trigger Reminder** | `ros2 service call /health/trigger_reminder std_srvs/srv/Trigger` |
| **Acknowledge Reminder**| `ros2 service call /health/acknowledge_reminder std_srvs/srv/Trigger` |
| **Keyboard Teleop** | `ros2 run teleop_twist_keyboard teleop_twist_keyboard` |
| **Save SLAM Map** | `ros2 run nav2_map_server map_saver_cli -f hospital_room_map` |

---

## 3. The 5-Minute Flawless Viva Demonstration Script

1. **Step 1: Open Code & Run Test Suite**
   - Open terminal: `python3 -m unittest discover -s tests -p "test_*.py" -v`.
   - *Tell Faculty:* *"Before launching any graphical tools, here is our automated validation suite comprising 21 unit tests covering differential kinematics, odometry calculations, JSON serial parsing, FSM behavior transitions, and XML package manifests. All 21 tests pass with 100% success."*
2. **Step 2: Launch Gazebo Simulation & RViz2**
   - Execute: `ros2 launch robot_bringup bringup_full_system.launch.py use_sim:=true`.
   - Point out Gazebo on the left and RViz2 on the right.
   - *Tell Faculty:* *"Notice our parametric differential chassis with two driven wheels and rear caster. The ODE physics engine simulates real contact friction, inertia tensors, and ray-casting. On RViz, you can observe live 720-point LiDAR scans in red, the TF tree, and the dynamic occupancy map from SLAM Toolbox."*
3. **Step 3: Demonstrate SLAM & Navigation**
   - In RViz2, click **2D Goal Pose** and place a marker in an open area.
   - Observe the robot dynamically plan a green path (`/plan`) and drive smoothly toward the goal while avoiding the center pillar.
4. **Step 4: Demonstrate Perception & Companion Interaction**
   - In terminal, echo `/perception/person_detected` and `/behaviour/current_state`.
   - Show how detecting a person transitions the FSM from `IDLE` to `INTERACTING` and triggers voice greeting: *"Hello! I am LUMI, your personal healthcare companion."*
5. **Step 5: Demonstrate Healthcare Reminder & Emergency Stop**
   - Trigger reminder: `ros2 service call /health/trigger_reminder std_srvs/srv/Trigger`.
   - Show state transitioning to `REMINDER`. Wait 30 seconds to show automatic escalation to `EMERGENCY` with voice alarm: *"Warning! Medicine reminder unacknowledged. Contacting caregiver."*
   - Show that in `EMERGENCY`, all velocity commands to `/cmd_vel` are locked to `0.0` for physical safety.

---

## 4. Top 10 Questions Faculty Are Guaranteed to Ask

1. **"Why does your robot not have arms?"**
   - *Answer:* LUMI is designed as an Autonomous Mobile Companion Robot (AMR). Manipulation introduces severe mechanical and safety hazards in domestic eldercare; our technical focus is robust autonomous mobility, SLAM mapping, perception, and reminder workflows.
2. **"How does the robot know where it is without GPS?"**
   - *Answer:* Indoors, LUMI relies on SLAM (using LiDAR scan matching + wheel odometry) to build a map, and AMCL (a particle filter) to probabilistically match live scans against the static map.
3. **"What is the difference between `base_link` and `base_footprint`?"**
   - *Answer:* `base_footprint` is the 2D projection on the floor ($Z = 0$) used for planar navigation costmaps. `base_link` is at the robot's center of mass ($Z = 0.04\,\text{m}$) containing the physical 3D mesh and inertia tensors.
4. **"What prevents duplicate TF publishers in your system?"**
   - *Answer:* Our master launch file uses an exclusive flag `use_sim`. When `use_sim:=true`, Gazebo's plugin publishes `odom -> base_footprint`. When `use_sim:=false`, `serial_bridge_node` publishes it. They are never run simultaneously.
5. **"What happens if serial communication between the RPi 5 and ESP32 drops?"**
   - *Answer:* Both sides have watchdog timers. If the ESP32 receives no serial packet for $>500\,\text{ms}$, it forces PWM to zero and halts the motors. If the RPi receives no telemetry, it switches to software loopback.
6. **"Why did you use OpenCV HOG+SVM instead of YOLOv8?"**
   - *Answer:* The Raspberry Pi 5 has an ARM CPU without a dedicated GPU. YOLOv8 runs at only 2–3 FPS and causes thermal throttling. OpenCV's HOG+SVM runs natively at 15–20 FPS on CPU, providing fast, lightweight person detection.
7. **"Why is `camera_optical_link` needed?"**
   - *Answer:* Robotics body frames follow REP-103 ($X$ forward, $Y$ left, $Z$ up). Camera image optics follow OpenCV standard ($Z$ forward, $X$ right, $Y$ down). `camera_optical_joint` applies the necessary rotation matrix.
8. **"Why did you use an asynchronous thread in `voice_node.py`?"**
   - *Answer:* `pyttsx3.runAndWait()` blocks until speech finishes. If run inside a ROS 2 callback, it would freeze the executor for several seconds, dropping timer events and sensor packets. A queue + background worker thread keeps the ROS callback non-blocking.
9. **"What is the difference between Global Costmap and Local Costmap?"**
   - *Answer:* The Global Costmap covers the entire house map for long-term path planning via NavFn (A*). The Local Costmap is a rolling $3\,\text{m} \times 3\,\text{m}$ window centered on the robot that updates at 5 Hz from live LiDAR to avoid dynamic obstacles.
10. **"What is your robot's wheel radius and track width?"**
    - *Answer:* Wheel radius $r = 0.04\,\text{m}$ (4 cm, 8 cm diameter), and wheel track separation $L = 0.32\,\text{m}$ (32 cm).

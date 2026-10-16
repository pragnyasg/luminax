# 07 — Comprehensive Viva Question Bank (55 Questions & Answers)

```
========================================================================================
Project: LUMI — AI Autonomous Healthcare Companion Robot
Target Environment: Ubuntu 22.04 LTS | ROS 2 Humble Hawksbill
Audience: Academic Faculty, External Examiners & Student Defense Preparation
========================================================================================
```

---

## Group 1: Project Architecture & System Scope

#### Q1: What is the primary objective of Project LUMI?
**Answer:** LUMI is an Autonomous Mobile Robot (AMR) designed as an indoor healthcare companion. It focuses on integrating ROS 2 differential-drive navigation, 2D SLAM mapping, person perception via computer vision, and companion assistance workflows (such as scheduled medication reminders with emergency escalation) onto a coherent embedded robotics platform.

#### Q2: Why does LUMI not have robotic arms or manipulators?
**Answer:** This was an explicit engineering design choice. Robotic manipulation adds significant mechanical complexity, high payload requirements, inverse kinematics solvers, and safety hazards without adding value to indoor mobile patrol. LUMI prioritizes robust mobility, reliable autonomous obstacle avoidance, SLAM mapping, and interactive voice/vision workflows over complex manipulation.

#### Q3: What is the division of labor between the Raspberry Pi 5 and the ESP32?
**Answer:** 
- The **Raspberry Pi 5** runs Ubuntu 22.04 LTS and the complete high-level ROS 2 Humble stack (SLAM, Nav2, computer vision, voice synthesis, and behavior FSM).
- The **ESP32** runs bare-metal C++ firmware to execute hard real-time tasks: 20 kHz ultrasonic motor PWM generation via LEDC, optical encoder interrupt accumulation (ISRs), battery ADC voltage sensing, and a 500 ms safety watchdog.

#### Q4: How is software modularity maintained across the repository?
**Answer:** The repository is partitioned into 9 specialized ROS 2 packages inside `robot_ws/src/`: `robot_description` (URDF/Xacro), `robot_simulation` (Gazebo worlds/launch), `robot_hardware` (serial bridge/odometry), `robot_navigation` (SLAM/Nav2 configs), `robot_perception` (vision), `robot_voice` (TTS), `robot_health` (reminders), `robot_behaviour` (FSM), and `robot_bringup` (master orchestration).

---

## Group 2: ROS 2 Fundamentals & Middleware

#### Q5: What is the fundamental difference between ROS 1 and ROS 2?
**Answer:** ROS 1 relied on a centralized master node (`roscore`) as a lookup registry; if `roscore` crashed, the entire communication network collapsed. ROS 2 eliminates `roscore` by adopting the industrial **DDS (Data Distribution Service)** standard, enabling peer-to-peer discovery, deterministic real-time communication, quality-of-service (QoS) tuning, and cross-platform native execution.

#### Q6: What is DDS and how does discovery work in ROS 2?
**Answer:** DDS (Data Distribution Service) is an open standard middleware for data-centric publish-subscribe systems. Nodes discover each other automatically across the local subnet using multicast UDP packets (RTPS protocol) matching participant GUIDs and topic type hashes, without requiring a central server.

#### Q7: What is the purpose of `colcon build --symlink-install`?
**Answer:** `colcon` is the collective construction build tool in ROS 2. The `--symlink-install` flag creates symbolic links from the `install/` directory to source files in `src/` (for Python scripts, launch files, and YAML configs). This allows developers to edit code and immediately test it without re-running compilation.

#### Q8: What is a ROS 2 lifecycle node?
**Answer:** A lifecycle node implements a managed finite state machine (`Unconfigured` $\to$ `Inactive` $\to$ `Active` $\to$ `Finalized`). It prevents nodes from processing inputs or publishing data until all hardware interfaces and configuration parameters have been successfully initialized. Nav2 heavily relies on lifecycle nodes for deterministic startup.

---

## Group 3: Topics, Publishers & Subscribers

#### Q9: What is a ROS 2 topic and what communication pattern does it use?
**Answer:** A topic is a named unidirectional bus over which nodes exchange strongly typed messages. It uses the asynchronous Publish/Subscribe pattern, decoupling data producers from consumers.

#### Q10: What message type is published on `/cmd_vel`?
**Answer:** `geometry_msgs/msg/Twist`. It contains two vector sub-fields: `linear` ($\begin{bmatrix}x & y & z\end{bmatrix}$) and `angular` ($\begin{bmatrix}x & y & z\end{bmatrix}$). In LUMI's planar differential base, only `linear.x` (forward speed) and `angular.z` (yaw turning rate) are non-zero.

#### Q11: What message type is published on `/scan`?
**Answer:** `sensor_msgs/msg/LaserScan`. It encapsulates 2D planar range readings: `angle_min`, `angle_max`, `angle_increment`, `range_min`, `range_max`, and a dynamic float array `ranges[]` containing distance measurements in meters.

#### Q12: How can you inspect live topic frequency in the terminal?
**Answer:** Using the CLI command `ros2 topic hz <topic_name>`. For example, `ros2 topic hz /scan` confirms if the LiDAR is publishing at its target 10 Hz rate.

---

## Group 4: Services and Actions

#### Q13: How does a ROS 2 Service differ from a Topic?
**Answer:** A Topic is continuous, asynchronous, and one-way (pub/sub). A Service is synchronous, two-way, and follows a Request/Response pattern. A client node sends a request to a server node and blocks or awaits a callback until the server returns a result.

#### Q14: Which services are implemented in LUMI?
**Answer:**
- `/health/trigger_reminder` (`std_srvs/srv/Trigger`): Triggers a medication reminder on demand.
- `/health/acknowledge_reminder` (`std_srvs/srv/Trigger`): Confirms medicine was taken.
- `/behaviour/reset_state` (`std_srvs/srv/Trigger`): Resets FSM back to IDLE.
- `/slam_toolbox/save_map` (`slam_toolbox/srv/SaveMap`): Saves the generated occupancy grid.

#### Q15: What is a ROS 2 Action and when should it be used instead of a Service?
**Answer:** An Action is an asynchronous, long-running, preemptible goal interaction with continuous feedback. It is used when a task takes noticeable time to complete (e.g., navigating across a house via `/navigate_to_pose`). Unlike a service, the client can monitor intermediate progress (distance remaining) and cancel the goal if an obstacle blocks the path.

#### Q16: What three sub-protocols constitute a ROS 2 Action?
**Answer:** An action internally combines two services (`send_goal` and `get_result`) and one topic (`feedback`).

---

## Group 5: Quality of Service (QoS), Callbacks & Executors

#### Q17: What are the two primary Reliability QoS policies in ROS 2?
**Answer:**
1. **Best Effort:** Messages are sent without acknowledgment; if packets are dropped due to network traffic, they are not retransmitted (used for high-rate sensor streams like `/scan` and `/camera/image_raw`).
2. **Reliable:** Guarantees delivery via packet acknowledgments and retries (used for navigation commands on `/cmd_vel` and discrete alarms).

#### Q18: What is Transient Local durability in QoS?
**Answer:** `Transient Local` instructs the publisher to store the last sent message. When a new subscriber joins the network late (such as launching RViz after mapping has started), it immediately receives the historical message without waiting for a re-transmission. This is essential for the `/map` topic.

#### Q19: What is a ROS 2 Executor?
**Answer:** An Executor is the runtime engine that coordinates incoming messages on callbacks, timer expirations, service requests, and action goals. ROS 2 provides `SingleThreadedExecutor` (processes callbacks sequentially) and `MultiThreadedExecutor` (dispatches callbacks concurrently across a thread pool).

#### Q20: Why did we use an asynchronous worker thread in `voice_node.py`?
**Answer:** If text-to-speech synthesis (`pyttsx3.runAndWait()`) executed synchronously inside `speak_callback`, the node's thread would freeze for 3–5 seconds while reading a sentence. During that time, the node could not process other incoming callbacks or timer ticks. Using an internal Python queue with a dedicated worker thread keeps the ROS callback execution instantaneous (<0.1 ms).

---

## Group 6: URDF, Xacro & Coordinate Frames (TF2)

#### Q21: What is the difference between URDF and Xacro?
**Answer:** URDF (Unified Robot Description Format) is raw XML; it cannot reuse code, compute math, or accept parameters. Xacro (XML Macros) extends URDF with macro definitions (`<xacro:macro>`), property constants (`<xacro:property>`), conditional evaluation, and mathematical expressions, making robot descriptions modular and maintainable.

#### Q22: What is the difference between `base_footprint` and `base_link`?
**Answer:**
- `base_footprint`: Projected on the floor surface ($Z = 0$), serving as the 2D ground projection reference for planar navigation and footprint obstacle checks.
- `base_link`: Centered on the physical chassis ($Z = 0.04\,\text{m}$), containing the actual 3D visual geometry, collision boundaries, and inertial tensors.

#### Q23: Why is `camera_optical_link` oriented differently from `camera_link`?
**Answer:** Robotics standards (REP-103) specify that links use $X$-forward, $Y$-left, $Z$-up. Optical sensor conventions (REP-105 / OpenCV) specify that cameras use $Z$-forward (out of the lens), $X$-right, $Y$-down. The fixed joint `camera_optical_joint` applies a $-\pi/2$ yaw and $-\pi/2$ pitch rotation to align optical image coordinates with the robot body.

#### Q24: What is the TF tree and what publishes each transform in LUMI?
**Answer:**
- `map -> odom`: Published by `slam_toolbox` (in mapping mode) or `amcl` (in localization mode).
- `odom -> base_footprint`: Published by Gazebo's `diff_drive_controller` (in simulation) OR `serial_bridge_node` (on physical hardware).
- `base_footprint -> base_link -> sensor_links`: Published by `robot_state_publisher` using joint states and URDF geometry.

---

## Group 7: Gazebo Classic 11 & RViz2

#### Q25: What is the exact distinction between Gazebo and RViz2?
**Answer:**
- **Gazebo** is a physics-based simulation world generator. It simulates rigid-body mass, inertia, friction, contact forces, and generates synthetic sensor readings.
- **RViz2** is purely a 3D visualization window. It has no physics engine; it merely renders what the robot's onboard software perceives (coordinate frames, laser scans, costmaps, and paths).

#### Q26: What plugins are configured in `healthcare_robot.urdf.xacro` for Gazebo?
**Answer:**
1. `libgazebo_ros_diff_drive.so`: Simulates differential-drive wheel joints, accepts `/cmd_vel`, and publishes `/odom`.
2. `libgazebo_ros_ray_sensor.so`: Simulates LiDAR ray casting across 720 samples and publishes `/scan`.
3. `libgazebo_ros_camera.so`: Simulates camera optics and publishes `/camera/image_raw`.

#### Q27: Why must `use_sim_time` be set to `true` when running Gazebo?
**Answer:** In simulation, physics step sizes vary depending on CPU load. Setting `use_sim_time:=true` forces ROS 2 nodes to synchronize their timestamps with the simulated clock published on `/clock` by Gazebo, preventing time-extrapolation and transform-dropout errors.

#### Q28: How is the caster wheel modeled in Gazebo to prevent turning friction?
**Answer:** The caster sphere is given near-zero friction parameters: `<mu1>0.001</mu1>` and `<mu2>0.001</mu2>`. This allows the ball to slide effortlessly across the ground without resisting turning torque.

---

## Group 8: Differential-Drive Kinematics & Odometry

#### Q29: What are the forward differential-drive kinematic equations?
**Answer:** Given linear speed $v$ and angular rate $\omega$, with track separation $L$:
$$v_L = v - \frac{\omega \cdot L}{2}, \quad v_R = v + \frac{\omega \cdot L}{2}$$

#### Q30: What are the inverse kinematic equations?
**Answer:** Given measured left and right wheel speeds $v_L$ and $v_R$:
$$v = \frac{v_R + v_L}{2}, \quad \omega = \frac{v_R - v_L}{L}$$

#### Q31: How are encoder ticks converted into wheel displacement?
**Answer:** With wheel radius $r = 0.04\,\text{m}$ and encoder counts per revolution $\text{CPR} = 334$:
$$\Delta d = \frac{\Delta\text{ticks}}{\text{CPR}} \times (2\pi r) = \frac{\Delta\text{ticks}}{334} \times (2\pi \times 0.04)$$

#### Q32: Why is Runge-Kutta / midpoint integration preferred over Euler integration for odometry?
**Answer:** Euler integration assumes heading is constant throughout the time interval ($\Delta x = \Delta d \cos\theta$), leading to compounding drift during turns. Midpoint integration uses the average heading ($\Delta x = \Delta d \cos(\theta + \Delta\theta / 2)$), matching the true curved trajectory and dramatically reducing odometry error.

---

## Group 9: SLAM Toolbox

#### Q33: What is the full form of SLAM and what core problem does it solve?
**Answer:** **Simultaneous Localization and Mapping**. It solves the problem of placing a robot in an unknown environment with no GPS and simultaneously building a consistent metric map while determining the robot's coordinates inside that map.

#### Q34: What algorithm does SLAM Toolbox use?
**Answer:** SLAM Toolbox uses pose-graph SLAM with Ceres scan-matching optimization and Karto-based graph formulation. It constructs a graph where nodes represent robot poses and edges represent spatial constraints derived from laser scan matching and wheel odometry.

#### Q35: What is a loop closure in SLAM?
**Answer:** A loop closure occurs when the robot recognizes an area it visited earlier. SLAM Toolbox matches the current scan against historical submaps, detects the loop, and applies global graph relaxation to eliminate accumulated odometry drift across the entire map.

#### Q36: How do you save a completed map generated by SLAM Toolbox?
**Answer:**
```bash
ros2 run nav2_map_server map_saver_cli -f my_room_map
```
This produces `my_room_map.pgm` (occupancy image) and `my_room_map.yaml` (metadata).

---

## Group 10: Nav2 & AMCL

#### Q37: What is AMCL and how does it work?
**Answer:** **Adaptive Monte Carlo Localization**. It uses a KLD-sampling particle filter to track the robot's pose on a known map. Each particle represents a hypothesized pose $(x, y, \theta)$. As the robot moves, particles are updated via odometry and weighted by matching live LiDAR scans against expected map obstacles. Over time, particles converge tightly around the true pose.

#### Q38: What is the role of the Global Planner in Nav2?
**Answer:** Nav2's global planner (`nav2_navfn_planner::NavfnPlanner`) calculates the shortest, collision-free geometric path from the robot's current pose to the goal pose across the static global costmap using Dijkstra or A* graph search algorithms.

#### Q39: What is the role of the Local Controller (DWB Local Planner)?
**Answer:** The DWB controller generates actual motor velocity commands on `/cmd_vel` to track the global path. It samples a dynamic window of feasible $(v, \omega)$ trajectories, projects them forward in time, evaluates cost critics (distance to path, goal alignment, obstacle clearance), and chooses the optimal trajectory.

#### Q40: What happens if an obstacle blocks LUMI's path during navigation?
**Answer:**
1. The obstacle appears in the live local costmap via LiDAR rays.
2. The DWB controller attempts to steer around it.
3. If completely blocked, the Behavior Tree (`bt_navigator`) engages recovery plugins: clearing costmaps, backing up (`nav2_behaviors/BackUp`), spinning in place (`nav2_behaviors/Spin`), or requesting a new global path plan.

---

## Group 11: Computer Vision Integration

#### Q41: Which computer vision algorithm is implemented in `person_detector_node.py`?
**Answer:** OpenCV's Histogram of Oriented Gradients (HOG) feature extractor coupled with a pre-trained Linear Support Vector Machine (SVM) classifier (`cv2.HOGDescriptor_getDefaultPeopleDetector()`).

#### Q42: Why was HOG+SVM chosen instead of a heavyweight deep-learning model like YOLOv8?
**Answer:** The Raspberry Pi 5 runs on an embedded ARM Cortex-A76 CPU without a dedicated neural processing unit (NPU) or discrete GPU. Running large deep learning networks causes thermal throttling and reduces frame rates to 2–3 FPS. HOG+SVM runs natively at 15–20 FPS on CPU, providing immediate person detection without requiring multi-gigabyte weight files.

#### Q43: How does the node estimate person distance without a stereo or depth camera?
**Answer:** It uses monocular geometric pinhole camera approximation based on average human stature ($H_{\text{real}} \approx 1.7\,\text{m}$):
$$\text{Distance} \approx \frac{H_{\text{real}} \cdot f_{\text{pixels}}}{h_{\text{bbox\_pixels}}}$$
where $f_{\text{pixels}}$ is the calibrated focal length and $h_{\text{bbox\_pixels}}$ is the pixel height of the detected bounding box.

#### Q44: What topics does `person_detector_node` publish?
**Answer:**
- `/perception/person_detected` (`std_msgs/msg/Bool`)
- `/perception/person_count` (`std_msgs/msg/Int32`)
- `/perception/detections` (`std_msgs/msg/String` JSON)
- `/perception/image_annotated` (`sensor_msgs/msg/Image`)

---

## Group 12: ESP32 Communication & Firmware

#### Q45: What communication protocol connects the Raspberry Pi 5 and ESP32?
**Answer:** USB CDC Serial communication at 115200 Baud, exchanging newline-delimited (`\n`) JSON packets for structured, human-readable command and telemetry verification.

#### Q46: What is the format of velocity commands sent to the ESP32?
**Answer:**
```json
{"cmd": "vel", "v_l": 0.25, "v_r": 0.25}
```
where `v_l` and `v_r` are target wheel speeds in meters per second.

#### Q47: What is the format of telemetry returned by the ESP32?
**Answer:**
```json
{"enc_l": 1520, "enc_r": 1530, "v_bat": 12.1}
```
where `enc_l` and `enc_r` are raw accumulated encoder ticks and `v_bat` is battery voltage.

#### Q48: What safety mechanism exists in the ESP32 firmware?
**Answer:** A 500 ms command watchdog timer. If no valid JSON `vel` command is received for $> 500\,\text{ms}$, target velocities are automatically forced to `0.0`, halting the motors immediately.

---

## Group 13: Debugging, Testing & Diagnostics

#### Q49: What automated unit tests were created and verified for LUMI?
**Answer:** A comprehensive 21-test suite using Python's `unittest` framework:
1. Differential-drive forward and inverse kinematics.
2. Encoder tick conversion and quaternion normalization.
3. Angle wrapping in $[-\pi, \pi]$.
4. Serial JSON serialization and battery percentage calculation.
5. FSM state transitions and voice emergency stops.
6. Healthcare reminder scheduling and timeout escalation.
7. XML schema compliance for all 9 packages and URDF/Xacro files.
8. Clean compilation of all Python source files.

#### Q50: How do you inspect the live ROS 2 computation graph?
**Answer:** Execute `rqt_graph`. It renders a dynamic visual graph showing all running nodes, published topics, and subscription connections.

#### Q51: How do you verify coordinate frame continuity?
**Answer:** Run `ros2 run tf2_tools view_frames`. This listens to `/tf` for 5 seconds and generates `frames.pdf`, detailing all frame relationships, publishers, and transform buffer ages.

#### Q52: What command would you use to test the ESP32 bridge in software loopback mode?
**Answer:** Simply launch `serial_bridge_node.py` without hardware connected. The node catches the serial open exception, logs a warning, and operates in software loopback mode, integrating simulated displacement from commanded velocities.

---

## Group 14: Limitations & Future Work

#### Q53: What are the current hardware limitations of this prototype?
**Answer:**
1. Motor control currently uses open-loop PWM duty cycle estimation rather than closed-loop PID velocity control on the ESP32.
2. Monocular distance estimation depends on upright human stature and is subject to variance compared to depth sensors.
3. The robot relies on 2D planar LiDAR, which cannot detect obstacles below or above the scanning plane (such as table overhangs or floor drop-offs).

#### Q54: What are the primary planned future enhancements?
**Answer:**
1. Implement onboard PID closed-loop motor velocity control inside the ESP32 firmware using encoder feedback.
2. Add an RGB-D depth camera (such as Intel RealSense D435) for 3D obstacle avoidance and pointcloud costmap clearing.
3. Integrate edge AI fall-detection models and caregiver notifications via WebSockets or a Flutter mobile app.

#### Q55: Why is this project academically rigorous?
**Answer:** Because it does not rely on pre-packaged black-box robotics bundles. We designed and parameterized the URDF robot description from first principles, implemented differential-drive kinematics and odometry integration, built the serial communication protocol and firmware, tuned SLAM Toolbox and Nav2 costmap configurations, integrated vision with healthcare supervisor logic, and validated the system through automated unit testing and full simulation.

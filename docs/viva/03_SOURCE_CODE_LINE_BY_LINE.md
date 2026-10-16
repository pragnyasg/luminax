# 03 — Exhaustive Line-by-Line Source Code Walkthrough & Defense Guide

```
========================================================================================
Project: LUMI — AI Autonomous Healthcare Companion Robot
Target Environment: Ubuntu 22.04 LTS | ROS 2 Humble Hawksbill
Coverage: Complete line-by-line explanation of every authored source file in the repository.
Format: File Path -> Architecture Role -> Line-by-Line Mechanics -> Viva Q&A
========================================================================================
```

---

## Table of Contents & File Coverage Checklist

- [x] **File 1:** `robot_description/urdf/healthcare_robot.urdf.xacro` (3D Physical & Inertial Robot Model)
- [x] **File 2:** `robot_hardware/robot_hardware/serial_bridge_node.py` (Differential Kinematics, Serial CDC, Odometry & TF)
- [x] **File 3:** `esp32_firmware/src/main.cpp` (20kHz PWM Motor Drive, ISR Encoder Tracking, Watchdog)
- [x] **File 4:** `robot_perception/robot_perception/person_detector_node.py` (OpenCV HOG+SVM Detection & Distance)
- [x] **File 5:** `robot_perception/robot_perception/webcam_publisher_node.py` (USB Camera Driver & Topic Publisher)
- [x] **File 6:** `robot_voice/robot_voice/voice_node.py` (Async Threaded Speech Output via Offline TTS)
- [x] **File 7:** `robot_health/robot_health/reminder_manager_node.py` (Medication Timers, Escalations, Trigger Services)
- [x] **File 8:** `robot_behaviour/robot_behaviour/behaviour_manager_node.py` (5-State FSM Supervisor & Safety Halts)
- [x] **File 9:** `robot_simulation/launch/gazebo_sim.launch.py` (Simulation Server, Spawner & Visualizer)
- [x] **File 10:** `robot_navigation/launch/slam.launch.py` & `navigation.launch.py` (SLAM Toolbox & Nav2 Bringup)
- [x] **File 11:** `robot_navigation/launch/full_navigation.launch.py` (Combined Sim + SLAM + Nav2 Orchestrator)
- [x] **File 12:** `robot_bringup/launch/bringup_full_system.launch.py` (Master Full System Launch with Sim/HW Switch)

---

## File 1: `robot_ws/src/robot_description/urdf/healthcare_robot.urdf.xacro`

### 1.1 Purpose and Architectural Role
This file is the single source of physical truth for the LUMI mobile base. It describes the robot's kinematic link tree, joint limits, visual geometry, collision boundaries, moments of inertia (required by ODE physics in Gazebo), and Gazebo Classic ROS integration plugins.

### 1.2 Line-by-Line Breakdown

#### Lines 1–16: Header & Pedagogical Overview
```xml
1: <?xml version="1.0"?>
2: <robot name="healthcare_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
```
- **Line 1:** XML declaration specifying XML version 1.0 standard.
- **Line 2:** Root `<robot>` tag named `healthcare_robot`. The XML namespace `xmlns:xacro` enables macro evaluations, property substitutions (`${...}`), and mathematical expressions.

#### Lines 17–44: Physical Properties & Dimensions
```xml
19:   <xacro:property name="chassis_radius" value="0.18" />   <!-- 36cm diameter body -->
20:   <xacro:property name="chassis_height" value="0.40" />   <!-- 40cm body height -->
21:   <xacro:property name="chassis_mass"   value="5.00" />   <!-- 5.0 kg total mass -->
24:   <xacro:property name="wheel_radius"   value="0.04" />   <!-- 8cm diameter wheel -->
25:   <xacro:property name="wheel_width"    value="0.02" />   <!-- 2cm wheel thickness -->
26:   <xacro:property name="wheel_track"    value="0.32" />   <!-- Distance between wheel centers -->
27:   <xacro:property name="wheel_mass"     value="0.25" />   <!-- 250 grams per wheel -->
30:   <xacro:property name="caster_radius"  value="0.02" />   <!-- 4cm diameter sphere -->
31:   <xacro:property name="caster_mass"    value="0.10" />   <!-- 100 grams -->
32:   <xacro:property name="caster_x_offset" value="-0.12" /> <!-- Positioned rear of chassis -->
```
- **Lines 19–21:** Defines the cylinder chassis: radius $r = 0.18\,\text{m}$ (36 cm diameter), height $h = 0.40\,\text{m}$ (40 cm), mass $m = 5.0\,\text{kg}$.
- **Lines 24–27:** Wheel dimensions: radius $r = 0.04\,\text{m}$ (8 cm diameter), thickness $w = 0.02\,\text{m}$, track separation $L = 0.32\,\text{m}$ (32 cm), mass $m = 0.25\,\text{kg}$.
- **Lines 30–33:** Passive caster ball: radius $0.02\,\text{m}$, positioned $12\,\text{cm}$ behind the wheel axis ($x = -0.12\,\text{m}$) to balance the differential base.
- **Lines 35–43:** LiDAR and camera bounding parameters.

#### Lines 66–93: Inertia Calculator Macros
```xml
67:   <xacro:macro name="cylinder_inertia" params="m r h">
68:     <inertial>
69:       <mass value="${m}"/>
70:       <inertia ixx="${(1/12)*m*(3*r*r + h*h)}" ixy="0.0" ixz="0.0"
71:                iyy="${(1/12)*m*(3*r*r + h*h)}" iyz="0.0"
72:                izz="${0.5*m*r*r}"/>
73:     </inertial>
74:   </xacro:macro>
```
- Standard analytic formulas for rotational inertia tensors:
  - Solid Cylinder (about central Z-axis): $I_{zz} = \frac{1}{2} m r^2$, $I_{xx} = I_{yy} = \frac{1}{12} m (3r^2 + h^2)$.
  - Solid Sphere (caster wheel): $I_{xx} = I_{yy} = I_{zz} = \frac{2}{5} m r^2$.
- *Why this matters in Viva:* Without physically accurate inertias, physics engines like ODE/Bullet in Gazebo will suffer numerical instability, causing the robot to jitter, bounce, or flip.

#### Lines 96–136: Base Footprint and Base Link
```xml
97:   <link name="base_footprint"/>
99:   <joint name="base_footprint_joint" type="fixed">
100:     <parent link="base_footprint"/>
101:     <child link="base_link"/>
102:     <origin xyz="0 0 ${wheel_radius}" rpy="0 0 0"/>
103:   </joint>
```
- **Line 97:** `base_footprint` is a zero-mass, zero-inertia virtual link located at the projection of the robot center on the floor ground plane ($Z = 0$).
- **Lines 99–103:** A `fixed` joint connects `base_footprint` to `base_link`. The origin offset $Z = 0.04\,\text{m}$ elevates `base_link` so the bottom of the wheels contact the ground at $Z = 0$.
- **Lines 105–131:** `base_link` defines the main chassis cylinder with visual color tags, collision geometry, and inertia.

#### Lines 138–174: Differential Wheel Macro & Joints
```xml
138:   <xacro:macro name="wheel" params="prefix y_reflect">
139:     <link name="${prefix}_wheel_link">
...
156:     <joint name="${prefix}_wheel_joint" type="continuous">
157:       <parent link="base_link"/>
158:       <child link="${prefix}_wheel_link"/>
159:       <origin xyz="0 ${y_reflect * wheel_track / 2} 0" rpy="0 0 0"/>
160:       <axis xyz="0 1 0"/>
161:     </joint>
```
- **Line 156:** `continuous` joint type allows unconstrained 360-degree continuous rotation (unlike `revolute` which requires upper/lower joint angle limits).
- **Line 159:** Origin positioned at $\pm 16\,\text{cm}$ ($y = \pm L/2$) along the Y-axis.
- **Line 160:** Rotation axis is $\begin{bmatrix}0 & 1 & 0\end{bmatrix}^T$ (pitch axis).
- **Lines 163–169:** Friction coefficients: $\mu_1 = \mu_2 = 1.0$ (high surface friction to prevent wheel slip).

#### Lines 176–205: Passive Balancing Caster Wheel
```xml
196:     <origin xyz="${caster_x_offset} 0 ${caster_radius - wheel_radius}" rpy="0 0 0"/>
202:       <mu1>0.001</mu1>
203:       <mu2>0.001</mu2>
```
- **Line 196:** Placed at $x = -0.12\,\text{m}$, $z = 0.02 - 0.04 = -0.02\,\text{m}$.
- **Lines 202–203:** Crucial simulation friction parameters: $\mu_1 = \mu_2 = 0.001$ (nearly frictionless). In physical robotics, a caster wheel uses a swivel bearing or omni ball. In Gazebo, modeling a full caster swivel introduces joint oscillation; setting $\mu = 0.001$ lets the ball slide smoothly without resisting turning torque.

#### Lines 206–270: Sensor Links & Camera Optical Frame
```xml
263:   <link name="camera_optical_link"/>
265:   <joint name="camera_optical_joint" type="fixed">
266:     <parent link="camera_link"/>
267:     <child link="camera_optical_link"/>
268:     <origin xyz="0 0 0" rpy="${-pi/2} 0 ${-pi/2}"/>
269:   </joint>
```
- **Lines 263–269:** **REP-103 vs REP-105 Coordinate Frame Standard.**
  - Robotics Body Frame (`camera_link`): X forward, Y left, Z up.
  - Optical Frame (`camera_optical_link`): Z forward (along lens optical axis), X right, Y down.
  - The rotation $R = \text{Rot}_z(-\pi/2) \cdot \text{Rot}_x(-\pi/2)$ transforms body coordinates into optical conventions required by OpenCV and RViz Image displays.

#### Lines 275–303: Differential-Drive Gazebo Plugin
```xml
276:     <plugin name="diff_drive_controller" filename="libgazebo_ros_diff_drive.so">
279:         <remapping>cmd_vel:=/cmd_vel</remapping>
280:         <remapping>odom:=/odom</remapping>
288:       <wheel_separation>${wheel_track}</wheel_separation>
289:       <wheel_diameter>${2 * wheel_radius}</wheel_diameter>
296:       <publish_odom>true</publish_odom>
297:       <publish_odom_tf>true</publish_odom_tf>
300:       <odometry_frame>odom</odometry_frame>
301:       <robot_base_frame>base_footprint</robot_base_frame>
```
- **Line 276:** Loads `libgazebo_ros_diff_drive.so` from ROS 2 `gazebo_plugins`.
- **Lines 279–280:** Remaps input velocity commands to `/cmd_vel` and output odometry to `/odom`.
- **Lines 288–289:** Injects track separation ($0.32\,\text{m}$) and diameter ($0.08\,\text{m}$).
- **Lines 296–301:** Commands Gazebo to compute odometry from simulated wheel rotation and broadcast the `odom -> base_footprint` TF transform.

#### Lines 306–339: 2D LiDAR Ray Sensor Plugin
```xml
307:     <sensor type="ray" name="lidar_sensor">
314:           <samples>720</samples>
316:           <min_angle>-3.14159</min_angle>
317:           <max_angle>3.14159</max_angle>
321:           <min>0.12</min>
322:           <max>10.0</max>
328:           <stddev>0.01</stddev>
331:       <plugin name="lidar_plugin" filename="libgazebo_ros_ray_sensor.so">
333:           <remapping>~/out:=/scan</remapping>
335:         <output_type>sensor_msgs/LaserScan</output_type>
336:         <frame_name>lidar_link</frame_name>
```
- **Lines 314–317:** 720 samples across $2\pi$ radians ($360^\circ$) yields angular resolution $\Delta\theta = 0.5^\circ$.
- **Lines 321–328:** Range: $0.12\,\text{m}$ to $10.0\,\text{m}$ with Gaussian noise ($\sigma = 1\,\text{cm}$) for realistic measurement variance.
- **Line 333:** Publishes `sensor_msgs/msg/LaserScan` messages directly on `/scan`.

### 1.3 Faculty Viva Q&A on this File
- **Q:** *Why do we have both `base_footprint` and `base_link`?*
  - **A:** `base_footprint` sits on the ground floor plane ($Z = 0$), which simplifies 2D planar navigation (costmaps and footprint polygons). `base_link` sits at the center of mass ($Z = 0.04\,\text{m}$), which is necessary for 3D physics and inertial dynamics.
- **Q:** *What happens if `caster_wheel_link` has $\mu = 1.0$ in Gazebo?*
  - **A:** The robot will experience massive scrubbing friction whenever it attempts to turn. The drive wheels will slip, angular velocity $\omega_z$ will drop near zero, and the robot will stall.

---

## File 2: `robot_ws/src/robot_hardware/robot_hardware/serial_bridge_node.py`

### 2.1 Purpose and Architectural Role
This node is the hardware bridge between the ROS 2 computational graph and the physical ESP32 microcontroller over USB Serial CDC (`/dev/ttyUSB0` at 115200 baud).

### 2.2 Line-by-Line Breakdown

#### Lines 17–28: Imports & Serial Availability Check
```python
17: import rclpy
18: from rclpy.node import Node
19: from geometry_msgs.msg import Twist, TransformStamped
20: from nav_msgs.msg import Odometry
21: from sensor_msgs.msg import BatteryState
22: import tf2_ros
24: try:
25:     import serial
26:     HAS_SERIAL = True
27: except ImportError:
28:     HAS_SERIAL = False
```
- **Lines 17–22:** Standard ROS 2 Python libraries. `TransformStamped` and `tf2_ros.TransformBroadcaster` handle coordinate transforms.
- **Lines 24–28:** Safe import of `pyserial`. If running on a developer machine without physical hardware or serial drivers, `HAS_SERIAL` falls back to `False` and engages software loopback simulation.

#### Lines 35–48: Parameter Declarations
```python
36:         self.declare_parameter('port', '/dev/ttyUSB0')
37:         self.declare_parameter('baudrate', 115200)
38:         self.declare_parameter('wheel_track', 0.32)      # 32 cm
39:         self.declare_parameter('wheel_radius', 0.04)     # 4 cm
40:         self.declare_parameter('encoder_cpr', 334.0)     # Counts per rev
41:         self.declare_parameter('publish_tf', True)
42:         self.declare_parameter('cmd_vel_timeout', 0.5)   # 500ms safety watchdog
```
- Dynamic parameters declared so port, baud rate, and kinematic dimensions can be reconfigured via launch files without editing Python code.

#### Lines 92–105: `/cmd_vel` Callback & Forward Kinematics
```python
92:     def cmd_vel_callback(self, msg: Twist):
98:         self.last_cmd_vel_time = self.get_clock().now()
99:         linear_v = msg.linear.x
100:        angular_w = msg.angular.z
102:        self.v_left_target = linear_v - (angular_w * self.wheel_track / 2.0)
103:        self.v_right_target = linear_v + (angular_w * self.wheel_track / 2.0)
105:        self._send_speed_command(self.v_left_target, self.v_right_target)
```
- **Lines 102–103:** Differential-drive kinematic equations:
  $$v_L = v_x - \frac{\omega_z \cdot L}{2}, \quad v_R = v_x + \frac{\omega_z \cdot L}{2}$$
  - When $v_x = 0.2\,\text{m/s}$ and $\omega_z = 0$, $v_L = v_R = 0.2\,\text{m/s}$.
  - When rotating CCW ($\omega_z = 1.0\,\text{rad/s}$), $v_L = -0.16\,\text{m/s}$, $v_R = +0.16\,\text{m/s}$.

#### Lines 107–118: Serial JSON Packet Transmission
```python
107:     def _send_speed_command(self, v_l: float, v_r: float):
109:             packet = {
110:                 "cmd": "vel",
111:                 "v_l": round(v_l, 3),
112:                 "v_r": round(v_r, 3)
113:             }
115:             line = json.dumps(packet) + "\n"
116:             self.serial_port.write(line.encode('utf-8'))
```
- Formats a compact JSON packet and transmits over UART. Newline delimiter (`\n`) allows the microcontroller to use simple `readStringUntil('\n')` parsing.

#### Lines 120–150: 20Hz Update Loop, Watchdog & Telemetry
```python
120:     def update_loop(self):
127:         current_time = self.get_clock().now()
128:         dt = (current_time - self.last_time).nanoseconds / 1e9
135:         time_since_cmd = (current_time - self.last_cmd_vel_time).nanoseconds / 1e9
136:         if time_since_cmd > self.cmd_vel_timeout:
137:             if self.v_left_target != 0.0 or self.v_right_target != 0.0:
138:                 self.v_left_target = 0.0
139:                 self.v_right_target = 0.0
140:                 self._send_speed_command(0.0, 0.0)
```
- **Lines 135–140:** **Watchdog Safety.** If the host system lags, Nav2 aborts, or the wireless teleop connection drops for more than $0.5\,\text{s}$, the node resets target speeds to zero and stops the motors.

#### Lines 152–185: Encoder Tick Decoding & Battery State
```python
155:                     if 'enc_l' in data and 'enc_r' in data:
156:                         enc_l = int(data['enc_l'])
157:                         enc_r = int(data['enc_r'])
159:                         if self.prev_enc_l is not None and self.prev_enc_r is not None:
160:                             delta_l = enc_l - self.prev_enc_l
161:                             delta_r = enc_r - self.prev_enc_r
162:                             meters_per_tick = (2.0 * math.pi * self.wheel_radius) / self.encoder_cpr
163:                             d_left = delta_l * meters_per_tick
164:                             d_right = delta_r * meters_per_tick
```
- **Lines 162–164:** Converts encoder tick differences to linear distance moved by each wheel:
  $$\Delta d = \frac{\Delta \text{ticks}}{\text{CPR}} \times (2\pi r)$$
- **Lines 176–185:** Reads `v_bat` from the telemetry packet and publishes `sensor_msgs/msg/BatteryState` on `/battery_state` with voltage and percentage estimates.

#### Lines 193–200: Odometry Integration (Runge-Kutta / Midpoint)
```python
193:         d_center = (d_right + d_left) / 2.0
194:         d_theta = (d_right - d_left) / self.wheel_track
196:         self.x += d_center * math.cos(self.theta + d_theta / 2.0)
197:         self.y += d_center * math.sin(self.theta + d_theta / 2.0)
198:         self.theta += d_theta
200:         self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))
```
- Midpoint integration formula:
  $$\Delta x = \Delta d \cos\left(\theta + \frac{\Delta\theta}{2}\right), \quad \Delta y = \Delta d \sin\left(\theta + \frac{\Delta\theta}{2}\right)$$
  Using the average heading during interval $dt$ provides significantly lower integration error than Euler integration ($\Delta x = \Delta d \cos\theta$).

#### Lines 206–243: TF & Odometry Publishing
```python
207:         qz = math.sin(self.theta / 2.0)
208:         qw = math.cos(self.theta / 2.0)
211:         if self.publish_tf:
218:             t.transform.rotation.z = qz
219:             t.transform.rotation.w = qw
220:             self.tf_broadcaster.sendTransform(t)
```
- Converts 2D heading $\theta$ to quaternion $\begin{bmatrix}0 & 0 & \sin(\theta/2) & \cos(\theta/2)\end{bmatrix}^T$ and broadcasts transform `odom -> base_footprint`.
- Publishes `nav_msgs/msg/Odometry` on `/odom` with pose, twist, and covariance estimates.

---

## File 3: `esp32_firmware/src/main.cpp`

### 3.1 Purpose and Architectural Role
Firmware executing on the ESP32 microcontroller. Provides hard real-time motor control via an L298N H-bridge driver, optical encoder interrupt service routines, battery ADC sampling, and fail-safe watchdog timeouts.

### 3.2 Line-by-Line Breakdown

#### Lines 18–32: GPIO Assignments
```cpp
19: #define MOTOR_LEFT_PWM      18  // ENA
20: #define MOTOR_LEFT_DIR1     19  // IN1
21: #define MOTOR_LEFT_DIR2     21  // IN2
24: #define MOTOR_RIGHT_PWM     22  // ENB
25: #define MOTOR_RIGHT_DIR1    23  // IN3
26: #define MOTOR_RIGHT_DIR2    5   // IN4
29: #define ENCODER_LEFT_A      34  // Left Phase A
30: #define ENCODER_LEFT_B      35  // Left Phase B
```
- Direct pin mapping to L298N driver inputs and optical encoder sensors. ESP32 pins 34, 35, 32, 33 are input-capable GPIOs.

#### Lines 37–42: LEDC PWM Configuration
```cpp
38: #define PWM_FREQ            20000 // 20 kHz
39: #define PWM_RESOLUTION      8     // 8-bit (0-255)
40: #define PWM_CHANNEL_LEFT    0
41: #define PWM_CHANNEL_RIGHT   1
```
- Uses ESP32's hardware LEDC PWM timer. Setting PWM frequency to $20\,\text{kHz}$ pushes switching above human hearing range ($20\,\text{Hz} - 20\,\text{kHz}$), eliminating motor whining sounds common at 1 kHz default PWM.

#### Lines 60–77: Interrupt Service Routines (ISRs)
```cpp
60: void IRAM_ATTR left_encoder_isr() {
61:   int b_state = digitalRead(ENCODER_LEFT_B);
62:   if (b_state > 0) {
63:     left_encoder_ticks++;
64:   } else {
65:     left_encoder_ticks--;
66:   }
67: }
```
- **`IRAM_ATTR`:** Placed in ESP32 Internal RAM (IRAM) rather than Flash cache. Guarantees near-instant execution (<1 microsecond) without cache misses.
- **Quadrature decoding:** When Phase A triggers a `RISING` edge interrupt, Phase B's state reveals rotation direction: Phase B high = forward rotation (++), Phase B low = reverse rotation (--).

#### Lines 79–111: Direction Logic & PWM Scaling
```cpp
80: void set_motor_speeds(float v_left, float v_right) {
85:   int pwm_left = constrain((int)(fabs(v_left) / MAX_WHEEL_SPEED * 255.0), 0, 255);
88:   if (v_left > 0.005) {
89:     digitalWrite(MOTOR_LEFT_DIR1, HIGH);
90:     digitalWrite(MOTOR_LEFT_DIR2, LOW);
91:   } else if (v_left < -0.005) {
92:     digitalWrite(MOTOR_LEFT_DIR1, LOW);
93:     digitalWrite(MOTOR_LEFT_DIR2, HIGH);
94:   } else {
95:     digitalWrite(MOTOR_LEFT_DIR1, LOW);
96:     digitalWrite(MOTOR_LEFT_DIR2, LOW);
97:   }
98:   ledcWrite(PWM_CHANNEL_LEFT, pwm_left);
```
- Converts continuous speed command ($0.0$ to $0.5\,\text{m/s}$) to 8-bit duty cycle ($0$ to $255$).
- Implements H-bridge truth table:
  - Forward: `DIR1 = HIGH`, `DIR2 = LOW`.
  - Reverse: `DIR1 = LOW`, `DIR2 = HIGH`.
  - Stop/Brake: `DIR1 = LOW`, `DIR2 = LOW`.

#### Lines 113–128: JSON Command Parsing & Watchdog Refresh
```cpp
114: void parse_serial_command() {
118:     StaticJsonDocument<200> doc;
119:     DeserializationError error = deserializeJson(doc, json_line);
121:       const char* cmd = doc["cmd"];
122:       if (cmd && strcmp(cmd, "vel") == 0) {
123:         target_v_left = doc["v_l"];
124:         target_v_right = doc["v_r"];
125:         last_cmd_time = millis(); // Refresh watchdog
126:       }
```
- Parses JSON using `ArduinoJson` library. Refreshes `last_cmd_time` on every valid packet.

#### Lines 168–187: Main Loop Watchdog & 20Hz Telemetry
```cpp
173:   if (millis() - last_cmd_time > CMD_TIMEOUT_MS) {
174:     target_v_left = 0.0;
175:     target_v_right = 0.0;
176:   }
179:   if (millis() - last_telemetry_time >= TELEMETRY_INTERVAL_MS) {
184:     StaticJsonDocument<150> doc;
185:     doc["enc_l"] = left_encoder_ticks;
186:     doc["enc_r"] = right_encoder_ticks;
187:     doc["v_bat"] = round(battery_voltage * 10.0) / 10.0;
188:     serializeJson(doc, Serial);
189:     Serial.println();
```
- Hardware safety: If the Raspberry Pi reboots, crashes, or cable disconnects, motors shut off after 500 ms.
- Telemetry: Emits encoder counts and battery voltage every 50 ms (20 Hz).

---

## File 4: `robot_ws/src/robot_perception/robot_perception/person_detector_node.py`

### 4.1 Purpose and Architectural Role
Subscribes to `/camera/image_raw`, executes an optimized OpenCV Histogram of Oriented Gradients (HOG) + Linear SVM detector, estimates human distance and bearing, and publishes detection flags and annotated frames.

### 4.2 Line-by-Line Breakdown
- **Lines 41–45:** `self.hog = cv2.HOGDescriptor(); self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())`. Initializes the pre-trained linear SVM classifier provided by OpenCV.
- **Lines 63–70:** Downsamples large frames to 640px width before inference. Running HOG on 1080p would bog down the RPi 5 CPU; 640px ensures 15–20 FPS throughput.
- **Lines 73–80:** `boxes, weights = self.hog.detectMultiScale(...)` scans the image pyramid with window stride of 8 pixels and scale factor of 1.05.
- **Lines 98–110:** Distance and bearing geometry:
  $$\text{Bearing} = \frac{x_{\text{center}} - (w_{\text{frame}} / 2)}{w_{\text{frame}} / 2} \in [-1.0, 1.0]$$
  $$\text{Distance} \approx \frac{H_{\text{human}} \cdot f_{\text{camera}}}{h_{\text{bbox\_pixels}}} \approx \frac{1.7 \cdot (0.8 \cdot w)}{h_{\text{pixels}}}$$
- **Lines 118–137:** Publishes `/perception/person_detected` (Bool), `/perception/person_count` (Int32), `/perception/detections` (JSON), and `/perception/image_annotated` (Image).

---

## File 5: `robot_ws/src/robot_perception/robot_perception/webcam_publisher_node.py`

### 5.1 Purpose and Architectural Role
Provides an immediate physical video driver for testing with USB webcams on Ubuntu (`/dev/video0`) or Windows index 0, publishing standard ROS 2 `Image` and `CameraInfo` topics.

### 5.2 Line-by-Line Breakdown
- **Lines 35–43:** Declares parameters `device_id` (default 0), `frame_width` (640), `frame_height` (480), `fps` (30.0), `frame_id` (`camera_optical_link`).
- **Lines 50–58:** Opens camera device using `cv2.VideoCapture(self.device_id)` and configures camera hardware resolution and framerate properties.
- **Lines 61–80:** `capture_loop` timer captures frames, converts BGR OpenCV numpy arrays to `sensor_msgs/msg/Image` using `CvBridge().cv2_to_imgmsg(frame, encoding='bgr8')`, stamps with current clock time, and publishes on `/camera/image_raw`.

---

## File 6: `robot_ws/src/robot_voice/robot_voice/voice_node.py`

### 6.1 Purpose and Architectural Role
Provides offline text-to-speech companion feedback. Implements a thread-safe Queue and dedicated daemon worker thread to prevent speech synthesis calls (`pyttsx3.runAndWait()`) from blocking the main ROS 2 callback executor thread.

### 6.2 Line-by-Line Breakdown
- **Lines 43–46:** Initializes `self.speech_queue = queue.Queue()` and spawns `self.worker_thread = threading.Thread(target=self._tts_worker, daemon=True)`.
- **Lines 51–76:** Worker thread executes `engine.say(text); engine.runAndWait()` inside a loop pulling items from the queue.
- **Lines 78–86:** `speak_callback` places incoming `/voice/speak` text into the queue and returns immediately (<0.1 ms).
- **Viva Note:** If `runAndWait()` were called directly inside `speak_callback`, the node would be unresponsive to all other topics, timer ticks, and pings for 3–5 seconds while speaking!

---

## File 7: `robot_ws/src/robot_health/robot_health/reminder_manager_node.py`

### 7.1 Purpose and Architectural Role
Manages healthcare routines. Operates periodic timers to remind patients to take medication, listens for voice confirmations, and escalates to emergency alerts if unacknowledged after 30 seconds.

### 7.2 Line-by-Line Breakdown
- **Lines 44–58:** Declares Trigger services `/health/trigger_reminder` and `/health/acknowledge_reminder`.
- **Lines 64–77:** Periodic timer (default 60s) triggers reminder alarm, logs event, and requests voice prompt: "Hello! I am LUMI. It is time for your scheduled medicine."
- **Lines 79–96:** 1 Hz `check_escalation` timer evaluates elapsed time:
  $$\text{elapsed} = t_{\text{current}} - t_{\text{reminder\_start}}$$
  If $\text{elapsed} \ge \text{escalation\_timeout}$ ($30\,\text{s}$), it fires an emergency warning on `/health/emergency_alert` and triggers caregiver voice alert.
- **Lines 98–110:** `acknowledge_reminder` clears active alarm upon hearing voice keywords ("medicine", "taken", "yes", "confirm") or via service call.

---

## File 8: `robot_ws/src/robot_behaviour/robot_behaviour/behaviour_manager_node.py`

### 8.1 Purpose and Architectural Role
The high-level companion supervisor. Implements a 5-State Finite State Machine (`IDLE`, `NAVIGATING`, `INTERACTING`, `REMINDER`, `EMERGENCY`). Coordinates behavioral responses and commands immediate safe stops in emergency conditions.

### 8.2 Line-by-Line Breakdown
- **Lines 19–25:** `RobotState` Enum definition.
- **Lines 69–80:** `set_state(new_state, reason)` transitions states with structured logging. When entering `EMERGENCY`, it immediately triggers `self._stop_robot()`.
- **Lines 82–84:** `_stop_robot()` publishes a `Twist` message with all linear and angular velocities set to zero.
- **Lines 86–95:** `person_detected_callback`: If `IDLE` and person detected, transition to `INTERACTING` and speak greeting. If person leaves view, revert to `IDLE`.
- **Lines 102–104:** `emergency_callback`: Escalation alert immediately forces state to `EMERGENCY`.
- **Lines 106–118:** Voice keywords "stop" or "halt" trigger safe stop; "reset" or "clear" resets state back to `IDLE`.

---

## File 9: `robot_ws/src/robot_simulation/launch/gazebo_sim.launch.py`

### 9.1 Purpose and Architectural Role
Launch file that initializes the simulation environment: starts Gazebo Classic 11 server and client, evaluates Xacro robot description, and spawns the robot entity into `healthcare_room.world`.

### 9.2 Line-by-Line Breakdown
- **Lines 30–33:** `robot_description = ParameterValue(Command(['xacro ', xacro_file_path]), value_type=str)` processes the Xacro file into raw URDF string substitution.
- **Lines 36–41:** Launches `gzserver` running physics engine on `healthcare_room.world`.
- **Lines 44–48:** Launches `gzclient` GUI conditionally based on `gui` launch argument (allows headless simulation over SSH).
- **Lines 51–57:** Runs `robot_state_publisher` passing `robot_description` parameter.
- **Lines 60–72:** Spawns the robot using `gazebo_ros/spawn_entity.py` at origin with $Z = 0.05\,\text{m}$ to ensure it drops cleanly onto wheels.

---

## Files 10, 11 & 12: Navigation & Bringup Launch Files

### 10.1 `robot_navigation/launch/slam.launch.py` & `navigation.launch.py`
- `slam.launch.py` runs `async_slam_toolbox_node` with parameters from `config/slam_toolbox_params.yaml` and `use_sim_time`.
- `navigation.launch.py` includes `nav2_bringup/launch/bringup_launch.py` with map path, `nav2_params.yaml`, and `autostart:=true`.

### 10.2 `robot_bringup/launch/bringup_full_system.launch.py`
- Master system launcher with single argument `use_sim`:
  - `use_sim:=true`: Launches Gazebo simulation stack.
  - `use_sim:=false`: Launches `robot_state_publisher` and `serial_bridge_node` connecting to real ESP32 hardware.
- Spawns SLAM, Nav2, Perception, Voice, Health, and Behaviour nodes in a unified terminal tree.

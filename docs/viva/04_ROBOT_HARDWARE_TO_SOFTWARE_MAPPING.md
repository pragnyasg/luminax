# 04 — LUMI Physical Hardware to ROS 2 Software Mapping Guide

```
========================================================================================
Project: LUMI — AI Autonomous Healthcare Companion Robot
Target Environment: Ubuntu 22.04 LTS | ROS 2 Humble Hawksbill
Standard: Complete end-to-end trace from physical pins and sensors to ROS 2 nodes.
========================================================================================
```

---

## 1. End-to-End Component Interface Mapping Table

| Physical Hardware Component | Electrical / Interface Connection | Low-Level Driver / Bridge | ROS 2 Interface / Topic | Consuming ROS 2 Node | Resulting System Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Raspberry Pi 5 (8GB)** | USB 3.0 / GPIO / Power Hat | Ubuntu 22.04 aarch64 OS | ROS 2 Humble Graph | All Nodes (`robot_ws`) | Master computational host executing SLAM, Nav2, Vision, FSM. |
| **ESP32-WROOM-32** | Micro-USB to RPi 5 USB Port | USB CDC Serial (115200 Baud) | `/cmd_vel` & `/odom` | `serial_bridge_node` | Real-time PWM generator (20 kHz) and encoder interrupt accumulator. |
| **L298N Dual H-Bridge Driver** | ESP32 GPIOs 18, 19, 21, 22, 23, 5 | `ledcWrite()` & `digitalWrite()` | `{"cmd":"vel","v_l":...,"v_r":...}` | ESP32 Firmware | Amplifies 3.3V logic to 12V DC motor power to drive left/right wheels. |
| **Two 12V Geared DC Motors** | L298N OUT1/OUT2 & OUT3/OUT4 | Differential Drive Chassis | Forward Kinematics | Real World Motion | Differential-drive propulsion with $0.04\,\text{m}$ radius wheels. |
| **Optical Wheel Encoders** | GPIO 34, 35 (Left), 32, 33 (Right) | `IRAM_ATTR` ISR Interrupts | `{"enc_l":...,"enc_r":...}` | `serial_bridge_node` | Measures wheel rotations (334 CPR); integrated into odometry $(x, y, \theta)$. |
| **2D Planar LiDAR (RPLiDAR A1)** | USB to Raspberry Pi 5 | `rplidar_ros` / Gazebo Ray Plugin | `/scan` (`sensor_msgs/LaserScan`) | `slam_toolbox`, `Nav2 costmaps` | 360-degree obstacle detection and metric room map generation. |
| **USB RGB Webcam** | USB to Raspberry Pi 5 | `webcam_publisher_node` / OpenCV | `/camera/image_raw` (`sensor_msgs/Image`)| `person_detector_node` | Video frame acquisition for human detection and distance estimation. |
| **12V Li-ion Battery Sensing** | 4:1 Voltage Divider to ESP32 Pin 36 (VP) | `analogRead()` (12-bit ADC) | `/battery_state` (`sensor_msgs/BatteryState`)| FSM / Companion Status | Real-time battery voltage monitoring and low-voltage warning. |
| **USB Speaker** | 3.5mm Jack / USB Audio to RPi 5 | ALSA / PulseAudio / `pyttsx3` | `/voice/speak` (`std_msgs/String`) | `voice_node` | Audible verbal announcements for medicine reminders and greetings. |
| **USB Microphone** | USB Audio to RPi 5 | PyAudio / SpeechRecognition | `/voice/command` (`std_msgs/String`) | `reminder_manager_node` | Voice keyword recognition for medicine confirmation and stop commands. |

---

## 2. Microcontroller Hardware Architecture & Pinout Contract

```text
                             +------------------------+
                             |    ESP32-WROOM-32      |
                             +------------------------+
                               |                    |
            [LEFT MOTOR PINS]  |                    |  [RIGHT MOTOR PINS]
            GPIO 18 --------> ENA (PWM 20kHz)       |  GPIO 22 --------> ENB (PWM 20kHz)
            GPIO 19 --------> IN1 (Direction)       |  GPIO 23 --------> IN3 (Direction)
            GPIO 21 --------> IN2 (Direction)       |  GPIO 5  --------> IN4 (Direction)
                               |                    |
            [LEFT ENCODER]     |                    |  [RIGHT ENCODER]
            GPIO 34 <-------- Phase A (Interrupt)   |  GPIO 32 <-------- Phase A (Interrupt)
            GPIO 35 <-------- Phase B (Direction)   |  GPIO 33 <-------- Phase B (Direction)
                               |                    |
            [ANALOG SENSING]   |                    |  [COMMUNICATION]
            GPIO 36 (VP) <--- 4:1 Battery Divider   |  USB UART <------> Raspberry Pi 5
                             +------------------------+
```

### 2.1 Motor Driver Electrical Interface (L298N)
The L298N contains a dual high-power full-bridge driver designed to drive inductive loads such as relays, solenoids, DC and stepping motors.
- **Power Rails:**
  - `VMS` (Motor Power): Connected to positive terminal of 12V Li-ion battery pack.
  - `VSS` (Logic Power): Regulated 5V input from buck converter.
  - `GND`: Common ground bonded between 12V battery, ESP32 ground, and RPi 5 ground.
- **Control Truth Table:**
  | IN1 | IN2 | ENA (PWM) | Left Motor State |
  | :--- | :--- | :--- | :--- |
  | `HIGH` | `LOW` | $> 0$ | Forward rotation |
  | `LOW` | `HIGH` | $> 0$ | Reverse rotation |
  | `LOW` | `LOW` | Any | Passive Coasting |
  | `HIGH` | `HIGH` | Any | Active Braking |

---

## 3. Sensor Data Flow & Abstraction Layers

### 3.1 Odometry Pipeline: From Encoder Discs to TF2
1. **Physical Ticks:** Optical encoder slotted disc rotates with wheel. Sensor phototransistor emits pulses on Phase A and Phase B.
2. **Interrupt Accumulation:** ESP32 `left_encoder_isr` increments/decrements `left_encoder_ticks` in under 1 microsecond.
3. **Telemetry Packet:** Every 50 ms (20 Hz), ESP32 packages ticks into JSON string:
   `{"enc_l": 240, "enc_r": 240, "v_bat": 12.2}`
4. **Distance Conversion:** In `serial_bridge_node.py`, the tick change $\Delta\text{ticks}$ is converted to wheel distance:
   $$\Delta d = \frac{\Delta\text{ticks}}{334} \times (2\pi \times 0.04)$$
5. **Kinematic Integration:** Linear displacement $\Delta d$ and angular heading change $\Delta\theta$ update global $(x, y, \theta)$.
6. **Transform Broadcast:** Broadcaster sends `odom -> base_footprint` transform stamped with ROS clock time.

### 3.2 LiDAR Pipeline: From Laser Pulses to Costmap Obstacles
1. **Infrared Laser Scan:** 2D LiDAR rotates at 10 Hz (600 RPM), sampling 720 distance points across 360 degrees.
2. **ROS Driver:** Emits `sensor_msgs/msg/LaserScan` stamped in `lidar_link` frame.
3. **TF Transformation:** Nav2's `costmap_2d::ObstacleLayer` uses TF2 to project range measurements from `lidar_link` into `odom` and `map` coordinates.
4. **Raytracing & Clearing:** Clear rays mark grid cells as free space (cost = 0); return endpoints mark obstacles (cost = 254).
5. **Inflation Layer:** Dilates obstacles with Gaussian cost drop-off ($r_{\text{inflat}} = 0.40\,\text{m}$) so DWB local planner maintains safe clearance around walls.

---

## 4. Honest Audit: Hardware Availability & Verification Status

| Subsystem Component | Physical Wiring Status | Software Driver Status | Verification Level |
| :--- | :--- | :--- | :--- |
| **Raspberry Pi 5 Host** | Specified in Hardware Target | Linux Ubuntu 22.04 LTS | Tested via Python & ROS test suites |
| **ESP32 Microcontroller** | Specified (ESP32-WROOM-32) | Authored & syntax-audited C++ | Tested via loopback and JSON parsing tests |
| **L298N Motor Driver** | Verified target specification | Firmware GPIO mapped | Verified pinout logic; unverified under physical load |
| **Drive Motors & Encoders** | 12V Geared DC + 334 CPR Encoders| Authored kinematics & ISRs | Kinematic math verified (100% pass) |
| **2D LiDAR** | Planned (RPLiDAR A1) | Full Gazebo model & Nav2 config | Simulated in Gazebo Classic 11 |
| **USB RGB Webcam** | Available (tested previously) | `person_detector_node` + `webcam_node` | Verified with OpenCV HOG detector |
| **Battery Voltage Divider**| Planned (Pin 36 ADC) | Firmware ADC read + BatteryState topic| Code verified; needs resistor divider calibration |
| **USB Speaker / Mic** | Standard USB Audio | `voice_node` + background Queue | Code verified with pyttsx3 fallback |
| **Robotic Arm / Manipulator**| **EXPLICITLY EXCLUDED** | **NOT IMPLEMENTED BY DESIGN** | Not applicable (Mobile Companion Base Only) |

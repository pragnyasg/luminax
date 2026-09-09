# Hardware Architecture

## 1. Physical Hardware Overview

The Baymax Healthcare Robot utilizes a dual-processor architecture: a **Raspberry Pi 5** for high-level ROS 2 computation and an **ESP32** for real-time low-level motor execution.

```text
                               +-----------------------------+
                               |  BAYMAX COMPANION ROBOT     |
                               +-----------------------------+
                                              |
                    +-------------------------+-------------------------+
                    |                                                   |
                    v                                                   v
     +------------------------------+                  +------------------------------+
     |      Raspberry Pi 5          |                  |           ESP32              |
     |  (High-Level ROS 2 Controller|                  |  (Low-Level Hardware Exec)   |
     +------------------------------+                  +------------------------------+
                    |                                                   |
       +------------+------------+                         +------------+------------+
       |            |            |                         |            |            |
       v            v            v                         v            v            v
    ROS 2        2D LiDAR      Camera                 Motor Driver    Encoders    Battery Mon.
   (Humble)     (/scan)   (/camera/image_raw)              |            |            |
       |                                                   v            v            v
 +-----+-----+                                         DC Motors    Wheel Speed   Voltage
 |     |     |                                         (Left/Right)  Odometry       Sense
 v     v     v
SLAM  Nav2   AI / Perception
```

---

## 2. Component Breakdown

### A. Main Computer: Raspberry Pi 5 (8GB)
- **OS**: Ubuntu 22.04 LTS (64-bit ARM)
- **Framework**: ROS 2 Humble Hawksbill
- **Responsibilities**:
  - Running ROS 2 node architecture
  - SLAM mapping and Nav2 autonomous path planning
  - Camera acquisition & lightweight vision AI
  - High-level companion state machine
  - USB Serial communications with ESP32 and LiDAR

### B. Microcontroller: ESP32-WROOM-32
- **Environment**: Arduino framework / ESP-IDF C++
- **Responsibilities**:
  - Generating high-frequency hardware PWM signals for motor driver
  - Reading quadrature optical encoders via hardware GPIO interrupts
  - Reading battery voltage via Analog-to-Digital Converter (ADC)
  - Processing JSON serial command packets from Raspberry Pi 5 (`v_left`, `v_right`)

### C. Mobile Base & Actuation
- **Motors**: 2 x Geared DC Motors (12V with 1:30 or 1:45 gear ratio)
- **Motor Driver**: L298N or TB6612FNG Dual H-Bridge Motor Driver
- **Encoders**: 2 x Optical / Hall-effect wheel encoders (e.g., 334 or 1100 pulses per wheel turn)
- **Wheels**: 2 x Main rubber wheels (Radius $R \approx 0.035 \text{ m}$) + 1 x Rear omni-directional caster ball

### D. Sensor Suite
- **2D LiDAR**: 360-degree laser range scanner (e.g., RPLiDAR A1M8 or YDLIDAR X4) connected via USB to RPi 5.
- **Camera**: USB Web Camera or RPi Camera Module v3 ($720\text{p} / 1080\text{p}$).
- **Power**: 12V LiFePO4 or Li-ion rechargeable battery pack with 5V 5A step-down buck converter for RPi 5 and ESP32.

---

## 3. Communication Protocol (Pi 5 <-> ESP32)

Communication takes place over standard **USB Serial (`/dev/ttyUSB0` or `/dev/ttyACM0`)** at 115200 baud.

### Command Packet (Pi 5 -> ESP32)
```json
{"cmd": "vel", "v_l": 0.25, "v_r": 0.25}
```

### Telemetry Packet (ESP32 -> Pi 5)
```json
{"enc_l": 1420, "enc_r": 1435, "v_bat": 12.2}
```

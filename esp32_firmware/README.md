# ESP32 Microcontroller Firmware (Implemented - Phase 5)

## 1. Firmware Overview
The `esp32_firmware/` directory contains the **ESP32 C++ Firmware** for the low-level motor control, optical wheel encoder pulse counting, battery voltage sensing, and serial communications for the Baymax Healthcare Robot.

---

## 2. Directory Structure

```text
esp32_firmware/
├── platformio.ini                    # PlatformIO build & dependency config
├── src/
│   └── main.cpp                      # ESP32 C++ firmware main logic
└── README.md                         # Documentation (this file)
```

---

## 3. Microcontroller Pinout & Wiring

| ESP32 Pin | Function | Connected Component |
| :--- | :--- | :--- |
| **GPIO 18** | PWM Left Speed (`ENA`) | Motor Driver ENA |
| **GPIO 19** | Direction Left 1 (`IN1`) | Motor Driver IN1 |
| **GPIO 21** | Direction Left 2 (`IN2`) | Motor Driver IN2 |
| **GPIO 22** | PWM Right Speed (`ENB`) | Motor Driver ENB |
| **GPIO 23** | Direction Right 1 (`IN3`) | Motor Driver IN3 |
| **GPIO 5** | Direction Right 2 (`IN4`) | Motor Driver IN4 |
| **GPIO 34** | Left Encoder Phase A | Left Optical Encoder Channel A |
| **GPIO 35** | Left Encoder Phase B | Left Optical Encoder Channel B |
| **GPIO 32** | Right Encoder Phase A | Right Optical Encoder Channel A |
| **GPIO 33** | Right Encoder Phase B | Right Optical Encoder Channel B |
| **GPIO 36** | Battery ADC Sense | Voltage Divider (12V Battery Pack) |

---

## 4. How to Flash Firmware

Using **PlatformIO** (VS Code extension or CLI):
```bash
cd baymax_healthcare_robot/esp32_firmware
pio run --target upload
```

Or using **Arduino IDE**:
1. Open `src/main.cpp`.
2. Install `ArduinoJson` library via Library Manager.
3. Select Board: `ESP32 Dev Module`.
4. Upload to ESP32 over USB Serial.

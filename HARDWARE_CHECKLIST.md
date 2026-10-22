# LUMI Hardware Integration Checklist (Raspberry Pi 5 & ESP32)

This checklist provides the exact physical setup, port mappings, and testing commands to bring up the physical LUMI Healthcare Robot with the Caregiver Mobile Application.

---

## 1. Hardware Bill of Materials & Port Assignments

| Component | Physical Connection | Device File on Pi 5 | Verified ROS 2 Node | Test Verification Command |
| :--- | :--- | :--- | :--- | :--- |
| **Raspberry Pi 5** | Main SBC (8GB RAM) | Host SBC | Master ROS 2 Orchestrator | `uname -m && lsb_release -a` |
| **USB Webcam** | USB 3.0 Port | `/dev/video0` | `lumi_vision_node` / `v4l2_camera` | `v4l2-ctl --list-devices` |
| **USB Microphone** | USB 2.0 Port | ALSA card (hw:1,0) | `voice_node` (Silero VAD + Whisper) | `arecord -l` |
| **USB Speaker** | USB 2.0 / 3.5mm Audio | ALSA card (hw:1,0) | `voice_node` (Piper TTS) | `aplay -l` |
| **ESP32 Motor Bridge** | USB 3.0 Port (CP2102/CH340) | `/dev/ttyUSB0` | `serial_bridge_node` | `ls -la /dev/ttyUSB0` |
| **RPLiDAR A1/A2** | USB 2.0 Port | `/dev/ttyUSB1` | `sllidar_node` / `rplidar_node` | `ros2 topic echo /scan --once` |
| **LiPo Battery Pack** | 3S 11.1V (12.6V peak) | ESP32 ADC pin GPIO34 | `serial_bridge_node` (/battery_state)| `ros2 topic echo /battery_state --once`|

---

## 2. Step-by-Step Setup Instructions on Raspberry Pi 5

### Step 1: User Group Permissions (USB Serial, Audio, Camera)
Ensure the `ubuntu` user has access to serial devices, camera, and audio hardware:
```bash
sudo usermod -a -G dialout,video,audio $USER
```
*Note: Log out and back in for group changes to take effect.*

### Step 2: Persistent udev Rules for ESP32 and LiDAR
To avoid `/dev/ttyUSB0` and `/dev/ttyUSB1` swapping on reboot, create persistent symlinks:
```bash
sudo tee /etc/udev/rules.d/99-lumi-hardware.rules << 'EOF'
# ESP32 Motor Controller (CP2102 or CH340)
KERNEL=="ttyUSB*", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", SYMLINK+="lumi_esp32"

# RPLiDAR A1/A2 (Silicon Labs / FTDI)
KERNEL=="ttyUSB*", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", SYMLINK+="lumi_lidar"
EOF

sudo udevadm control --reload-rules && sudo udevadm trigger
```

### Step 3: Clone, Build & Source ROS 2 Workspace
```bash
git clone https://github.com/pragnyasg/luminax.git ~/luminax
cd ~/luminax/robot_ws

source /opt/ros/$ROS_DISTRO/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

### Step 4: Verify Python & Audio/Vision Packages
```bash
pip install --break-system-packages \
    fastapi \
    uvicorn \
    websockets \
    pydantic \
    pydantic-settings \
    mediapipe \
    faster-whisper \
    sounddevice \
    soundfile \
    pyttsx3
```

### Step 5: Test ESP32 Serial Communication
Verify encoder ticks and battery telemetry stream over serial:
```bash
python3 -c "
import serial, time
s = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)
s.write(b'{\"cmd\":\"vel\",\"v_l\":0.0,\"v_r\":0.0}\n')
for _ in range(5):
    print('ESP32 telemetry:', s.readline().decode().strip())
s.close()
"
```

---

## 3. Starting the Integrated System

### Terminal 1: Launch Full Hardware ROS 2 Stack
```bash
cd ~/luminax/robot_ws
source install/setup.bash

# Launches physical camera, LiDAR, ESP32 base, Nav2, Vision Pipeline, and Voice Assistant
ros2 launch robot_bringup bringup_full_system.launch.py \
    use_sim:=false \
    use_vision:=true \
    use_voice:=true \
    use_nav2:=true
```

### Terminal 2: Launch Caregiver Integration Backend Server
```bash
cd ~/luminax
source ~/luminax/robot_ws/install/setup.bash

# Runs FastAPI and WebSockets on port 8000 connected to live ROS 2
python3 -m lumi_backend.run_server --host 0.0.0.0 --port 8000 --ros
```

### Terminal 3: Mobile Phone Connection
1. Note the Pi 5 IP address (`hostname -I`).
2. Open **LUMI Caregiver** on the smartphone.
3. In **Settings**, enter `http://<pi-ip>:8000` and tap **Save & Apply**.
4. Both camera video, fall detection alarms, and teleoperation are now fully live and controlling physical hardware!

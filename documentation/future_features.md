# Future Features & Advanced Module Blueprints

This document serves as an architectural blueprint for future advanced capabilities planned for later development phases.

> [!NOTE]
> None of the complex AI or voice modules listed here should be allowed to delay the primary objective: **Reliable Autonomous Indoor Navigation**.

---

## 1. Person Detection Pipeline (`robot_perception`)

- **Objective**: Detect humans in camera view to allow the robot to approach a patient.
- **Model Choice**: Pretrained MobileNet-SSD v2 or YOLOv8-nano (ONNX / OpenCV dnn module).
- **Input**: `/camera/image_raw` (`sensor_msgs/msg/Image`)
- **Output**: `/perception/person_detected` (`std_msgs/msg/Bool`), bounding box coordinates.
- **Why Pretrained?**: Training neural networks from scratch is unnecessary and counter-productive for university project timelines.

---

## 2. Healthcare Reminder System (`robot_health`)

- **Objective**: Provide scheduled medicine alerts.
- **Architecture**:
  - Simple Python `cron` or ROS 2 timer event checking system time against scheduled alarm list.
  - Triggers state change in `robot_behaviour` node.
  - Robot moves to target home/patient waypoint using Nav2 goal action client.
  - Speaks audio alert: *"Time for your evening medicine."*

---

## 3. Voice Interaction Pipeline (`robot_voice`)

- **Objective**: Allow basic spoken interactions.
- **Text-to-Speech (TTS)**: Offline `pyttsx3` or `espeak-ng`.
- **Speech-to-Text (STT)**: Offline `Vosk` lightweight keyword spotter.
- **Supported Key Commands**:
  - *"Stop"* -> Emergency navigation halt.
  - *"Hello"* -> Audio greeting response.
  - *"Medicine"* -> Acknowledge medicine taken.

---

## 4. Behavior Manager Finite State Machine (`robot_behaviour`)

- **Objective**: Coordinates robot behaviors without complicated behavior trees.
- **States**:
  1. `IDLE`: Resting at home station, monitoring battery.
  2. `NAVIGATING`: Executing Nav2 waypoint path.
  3. `INTERACTING`: Playing medicine reminder or talking to user.
  4. `REMINDER`: Waiting for patient confirmation.
  5. `EMERGENCY`: Escalating unacknowledged alert.

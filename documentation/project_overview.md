# Project Overview: Baymax-Inspired Autonomous Healthcare Companion Robot

## 1. Project Vision
The **Baymax Healthcare Robot** is a university educational robotics project designed to explore modern autonomous mobile robotics principles using **ROS 2 Humble** and **Ubuntu 22.04 LTS**.

Inspired by the companion spirit of Baymax, the robot acts as an indoor mobile assistant capable of navigating domestic or clinical environments, providing medicine reminders, interacting via voice, and monitoring safety.

---

## 2. Critical Design Decisions

### A. Autonomous Mobile Robot (AMR) - NO ARMS
> [!IMPORTANT]
> **This robot has NO ARMS, hands, or grasping mechanisms.**
> University student teams often fail when trying to build both complex mobility and complex manipulation simultaneously. By eliminating robotic arms:
> - Mechanical complexity is dramatically reduced.
> - Inverse kinematics (IK) and MoveIt overhead are eliminated.
> - The team can focus 100% of engineering effort on reliable indoor navigation (SLAM, Nav2, obstacle avoidance).

### B. Differential Drive Kinematics
The mobile base uses a two-wheel differential drive setup with a rear balancing caster wheel:
- **Linear Velocity ($v$)**: Speed moving forward or backward.
- **Angular Velocity ($\omega$)**: Rate of rotation around the z-axis.
- **Left Wheel Velocity ($v_L$)** & **Right Wheel Velocity ($v_R$)**:
  $$v_L = v - \frac{\omega \cdot W}{2}$$
  $$v_R = v + \frac{\omega \cdot W}{2}$$
  *(where $W$ is the track width between the left and right wheels)*

---

## 3. High-Level Core Capabilities

1. **Differential Drive Motion**: Smooth movement via `/cmd_vel` velocity commands.
2. **LiDAR Range Sensing**: 2D 360-degree planar scan line data (`/scan`).
3. **Wheel Odometry**: Real-time wheel rotation integration (`/odom`).
4. **SLAM Mapping**: Environment mapping using `slam_toolbox`.
5. **Nav2 Autonomous Navigation**: Waypoint goal navigation with global and local costmaps.
6. **Camera Perception**: RGB video stream for person detection (`/camera/image_raw`).
7. **Healthcare Interactions**: Scheduled audio/visual medicine reminders.
8. **Voice Commands**: Simple offline text-to-speech and keyword recognition.

---

## 4. Student Educational Goals

This project prepares students for academic evaluation and oral defense by teaching:
- How ROS 2 handles node communication via Pub/Sub, Services, and Actions.
- How kinematic models translate ROS 2 `/cmd_vel` commands to physical motor speeds.
- How coordinate frames (TF tree: `map` -> `odom` -> `base_footprint` -> `base_link`) maintain spatial awareness.
- How to isolate high-level decision logic (Raspberry Pi 5) from low-level real-time control (ESP32).

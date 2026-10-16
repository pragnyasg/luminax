/**
 * ESP32 Low-Level Motor Control & Encoder Telemetry Firmware
 * Project: LUMI — AI Healthcare Companion Robot
 *
 * Microcontroller: ESP32-WROOM-32
 * Motor Driver: L298N Dual H-Bridge
 * Encoders: Dual Channel Quadrature Optical Encoders (GPIO Interrupts)
 * Motors: Two 12V Geared DC Motors (Differential Drive)
 *
 * Serial Protocol: USB Serial at 115200 Baud (JSON Packets)
 * Command Input:  {"cmd":"vel", "v_l": 0.25, "v_r": 0.25}
 * Telemetry Out: {"enc_l": 1520, "enc_r": 1530, "v_bat": 12.1}
 *
 * Safety Watchdog: If no command received for >500ms, motors halt automatically.
 */

#include <Arduino.h>
#include <ArduinoJson.h>

// ==================== GPIO PIN DEFINITIONS ====================
// Left Motor Driver Pins (L298N)
#define MOTOR_LEFT_PWM      18  // ENA (PWM speed control)
#define MOTOR_LEFT_DIR1     19  // IN1
#define MOTOR_LEFT_DIR2     21  // IN2

// Right Motor Driver Pins (L298N)
#define MOTOR_RIGHT_PWM     22  // ENB (PWM speed control)
#define MOTOR_RIGHT_DIR1    23  // IN3
#define MOTOR_RIGHT_DIR2    5   // IN4

// Optical Wheel Encoder Pins (Interrupt Compatible GPIOs)
#define ENCODER_LEFT_A      34  // Left Encoder Phase A
#define ENCODER_LEFT_B      35  // Left Encoder Phase B
#define ENCODER_RIGHT_A     32  // Right Encoder Phase A
#define ENCODER_RIGHT_B     33  // Right Encoder Phase B

// Battery Voltage ADC Sensing Pin
#define BATTERY_ADC_PIN     36  // VP Pin (Analog input with voltage divider)

// PWM Channel Setup (ESP32 LEDC PWM Peripheral)
#define PWM_FREQ            20000 // 20 kHz ultrasonic frequency (no audible motor whine)
#define PWM_RESOLUTION      8     // 8-bit resolution (0 to 255)
#define PWM_CHANNEL_LEFT    0
#define PWM_CHANNEL_RIGHT   1

// Physical Robot Kinematic Constants
const float WHEEL_RADIUS = 0.04;  // 4 cm radius (8 cm diameter wheel)
const float WHEEL_TRACK  = 0.32;  // 32 cm track width between wheel contact points
const float ENCODER_CPR  = 334.0; // Counts per wheel revolution
const float MAX_WHEEL_SPEED = 0.5; // Max velocity in m/s corresponding to PWM 255

// Global Encoder Tick Counters (volatile for ISR safety)
volatile long left_encoder_ticks = 0;
volatile long right_encoder_ticks = 0;

// Target Wheel Velocities (m/s)
float target_v_left = 0.0;
float target_v_right = 0.0;

// Communication & Safety Watchdog Timers
unsigned long last_cmd_time = 0;
const unsigned long CMD_TIMEOUT_MS = 500; // Stop motors if serial drops for >500ms

unsigned long last_telemetry_time = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 50; // 20 Hz output

// ==================== ENCODER INTERRUPT HANDLERS ====================
void IRAM_ATTR left_encoder_isr() {
  int b_state = digitalRead(ENCODER_LEFT_B);
  if (b_state > 0) {
    left_encoder_ticks++;
  } else {
    left_encoder_ticks--;
  }
}

void IRAM_ATTR right_encoder_isr() {
  int b_state = digitalRead(ENCODER_RIGHT_B);
  if (b_state > 0) {
    right_encoder_ticks++;
  } else {
    right_encoder_ticks--;
  }
}

// ==================== MOTOR CONTROLLER FUNCTION ====================
void set_motor_speeds(float v_left, float v_right) {
  // Constrain requested velocities
  v_left = constrain(v_left, -MAX_WHEEL_SPEED, MAX_WHEEL_SPEED);
  v_right = constrain(v_right, -MAX_WHEEL_SPEED, MAX_WHEEL_SPEED);

  // Convert velocity (m/s) to 8-bit PWM duty cycle (0-255)
  int pwm_left = constrain((int)(fabs(v_left) / MAX_WHEEL_SPEED * 255.0), 0, 255);
  int pwm_right = constrain((int)(fabs(v_right) / MAX_WHEEL_SPEED * 255.0), 0, 255);

  // Left Motor Direction Control (L298N IN1/IN2 truth table)
  if (v_left > 0.005) {
    digitalWrite(MOTOR_LEFT_DIR1, HIGH);
    digitalWrite(MOTOR_LEFT_DIR2, LOW);
  } else if (v_left < -0.005) {
    digitalWrite(MOTOR_LEFT_DIR1, LOW);
    digitalWrite(MOTOR_LEFT_DIR2, HIGH);
  } else {
    digitalWrite(MOTOR_LEFT_DIR1, LOW);
    digitalWrite(MOTOR_LEFT_DIR2, LOW);
  }
  ledcWrite(PWM_CHANNEL_LEFT, pwm_left);

  // Right Motor Direction Control (L298N IN3/IN4 truth table)
  if (v_right > 0.005) {
    digitalWrite(MOTOR_RIGHT_DIR1, HIGH);
    digitalWrite(MOTOR_RIGHT_DIR2, LOW);
  } else if (v_right < -0.005) {
    digitalWrite(MOTOR_RIGHT_DIR1, LOW);
    digitalWrite(MOTOR_RIGHT_DIR2, HIGH);
  } else {
    digitalWrite(MOTOR_RIGHT_DIR1, LOW);
    digitalWrite(MOTOR_RIGHT_DIR2, LOW);
  }
  ledcWrite(PWM_CHANNEL_RIGHT, pwm_right);
}

// ==================== SERIAL COMMAND PARSER ====================
void parse_serial_command() {
  while (Serial.available() > 0) {
    String json_line = Serial.readStringUntil('\n');
    json_line.trim();
    if (json_line.length() == 0) continue;

    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, json_line);

    if (!error) {
      const char* cmd = doc["cmd"];
      if (cmd && strcmp(cmd, "vel") == 0) {
        target_v_left = doc["v_l"];
        target_v_right = doc["v_r"];
        last_cmd_time = millis(); // Refresh watchdog timer
      }
    }
  }
}

// ==================== BATTERY VOLTAGE MONITORING ====================
float read_battery_voltage() {
  int raw_adc = analogRead(BATTERY_ADC_PIN);
  // ADC range 0-4095 mapped to 0-3.3V with 4:1 voltage divider (for 12V Li-ion pack)
  float voltage = (raw_adc / 4095.0) * 3.3 * 4.0;
  return voltage;
}

// ==================== SETUP FUNCTION ====================
void setup() {
  Serial.begin(115200);

  // Motor Direction Pins
  pinMode(MOTOR_LEFT_DIR1, OUTPUT);
  pinMode(MOTOR_LEFT_DIR2, OUTPUT);
  pinMode(MOTOR_RIGHT_DIR1, OUTPUT);
  pinMode(MOTOR_RIGHT_DIR2, OUTPUT);

  // ESP32 PWM Setup (LEDC peripheral)
  ledcSetup(PWM_CHANNEL_LEFT, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(MOTOR_LEFT_PWM, PWM_CHANNEL_LEFT);

  ledcSetup(PWM_CHANNEL_RIGHT, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(MOTOR_RIGHT_PWM, PWM_CHANNEL_RIGHT);

  // Encoder Pins with internal pullups
  pinMode(ENCODER_LEFT_A, INPUT_PULLUP);
  pinMode(ENCODER_LEFT_B, INPUT_PULLUP);
  pinMode(ENCODER_RIGHT_A, INPUT_PULLUP);
  pinMode(ENCODER_RIGHT_B, INPUT_PULLUP);

  // Encoder Interrupt Attachments
  attachInterrupt(digitalPinToInterrupt(ENCODER_LEFT_A), left_encoder_isr, RISING);
  attachInterrupt(digitalPinToInterrupt(ENCODER_RIGHT_A), right_encoder_isr, RISING);

  // Initial safe state
  set_motor_speeds(0.0, 0.0);
  last_cmd_time = millis();
}

// ==================== MAIN LOOP ====================
void loop() {
  parse_serial_command();

  // Watchdog Safety: Halt motors if command stream has stalled
  if (millis() - last_cmd_time > CMD_TIMEOUT_MS) {
    target_v_left = 0.0;
    target_v_right = 0.0;
  }

  set_motor_speeds(target_v_left, target_v_right);

  // 20Hz Telemetry Publisher to Raspberry Pi 5
  if (millis() - last_telemetry_time >= TELEMETRY_INTERVAL_MS) {
    last_telemetry_time = millis();

    float battery_voltage = read_battery_voltage();

    StaticJsonDocument<150> doc;
    doc["enc_l"] = left_encoder_ticks;
    doc["enc_r"] = right_encoder_ticks;
    doc["v_bat"] = round(battery_voltage * 10.0) / 10.0;

    serializeJson(doc, Serial);
    Serial.println();
  }
}

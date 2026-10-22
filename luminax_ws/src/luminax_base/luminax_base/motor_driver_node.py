#!/usr/bin/env python3
# =====================================================================
#  LUMINAX motor_driver_node
#  Subscribes:  /cmd_vel  (geometry_msgs/Twist)
#  Drives   :   two DC motors through a motor driver wired to the
#               Raspberry Pi 5 GPIO header.
#
#  Odometry is NOT produced here -- rf2o_laser_odometry provides odom.
#  This node is OPEN-LOOP: it maps a commanded wheel speed to a PWM duty
#  cycle using the `max_wheel_speed` parameter. You tune that value by
#  experiment (see README, Step 4).
#
#  SAFETY (read this):
#   * A watchdog stops the motors if no /cmd_vel arrives within
#     `cmd_vel_timeout` seconds. This prevents runaway if the publisher
#     dies or Wi-Fi drops.
#   * Velocities are clamped to max_linear_speed / max_angular_speed.
#   * On shutdown the motors are forced to zero.
#   * THIS IS NOT A SUBSTITUTE FOR A PHYSICAL EMERGENCY STOP. You must
#     still wire a latching e-stop that physically cuts MOTOR power.
#
#  Pi 5 note: the Pi 5 uses the RP1 I/O chip. Legacy RPi.GPIO does not
#  work. This node uses gpiozero with the lgpio pin factory.
# =====================================================================

import math
import threading

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from geometry_msgs.msg import Twist


# ---------------------------------------------------------------------
#  Hardware abstraction
# ---------------------------------------------------------------------
class MotorBackend:
    """Interface. set_duty(left, right) with values in [-1.0, 1.0]."""

    def set_duty(self, left: float, right: float) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        self.set_duty(0.0, 0.0)

    def close(self) -> None:
        pass


class DryRunBackend(MotorBackend):
    """No GPIO. Logs duty cycles. Use on a laptop / in CI to test logic."""

    def __init__(self, logger):
        self._logger = logger
        self._last = None

    def set_duty(self, left: float, right: float) -> None:
        pair = (round(left, 3), round(right, 3))
        if pair != self._last:
            self._logger.info(f'[DRY-RUN] duty L={pair[0]:+.3f}  R={pair[1]:+.3f}')
            self._last = pair


class GpiozeroBackend(MotorBackend):
    """Real GPIO backend using gpiozero + lgpio.

    Two wiring styles are supported via `driver_mode`:

      "pwm_dir"  (e.g. Cytron MDD10A, TB6612 single-PWM style):
          one PWM pin + one DIR pin per motor.
          pins needed: left_pwm, left_dir, right_pwm, right_dir

      "dual_pwm" (e.g. BTS7960):
          two PWM pins per motor (forward pin + reverse pin).
          pins needed: left_rpwm, left_lpwm, right_rpwm, right_lpwm
          (optional enable pins left_en / right_en driven high)
    """

    def __init__(self, params, logger):
        self._logger = logger
        self.mode = params['driver_mode']
        self.invert_left = params['invert_left']
        self.invert_right = params['invert_right']
        freq = params['pwm_frequency']

        # Import here so the node still loads on machines without gpiozero.
        from gpiozero import PWMOutputDevice, DigitalOutputDevice, Device
        try:
            from gpiozero.pins.lgpio import LGPIOFactory
            Device.pin_factory = LGPIOFactory()
            logger.info('gpiozero pin factory: lgpio (Raspberry Pi 5 compatible)')
        except Exception as exc:  # noqa: BLE001
            logger.warn(f'Could not force lgpio factory ({exc}); '
                        f'using gpiozero default. On Pi 5 install: sudo apt install python3-lgpio')

        if self.mode == 'pwm_dir':
            self.l_pwm = PWMOutputDevice(params['left_pwm_pin'], frequency=freq)
            self.l_dir = DigitalOutputDevice(params['left_dir_pin'])
            self.r_pwm = PWMOutputDevice(params['right_pwm_pin'], frequency=freq)
            self.r_dir = DigitalOutputDevice(params['right_dir_pin'])

        elif self.mode == 'dual_pwm':
            self.l_r = PWMOutputDevice(params['left_rpwm_pin'], frequency=freq)
            self.l_l = PWMOutputDevice(params['left_lpwm_pin'], frequency=freq)
            self.r_r = PWMOutputDevice(params['right_rpwm_pin'], frequency=freq)
            self.r_l = PWMOutputDevice(params['right_lpwm_pin'], frequency=freq)
            self._enables = []
            for key in ('left_en_pin', 'right_en_pin'):
                pin = params.get(key, -1)
                if pin is not None and pin >= 0:
                    en = DigitalOutputDevice(pin)
                    en.on()
                    self._enables.append(en)
        else:
            raise ValueError(f"Unknown driver_mode '{self.mode}'. "
                             f"Use 'pwm_dir' or 'dual_pwm'.")

    def set_duty(self, left: float, right: float) -> None:
        if self.invert_left:
            left = -left
        if self.invert_right:
            right = -right
        left = max(-1.0, min(1.0, left))
        right = max(-1.0, min(1.0, right))

        if self.mode == 'pwm_dir':
            self.l_dir.value = 1 if left >= 0 else 0
            self.l_pwm.value = abs(left)
            self.r_dir.value = 1 if right >= 0 else 0
            self.r_pwm.value = abs(right)
        else:  # dual_pwm
            if left >= 0:
                self.l_r.value = abs(left); self.l_l.value = 0.0
            else:
                self.l_r.value = 0.0; self.l_l.value = abs(left)
            if right >= 0:
                self.r_r.value = abs(right); self.r_l.value = 0.0
            else:
                self.r_r.value = 0.0; self.r_l.value = abs(right)

    def close(self) -> None:
        try:
            self.stop()
            if self.mode == 'pwm_dir':
                for d in (self.l_pwm, self.l_dir, self.r_pwm, self.r_dir):
                    d.close()
            else:
                for d in (self.l_r, self.l_l, self.r_r, self.r_l):
                    d.close()
                for en in getattr(self, '_enables', []):
                    en.close()
        except Exception:  # noqa: BLE001
            pass


# ---------------------------------------------------------------------
#  Node
# ---------------------------------------------------------------------
class MotorDriverNode(Node):

    def __init__(self):
        super().__init__('motor_driver_node')

        # ---- Parameters ----
        self.declare_parameter('use_hardware', True)
        self.declare_parameter('driver_mode', 'dual_pwm')  # 'pwm_dir' or 'dual_pwm'

        # Geometry
        self.declare_parameter('wheel_radius', 0.045)
        self.declare_parameter('wheel_separation', 0.375)

        # Limits (angular capped at 0.5 rad/s by default to protect rf2o)
        self.declare_parameter('max_linear_speed', 0.5)     # m/s
        self.declare_parameter('max_angular_speed', 0.5)    # rad/s
        # Wheel linear speed that corresponds to 100% PWM duty. TUNE THIS.
        self.declare_parameter('max_wheel_speed', 0.6)      # m/s at full duty
        self.declare_parameter('min_duty', 0.0)             # deadband floor

        # Safety / timing
        self.declare_parameter('cmd_vel_timeout', 0.5)      # s
        self.declare_parameter('control_rate', 20.0)        # Hz watchdog/apply loop

        # Direction fixes (flip if a wheel spins the wrong way)
        self.declare_parameter('invert_left', False)
        self.declare_parameter('invert_right', False)

        # PWM
        self.declare_parameter('pwm_frequency', 1000)       # Hz

        # Pins -- BCM numbering.  (MEASURE/CONFIRM your wiring!)
        #   dual_pwm (BTS7960) defaults:
        self.declare_parameter('left_rpwm_pin', 12)
        self.declare_parameter('left_lpwm_pin', 13)
        self.declare_parameter('right_rpwm_pin', 18)
        self.declare_parameter('right_lpwm_pin', 19)
        self.declare_parameter('left_en_pin', -1)    # -1 = unused (tie R_EN/L_EN high in HW)
        self.declare_parameter('right_en_pin', -1)
        #   pwm_dir (Cytron MDD10A) defaults:
        self.declare_parameter('left_pwm_pin', 12)
        self.declare_parameter('left_dir_pin', 5)
        self.declare_parameter('right_pwm_pin', 18)
        self.declare_parameter('right_dir_pin', 6)

        g = self.get_parameter
        self.wheel_radius = g('wheel_radius').value
        self.wheel_sep = g('wheel_separation').value
        self.max_lin = g('max_linear_speed').value
        self.max_ang = g('max_angular_speed').value
        self.max_wheel = max(1e-6, g('max_wheel_speed').value)
        self.min_duty = g('min_duty').value
        self.timeout = g('cmd_vel_timeout').value
        rate = max(1.0, g('control_rate').value)

        # ---- State ----
        self._lock = threading.Lock()
        self._target_v = 0.0
        self._target_w = 0.0
        self._last_cmd_time = self.get_clock().now()
        self._stopped_logged = False

        # ---- Backend ----
        use_hw = g('use_hardware').value
        if use_hw:
            try:
                params = {
                    'driver_mode': g('driver_mode').value,
                    'pwm_frequency': g('pwm_frequency').value,
                    'invert_left': g('invert_left').value,
                    'invert_right': g('invert_right').value,
                    'left_rpwm_pin': g('left_rpwm_pin').value,
                    'left_lpwm_pin': g('left_lpwm_pin').value,
                    'right_rpwm_pin': g('right_rpwm_pin').value,
                    'right_lpwm_pin': g('right_lpwm_pin').value,
                    'left_en_pin': g('left_en_pin').value,
                    'right_en_pin': g('right_en_pin').value,
                    'left_pwm_pin': g('left_pwm_pin').value,
                    'left_dir_pin': g('left_dir_pin').value,
                    'right_pwm_pin': g('right_pwm_pin').value,
                    'right_dir_pin': g('right_dir_pin').value,
                }
                self.backend = GpiozeroBackend(params, self.get_logger())
                self.get_logger().info(
                    f"Hardware backend active (driver_mode="
                    f"{g('driver_mode').value}).")
            except Exception as exc:  # noqa: BLE001
                self.get_logger().error(
                    f'Failed to init GPIO backend ({exc}). '
                    f'Falling back to DRY-RUN. Set use_hardware:=false to silence.')
                self.backend = DryRunBackend(self.get_logger())
        else:
            self.backend = DryRunBackend(self.get_logger())
            self.get_logger().warn('use_hardware=false -> DRY-RUN (no motors will move).')

        # ---- ROS interfaces ----
        self.sub = self.create_subscription(
            Twist, 'cmd_vel', self._on_cmd_vel, QoSProfile(depth=10))
        self.timer = self.create_timer(1.0 / rate, self._control_loop)

        self.get_logger().info('=' * 56)
        self.get_logger().info(' LUMINAX motor_driver_node started')
        self.get_logger().info(f'  wheel_radius      = {self.wheel_radius} m')
        self.get_logger().info(f'  wheel_separation  = {self.wheel_sep} m')
        self.get_logger().info(f'  max_linear_speed  = {self.max_lin} m/s')
        self.get_logger().info(f'  max_angular_speed = {self.max_ang} rad/s')
        self.get_logger().info(f'  max_wheel_speed   = {self.max_wheel} m/s @100% duty')
        self.get_logger().info(f'  cmd_vel_timeout   = {self.timeout} s')
        self.get_logger().info('  >> A PHYSICAL E-STOP IS STILL REQUIRED <<')
        self.get_logger().info('=' * 56)

    # -- callbacks --
    def _on_cmd_vel(self, msg: Twist):
        v = max(-self.max_lin, min(self.max_lin, msg.linear.x))
        w = max(-self.max_ang, min(self.max_ang, msg.angular.z))
        with self._lock:
            self._target_v = v
            self._target_w = w
            self._last_cmd_time = self.get_clock().now()

    def _control_loop(self):
        now = self.get_clock().now()
        with self._lock:
            v, w = self._target_v, self._target_w
            last = self._last_cmd_time

        age = (now - last).nanoseconds * 1e-9
        if age > self.timeout:
            # Watchdog: no fresh command -> stop.
            self.backend.stop()
            if not self._stopped_logged:
                self.get_logger().warn(
                    f'cmd_vel timeout ({age:.2f}s > {self.timeout}s): motors stopped.')
                self._stopped_logged = True
            return
        self._stopped_logged = False

        # Differential-drive inverse kinematics -> wheel linear speeds
        v_left = v - (w * self.wheel_sep / 2.0)
        v_right = v + (w * self.wheel_sep / 2.0)

        duty_left = self._speed_to_duty(v_left)
        duty_right = self._speed_to_duty(v_right)
        self.backend.set_duty(duty_left, duty_right)

    def _speed_to_duty(self, wheel_speed: float) -> float:
        duty = wheel_speed / self.max_wheel
        duty = max(-1.0, min(1.0, duty))
        # Optional static-friction deadband floor so tiny commands still move.
        if self.min_duty > 0.0 and 0.0 < abs(duty) < self.min_duty:
            duty = math.copysign(self.min_duty, duty)
        return duty

    def destroy_node(self):
        try:
            self.backend.stop()
            self.backend.close()
        finally:
            super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MotorDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

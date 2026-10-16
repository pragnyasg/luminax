#!/usr/bin/env python3
"""
USB Webcam Video Stream Publisher ROS 2 Node for LUMI Healthcare Robot.

Provides an out-of-the-box hardware camera publisher:
1. Opens physical USB webcam via OpenCV VideoCapture (default device /dev/video0).
2. Captures video frames at configurable resolution and framerate.
3. Publishes sensor_msgs/msg/Image on /camera/image_raw.
4. Publishes sensor_msgs/msg/CameraInfo on /camera/camera_info.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo

try:
    import cv2
    from cv_bridge import CvBridge
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False


class WebcamPublisherNode(Node):
    def __init__(self):
        super().__init__('webcam_publisher_node')

        # Parameters
        self.declare_parameter('device_id', 0)
        self.declare_parameter('frame_width', 640)
        self.declare_parameter('frame_height', 480)
        self.declare_parameter('fps', 30.0)
        self.declare_parameter('frame_id', 'camera_optical_link')
        self.declare_parameter('topic_name', '/camera/image_raw')

        self.device_id = self.get_parameter('device_id').value
        self.frame_width = self.get_parameter('frame_width').value
        self.frame_height = self.get_parameter('frame_height').value
        self.fps = self.get_parameter('fps').value
        self.frame_id = self.get_parameter('frame_id').value
        self.topic_name = self.get_parameter('topic_name').value

        self.pub_image = self.create_publisher(Image, self.topic_name, 10)
        self.pub_info = self.create_publisher(CameraInfo, '/camera/camera_info', 10)

        if not HAS_OPENCV:
            self.get_logger().error('OpenCV not installed. Cannot open physical webcam device.')
            self.cap = None
            self.bridge = None
            return

        self.bridge = CvBridge()
        self.cap = cv2.VideoCapture(self.device_id)

        if not self.cap.isOpened():
            self.get_logger().warn(f'Could not open video device index {self.device_id}. Will retry...')
        else:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.get_logger().info(f'Webcam device {self.device_id} opened successfully ({self.frame_width}x{self.frame_height} @ {self.fps} FPS).')

        timer_period = 1.0 / max(self.fps, 1.0)
        self.timer = self.create_timer(timer_period, self.capture_loop)

    def capture_loop(self):
        """Captures frame from webcam and publishes to ROS 2 topic."""
        if not HAS_OPENCV or self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return

        current_time = self.get_clock().now()

        # Build Image message
        img_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        img_msg.header.stamp = current_time.to_msg()
        img_msg.header.frame_id = self.frame_id
        self.pub_image.publish(img_msg)

        # Build basic CameraInfo message
        info_msg = CameraInfo()
        info_msg.header.stamp = current_time.to_msg()
        info_msg.header.frame_id = self.frame_id
        info_msg.width = frame.shape[1]
        info_msg.height = frame.shape[0]
        self.pub_info.publish(info_msg)

    def destroy_node(self):
        if hasattr(self, 'cap') and self.cap and self.cap.isOpened():
            self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = WebcamPublisherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

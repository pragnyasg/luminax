#!/usr/bin/env python3
"""
Person Detection ROS 2 Node for Baymax Healthcare Robot.

This node performs 3 key tasks:
1. Subscribes to /camera/image_raw (sensor_msgs/msg/Image).
2. Processes video frames using OpenCV human detection algorithms.
3. Publishes /perception/person_detected (Bool) and /perception/image_annotated (Image).
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from sensor_msgs.msg import Image

try:
    import cv2
    import numpy as np
    from cv_bridge import CvBridge
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False


class PersonDetectorNode(Node):
    def __init__(self):
        super().__init__('person_detector_node')

        # ROS 2 Subscribers and Publishers
        self.sub_image = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.pub_detected = self.create_publisher(Bool, '/perception/person_detected', 10)
        self.pub_annotated = self.create_publisher(Image, '/perception/image_annotated', 10)

        # OpenCV HOG Person Detector Setup
        if HAS_OPENCV:
            self.bridge = CvBridge()
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            self.get_logger().info('Person Detector Node initialized with OpenCV HOG SVM detector.')
        else:
            self.get_logger().warn('OpenCV / CvBridge not installed. Running in mock perception mode.')

    def image_callback(self, msg: Image):
        """Processes incoming camera image frames for human detection."""
        person_found = False

        if not HAS_OPENCV:
            # Fallback mock detector
            bool_msg = Bool()
            bool_msg.data = False
            self.pub_detected.publish(bool_msg)
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Resize frame for fast processing on RPi 5
            resized = cv2.resize(cv_image, (640, 480))
            
            # Detect people using OpenCV HOG Descriptor
            boxes, weights = self.hog.detectMultiScale(
                resized,
                winStride=(8, 8),
                padding=(4, 4),
                scale=1.05
            )

            # Filter detected boxes
            for (x, y, w, h) in boxes:
                person_found = True
                # Draw bounding box on image (Green box with Baymax label)
                cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    resized,
                    "Person Detected",
                    (x, max(y - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

            # Publish Boolean Detection Result
            detected_msg = Bool()
            detected_msg.data = person_found
            self.pub_detected.publish(detected_msg)

            # Publish Annotated Video Frame for RViz2
            annotated_msg = self.bridge.cv2_to_imgmsg(resized, encoding='bgr8')
            annotated_msg.header = msg.header
            self.pub_annotated.publish(annotated_msg)

        except Exception as e:
            self.get_logger().error(f'Error processing camera image: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = PersonDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

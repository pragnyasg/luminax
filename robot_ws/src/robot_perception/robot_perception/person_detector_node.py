#!/usr/bin/env python3
"""
Person Detection ROS 2 Node for LUMI Healthcare Robot.

This node performs:
1. Subscribes to camera video stream on /camera/image_raw (sensor_msgs/msg/Image).
2. Performs human detection using OpenCV HOG (Histogram of Oriented Gradients) + Linear SVM.
3. Publishes detection alerts on /perception/person_detected (std_msgs/msg/Bool).
4. Publishes detected count on /perception/person_count (std_msgs/msg/Int32).
5. Publishes structured JSON detection data on /perception/detections (std_msgs/msg/String).
6. Publishes annotated video frame on /perception/image_annotated for RViz2 / GUI monitoring.
"""

import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int32, String
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

        # Declare ROS 2 Parameters
        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('annotated_image_topic', '/perception/image_annotated')
        self.declare_parameter('publish_annotated', True)
        self.declare_parameter('downsample_width', 640)
        self.declare_parameter('hit_threshold', 0.0)

        # Retrieve Parameter Values
        self.image_topic = self.get_parameter('image_topic').value
        self.annotated_image_topic = self.get_parameter('annotated_image_topic').value
        self.publish_annotated = self.get_parameter('publish_annotated').value
        self.downsample_width = self.get_parameter('downsample_width').value
        self.hit_threshold = self.get_parameter('hit_threshold').value

        # Publishers
        self.pub_detected = self.create_publisher(Bool, '/perception/person_detected', 10)
        self.pub_count = self.create_publisher(Int32, '/perception/person_count', 10)
        self.pub_detections = self.create_publisher(String, '/perception/detections', 10)
        self.pub_annotated = self.create_publisher(Image, self.annotated_image_topic, 10)

        # OpenCV HOG Person Detector Setup
        if HAS_OPENCV:
            self.bridge = CvBridge()
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            self.get_logger().info('Person Detector initialized with OpenCV HOG+SVM model.')
        else:
            self.bridge = None
            self.get_logger().warn('OpenCV / CvBridge not found. Running in fallback detection mode.')

        # Subscriber
        self.sub_image = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            10
        )

        self.get_logger().info(f'Subscribed to image topic: {self.image_topic}')

    def image_callback(self, msg: Image):
        """Processes incoming camera video frames for human detection."""
        if not HAS_OPENCV or self.bridge is None:
            # Fallback when OpenCV is unavailable
            bool_msg = Bool()
            bool_msg.data = False
            self.pub_detected.publish(bool_msg)
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            h, w = cv_image.shape[:2]

            # Scale frame for optimized CPU processing on Raspberry Pi 5
            if w > self.downsample_width and self.downsample_width > 0:
                scale = self.downsample_width / float(w)
                new_h = int(h * scale)
                frame = cv2.resize(cv_image, (self.downsample_width, new_h))
            else:
                scale = 1.0
                frame = cv_image

            # Run HOG MultiScale Person Detector
            boxes, weights = self.hog.detectMultiScale(
                frame,
                winStride=(8, 8),
                padding=(4, 4),
                scale=1.05,
                hitThreshold=self.hit_threshold
            )

            person_found = len(boxes) > 0
            detections_data = []

            for i, (bx, by, bw, bh) in enumerate(boxes):
                # Scale coordinates back if resized
                orig_x = int(bx / scale)
                orig_y = int(by / scale)
                orig_w = int(bw / scale)
                orig_h = int(bh / scale)

                # Center point of bounding box
                center_x = orig_x + (orig_w // 2)
                center_y = orig_y + (orig_h // 2)

                # Normalized bearing (-1.0 to 1.0, where 0.0 is center of camera view)
                bearing = (center_x - (w / 2.0)) / (w / 2.0)

                # Rough distance estimate based on human height (~1.7m) and camera focal length
                # Distance = (Real Height * Focal Length) / Pixel Height
                approx_focal_px = w * 0.8
                est_distance_m = round((1.7 * approx_focal_px) / max(orig_h, 1), 2)

                conf = float(weights[i]) if i < len(weights) else 1.0
                detections_data.append({
                    "id": i,
                    "bbox": [orig_x, orig_y, orig_w, orig_h],
                    "center": [center_x, center_y],
                    "bearing": round(bearing, 3),
                    "estimated_distance_m": est_distance_m,
                    "confidence": round(conf, 3)
                })

                # Draw bounding box and label on annotated image
                if self.publish_annotated:
                    cv2.rectangle(cv_image, (orig_x, orig_y), (orig_x + orig_w, orig_y + orig_h), (0, 255, 0), 2)
                    label = f"Person #{i+1} ({est_distance_m}m)"
                    cv2.putText(
                        cv_image,
                        label,
                        (orig_x, max(orig_y - 8, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (0, 255, 0),
                        2
                    )

            # 1. Publish Bool detection flag
            bool_msg = Bool()
            bool_msg.data = person_found
            self.pub_detected.publish(bool_msg)

            # 2. Publish Count
            count_msg = Int32()
            count_msg.data = len(boxes)
            self.pub_count.publish(count_msg)

            # 3. Publish Structured JSON telemetry
            json_msg = String()
            json_msg.data = json.dumps({
                "count": len(boxes),
                "timestamp": msg.header.stamp.sec + (msg.header.stamp.nanosec * 1e-9),
                "detections": detections_data
            })
            self.pub_detections.publish(json_msg)

            # 4. Publish Annotated video frame
            if self.publish_annotated:
                annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
                annotated_msg.header = msg.header
                self.pub_annotated.publish(annotated_msg)

        except Exception as e:
            self.get_logger().error(f'Error in perception image_callback: {e}')


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

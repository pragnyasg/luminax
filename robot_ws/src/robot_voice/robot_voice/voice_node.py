#!/usr/bin/env python3
"""
Voice Synthesis & Speech Output ROS 2 Node for LUMI Healthcare Robot.

This node performs:
1. Subscribes to /voice/speak (std_msgs/msg/String).
2. Uses an asynchronous background worker thread to render speech via offline TTS (pyttsx3/espeak),
   preventing the ROS 2 callback executor thread from blocking during long speech utterances.
3. Publishes recognized or received voice commands on /voice/command (std_msgs/msg/String).
4. Provides graceful fallback to console logging when physical audio/TTS is unavailable.
"""

import queue
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False


class VoiceNode(Node):
    def __init__(self):
        super().__init__('voice_node')

        # Parameters
        self.declare_parameter('voice_rate', 150)       # Words per minute
        self.declare_parameter('voice_volume', 1.0)     # Volume level 0.0 to 1.0
        self.declare_parameter('enabled', True)

        self.voice_rate = self.get_parameter('voice_rate').value
        self.voice_volume = self.get_parameter('voice_volume').value
        self.enabled = self.get_parameter('enabled').value

        # Subscribers & Publishers
        self.sub_speak = self.create_subscription(
            String,
            '/voice/speak',
            self.speak_callback,
            10
        )

        self.pub_command = self.create_publisher(String, '/voice/command', 10)

        # Thread-safe speech queue & worker
        self.speech_queue = queue.Queue()
        self.is_running = True

        if HAS_TTS and self.enabled:
            self.worker_thread = threading.Thread(target=self._tts_worker, daemon=True)
            self.worker_thread.start()
            self.get_logger().info('Voice Node initialized with background pyttsx3 worker thread.')
        else:
            self.worker_thread = None
            self.get_logger().warn('pyttsx3 not available or disabled. Running in console speech logging mode.')

    def _tts_worker(self):
        """Dedicated worker thread handling TTS playback without blocking ROS 2 thread."""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.voice_rate)
            engine.setProperty('volume', self.voice_volume)
        except Exception as e:
            self.get_logger().warn(f'Could not initialize pyttsx3 engine in worker: {e}. Fallback active.')
            engine = None

        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if text is None:  # Shutdown signal
                break

            if engine is not None:
                try:
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    self.get_logger().error(f'Error rendering TTS speech: {e}')

            self.speech_queue.task_done()

    def speak_callback(self, msg: String):
        """Enqueue speech request."""
        text = msg.data.strip()
        if not text:
            return

        self.get_logger().info(f'[LUMI VOICE]: "{text}"')

        if HAS_TTS and self.worker_thread is not None:
            self.speech_queue.put(text)

    def destroy_node(self):
        self.is_running = False
        if hasattr(self, 'speech_queue'):
            self.speech_queue.put(None)
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = VoiceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

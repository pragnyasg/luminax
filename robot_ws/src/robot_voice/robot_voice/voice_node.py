#!/usr/bin/env python3
"""
Voice Synthesis & Keyword Parser ROS 2 Node for Baymax Healthcare Robot.

This node performs 2 key tasks:
1. Subscribes to /voice/speak (String) and uses TTS engine (pyttsx3/espeak) to speak prompts.
2. Publishes /voice/command (String) for simple keyword interactions.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# Try importing pyttsx3 offline text-to-speech engine
try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False


class VoiceNode(Node):
    def __init__(self):
        super().__init__('voice_node')

        # ROS 2 Subscribers and Publishers
        self.sub_speak = self.create_subscription(
            String,
            '/voice/speak',
            self.speak_callback,
            10
        )

        self.pub_command = self.create_publisher(String, '/voice/command', 10)

        # Initialize TTS Engine
        if HAS_TTS:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)  # Gentle speaking pace
                self.get_logger().info('Voice Node initialized with pyttsx3 TTS engine.')
            except Exception as e:
                self.get_logger().warn(f'Could not initialize pyttsx3 engine: {e}. Using console log TTS fallback.')
                self.tts_engine = None
        else:
            self.get_logger().warn('pyttsx3 module not installed. Running in console log TTS fallback mode.')
            self.tts_engine = None

    def speak_callback(self, msg: String):
        """Speaks the incoming text message using offline TTS."""
        text_to_speak = msg.data
        self.get_logger().info(f'[BAYMAX VOICE OUTPUT]: "{text_to_speak}"')

        if HAS_TTS and self.tts_engine:
            try:
                self.tts_engine.say(text_to_speak)
                self.tts_engine.runAndWait()
            except Exception as e:
                self.get_logger().error(f'Error rendering TTS audio: {e}')


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

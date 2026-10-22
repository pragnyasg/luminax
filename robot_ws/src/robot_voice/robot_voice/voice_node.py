#!/usr/bin/env python3
"""
Deep Learning Voice Assistant & Speech Synthesis ROS 2 Node for LUMINAX Robot.

Integrates:
1. Speech-to-Text: OpenAI Whisper via faster-whisper.
2. Conversational AI: Local LLM via Ollama with healthcare safety system prompts.
3. Text-to-Speech: Offline speech synthesis (Piper TTS / pyttsx3 fallback).
4. Audio I/O: Microphone capture with VAD and speaker playback for Raspberry Pi 5.
5. ROS 2 Bridge:
   - Subscribes to /voice/speak (std_msgs/msg/String) for outbound speech prompts.
   - Subscribes to /voice/command (std_msgs/msg/String) for pipeline control.
   - Subscribes to /vision/events/emergency (std_msgs/msg/String) for immediate verbal fall alerts.
   - Publishes /voice/recognized_speech (std_msgs/msg/String) with user transcription.
   - Publishes /voice/response_text (std_msgs/msg/String) with LUMI's spoken response.
   - Publishes /voice/status (std_msgs/msg/String) with pipeline health telemetry.
"""

import json
import logging
import os
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

# ROS 2 imports with conditional fallback for non-ROS environments
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False
    Node = object  # type: ignore

# Import lumi_voice modular components
try:
    from robot_voice.lumi_voice.config import LumiConfig
    from robot_voice.lumi_voice.pipeline import ComponentStatus, PipelineState, VoicePipeline
    HAS_LUMI_VOICE = True
except ImportError:
    try:
        from lumi_voice.config import LumiConfig
        from lumi_voice.pipeline import ComponentStatus, PipelineState, VoicePipeline
        HAS_LUMI_VOICE = True
    except ImportError:
        HAS_LUMI_VOICE = False

# Fallback pyttsx3 import
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

logger = logging.getLogger('robot_voice')


class VoiceNode(Node if HAS_ROS2 else object):
    """
    ROS 2 Voice Assistant Node coordinating STT, LLM reasoning, TTS, and safety alerts.
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        if HAS_ROS2:
            super().__init__('voice_node')
            self.declare_parameter('config_path', '')
            self.declare_parameter('continuous_listening', False)
            self.declare_parameter('voice_rate', 150)
            self.declare_parameter('voice_volume', 1.0)
            self.declare_parameter('enabled', True)

            cfg_param = self.get_parameter('config_path').value
            self.continuous_listening = self.get_parameter('continuous_listening').value
            self.voice_rate = self.get_parameter('voice_rate').value
            self.voice_volume = self.get_parameter('voice_volume').value
            self.enabled = self.get_parameter('enabled').value
            cfg_path = config_path or (cfg_param if cfg_param else None)
        else:
            self.continuous_listening = False
            self.voice_rate = 150
            self.voice_volume = 1.0
            self.enabled = True
            cfg_path = config_path

        self.speech_queue = queue.Queue()
        self.is_running = True
        self.pipeline: Optional[Any] = None

        # 1. Initialize Deep Learning Voice Pipeline if available
        if HAS_LUMI_VOICE and self.enabled:
            try:
                lumi_cfg = self._load_lumi_config(cfg_path)
                self.pipeline = VoicePipeline(
                    config=lumi_cfg,
                    on_state_change=self._on_pipeline_state_change,
                    on_transcript=self._on_transcript,
                    on_response=self._on_response,
                    on_error=self._on_pipeline_error,
                )
                self.pipeline.start()
                if self.continuous_listening:
                    self.pipeline.start_continuous_listening()
                if HAS_ROS2:
                    self.get_logger().info('LUMI Deep Learning Voice Pipeline initialized successfully.')
            except Exception as e:
                if HAS_ROS2:
                    self.get_logger().warn(f'Could not initialize full VoicePipeline ({e}). Falling back to lightweight speech engine.')
                self.pipeline = None

        # 2. Lightweight pyttsx3 fallback worker
        self._init_tts_fallback()

        # 3. Setup ROS 2 Communications
        if HAS_ROS2:
            self.pub_speech = self.create_publisher(String, '/voice/recognized_speech', 10)
            self.pub_response = self.create_publisher(String, '/voice/response_text', 10)
            self.pub_status = self.create_publisher(String, '/voice/status', 10)
            self.pub_command = self.create_publisher(String, '/voice/command', 10)

            # Subscribers
            self.sub_speak = self.create_subscription(
                String,
                '/voice/speak',
                self.speak_callback,
                10
            )

            self.sub_command = self.create_subscription(
                String,
                '/voice/command',
                self.command_callback,
                10
            )

            # Emergency Fall Alert subscriber
            self.sub_emergency = self.create_subscription(
                String,
                '/vision/events/emergency',
                self.emergency_alert_callback,
                10
            )

            # Periodic status timer (every 5 seconds)
            self.status_timer = self.create_timer(5.0, self._publish_status)
            self.get_logger().info('LUMI Voice Node listening on /voice/speak and /vision/events/emergency')

    def _load_lumi_config(self, cfg_path: Optional[str]) -> Any:
        if cfg_path and os.path.isfile(cfg_path):
            return LumiConfig.load_yaml(cfg_path)
        # Search candidate locations
        candidates = [
            'config/voice_config.yaml',
            'robot_ws/src/robot_voice/config/voice_config.yaml',
            '../config/voice_config.yaml',
        ]
        for c in candidates:
            if os.path.isfile(c):
                return LumiConfig.load_yaml(c)
        return LumiConfig()

    def _init_tts_fallback(self) -> None:
        if self.pipeline is None and HAS_PYTTSX3 and self.enabled:
            self.worker_thread = threading.Thread(target=self._tts_worker, daemon=True)
            self.worker_thread.start()
        else:
            self.worker_thread = None

    def _tts_worker(self) -> None:
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.voice_rate)
            engine.setProperty('volume', self.voice_volume)
        except Exception:
            engine = None

        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if text is None:
                break

            if engine is not None:
                try:
                    engine.say(text)
                    engine.runAndWait()
                except Exception as exc:
                    if HAS_ROS2:
                        self.get_logger().error(f'Error rendering TTS: {exc}')

            self.speech_queue.task_done()

    def speak(self, text: str) -> None:
        """Deliver spoken utterance through available pipeline or fallback."""
        text = text.strip()
        if not text:
            return

        if HAS_ROS2:
            self.get_logger().info(f'[LUMI VOICE SPOKEN]: "{text}"')

        if self.pipeline is not None:
            # Process via Piper TTS / playback
            try:
                self.pipeline.process_text_input(text)
                return
            except Exception as exc:
                if HAS_ROS2:
                    self.get_logger().warn(f'Pipeline speech failed ({exc}); routing to fallback.')

        # Fallback queue
        if self.worker_thread is not None:
            self.speech_queue.put(text)
        else:
            print(f'[LUMI VOICE AUDIBLE]: {text}')

    def speak_callback(self, msg: Any) -> None:
        """Direct speech invocation from ROS 2 topic."""
        self.speak(msg.data)

    def emergency_alert_callback(self, msg: Any) -> None:
        """Handles incoming vision emergency events (fall detection, missing patient)."""
        try:
            data = json.loads(msg.data)
            ev_type = data.get('event_type', '')
            person = data.get('person_name', 'Patient')
            if person in (None, 'Unknown', 'None'):
                person = 'someone'

            if ev_type == 'fall_confirmed':
                prompt = f"Warning! A fall has been detected for {person}. Please stay still, emergency alerts have been transmitted to your caregiver."
                self.speak(prompt)
            elif ev_type == 'fall_suspected':
                prompt = f"{person}, are you alright? I detected a rapid descent."
                self.speak(prompt)
            elif ev_type == 'person_missing':
                prompt = f"Notice: {person} is no longer visible in the camera view."
                self.speak(prompt)
        except Exception as exc:
            if HAS_ROS2:
                self.get_logger().error(f'Error parsing emergency event in voice node: {exc}')

    def command_callback(self, msg: Any) -> None:
        """Handle incoming voice command strings or JSON action payloads."""
        raw = msg.data.strip()
        if not raw:
            return

        try:
            cmd = json.loads(raw)
            action = cmd.get('action', '')
            if action == 'speak':
                self.speak(cmd.get('text', ''))
            elif action == 'listen':
                if self.pipeline:
                    self.pipeline.start_continuous_listening()
            elif action == 'stop':
                if self.pipeline:
                    self.pipeline.stop_all()
            elif action == 'status':
                self._publish_status()
        except json.JSONDecodeError:
            # Plain string
            self.speak(raw)

    def _on_transcript(self, text: str) -> None:
        """Callback when Whisper transcribes user speech."""
        if HAS_ROS2:
            self.get_logger().info(f'Transcribed user speech: "{text}"')
            msg = String()
            msg.data = text
            self.pub_speech.publish(msg)
            self.pub_command.publish(msg)

    def _on_response(self, text: str) -> None:
        """Callback when Ollama/LLM produces response text."""
        if HAS_ROS2:
            self.get_logger().info(f'LUMI LLM Response: "{text}"')
            msg = String()
            msg.data = text
            self.pub_response.publish(msg)

    def _on_pipeline_state_change(self, state: Any) -> None:
        if HAS_ROS2:
            self.get_logger().debug(f'Voice Pipeline State: {state}')

    def _on_pipeline_error(self, err_msg: str) -> None:
        if HAS_ROS2:
            self.get_logger().error(f'Voice Pipeline Error: {err_msg}')

    def _publish_status(self) -> None:
        if not HAS_ROS2:
            return
        status_info = {
            'has_lumi_voice': HAS_LUMI_VOICE,
            'pipeline_active': self.pipeline is not None,
            'state': self.pipeline.state.value if self.pipeline else 'fallback',
            'components': self.pipeline.status.to_dict() if self.pipeline else {
                'microphone': 'unavailable',
                'stt': 'unavailable',
                'llm': 'fallback',
                'tts': 'pyttsx3' if HAS_PYTTSX3 else 'console',
            },
        }
        msg = String()
        msg.data = json.dumps(status_info)
        self.pub_status.publish(msg)

    def destroy_node(self) -> None:
        self.is_running = False
        if self.pipeline is not None:
            try:
                self.pipeline.shutdown()
            except Exception:
                pass
        if hasattr(self, 'speech_queue'):
            self.speech_queue.put(None)
        if HAS_ROS2:
            super().destroy_node()


def main(args: Optional[list] = None) -> None:
    if not HAS_ROS2:
        print('ROS 2 (rclpy) is not available in the current environment.')
        print('Running standalone VoiceNode...')
        node = VoiceNode()
        node.speak('Hello! I am LUMI, your healthcare companion robot.')
        time.sleep(1.0)
        node.destroy_node()
        return

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

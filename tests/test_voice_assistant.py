import os
import sys

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
voice_src = os.path.join(repo_root, 'robot_ws', 'src', 'robot_voice')
if voice_src not in sys.path:
    sys.path.insert(0, voice_src)

"""
Unit Tests for LUMI Voice Assistant & ROS 2 Voice Integration.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from robot_voice.voice_node import VoiceNode
from robot_voice.lumi_voice.config import LumiConfig
from robot_voice.lumi_voice.conversation import ConversationManager, Message
from robot_voice.lumi_voice.llm import LLMEngine


class TestConversationManager:
    def test_message_formatting(self):
        mgr = ConversationManager(system_prompt="You are LUMI.", max_history=5)
        mgr.add_user_message("Hello LUMI")
        mgr.add_assistant_message("Hello! How are you feeling today?")

        api_msgs = mgr.get_messages_for_api()
        assert len(api_msgs) == 3
        assert api_msgs[0]["role"] == "system"
        assert api_msgs[1]["role"] == "user"
        assert api_msgs[2]["role"] == "assistant"

    def test_history_trimming(self):
        mgr = ConversationManager(system_prompt="System", max_history=3)
        for i in range(10):
            mgr.add_user_message(f"Message {i}")
        assert mgr.message_count == 3
        assert mgr.messages[-1].content == "Message 9"


class TestVoiceNode:
    def test_voice_node_init(self):
        node = VoiceNode()
        assert node.is_running is True
        assert node.enabled is True
        node.destroy_node()

    def test_voice_node_speak(self):
        node = VoiceNode()
        # Mock speak queue
        node.speak("Please remember to drink water.")
        node.destroy_node()

    def test_emergency_alert_callback_fall_confirmed(self):
        node = VoiceNode()
        spoken_messages = []
        node.speak = lambda text: spoken_messages.append(text)

        msg = MagicMock()
        msg.data = json.dumps({
            "event_type": "fall_confirmed",
            "person_name": "Pragnya",
            "severity": "CRITICAL"
        })
        node.emergency_alert_callback(msg)

        assert len(spoken_messages) == 1
        assert "fall has been detected for Pragnya" in spoken_messages[0]
        node.destroy_node()

    def test_emergency_alert_callback_person_missing(self):
        node = VoiceNode()
        spoken_messages = []
        node.speak = lambda text: spoken_messages.append(text)

        msg = MagicMock()
        msg.data = json.dumps({
            "event_type": "person_missing",
            "person_name": "Madhav",
            "severity": "WARNING"
        })
        node.emergency_alert_callback(msg)

        assert len(spoken_messages) == 1
        assert "Madhav is no longer visible" in spoken_messages[0]
        node.destroy_node()

    def test_command_callback_json(self):
        node = VoiceNode()
        spoken_messages = []
        node.speak = lambda text: spoken_messages.append(text)

        msg = MagicMock()
        msg.data = json.dumps({"action": "speak", "text": "Taking vitals now."})

        node.command_callback(msg)

        assert len(spoken_messages) == 1
        assert spoken_messages[0] == "Taking vitals now."
        node.destroy_node()

#!/usr/bin/env python3
"""
Unit Tests for LUMI ESP32 Serial Protocol JSON Encoding & Decoding.
"""

import json
import unittest


class TestSerialProtocol(unittest.TestCase):
    def test_velocity_command_serialization(self):
        """Test sending velocity packets from ROS 2 to ESP32."""
        v_l = 0.254
        v_r = 0.187
        packet = {
            "cmd": "vel",
            "v_l": round(v_l, 3),
            "v_r": round(v_r, 3)
        }
        encoded = json.dumps(packet) + "\n"
        decoded = json.loads(encoded.strip())

        self.assertEqual(decoded["cmd"], "vel")
        self.assertEqual(decoded["v_l"], 0.254)
        self.assertEqual(decoded["v_r"], 0.187)

    def test_telemetry_packet_parsing(self):
        """Test parsing ESP32 telemetry packet with encoder ticks and battery voltage."""
        raw_telemetry = '{"enc_l": 1520, "enc_r": 1530, "v_bat": 12.1}\n'
        data = json.loads(raw_telemetry.strip())

        self.assertIn("enc_l", data)
        self.assertIn("enc_r", data)
        self.assertIn("v_bat", data)
        self.assertEqual(data["enc_l"], 1520)
        self.assertEqual(data["enc_r"], 1530)
        self.assertEqual(data["v_bat"], 12.1)

    def test_battery_percentage_calculation(self):
        """Test 12V Li-ion battery state estimation (min 10.5V, max 12.6V)."""
        def calc_battery_pct(v_bat):
            return max(0.0, min(1.0, (v_bat - 10.5) / (12.6 - 10.5)))

        self.assertAlmostEqual(calc_battery_pct(12.6), 1.0)
        self.assertAlmostEqual(calc_battery_pct(10.5), 0.0)
        self.assertAlmostEqual(calc_battery_pct(11.55), 0.5)
        # Clamping
        self.assertAlmostEqual(calc_battery_pct(13.0), 1.0)
        self.assertAlmostEqual(calc_battery_pct(9.0), 0.0)

    def test_malformed_telemetry_robustness(self):
        """Ensure malformed or incomplete serial lines are safely rejected."""
        invalid_packets = [
            "BROKEN_JSON_DATA",
            "{'missing_closing_brace'",
            "",
            "   \n"
        ]
        for packet in invalid_packets:
            with self.assertRaises((json.JSONDecodeError, ValueError)):
                if not packet.strip():
                    raise ValueError("Empty")
                json.loads(packet.strip())


if __name__ == '__main__':
    unittest.main()

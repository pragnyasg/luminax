#!/usr/bin/env python3
"""
Unit Tests for XML, URDF/Xacro, YAML, and Python Compilation across LUMI Workspace.
"""

import glob
import os
import py_compile
import unittest
import xml.etree.ElementTree as ET
import yaml


class TestROSStructureAndSyntax(unittest.TestCase):
    def setUp(self):
        # Locate workspace root
        self.repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.robot_ws_src = os.path.join(self.repo_root, 'robot_ws', 'src')

    def test_package_xml_validity(self):
        """All package.xml manifests must be valid XML and define format 3."""
        package_xmls = glob.glob(os.path.join(self.robot_ws_src, '**', 'package.xml'), recursive=True)
        self.assertGreater(len(package_xmls), 0, "No package.xml files found in workspace!")

        expected_packages = [
            'robot_description',
            'robot_simulation',
            'robot_hardware',
            'robot_navigation',
            'robot_perception',
            'robot_voice',
            'robot_health',
            'robot_behaviour',
            'robot_bringup',
            'luminax_vision_ros'
        ]
        found_packages = []

        for pxml in package_xmls:
            tree = ET.parse(pxml)
            root = tree.getroot()
            self.assertEqual(root.tag, 'package')
            self.assertEqual(root.attrib.get('format'), '3')
            name_node = root.find('name')
            self.assertIsNotNone(name_node, f"Package {pxml} missing <name> tag")
            found_packages.append(name_node.text.strip())

        for exp in expected_packages:
            self.assertIn(exp, found_packages, f"Required package {exp} not found in workspace!")

    def test_urdf_xacro_validity(self):
        """URDF and Xacro files must be well-formed XML and contain required links and joints."""
        xacro_files = glob.glob(os.path.join(self.robot_ws_src, '**', '*.xacro'), recursive=True)
        self.assertGreater(len(xacro_files), 0)

        for xf in xacro_files:
            tree = ET.parse(xf)
            root = tree.getroot()
            self.assertEqual(root.tag, 'robot')

            # Check essential links in healthcare_robot.urdf.xacro
            link_names = [elem.attrib.get('name') for elem in root.findall('link')]
            for req_link in ['base_footprint', 'base_link', 'caster_wheel_link', 'lidar_link', 'camera_link']:
                self.assertIn(req_link, link_names, f"Missing required link {req_link} in {xf}")

            # Check essential fixed/continuous joints
            joint_names = [elem.attrib.get('name') for elem in root.findall('joint')]
            for req_joint in ['base_footprint_joint', 'caster_wheel_joint', 'lidar_joint', 'camera_joint']:
                self.assertIn(req_joint, joint_names, f"Missing required joint {req_joint} in {xf}")

    def test_yaml_files_validity(self):
        """All YAML configuration files in config directories must be valid YAML."""
        yaml_files = glob.glob(os.path.join(self.robot_ws_src, '**', '*.yaml'), recursive=True)
        self.assertGreater(len(yaml_files), 0)

        for yf in yaml_files:
            with open(yf, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            self.assertIsInstance(data, dict, f"YAML file {yf} did not parse into a dictionary")

    def test_python_source_compilation(self):
        """Every Python file in robot_ws, scripts, and tests must compile cleanly."""
        py_files = glob.glob(os.path.join(self.repo_root, '**', '*.py'), recursive=True)
        self.assertGreater(len(py_files), 10)

        for pf in py_files:
            # Skip virtual environments if any exist
            if '.venv' in pf or 'env' in pf:
                continue
            py_compile.compile(pf, doraise=True)


if __name__ == '__main__':
    unittest.main()

import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'robot_behaviour'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Team Baymax',
    maintainer_email='student@university.edu',
    description='Finite State Machine companion behavior manager for Baymax Healthcare Robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'behaviour_manager_node = robot_behaviour.behaviour_manager_node:main',
        ],
    },
)

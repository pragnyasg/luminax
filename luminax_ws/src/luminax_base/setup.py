import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'luminax_base'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='LUMINAX Team',
    maintainer_email='you@example.com',
    description='Differential-drive motor control node (Pi 5 GPIO) for LUMINAX.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'motor_driver_node = luminax_base.motor_driver_node:main',
        ],
    },
)

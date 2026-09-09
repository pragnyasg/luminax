import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'robot_navigation'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.[py][xml]*'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.[yaml][yml]*'))),
        (os.path.join('share', package_name, 'maps'), glob(os.path.join('maps', '*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Team Baymax',
    maintainer_email='student@university.edu',
    description='SLAM mapping and Nav2 autonomous goal navigation package for Baymax Healthcare Robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)

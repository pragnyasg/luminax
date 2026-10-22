import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_voice = get_package_share_directory('robot_voice')
    default_config_path = os.path.join(pkg_voice, 'config', 'voice_config.yaml')

    config_arg = DeclareLaunchArgument(
        'config_file',
        default_value=default_config_path,
        description='Path to voice configuration YAML file'
    )

    continuous_arg = DeclareLaunchArgument(
        'continuous_listening',
        default_value='false',
        description='Enable continuous audio listening from microphone'
    )

    voice_node = Node(
        package='robot_voice',
        executable='voice_node',
        name='voice_node',
        output='screen',
        parameters=[{
            'config_path': LaunchConfiguration('config_file'),
            'continuous_listening': LaunchConfiguration('continuous_listening'),
        }]
    )

    return LaunchDescription([
        config_arg,
        continuous_arg,
        voice_node
    ])

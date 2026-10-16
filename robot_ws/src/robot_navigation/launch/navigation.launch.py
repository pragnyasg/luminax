import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    """
    ROS 2 Humble Nav2 Autonomous Navigation Launch File.
    Launches standard nav2_bringup stack with nav2_params.yaml.
    """

    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    pkg_robot_navigation = get_package_share_directory('robot_navigation')

    default_params_file = os.path.join(pkg_robot_navigation, 'config', 'nav2_params.yaml')
    default_map_file = os.path.join(pkg_robot_navigation, 'maps', 'sample_map.yaml')

    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Full path to Nav2 parameters file'
    )

    map_file_arg = DeclareLaunchArgument(
        'map',
        default_value=default_map_file,
        description='Full path to map YAML file'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    autostart_arg = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the Nav2 lifecycle stack'
    )

    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'params_file': LaunchConfiguration('params_file'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'autostart': LaunchConfiguration('autostart')
        }.items()
    )

    return LaunchDescription([
        params_file_arg,
        map_file_arg,
        use_sim_time_arg,
        autostart_arg,
        nav2_bringup_launch
    ])

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    """
    ROS 2 Humble Launch Description for Baymax Healthcare Robot.
    
    This launch file performs 3 primary tasks:
    1. Processes the Xacro robot description file into raw URDF format.
    2. Runs robot_state_publisher to publish robot joint transforms (/tf).
    3. Launches joint_state_publisher_gui and rviz2 for 3D visualization.
    """

    # Locate package share directory
    pkg_share = get_package_share_directory('robot_description')
    
    # Default file paths
    default_model_path = os.path.join(pkg_share, 'urdf', 'healthcare_robot.urdf.xacro')
    default_rviz_config_path = os.path.join(pkg_share, 'rviz', 'robot.rviz')

    # Launch Configurations (command line arguments)
    model_arg = DeclareLaunchArgument(
        name='model',
        default_value=default_model_path,
        description='Absolute path to robot Xacro description file'
    )
    
    rviz_arg = DeclareLaunchArgument(
        name='rvizconfig',
        default_value=default_rviz_config_path,
        description='Absolute path to RViz configuration file'
    )

    # Process Xacro file using ROS 2 Humble ParameterValue substitution
    robot_description = ParameterValue(
        Command(['xacro ', LaunchConfiguration('model')]),
        value_type=str
    )

    # 1. Robot State Publisher Node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}]
    )

    # 2. Joint State Publisher GUI Node (provides interactive sliders for wheel rotation)
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # 3. RViz2 Visualization Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')]
    )

    return LaunchDescription([
        model_arg,
        rviz_arg,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])

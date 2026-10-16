import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    """
    ROS 2 Humble Master Gazebo Simulation Launch File for LUMI Healthcare Robot.
    
    1. Launches Gazebo Classic 11 server (gzserver) with healthcare_room world.
    2. Conditionally launches Gazebo client (gzclient) GUI.
    3. Runs robot_state_publisher with healthcare_robot.urdf.xacro.
    4. Spawns differential-drive robot entity into Gazebo at origin.
    5. Conditionally opens RViz2 configured with robot model and sensor displays.
    """

    # Locate package directories
    pkg_robot_description = get_package_share_directory('robot_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    
    try:
        pkg_robot_simulation = get_package_share_directory('robot_simulation')
        default_world_path = os.path.join(pkg_robot_simulation, 'worlds', 'healthcare_room.world')
    except Exception:
        default_world_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'worlds', 'healthcare_room.world')

    xacro_file_path = os.path.join(pkg_robot_description, 'urdf', 'healthcare_robot.urdf.xacro')
    rviz_config_path = os.path.join(pkg_robot_description, 'rviz', 'robot.rviz')

    # Declare Launch Arguments
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world_path,
        description='Full path to Gazebo world file to load'
    )

    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Set to "true" to run Gazebo GUI (gzclient), "false" for headless'
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Set to "true" to open RViz2 alongside Gazebo'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # Process Xacro into robot_description XML string
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file_path]),
        value_type=str
    )

    # 1. Gazebo Server (gzserver)
    start_gazebo_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': LaunchConfiguration('world')}.items()
    )

    # 2. Gazebo Client (gzclient) GUI
    start_gazebo_client_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('gui'))
    )

    # 3. Robot State Publisher Node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }]
    )

    # 4. Spawn Robot Entity into Gazebo
    spawn_robot_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', 'healthcare_robot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.05'
        ]
    )

    # 5. RViz2 Visualization
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(LaunchConfiguration('use_rviz'))
    )

    return LaunchDescription([
        world_arg,
        gui_arg,
        use_rviz_arg,
        use_sim_time_arg,
        start_gazebo_server_cmd,
        start_gazebo_client_cmd,
        robot_state_publisher_node,
        spawn_robot_node,
        rviz_node
    ])

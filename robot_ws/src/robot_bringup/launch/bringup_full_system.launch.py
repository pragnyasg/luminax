import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    """
    Master Bringup Launch File for LUMI Healthcare Companion Robot.
    
    Seamlessly orchestrates:
    - Mode A: Simulation (Gazebo Classic 11 + gzclient/headless) when use_sim:=true.
    - Mode B: Real Hardware (serial_bridge_node to ESP32 + robot_state_publisher) when use_sim:=false.
    - SLAM Mapping (slam_toolbox) when use_slam:=true.
    - Nav2 Goal Navigation when use_nav2:=true.
    - Perception (OpenCV HOG Person Detection) when use_perception:=true.
    - Voice Interaction (pyttsx3 Async TTS) when use_voice:=true.
    - Healthcare Reminders & Escalations when use_health:=true.
    - FSM Behaviour Supervisor when use_behaviour:=true.
    - RViz2 3D Sensor & Map Visualization when use_rviz:=true.
    """

    # Locate package directories
    pkg_robot_description = get_package_share_directory('robot_description')
    pkg_robot_navigation = get_package_share_directory('robot_navigation')
    
    try:
        pkg_robot_simulation = get_package_share_directory('robot_simulation')
        gazebo_launch_path = os.path.join(pkg_robot_simulation, 'launch', 'gazebo_sim.launch.py')
    except Exception:
        pkg_simulation_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        gazebo_launch_path = os.path.join(pkg_simulation_dir, 'simulation', 'launch', 'gazebo_sim.launch.py')

    xacro_file_path = os.path.join(pkg_robot_description, 'urdf', 'healthcare_robot.urdf.xacro')
    rviz_nav_config_path = os.path.join(pkg_robot_navigation, 'rviz', 'navigation.rviz')
    slam_launch_path = os.path.join(pkg_robot_navigation, 'launch', 'slam.launch.py')
    nav2_launch_path = os.path.join(pkg_robot_navigation, 'launch', 'navigation.launch.py')

    # Declare Launch Arguments
    use_sim_arg = DeclareLaunchArgument(
        'use_sim',
        default_value='true',
        description='Launch Gazebo simulation if true; launch hardware serial bridge if false'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock if true'
    )

    use_slam_arg = DeclareLaunchArgument(
        'use_slam',
        default_value='true',
        description='Launch SLAM Toolbox mapping if true'
    )

    use_nav2_arg = DeclareLaunchArgument(
        'use_nav2',
        default_value='true',
        description='Launch Nav2 autonomous navigation if true'
    )

    use_perception_arg = DeclareLaunchArgument(
        'use_perception',
        default_value='true',
        description='Launch camera person detector node if true'
    )

    use_voice_arg = DeclareLaunchArgument(
        'use_voice',
        default_value='true',
        description='Launch voice synthesis node if true'
    )

    use_health_arg = DeclareLaunchArgument(
        'use_health',
        default_value='true',
        description='Launch healthcare reminder manager if true'
    )

    use_behaviour_arg = DeclareLaunchArgument(
        'use_behaviour',
        default_value='true',
        description='Launch behaviour supervisor FSM if true'
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz2 if true'
    )

    # 1. SIMULATION STACK (Launched only when use_sim:=true)
    sim_stack = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch_path),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'use_rviz': 'false'  # We launch our custom navigation.rviz below
        }.items(),
        condition=IfCondition(LaunchConfiguration('use_sim'))
    )

    # 2. HARDWARE STACK (Launched only when use_sim:=false on physical robot)
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file_path]),
        value_type=str
    )

    hw_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False
        }],
        condition=UnlessCondition(LaunchConfiguration('use_sim'))
    )

    hw_serial_bridge = Node(
        package='robot_hardware',
        executable='serial_bridge_node',
        name='serial_bridge_node',
        output='screen',
        parameters=[{
            'port': '/dev/ttyUSB0',
            'baudrate': 115200,
            'publish_tf': True
        }],
        condition=UnlessCondition(LaunchConfiguration('use_sim'))
    )

    # 3. SLAM MAPPING
    slam_stack = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_launch_path),
        launch_arguments={'use_sim_time': LaunchConfiguration('use_sim_time')}.items(),
        condition=IfCondition(LaunchConfiguration('use_slam'))
    )

    # 4. NAV2 GOAL NAVIGATION
    nav2_stack = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_launch_path),
        launch_arguments={'use_sim_time': LaunchConfiguration('use_sim_time')}.items(),
        condition=IfCondition(LaunchConfiguration('use_nav2'))
    )

    # 5. PERCEPTION: Person Detector Node
    person_detector_node = Node(
        package='robot_perception',
        executable='person_detector_node',
        name='person_detector_node',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_perception'))
    )

    # 6. VOICE: Speech Interaction Node
    voice_node = Node(
        package='robot_voice',
        executable='voice_node',
        name='voice_node',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_voice'))
    )

    # 7. HEALTH: Reminder Manager Node
    reminder_manager_node = Node(
        package='robot_health',
        executable='reminder_manager_node',
        name='reminder_manager_node',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_health'))
    )

    # 8. BEHAVIOUR: FSM Supervisor Node
    behaviour_manager_node = Node(
        package='robot_behaviour',
        executable='behaviour_manager_node',
        name='behaviour_manager_node',
        output='screen',
        condition=IfCondition(LaunchConfiguration('use_behaviour'))
    )

    # 9. RVIZ2 VISUALIZATION
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_nav_config_path],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(LaunchConfiguration('use_rviz'))
    )

    return LaunchDescription([
        use_sim_arg,
        use_sim_time_arg,
        use_slam_arg,
        use_nav2_arg,
        use_perception_arg,
        use_voice_arg,
        use_health_arg,
        use_behaviour_arg,
        use_rviz_arg,
        sim_stack,
        hw_robot_state_publisher,
        hw_serial_bridge,
        slam_stack,
        nav2_stack,
        person_detector_node,
        voice_node,
        reminder_manager_node,
        behaviour_manager_node,
        rviz_node
    ])

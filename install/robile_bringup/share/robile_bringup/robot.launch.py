#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.descriptions import ParameterValue


def generate_launch_description():

    robotname = os.environ['ROBOT_NAME']

    smart_wheel_driver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory("kelo_tulip"), 'launch'),
            '/example_joypad.launch.py'])
    )

    if robotname=='robile3':
        print('[INFO] [launch] robile3: loading Sick-LMS1XX')
        laser_scanner = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('sick_scan'), 'launch'),
            '/sick_lms_1xx.launch.py']),
    )  
    elif robotname=='robile4':
        print('[INFO] [launch] robile4: loading Hukoyu-URG04LX-UG01')
        laser_scanner = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('urg_node2'), 'launch'),
            '/urg_node2.launch.py']),
    )

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [
                    FindPackageShare("robile_description"),
                    "gazebo",
                    "gazebo_robile_laserscanner_camera.xacro"
                ]
            ),
            " ",
            "platform_config:=4_wheel_config",
            " ",
            "movable_joints:=False",
        ]
    )

    joint_state_publisher = Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
    )

    robot_state_publisher = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': ParameterValue(robot_description_content, value_type=str)
            }],            
    )  

    rviz_cmd = Node(package='rviz2',
                    namespace='',
                    executable='rviz2',
                    name='rviz2',
                    output='screen'
    )
    
    static_transform = Node(package="tf2_ros",
                                executable="static_transform_publisher",
                                output="screen",
                                arguments=["0", "0", "0", "0", "0",
                                           "0", "base_link", "base_footprint"]
    )

    static_transform_cmd = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='laser_link_node',
        output='screen',
        arguments=["0.45", "0", "0.22", "0", "0",
                    "0", "base_link", "base_laser"]
    )                                
    
    return LaunchDescription([
        laser_scanner,
        smart_wheel_driver,
        static_transform_cmd,
        joint_state_publisher,
        robot_state_publisher,
        rviz_cmd,
        static_transform
    ])

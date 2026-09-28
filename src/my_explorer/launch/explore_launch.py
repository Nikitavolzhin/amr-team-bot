from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_explorer',
            executable='rip_explorer_exe',
            name='rip_explorer_node',
            output='screen',
            parameters=[
                {'use_sim_time': True}
            ]
        )
    ])
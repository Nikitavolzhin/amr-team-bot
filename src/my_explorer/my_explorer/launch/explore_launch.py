from launch import LaunchDescription
#from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_explorer',
            executable='explorer_exe',
            name='explorer_node',
            output='screen',
            parameters=[
                {'use_sim_time': True}
            ]
        )
    ])
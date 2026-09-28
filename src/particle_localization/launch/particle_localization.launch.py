from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    particle_filter = Node(
        package='particle_localization',
        executable='particle_filter',
        name='particle_filter',
        output='screen',
        parameters=[
            {
                'use_sim_time': True
            }
        ],
    )

    return LaunchDescription([
        particle_filter
    ])

import math
import random
from dataclasses import dataclass

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node


from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseArray
from geometry_msgs.msg import Quaternion


@dataclass
class particle:
    x: float
    y: float
    yaw: float
    weight: float


def quat_to_yaw_conversion(q):
    siny = 2 * (q.w * q.z + q.x * q.y)

    cosy = 1 - 2 * (q.y * q.y + q.z * q.z)

    return math.atan2(siny, cosy)


def yaw_to_quaternion(yaw):

    q = Quaternion()

    q.x = 0.0
    q.y = 0.0

    q.z = math.sin(yaw / 2)

    q.w = math.cos(yaw / 2)

    return q


class particle_filter(Node):

    def __init__(self):
        super().__init__("particle_filter_node")

        self.number_of_particles = 10  # can be tunes later

        self.noise_position = 0.20  # can be modified later
        self.noise_yaw = 0.15  # can be modified later


        self.particle_publisher = self.create_publisher(
        
                    PoseArray,
                    "/particle_cloud",
                    10,
                )

        
        self.particles = self.gg_particles(
            initial_x=0.0,
            initial_y=0.0,
            initial_yaw=0.0,
        )

        self.publish_particles()
        

        self.previous_odometry_x = None
        self.previous_odometry_y = None
        self.previous_odometry_yaw = None

        self.odometry_subscription = self.create_subscription(

            Odometry,
            "/odom",
            self.odometry_callback_function,
            10,
        )

       


        self.get_logger().info("Particle filter node started!")





    def gg_particles(self, initial_x, initial_y, initial_yaw):

        particle_list = []

        weight_each = 1.0 / self.number_of_particles

        for i in range(self.number_of_particles):

            self.get_logger().info(f"Creating particle {i}")

            new_particle = particle(

                x=random.gauss(initial_x, self.noise_position),

                y=random.gauss(initial_y, self.noise_position),

                yaw=random.gauss(initial_yaw, self.noise_yaw),

                weight=weight_each,

            )

            particle_list.append(new_particle)

        return particle_list

    def motion_update(self, dx, dy, dyaw):

        for p in self.particles:

            noisy_dx = random.gauss(dx, self.noise_position)
            noisy_dy = random.gauss(dy, self.noise_position)
            noisy_dyaw = random.gauss(dyaw, self.noise_yaw)

            p.x += noisy_dx
            p.y += noisy_dy
            p.yaw += noisy_dyaw

        self.publish_particles()


        

    def publish_particles(self):

        particle_cloud = PoseArray()

        particle_cloud.header.frame_id = "map"
        particle_cloud.header.stamp = self.get_clock().now().to_msg() 

        for p in self.particles:

            pose = Pose()

            pose.position.x = p.x
            pose.position.y = p.y
            pose.position.z = 0.0

            pose.orientation = yaw_to_quaternion(p.yaw)

            particle_cloud.poses.append(pose)

        self.particle_publisher.publish(particle_cloud)
        self.get_logger().info("Publishing particle cloud")


    def odometry_callback_function(self, odometry_message):

        robot_x_position = odometry_message.pose.pose.position.x
        robot_y_position = odometry_message.pose.pose.position.y
        robot_yaw_angle = quat_to_yaw_conversion(
            odometry_message.pose.pose.orientation
        )

        if self.previous_odometry_x is None:

            self.previous_odometry_x = robot_x_position
            self.previous_odometry_y = robot_y_position
            self.previous_odometry_yaw = robot_yaw_angle

            self.get_logger().info("First odometry message received.")

            return

        dx = robot_x_position - self.previous_odometry_x
        dy = robot_y_position - self.previous_odometry_y
        dyaw = robot_yaw_angle - self.previous_odometry_yaw



        
        
        self.motion_update(dx, dy, dyaw)

        self.get_logger().info(
            f"dx={dx:.3f}, dy={dy:.3f}, dyaw={dyaw:.3f}"
        )

        self.previous_odometry_x = robot_x_position
        self.previous_odometry_y = robot_y_position
        self.previous_odometry_yaw = robot_yaw_angle


def main(args=None):

    rclpy.init(args=args)

    filter_node = particle_filter()

    try:
        rclpy.spin(filter_node)

    finally:
        filter_node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
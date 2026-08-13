import math
import random
from dataclasses import dataclass

import rclpy
from geometry_msgs.msg import Pose, PoseArray
from nav_msgs.msg import Odometry
from rclpy.node import Node


@dataclass
class Particle:


    x: float
    y: float
    yaw: float
    weight: float


class teasting_particle_filter(Node):
  

    def __init__(self) -> None:
        super().__init__("testing_particle_filter")

        # Particle settings
        self.number_of_particles = 30
        self.position_noise = 0.20
        self.yaw_noise = 0.15

        # We have particles around the initial pose (0, 0, 0).
        self.particles = self.initialize_particles(
            initial_x=0.0,
            initial_y=0.0,
            initial_yaw=0.0,
        )

        # Publishing as posearray.
        self.particle_publisher = self.create_publisher(
            PoseArray,
            "/particle_cloud",
            10,
        )

        # TIMER
        self.particle_timer = self.create_timer(
            0.5,
            self.publish_particles,
        )

        # ODOM SUB
        self.odom_sub = self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            10,
        )

        self.get_logger().info(
            f"Created {len(self.particles)} particles"
        )

     
        for particle in self.particles[:3]:
            self.get_logger().info(f"Particle: x={particle.x:.3f}, " f"y={particle.y:.3f}, "f"yaw={particle.yaw:.3f}, "f"weight={particle.weight:.4f}")

        total_weight = sum(particle.weight for particle in self.particles)

        self.get_logger().info(f"Total particle weight: {total_weight:.3f}")

        self.get_logger().info("Node started — ALLES GUT " "(NICHT KAPUTT SO FAR :) )")

    def initialize_particles(self,initial_x: float,initial_y: float,initial_yaw: float,) -> list[Particle]:
        

        if self.number_of_particles <= 0:
            raise ValueError("Number of particles must be greater than zero")

        particles: list[Particle] = []

      
        uniform_weight = 1.0 / self.number_of_particles

        for _ in range(self.number_of_particles):
            particle_x = random.gauss(
                initial_x,
                self.position_noise,
            )

            particle_y = random.gauss(
                initial_y,
                self.position_noise,
            )

            particle_yaw = random.gauss(
                initial_yaw,
                self.yaw_noise,
            )

            particle = Particle(
                x=particle_x,
                y=particle_y,
                yaw=particle_yaw,
                weight=uniform_weight,
            )

            particles.append(particle)

        return particles

    def publish_particles(self) -> None:
   

        particle_cloud = PoseArray()

        particle_cloud.header.stamp = (
            self.get_clock().now().to_msg()
        )
        particle_cloud.header.frame_id = "odom"

        for particle in self.particles:
            particle_pose = Pose()

            particle_pose.position.x = particle.x
            particle_pose.position.y = particle.y
            particle_pose.position.z = 0.0

            
            particle_pose.orientation.z = math.sin(
                particle.yaw / 2.0
            )
            particle_pose.orientation.w = math.cos(
                particle.yaw / 2.0
            )

            particle_cloud.poses.append(particle_pose)

        self.particle_publisher.publish(particle_cloud)

    def odom_callback(self, msg: Odometry) -> None:


        position = msg.pose.pose.position

        self.get_logger().info(
            f"Current odometry position: "
            f"x={position.x:.3f}, y={position.y:.3f}"
        )


def main(args=None) -> None:
    rclpy.init(args=args)

    node = teasting_particle_filter()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


# GGWP :3
if __name__ == "__main__":
    main()
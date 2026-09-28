import rclpy
from rclpy.node import Node

import numpy as np

from nav_msgs.msg import OccupancyGrid
from nav_msgs.msg import Odometry


class ParticleFilter(Node):

    def __init__(self):
        super().__init__('mcl_particle_filter')

        self.num_particles = 500

        self.particles = np.zeros((self.num_particles, 3))
        self.weights = np.ones(self.num_particles) / self.num_particles




        self.map_received = False
        self.particles_initialized = False
        self.map_resolution = None
        self.map_width = None
        self.map_height = None
        self.map_origin_x = None
        self.map_origin_y = None
        self.map_data = None



        self.map_subscriber = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10
        )
        self.previous_odom = None

        self.odom_subscriber = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.get_logger().info(
            f'Particle Filter started with {self.num_particles} particles'
        )



    def map_callback(self, msg):

   
        self.map_resolution = msg.info.resolution
        self.map_width = msg.info.width
        self.map_height = msg.info.height

        self.map_origin_x = msg.info.origin.position.x
        self.map_origin_y = msg.info.origin.position.y


        self.map_data = np.array(msg.data)

        self.map_received = True

        self.get_logger().info(
            f'Map received: '
            f'{self.map_width} x {self.map_height}, '
            f'resolution={self.map_resolution}'
        )


        if not self.particles_initialized:
            self.initialize_particles()



    def initialize_particles(self):

        if not self.map_received:
            return

        free_cells = np.where(self.map_data == 0)[0]

        if len(free_cells) == 0:
            self.get_logger().error('No free cells found in map!')
            return


        selected_cells = np.random.choice(
            free_cells,
            self.num_particles
        )

        for i, cell in enumerate(selected_cells):


            map_y, map_x = np.unravel_index(cell,(self.map_height, self.map_width))

 
            self.particles[i, 0] = (self.map_origin_x +(map_x + 0.5) * self.map_resolution)

            self.particles[i, 1] = (self.map_origin_y +(map_y + 0.5) * self.map_resolution)


            self.particles[i, 2] = np.random.uniform(-np.pi,np.pi)

        self.get_logger().info('Particles initialized in free space.')

        self.particles_initialized = True



    def odom_callback(self, msg):

        current_x = msg.pose.pose.position.x
        current_y = msg.pose.pose.position.y

        current_q = msg.pose.pose.orientation


        current_theta = self.quaternion_to_yaw(
            current_q.x,
            current_q.y,
            current_q.z,
            current_q.w
        )


        if self.previous_odom is None:

            self.previous_odom = (
                current_x,
                current_y,
                current_theta
            )

            return

        previous_x = self.previous_odom[0]
        previous_y = self.previous_odom[1]
        previous_theta = self.previous_odom[2]


        delta_x = current_x - previous_x
        delta_y = current_y - previous_y
        delta_theta = self.normalize_angle(current_theta - previous_theta)


        self.motion_update(delta_x,delta_y,delta_theta)


        self.previous_odom = (current_x,current_y,current_theta)

    def motion_update(
        self,
        delta_x,
        delta_y,
        delta_theta
    ):


        noise_x = np.random.normal(
            0.0,
            0.02,
            self.num_particles
        )

        noise_y = np.random.normal(
            0.0,
            0.02,
            self.num_particles
        )

        noise_theta = np.random.normal(
            0.0,
            0.02,
            self.num_particles
        )

        self.particles[:, 0] += delta_x + noise_x
        self.particles[:, 1] += delta_y + noise_y

        self.particles[:, 2] += (
            delta_theta + noise_theta
        )


        self.particles[:, 2] = (
            self.particles[:, 2] + np.pi
        ) % (2 * np.pi) - np.pi



    def quaternion_to_yaw(
        self,
        x,
        y,
        z,
        w
    ):

        sin_yaw = 2.0 * (w * z + x * y)

        cos_yaw = 1.0 - 2.0 * (y * y + z * z)

        return np.arctan2(
            sin_yaw,
            cos_yaw
        )



    def normalize_angle(self, angle):

        return (
            angle + np.pi
        ) % (2 * np.pi) - np.pi


def main(args=None):

    rclpy.init(args=args)

    node = ParticleFilter()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
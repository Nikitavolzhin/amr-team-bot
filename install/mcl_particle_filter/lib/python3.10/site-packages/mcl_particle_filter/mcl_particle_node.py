import rclpy
from rclpy.node import Node


class ParticleFilter(Node):

    def __init__(self):
        super().__init__('particle_filter')

        self.get_logger().info('Particle Filter started!')


def main(args=None):
    rclpy.init(args=args)

    node = ParticleFilter()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

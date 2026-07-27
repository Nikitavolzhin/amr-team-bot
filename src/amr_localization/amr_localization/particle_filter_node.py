import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.node import Node


class ParticleFilterNode(Node):
    

    def __init__(self) -> None:
        super().__init__("particle_filter_localization")

        self.pose_publisher = self.create_publisher(
            PoseWithCovarianceStamped,
            "/estimated_pose",
            10,
        )

 
        self.timer = self.create_timer(
            1.0,
            self.publish_test_pose,
        )

        self.get_logger().info(
            "Particle filter localization node started- ALLES GUT (NICHT KAPUT xd)"
        )

    def publish_test_pose(self) -> None:
       
        message = PoseWithCovarianceStamped()
        message.header.stamp = self.get_clock().now().to_msg()

        message.header.frame_id = "odom"
        # Fixed position - ; for testing
        message.pose.pose.position.x = 0.0
        message.pose.pose.position.y = 0.0
        message.pose.pose.position.z = 0.0
        
        message.pose.pose.orientation.x = 0.0
        message.pose.pose.orientation.y = 0.0
        message.pose.pose.orientation.z = 0.0
        message.pose.pose.orientation.w = 1.0

        self.pose_publisher.publish(message)


def main(args=None) -> None:
    """Initialize ROS 2 and run the node."""
    rclpy.init(args=args)

    node = ParticleFilterNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class test_particle_filter(Node):
    

    def __init__(self) -> None:
        super().__init__("testing_particle_filter")


        self.odom_sub = self.create_subscription(Odometry, "/odom", self.odom_call, 10,)

        self.get_logger().info("NODE HAS STARTED ALLES GUT (NICHT KAPUT SO FAR :) )")

    def odom_call(self, msg: Odometry) -> None:
        self.position_of_x = msg.pose.pose.position.x
        self.position_of_y = msg.pose.pose.position.y

        self.get_logger().info(f"CURRENT POSITION -> : x={self.position_of_x:.3f}, y={self.position_of_y:.3f}")
   


def main(args=None):
    rclpy.init(args=args)

    node = test_particle_filter()

    
    rclpy.spin(node)

    node.destroy_node()


    rclpy.shutdown()

#GGWP :3
if __name__ == '__main__':
    main()
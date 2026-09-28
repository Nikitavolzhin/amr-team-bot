import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist

class CmdVelocityPublisher(Node):

    def __init__(self):
        super().__init__('circular_motion_publisher')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        timer_period = 0.5  # seconds
        # creating a timer to publish the velocity at a fixed rate
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        """
        set the linear and angular velocity of the robot according to required behavior
        """
        ## Example: 
        # linear velocity in 'x' direction can be set as: "msg.linear.x = 0.5"
        msg.linear.x = 0.5 # m/s; this is example code, you need to change this section according to the required behavior

        ### YOUR CODE HERE (plese feel free to change the above example code)

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    cmd_velocity_publisher = CmdVelocityPublisher()

    rclpy.spin(cmd_velocity_publisher)

    cmd_velocity_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
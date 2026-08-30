import rclpy
from rclpy.node import Node

from tf_transformations import euler_from_quaternion
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import Odometry, Path
import numpy as np
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
#NB: maually from terminal we obtained the following
# frame_id: base_link
# child_frame_id: base_laser_front_link
# transform: translation: x: 0.45 y: 0.0 z: 0.22
# rotation: x: 0.0 y: 0.0 z: 0.0 w: 1.0

# Z-axis does not affect, no rotation in transformtaion, no tranlation along y axis => change only x

class Potential(Node):
    def __init__(self):
        super().__init__('potential_node')
        path_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )

        self.path_subscription = self.create_subscription(
            Path,
            '/wavefront_path',
            self.path_reader,
            path_qos
        )
        self.cart_data = None
        self.path = None
        self.buffer = 0.6
        self.k_a = 1.3 #1.3
        self.k_r = -0.008 #-0.005
        self.ro = 3.0 # 3.0
        self.x = 0.0
        self.y = 0.0
        self.current_goal = 0
        '''
        self.goals = [np.array([2.0, -2.0]),
                      np.array([3.0, -1.0]),
                      np.array([5.0, -2.0]),
                      np.array([6.0, -4.0]),
                      np.array([5.0, -2.0]),
                      # np.array([6.0, -2.0]),
                      np.array([3.0, -1.0]),
                      np.array([3.0, 1.0]),
                      np.array([4.0, 1.5]),
                      np.array([0.0, 1.0]),
                      np.array([0.0, 0.0]),
                      ]
        '''
        self.goal_orientation = -1.0
        self.angle = 0.0
        self.subscriber_odom = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_data_reader,
            10
        )
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.listener_callback,
            10
        )
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        time_period = 0.5
        self.timer = self.create_timer(time_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = Twist()
        R = np.array([
            [np.cos(self.angle), np.sin(self.angle)],
            [-np.sin(self.angle), np.cos(self.angle)]
        ])
        v = R @ (np.array([self.x, self.y]) - self.path[self.current_goal])
        v = -self.k_a * v/np.linalg.norm(v)
        if self.cart_data is None:
            return
        for i in self.cart_data:
            denom = np.linalg.norm(i)
            if denom != 0 and denom < self.ro:
                v_rep = self.k_r * (1/denom - 1/self.ro) * (1/denom ** 2)* i/denom
                v += v_rep

        angle_to_goal = np.arctan2(v[1], v[0])

        msg.angular.z = self.normalize_angle(angle_to_goal)
        msg.linear.x = v[0]/3
        if np.linalg.norm(np.array([self.x, self.y]) - self.path[self.current_goal]) < self.buffer:
            msg.linear.x = 0.0
            #if abs(self.angle - self.goal_orientation) > 0.15:
            #    self.get_logger().info(f"Changing orientation")
            #    msg.angular.z = self.goal_orientation - self.angle
            #else:
            msg.angular.z = 0.0
            self.get_logger().info(f"goal achieved! Current position: {self.x, self.y}; Goal: {self.path[self.current_goal]}")
            if len(self.path)-1 > self.current_goal:
                self.current_goal+=1
        self.publisher.publish(msg)
    
    def path_reader(self, msg):
        self.path = list()
        for pose in msg.poses:
            self.path.append([pose.pose.position.x, pose.pose.position.y])
        if not self.path:
            self.get_logger().warning('Received an empty path')
            return
        self.get_logger().info(
            f'Received path: {self.path}'
        )
        
    def odom_data_reader(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        _, _, self.angle = euler_from_quaternion([q.x, q.y, q.z, q.w])

    def listener_callback(self, msg):
        ranges = np.array(msg.ranges)
        idx = np.array([ranges <= msg.range_max]) * np.array([ranges >= msg.range_min])
        #self.ro = msg.range_max
        idx = idx.reshape(-1)
        angles = msg.angle_min + np.arange(len(ranges))*msg.angle_increment
        angles = angles[idx]
        ranges = ranges[idx]
        polar_data = np.vstack([ranges, angles]).T
        cart_data = self.np_polar2cart(polar_data)
        self.cart_data = cart_data

    # function from HW 2
    def np_polar2cart(self, np_polar):
        x = np_polar[:, 0] * np.cos(np_polar[:,1]) + 0.45 #!!! change of frame
        y = np_polar[:, 0] * np.sin(np_polar[:,1])
        np_cart = np.vstack([x, y]).T
        return np_cart

    def normalize_angle(self, angle):
        while angle > np.pi:
            angle -= 2.0 * np.pi
        while angle < -np.pi:
            angle += 2.0 * np.pi
        return angle

def main(args=None):
    rclpy.init(args=args)

    potential = Potential()

    rclpy.spin(potential)
    potential.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
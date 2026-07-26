import rclpy
from rclpy.node import Node

import sys

from tf_transformations import euler_from_quaternion
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import Odometry, OccupancyGrid
import numpy as np
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped

class Wave(Node):
    def __init__(self):
        super().__init__('wavefront_node')
        goal_x = float(sys.argv[1])
        goal_y = float(sys.argv[2])
        self.goal = [goal_x, goal_y] #e.g. 5.0 -4.0 is valid
        self.map = None
        odom_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE
        )

        self.subscriber_odom = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_data_reader,
            odom_qos
        )

        self.x = None
        self.y = None
        self.odom_received = False

        map_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )

        self.subscriber_map = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_reader,
            map_qos
        )
        self.planning_timer = self.create_timer(
             0.2,
             self.planning
        )

        path_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )

        self.path_publisher = self.create_publisher(
            Path,
            '/wavefront_path',
            path_qos
        )
        
    def map_reader(self, msg):
        self.resolution = msg.info.resolution
        self.width = msg.info.width
        self.height = msg.info.height
        self.map = np.array(msg.data).reshape(int(self.height), int(self.width))
        self.origin = msg.info.origin.position
        self.get_logger().info(f'W: {self.width}; H: {self.height}, resolution: {self.resolution}, or: {self.origin}')
        self.get_logger().info(f'map: {np.unique(self.map)}') #0 free, 100 occupied

        self.wave_map = self.wave_map = np.full((self.height, self.width), -1, dtype=np.int32)


    def planning(self):
        if self.map is None:
            self.get_logger().info(
                'Waiting for map...',
                throttle_duration_sec=2.0
            )
            return

        if self.x is None:
            self.get_logger().info(
                'Waiting for odometry...',
                throttle_duration_sec=2.0
            )
            return
        init_idx = self.to_grid_idx(self.x, self.y)
        goal_idx = self.to_grid_idx(self.goal[0], self.goal[1])
        # to do: check if both goal and init have 0 values on the grid
        self.get_logger().info(
            f'idx of init({self.x, self.y}): {init_idx} and value: {self.map[init_idx[0]][init_idx[1]]}')
        self.get_logger().info(f'idx of goal({self.goal}): {goal_idx} and value: {self.map[goal_idx[0]][goal_idx[1]]}')
        self.wave_map[init_idx[0]][init_idx[1]] = 0
        queue = [init_idx]
        success = 0
        while queue:

            cell = queue.pop(0)
            # self.get_logger().info(f'on: {cell}')
            if goal_idx[0] == cell[0] and goal_idx[1] == cell[1]:
                self.get_logger().info(f'goal found')
                success = 1
                break
            current_value = self.wave_map[cell[0]][cell[1]]
            if cell[0] + 1 < self.height and self.map[cell[0] + 1][cell[1]] == 0 and self.wave_map[cell[0] + 1][
                cell[1]] == -1:
                self.wave_map[cell[0] + 1][cell[1]] = current_value + 1
                queue.append([cell[0] + 1, cell[1]])
            if cell[0] - 1 > -1 and self.map[cell[0] - 1][cell[1]] == 0 and self.wave_map[cell[0] - 1][cell[1]] == -1:
                self.wave_map[cell[0] - 1][cell[1]] = current_value + 1
                queue.append([cell[0] - 1, cell[1]])
            if cell[1] + 1 < self.width and self.map[cell[0]][cell[1] + 1] == 0 and self.wave_map[cell[0]][
                cell[1] + 1] == -1:
                self.wave_map[cell[0]][cell[1] + 1] = current_value + 1
                queue.append([cell[0], cell[1] + 1])
            if cell[1] - 1 > -1 and self.map[cell[0]][cell[1] - 1] == 0 and self.wave_map[cell[0]][cell[1] - 1] == -1:
                self.wave_map[cell[0]][cell[1] - 1] = current_value + 1
                queue.append([cell[0], cell[1] - 1])

        if success:
            path = [goal_idx]
            while True:
                current = path[-1]

                current_value = self.wave_map[current[0]][current[1]]
                if current_value == 0:
                    break
                if current[0] + 1 < self.height and self.wave_map[current[0] + 1][current[1]] == current_value - 1:
                    path.append([current[0] + 1, current[1]])
                elif current[0] - 1 > -1 and self.wave_map[current[0] - 1][current[1]] == current_value - 1:
                    path.append([current[0] - 1, current[1]])
                elif current[1] + 1 < self.width and self.wave_map[current[0]][current[1] + 1] == current_value - 1:
                    path.append([current[0], current[1] + 1])
                elif current[1] - 1 > -1 and self.wave_map[current[0]][current[1] - 1] == current_value - 1:
                    path.append([current[0], current[1] - 1])

            self.path_idx = path[::-10]
            self.path = list()
            for i in range(len(self.path_idx)):
                self.path.append(self.to_coordinate(self.path_idx[i][0], self.path_idx[i][1]))
            self.get_logger().info(f'path: {self.path}')
            self.publish_path(self.path)
            self.planning_timer.cancel()

    def to_grid_idx(self, x, y):
        col = int((x - self.origin.x) / self.resolution)
        row = int((y - self.origin.y) / self.resolution)

        return row, col

    def to_coordinate(self, row, col):
        x = round(self.resolution * col + self.origin.x, 3)
        y = round(self.resolution * row + self.origin.y, 3)

        return x, y

    def odom_data_reader(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation

        _, _, self.angle = euler_from_quaternion([q.x, q.y, q.z, q.w])
        self.odom_received = True

    def publish_path(self, path):
        path_msg = Path()
        path_msg.header.stamp = self.get_clock().now().to_msg()
        path_msg.header.frame_id = 'map'

        for x, y in path:
            pose = PoseStamped()
            pose.header.stamp = path_msg.header.stamp
            pose.header.frame_id = 'map'
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.position.z = 0.0
            pose.pose.orientation.x = 0.0
            pose.pose.orientation.y = 0.0
            pose.pose.orientation.z = 0.0
            pose.pose.orientation.w = 1.0
            path_msg.poses.append(pose)

        self.path_publisher.publish(path_msg)
        self.get_logger().info(
            f'Published path containing {len(path_msg.poses)} poses'
        )

def main(args=None):
    rclpy.init(args=args)

    wave = Wave()

    rclpy.spin(wave)
    wave.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

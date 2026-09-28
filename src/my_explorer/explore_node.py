import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import OccupancyGrid
from visualization_msgs.msg import Marker
from action_msgs.msg import GoalStatus
from tf2_ros import Buffer, TransformListener
import numpy as np
import cv2
import math

class ExplorationNode(Node):
    def __init__(self):
        super().__init__('exploration_node')
        
        # --- FIX START ---
        # Check if the parameter is already declared by the system/environment
        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', True)
        # --- FIX END ---

        self.map_sub = self.create_subscription(OccupancyGrid, 'map', self.map_callback, 10)
        self.marker_pub = self.create_publisher(Marker, 'next_goal_marker', 10)
        
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        self.map_data = None
        self.is_moving = False
        self.blacklist = [] 
        self.current_goal = None
        
        # Timer for decision making
        self.create_timer(3.0, self.exploration_step) 
        self.get_logger().info("--- Exploration Node Started ---")

    def map_callback(self, msg):
        self.map_data = msg

    def get_robot_pose(self):
        try:
            # Look up transform from map to base_link
            now = rclpy.time.Time()
            t = self.tf_buffer.lookup_transform('map', 'base_link', now, rclpy.duration.Duration(seconds=1.0))
            return (t.transform.translation.x, t.transform.translation.y)
        except Exception as e:
            self.get_logger().error(f"Could not get robot pose: {e}")
            return None

    def exploration_step(self):
        if self.map_data is None:
            self.get_logger().info("Waiting for map...")
            return
        
        if self.is_moving:
            return
        
        robot_pose = self.get_robot_pose()
        if not robot_pose:
            return

        self.get_logger().info("Analyzing map for frontiers...")
        goal = self.find_best_frontier(self.map_data, robot_pose)
        
        if goal:
            self.send_goal(goal)
        else:
            self.get_logger().warn("No reachable frontiers found.")

    def find_best_frontier(self, msg, robot_pose):
        width = msg.info.width
        height = msg.info.height
        resolution = msg.info.resolution
        origin_x = msg.info.origin.position.x
        origin_y = msg.info.origin.position.y
        
        # Convert map to numpy
        data = np.array(msg.data).reshape((height, width))
        
        # 1. Create masks
        unknown = (data == -1).astype(np.uint8) * 255
        free = (data == 0).astype(np.uint8) * 255
        obstacles = (data > 50).astype(np.uint8) * 255

        # 2. Dilate obstacles to avoid spawning goals too close to walls
        kernel_size = max(1, int(0.3 / resolution))
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        danger_zone = cv2.dilate(obstacles, kernel)
        
        # 3. Find frontiers (areas where free space meets unknown space)
        free_dilated = cv2.dilate(free, np.ones((3,3), np.uint8))
        frontier_mask = cv2.bitwise_and(free_dilated, unknown)
        frontier_mask = cv2.bitwise_and(frontier_mask, cv2.bitwise_not(danger_zone))
        
        contours, _ = cv2.findContours(frontier_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        frontiers = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 2: continue # Ignore tiny noise
                
            M = cv2.moments(cnt)
            if M['m00'] == 0: continue
            
            px, py = M['m10']/M['m00'], M['m01']/M['m00']
            gx = (px * resolution) + origin_x
            gy = (py * resolution) + origin_y
            
            dist = math.sqrt((gx - robot_pose[0])**2 + (gy - robot_pose[1])**2)
            
            # Check if this area is blacklisted
            if any(math.sqrt((gx-b[0])**2 + (gy-b[1])**2) < 0.8 for b in self.blacklist):
                continue

            # Scoring: larger area is better, closer distance is better
            score = area / (dist + 0.5)
            
            if dist > 0.5: 
                frontiers.append(((gx, gy), score))

        if not frontiers:
            return None

        # Sort by best score
        frontiers.sort(key=lambda x: x[1], reverse=True) 
        return frontiers[0][0]

    def send_goal(self, coords):
        if not self.nav_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().error("NavigateToPose action server not available!")
            return

        self.is_moving = True
        self.current_goal = coords
        self.publish_marker(coords)
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = coords[0]
        goal_msg.pose.pose.position.y = coords[1]
        goal_msg.pose.pose.orientation.w = 1.0
        
        self.get_logger().info(f"Sending Goal: {coords[0]:.2f}, {coords[1]:.2f}")
        
        send_goal_future = self.nav_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal REJECTED by Nav2 stack.")
            self.blacklist.append(self.current_goal)
            self.is_moving = False
            return

        self.get_logger().info("Goal ACCEPTED, moving...")
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        status = future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Goal REACHED.")
        else:
            self.get_logger().warn(f"Goal FAILED with status: {status}. Adding to blacklist.")
            if self.current_goal:
                self.blacklist.append(self.current_goal)
        
        self.is_moving = False

    def publish_marker(self, coords):
        m = Marker()
        m.header.frame_id = "map"
        m.header.stamp = self.get_clock().now().to_msg()
        m.id = 0
        m.type = Marker.SPHERE
        m.pose.position.x = coords[0]
        m.pose.position.y = coords[1]
        m.pose.position.z = 0.5
        m.scale.x, m.scale.y, m.scale.z = 0.3, 0.3, 0.3
        m.color.a, m.color.r, m.color.g = 1.0, 1.0, 0.0 # Yellow marker
        self.marker_pub.publish(m)

def main():
    rclpy.init()
    node = ExplorationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
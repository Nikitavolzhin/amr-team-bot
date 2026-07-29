import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import OccupancyGrid
from visualization_msgs.msg import Marker
from action_msgs.msg import GoalStatus
from tf2_ros import Buffer, TransformListener
import numpy as np
import math

class ExplorationNode(Node):
    def __init__(self):
        super().__init__('exploration_node')
        
        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', True)

        self.map_sub = self.create_subscription(OccupancyGrid, 'map', self.map_callback, 1)
        self.marker_pub = self.create_publisher(Marker, 'next_goal_marker', 1)
        
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        self.map_data = None
        self.is_moving = False
        self.blacklist = [] 
        self.current_goal_coords = None
        
        # Anti-spin metrics
        self.spin_recovery_counter = 0

        # Run evaluation every 3.0 seconds for snappier responses
        self.create_timer(3.0, self.exploration_step) 
        self.get_logger().info("--- Narrow Maze Wall Explorer Engaged ---")

    def map_callback(self, msg):
        self.map_data = msg

    def get_robot_pose(self):
        try:
            now = rclpy.time.Time()
            t = self.tf_buffer.lookup_transform('map', 'base_link', now, rclpy.duration.Duration(seconds=0.2))
            return (t.transform.translation.x, t.transform.translation.y)
        except Exception:
            return None

    def shift_array(self, arr, dx, dy):
        res = np.roll(np.roll(arr, dx, axis=0), dy, axis=1)
        if dx > 0: res[:dx, :] = False
        elif dx < 0: res[dx:, :] = False
        if dy > 0: res[:, :dy] = False
        elif dy < 0: res[:, dy:] = False
        return res

    def exploration_step(self):
        if self.map_data is None or self.is_moving:
            return
        
        robot_pose = self.get_robot_pose()
        if not robot_pose:
            return

        # Try searching with standard safety buffers first, then squeeze if choked
        goal = self.find_best_frontier(self.map_data, robot_pose, safety_radius=0.55)
        
        if not goal:
            self.get_logger().warn("Hallway narrowness detected. Squeezing inflation layers to find doorways...")
            goal = self.find_best_frontier(self.map_data, robot_pose, safety_radius=0.22)

        if goal:
            self.spin_recovery_counter = 0
            self.send_goal(goal, force_heading=True)
        else:
            # HARD ESCAPE: Force translation along the absolute Map X-axis to break local costmap traps
            self.spin_recovery_counter += 1
            direction = 1.0 if (self.spin_recovery_counter % 2 == 0) else -1.0
            escape_x = robot_pose[0] + (direction * 0.8)
            escape_y = robot_pose[1]
            
            self.get_logger().error(f"🚨 Blinded by walls! Forcing absolute translation to map coordinate: ({escape_x:.2f}, {escape_y:.2f})")
            self.send_goal((escape_x, escape_y), force_heading=False)

    def find_best_frontier(self, msg, robot_pose, safety_radius):
        width, height = msg.info.width, msg.info.height
        res, ox, oy = msg.info.resolution, msg.info.origin.position.x, msg.info.origin.position.y
        
        data = np.array(msg.data).reshape((height, width))
        
        unknown = (data == -1)
        free = (data == 0)
        occupied = (data > 40)

        # Dynamic safety buffer based on function argument
        steps = max(1, int(safety_radius / res)) 
        danger_zone = occupied.copy()
        for i in range(-steps, steps + 1):
            if i == 0: continue
            danger_zone |= self.shift_array(occupied, i, 0)
            danger_zone |= self.shift_array(occupied, 0, i)

        # Look for free cells adjacent to unmapped territory
        unknown_dilated = self.shift_array(unknown, 1, 0) | self.shift_array(unknown, -1, 0) | \
                          self.shift_array(unknown, 0, 1) | self.shift_array(unknown, 0, -1)
        
        frontier_mask = free & unknown_dilated & ~danger_zone
        
        rows, cols = np.where(frontier_mask)
        if len(rows) == 0:
            return None

        best_point = None
        max_score = -1e9
        
        sample_indices = np.linspace(0, len(rows)-1, min(150, len(rows)), dtype=int)
        
        for idx in sample_indices:
            r, c = rows[idx], cols[idx]
            gx = (c * res) + ox
            gy = (r * res) + oy
            
            dist = math.sqrt((gx - robot_pose[0])**2 + (gy - robot_pose[1])**2)
            
            # Allow closer targets when navigating tight doorways
            if dist < 0.6: continue
            if any(math.sqrt((gx-b[0])**2 + (gy-b[1])**2) < 0.7 for b in self.blacklist): continue

            r_start, r_end = max(0, r-3), min(height, r+4)
            c_start, c_end = max(0, c-3), min(width, c+4)
            density = np.sum(frontier_mask[r_start:r_end, c_start:c_end])
            
            # Balanced Scoring Formula
            score = (density * 20.0) - dist
            
            if score > max_score:
                max_score = score
                # Pull back target slightly so it resides strictly within the known open hallway
                angle = math.atan2(robot_pose[1] - gy, robot_pose[0] - gx)
                target_x = gx + math.cos(angle) * 0.25
                target_y = gy + math.sin(angle) * 0.25
                best_point = (target_x, target_y)

        return best_point

    def send_goal(self, coords, force_heading=True):
        if not self.nav_client.wait_for_server(timeout_sec=1.0):
            return

        self.is_moving = True
        self.current_goal_coords = coords
        self.publish_marker(coords)
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x, goal_msg.pose.pose.position.y = coords[0], coords[1]
        
        robot_pose = self.get_robot_pose()
        if robot_pose and force_heading:
            # Face the room opening normally
            yaw = math.atan2(coords[1] - robot_pose[1], coords[0] - robot_pose[0])
            goal_msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
            goal_msg.pose.pose.orientation.w = math.cos(yaw / 2.0)
        else:
            # Use neutral orientation during recoveries to stop local planner yaw-spinning loops
            goal_msg.pose.pose.orientation.w = 1.0
        
        send_goal_future = self.nav_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            if self.current_goal_coords:
                self.blacklist.append(self.current_goal_coords)
            self.is_moving = False
            return
        
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        status = future.result().status
        if status != GoalStatus.STATUS_SUCCEEDED:
            if self.current_goal_coords and len(self.blacklist) < 300: 
                self.blacklist.append(self.current_goal_coords)
        
        self.is_moving = False
        self.current_goal_coords = None

    def publish_marker(self, coords):
        m = Marker()
        m.header.frame_id, m.header.stamp = "map", self.get_clock().now().to_msg()
        m.type, m.id = Marker.SPHERE, 0
        m.pose.position.x, m.pose.position.y, m.pose.position.z = coords[0], coords[1], 0.4
        m.scale.x = m.scale.y = m.scale.z = 0.3
        m.color.a, m.color.r, m.color.g, m.color.b = 1.0, 0.0, 0.0, 1.0 # Blue Destination Marker
        self.marker_pub.publish(m)

def main():
    rclpy.init()
    node = ExplorationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

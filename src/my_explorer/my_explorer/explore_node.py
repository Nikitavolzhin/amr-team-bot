import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import OccupancyGrid
from tf2_ros import Buffer, TransformListener
import numpy as np
import math

class SlamExplorer(Node):
    def __init__(self):
        super().__init__('slam_explorer_node')

        # Prevent Parameter errors
        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', True)

        # Map and TF
        self.map_sub = self.create_subscription(OccupancyGrid, 'map', self.map_callback, 10)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Action Client
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Exploration State
        self.map_data = None
        self.blacklist = []
        self.is_navigating = False
        self.curr_goal_coords = (0.0, 0.0)
        
        # --- SLAM TUNING ---
        self.SCAN_RATE = 1.0          # Seconds between planning cycles
        self.UTILITY_RADIUS = 4       # How far to look for unknown pixels (in pixels)
        self.MIN_FRONTIER_DIST = 1.0  # Minimum meters from robot
        self.WALL_SAFETY_PX = 3       # Buffer from obstacles
        self.MOMENTUM_DIST = 0.6      # Distance to target before replanning
        # -------------------
        
        self.timer = self.create_timer(self.SCAN_RATE, self.exploration_loop)
        self.get_logger().info("Active SLAM Explorer Started. Priority: Max Information Gain.")

    def map_callback(self, msg):
        self.map_data = msg

    def get_robot_pose(self):
        try:
            t = self.tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time())
            return (t.transform.translation.x, t.transform.translation.y)
        except Exception:
            return None

    def exploration_loop(self):
        pose = self.get_robot_pose()
        if pose is None or self.map_data is None:
            return

        # Momentum/Continuity check
        if self.is_navigating:
            dist_to_goal = math.sqrt((pose[0] - self.curr_goal_coords[0])**2 + 
                                     (pose[1] - self.curr_goal_coords[1])**2)
            if dist_to_goal > self.MOMENTUM_DIST:
                return 

        # SLAM Method: Find the point with the highest information gain
        best_goal = self.find_best_utility_target(pose[0], pose[1])
        
        if best_goal:
            self.send_nav_goal(best_goal)

    def find_best_utility_target(self, rx, ry):
        info = self.map_data.info
        grid = np.array(self.map_data.data).reshape((info.height, info.width))
        
        # Find all candidate frontier points
        y_indices, x_indices = np.where(grid == 0)
        
        # Sample points to keep WSL2 fast
        sample_step = 10 
        indices = np.arange(0, len(x_indices), sample_step)
        np.random.shuffle(indices)

        best_target = None
        max_utility = -1

        # Check the first 50 valid candidates to find the best "Information Gain"
        candidates_checked = 0
        for i in indices:
            if candidates_checked > 50: break
            
            x, y = x_indices[i], y_indices[i]

            # 1. Is it a frontier? (Check if touching -1)
            sub = grid[max(0, y-1):y+2, max(0, x-1):x+2]
            if -1 not in sub: continue
            
            # 2. Safety Check (Wall distance)
            safety_zone = grid[max(0, y-self.WALL_SAFETY_PX):y+self.WALL_SAFETY_PX+1, 
                               max(0, x-self.WALL_SAFETY_PX):x+self.WALL_SAFETY_PX+1]
            if np.any(safety_zone > 50): continue

            # 3. Distance Check
            wx = x * info.resolution + info.origin.position.x
            wy = y * info.resolution + info.origin.position.y
            dist = math.sqrt((wx - rx)**2 + (wy - ry)**2)
            if dist < self.MIN_FRONTIER_DIST: continue

            # 4. SLAM Utility: Count unknown pixels in a radius
            # Higher utility = revealing more of the map
            utility_zone = grid[max(0, y-self.UTILITY_RADIUS):y+self.UTILITY_RADIUS+1, 
                                max(0, x-self.UTILITY_RADIUS):x+self.UTILITY_RADIUS+1]
            utility = np.count_nonzero(utility_zone == -1)

            if utility > max_utility:
                # Blacklist check
                if not any(math.sqrt((wx-b[0])**2 + (wy-b[1])**2) < 0.8 for b in self.blacklist):
                    max_utility = utility
                    best_target = (wx, wy)
            
            candidates_checked += 1

        return best_target

    def send_nav_goal(self, goal_data):
        wx, wy = goal_data
        if not self.nav_client.wait_for_server(timeout_sec=1.0): return

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = wx
        goal_msg.pose.pose.position.y = wy
        goal_msg.pose.pose.orientation.w = 1.0 

        self.get_logger().info(f"New SLAM Goal: ({wx:.2f}, {wy:.2f})")
        
        self.is_navigating = True
        self.curr_goal_coords = (wx, wy)
        
        future = self.nav_client.send_goal_async(goal_msg)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.is_navigating = False
            return
        goal_handle.get_result_async().add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        status = future.result().status
        if status != 4: # If goal failed
            self.blacklist.append(self.curr_goal_coords)
            if len(self.blacklist) > 15: self.blacklist.pop(0)
        self.is_navigating = False

def main():
    rclpy.init()
    node = SlamExplorer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
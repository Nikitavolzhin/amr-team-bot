import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.duration import Duration
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import OccupancyGrid
from tf2_ros import Buffer, TransformListener
import numpy as np
import math
import time

class RipExplorer(Node):
    def __init__(self):
        super().__init__('rip_explorer_node')

        # FIX: Safety check for parameter declaration
        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', True)

        # Map and TF
        self.map_sub = self.create_subscription(OccupancyGrid, 'map', self.map_callback, 10)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Action Client
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # State
        self.map_data = None
        self.blacklist = []
        self.last_pos = (0.0, 0.0)
        
        # --- AGGRESSIVE TUNING ---
        self.SCAN_RATE = 0.8          # "Rip" a new goal every 0.8 seconds
        self.MIN_FRONTIER_DIST = 1.0   # How far away the next target must be
        self.WALL_SAFETY_PX = 1        # Keep walls thin (1 pixel buffer)
        # -------------------------
        
        self.timer = self.create_timer(self.SCAN_RATE, self.exploration_loop)
        self.get_logger().info("RIP MODE: Streaming goals to Nav2 without stopping.")

    def map_callback(self, msg):
        self.map_data = msg

    def get_robot_pose(self):
        try:
            # Short timeout for faster loops
            t = self.tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time(), timeout=Duration(seconds=0.05))
            return (t.transform.translation.x, t.transform.translation.y)
        except: return None

    def exploration_loop(self):
        """Constant scanning. No 'is_navigating' check here."""
        if self.map_data is None: return
        pose = self.get_robot_pose()
        if pose is None: return
        
        # Find the next place to rip into
        new_goal = self.find_frontier_aggressive(pose[0], pose[1])
        
        if new_goal:
            self.send_nav_goal(new_goal)

    def find_frontier_aggressive(self, rx, ry):
        info = self.map_data.info
        # Downsample the map (skip pixels) to ensure WSL2 doesn't lag
        grid = np.array(self.map_data.data).reshape((info.height, info.width))
        
        # Find all free pixels (0)
        y_indices, x_indices = np.where(grid == 0)
        
        # Shuffle so the robot doesn't get stuck in a loop looking at the same spot
        # We check every 3rd pixel for extreme speed
        indices = np.arange(0, len(x_indices), 3)
        np.random.shuffle(indices)
        
        for i in indices:
            x, y = x_indices[i], y_indices[i]

            # Frontier Check: Is it touching Unknown space (-1)?
            # Check a small 3x3 block around the pixel
            sub = grid[max(0, y-1):y+2, max(0, x-1):x+2]
            if -1 not in sub: continue
            
            # Wall Safety Check
            if np.any(grid[max(0, y-self.WALL_SAFETY_PX):y+self.WALL_SAFETY_PX+1, 
                           max(0, x-self.WALL_SAFETY_PX):x+self.WALL_SAFETY_PX+1] > 50):
                continue

            # Convert to world
            wx = x * info.resolution + info.origin.position.x
            wy = y * info.resolution + info.origin.position.y
            
            # Distance logic
            dist = math.sqrt((wx - rx)**2 + (wy - ry)**2)
            if dist < self.MIN_FRONTIER_DIST: continue

            # Quick Blacklist check
            if any(math.sqrt((wx-b[0])**2 + (wy-b[1])**2) < 0.5 for b in self.blacklist):
                continue

            return (wx, wy)
        return None

    def send_nav_goal(self, goal_data):
        wx, wy = goal_data
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = wx
        goal_msg.pose.pose.position.y = wy
        goal_msg.pose.pose.orientation.w = 1.0 

        # We do NOT wait for results. 
        # We just fire the goal and let Nav2 overwrite the previous one.
        self.nav_client.wait_for_server(timeout_sec=0.1)
        self.nav_client.send_goal_async(goal_msg)
        
        # Memory management: keep the blacklist small
        if len(self.blacklist) > 15: self.blacklist.pop(0)

def main():
    rclpy.init()
    node = RipExplorer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
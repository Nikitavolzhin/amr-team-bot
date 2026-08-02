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
import time

class GlobalMazeExplorer(Node):
    def __init__(self):
        super().__init__('global_maze_explorer')
        
        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', True)

        self.map_sub = self.create_subscription(OccupancyGrid, 'map', self.map_callback, 1)
        self.marker_pub = self.create_publisher(Marker, 'exploration_marker', 1)
        
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        self.map_data = None
        self.current_goal = None
        self.is_moving = False
        
        # PERSISTENT MEMORY
        self.visited_points = [] # List of previous goals to avoid
        self.blacklist = []      # List of unreachable goals
        
        self.last_pose = (0.0, 0.0)
        self.stuck_time = time.time()

        # Check for goals every 1.5 seconds (Lower frequency to allow Nav2 to stabilize)
        self.create_timer(1.5, self.control_loop)
        self.get_logger().info("--- Global Maze Explorer Engaged: Room-Exit Mode ---")

    def map_callback(self, msg):
        self.map_data = msg

    def get_pose(self):
        try:
            t = self.tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time())
            return (t.transform.translation.x, t.transform.translation.y)
        except: return None

    def control_loop(self):
        if self.map_data is None: return
        pose = self.get_pose()
        if not pose: return

        # 1. DETECT SPINNING/STUCK
        if self.is_moving:
            if math.dist(pose, self.last_pose) < 0.1:
                if (time.time() - self.stuck_time) > 6.0:
                    self.get_logger().error("Loop detected! Forcing exit to new room.")
                    self.blacklist.append(self.current_goal)
                    self.is_moving = False
            else:
                self.last_pose = pose
                self.stuck_time = time.time()

            # Continuous Flow: If driving well, don't interrupt
            if math.dist(pose, self.current_goal) > 1.5:
                return

        # 2. GLOBAL FRONTIER SEARCH
        # We search for the BEST frontier, not the CLOSEST one.
        goal = self.find_global_frontier(pose)
        
        if goal:
            self.send_goal(goal)
        else:
            self.get_logger().warn("No frontiers found. Clearing memory to re-scan...")
            self.visited_points = []
            self.blacklist = []

    def find_global_frontier(self, pose):
        info = self.map_data.info
        res, ox, oy = info.resolution, info.origin.position.x, info.origin.position.y
        data = self.map_data.data
        w, h = info.width, info.height

        best_goal = None
        max_score = -1e9

        # Search up to 15 meters away to find other rooms
        for radius in np.arange(1.5, 15.0, 1.0):
            for angle in np.arange(0, 2*math.pi, math.pi/12):
                tx = pose[0] + radius * math.cos(angle)
                ty = pose[1] + radius * math.sin(angle)

                # Boundary Guard
                if not (ox+0.5 < tx < ox+w*res-0.5 and oy+0.5 < ty < oy+h*res-0.5):
                    continue

                c, r = int((tx - ox) / res), int((ty - oy) / res)
                idx = r * w + c
                
                # Index Safety
                if 0 <= idx < len(data) and data[idx] == -1: # Unknown Area
                    safe_pt = self.get_free_nearby(r, c, info, data)
                    if safe_pt:
                        # SCORING SYSTEM:
                        # 1. Distance from robot (we want some distance to explore)
                        # 2. Distance from ALL previous goals (Prevents going back to same room)
                        dist_from_robot = radius
                        dist_from_history = min([math.dist(safe_pt, p) for p in self.visited_points] + [10.0])
                        
                        # Big clusters are better (finding hallways/doors)
                        cluster_size = self.get_cluster_size(r, c, w, h, data)
                        
                        # Score: Prioritize large areas that are FAR from where we have been
                        score = (cluster_size * 5.0) + (dist_from_history * 10.0) - (dist_from_robot * 0.5)

                        if score > max_score:
                            if not any(math.dist(safe_pt, b) < 1.0 for b in self.blacklist):
                                max_score = score
                                best_goal = safe_pt
        return best_goal

    def get_cluster_size(self, r, c, w, h, data):
        count = 0
        for dr in range(-3, 4):
            for dc in range(-3, 4):
                nr, nc = r+dr, c+dc
                if 0 <= nr < h and 0 <= nc < w:
                    if data[nr*w+nc] == -1: count += 1
        return count

    def get_free_nearby(self, r, c, info, data):
        res, ox, oy = info.resolution, info.origin.position.x, info.origin.position.y
        w, h = info.width, info.height
        for dr in range(-6, 7, 2):
            for dc in range(-6, 7, 2):
                nr, nc = r+dr, c+dc
                if 0 <= nr < h and 0 <= nc < w:
                    if data[nr*w+nc] == 0:
                        if self.check_clearance(nr, nc, w, h, data, int(0.3/res)):
                            return (nc*res+ox, nr*res+oy)
        return None

    def check_clearance(self, r, c, w, h, data, step):
        for dr in range(-step, step+1):
            for dc in range(-step, step+1):
                nr, nc = r+dr, c+dc
                if 0 <= nr < h and 0 <= nc < w:
                    if data[nr*w+nc] > 50: return False
        return True

    def send_goal(self, coords):
        self.current_goal = coords
        self.visited_points.append(coords)
        if len(self.visited_points) > 20: self.visited_points.pop(0) # Keep recent history
        
        self.is_moving = True
        self.stuck_time = time.time()
        
        msg = NavigateToPose.Goal()
        msg.pose.header.frame_id = 'map'
        msg.pose.pose.position.x, msg.pose.pose.position.y = coords
        msg.pose.pose.orientation.w = 1.0 
        
        self.publish_marker(coords)
        self.nav_client.wait_for_server()
        self.nav_client.send_goal_async(msg).add_done_callback(self.goal_cb)

    def goal_cb(self, future):
        handle = future.result()
        if not handle.accepted: self.is_moving = False
        else: handle.get_result_async().add_done_callback(self.done_cb)

    def done_cb(self, future):
        self.is_moving = False

    def publish_marker(self, coords):
        m = Marker()
        m.header.frame_id, m.id = "map", 0
        m.type = Marker.SPHERE
        m.pose.position.x, m.pose.position.y, m.pose.position.z = coords[0], coords[1], 0.4
        m.scale.x = m.scale.y = m.scale.z = 0.6
        m.color.a, m.color.r, m.color.g, m.color.b = 1.0, 1.0, 0.0, 1.0 # Bright Yellow
        self.marker_pub.publish(m)

def main():
    rclpy.init()
    node = GlobalMazeExplorer()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    rclpy.shutdown()

if __name__ == '__main__': main()
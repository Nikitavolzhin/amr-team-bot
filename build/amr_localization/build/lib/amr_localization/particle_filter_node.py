import math
import numpy as np
import rclpy
from rclpy.node import Node

from nav_msgs.msg import OccupancyGrid, Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseArray, Pose, TransformStamped

import tf2_ros
from tf_transformations import euler_from_quaternion, quaternion_from_euler

from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy


class ParticleFilter(Node):

    def __init__(self):
        super().__init__("particle_filter")

        # Main settings
        self.particle_number = 500
        self.motion_noise = [0.02, 0.02, 0.02]
        self.laser_x = 0.45
        self.max_range = 5.6
        self.rays = 48
        self.sigma = 0.30
        self.resample_ratio = 0.35
        self.resample_fraction = 0.10

        # Map
        self.map = None
        self.free_cells = None
        self.distance_map = None
        self.resolution = None
        self.origin_x = self.origin_y = None
        self.width = self.height = None

        # Robot and particles
        self.particles = None
        self.odom = self.last_odom = None

        self.pose_pub = self.create_publisher(
            PoseWithCovarianceStamped, "/particle_filter_pose", 10)
        self.cloud_pub = self.create_publisher(
            PoseArray, "/particle_cloud", 10)

        qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL)

        self.create_subscription(
            OccupancyGrid, "/map", self.map_callback, qos)
        self.create_subscription(
            Odometry, "/odom", self.odom_callback, 50)
        self.create_subscription(
            LaserScan, "/scan", self.scan_callback, 10)

        self.tf = tf2_ros.TransformBroadcaster(self)
        self.create_timer(0.05, self.publish)

        self.get_logger().info("Particle filter started.")

    # =========================================================
    # MAP
    # =========================================================

    def map_callback(self, msg):
        self.map = np.array(msg.data).reshape(
            msg.info.height, msg.info.width)

        self.resolution = msg.info.resolution
        self.origin_x = msg.info.origin.position.x
        self.origin_y = msg.info.origin.position.y
        self.width = msg.info.width
        self.height = msg.info.height

        self.free_cells = np.argwhere(
            (self.map >= 0) & (self.map <= 10))

        if self.particles is None and len(self.free_cells):
            self.make_distance_map()
            self.initialize_particles()

    def make_distance_map(self):
        if self.map is None:
            return
        
        occupied = np.argwhere(self.map >= 50)

        if not len(occupied):
            self.distance_map = np.full(
                self.map.shape, 2.0)
            return

        yy, xx = np.indices(self.map.shape)
        distance = np.full(self.map.shape, np.inf)

        for cells in np.array_split(occupied, max(1, len(occupied) // 256)):
            cy = cells[:, 0, None, None]
            cx = cells[:, 1, None, None]
            d = (yy - cy) ** 2 + (xx - cx) ** 2
            distance = np.minimum(distance, np.min(d, axis=0))

        self.distance_map = np.minimum(
            np.sqrt(distance) * self.resolution, 2.0)

    # =========================================================
    # PARTICLES
    # =========================================================

    def initialize_particles(self):

        if self.free_cells is None:
            return

        self.particles = np.zeros((self.particle_number, 4))

        ids = np.random.randint(len(self.free_cells), size=self.particle_number)
        cells = self.free_cells[ids]

        self.particles[:, 0] = (
            self.origin_x +
            (cells[:, 1] + np.random.rand(self.particle_number)) *
            self.resolution)

        self.particles[:, 1] = (
            self.origin_y +
            (cells[:, 0] + np.random.rand(self.particle_number)) *
            self.resolution)

        self.particles[:, 2] = np.random.uniform(
            -math.pi, math.pi, self.particle_number)

        self.particles[:, 3] = 1.0 / self.particle_number

    # =========================================================
    # ODOMETRY / MOTION
    # =========================================================

    def odom_callback(self, msg):
        if self.particles is None:
            return

        p = msg.pose.pose.position
        q = msg.pose.pose.orientation

        _, _, yaw = euler_from_quaternion(
            [q.x, q.y, q.z, q.w])

        current = (p.x, p.y, yaw)
        self.odom = current

        if self.last_odom is None:
            self.last_odom = current
            return

        lx, ly, lyaw = self.last_odom

        dx = p.x - lx
        dy = p.y - ly
        dyaw = self.angle(yaw - lyaw)

        c, s = math.cos(lyaw), math.sin(lyaw)
        dx = c * dx + s * dy
        dy = -s * dx + c * dy

        dx += np.random.normal(0, self.motion_noise[0], self.particle_number)
        dy += np.random.normal(0, self.motion_noise[1], self.particle_number)
        dyaw += np.random.normal(0, self.motion_noise[2], self.particle_number)

        theta = self.particles[:, 2]

        self.particles[:, 0] += (
            dx * np.cos(theta) - dy * np.sin(theta))

        self.particles[:, 1] += (
            dx * np.sin(theta) + dy * np.cos(theta))

        self.particles[:, 2] = self.normalize(theta + dyaw)
        self.last_odom = current

    # =========================================================
    # LASER
    # =========================================================

    def scan_callback(self, msg):
        if self.particles is None or self.distance_map is None:
            return

        ranges = np.asarray(msg.ranges)
        valid = (
            np.isfinite(ranges) &
            (ranges >= msg.range_min) &
            (ranges <= min(msg.range_max, self.max_range)))

        ids = np.where(valid)[0]

        if not len(ids):
            return

        if len(ids) > self.rays:
            ids = ids[np.linspace(
                0, len(ids) - 1, self.rays, dtype=int)]

        ranges = ranges[ids]
        angles = msg.angle_min + ids * msg.angle_increment

        weights = self.sensor_model(ranges, angles)

        if weights is None:
            return
        
        total = np.sum(weights)

        if total > 0:
            weights /= total
        else:
            weights[:] = 1.0 / self.particle_number

        self.particles[:, 3] = weights

        if self.ess(weights) < self.resample_ratio * self.particle_number:
            self.resample()

    # =========================================================
    # SENSOR MODEL
    # =========================================================

    def sensor_model(self, ranges, angles):

        if self.particles is None:
            return


        if self.distance_map is None:
                    return
        

        log_weights = np.zeros(self.particle_number)

        for start in range(0, self.particle_number, 100):
            end = min(start + 100, self.particle_number)
            p = self.particles[start:end]

            theta = p[:, 2:3]

            lx = p[:, 0:1] + self.laser_x * np.cos(theta)
            ly = p[:, 1:2] + self.laser_x * np.sin(theta)

            ray_angle = theta + angles

            hit_x = lx + ranges * np.cos(ray_angle)
            hit_y = ly + ranges * np.sin(ray_angle)

            mx = ((hit_x - self.origin_x) /
                  self.resolution).astype(int)
            my = ((hit_y - self.origin_y) /
                  self.resolution).astype(int)

            inside = (
                (mx >= 0) & (my >= 0) &
                (mx < self.width) & (my < self.height))

            distance = np.full(mx.shape, 2.0)

            distance[inside] = self.distance_map[
                my[inside], mx[inside]]

            hit = np.exp(
                -(distance ** 2) /
                (2 * self.sigma ** 2))

            probability = (
                0.70 * hit +
                0.25 / self.max_range)

            probability[~inside] *= 0.05

            log_weights[start:end] = np.sum(
                np.log(np.maximum(probability, 1e-12)),
                axis=1)

        return np.exp(log_weights - np.max(log_weights))

    # =========================================================
    # RESAMPLING
    # =========================================================

    def resample(self):

        if self.particles is None:
            return

     

        weights = self.particles[:, 3]
        weights /= np.sum(weights)

        count = max(1, int(self.resample_fraction * self.particle_number))
        replace = np.random.choice(self.particle_number, count, replace=False)

        cumulative = np.cumsum(weights)
        source = np.searchsorted(
            cumulative, np.random.rand(count))
        source = np.clip(source, 0, self.particle_number - 1)

        new = self.particles[source].copy()

        new[:, 0] += np.random.normal(0, 0.03, count)
        new[:, 1] += np.random.normal(0, 0.03, count)
        new[:, 2] = self.normalize(
            new[:, 2] + np.random.normal(0, 0.04, count))

        self.particles[replace] = new
        self.particles[:, 3] = 1.0 / self.particle_number

        self.keep_valid_particles()

    def keep_valid_particles(self):


        if self.particles is None:
            return

        if self.origin_x is None:
            return
        
        if self.origin_y is None:
            return

        
        if self.map is None:
            return    


        if self.free_cells is None:
            return          


        mx = ((self.particles[:, 0] - self.origin_x) /
              self.resolution).astype(int)
        my = ((self.particles[:, 1] - self.origin_y) /
              self.resolution).astype(int)

        inside = (
            (mx >= 0) & (my >= 0) &
            (mx < self.width) & (my < self.height))

        valid = np.zeros(self.particle_number, dtype=bool)
        ids = np.where(inside)[0]

        valid[ids] = (
            (self.map[my[ids], mx[ids]] >= 0) &
            (self.map[my[ids], mx[ids]] <= 10))

        bad = np.where(~valid)[0]

        if not len(bad):
            return

        cells = self.free_cells[
            np.random.randint(len(self.free_cells), size=len(bad))]

        self.particles[bad, 0] = (
            self.origin_x +
            (cells[:, 1] + np.random.rand(len(bad))) *
            self.resolution)

        self.particles[bad, 1] = (
            self.origin_y +
            (cells[:, 0] + np.random.rand(len(bad))) *
            self.resolution)

        self.particles[bad, 2] = np.random.uniform(
            -math.pi, math.pi, len(bad))

    # =========================================================
    # POSE
    # =========================================================

    def estimate_pose(self):


        if self.particles is None:
            return

        
        w = self.particles[:, 3]
        w /= np.sum(w)

        x = np.sum(self.particles[:, 0] * w)
        y = np.sum(self.particles[:, 1] * w)

        yaw = math.atan2(
            np.sum(np.sin(self.particles[:, 2]) * w),
            np.sum(np.cos(self.particles[:, 2]) * w))

        return x, y, yaw

    def publish(self):
        if self.particles is None or self.odom is None :
            return


        estimate_pose = self.estimate_pose()

        if estimate_pose is None:
            return

        x, y, yaw = estimate_pose
        stamp = self.get_clock().now().to_msg()

        # Estimated pose
        pose = PoseWithCovarianceStamped()
        pose.header.stamp = stamp
        pose.header.frame_id = "map"
        pose.pose.pose.position.x = x
        pose.pose.pose.position.y = y

        q = quaternion_from_euler(0, 0, yaw)
        pose.pose.pose.orientation.x = q[0]
        pose.pose.pose.orientation.y = q[1]
        pose.pose.pose.orientation.z = q[2]
        pose.pose.pose.orientation.w = q[3]

        self.pose_pub.publish(pose)

        # Particle cloud
        cloud = PoseArray()
        cloud.header.stamp = stamp
        cloud.header.frame_id = "map"

        for p in self.particles:
            particle = Pose()
            particle.position.x = p[0]
            particle.position.y = p[1]

            q = quaternion_from_euler(0, 0, p[2])
            particle.orientation.x = q[0]
            particle.orientation.y = q[1]
            particle.orientation.z = q[2]
            particle.orientation.w = q[3]

            cloud.poses.append(particle)

        self.cloud_pub.publish(cloud)

        # map -> odom
        ox, oy, oyaw = self.odom
        a = self.angle(yaw - oyaw)

        c, s = math.cos(a), math.sin(a)

        tf = TransformStamped()
        tf.header.stamp = stamp
        tf.header.frame_id = "map"
        tf.child_frame_id = "odom"

        tf.transform.translation.x = x - (c * ox - s * oy)
        tf.transform.translation.y = y - (s * ox + c * oy)

        q = quaternion_from_euler(0, 0, a)
        tf.transform.rotation.x = q[0]
        tf.transform.rotation.y = q[1]
        tf.transform.rotation.z = q[2]
        tf.transform.rotation.w = q[3]

        self.tf.sendTransform(tf)

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def ess(weights):
        return 1.0 / np.sum(weights ** 2)

    @staticmethod
    def angle(a):
        return math.atan2(math.sin(a), math.cos(a))

    @staticmethod
    def normalize(a):
        return np.arctan2(np.sin(a), np.cos(a))


def main():
    rclpy.init()
    node = ParticleFilter()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
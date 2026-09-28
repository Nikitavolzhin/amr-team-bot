import math
import numpy as np

import rclpy
from rclpy.node import Node

from nav_msgs.msg import OccupancyGrid, Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseArray, Pose, TransformStamped

import tf2_ros
from tf_transformations import euler_from_quaternion, quaternion_from_euler


class ParticleFilter(Node):

    def __init__(self):
        super().__init__("particle_filter")

        # ---------------- Settings ----------------
        self.N = 500

        self.motion_noise = [0.02, 0.02, 0.02]
        self.laser_x = 0.45

        self.max_range = 5.6
        self.rays = 48
        self.sigma = 0.30

        self.resample_ratio = 0.35
        self.resample_fraction = 0.10
        self.jitter = [0.03, 0.03, 0.04]

        self.global_localization = True
        self.initial_pose = [0.0, 0.0, 0.0]

        # ---------------- Map ----------------
        self.map = None
        self.resolution = None
        self.origin_x = None
        self.origin_y = None
        self.width = None
        self.height = None

        self.free_cells = None
        self.distance_map = None

        # ---------------- Particles ----------------
        # [x, y, yaw, weight]
        self.particles = None

        # ---------------- Odometry ----------------
        self.odom = None
        self.last_odom = None

        # ---------------- Localization ----------------
        self.start_time = None
        self.converged = False
        self.convergence_count = 0

        # ---------------- Publishers ----------------
        self.pose_pub = self.create_publisher(
            PoseWithCovarianceStamped,
            "/particle_filter_pose",
            10
        )

        self.cloud_pub = self.create_publisher(
            PoseArray,
            "/particle_cloud",
            10
        )

        # ---------------- Map subscriber ----------------
        map_qos = rclpy.qos.QoSProfile(
            depth=1,
            reliability=rclpy.qos.ReliabilityPolicy.RELIABLE,
            durability=rclpy.qos.DurabilityPolicy.TRANSIENT_LOCAL
        )

        self.create_subscription(
            OccupancyGrid,
            "/map",
            self.map_callback,
            map_qos
        )

        # ---------------- Robot sensors ----------------
        self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            50
        )

        self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_callback,
            10
        )

        # ---------------- TF ----------------
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.create_timer(0.05, self.publish)

        self.get_logger().info("Particle filter started.")

    # ============================================================
    # MAP
    # ============================================================

    def map_callback(self, msg):

        self.resolution = msg.info.resolution
        self.origin_x = msg.info.origin.position.x
        self.origin_y = msg.info.origin.position.y
        self.width = msg.info.width
        self.height = msg.info.height

        self.map = np.asarray(
            msg.data,
            dtype=np.int16
        ).reshape(self.height, self.width)

        # Free cells
        self.free_cells = np.argwhere(
            (self.map >= 0) & (self.map <= 10)
        )

        if len(self.free_cells) == 0:
            return

        self.build_distance_map()

        # Initialize only once
        if self.particles is None:
            self.initialize_particles()
            self.start_time = self.get_clock().now()

    # ============================================================
    # DISTANCE MAP
    # ============================================================

    def build_distance_map(self):

        occupied = np.argwhere(self.map >= 50)

        if len(occupied) == 0:
            self.distance_map = np.full(
                self.map.shape,
                2.0,
                dtype=np.float32
            )
            return

        yy, xx = np.indices(
            self.map.shape,
            dtype=np.float32
        )

        distance = np.full(
            self.map.shape,
            np.inf,
            dtype=np.float32
        )

        # Distance to nearest occupied cell
        for i in range(0, len(occupied), 256):

            cells = occupied[i:i + 256]

            cy = cells[:, 0].astype(np.float32)
            cx = cells[:, 1].astype(np.float32)

            d = (
                (yy[None] - cy[:, None, None]) ** 2 +
                (xx[None] - cx[:, None, None]) ** 2
            )

            distance = np.minimum(
                distance,
                np.min(d, axis=0)
            )

        self.distance_map = np.minimum(
            np.sqrt(distance) * self.resolution,
            2.0
        )

    # ============================================================
    # PARTICLE INITIALIZATION
    # ============================================================

    def initialize_particles(self):

        self.particles = np.zeros(
            (self.N, 4),
            dtype=np.float64
        )

        if self.global_localization:

            ids = np.random.randint(
                len(self.free_cells),
                size=self.N
            )

            cells = self.free_cells[ids]

            self.particles[:, 0] = (
                self.origin_x +
                (cells[:, 1] + np.random.rand(self.N))
                * self.resolution
            )

            self.particles[:, 1] = (
                self.origin_y +
                (cells[:, 0] + np.random.rand(self.N))
                * self.resolution
            )

            self.particles[:, 2] = np.random.uniform(
                -math.pi,
                math.pi,
                self.N
            )

        else:

            x, y, yaw = self.initial_pose

            self.particles[:, 0] = np.random.normal(
                x, 0.2, self.N
            )

            self.particles[:, 1] = np.random.normal(
                y, 0.2, self.N
            )

            self.particles[:, 2] = np.random.normal(
                yaw, 0.2, self.N
            )

            self.particles[:, 2] = self.normalize(
                self.particles[:, 2]
            )

            self.keep_valid_particles()

        self.particles[:, 3] = 1.0 / self.N

    # ============================================================
    # ODOMETRY / MOTION MODEL
    # ============================================================

    def odom_callback(self, msg):

        q = msg.pose.pose.orientation

        _, _, yaw = euler_from_quaternion([
            q.x, q.y, q.z, q.w
        ])

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        self.odom = [x, y, yaw]

        if self.particles is None:
            return

        if self.last_odom is None:
            self.last_odom = self.odom
            return

        lx, ly, lyaw = self.last_odom

        dx = x - lx
        dy = y - ly
        dyaw = self.angle(yaw - lyaw)

        # Odometry displacement -> robot frame
        c = math.cos(lyaw)
        s = math.sin(lyaw)

        dx_r = c * dx + s * dy
        dy_r = -s * dx + c * dy

        # Add noise
        dx_r += np.random.normal(
            0, self.motion_noise[0], self.N
        )

        dy_r += np.random.normal(
            0, self.motion_noise[1], self.N
        )

        dyaw += np.random.normal(
            0, self.motion_noise[2], self.N
        )

        yaw = self.particles[:, 2]

        c = np.cos(yaw)
        s = np.sin(yaw)

        # Move every particle
        self.particles[:, 0] += (
            dx_r * c - dy_r * s
        )

        self.particles[:, 1] += (
            dx_r * s + dy_r * c
        )

        self.particles[:, 2] = self.normalize(
            yaw + dyaw
        )

        self.last_odom = self.odom

    # ============================================================
    # LASER / SENSOR MODEL
    # ============================================================

    def scan_callback(self, msg):

        if self.particles is None or self.distance_map is None:
            return

        ranges = np.asarray(
            msg.ranges,
            dtype=np.float64
        )

        valid = (
            np.isfinite(ranges) &
            (ranges >= msg.range_min) &
            (ranges <= min(msg.range_max, self.max_range))
        )

        indices = np.where(valid)[0]

        if len(indices) == 0:
            return

        # Use only a limited number of rays
        if len(indices) > self.rays:

            indices = indices[
                np.linspace(
                    0,
                    len(indices) - 1,
                    self.rays,
                    dtype=int
                )
            ]

        measured = ranges[indices]

        angles = (
            msg.angle_min +
            indices * msg.angle_increment
        )

        max_range = (
            measured >= 0.995 * self.max_range
        )

        weights = self.sensor_model(
            measured,
            angles,
            max_range
        )

        total = np.sum(weights)

        if total <= 0 or not np.isfinite(total):
            weights[:] = 1.0 / self.N
        else:
            weights /= total

        self.particles[:, 3] = weights

        # Resample when particles become concentrated
        if self.effective_sample_size(weights) < self.resample_ratio * self.N:
            self.resample()

        self.update_convergence()

    # ============================================================
    # LIKELIHOOD FIELD SENSOR MODEL
    # ============================================================

    def sensor_model(self, ranges, angles, max_range):

        log_weights = np.zeros(self.N)

        sigma2 = self.sigma ** 2

        for start in range(0, self.N, 100):

            end = min(start + 100, self.N)

            p = self.particles[start:end]

            yaw = p[:, 2:3]

            # Laser position
            lx = (
                p[:, 0:1] +
                self.laser_x * np.cos(yaw)
            )

            ly = (
                p[:, 1:2] +
                self.laser_x * np.sin(yaw)
            )

            ray_angle = yaw + angles[None, :]

            hit_x = (
                lx +
                ranges[None, :] * np.cos(ray_angle)
            )

            hit_y = (
                ly +
                ranges[None, :] * np.sin(ray_angle)
            )

            # World -> map coordinates
            mx = (
                (hit_x - self.origin_x) /
                self.resolution
            ).astype(int)

            my = (
                (hit_y - self.origin_y) /
                self.resolution
            ).astype(int)

            inside = (
                (mx >= 0) &
                (my >= 0) &
                (mx < self.width) &
                (my < self.height)
            )

            distance = np.full(
                mx.shape,
                2.0
            )

            distance[inside] = self.distance_map[
                my[inside],
                mx[inside]
            ]

            # Gaussian hit model
            p_hit = np.exp(
                -(distance ** 2) /
                (2 * sigma2)
            )

            # Simple mixture sensor model
            p = (
                0.70 * p_hit +
                0.25 * (1.0 / self.max_range) +
                0.05 * max_range
            )

            # Penalize rays outside map
            p[~inside] *= 0.05

            log_weights[start:end] = np.sum(
                np.log(np.maximum(p, 1e-12)),
                axis=1
            )

        best = np.max(log_weights)

        return np.exp(
            log_weights - best
        )

    # ============================================================
    # RESAMPLING
    # ============================================================

    def resample(self):

        weights = self.particles[:, 3]
        weights /= np.sum(weights)

        count = max(
            1,
            int(self.N * self.resample_fraction)
        )

        # Particles to replace
        replace = np.random.choice(
            self.N,
            count,
            replace=False
        )

        # Select good particles according to weight
        cumulative = np.cumsum(weights)

        source = np.searchsorted(
            cumulative,
            np.random.rand(count)
        )

        source = np.clip(
            source,
            0,
            self.N - 1
        )

        new = self.particles[source].copy()

        # Small noise prevents all particles becoming identical
        new[:, 0] += np.random.normal(
            0,
            self.jitter[0],
            count
        )

        new[:, 1] += np.random.normal(
            0,
            self.jitter[1],
            count
        )

        new[:, 2] = self.normalize(
            new[:, 2] +
            np.random.normal(
                0,
                self.jitter[2],
                count
            )
        )

        self.particles[replace] = new

        self.particles[:, 3] = 1.0 / self.N

        self.keep_valid_particles()

    # ============================================================
    # CONVERGENCE
    # ============================================================

    def update_convergence(self):

        if not self.global_localization:
            self.converged = True
            return

        if self.start_time is None:
            return

        elapsed = (
            self.get_clock().now() -
            self.start_time
        ).nanoseconds / 1e9

        # Give the filter some time to localize
        if elapsed < 5.0:
            return

        x, y, yaw = self.estimate_pose()

        weights = self.normalized_weights()

        distance = np.sqrt(
            (self.particles[:, 0] - x) ** 2 +
            (self.particles[:, 1] - y) ** 2
        )

        close = np.sum(
            weights[distance < 0.30]
        )

        good = (
            self.position_std() < 0.30 and
            self.yaw_std() < 0.30 and
            close > 0.60
        )

        if good:
            self.convergence_count += 1
        else:
            self.convergence_count = 0

        if self.convergence_count >= 30:
            self.converged = True

    # ============================================================
    # POSE ESTIMATION
    # ============================================================

    def estimate_pose(self):

        w = self.normalized_weights()

        x = np.sum(
            self.particles[:, 0] * w
        )

        y = np.sum(
            self.particles[:, 1] * w
        )

        yaw = math.atan2(
            np.sum(
                np.sin(self.particles[:, 2]) * w
            ),
            np.sum(
                np.cos(self.particles[:, 2]) * w
            )
        )

        return float(x), float(y), float(yaw)

    def position_std(self):

        x, y, _ = self.estimate_pose()
        w = self.normalized_weights()

        variance = np.sum(
            (
                (self.particles[:, 0] - x) ** 2 +
                (self.particles[:, 1] - y) ** 2
            ) * w
        )

        return float(np.sqrt(max(variance, 0)))

    def yaw_std(self):

        _, _, yaw = self.estimate_pose()
        w = self.normalized_weights()

        d = self.normalize(
            self.particles[:, 2] - yaw
        )

        return float(
            np.sqrt(np.sum(d ** 2 * w))
        )

    # ============================================================
    # KEEP PARTICLES IN FREE SPACE
    # ============================================================

    def keep_valid_particles(self):

        if self.free_cells is None:
            return

        mx = (
            (self.particles[:, 0] - self.origin_x) /
            self.resolution
        ).astype(int)

        my = (
            (self.particles[:, 1] - self.origin_y) /
            self.resolution
        ).astype(int)

        inside = (
            (mx >= 0) &
            (my >= 0) &
            (mx < self.width) &
            (my < self.height)
        )

        valid = np.zeros(
            self.N,
            dtype=bool
        )

        ids = np.where(inside)[0]

        valid[ids] = (
            (self.map[my[ids], mx[ids]] >= 0) &
            (self.map[my[ids], mx[ids]] <= 10)
        )

        bad = np.where(~valid)[0]

        if len(bad) == 0:
            return

        cells = self.free_cells[
            np.random.randint(
                len(self.free_cells),
                size=len(bad)
            )
        ]

        self.particles[bad, 0] = (
            self.origin_x +
            (cells[:, 1] + np.random.rand(len(bad))) *
            self.resolution
        )

        self.particles[bad, 1] = (
            self.origin_y +
            (cells[:, 0] + np.random.rand(len(bad))) *
            self.resolution
        )

        self.particles[bad, 2] = np.random.uniform(
            -math.pi,
            math.pi,
            len(bad)
        )

    # ============================================================
    # PUBLISH
    # ============================================================

    def publish(self):

        if self.particles is None or self.odom is None:
            return

        x, y, yaw = self.estimate_pose()

        # Keep robot at initial pose until localization converges
        if not self.converged:
            x, y, yaw = self.initial_pose

        stamp = self.get_clock().now().to_msg()

        # ---------------- Pose ----------------

        pose = PoseWithCovarianceStamped()

        pose.header.stamp = stamp
        pose.header.frame_id = "map"

        pose.pose.pose.position.x = x
        pose.pose.pose.position.y = y

        q = quaternion_from_euler(
            0,
            0,
            yaw
        )

        pose.pose.pose.orientation.x = q[0]
        pose.pose.pose.orientation.y = q[1]
        pose.pose.pose.orientation.z = q[2]
        pose.pose.pose.orientation.w = q[3]

        pose.pose.covariance[0] = self.position_std() ** 2
        pose.pose.covariance[7] = self.position_std() ** 2
        pose.pose.covariance[35] = self.yaw_std() ** 2

        self.pose_pub.publish(pose)

        # ---------------- Particle cloud ----------------

        cloud = PoseArray()

        cloud.header.stamp = stamp
        cloud.header.frame_id = "map"

        for p in self.particles:

            particle = Pose()

            particle.position.x = p[0]
            particle.position.y = p[1]

            q = quaternion_from_euler(
                0,
                0,
                p[2]
            )

            particle.orientation.x = q[0]
            particle.orientation.y = q[1]
            particle.orientation.z = q[2]
            particle.orientation.w = q[3]

            cloud.poses.append(particle)

        self.cloud_pub.publish(cloud)

        # ---------------- map -> odom ----------------

        ox, oy, oyaw = self.odom

        angle = self.angle(
            yaw - oyaw
        )

        c = math.cos(angle)
        s = math.sin(angle)

        tf = TransformStamped()

        tf.header.stamp = stamp
        tf.header.frame_id = "map"
        tf.child_frame_id = "odom"

        tf.transform.translation.x = (
            x - (c * ox - s * oy)
        )

        tf.transform.translation.y = (
            y - (s * ox + c * oy)
        )

        q = quaternion_from_euler(
            0,
            0,
            angle
        )

        tf.transform.rotation.x = q[0]
        tf.transform.rotation.y = q[1]
        tf.transform.rotation.z = q[2]
        tf.transform.rotation.w = q[3]

        self.tf_broadcaster.sendTransform(tf)

    # ============================================================
    # HELPERS
    # ============================================================

    def normalized_weights(self):

        w = self.particles[:, 3]
        total = np.sum(w)

        if total <= 0 or not np.isfinite(total):
            return np.ones(self.N) / self.N

        return w / total

    @staticmethod
    def effective_sample_size(w):
        return 1.0 / np.sum(w ** 2)

    @staticmethod
    def angle(a):
        return math.atan2(
            math.sin(a),
            math.cos(a)
        )

    @staticmethod
    def normalize(a):
        return np.arctan2(
            np.sin(a),
            np.cos(a)
        )


def main(args=None):

    rclpy.init(args=args)

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
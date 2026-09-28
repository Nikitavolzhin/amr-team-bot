import math
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from nav_msgs.msg import OccupancyGrid, Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import (
    PoseWithCovarianceStamped,
    PoseArray,
    Pose,
    TransformStamped,
)

import tf2_ros
from tf_transformations import euler_from_quaternion, quaternion_from_euler


class ParticleFilter(Node):

    def __init__(self):
        super().__init__("particle_filter")

        # Parameters
        self.num_particles = 500
        self.map_frame = "map"
        self.odom_frame = "odom"

        self.global_localization = True
        self.initial_pose = (0.0, 0.0, 0.0)

        self.laser_offset_x = 0.45
        self.laser_offset_y = 0.0
        self.laser_offset_yaw = 0.0

        self.motion_noise = (0.02, 0.02, 0.02)

        self.max_range = 5.6
        self.num_rays = 48
        self.sensor_sigma = 0.30

        self.ess_ratio = 0.35
        self.resample_fraction = 0.10
        self.resample_jitter = (0.03, 0.03, 0.04)

        self.minimum_localization_time = 5.0

        self.convergence_position_std = 0.30
        self.convergence_yaw_std = 0.30
        self.convergence_fraction = 0.60
        self.convergence_count_required = 30

        self.recovery_enabled = True
        self.recovery_fraction = 0.30
        self.recovery_quality_threshold = 0.08
        self.recovery_count_required = 5
        self.recovery_cooldown = 5.0

        # Map
        self.map_data = None
        self.map_resolution = None
        self.map_origin_x = None
        self.map_origin_y = None
        self.map_width = None
        self.map_height = None
        self.free_cells = None
        self.distance_field = None

        # Particles: [x, y, yaw, weight]
        self.particles = None

        # Odometry
        self.current_odom = None
        self.last_odom = None

        # Localization state
        self.localization_start_time = None
        self.is_converged = False
        self.convergence_count = 0

        # Recovery state
        self.recovery_count = 0
        self.last_recovery_time = None
        self.sensor_quality = 0.0

        # Publishers
        self.pose_pub = self.create_publisher(
            PoseWithCovarianceStamped,
            "/particle_filter_pose",
            10
        )

        self.particle_pub = self.create_publisher(
            PoseArray,
            "/particle_cloud",
            10
        )

        # Map uses transient-local QoS
        map_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )

        # Subscribers
        self.create_subscription(
            OccupancyGrid,
            "/map",
            self.map_callback,
            map_qos
        )

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

        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.create_timer(0.05, self.publish)

        self.get_logger().info("Particle filter started.")

    # ==============================================================
    # MAP
    # ==============================================================

    def map_callback(self, msg):

        self.map_resolution = msg.info.resolution
        self.map_origin_x = msg.info.origin.position.x
        self.map_origin_y = msg.info.origin.position.y
        self.map_width = msg.info.width
        self.map_height = msg.info.height

        self.map_data = np.asarray(
            msg.data,
            dtype=np.int16
        ).reshape(
            self.map_height,
            self.map_width
        )

        # Free cells
        self.free_cells = np.argwhere(
            (self.map_data >= 0) &
            (self.map_data <= 10)
        )

        self.build_distance_field()

        if self.particles is None:
            self.initialize_particles()
            self.localization_start_time = self.get_clock().now()

            self.get_logger().info(
                "Particles initialized across the map."
            )

    def build_distance_field(self):

        occupied = np.argwhere(self.map_data >= 50)

        if len(occupied) == 0:
            self.distance_field = np.full(
                self.map_data.shape,
                2.0,
                dtype=np.float32
            )
            return

        yy, xx = np.indices(
            self.map_data.shape,
            dtype=np.float32
        )

        distance_squared = np.full(
            self.map_data.shape,
            np.inf,
            dtype=np.float32
        )

        # Calculate distance to the nearest occupied cell
        for start in range(0, len(occupied), 256):

            cells = occupied[start:start + 256]

            cy = cells[:, 0].astype(np.float32)
            cx = cells[:, 1].astype(np.float32)

            distance = (
                (yy[None, :, :] - cy[:, None, None]) ** 2 +
                (xx[None, :, :] - cx[:, None, None]) ** 2
            )

            distance_squared = np.minimum(
                distance_squared,
                np.min(distance, axis=0)
            )

        self.distance_field = np.minimum(
            np.sqrt(distance_squared) * self.map_resolution,
            2.0
        )

    # ==============================================================
    # INITIALIZATION
    # ==============================================================

    def initialize_particles(self):

        self.particles = np.zeros(
            (self.num_particles, 4),
            dtype=np.float64
        )

        if (
            self.global_localization
            and len(self.free_cells) > 0
        ):

            indices = np.random.randint(
                len(self.free_cells),
                size=self.num_particles
            )

            cells = self.free_cells[indices]

            self.particles[:, 0] = (
                self.map_origin_x +
                (cells[:, 1] + np.random.rand(self.num_particles))
                * self.map_resolution
            )

            self.particles[:, 1] = (
                self.map_origin_y +
                (cells[:, 0] + np.random.rand(self.num_particles))
                * self.map_resolution
            )

            self.particles[:, 2] = np.random.uniform(
                -math.pi,
                math.pi,
                self.num_particles
            )

        else:

            x, y, yaw = self.initial_pose

            self.particles[:, 0] = np.random.normal(
                x, 0.20, self.num_particles
            )

            self.particles[:, 1] = np.random.normal(
                y, 0.20, self.num_particles
            )

            self.particles[:, 2] = np.random.normal(
                yaw, 0.20, self.num_particles
            )

            self.particles[:, 2] = self.normalize_angles(
                self.particles[:, 2]
            )

            self.keep_valid_particles()

        self.particles[:, 3] = 1.0 / self.num_particles

    # ==============================================================
    # ODOMETRY / MOTION UPDATE
    # ==============================================================

    def odom_callback(self, msg):

        orientation = msg.pose.pose.orientation

        _, _, yaw = euler_from_quaternion([
            orientation.x,
            orientation.y,
            orientation.z,
            orientation.w
        ])

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        self.current_odom = (x, y, yaw)

        if self.particles is None:
            return

        if self.last_odom is None:
            self.last_odom = self.current_odom
            return

        last_x, last_y, last_yaw = self.last_odom

        dx = x - last_x
        dy = y - last_y
        dyaw = self.normalize_angle(yaw - last_yaw)

        # Convert odometry movement into robot coordinates
        cos_yaw = math.cos(last_yaw)
        sin_yaw = math.sin(last_yaw)

        dx_robot = (
            cos_yaw * dx +
            sin_yaw * dy
        )

        dy_robot = (
            -sin_yaw * dx +
            cos_yaw * dy
        )

        # Add motion noise
        dx_robot += np.random.normal(
            0,
            self.motion_noise[0],
            self.num_particles
        )

        dy_robot += np.random.normal(
            0,
            self.motion_noise[1],
            self.num_particles
        )

        dyaw += np.random.normal(
            0,
            self.motion_noise[2],
            self.num_particles
        )

        particle_yaw = self.particles[:, 2]

        cos_particle = np.cos(particle_yaw)
        sin_particle = np.sin(particle_yaw)

        self.particles[:, 0] += (
            dx_robot * cos_particle -
            dy_robot * sin_particle
        )

        self.particles[:, 1] += (
            dx_robot * sin_particle +
            dy_robot * cos_particle
        )

        self.particles[:, 2] = self.normalize_angles(
            particle_yaw + dyaw
        )

        self.last_odom = self.current_odom

    # ==============================================================
    # LASER UPDATE
    # ==============================================================

    def scan_callback(self, msg):

        if (
            self.particles is None or
            self.distance_field is None
        ):
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

        if len(indices) > self.num_rays:

            indices = indices[
                np.linspace(
                    0,
                    len(indices) - 1,
                    self.num_rays,
                    dtype=int
                )
            ]

        measured_ranges = ranges[indices]

        beam_angles = (
            msg.angle_min +
            indices * msg.angle_increment +
            self.laser_offset_yaw
        )

        max_range = (
            measured_ranges >= 0.995 * self.max_range
        )

        weights = self.sensor_model(
            measured_ranges,
            beam_angles,
            max_range
        )

        total = np.sum(weights)

        if not np.isfinite(total) or total <= 0:
            weights[:] = 1.0 / self.num_particles
        else:
            weights /= total

        self.particles[:, 3] = weights

        # Wait before starting resampling
        elapsed = (
            self.get_clock().now() -
            self.localization_start_time
        ).nanoseconds / 1e9

        if (
            elapsed >= self.minimum_localization_time and
            self.effective_sample_size(weights) <
            self.ess_ratio * self.num_particles
        ):
            self.resample()

        self.update_convergence()
        self.check_recovery()

    # ==============================================================
    # SENSOR MODEL
    # ==============================================================

    def sensor_model(
        self,
        measured_ranges,
        beam_angles,
        max_range
    ):

        log_weights = np.zeros(
            self.num_particles
        )

        sigma_squared = self.sensor_sigma ** 2

        # Evaluate particles in small batches
        for start in range(0, self.num_particles, 100):

            end = min(
                start + 100,
                self.num_particles
            )

            particles = self.particles[start:end]

            yaw = particles[:, 2:3]

            cos_yaw = np.cos(yaw)
            sin_yaw = np.sin(yaw)

            laser_x = (
                particles[:, 0:1] +
                self.laser_offset_x * cos_yaw -
                self.laser_offset_y * sin_yaw
            )

            laser_y = (
                particles[:, 1:2] +
                self.laser_offset_x * sin_yaw +
                self.laser_offset_y * cos_yaw
            )

            angles = yaw + beam_angles[None, :]

            hit_x = (
                laser_x +
                measured_ranges[None, :] * np.cos(angles)
            )

            hit_y = (
                laser_y +
                measured_ranges[None, :] * np.sin(angles)
            )

            map_x = np.floor(
                (hit_x - self.map_origin_x) /
                self.map_resolution
            ).astype(np.int32)

            map_y = np.floor(
                (hit_y - self.map_origin_y) /
                self.map_resolution
            ).astype(np.int32)

            inside = (
                (map_x >= 0) &
                (map_y >= 0) &
                (map_x < self.map_width) &
                (map_y < self.map_height)
            )

            distance = np.full(
                map_x.shape,
                2.0
            )

            distance[inside] = self.distance_field[
                map_y[inside],
                map_x[inside]
            ]

            hit_probability = np.exp(
                -(distance ** 2) /
                (2 * sigma_squared)
            )

            random_probability = 1.0 / self.max_range

            probability = (
                0.70 * hit_probability +
                0.25 * random_probability +
                0.05 * max_range
            )

            probability[~inside] *= 0.05

            log_weights[start:end] = np.sum(
                np.log(
                    np.maximum(
                        probability,
                        1e-12
                    )
                ),
                axis=1
            )

        best = np.max(log_weights)

        self.sensor_quality = float(
            np.exp(
                np.clip(
                    best / max(len(measured_ranges), 1),
                    -50,
                    0
                )
            )
        )

        return np.exp(log_weights - best)

    # ==============================================================
    # RESAMPLING
    # ==============================================================

    def resample(self):

        weights = self.particles[:, 3].copy()
        weights /= np.sum(weights)

        count = max(
            1,
            int(self.num_particles * self.resample_fraction)
        )

        replace_indices = np.random.choice(
            self.num_particles,
            count,
            replace=False
        )

        cumulative = np.cumsum(weights)

        source_indices = np.searchsorted(
            cumulative,
            np.random.rand(count),
            side="left"
        )

        source_indices = np.clip(
            source_indices,
            0,
            self.num_particles - 1
        )

        new_particles = self.particles[
            source_indices
        ].copy()

        new_particles[:, 0] += np.random.normal(
            0,
            self.resample_jitter[0],
            count
        )

        new_particles[:, 1] += np.random.normal(
            0,
            self.resample_jitter[1],
            count
        )

        new_particles[:, 2] = self.normalize_angles(
            new_particles[:, 2] +
            np.random.normal(
                0,
                self.resample_jitter[2],
                count
            )
        )

        self.particles[
            replace_indices
        ] = new_particles

        self.particles[:, 3] = (
            1.0 / self.num_particles
        )

        self.keep_valid_particles()

    # ==============================================================
    # CONVERGENCE
    # ==============================================================

    def update_convergence(self):

        if not self.global_localization:
            self.is_converged = True
            return

        elapsed = (
            self.get_clock().now() -
            self.localization_start_time
        ).nanoseconds / 1e9

        if elapsed < self.minimum_localization_time:
            self.convergence_count = 0
            return

        x, y, yaw = self.estimate_pose()

        weights = self.normalized_weights()

        distance = np.sqrt(
            (self.particles[:, 0] - x) ** 2 +
            (self.particles[:, 1] - y) ** 2
        )

        position_std = self.get_position_std()
        yaw_std = self.get_yaw_std()

        close_fraction = np.sum(
            weights[
                distance < self.convergence_position_std
            ]
        )

        converged = (
            position_std <= self.convergence_position_std and
            yaw_std <= self.convergence_yaw_std and
            close_fraction >= self.convergence_fraction
        )

        if converged:
            self.convergence_count += 1
        else:
            self.convergence_count = 0

        if self.convergence_count >= self.convergence_count_required:
            if not self.is_converged:
                self.get_logger().info(
                    "Particle filter converged."
                )

            self.is_converged = True

    # ==============================================================
    # RECOVERY
    # ==============================================================

    def check_recovery(self):

        if not self.recovery_enabled:
            return

        if not self.is_converged:
            self.recovery_count = 0
            return

        if self.sensor_quality >= self.recovery_quality_threshold:
            self.recovery_count = 0
            return

        self.recovery_count += 1

        if self.recovery_count < self.recovery_count_required:
            return

        now = self.get_clock().now()

        if self.last_recovery_time is not None:

            elapsed = (
                now - self.last_recovery_time
            ).nanoseconds / 1e9

            if elapsed < self.recovery_cooldown:
                return

        self.inject_recovery_particles()

        self.recovery_count = 0
        self.last_recovery_time = now

    def inject_recovery_particles(self):

        count = int(
            self.num_particles *
            self.recovery_fraction
        )

        indices = np.random.choice(
            self.num_particles,
            count,
            replace=False
        )

        cells = self.free_cells[
            np.random.randint(
                len(self.free_cells),
                size=count
            )
        ]

        self.particles[indices, 0] = (
            self.map_origin_x +
            (cells[:, 1] + np.random.rand(count)) *
            self.map_resolution
        )

        self.particles[indices, 1] = (
            self.map_origin_y +
            (cells[:, 0] + np.random.rand(count)) *
            self.map_resolution
        )

        self.particles[indices, 2] = np.random.uniform(
            -math.pi,
            math.pi,
            count
        )

        self.particles[:, 3] = (
            1.0 / self.num_particles
        )

        self.get_logger().warn(
            f"Localization recovery: "
            f"{count}/{self.num_particles} particles replaced."
        )

    # ==============================================================
    # POSE ESTIMATION
    # ==============================================================

    def estimate_pose(self):

        weights = self.normalized_weights()

        x = np.sum(
            self.particles[:, 0] * weights
        )

        y = np.sum(
            self.particles[:, 1] * weights
        )

        yaw = math.atan2(
            np.sum(
                np.sin(self.particles[:, 2]) *
                weights
            ),
            np.sum(
                np.cos(self.particles[:, 2]) *
                weights
            )
        )

        return float(x), float(y), float(yaw)

    def get_position_std(self):

        x, y, _ = self.estimate_pose()
        weights = self.normalized_weights()

        variance = np.sum(
            (
                (self.particles[:, 0] - x) ** 2 +
                (self.particles[:, 1] - y) ** 2
            ) * weights
        )

        return float(np.sqrt(max(variance, 0)))

    def get_yaw_std(self):

        _, _, yaw = self.estimate_pose()
        weights = self.normalized_weights()

        difference = self.normalize_angles(
            self.particles[:, 2] - yaw
        )

        return float(
            np.sqrt(
                np.sum(
                    difference ** 2 *
                    weights
                )
            )
        )

    # ==============================================================
    # PUBLISH
    # ==============================================================

    def publish(self):

        if self.particles is None or self.current_odom is None:
            return

        x, y, yaw = self.estimate_pose()

        # Before convergence keep RViz at the initial pose.
        if not self.is_converged:
            x, y, yaw = self.initial_pose

        stamp = self.get_clock().now().to_msg()

        # Pose
        pose = PoseWithCovarianceStamped()

        pose.header.stamp = stamp
        pose.header.frame_id = self.map_frame

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

        position_std = self.get_position_std()
        yaw_std = self.get_yaw_std()

        pose.pose.covariance[0] = position_std ** 2
        pose.pose.covariance[7] = position_std ** 2
        pose.pose.covariance[35] = yaw_std ** 2

        self.pose_pub.publish(pose)

        # Particle cloud
        cloud = PoseArray()

        cloud.header.stamp = stamp
        cloud.header.frame_id = self.map_frame

        for particle in self.particles:

            p = Pose()

            p.position.x = particle[0]
            p.position.y = particle[1]

            q = quaternion_from_euler(
                0,
                0,
                particle[2]
            )

            p.orientation.x = q[0]
            p.orientation.y = q[1]
            p.orientation.z = q[2]
            p.orientation.w = q[3]

            cloud.poses.append(p)

        self.particle_pub.publish(cloud)

        # map -> odom
        odom_x, odom_y, odom_yaw = self.current_odom

        transform_yaw = self.normalize_angle(
            yaw - odom_yaw
        )

        c = math.cos(transform_yaw)
        s = math.sin(transform_yaw)

        transform = TransformStamped()

        transform.header.stamp = stamp
        transform.header.frame_id = self.map_frame
        transform.child_frame_id = self.odom_frame

        transform.transform.translation.x = (
            x - (c * odom_x - s * odom_y)
        )

        transform.transform.translation.y = (
            y - (s * odom_x + c * odom_y)
        )

        q = quaternion_from_euler(
            0,
            0,
            transform_yaw
        )

        transform.transform.rotation.x = q[0]
        transform.transform.rotation.y = q[1]
        transform.transform.rotation.z = q[2]
        transform.transform.rotation.w = q[3]

        self.tf_broadcaster.sendTransform(transform)

    # ==============================================================
    # HELPERS
    # ==============================================================

    def keep_valid_particles(self):

        if self.free_cells is None:
            return

        map_x = (
            (self.particles[:, 0] - self.map_origin_x) /
            self.map_resolution
        ).astype(int)

        map_y = (
            (self.particles[:, 1] - self.map_origin_y) /
            self.map_resolution
        ).astype(int)

        inside = (
            (map_x >= 0) &
            (map_y >= 0) &
            (map_x < self.map_width) &
            (map_y < self.map_height)
        )

        valid = np.zeros(
            self.num_particles,
            dtype=bool
        )

        ids = np.where(inside)[0]

        valid[ids] = (
            (self.map_data[map_y[ids], map_x[ids]] >= 0) &
            (self.map_data[map_y[ids], map_x[ids]] <= 10)
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
            self.map_origin_x +
            (cells[:, 1] + np.random.rand(len(bad))) *
            self.map_resolution
        )

        self.particles[bad, 1] = (
            self.map_origin_y +
            (cells[:, 0] + np.random.rand(len(bad))) *
            self.map_resolution
        )

        self.particles[bad, 2] = np.random.uniform(
            -math.pi,
            math.pi,
            len(bad)
        )

    def normalized_weights(self):

        weights = self.particles[:, 3]
        total = np.sum(weights)

        if total <= 0 or not np.isfinite(total):
            return np.ones(self.num_particles) / self.num_particles

        return weights / total

    @staticmethod
    def effective_sample_size(weights):
        return 1.0 / np.sum(weights ** 2)

    @staticmethod
    def normalize_angle(angle):
        return math.atan2(
            math.sin(angle),
            math.cos(angle)
        )

    @staticmethod
    def normalize_angles(angles):
        return np.arctan2(
            np.sin(angles),
            np.cos(angles)
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
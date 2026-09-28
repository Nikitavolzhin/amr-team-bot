#!/usr/bin/env python3

import math
import heapq

import numpy as np

import rclpy
from rclpy.node import Node

from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    DurabilityPolicy,
    HistoryPolicy,
)

from nav_msgs.msg import OccupancyGrid, Odometry
from sensor_msgs.msg import LaserScan

from geometry_msgs.msg import (
    Pose,
    PoseArray,
    PoseWithCovarianceStamped,
    TransformStamped,
)

import tf2_ros


# ================================================================
# Utility functions
# ================================================================

def normalize_angle(angle):
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def yaw_from_quaternion(q):
    return math.atan2(
        2.0 * (q.w * q.z + q.x * q.y),
        1.0 - 2.0 * (q.y * q.y + q.z * q.z),
    )


def quaternion_from_yaw(yaw):
    return (
        0.0,
        0.0,
        math.sin(yaw / 2.0),
        math.cos(yaw / 2.0),
    )


# ================================================================
# Particle Filter
# ================================================================

class ParticleFilter(Node):

    def __init__(self):

        super().__init__('particle_filter')

        # ========================================================
        # PARAMETERS
        # ========================================================

        self.declare_parameter('num_particles', 500)
        self.declare_parameter('publish_rate', 10.0)

        # Motion noise
        self.declare_parameter('motion_noise_x', 0.005)
        self.declare_parameter('motion_noise_y', 0.005)
        self.declare_parameter('motion_noise_theta', 0.01)

        # Laser model
        self.declare_parameter('laser_sigma', 0.20)
        self.declare_parameter('laser_z_hit', 0.90)
        self.declare_parameter('laser_z_rand', 0.10)

        self.declare_parameter('laser_min_range', 0.05)
        self.declare_parameter('laser_max_range', 5.6)

        # Use approximately 40 beams.
        self.declare_parameter('laser_beams', 40)

        # Resampling
        self.declare_parameter('resample_threshold', 0.50)

        # Frames
        self.declare_parameter(
            'map_frame',
            'map'
        )

        self.declare_parameter(
            'odom_frame',
            'odom'
        )

        self.declare_parameter(
            'base_frame',
            'base_footprint'
        )

        # ========================================================
        # READ PARAMETERS
        # ========================================================

        self.num_particles = int(
            self.get_parameter(
                'num_particles'
            ).value
        )

        self.publish_rate = float(
            self.get_parameter(
                'publish_rate'
            ).value
        )

        self.motion_noise_x = float(
            self.get_parameter(
                'motion_noise_x'
            ).value
        )

        self.motion_noise_y = float(
            self.get_parameter(
                'motion_noise_y'
            ).value
        )

        self.motion_noise_theta = float(
            self.get_parameter(
                'motion_noise_theta'
            ).value
        )

        self.laser_sigma = float(
            self.get_parameter(
                'laser_sigma'
            ).value
        )

        self.laser_z_hit = float(
            self.get_parameter(
                'laser_z_hit'
            ).value
        )

        self.laser_z_rand = float(
            self.get_parameter(
                'laser_z_rand'
            ).value
        )

        self.laser_min_range = float(
            self.get_parameter(
                'laser_min_range'
            ).value
        )

        self.laser_max_range = float(
            self.get_parameter(
                'laser_max_range'
            ).value
        )

        self.laser_beams = int(
            self.get_parameter(
                'laser_beams'
            ).value
        )

        self.resample_threshold = float(
            self.get_parameter(
                'resample_threshold'
            ).value
        )

        self.map_frame = str(
            self.get_parameter(
                'map_frame'
            ).value
        )

        self.odom_frame = str(
            self.get_parameter(
                'odom_frame'
            ).value
        )

        self.base_frame = str(
            self.get_parameter(
                'base_frame'
            ).value
        )

        # ========================================================
        # STATE
        # ========================================================

        self.map_received = False
        self.odom_received = False
        self.scan_received = False
        self.initialized = False

        # --------------------------------------------------------
        # Map
        # --------------------------------------------------------

        self.map_resolution = None
        self.map_width = None
        self.map_height = None

        self.map_origin_x = None
        self.map_origin_y = None

        self.occupancy = None
        self.distance_map = None

        # --------------------------------------------------------
        # Particles
        #
        # [x, y, yaw, weight]
        # --------------------------------------------------------

        self.particles = np.zeros(
            (self.num_particles, 4),
            dtype=np.float64
        )

        # --------------------------------------------------------
        # Odometry
        # --------------------------------------------------------

        self.last_odom_x = None
        self.last_odom_y = None
        self.last_odom_yaw = None

        self.current_odom_x = 0.0
        self.current_odom_y = 0.0
        self.current_odom_yaw = 0.0

        # --------------------------------------------------------
        # Scan
        # --------------------------------------------------------

        self.latest_scan = None

        # IMPORTANT:
        # Prevent processing the same LaserScan repeatedly.
        self.last_processed_scan_stamp = None

        # --------------------------------------------------------
        # Estimated pose
        # --------------------------------------------------------

        self.estimated_x = 0.0
        self.estimated_y = 0.0
        self.estimated_yaw = 0.0

        # --------------------------------------------------------
        # Diagnostics
        # --------------------------------------------------------

        self.last_ess = float(self.num_particles)

        # ========================================================
        # TF
        # ========================================================

        self.tf_buffer = tf2_ros.Buffer()

        self.tf_listener = tf2_ros.TransformListener(
            self.tf_buffer,
            self
        )

        self.tf_broadcaster = (
            tf2_ros.TransformBroadcaster(self)
        )

        # ========================================================
        # MAP QoS
        # ========================================================

        map_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        # ========================================================
        # SUBSCRIBERS
        # ========================================================

        self.map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            map_qos
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            20
        )

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            20
        )

        # ========================================================
        # PUBLISHERS
        # ========================================================

        self.particle_pub = self.create_publisher(
            PoseArray,
            '/particle_cloud',
            10
        )

        self.pose_pub = self.create_publisher(
            PoseWithCovarianceStamped,
            '/particle_filter_pose',
            10
        )

        # ========================================================
        # TIMER
        # ========================================================

        self.timer = self.create_timer(
            1.0 / self.publish_rate,
            self.process_filter
        )

        self.get_logger().info(
            '========================================'
        )

        self.get_logger().info(
            'Particle Filter Localization started'
        )

        self.get_logger().info(
            f'Particles: {self.num_particles}'
        )

        self.get_logger().info(
            f'Laser beams: {self.laser_beams}'
        )

        self.get_logger().info(
            f'Laser sigma: {self.laser_sigma}'
        )

        self.get_logger().info(
            f'Resample threshold: '
            f'{self.resample_threshold}'
        )

        self.get_logger().info(
            '========================================'
        )

    # ================================================================
    # MAP CALLBACK
    # ================================================================

    def map_callback(self, msg):

        if self.map_received:
            return

        self.map_resolution = float(
            msg.info.resolution
        )

        self.map_width = int(
            msg.info.width
        )

        self.map_height = int(
            msg.info.height
        )

        self.map_origin_x = float(
            msg.info.origin.position.x
        )

        self.map_origin_y = float(
            msg.info.origin.position.y
        )

        data = np.asarray(
            msg.data,
            dtype=np.int16
        )

        self.occupancy = data.reshape(
            self.map_height,
            self.map_width
        )

        free_count = int(
            np.sum(self.occupancy == 0)
        )

        occupied_count = int(
            np.sum(self.occupancy >= 65)
        )

        self.get_logger().info(
            f'Map received: '
            f'{self.map_width} x '
            f'{self.map_height}'
        )

        self.get_logger().info(
            f'Free cells: {free_count}'
        )

        self.get_logger().info(
            f'Occupied cells: {occupied_count}'
        )

        # --------------------------------------------------------
        # Build likelihood-field distance map
        # --------------------------------------------------------

        self.distance_map = (
            self.build_distance_map()
        )

        if self.distance_map is None:

            self.get_logger().error(
                'Failed to create distance map.'
            )

            return

        self.get_logger().info(
            'Distance map created.'
        )

        self.map_received = True

        # We initialize only after map is ready.
        self.try_initialize()

    # ================================================================
    # DISTANCE MAP
    # ================================================================

    def build_distance_map(self):

        height = self.map_height
        width = self.map_width

        distance = np.full(
            (height, width),
            np.inf,
            dtype=np.float64
        )

        occupied = np.argwhere(
            self.occupancy >= 65
        )

        if len(occupied) == 0:

            self.get_logger().error(
                'Map has no occupied cells.'
            )

            return None

        heap = []

        # --------------------------------------------------------
        # Occupied cells have distance 0
        # --------------------------------------------------------

        for y, x in occupied:

            y = int(y)
            x = int(x)

            distance[y, x] = 0.0

            heapq.heappush(
                heap,
                (0.0, y, x)
            )

        neighbors = [
            (-1, -1, math.sqrt(2.0)),
            (-1,  0, 1.0),
            (-1,  1, math.sqrt(2.0)),
            ( 0, -1, 1.0),
            ( 0,  1, 1.0),
            ( 1, -1, math.sqrt(2.0)),
            ( 1,  0, 1.0),
            ( 1,  1, math.sqrt(2.0)),
        ]

        # --------------------------------------------------------
        # Dijkstra
        # --------------------------------------------------------

        while heap:

            current_distance, cy, cx = (
                heapq.heappop(heap)
            )

            if current_distance > distance[cy, cx]:
                continue

            for dy, dx, cost in neighbors:

                ny = cy + dy
                nx = cx + dx

                if ny < 0 or ny >= height:
                    continue

                if nx < 0 or nx >= width:
                    continue

                new_distance = (
                    current_distance + cost
                )

                if new_distance < distance[ny, nx]:

                    distance[ny, nx] = (
                        new_distance
                    )

                    heapq.heappush(
                        heap,
                        (
                            new_distance,
                            ny,
                            nx
                        )
                    )

        distance *= self.map_resolution

        return distance.astype(
            np.float32
        )

    # ================================================================
    # INITIALIZATION
    # ================================================================

    def try_initialize(self):

        if self.initialized:
            return

        if not self.map_received:
            return

        if not self.odom_received:
            return

        self.initialize_particles()

    # ================================================================
    # INITIALIZE PARTICLES GLOBALLY
    # ================================================================

    def initialize_particles(self):

        if self.occupancy is None:
            return

        free_cells = np.argwhere(
            self.occupancy == 0
        )

        if len(free_cells) == 0:

            self.get_logger().error(
                'No free cells available.'
            )

            return

        # Random free cells
        indices = np.random.choice(
            len(free_cells),
            size=self.num_particles,
            replace=True
        )

        selected = free_cells[
            indices
        ]

        # --------------------------------------------------------
        # x
        # --------------------------------------------------------

        self.particles[:, 0] = (
            self.map_origin_x
            + (selected[:, 1] + 0.5)
            * self.map_resolution
        )

        # --------------------------------------------------------
        # y
        # --------------------------------------------------------

        self.particles[:, 1] = (
            self.map_origin_y
            + (selected[:, 0] + 0.5)
            * self.map_resolution
        )

        # --------------------------------------------------------
        # yaw
        # --------------------------------------------------------

        self.particles[:, 2] = np.random.uniform(
            -math.pi,
            math.pi,
            self.num_particles
        )

        # --------------------------------------------------------
        # equal initial weights
        # --------------------------------------------------------

        self.particles[:, 3] = (
            1.0 / self.num_particles
        )

        self.initialized = True

        self.get_logger().info(
            'Global particle initialization complete.'
        )

    # ================================================================
    # ODOM CALLBACK
    # ================================================================

    def odom_callback(self, msg):

        x = float(
            msg.pose.pose.position.x
        )

        y = float(
            msg.pose.pose.position.y
        )

        yaw = yaw_from_quaternion(
            msg.pose.pose.orientation
        )

        self.current_odom_x = x
        self.current_odom_y = y
        self.current_odom_yaw = yaw

        # --------------------------------------------------------
        # First odometry message
        # --------------------------------------------------------

        if self.last_odom_x is None:

            self.last_odom_x = x
            self.last_odom_y = y
            self.last_odom_yaw = yaw

            self.odom_received = True

            self.try_initialize()

            return

        if not self.initialized:
            return

        # --------------------------------------------------------
        # Odometry delta in world frame
        # --------------------------------------------------------

        dx_world = (
            x - self.last_odom_x
        )

        dy_world = (
            y - self.last_odom_y
        )

        dyaw = normalize_angle(
            yaw - self.last_odom_yaw
        )

        # --------------------------------------------------------
        # Convert translation to previous robot frame
        # --------------------------------------------------------

        c = math.cos(
            self.last_odom_yaw
        )

        s = math.sin(
            self.last_odom_yaw
        )

        delta_x = (
            c * dx_world
            + s * dy_world
        )

        delta_y = (
            -s * dx_world
            + c * dy_world
        )

        # --------------------------------------------------------
        # Ignore tiny Gazebo noise
        # --------------------------------------------------------

        if (
            abs(delta_x) < 1e-5
            and abs(delta_y) < 1e-5
            and abs(dyaw) < 1e-5
        ):

            self.last_odom_x = x
            self.last_odom_y = y
            self.last_odom_yaw = yaw

            return

        # --------------------------------------------------------
        # Particle motion model
        # --------------------------------------------------------

        particle_yaw = (
            self.particles[:, 2]
        )

        noisy_dx = (
            delta_x
            + np.random.normal(
                0.0,
                self.motion_noise_x,
                self.num_particles
            )
        )

        noisy_dy = (
            delta_y
            + np.random.normal(
                0.0,
                self.motion_noise_y,
                self.num_particles
            )
        )

        noisy_dyaw = (
            dyaw
            + np.random.normal(
                0.0,
                self.motion_noise_theta,
                self.num_particles
            )
        )

        cp = np.cos(
            particle_yaw
        )

        sp = np.sin(
            particle_yaw
        )

        self.particles[:, 0] += (
            cp * noisy_dx
            - sp * noisy_dy
        )

        self.particles[:, 1] += (
            sp * noisy_dx
            + cp * noisy_dy
        )

        self.particles[:, 2] = (
            particle_yaw
            + noisy_dyaw
        )

        self.particles[:, 2] = (
            (self.particles[:, 2] + math.pi)
            % (2.0 * math.pi)
            - math.pi
        )

        # --------------------------------------------------------
        # Repair particles that entered obstacles/outside map
        # --------------------------------------------------------

        self.repair_invalid_particles()

        # --------------------------------------------------------
        # Update odometry reference
        # --------------------------------------------------------

        self.last_odom_x = x
        self.last_odom_y = y
        self.last_odom_yaw = yaw

    # ================================================================
    # REPAIR INVALID PARTICLES
    # ================================================================

    def repair_invalid_particles(self):

        if self.occupancy is None:
            return

        mx = np.floor(
            (
                self.particles[:, 0]
                - self.map_origin_x
            )
            / self.map_resolution
        ).astype(np.int32)

        my = np.floor(
            (
                self.particles[:, 1]
                - self.map_origin_y
            )
            / self.map_resolution
        ).astype(np.int32)

        valid = (
            (mx >= 0)
            & (mx < self.map_width)
            & (my >= 0)
            & (my < self.map_height)
        )

        safe_mx = np.clip(
            mx,
            0,
            self.map_width - 1
        )

        safe_my = np.clip(
            my,
            0,
            self.map_height - 1
        )

        valid &= (
            self.occupancy[
                safe_my,
                safe_mx
            ] == 0
        )

        invalid = np.where(
            ~valid
        )[0]

        if len(invalid) == 0:
            return

        free_cells = np.argwhere(
            self.occupancy == 0
        )

        replacement = np.random.choice(
            len(free_cells),
            size=len(invalid),
            replace=True
        )

        selected = free_cells[
            replacement
        ]

        self.particles[
            invalid,
            0
        ] = (
            self.map_origin_x
            + (selected[:, 1] + 0.5)
            * self.map_resolution
        )

        self.particles[
            invalid,
            1
        ] = (
            self.map_origin_y
            + (selected[:, 0] + 0.5)
            * self.map_resolution
        )

        self.particles[
            invalid,
            2
        ] = np.random.uniform(
            -math.pi,
            math.pi,
            len(invalid)
        )

    # ================================================================
    # SCAN CALLBACK
    # ================================================================

    def scan_callback(self, msg):

        self.latest_scan = msg
        self.scan_received = True

    # ================================================================
    # LASER TF
    # ================================================================

    def get_laser_pose(self, scan):

        try:

            transform = (
                self.tf_buffer.lookup_transform(
                    self.base_frame,
                    scan.header.frame_id,
                    rclpy.time.Time()
                )
            )

        except Exception as e:

            self.get_logger().warning(
                'Laser TF unavailable: '
                f'{self.base_frame} -> '
                f'{scan.header.frame_id}: {e}',
                throttle_duration_sec=5.0
            )

            return None

        tx = float(
            transform.transform.translation.x
        )

        ty = float(
            transform.transform.translation.y
        )

        yaw = yaw_from_quaternion(
            transform.transform.rotation
        )

        return tx, ty, yaw

    # ================================================================
    # SENSOR UPDATE
    # ================================================================

    def sensor_update(self):

        if not self.initialized:
            return

        if self.latest_scan is None:
            return

        if self.distance_map is None:
            return

        scan = self.latest_scan

        # --------------------------------------------------------
        # IMPORTANT:
        # Process each LaserScan only once.
        # --------------------------------------------------------

        stamp = (
            scan.header.stamp.sec,
            scan.header.stamp.nanosec
        )

        if (
            self.last_processed_scan_stamp
            == stamp
        ):
            return

        self.last_processed_scan_stamp = stamp

        # --------------------------------------------------------
        # Laser TF
        # --------------------------------------------------------

        laser_pose = self.get_laser_pose(
            scan
        )

        if laser_pose is None:
            return

        laser_x, laser_y, laser_yaw = (
            laser_pose
        )

        # --------------------------------------------------------
        # Laser ranges
        # --------------------------------------------------------

        ranges = np.asarray(
            scan.ranges,
            dtype=np.float64
        )

        if ranges.size == 0:
            return

        min_range = max(
            self.laser_min_range,
            float(scan.range_min)
        )

        max_range = min(
            self.laser_max_range,
            float(scan.range_max)
        )

        # --------------------------------------------------------
        # Valid ranges
        # --------------------------------------------------------

        valid = (
            np.isfinite(ranges)
            & (ranges >= min_range)
            & (ranges <= max_range)
        )

        indices = np.where(
            valid
        )[0]

        if len(indices) == 0:
            return

        # --------------------------------------------------------
        # Select evenly distributed beams
        # --------------------------------------------------------

        if len(indices) > self.laser_beams:

            selected = np.linspace(
                0,
                len(indices) - 1,
                self.laser_beams
            ).astype(np.int32)

            indices = indices[
                selected
            ]

        ranges_used = ranges[
            indices
        ]

        angles_used = (
            float(scan.angle_min)
            + indices
            * float(scan.angle_increment)
            + laser_yaw
        )

        # ========================================================
        # PARTICLE POSES
        # ========================================================

        px = self.particles[:, 0]
        py = self.particles[:, 1]
        pyaw = self.particles[:, 2]

        cp = np.cos(
            pyaw
        )

        sp = np.sin(
            pyaw
        )

        # ========================================================
        # LASER ORIGIN IN MAP
        # ========================================================

        laser_origin_x = (
            px
            + cp * laser_x
            - sp * laser_y
        )

        laser_origin_y = (
            py
            + sp * laser_x
            + cp * laser_y
        )

        # ========================================================
        # BEAM ANGLES
        # ========================================================

        beam_angles = (
            pyaw[:, None]
            + angles_used[None, :]
        )

        # ========================================================
        # PREDICTED LASER ENDPOINTS
        # ========================================================

        endpoint_x = (
            laser_origin_x[:, None]
            + ranges_used[None, :]
            * np.cos(beam_angles)
        )

        endpoint_y = (
            laser_origin_y[:, None]
            + ranges_used[None, :]
            * np.sin(beam_angles)
        )

        # ========================================================
        # WORLD -> MAP CELL
        # ========================================================

        map_x = np.floor(
            (
                endpoint_x
                - self.map_origin_x
            )
            / self.map_resolution
        ).astype(np.int32)

        map_y = np.floor(
            (
                endpoint_y
                - self.map_origin_y
            )
            / self.map_resolution
        ).astype(np.int32)

        inside = (
            (map_x >= 0)
            & (map_x < self.map_width)
            & (map_y >= 0)
            & (map_y < self.map_height)
        )

        # ========================================================
        # DISTANCE TO NEAREST OBSTACLE
        # ========================================================

        # Outside map = very bad measurement.
        distances = np.full(
            map_x.shape,
            2.5,
            dtype=np.float64
        )

        rows, cols = np.where(
            inside
        )

        if len(rows) > 0:

            distances[
                rows,
                cols
            ] = self.distance_map[
                map_y[rows, cols],
                map_x[rows, cols]
            ]

        distances = np.nan_to_num(
            distances,
            nan=2.5,
            posinf=2.5,
            neginf=0.0
        )

        distances = np.clip(
            distances,
            0.0,
            2.5
        )

        # ========================================================
        # LIKELIHOOD FIELD
        # ========================================================

        sigma = max(
            self.laser_sigma,
            0.03
        )

        hit_probability = np.exp(
            -0.5
            * (
                distances / sigma
            ) ** 2
        )

        random_probability = (
            1.0 / max_range
        )

        probabilities = (
            self.laser_z_hit
            * hit_probability
            +
            self.laser_z_rand
            * random_probability
        )

        probabilities = np.clip(
            probabilities,
            1e-12,
            1.0
        )

        # ========================================================
        # ACCUMULATE EVIDENCE FROM ALL BEAMS
        # ========================================================

        log_weights = np.sum(
            np.log(probabilities),
            axis=1
        )

        # --------------------------------------------------------
        # Numerical stabilization
        # --------------------------------------------------------

        max_log = np.max(
            log_weights
        )

        weights = np.exp(
            log_weights - max_log
        )

        weight_sum = np.sum(
            weights
        )

        if (
            not np.isfinite(weight_sum)
            or weight_sum <= 0.0
        ):

            weights = np.full(
                self.num_particles,
                1.0 / self.num_particles
            )

        else:

            weights /= weight_sum

        self.particles[:, 3] = (
            weights
        )

        # ========================================================
        # ESTIMATE
        # ========================================================

        self.update_estimate()

        # ========================================================
        # EFFECTIVE SAMPLE SIZE
        # ========================================================

        ess = (
            1.0
            / np.sum(weights ** 2)
        )

        self.last_ess = ess

        threshold = (
            self.resample_threshold
            * self.num_particles
        )

        if ess < threshold:

            self.systematic_resample()

            self.get_logger().info(
                f'Resampling: ESS={ess:.1f}'
            )

    # ================================================================
    # ESTIMATE POSE
    # ================================================================

    def update_estimate(self):

        weights = (
            self.particles[:, 3]
        )

        weight_sum = np.sum(
            weights
        )

        if (
            not np.isfinite(weight_sum)
            or weight_sum <= 0.0
        ):

            weights = np.full(
                self.num_particles,
                1.0 / self.num_particles
            )

        else:

            weights = (
                weights / weight_sum
            )

        self.estimated_x = float(
            np.sum(
                self.particles[:, 0]
                * weights
            )
        )

        self.estimated_y = float(
            np.sum(
                self.particles[:, 1]
                * weights
            )
        )

        sin_sum = np.sum(
            np.sin(
                self.particles[:, 2]
            )
            * weights
        )

        cos_sum = np.sum(
            np.cos(
                self.particles[:, 2]
            )
            * weights
        )

        self.estimated_yaw = math.atan2(
            sin_sum,
            cos_sum
        )

    # ================================================================
    # SYSTEMATIC RESAMPLING
    # ================================================================

    def systematic_resample(self):

        weights = (
            self.particles[:, 3]
        )

        cumulative = np.cumsum(
            weights
        )

        cumulative[-1] = 1.0

        start = np.random.uniform(
            0.0,
            1.0 / self.num_particles
        )

        positions = (
            start
            + np.arange(
                self.num_particles
            )
            / self.num_particles
        )

        indices = np.searchsorted(
            cumulative,
            positions
        )

        indices = np.clip(
            indices,
            0,
            self.num_particles - 1
        )

        new_particles = (
            self.particles[
                indices
            ].copy()
        )

        new_particles[:, 3] = (
            1.0 / self.num_particles
        )

        self.particles = (
            new_particles
        )

    # ================================================================
    # MAP -> ODOM TF
    # ================================================================

    def publish_map_to_odom(self):

        if not self.odom_received:
            return

        # --------------------------------------------------------
        # T_map_base =
        #       T_map_odom * T_odom_base
        #
        # Therefore:
        #
        # T_map_odom =
        #       T_map_base *
        #       inverse(T_odom_base)
        # --------------------------------------------------------

        map_x = self.estimated_x
        map_y = self.estimated_y
        map_yaw = self.estimated_yaw

        odom_x = self.current_odom_x
        odom_y = self.current_odom_y
        odom_yaw = self.current_odom_yaw

        map_odom_yaw = normalize_angle(
            map_yaw - odom_yaw
        )

        c = math.cos(
            map_odom_yaw
        )

        s = math.sin(
            map_odom_yaw
        )

        map_odom_x = (
            map_x
            - (
                c * odom_x
                - s * odom_y
            )
        )

        map_odom_y = (
            map_y
            - (
                s * odom_x
                + c * odom_y
            )
        )

        qx, qy, qz, qw = (
            quaternion_from_yaw(
                map_odom_yaw
            )
        )

        transform = TransformStamped()

        transform.header.stamp = (
            self.get_clock()
            .now()
            .to_msg()
        )

        transform.header.frame_id = (
            self.map_frame
        )

        transform.child_frame_id = (
            self.odom_frame
        )

        transform.transform.translation.x = (
            map_odom_x
        )

        transform.transform.translation.y = (
            map_odom_y
        )

        transform.transform.translation.z = 0.0

        transform.transform.rotation.x = qx
        transform.transform.rotation.y = qy
        transform.transform.rotation.z = qz
        transform.transform.rotation.w = qw

        self.tf_broadcaster.sendTransform(
            transform
        )

    # ================================================================
    # PARTICLE CLOUD
    # ================================================================

    def publish_particle_cloud(self):

        if not self.initialized:
            return

        msg = PoseArray()

        msg.header.stamp = (
            self.get_clock()
            .now()
            .to_msg()
        )

        msg.header.frame_id = (
            self.map_frame
        )

        poses = []

        for i in range(
            self.num_particles
        ):

            pose = Pose()

            pose.position.x = float(
                self.particles[i, 0]
            )

            pose.position.y = float(
                self.particles[i, 1]
            )

            pose.position.z = 0.0

            qx, qy, qz, qw = (
                quaternion_from_yaw(
                    self.particles[i, 2]
                )
            )

            pose.orientation.x = qx
            pose.orientation.y = qy
            pose.orientation.z = qz
            pose.orientation.w = qw

            poses.append(
                pose
            )

        msg.poses = poses

        self.particle_pub.publish(
            msg
        )

    # ================================================================
    # ESTIMATED POSE
    # ================================================================

    def publish_pose(self):

        if not self.initialized:
            return

        msg = (
            PoseWithCovarianceStamped()
        )

        msg.header.stamp = (
            self.get_clock()
            .now()
            .to_msg()
        )

        msg.header.frame_id = (
            self.map_frame
        )

        msg.pose.pose.position.x = (
            self.estimated_x
        )

        msg.pose.pose.position.y = (
            self.estimated_y
        )

        msg.pose.pose.position.z = 0.0

        qx, qy, qz, qw = (
            quaternion_from_yaw(
                self.estimated_yaw
            )
        )

        msg.pose.pose.orientation.x = qx
        msg.pose.pose.orientation.y = qy
        msg.pose.pose.orientation.z = qz
        msg.pose.pose.orientation.w = qw

        # --------------------------------------------------------
        # Covariance
        # --------------------------------------------------------

        msg.pose.covariance[0] = 0.10
        msg.pose.covariance[7] = 0.10
        msg.pose.covariance[35] = 0.10

        self.pose_pub.publish(
            msg
        )

    # ================================================================
    # MAIN FILTER LOOP
    # ================================================================

    def process_filter(self):

        if not self.initialized:
            return

        if not self.odom_received:
            return

        if not self.scan_received:
            return

        # --------------------------------------------------------
        # Measurement update.
        #
        # sensor_update() itself checks whether this is a NEW scan.
        # --------------------------------------------------------

        self.sensor_update()

        # --------------------------------------------------------
        # Publish
        # --------------------------------------------------------

        self.publish_particle_cloud()

        self.publish_pose()

        self.publish_map_to_odom()


# ================================================================
# MAIN
# ================================================================

def main(args=None):

    rclpy.init(
        args=args
    )

    node = ParticleFilter()

    try:

        rclpy.spin(
            node
        )

    except KeyboardInterrupt:
        pass

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':
    main()
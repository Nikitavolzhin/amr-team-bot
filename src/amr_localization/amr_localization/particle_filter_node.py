import math
import numpy as np

import rclpy
from rclpy.node import Node

from nav_msgs.msg import OccupancyGrid, Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import (
    PoseWithCovarianceStamped,
    PoseArray,
    Pose,
    TransformStamped
)

import tf2_ros
from tf_transformations import (
    euler_from_quaternion,
    quaternion_from_euler
)

from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    DurabilityPolicy
)


class ParticleFilter(Node):

    def __init__(self):
        super().__init__("mcl_particle_filter")

      # we can update the parameters 
        self.N = 200
        self.motion_noise = [0.02, 0.02, 0.02]

        self.laser_x = 0.45
        self.max_range = 5.6
        self.rays = 16

        self.sigma = 0.50
        self.z_hit = 0.90
        self.z_rand = 0.10

        self.resample_threshold = 0.35

        self.min_distance = 0.03
        self.min_angle = 0.03


        self.map = None
        self.free_cells = None
        self.distance_map = None

        self.resolution = None
        self.origin_x = None
        self.origin_y = None
        self.width = None
        self.height = None


        self.particles = None
        self.odom = None
        self.last_odom = None
        self.moved = False

  
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

 
        map_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )


        self.create_subscription(
            OccupancyGrid, "/map",
            self.map_callback, map_qos
        )

        self.create_subscription(
            Odometry, "/odom",
            self.odom_callback, 50
        )

        self.create_subscription(
            LaserScan, "/scan",
            self.scan_callback, 10
        )


        self.create_subscription(
            PoseWithCovarianceStamped, "/initialpose",
            self.initial_pose_callback, 10
        )

        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.create_timer(0.05, self.publish)

        self.get_logger().info("Simple MCL started.")


    def map_callback(self, msg):
        self.map = np.array(msg.data).reshape(
            msg.info.height, msg.info.width
        )

        self.resolution = msg.info.resolution
        self.origin_x = msg.info.origin.position.x
        self.origin_y = msg.info.origin.position.y
        self.width = msg.info.width
        self.height = msg.info.height

        self.free_cells = np.argwhere(
            (self.map >= 0) & (self.map <= 10)
        )

        if self.particles is None:
            self.make_distance_map()
            self.initialize_particles()
            self.get_logger().info(
                f"Map received: {self.width} x {self.height}"
            )

    def make_distance_map(self):
        occupied = np.argwhere(self.map >= 50)

        if len(occupied) == 0:
            self.distance_map = np.full(self.map.shape, 2.0)
            return

        yy, xx = np.indices(self.map.shape)
        distance = np.full(self.map.shape, np.inf)

        for cells in np.array_split(
            occupied, max(1, len(occupied) // 256)
        ):
            cy = cells[:, 0, None, None]
            cx = cells[:, 1, None, None]

            d = (yy - cy) ** 2 + (xx - cx) ** 2
            distance = np.minimum(distance, np.min(d, axis=0))

        self.distance_map = np.minimum(
            np.sqrt(distance) * self.resolution,
            2.0
        )


    def initialize_particles(self):
        self.particles = np.zeros((self.N, 4))

        ids = np.random.randint(
            len(self.free_cells), size=self.N
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
            -math.pi, math.pi, self.N
        )

        self.particles[:, 3] = 1.0 / self.N



    def initial_pose_callback(self, msg):
        if self.particles is None:
            return

        p = msg.pose.pose.position
        q = msg.pose.pose.orientation

        _, _, yaw = euler_from_quaternion([
            q.x, q.y, q.z, q.w
        ])

        self.particles[:, 0] = np.random.normal(
            p.x, 0.20, self.N
        )
        self.particles[:, 1] = np.random.normal(
            p.y, 0.20, self.N
        )
        self.particles[:, 2] = self.normalize(
            np.random.normal(yaw, 0.15, self.N)
        )
        self.particles[:, 3] = 1.0 / self.N

        if self.odom is not None:
            self.last_odom = self.odom

        self.moved = False
        self.get_logger().info("Initial pose set.")


    def odom_callback(self, msg):
        if self.particles is None:
            return

        p = msg.pose.pose.position
        q = msg.pose.pose.orientation

        _, _, yaw = euler_from_quaternion([
            q.x, q.y, q.z, q.w
        ])

        current = (p.x, p.y, yaw)
        self.odom = current

        if self.last_odom is None:
            self.last_odom = current
            return

        old_x, old_y, old_yaw = self.last_odom

        dx = p.x - old_x
        dy = p.y - old_y
        dyaw = self.normalize(yaw - old_yaw)

        distance = math.sqrt(dx * dx + dy * dy)

        if (
            distance < self.min_distance
            and abs(dyaw) < self.min_angle
        ):
            return

        c = math.cos(old_yaw)
        s = math.sin(old_yaw)

        dx = c * dx + s * dy
        dy = -s * dx + c * dy

       
        dx += np.random.normal(
            0, self.motion_noise[0], self.N
        )
        dy += np.random.normal(
            0, self.motion_noise[1], self.N
        )
        dyaw += np.random.normal(
            0, self.motion_noise[2], self.N
        )

        theta = self.particles[:, 2]

        self.particles[:, 0] += (
            dx * np.cos(theta) -
            dy * np.sin(theta)
        )

        self.particles[:, 1] += (
            dx * np.sin(theta) +
            dy * np.cos(theta)
        )

        self.particles[:, 2] = self.normalize(
            theta + dyaw
        )

        self.last_odom = current
        self.moved = True



    def scan_callback(self, msg):
        if (
            self.particles is None
            or self.distance_map is None
            or not self.moved
        ):
            return

        ranges = np.asarray(msg.ranges)

        valid = (
            np.isfinite(ranges)
            & (ranges >= msg.range_min)
            & (ranges <= self.max_range)
        )

        ids = np.where(valid)[0]

        if len(ids) == 0:
            return

        if len(ids) > self.rays:
            ids = ids[
                np.linspace(
                    0, len(ids) - 1,
                    self.rays, dtype=int
                )
            ]

        ranges = ranges[ids]
        angles = (
            msg.angle_min +
            ids * msg.angle_increment
        )

        weights = self.sensor_model(
            ranges, angles
        )

        total = np.sum(weights)

        if total == 0:
            return

        weights /= total
        self.particles[:, 3] = weights

    
        ess = 1.0 / np.sum(weights ** 2)

        if ess < self.resample_threshold * self.N:
            self.resample()

        self.moved = False

    def sensor_model(self, ranges, angles):
        log_weights = np.zeros(self.N)

        for start in range(0, self.N, 100):
            end = min(start + 100, self.N)
            p = self.particles[start:end]

            theta = p[:, 2:3]

            laser_x = (
                p[:, 0:1] +
                self.laser_x * np.cos(theta)
            )

            laser_y = (
                p[:, 1:2] +
                self.laser_x * np.sin(theta)
            )

            ray_angle = theta + angles

            hit_x = (
                laser_x +
                ranges * np.cos(ray_angle)
            )

            hit_y = (
                laser_y +
                ranges * np.sin(ray_angle)
            )

            mx = (
                (hit_x - self.origin_x)
                / self.resolution
            ).astype(int)

            my = (
                (hit_y - self.origin_y)
                / self.resolution
            ).astype(int)

            inside = (
                (mx >= 0) &
                (my >= 0) &
                (mx < self.width) &
                (my < self.height)
            )

            distance = np.full(
                mx.shape, 2.0
            )

            distance[inside] = self.distance_map[
                my[inside], mx[inside]
            ]

            p_hit = np.exp(
                -(distance ** 2) /
                (2 * self.sigma ** 2)
            )

            probability = (
                self.z_hit * p_hit +
                self.z_rand / self.max_range
            )

            probability[~inside] *= 0.05

            log_weights[start:end] = np.sum(
                np.log(
                    np.maximum(
                        probability, 1e-12
                    )
                ),
                axis=1
            )

        return np.exp(
            log_weights - np.max(log_weights)
        )


    def resample(self):
        weights = self.particles[:, 3]
        weights /= np.sum(weights)

        indexes = np.random.choice(
            self.N, self.N,
            replace=True, p=weights
        )

        self.particles = (
            self.particles[indexes].copy()
        )

        self.particles[:, 0] += np.random.normal(
            0, 0.03, self.N
        )
        self.particles[:, 1] += np.random.normal(
            0, 0.03, self.N
        )
        self.particles[:, 2] = self.normalize(
            self.particles[:, 2] +
            np.random.normal(0, 0.04, self.N)
        )

        self.particles[:, 3] = 1.0 / self.N

    def estimate_pose(self):
        weights = self.particles[:, 3]
        weights /= np.sum(weights)

        x = np.sum(self.particles[:, 0] * weights)
        y = np.sum(self.particles[:, 1] * weights)

        yaw = math.atan2(
            np.sum(np.sin(self.particles[:, 2]) * weights),
            np.sum(np.cos(self.particles[:, 2]) * weights)
        )

        return x, y, yaw

    def publish(self):
        if self.particles is None or self.odom is None:
            return

        x, y, yaw = self.estimate_pose()
        stamp = self.get_clock().now().to_msg()

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

        cloud = PoseArray()
        cloud.header.stamp = stamp
        cloud.header.frame_id = "map"

        for particle in self.particles:
            p = Pose()
            p.position.x = particle[0]
            p.position.y = particle[1]

            q = quaternion_from_euler(
                0, 0, particle[2]
            )

            p.orientation.x = q[0]
            p.orientation.y = q[1]
            p.orientation.z = q[2]
            p.orientation.w = q[3]

            cloud.poses.append(p)

        self.cloud_pub.publish(cloud)

        # map -> odom
        ox, oy, oyaw = self.odom
        rotation = self.normalize(yaw - oyaw)

        c = math.cos(rotation)
        s = math.sin(rotation)

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
            0, 0, rotation
        )

        tf.transform.rotation.x = q[0]
        tf.transform.rotation.y = q[1]
        tf.transform.rotation.z = q[2]
        tf.transform.rotation.w = q[3]

        self.tf_broadcaster.sendTransform(tf)

    @staticmethod
    def normalize(angle):
        return np.arctan2(
            np.sin(angle),
            np.cos(angle)
        )


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
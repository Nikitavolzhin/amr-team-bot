import math
import random
from dataclasses import dataclass

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry, OccupancyGrid
from sensor_msgs.msg import LaserScan

from geometry_msgs.msg import Pose
from geometry_msgs.msg import PoseArray
from geometry_msgs.msg import PoseWithCovarianceStamped
from geometry_msgs.msg import Quaternion
from geometry_msgs.msg import TransformStamped

from tf2_ros import TransformBroadcaster

from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy
from rclpy.qos import DurabilityPolicy


@dataclass
class Particle:

    x: float
    y: float
    yaw: float
    weight: float


def quaternion_to_yaw(q):

    sin_yaw = 2.0 * (q.w * q.z + q.x * q.y)
    cos_yaw = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)

    return math.atan2(sin_yaw, cos_yaw)


def yaw_to_quaternion(yaw):

    q = Quaternion()

    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)

    return q


class ParticleFilter(Node):

    def __init__(self):

        super().__init__("particle_filter_node")

        self.number_of_particles = 300 # can be tunes later wwhen we need it

        self.map_data = None
        self.map_width = 0
        self.map_height = 0
        self.map_resolution = 0.0
        self.map_origin = None

        self.scan = None
        self.scan_angle_min = 0.0
        self.scan_angle_increment = 0.0
        self.scan_range_min = 0.0
        self.scan_range_max = 0.0

        self.particles: list[Particle] = []

        self.previous_odom_x = None
        self.previous_odom_y = None
        self.previous_odom_yaw = None

        self.estimated_x = None
        self.estimated_y = None
        self.estimated_yaw = None

        self.scan_count = 0

        self.initial_scan_count = 12

      
        self.resample_every = 6

       
        self.pose_alpha = 0.20

        self.localized = False

        self.tf_broadcaster = TransformBroadcaster(self)

        self.particle_publisher = self.create_publisher(
            PoseArray,
            "/particle_cloud",
            10
        )

        self.pose_publisher = self.create_publisher(
            PoseWithCovarianceStamped,
            "/particle_filter_pose",
            10
        )

        self.map_subscription = self.create_subscription(
            OccupancyGrid,
            "/map",
            self.map_callback,
            self.map_qos()
        )

        self.odom_subscription = self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            10
        )

        self.scan_subscription = self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_callback,
            10
        )

        self.initial_pose_subscription = self.create_subscription(
            PoseWithCovarianceStamped,
            "/initialpose",
            self.initial_pose_callback,
            10
        )

        self.get_logger().info("Particle filter node started.")


    def map_qos(self):

        qos = QoSProfile(depth=1)

        qos.reliability = ReliabilityPolicy.RELIABLE
        qos.durability = DurabilityPolicy.TRANSIENT_LOCAL

        return qos


    def map_callback(self, message):

        if self.map_data is not None:
            return

        self.map_data = list(message.data)

        self.map_width = message.info.width
        self.map_height = message.info.height
        self.map_resolution = message.info.resolution
        self.map_origin = message.info.origin

        self.particles = self.create_random_particles()

        self.publish_particles()

        self.get_logger().info("Map received. Particles are spread over the map.")


    def create_random_particles(self):

        if self.map_data is None or self.map_origin is None:
            return []

        free_cells = []

        for map_y in range(self.map_height):

            for map_x in range(self.map_width):

                index = (map_y * self.map_width+ map_x)

                if self.map_data[index] == 0:

                    free_cells.append((map_x, map_y))


        particles = []

        if not free_cells:
            return particles

        weight = (1.0/ self.number_of_particles)

        for i in range(self.number_of_particles):

            map_x, map_y = random.choice(free_cells)

            x = (self.map_origin.position.x+ (map_x + 0.5)* self.map_resolution)

            y = (self.map_origin.position.y+ (map_y + 0.5)* self.map_resolution)

            yaw = random.uniform(-math.pi,math.pi)

            particles.append(Particle(x=x,y=y,yaw=yaw,weight=weight  ))

        return particles




    def create_particles_around_pose(self,x,y,yaw):

        particles = []

        weight = (1.0/ self.number_of_particles)

        for i in range(
            self.number_of_particles):

            particles.append(Particle(x=x + random.gauss(0.0, 0.10),
                    y=y + random.gauss(0.0, 0.10),
                    yaw=yaw + random.gauss(0.0, 0.15),
                    weight=weight
                )
            )

        return particles





    def odom_callback(self, message):

        x = message.pose.pose.position.x
        y = message.pose.pose.position.y

        yaw = quaternion_to_yaw(
            message.pose.pose.orientation
        )

        if self.previous_odom_x is None or self.previous_odom_y is None or self.previous_odom_yaw is None:

            self.previous_odom_x = x
            self.previous_odom_y = y
            self.previous_odom_yaw = yaw

            return

        dx = x - self.previous_odom_x
        dy = y - self.previous_odom_y

        dyaw = yaw - self.previous_odom_yaw

        dyaw = math.atan2(math.sin(dyaw),math.cos(dyaw))

        distance = math.sqrt(dx * dx + dy * dy)

        # Ignore tiny odometry noise while stopped.
        if (distance > 0.005 or abs(dyaw) > 0.015 ):

            self.motion_update(
                dx,
                dy,
                dyaw
            )




        self.previous_odom_x = x
        self.previous_odom_y = y
        self.previous_odom_yaw = yaw

        self.publish_particles()


    def motion_update(self,dx,dy,dyaw):

        if not self.particles:
            return
        
        if self.previous_odom_yaw is None:
            return


        old_yaw = self.previous_odom_yaw

        local_dx = (math.cos(old_yaw) * dx+ math.sin(old_yaw) * dy)

        local_dy = (-math.sin(old_yaw) * dx+ math.cos(old_yaw) * dy
        )

        distance = math.sqrt(dx * dx + dy * dy )

        position_noise = min(0.015,0.003 + 0.02 * distance)

        yaw_noise = min(0.02,0.003 + 0.02 * abs(dyaw))

        for p in self.particles:

            move_x = (local_dx+ random.gauss(0.0,position_noise))

            move_y = (local_dy+ random.gauss(0.0,position_noise))

            move_yaw = (dyaw+ random.gauss(0.0,yaw_noise))

            p.x += (move_x * math.cos(p.yaw)- move_y * math.sin(p.yaw))

            p.y += (move_x * math.sin(p.yaw)+ move_y * math.cos(p.yaw))

            p.yaw += move_yaw

            p.yaw = math.atan2(math.sin(p.yaw),math.cos(p.yaw))


    def scan_callback(self, message):

        self.scan = list(message.ranges)

        self.scan_angle_min = message.angle_min
        self.scan_angle_increment = message.angle_increment
        self.scan_range_min = message.range_min
        self.scan_range_max = message.range_max

        if (not self.particles or self.map_data is None):


            return

        self.scan_count += 1

        self.update_weights()



        if (self.scan_count >= self.initial_scan_count and self.scan_count % self.resample_every == 0):

            self.resample_particles()

            self.localized = True

            self.estimate_pose()

            self.publish_pose()

            self.publish_map_to_odom()



        self.publish_particles()





    def get_map_cell(self, x, y):


        if self.map_data is None or self.map_origin is None:
            return None

        map_x = int((x- self.map_origin.position.x)/ self.map_resolution)

        map_y = int((y- self.map_origin.position.y)/ self.map_resolution)

        if (map_x < 0 or map_x >= self.map_width or map_y < 0 or map_y >= self.map_height):

            return None

        index = (map_y * self.map_width + map_x)




        return self.map_data[index]






    def particle_weight(self, p):

        if not self.scan:
            return 1.0

        score = 0.0
        valid_rays = 0

        number_of_rays = 40

        step = max(1,len(self.scan)// number_of_rays)

        for index in range(0,len(self.scan),step):

            distance = self.scan[index]

            if math.isnan(distance):




                continue

            if math.isinf(distance):


                continue

            if (distance < self.scan_range_min or distance > self.scan_range_max):


                continue



            angle = (self.scan_angle_min+ index * self.scan_angle_increment)

            obstacle_x = (p.x+ distance* math.cos(p.yaw + angle))

            obstacle_y = (p.y+ distance* math.sin(p.yaw + angle))

            cell = self.get_map_cell(obstacle_x,obstacle_y)



            if cell is None:


                continue

            valid_rays += 1

            if cell >= 50:

                score += 1.0

            elif cell == 0:

                score -= 0.35

        if valid_rays == 0:
            return 0.001

        score /= valid_rays

        return (0.20+ math.exp(2.5 * score))


    def update_weights(self):

        for p in self.particles:

            p.weight = self.particle_weight(p)

        self.normalize_weights()


    def normalize_weights(self):

        total = sum(
            p.weight
            for p in self.particles
        )



        if total <= 0.0:

            weight = (1.0/ self.number_of_particles)

            for p in self.particles:

                p.weight = weight

            return

        for p in self.particles:

            p.weight /= total


    def estimate_pose(self):

        if not self.particles:
            return

        x = 0.0
        y = 0.0
        sin_yaw = 0.0
        cos_yaw = 0.0

        for p in self.particles:

            x += p.x * p.weight
            y += p.y * p.weight

            sin_yaw += (math.sin(p.yaw)* p.weight)

            cos_yaw += (math.cos(p.yaw)* p.weight)

        yaw = math.atan2(sin_yaw,cos_yaw)

        if not self.localized:


            self.estimated_x = None
            self.estimated_y = None
            self.estimated_yaw = None

            return

        if self.estimated_x is None or self.estimated_y is None or self.estimated_yaw is None:

            self.estimated_x = x
            self.estimated_y = y
            self.estimated_yaw = yaw

            return

        self.estimated_x = (0.80 * self.estimated_x+ 0.20 * x)

        self.estimated_y = (0.80 * self.estimated_y+ 0.20 * y)

        yaw_difference = math.atan2(math.sin(yaw - self.estimated_yaw),math.cos(yaw - self.estimated_yaw))

        self.estimated_yaw += (0.20 * yaw_difference)

        self.estimated_yaw = math.atan2(math.sin(self.estimated_yaw),math.cos(self.estimated_yaw))


    def publish_pose(self):

        if self.estimated_x is None:
            return

        pose = PoseWithCovarianceStamped()

        pose.header.stamp = (self.get_clock().now().to_msg())

        pose.header.frame_id = "map"

        pose.pose.pose.position.x = self.estimated_x
        pose.pose.pose.position.y = self.estimated_y
        pose.pose.pose.position.z = 0.0

        pose.pose.pose.orientation = (yaw_to_quaternion(self.estimated_yaw))

        pose.pose.covariance[0] = 0.02
        pose.pose.covariance[7] = 0.02
        pose.pose.covariance[35] = 0.05

        self.pose_publisher.publish(pose)





    def resample_particles(self):

        if not self.particles:
            return

        old_particles = self.particles

        new_particles = []

        weights = [p.weight
            for p in old_particles
        ]

        total = sum(weights)

        if total <= 0.0:
            return

        step = 1.0 / self.number_of_particles

        start = random.uniform(0.0,step)

        cumulative = weights[0]
        index = 0

        for i in range(self.number_of_particles):

            target = (start+ i * step)

            while (target > cumulative and index < len(old_particles) - 1):

                index += 1
                cumulative += weights[index]



            selected = old_particles[index]

            new_particles.append(
                Particle(x=selected.x+ random.gauss(0.0,0.015),y=selected.y+ random.gauss(0.0,0.015),

                yaw=selected.yaw+ random.gauss(0.0,0.02), weight=(1.0/ self.number_of_particles)))
            

        self.particles = new_particles


    def initial_pose_callback(self, message):

        x = message.pose.pose.position.x
        y = message.pose.pose.position.y

        yaw = quaternion_to_yaw(message.pose.pose.orientation)

        self.particles = (self.create_particles_around_pose(x,y,yaw))

        self.estimated_x = x
        self.estimated_y = y
        self.estimated_yaw = yaw

        self.localized = True

        self.publish_pose()
        self.publish_particles()
        self.publish_map_to_odom()

        self.get_logger().info("Initial pose received- HURAAAAAAAAH.")


    def publish_particles(self):

        if not self.particles:



            return

        cloud = PoseArray()

        cloud.header.stamp = (self.get_clock().now().to_msg())

        cloud.header.frame_id = "map"

        poses = []

        for p in self.particles:

            pose = Pose()

            pose.position.x = p.x
            pose.position.y = p.y
            pose.position.z = 0.0

            pose.orientation = yaw_to_quaternion(p.yaw)

            poses.append(pose)

        cloud.poses = poses

        self.particle_publisher.publish(cloud)


    def publish_map_to_odom(self):

        if (
            not self.localized
            or self.estimated_x is None
            or self.estimated_y is None
            or self.estimated_yaw is None
            or self.previous_odom_x is None
            or self.previous_odom_y is None
            or self.previous_odom_yaw is None
        ):
            return
        

        map_odom_yaw = (self.estimated_yaw- self.previous_odom_yaw)

        map_odom_yaw = math.atan2(math.sin(map_odom_yaw),math.cos(map_odom_yaw))

        cos_yaw = math.cos(map_odom_yaw)

        sin_yaw = math.sin(map_odom_yaw)

        map_odom_x = (self.estimated_x- (cos_yaw * self.previous_odom_x- sin_yaw * self.previous_odom_y))

        map_odom_y = (self.estimated_y- (sin_yaw * self.previous_odom_x+ cos_yaw * self.previous_odom_y))

        transform = TransformStamped()


        transform.header.stamp = (self.get_clock().now().to_msg())

        transform.header.frame_id = "map"
        transform.child_frame_id = "odom"

        transform.transform.translation.x = map_odom_x
        transform.transform.translation.y = map_odom_y
        transform.transform.translation.z = 0.0

        transform.transform.rotation = (yaw_to_quaternion(map_odom_yaw))

        self.tf_broadcaster.sendTransform(transform )


def main(args=None):

    rclpy.init(args=args)

    node = ParticleFilter()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":

    main()
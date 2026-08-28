import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.duration import Duration

from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import OccupancyGrid

from tf2_ros import Buffer, TransformListener

import numpy as np
import math
import cv2
import oss
"""Compute learning odometry from measured wheel joint angles, without TF."""
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import JointState
from nav_msgs.msg import Odometry
from .kinematics import integrate_pose, WHEEL_RADIUS, WHEEL_SEPARATION


class EncoderOdometry(Node):
    def __init__(self):
        super().__init__('encoder_odometry')
        self.radius = self.declare_parameter('wheel_radius', WHEEL_RADIUS).value
        self.separation = self.declare_parameter('wheel_separation', WHEEL_SEPARATION).value
        if self.radius <= 0 or self.separation <= 0:
            raise ValueError('Wheel geometry must be positive')
        self.publisher = self.create_publisher(Odometry, '/wheel/odom', 10)
        self.create_subscription(JointState, '/joint_states', self.update, qos_profile_sensor_data)
        self.previous = None
        self.pose = (0.0, 0.0, 0.0)

    def update(self, msg):
        angles = dict(zip(msg.name, msg.position))
        try:
            left = (angles['front_left_wheel_joint'] + angles['rear_left_wheel_joint']) / 2
            right = (angles['front_right_wheel_joint'] + angles['rear_right_wheel_joint']) / 2
        except KeyError:
            return
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if not all(math.isfinite(v) for v in (left, right, stamp)):
            return
        current = (left, right, stamp)
        if self.previous is None:
            self.previous = current
            return
        old_left, old_right, old_stamp = self.previous
        dt = stamp - old_stamp
        if dt <= 0:
            if dt < 0:  # Simulation clock reset: discard old encoder baseline.
                self.previous = current
                self.pose = (0.0, 0.0, 0.0)
            return
        dl, dr = (left - old_left) * self.radius, (right - old_right) * self.radius
        self.previous = current
        self.pose = integrate_pose(*self.pose, dl, dr, self.separation)
        x, y, yaw = self.pose
        odom = Odometry()
        odom.header = msg.header
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        odom.pose.pose.position.x, odom.pose.pose.position.y = x, y
        odom.pose.pose.orientation.z = math.sin(yaw / 2)
        odom.pose.pose.orientation.w = math.cos(yaw / 2)
        odom.twist.twist.linear.x = (dr + dl) / (2 * dt)
        odom.twist.twist.angular.z = (dr - dl) / (self.separation * dt)
        for index, variance in zip((0, 7, 14, 21, 28, 35), (0.02, 0.02, 1e6, 1e6, 1e6, 0.05)):
            odom.pose.covariance[index] = variance
            odom.twist.covariance[index] = variance
        self.publisher.publish(odom)


def main(args=None):
    rclpy.init(args=args)
    node = EncoderOdometry()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

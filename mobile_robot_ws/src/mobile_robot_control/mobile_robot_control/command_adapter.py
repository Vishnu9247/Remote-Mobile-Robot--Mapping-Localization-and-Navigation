"""Convert teleop/Nav2 Twist to the Jazzy controller's TwistStamped."""
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped
from std_msgs.msg import Bool
from .kinematics import limit_command


class CommandAdapter(Node):
    def __init__(self):
        super().__init__('command_adapter')
        self.publisher = self.create_publisher(TwistStamped, '/diff_drive_controller/cmd_vel', 10)
        self.create_subscription(Twist, '/cmd_vel', self.command, 10)
        self.create_subscription(Bool, '/emergency_stop', self.stop, 10)
        self.last_command = (0.0, 0.0)
        self.received_at = 0.0
        self.stopped = False
        self.create_timer(0.05, self.publish)

    def command(self, msg):
        if not self.stopped:
            self.last_command = limit_command(msg.linear.x, msg.angular.z)
            self.received_at = time.monotonic()

    def stop(self, msg):
        self.stopped = msg.data
        self.last_command = (0.0, 0.0)
        self.received_at = 0.0  # Never resume a pre-stop command.
        self.publish()

    def publish(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        if not self.stopped and time.monotonic() - self.received_at < 0.3:
            msg.twist.linear.x, msg.twist.angular.z = self.last_command
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CommandAdapter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.last_command = (0.0, 0.0)
        if rclpy.ok():
            node.publish()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

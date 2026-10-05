"""Send one map-frame goal; reports acceptance and the actual action result."""
import argparse
import math
import time
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus
from .goals import validate_goal, make_goal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('x', type=float)
    parser.add_argument('y', type=float)
    parser.add_argument('theta', type=float, help='Yaw in radians')
    parser.add_argument('--timeout', type=float, default=180.0)
    options, ros_args = parser.parse_known_args()
    values = validate_goal({'x': options.x, 'y': options.y, 'theta': options.theta})
    if not math.isfinite(options.timeout) or options.timeout <= 0:
        parser.error('--timeout must be finite and positive')
    # Keep the ROS context alive while handling Ctrl+C and canceling the goal.
    rclpy.init(args=ros_args, signal_handler_options=SignalHandlerOptions.NO)
    node = Node('send_goal')
    client = ActionClient(node, NavigateToPose, '/navigate_to_pose')
    try:
        if not client.wait_for_server(timeout_sec=10.0):
            raise RuntimeError('Nav2 action server unavailable; start navigation and initialize AMCL')
        future = client.send_goal_async(make_goal(*values, node.get_clock().now().to_msg()))
        rclpy.spin_until_future_complete(node, future, timeout_sec=10.0)
        if not future.done():
            raise RuntimeError('Timed out waiting for goal acceptance')
        handle = future.result()
        if not handle.accepted:
            raise RuntimeError('Nav2 rejected the goal')
        result = handle.get_result_async()
        deadline = time.monotonic() + options.timeout
        try:
            while rclpy.ok() and not result.done() and time.monotonic() < deadline:
                rclpy.spin_once(node, timeout_sec=0.1)
        except KeyboardInterrupt:
            cancel = handle.cancel_goal_async()
            rclpy.spin_until_future_complete(node, cancel, timeout_sec=2.0)
            raise
        if not result.done():
            cancel = handle.cancel_goal_async()
            rclpy.spin_until_future_complete(node, cancel, timeout_sec=2.0)
            raise RuntimeError('Navigation timed out; cancellation requested')
        if result.result().status != GoalStatus.STATUS_SUCCEEDED:
            raise RuntimeError(f'Navigation ended with status {result.result().status}')
        print('Goal reached.')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

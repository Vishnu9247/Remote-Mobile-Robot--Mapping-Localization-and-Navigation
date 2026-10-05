"""Small, ROS-independent validation helper for CLI and HTTP goals."""
import math


def validate_goal(data):
    if not isinstance(data, dict) or set(data) != {'x', 'y', 'theta'}:
        raise ValueError('Provide exactly x, y, theta (metres, metres, radians)')
    values = tuple(data[key] for key in ('x', 'y', 'theta'))
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError('Goal coordinates must be finite numbers')
    return tuple(float(v) for v in values)


def make_goal(x, y, theta, stamp):
    from nav2_msgs.action import NavigateToPose
    goal = NavigateToPose.Goal()
    goal.pose.header.frame_id = 'map'
    goal.pose.header.stamp = stamp
    goal.pose.pose.position.x = x
    goal.pose.pose.position.y = y
    goal.pose.pose.orientation.z = math.sin(theta / 2)
    goal.pose.pose.orientation.w = math.cos(theta / 2)
    return goal

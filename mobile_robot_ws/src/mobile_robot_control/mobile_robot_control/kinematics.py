"""Pure Python differential-drive maths; all distances are metres."""
import math

WHEEL_RADIUS = 0.060
WHEEL_SEPARATION = 0.246


def wheel_speeds(linear, angular, radius=WHEEL_RADIUS, separation=WHEEL_SEPARATION):
    """Body speed (m/s, rad/s) -> left and right wheel speeds (rad/s)."""
    if radius <= 0 or separation <= 0:
        raise ValueError('Wheel radius and separation must be positive')
    return ((linear - angular * separation / 2) / radius,
            (linear + angular * separation / 2) / radius)


def ticks_to_radians(ticks, ticks_per_revolution):
    """Resolution must include gearbox ratio and quadrature counting."""
    if ticks_per_revolution <= 0:
        raise ValueError('Encoder resolution must be positive')
    return ticks * 2 * math.pi / ticks_per_revolution


def integrate_pose(x, y, yaw, left_distance, right_distance, separation=WHEEL_SEPARATION):
    """Exact constant-curvature integration over one encoder interval."""
    if separation <= 0:
        raise ValueError('Wheel separation must be positive')
    distance = (right_distance + left_distance) / 2
    turn = (right_distance - left_distance) / separation
    scale = 1.0 if abs(turn) < 1e-9 else math.sin(turn / 2) / (turn / 2)
    x += distance * scale * math.cos(yaw + turn / 2)
    y += distance * scale * math.sin(yaw + turn / 2)
    yaw = math.atan2(math.sin(yaw + turn), math.cos(yaw + turn))
    return x, y, yaw


def limit_command(linear, angular, max_linear=0.20, max_angular=0.8, max_wheel=5.0):
    """Scale both speeds together to respect motor speed and preserve curvature."""
    if not math.isfinite(linear) or not math.isfinite(angular):
        return 0.0, 0.0
    left, right = wheel_speeds(linear, angular)
    scale = max(1.0, abs(linear) / max_linear, abs(angular) / max_angular,
                abs(left) / max_wheel, abs(right) / max_wheel)
    return linear / scale, angular / scale

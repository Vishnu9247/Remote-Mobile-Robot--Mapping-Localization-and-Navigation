"""Run this first: ros2 run mobile_robot_control kinematics_demo."""
import argparse
import math
from .kinematics import wheel_speeds, ticks_to_radians, WHEEL_RADIUS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--linear', type=float, default=0.2)
    parser.add_argument('--angular', type=float, default=0.0)
    parser.add_argument('--ticks', type=int, default=2048)
    parser.add_argument('--resolution', type=int, default=2048,
                        help='Learning example; actual servo encoder resolution is unknown')
    args = parser.parse_args()
    left, right = wheel_speeds(args.linear, args.angular)
    print(f'Wheel rad/s: left={left:.3f}, right={right:.3f}')
    print(f'Wheel RPM: left={left*60/(2*math.pi):.2f}, right={right*60/(2*math.pi):.2f}')
    print(f'Encoder example distance: {WHEEL_RADIUS*ticks_to_radians(args.ticks, args.resolution):.4f} m')
    print('Turning radius: ' + (f'{args.linear/args.angular:.3f} m' if args.angular else 'straight line'))


if __name__ == '__main__':
    main()

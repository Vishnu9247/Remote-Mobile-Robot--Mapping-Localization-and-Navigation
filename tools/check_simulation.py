"""Read-only Ubuntu smoke check while simulation.launch.xml is running."""
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import JointState, LaserScan, Imu, Image, CameraInfo
from nav_msgs.msg import Odometry
from tf2_ros import Buffer, TransformListener


def main():
    rclpy.init()
    node = Node('simulation_smoke_check')
    node.set_parameters([rclpy.parameter.Parameter('use_sim_time', value=True)])
    seen = {}
    topics = {'/joint_states': JointState, '/scan': LaserScan, '/imu/data': Imu,
              '/camera/image_raw': Image, '/camera/camera_info': CameraInfo,
              '/wheel/odom': Odometry, '/diff_drive_controller/odom': Odometry, '/odom': Odometry}
    subscriptions = [node.create_subscription(cls, topic, lambda msg, key=topic: seen.__setitem__(key, msg),
                                              qos_profile_sensor_data) for topic, cls in topics.items()]
    buffer = Buffer()
    listener = TransformListener(buffer, node)
    deadline = time.monotonic() + 20
    valid_tf = False
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
        valid_tf = all(buffer.can_transform('odom', target, rclpy.time.Time())
                       for target in ('base_link', 'lidar_link', 'imu_link', 'camera_optical_frame'))
        if len(seen) == len(topics) and valid_tf:
            break
    errors = []
    for topic in topics:
        if topic not in seen:
            errors.append(f'No messages: {topic}')
    if not valid_tf:
        errors.append('Missing odom/base/sensor TF chain')
    expected_frames = {'/scan': 'lidar_link', '/imu/data': 'imu_link',
                       '/camera/image_raw': 'camera_optical_frame'}
    for topic, frame in expected_frames.items():
        if topic in seen and seen[topic].header.frame_id != frame:
            errors.append(f'{topic}: expected frame {frame}, got {seen[topic].header.frame_id}')
    if '/joint_states' in seen:
        expected = {f'{end}_{side}_wheel_joint' for end in ('front', 'rear') for side in ('left', 'right')}
        if not expected.issubset(seen['/joint_states'].name):
            errors.append('Missing one or more wheel joints')
    node.destroy_node()
    rclpy.shutdown()
    if errors:
        raise SystemExit('\n'.join(errors))
    print('PASS: wheel feedback, both odometry implementations, EKF, sensors and TF received.')
    print('Next verify driving, mapping, AMCL initialization, obstacle stopping and goal arrival.')


if __name__ == '__main__':
    main()

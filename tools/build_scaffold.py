"""Create package metadata and convert the supplied print STLs to ROS metres.

Run from the repository root. Existing CAD is never changed.
"""
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'mobile_robot_ws' / 'src'
DEPS = {
    'description': ['robot_state_publisher', 'joint_state_publisher_gui', 'rviz2', 'xacro'],
    'gazebo': ['ros_gz_sim', 'ros_gz_bridge', 'gz_ros2_control', 'mobile_robot_description', 'mobile_robot_control'],
    'control': ['rclpy', 'geometry_msgs', 'sensor_msgs', 'nav_msgs', 'std_msgs', 'controller_manager', 'diff_drive_controller', 'joint_state_broadcaster'],
    'localization': ['robot_localization', 'slam_toolbox'],
    'navigation': ['nav2_bringup', 'nav2_simple_commander', 'nav2_msgs', 'rclpy', 'geometry_msgs', 'action_msgs'],
    'bringup': ['mobile_robot_description', 'mobile_robot_gazebo', 'mobile_robot_control', 'mobile_robot_localization', 'mobile_robot_navigation', 'teleop_twist_keyboard'],
}
for short, deps in DEPS.items():
    name = 'mobile_robot_' + short
    folder = SRC / name
    folder.mkdir(parents=True, exist_ok=True)
    for sub in ['launch', 'config']:
        (folder / sub).mkdir(exist_ok=True)
    python_package = short in ('control', 'navigation')
    build_type = 'ament_python' if python_package else 'ament_cmake'
    xml = '\n'.join(f'  <exec_depend>{dep}</exec_depend>' for dep in deps + ['launch_ros', 'launch_xml'])
    (folder / 'package.xml').write_text(f'''<?xml version="1.0"?>
<package format="3">
  <name>{name}</name><version>0.1.0</version>
  <description>CAD-based four-wheel mobile robotics learning project.</description>
  <maintainer email="maintainer@example.com">Robot project maintainer</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>{build_type}</buildtool_depend>
{xml}
  <export><build_type>{build_type}</build_type></export>
</package>
''', encoding='utf-8')
    if python_package:
        (folder / name).mkdir(exist_ok=True)
        (folder / name / '__init__.py').touch()
        (folder / 'resource').mkdir(exist_ok=True)
        (folder / 'resource' / name).touch()
        executables = {'control': ['command_adapter', 'encoder_odometry', 'kinematics_demo'],
                       'navigation': ['send_goal', 'mission_api']}[short]
        entries = [f'{entry} = {name}.{entry}:main' for entry in executables]
        (folder / 'setup.py').write_text(f'''from setuptools import setup
from pathlib import Path
package_name = '{name}'
data_files = [('share/ament_index/resource_index/packages', ['resource/' + package_name]),
              ('share/' + package_name, ['package.xml'])]
for directory in ['launch', 'config', 'maps']:
    for path in Path(directory).rglob('*'):
        if path.is_file():
            data_files.append(('share/' + package_name + '/' + str(path.parent), [str(path)]))
setup(name=package_name, version='0.1.0', packages=[package_name],
      data_files=data_files, install_requires=['setuptools'], zip_safe=True,
      maintainer='Robot project maintainer', maintainer_email='maintainer@example.com',
      description='Simple Python robot learning nodes', license='Apache-2.0',
      entry_points={{'console_scripts': {entries!r}}})
''', encoding='utf-8')
        (folder / 'setup.cfg').write_text(f'[develop]\nscript_dir=$base/lib/{name}\n[install]\ninstall_scripts=$base/lib/{name}\n')
    else:
        directories = {'description': 'launch urdf meshes rviz',
                       'gazebo': 'launch config worlds',
                       'localization': 'launch config', 'bringup': 'launch'}[short]
        for directory in directories.split():
            (folder / directory).mkdir(exist_ok=True)
        (folder / 'CMakeLists.txt').write_text(f'''cmake_minimum_required(VERSION 3.8)
project({name})
find_package(ament_cmake REQUIRED)
install(DIRECTORY {directories} DESTINATION share/${{PROJECT_NAME}})
ament_package()
''')

# Print files have shifted origins. Centre each mesh before its URDF placement.
# This retains all facets, and changes only vertex units/origin, not CAD source.
meshes = SRC / 'mobile_robot_description' / 'meshes'
for part in ['P01_deck_front', 'P02_deck_rear', 'P08_wheel_rim', 'P09_TPU_tyre', 'P10_sensor_platform']:
    raw = bytearray((ROOT / 'CAD Files' / 'robot_redesign_R1' / 'STL' / (part + '.stl')).read_bytes())
    count = struct.unpack_from('<I', raw, 80)[0]
    assert len(raw) == 84 + 50 * count
    vertices = [struct.unpack_from('<3f', raw, 84 + 50 * i + 12 + 12 * j)
                for i in range(count) for j in range(3)]
    centre = [(min(v[k] for v in vertices) + max(v[k] for v in vertices)) / 2 for k in range(3)]
    for i in range(count):
        for j in range(3):
            offset = 84 + 50 * i + 12 + 12 * j
            vertex = struct.unpack_from('<3f', raw, offset)
            struct.pack_into('<3f', raw, offset, *[(vertex[k] - centre[k]) / 1000 for k in range(3)])
    (meshes / (part + '.stl')).write_bytes(raw)
print('Six packages created; five centred metre-scale CAD meshes converted.')

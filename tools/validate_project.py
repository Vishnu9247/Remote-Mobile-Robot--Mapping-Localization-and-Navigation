"""Static verification; requires PyYAML and Xacro, but no ROS/Gazebo runtime.

On Ubuntu: source ROS, then python3 tools/validate_project.py.
On Windows: optionally install PyYAML and Xacro into .validation-deps.
"""
from pathlib import Path
import ast
import re
import struct
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'mobile_robot_ws/src'
if sys.platform == 'win32' and (ROOT / '.validation-deps').exists():
    sys.path.insert(0, str(ROOT / '.validation-deps'))
import yaml
import xacro
import xacro.substitution_args


def main():
    counts = {'python': 0, 'xml': 0, 'yaml': 0, 'meshes': 0}
    for path in list(SRC.rglob('*.py')) + list((ROOT / 'tools').glob('*.py')):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        counts['python'] += 1
    for pattern in ('*.xml', '*.xacro', '*.sdf'):
        for path in SRC.rglob(pattern):
            ET.parse(path)
            counts['xml'] += 1
            for package, suffix in re.findall(r'\$\(find-pkg-share (mobile_robot_\w+)\)([A-Za-z0-9_./-]*)', path.read_text()):
                assert (SRC / package / suffix.lstrip('/')).exists(), (path, package, suffix)
    for path in list(SRC.rglob('*.yaml')) + list(SRC.rglob('*.rviz')):
        assert yaml.safe_load(path.read_text()), path
        counts['yaml'] += 1
    for path in (SRC / 'mobile_robot_description/meshes').glob('*.stl'):
        raw = path.read_bytes()
        count = struct.unpack_from('<I', raw, 80)[0]
        assert len(raw) == 84 + 50 * count
        vertices = [struct.unpack_from('<3f', raw, 84 + 50*i + 12 + 12*j) for i in range(count) for j in range(3)]
        assert max(abs(v) for vertex in vertices for v in vertex) < 0.2
        counts['meshes'] += 1
    # Only substitute the package-share lookup when ROS is unavailable.
    # The actual Xacro evaluator expands all expressions/macros normally.
    try:
        import ament_index_python
    except ImportError:
        xacro.substitution_args._eval_find = lambda package: str(SRC / package)
    for simulation in ('false', 'true'):
        document = xacro.process_file(str(SRC / 'mobile_robot_description/urdf/robot.urdf.xacro'),
                                      mappings={'simulation': simulation})
        robot = ET.fromstring(document.toxml())
        links = {link.attrib['name'] for link in robot.findall('link')}
        joints = robot.findall('joint')
        assert len(links) == 9 and len(joints) == 8
        children = [joint.find('child').attrib['link'] for joint in joints]
        assert len(children) == len(set(children))
        assert links - set(children) == {'base_link'}
        for joint in joints:
            assert joint.find('parent').attrib['link'] in links
            assert joint.find('child').attrib['link'] in links
        if simulation == 'true':
            assert len(robot.find('ros2_control').findall('joint')) == 4
            assert len(robot.findall('.//sensor')) == 3
            bridges = yaml.safe_load((SRC / 'mobile_robot_gazebo/config/bridge.yaml').read_text())
            bridge_topics = {bridge['gz_topic_name'] for bridge in bridges}
            for sensor in robot.findall('.//sensor'):
                assert sensor.findtext('topic') in bridge_topics, sensor.attrib['name']
                assert sensor.findtext('gz_frame_id') in links
        else:
            assert robot.find('ros2_control') is None
    controllers = yaml.safe_load((SRC / 'mobile_robot_control/config/controllers.yaml').read_text())
    drive = controllers['diff_drive_controller']['ros__parameters']
    assert drive['wheel_radius'] == 0.060 and drive['wheel_separation'] == 0.246
    assert drive['enable_odom_tf'] is False and drive['open_loop'] is False
    nav = yaml.safe_load((SRC / 'mobile_robot_navigation/config/nav2.yaml').read_text())
    launch = ET.parse(SRC / 'mobile_robot_navigation/launch/navigation.launch.xml').getroot()
    for node in launch.findall('node'):
        for param in node.findall('param'):
            if param.attrib.get('from') == '$(var params_file)':
                assert param.attrib.get('allow_substs') == 'true'
    for costmap in ('local_costmap', 'global_costmap'):
        assert nav[costmap][costmap]['ros__parameters']['use_sim_time'] == '$(var use_sim_time)'
        footprint = ast.literal_eval(nav[costmap][costmap]['ros__parameters']['footprint'])
        assert max(point[0] for point in footprint) >= 0.155
        assert max(point[1] for point in footprint) >= 0.135
    for folder in SRC.iterdir():
        package = ET.parse(folder / 'package.xml').getroot()
        assert package.findtext('name') == folder.name
        cmake = folder / 'CMakeLists.txt'
        if cmake.exists():
            # Git omits empty folders; every installed directory needs content.
            installs = re.findall(r'install\(DIRECTORY\s+(.*?)\s+DESTINATION', cmake.read_text(), re.DOTALL)
            for directories in installs:
                for directory in directories.split():
                    target = folder / directory
                    assert target.is_dir(), f'Missing CMake install directory: {target}'
                    assert any(path.is_file() for path in target.rglob('*')), f'Empty CMake install directory: {target}'
    print('PASS:', counts, '; both Xacro modes, TF tree, wheel interfaces, geometry and footprint')
    print('This is static validation, not a ROS launch or Gazebo physics test.')


if __name__ == '__main__':
    main()

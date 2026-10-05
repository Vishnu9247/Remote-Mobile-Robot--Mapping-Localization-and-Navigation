from setuptools import setup
from pathlib import Path
package_name = 'mobile_robot_control'
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
      entry_points={'console_scripts': ['command_adapter = mobile_robot_control.command_adapter:main', 'encoder_odometry = mobile_robot_control.encoder_odometry:main', 'kinematics_demo = mobile_robot_control.kinematics_demo:main']})

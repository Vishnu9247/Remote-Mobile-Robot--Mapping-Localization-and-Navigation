# CAD-based mobile robot: ROS 2 Jazzy + Gazebo Harmonic

A staged learning project for **Ubuntu 24.04**, with simple Python nodes and
XML launch files. It follows your plan from kinematics through simulated
navigation and a local mission API. Existing CAD files are preserved.

**Your CAD is a four-wheel skid-steer robot**, not a two-wheel robot with a
caster. This project matches the CAD: 60 mm wheel radius, 246 mm track,
190 mm wheelbase, four HX-30HM wheel modules. Each side's two wheels receive
the same velocity command. See [robot dimensions and maths](docs/ROBOT_DESIGN.md).

**Validation status:** Python maths/input tests and static XML/YAML/Xacro/mesh
checks pass on Windows. ROS, Gazebo physics, sensor streaming, SLAM, and Nav2
have not been run here. Follow the acceptance checks below on Ubuntu before
treating the simulation as verified. Hardware phases require actual components
and measurements; see [hardware integration](docs/HARDWARE.md).

## Folder layout

```text
CAD Files/                    Original STEP/STL, build source and mechanical guide
docs/                         Maths, hardware plan and verification record
tools/                        CAD conversion, maths tests and validation tools
mobile_robot_ws/src/
  mobile_robot_description/   CAD meshes, Xacro, RViz and display launch
  mobile_robot_gazebo/        Harmonic world, sensor bridge and spawn launch
  mobile_robot_control/       Python kinematics, command adapter, encoder odometry
  mobile_robot_localization/  EKF and SLAM settings/launches
  mobile_robot_navigation/    AMCL/Nav2 settings, goal client and HTTP mission API
  mobile_robot_bringup/       Combined simulation, mapping and navigation launches
```

Our own launch files are XML. They include the installed Gazebo and SLAM
packages' existing Python launches. Package metadata uses CMake for asset
packages and setuptools for Python packages; no custom C++ nodes are required.

## 0. Prepare Ubuntu and install ROS

Copy or clone this whole repository to `~/remote_mobile_robot` on Ubuntu.
A path without spaces makes ROS/CMake development easier. Use Ubuntu's
system Python with ROS; do not run the ROS nodes inside a pip virtual environment.

If Jazzy is already installed, skip the ROS repository setup and desktop install.
These commands follow the [official Jazzy installation guide](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html).

```bash
sudo apt update
sudo apt install -y locales software-properties-common curl
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
sudo add-apt-repository -y universe

# Configure ROS apt repositories using the official ros2-apt-source package.
ROS_APT_SOURCE_VERSION=$(curl -fsSL https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | python3 -c 'import json,sys; print(json.load(sys.stdin)["tag_name"])')
curl -fL -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.noble_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt update
sudo apt install -y ros-jazzy-desktop ros-dev-tools
source /opt/ros/jazzy/setup.bash
```

Keep Ubuntu packages updated using your normal system maintenance. If apt
reports dependency conflicts, check the official guide and make sure Ubuntu's
`noble-updates` and `noble-backports` repositories are enabled.

**In every new terminal**, set your repository location and source ROS:

```bash
export ROBOT_REPO="$HOME/remote_mobile_robot"
source /opt/ros/jazzy/setup.bash
# After building packages, also run:
source "$ROBOT_REPO/mobile_robot_ws/install/setup.bash"
```

The examples below assume `ROBOT_REPO` has been set in each terminal. Do not
source `install/setup.bash` until the first successful build.

## 1. Learn the motion equations

Read [ROBOT_DESIGN.md](docs/ROBOT_DESIGN.md) before launching ROS.
The maths can run with plain Python, even before building packages:

```bash
cd "$ROBOT_REPO"
python3 tools/test_core.py
PYTHONPATH=mobile_robot_ws/src/mobile_robot_control python3 -m mobile_robot_control.kinematics_demo --linear 0.2 --angular 0.0
PYTHONPATH=mobile_robot_ws/src/mobile_robot_control python3 -m mobile_robot_control.kinematics_demo --linear 0.0 --angular 0.8
```

Expected: straight travel needs about 31.83 RPM on both sides; a positive
rotation spins the left side backward and the right side forward. The 2048
tick example is a teaching value, not a verified servo encoder specification.

## 2–5. Inspect dimensions, build the description and view it

Install only the description dependencies first:

```bash
sudo apt install -y ros-jazzy-xacro ros-jazzy-robot-state-publisher ros-jazzy-joint-state-publisher-gui
cd "$ROBOT_REPO/mobile_robot_ws"
colcon build --symlink-install --packages-select mobile_robot_description
source install/setup.bash
ros2 launch mobile_robot_description display.launch.xml
```

Expected: RViz shows four 120 mm wheels, the split chassis and raised platform.
The GUI sliders rotate each wheel. Sensors are simple boxes. The original
mechanical assembly includes details omitted from this simplified physics model.
Close this launch before starting simulation: the GUI must not publish wheel
positions while Gazebo is publishing real simulated joint states.

The five converted meshes are already included. If you intentionally update
the original CAD, `python3 tools/build_scaffold.py` regenerates those meshes
**and package metadata**. It is not necessary for ordinary builds and does not
automatically update dimensions, sensor placements or controller parameters.

## 6. Install simulation and autonomy dependencies, then build all packages

Jazzy pairs with Gazebo Harmonic through
[gz_ros2_control](https://control.ros.org/jazzy/doc/gz_ros2_control/doc/index.html).
Use modern `ros_gz`, not Gazebo Classic plugins.

```bash
sudo apt install -y ros-jazzy-ros-gz ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-controllers ros-jazzy-robot-localization \
  ros-jazzy-slam-toolbox ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
  ros-jazzy-teleop-twist-keyboard python3-yaml

# Run init only once per Ubuntu installation. Skip it if rosdep is initialized.
sudo rosdep init
rosdep update
cd "$ROBOT_REPO/mobile_robot_ws"
rosdep install --from-paths src --ignore-src --rosdistro jazzy -r -y
colcon build --symlink-install
source install/setup.bash
cd "$ROBOT_REPO"
python3 tools/test_core.py
python3 tools/validate_project.py
```

To inspect Gazebo alone, without the Python odometry/EKF stack:

```bash
ros2 launch mobile_robot_gazebo sim.launch.xml
```

Expected: a six-metre room with one shelf, the robot near the centre, and
two active controllers. Close this launch before the combined launch below.

## 7. Drive the robot manually

Terminal 1: launch Gazebo, robot model, controller, Python encoder odometry,
EKF, bridges and RViz together:

```bash
ros2 launch mobile_robot_bringup simulation.launch.xml
```

Terminal 2: check controllers and drive:

```bash
ros2 control list_controllers
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p speed:=0.15 -p turn:=0.5
```

Keep keyboard focus in the teleop terminal. `i` drives forward, `j` rotates
left, `l` rotates right, `k` stops. Jazzy teleop publishes on key events;
hold/repeat the motion key to keep fresh commands arriving. The adapter stops
after 0.3 seconds without a new command, including a keyboard auto-repeat gap.
Stop teleop with Ctrl+C when finished.

An alternative repeatable command, in place of teleop:

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.1}, angular: {z: 0.0}}'
```

Press Ctrl+C to stop publishing. The adapter drops stale commands after
0.3 seconds; the controller has a second 0.5-second command timeout.
The adapter also scales excessive commands to respect body and wheel limits.
Jazzy's controller expects
[TwistStamped](https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html);
the adapter converts the standard `/cmd_vel` Twist messages and stamps them.

Simulation software stop and reset:

```bash
ros2 topic pub --once /emergency_stop std_msgs/msg/Bool '{data: true}'
ros2 topic pub --once /emergency_stop std_msgs/msg/Bool '{data: false}'
```

Reset discards the old command; fresh commands are required. This software
stop state lasts for the node's lifetime and is not a physical power cutoff.

For a server-only Gazebo run (GPU sensor rendering is still required):

```bash
ros2 launch mobile_robot_bringup simulation.launch.xml rviz:=false gz_args:="-r -s --headless-rendering $ROBOT_REPO/mobile_robot_ws/src/mobile_robot_gazebo/worlds/learning_room.sdf"
```

## 8. Understand and compare encoder odometry

The Python node averages the two measured joint positions on each side and
integrates the side distances. It does not infer travel from `/cmd_vel`.

```bash
ros2 topic echo /joint_states --once
ros2 topic echo /wheel/odom --once
ros2 topic echo /diff_drive_controller/odom --once
ros2 run mobile_robot_control kinematics_demo --linear 0.15 --angular 0.3
```

Drive straight, reverse, then turn. Compare positions and signs in the two
odometry topics. Small differences from integration/filtering are expected.
Both estimate wheel travel, so agreement does not prove slip-free ground truth.

To compare EKF results using the standard controller as input, stop the current
launch, then restart with:

```bash
ros2 launch mobile_robot_bringup simulation.launch.xml odom_topic:=/diff_drive_controller/odom
```

The Python odometry still runs for comparison. Only one selected source is
fused at a time; neither wheel odometry source publishes TF.

## 9–11. Inspect IMU, LiDAR, camera, EKF and TF

In another sourced terminal:

```bash
ros2 topic hz /scan
# Ctrl+C before the next command.
ros2 topic echo /imu/data --once
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo odom base_link
# Ctrl+C before the next command.
ros2 run tf2_ros tf2_echo base_link lidar_link
# Ctrl+C before the next command.
python3 "$ROBOT_REPO/tools/check_simulation.py"
```

The smoke check waits up to 20 seconds for all sensors, wheel feedback, both
wheel odometry implementations, filtered odometry, and the odom/sensor TF chain.
It also checks sensor frame IDs. It does not command motion.

In RViz, use Fixed Frame `odom` during driving. The Scan display should align
with the room walls. Add an Image display on `/camera/image_raw` to view the
RGB camera. The camera optical frame has X right, Y down, Z forward.
The EKF combines measured forward velocity, a lateral zero-motion constraint,
and IMU yaw rate; see the design document for slip and covariance caveats.

## 12. Build and save a map with SLAM

Stop the previous simulation and start this instead. Do not run two simulator
launches at once.

```bash
ros2 launch mobile_robot_bringup mapping.launch.xml
```

In RViz change Fixed Frame to `map`. In a second terminal run teleop as above.
Drive slowly around the shelf and room, revisit areas to close loops, and stop.
SLAM estimates the map and `map → odom` from scans and odometry transforms.

Save the occupancy map in a third sourced terminal:

```bash
mkdir -p "$ROBOT_REPO/maps"
ros2 run nav2_map_server map_saver_cli -f "$ROBOT_REPO/maps/room" --ros-args -p use_sim_time:=true -p save_map_timeout:=10.0
ls "$ROBOT_REPO/maps/room.yaml" "$ROBOT_REPO/maps/room.pgm"
```

Default map saving produces a YAML file and PGM image. Keep both together.
This map supports AMCL; it is not the serialized SLAM pose graph used to
resume mapping. Maps are generated from your run; no fabricated map is included.

## 13–14. Localize with AMCL and navigate

Stop mapping and teleop. Start a fresh simulator with your saved map:

```bash
ros2 launch mobile_robot_bringup navigation.launch.xml map:="$ROBOT_REPO/maps/room.yaml"
```

In RViz:

1. Set Fixed Frame to `map`.
2. Use **2D Pose Estimate** at the robot's starting location near (0,0), pointing
   along positive X. This initializes AMCL; verify the scan overlays the map.
3. Wait for the Nav2 lifecycle nodes to become active.
4. Use **2D Goal Pose** to choose a free location within the room.

Checks and a Python goal alternative:

```bash
ros2 lifecycle get /amcl
ros2 lifecycle get /bt_navigator
ros2 run tf2_ros tf2_echo map base_link
# Ctrl+C, then send a goal in a clear part of your saved map.
ros2 run mobile_robot_navigation send_goal 1.0 -1.0 0.0 --timeout 180 --ros-args -p use_sim_time:=true
```

Goal arguments are X metres, Y metres, yaw radians. The script reports the
action result and requests cancellation on timeout or Ctrl+C during navigation.
Coordinates from the original warehouse example are outside this small room.

Nav2 uses an A* global planner and a DWB local controller, a rectangular CAD
footprint, scan obstacle layers, inflation, smoothing, and spin/backup/wait
recoveries. SLAM and AMCL must never run together: each would own `map → odom`.
For localization/navigation on an already running simulator, use the lower-level
`mobile_robot_navigation navigation.launch.xml map:=...` without launching a
second simulator.

## 15. Obstacle avoidance and camera

During navigation, add/move an obstacle in Gazebo and verify the scan/costmap
detects it, the robot replans or stops, and the goal can be canceled. Nav2's
collision monitor stops when at least three scan points enter the configured
stop polygon; missing/stale scan data also prevents navigation commands.
This is a simulated software behavior to verify, not certified hardware safety.

Navigation command flow:

```text
controller/behaviors → /cmd_vel_nav → velocity smoother
→ /cmd_vel_smoothed → collision monitor → /cmd_vel
→ Python command adapter → /diff_drive_controller/cmd_vel
```

Manual teleop publishes directly to `/cmd_vel`, so it bypasses Nav2's collision
monitor. Do not run teleop and navigation commands simultaneously. Camera
streaming is included; detection, docking, AprilTags and RGB-D work are future
perception tasks after sensor selection and calibration.

## 16. Use the mission API

With AMCL initialized and navigation active, start the API in another terminal:

```bash
ros2 launch mobile_robot_navigation mission.launch.xml
```

Submit one goal, check its status, or request cancellation:

```bash
curl -X POST http://127.0.0.1:8000/robot/move \
  -H 'Content-Type: application/json' \
  -d '{"x": 1.0, "y": -1.0, "theta": 0.0}'
curl http://127.0.0.1:8000/robot/status
curl -X POST http://127.0.0.1:8000/robot/cancel
```

HTTP 202 means the request was queued, not that the robot reached the goal.
Poll status until `SUCCEEDED`, `FAILED`, `REJECTED`, or `CANCELED`. A second
goal while busy returns 409; malformed coordinates return 400. The server
binds to localhost and is a single-robot learning interface, without remote
authentication, persistence or fleet scheduling. ROS action callbacks execute
in the ROS thread; HTTP handlers queue requests.

## 17–20. Hardware, calibration and real-world navigation

Follow [HARDWARE.md](docs/HARDWARE.md). These stages cannot be verified from CAD
alone. The HX-30HM feedback protocol/resolution, real bus controller, power
system, emergency stop and sensor models need confirmation. Implement the
motor/feedback bridge only after those choices; reuse the same topic/frame
contracts and run hardware nodes with `use_sim_time:=false`.

## Editing and rebuilding

```bash
cd "$ROBOT_REPO/mobile_robot_ws"
colcon build --symlink-install
source install/setup.bash
```

Restart launches after changing YAML/Xacro. Maintain geometry consistently in
the Xacro, controllers YAML, Python kinematics defaults, and Nav2 footprint.
Regenerate meshes only when CAD changes. Keep generated Ubuntu `build/`,
`install/`, and `log/` folders out of version control.

## Troubleshooting

| Symptom | Check |
|---|---|
| `Package not found` | Source `/opt/ros/jazzy/setup.bash` and this workspace's `install/setup.bash` in that terminal. |
| Wheels do not move | `ros2 control list_controllers`; both controllers must be active. Check `/cmd_vel` and `/diff_drive_controller/cmd_vel` types/rates; Gazebo must be playing. |
| Gazebo robot/meshes missing | Verify installed mesh files; sim launch adds the description share directory to `GZ_SIM_RESOURCE_PATH`. Check spawn/plugin logs. |
| Robot won't turn or slides badly | Wheel signs, track/radius, contact friction and four-wheel scrub; calibrate rather than assuming ideal differential-drive contact. |
| No scan/camera | Gazebo Sensors plugin, Ogre2/GPU support, bridges and frame IDs; run `check_simulation.py`. Server mode still needs a working render backend. |
| RViz has no transform | `odom` before SLAM; `map` after SLAM/AMCL initialization. Check EKF input and single TF ownership. |
| Navigation stays inactive | Read the lifecycle/configuration error logs, check map YAML/image, initialize AMCL, and verify map-to-base TF. |
| Robot stops unexpectedly | Command timeout, `/emergency_stop`, stale scan or stop-zone points. Inspect `/cmd_vel_nav`, `/cmd_vel_smoothed`, `/cmd_vel` in order. |
| Map saving fails | Confirm `/map` exists, simulation is playing, and the output directory is writable. |

## Sources

- [ROS Jazzy installation](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)
- [Jazzy differential-drive controller](https://control.ros.org/jazzy/doc/ros2_controllers/diff_drive_controller/doc/userdoc.html)
- [Gazebo ros2_control integration](https://control.ros.org/jazzy/doc/gz_ros2_control/doc/index.html)
- [ROS XML launch format](https://design.ros2.org/articles/roslaunch_xml.html)
- [Nav2 first robot setup](https://docs.nav2.org/setup_guides/index.html)
- Mechanical source: `CAD Files/robot_redesign_R1/docs/BUILD_GUIDE.md` and its manufacturer references.

# Physical robot integration: steps 17–20

The software through simulated missions is supplied. Physical construction,
motor protocol integration, calibration, and real-world qualification remain
work on actual hardware. There is intentionally no launch file that sends
untested serial commands to the HX-30HM servos.

## Choose and verify hardware

1. Follow the CAD guide's one-module fit test and load checks before assembling
   all four servo modules. Verify horn threads, retaining screw, radial loads,
   tyre retention, cable clearance, and temperature/current under skid turns.
2. Verify HX-30HM continuous motor mode, bus voltage, controller interface,
   unique IDs, command units, direction signs, and available feedback against
   the protocol for your exact servo revision. Do not guess register addresses.
3. Establish whether this servo returns continuous wheel position/velocity in
   motor mode. If not, fit external encoders. Position-limited servo angle is
   not automatically usable as continuous wheel odometry.
4. Select LiDAR, IMU, camera, battery, regulator, fuse, bus controller, and
   computer. Measure their locations, total mass, centre of mass, and inertia.
5. Implement a physical emergency stop that removes motor power, and a
   microcontroller/bus-controller watchdog that stops motors if host messages
   cease. The `/emergency_stop` software topic is only a simulation aid.

## Keep the ROS contracts

The simplest future Python hardware bridge should subscribe to a bounded
velocity command, call `wheel_speeds(v,w)`, drive four servos with correct signs,
and publish `sensor_msgs/JointState` for all four named wheel joints. Joint
positions must be unwrapped radians, velocities rad/s, with measurement stamps.
Reject invalid feedback, handle disconnections, and command zero on timeout.
The Python odometry node can then operate without changes.

A Python serial bridge is an alternative to ros2_control hardware, not an
implementation of a ros2_control hardware plugin. Standard native ros2_control
hardware plugins are compiled components. Do not launch the Gazebo controller
manager or pretend its GazeboSimSystem works on the robot.

Required sensor contracts:

| Topic | Type | Frame |
|---|---|---|
| /joint_states | sensor_msgs/msg/JointState | Named wheel joints |
| /scan | sensor_msgs/msg/LaserScan | lidar_link |
| /imu/data | sensor_msgs/msg/Imu | imu_link |
| /camera/image_raw | sensor_msgs/msg/Image | camera_optical_frame |
| /camera/camera_info | sensor_msgs/msg/CameraInfo | camera_optical_frame |

On hardware, every node uses `use_sim_time:=false`. Driver timestamps and
computers must share a consistent clock. Publish the measured URDF through
robot_state_publisher; publish wheel joints through the driver, never the GUI.
Start control/odometry, EKF, then SLAM or AMCL/Nav2 after TF and scan are valid.
The simulation command adapter targets the Gazebo controller, so replace it
with the actual hardware command bridge when building hardware bringup.

## Calibration and acceptance order

1. Lift the wheels: verify names, signs, IDs, encoder counts, command units,
   timeout stopping, and power emergency stop.
2. At low speed measure a straight metre; update radius from measured/estimated
   travel. Compare both sides; fix mechanical alignment and uneven tyres.
3. Measure complete turns both directions; calibrate effective track for tyre
   scrub. Repeat on the intended floor and payload.
4. Record stationary/driving encoder and IMU data; estimate bias/covariance.
   Check IMU axes, acceleration units, timestamp lag, and magnetic interference.
5. Verify scan alignment and camera optical axes using fixed landmarks.
6. Map and localize before navigation; test open space, then static obstacles,
   sensor loss, bus loss, battery sag, stop/cancel, and dynamic obstacles.
7. Increase operating limits only after repeatable stopping distances and
   current/temperature/load performance are established.

Camera streaming is implemented. Object detection, AprilTags, docking, depth
perception, and commercial warehouse scheduling are later extensions; they
require chosen sensors, calibration data, and application requirements.

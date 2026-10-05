# Step 1: dimensions and differential-drive maths

The supplied R1 CAD is a **four-wheel skid-steer** robot with four HX-30HM
servos. There is no caster. Two left wheels receive the same angular speed;
two right wheels receive the same angular speed. This applies the plan's
differential-drive equations to the actual CAD, with lateral tyre slip during turns.

Source: `CAD Files/robot_redesign_R1/docs/BUILD_GUIDE.md` and
`source/build_robot.py`. STEP contains assembly datums; STL contains translated
print-bed datums. Never place unmodified print STL files directly at joint origins.

| Quantity | Model value | Origin |
|---|---:|---|
| Wheel radius r | 0.060 m | CAD tyre diameter 120 mm |
| Track L | 0.246 m | CAD wheel centres Y = ±123 mm |
| Wheelbase | 0.190 m | CAD wheel centres X = ±95 mm |
| Wheel centre height | 0.060 m | CAD |
| Deck underside | 0.086 m | CAD |
| Deck length / width | 0.300 / 0.200 m | CAD |
| Platform top | 0.147 m | CAD |
| Overall ground footprint | 0.310 × 0.270 m | CAD wheel envelope |
| Total simulated mass | 3.0 kg | Unmeasured CAD design target |
| Command speed limits | 0.20 m/s, 0.8 rad/s | Initial simulation settings |
| Wheel speed limit | 5 rad/s ≈ 47.75 RPM | Initial simulation setting |
| Encoder resolution example | 2048 ticks / wheel revolution | Teaching assumption only |

Positive X is forward, positive Y is left, positive Z is up. Positive yaw is
counterclockwise. All four wheel joints use the +Y axis: a positive wheel
velocity moves the robot forward. Opposing physical motor installation may
require different bus command signs; handle that in the future hardware driver.

For commanded body speed v and yaw rate w:

```text
left wheel rad/s  = (v - w L/2) / r
right wheel rad/s = (v + w L/2) / r
v = r (right rad/s + left rad/s) / 2
w = r (right rad/s - left rad/s) / L
RPM = wheel rad/s × 60 / (2π)
turning radius = v / w     (w = 0 means a straight line)
```

At v = 0.20 m/s and w = 0, both sides need 3.333 rad/s = 31.83 RPM.
At v = 0 and w = 0.8 rad/s, the sides need ±1.64 rad/s = ±15.66 RPM.
At v = 0.20 and w = 0.8, the faster wheel needs 4.973 rad/s = 47.49 RPM.
The CAD guide's advertised unloaded estimate is about 52.6 RPM / 0.33 m/s;
it does not establish loaded continuous performance.

For encoder ticks measured **at the wheel**:

```text
wheel angle = ticks × 2π / ticks_per_wheel_revolution
wheel distance = r × wheel angle
distance = (right distance + left distance) / 2
delta yaw = (right distance - left distance) / L
```

The Python implementation uses exact circular-arc integration, with a straight
line limit when delta yaw approaches zero. Gazebo joint position is continuous
angle feedback, not quantized encoder ticks. Tick conversion is taught separately;
2048 is not asserted as the HX-30HM resolution. A real driver must unwrap its
encoder readings and account for tick rollover, gear ratio, and direction signs.

## CAD visuals and physics

`tools/build_scaffold.py` converts five supplied STLs to centred metre-scale
meshes. Deck halves are placed at X = ±0.075075 m, Z = 0.093 m, the platform
at Z = 0.1445 m, and rims/tyres are centred at the wheel joints. The rims have
different inner/outer faces: this learning model centres and aligns them for
appearance, without claiming full fastener/servo assembly fidelity.

Servos, cradles, shims, bolts, and platform posts are omitted from the visual
model. Their mass is lumped into the body. Sensor boxes and positions are
assumptions because exact sensor models have not been selected. Box/cylinder
collisions make simulation simpler; they are not the detailed CAD contact shapes.
Body inertia and masses must be replaced by measurements before hardware use.

Four-wheel skid steering requires wheel scrub. Contact friction is an initial
approximation; excessive grip may prevent turning. Calibrate effective track
from a measured full rotation and wheel radius from measured straight travel.
Controller multipliers and Python geometry must be kept consistent. IMU yaw rate
helps account for turning slip, but does not recover every translational slip error.

## TF ownership and data flow

```text
map → odom                    slam_toolbox OR AMCL (never both)
odom → base_link              EKF only
base_link → wheels/sensors    robot_state_publisher
camera_link → optical frame   robot_state_publisher
```

`base_link` is at the ground-centre CAD datum, not the body centre of mass.
The inertial origin is elevated independently. No separate base_footprint is needed.

| Component | Problem / input | Concept | Output |
|---|---|---|---|
| ros2_control controller | /diff_drive_controller/cmd_vel + wheel position | Side speed conversion and feedback integration | Joint velocity commands, /diff_drive_controller/odom |
| Python encoder node | /joint_states positions | Average each side, integrate distance and yaw | /wheel/odom; no TF |
| EKF | /wheel/odom planar velocity + /imu/data yaw rate | Predict state, correct using covariance-weighted measurements | /odom and odom → base_link |
| SLAM | /scan and continuous odom TF | Match scans and optimize map/pose graph | /map and map → odom |
| AMCL | Saved map, /scan, odom TF | Particle-filter pose estimation | /amcl_pose and map → odom |
| Nav2 | Map, scan, TF, odom, goal | A* plan, DWB local trajectories, costmaps, recovery | /cmd_vel after smoothing and collision monitor |
| Mission API | Validated HTTP coordinates | One queued Nav2 action with status/cancellation | NavigateToPose and JSON status |

The EKF uses wheel vx plus a non-holonomic vy = 0 measurement, and IMU yaw rate.
It does not double-count wheel pose and velocity, or fuse an arbitrary absolute
IMU yaw. Skid steering can violate the lateral zero-velocity assumption: tune
that covariance or disable the vy channel after observing lateral slip. All
covariances are initial estimates requiring calibration.

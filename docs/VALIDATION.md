# Verification record

Checked on the Windows development host. Runtime target is Ubuntu 24.04,
ROS 2 Jazzy, Gazebo Harmonic. No ROS/Gazebo runtime was available on this host.

## Passed locally

- 10 standalone tests: straight/reverse motion, in-place rotation and sign,
  analytic quarter-circle integration, encoder tick conversion, invalid geometry,
  command scaling preserving curvature, non-finite velocity stop behavior, and
  valid/invalid mission goal inputs.
- Python source syntax checked with AST parsing.
- XML package/launch/world documents parsed, and local package paths checked.
- CMake install directories checked for files so builds do not depend on empty
  directories that Git omits from clones.
- All YAML and RViz configurations parsed with PyYAML.
- Xacro expanded in display and simulation modes using Xacro 2.1.1. On Windows,
  only package-share discovery was substituted with local source paths; the
  macro/expression evaluator itself was used without replacing its logic.
- Expanded model has 9 links, 8 joints, a single base root, four wheel control
  interfaces, and three simulated sensors. Display mode has no Gazebo hardware.
- Five binary STL meshes verified for record count and metre-scale coordinates.
- CAD radius/track, controller TF ownership and footprint coverage checked.

These checks do not prove that ROS launch substitutions execute, controllers
activate, contact dynamics behave correctly, or autonomous navigation succeeds.

## Ubuntu acceptance checklist

Follow the README in order and record results here after running:

- [ ] All six packages build with colcon and rosdep resolves their dependencies.
- [ ] Description launch shows the CAD wheels/deck/platform in RViz.
- [ ] Gazebo spawns the model and both controllers become active.
- [ ] `tools/check_simulation.py` receives all topics and expected frames/TF.
- [ ] Straight, reverse, positive/negative rotation and curved motion have correct signs.
- [ ] Releasing commands and the software stop halt motion; reset needs a fresh command.
- [ ] Wheel odometry is consistent with controller odometry; turning slip is observed/tuned.
- [ ] Laser scan aligns with walls; IMU axes and RGB image/optical frame are correct.
- [ ] EKF is the only odom-to-base TF publisher; localization is the only map-to-odom publisher.
- [ ] Mapping produces a usable saved YAML/image pair.
- [ ] AMCL initializes against that map; map-to-base TF is continuous and plausible.
- [ ] Nav2 reaches a free-space goal and returns success.
- [ ] An obstacle triggers replanning or stopping; stale scan stops navigation commands.
- [ ] Mission API rejects invalid/busy goals, reports terminal status, and cancels a running goal.

Physical acceptance and calibration are tracked separately in HARDWARE.md.

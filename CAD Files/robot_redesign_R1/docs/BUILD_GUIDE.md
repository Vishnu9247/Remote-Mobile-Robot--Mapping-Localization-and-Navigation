# HX-30HM mobile robot base - R1

**Engineering prototype / first-article build. Not released for production.**
Designed for a 220 x 220 mm print bed and a target total robot mass of 3 kg,
including chassis, battery, electronics and payload. This is a design target,
not a verified load rating. Dimensions are millimetres.

## What changed

This is a new mechanical design, not a rescaled version of the input CAD.
The original placeholder motor and damaged wheel have been replaced with
manufacturer HX-30HM geometry and a new wheel/horn interface. The chassis
has two reinforced halves, three bolted splice plates, four removable servo
cradles, separate clamp caps, interchangeable horn adapters, keyed wheel rims,
TPU tyres, and a raised universal sensor platform.

## Principal dimensions and datums

| Item | Dimension |
|---|---|
| Chassis deck | 300 x 200 x 6; upper ribs extend 8 above deck |
| Main deck underside / top | Z = 86 / 92 |
| Tyre outside diameter / contact width | 120 / 20 |
| Rim overall width | 24 |
| Wheelbase | 190 |
| Track, tyre centre planes | 246 |
| Overall wheel envelope | 310 long x 270 wide |
| Ground clearance, lowest cradle | 21.6 |
| Sensor platform | 120 x 100 x 5; top Z = 147 |
| Wheel centres | X = +/-95, Y = +/-123, Z = 60 |
| Servo output face datums | X = +/-95, Y = +/-100, Z = 60 |

The world origin is on the floor at chassis centre. X is forward, Y left,
Z up. STEP components use functional local datums; the named assembly places
them correctly. STL files are independently oriented and translated onto
Z=0 for printing; do not assemble using STL origins. CAD/STL use mm; ROS
meshes need conversion to metres. STEP export contains named components,
not a Fusion parametric timeline or motion joints. Editable CadQuery construction
source is supplied in source/build_robot.py. Dimensions are defined in that
script; source/nominal_dimensions.json is a reference summary, not an input
configuration file. Install CadQuery 2.x and run python source/build_robot.py
from the unzipped package; the vendor models must remain in reference/.

## Printed parts

| ID | Part | Quantity | Material |
|---|---|---:|---|
| P01 | Front deck | 1 | PETG |
| P02 | Rear deck | 1 | PETG |
| P03 | Servo cradle | 4 | PETG |
| P04 | Servo clamp cap | 4 | PETG |
| P05 | Servo shim | 8 | TPU |
| P06 | Chassis splice | 3 | PETG |
| P07 | Horn adapter | 4 | PETG |
| P08 | Wheel rim | 4 | PETG |
| P09 | Keyed tyre | 4 | TPU 95A |
| P10 | Sensor platform | 1 | PETG |
| P11 | Platform spacer | 4 | PETG |
| P12 | Fastener fit coupon | 1 initially | PETG |

Use supplied print orientation. Starting settings: 0.4 mm nozzle, 0.2 mm
layers, six walls, six top/bottom layers, 40% infill. Use 100% infill for
horn adapters and clamp caps. TPU tyres: start with four walls and 25-35%
infill; adjust compliance after testing. These are initial process settings,
not validated material properties. Print thin shims as solid single layers
at their actual 0.25 mm model thickness. Cradles print on their rear face; use local
support only if needed around horizontal access holes. Keep support off
servo contact surfaces. Splice plates print with nut-pocket face down and
may need a small brim. Clear pockets before assembly.

No printed plastic threads carry structural fasteners. M3 holes are 3.4 mm;
M4 holes are 4.5 mm. Modelled nut pocket widths are 5.8 mm for M3 and 7.3 mm
for M4. Test the coupon: actual clearance depends on printer, material and
slicer. Drill/ream clearance holes to the intended diameter if required;
do not force bolts through an undersized hole and split a printed part.

## Purchased mechanical hardware

| Item | Qty | Use |
|---|---:|---|
| Hiwonder HX-30HM servo | 4 | One per wheel |
| Matching metal drive horn, splined side | 4 | Use the manufacturer's metal spline; do not print it |
| OEM centre retaining screw | 4 | Supplied/approved for the purchased servo and horn |
| M4 x 20 socket-head screw | 16 | Servo cradles to deck |
| M4 nyloc nut | 16 | Cradle mounting, accessible beneath bridge |
| M4 x 16 socket-head screw | 6 | Chassis seam splices |
| M4 regular hex nut | 6 | Captured in splice plates |
| M4 flat washer, nominal 0.8 thick | 38 | 32 on cradle joints; 6 above seam joints |
| M3 x 12 socket-head screw | 32 | 16 clamp caps, 16 rim-to-adapter joints |
| M3 regular hex nut | 32 | Captured in cradles and adapters |
| M3 x 70 socket-head screw | 4 | Through platform, spacers and main deck |
| M3 nyloc nut | 4 | Platform underside |
| M3 flat washer, nominal 0.5 thick | 40 | Caps/rims plus both ends of platform joints |
| M2 x 8 machine screw | 16 | Adapter to metal horn; verify actual horn thread/depth |
| M2 flat washer, nominal 0.3 thick | 16 | Adapter screw heads |
| 20 mm wide reusable battery strap, about 300 mm long | 2 | Slots in deck; choose length for actual battery |

Metric coarse pitches: M2 x 0.4, M3 x 0.5, M4 x 0.7. Socket-head screws:
ISO 4762 / DIN 912 type; regular hex nuts: ISO 4032 / DIN 934 type. Use
washers against printed surfaces. Nyloc heights vary by supplier; verify
bolt protrusion before tightening. The OEM centre screw is an exception:
use the supplied correct screw, not a guessed length.

M3/M4 cannot replace the horn's small fasteners. The vendor horn STEP has
four nominal 1.6 mm holes consistent with an M2 thread core, on a 14 mm bolt circle. The design
uses M2 fasteners there. Confirm the actual purchased horn is threaded M2;
do not force M2 screws into an unthreaded or different revision horn.

## Assembly sequence

1. **Test one module first.** Print P12, one P03 cradle, one P04 cap, one
   P07 adapter and shim samples. Check actual servo insertion, connector
   access, horn diameter/bolt circle and fasteners before printing all parts.
2. Fit the six M4 regular nuts into the three splice plates. Align the
   deck halves with the 0.3 mm centre gap. Fit splices beneath the seam at
   Y=-65, 0, +65, using six M4 x 16 screws and top washers.
3. Slide four M3 nuts into each cradle's side-entry nut pockets. Add a
   lower shim and servo with output facing outward. Feed cables through
   the rear cable window. Add the upper shim and cap; use four M3 x 12
   screws and washers. Tighten evenly only until the servo is retained.
   The housing must not distort. Adjust shim thickness to eliminate rocking.
4. Attach each complete cradle beneath the deck with four M4 x 20 screws,
   eight washers and four nyloc nuts. The bridge faces seat directly against
   the deck underside. Cap screws remain reachable through access holes.
5. Fit the genuine splined metal horn and its OEM centre retaining screw.
   The rear idler horn is not used. The mating spline is supplied hardware.
6. Insert four M3 nuts in the back of each printed adapter. Attach each
   adapter to its metal horn using four M2 x 8 screws and washers. Confirm
   screws engage about 2.9 mm in the modeled horn and do not bottom out.
   The adapter's 19.4 mm locating recess is based on the vendor CAD's 19 mm
   horn; measure your horn before printing the set (the marketing drawing
   rounds its diameter to 20 mm). Change the recess if your revision differs.
7. Stretch each TPU tyre over a rim lip, align the six keys, and seat it
   between the lips. The keyed features transmit torque; tyre stiffness and
   fit still need a physical test. Do not use a bare PETG rim as the tyre.
8. Attach each rim to its adapter with four M3 x 12 screws and washers.
   The 22 mm centre access opening leaves the horn screws accessible.
9. Install the four 50 mm spacers and sensor platform using M3 x 70 screws,
   washers at both ends, and nyloc nuts underneath the main deck.
10. Mount battery low and near the centre. Use the universal grid/platform
    for electronics. A specific LiDAR, camera or battery footprint has not
    been assumed; design its adapter after choosing the exact model.

## Servo operation and design limits

The HX-30HM has a velocity-controlled motor mode suitable for continuous
wheel rotation. Set unique IDs before connecting all four servos. Use the
manufacturer's half-duplex UART interface and compatible bus controller.
The advertised 30 kgf.cm value is torque, not a 30 kg payload rating.
At 0.19 s per 60 degrees the theoretical unloaded speed is about 52.6 rpm,
or 0.33 m/s with these tyres; loaded speed will be lower. It is not a
continuous-duty torque or speed guarantee.

The mass target is 3 kg TOTAL. At even static load distribution each wheel
supports approximately 7.4 N. A wheel centre 23 mm outboard of the servo
front datum creates roughly 0.17 N.m bending moment about that datum.
The manufacturer's published radial-load limit was not established. Direct
wheel support by the servo therefore requires physical verification. For
higher loads, impacts or continuous commercial duty, use a bearing-supported
axle or a drivetrain with published wheel-load and continuous-duty ratings.
This is a material blocker to a production load rating, not solved by STEP
validity. Four-wheel skid steering also increases tyre scrub and drivetrain
loads during turns; test on the intended floor.

## Required release checks

- Measure actual servo and horn revision; check clamp, shaft engagement,
  connector clearance, bolt circle, thread size and screw depth on one module.
- Print the fit coupon in the final material. Check nut capture, clamp grip,
  tyre retention and wheel runout; correct tolerances in source if needed.
- Confirm wheels turn freely by hand, cables cannot touch rotating parts,
  and every fastener is accessible with the platform installed.
- Test unloaded, then incrementally load to the 3 kg target on a level floor.
  Record current, temperature, tracking, tyre slip and fastener loosening,
  including repeated starts, stops and skid turns. Set operating limits from
  those results and the manufacturer's ratings.
- Inspect printed joints for cracking/creep and perform an agreed proof-load
  and endurance test before production release. No FEA, fatigue qualification,
  radial-load qualification or physical printing has been performed here.

## Sources and traceability

Manufacturer product: https://www.hiwonder.com/products/hx-30hm
Manufacturer resource page: https://www.hiwonder.com.cn/store/learn/43.html
Manufacturer HX-30HM resource folder:
https://drive.google.com/drive/folders/1xmsYPLw4wU3SoEZABs0Quua_oJLB2lXZ
Servo CAD: https://drive.google.com/file/d/1LS3cizvNKFOIIMLmUDeMT0-VcW8TMGUd/view
Horn/brackets CAD: https://drive.google.com/file/d/1_G9rTeujNCA0BhDlBWFsojOa9U4fKScV/view
Bus modes: https://docs.hiwonder.com/projects/BusLinker/en/latest/docs/1_BusLinker_V3.0_Servo_Debugging_Board_User_Manual.html
Protocol: https://github.com/Hiwonder-official/hiwonder-servo-sdk/blob/main/docs/protocol_en.md

Downloaded 2026-10-04. Original manufacturer STEP files are retained in
reference/. Their geometry is supplied by Hiwonder; the printed parts and
assembly placement are newly designed. The public product page contains
some mixed HX-10HM/HX-30HM descriptive text; the CAD dimensions and exact
HX-30HM protocol are the primary model/interface references here.

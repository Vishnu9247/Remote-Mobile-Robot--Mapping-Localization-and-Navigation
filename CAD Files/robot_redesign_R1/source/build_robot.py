"""R1 HX-30HM mobile base. Units mm. CadQuery 2.x. Run from any directory.
Vendor STEP data are in ../reference. Export STEP in assembly coordinates/local
functional datums; STL files are moved/oriented onto a print bed at Z=0.
Engineering prototype: physical fit/load testing required before release.
"""
from pathlib import Path
import cadquery as cq
import math,json
ROOT=Path(__file__).resolve().parents[1]
for d in ['STEP','STL','docs']: (ROOT/d).mkdir(exist_ok=True)
P={'wheel_radius':60.,'axle_z':60.,'axle_x':95.,'servo_face_y':100.,'deck_z':86.,'deck_t':6.,'M3_clear':3.4,'M4_clear':4.5,'horn_PCD':14.,'body_side_clearance':0.34}
C=cq.Compound
V=cq.Vector
parts={};placed=[];assy=cq.Assembly(name='HX30HM_mobile_base_R1')
def box(x,y,z,dx,dy,dz):return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z)).val()
def cyl(r,h,x=0,y=0,z=0):return cq.Solid.makeCylinder(r,h,V(x,y,z))
def fuse(shapes):
 s=shapes[0]
 for q in shapes[1:]:s=s.fuse(q)
 return s.clean()
def cut(s,tools):
 for q in tools:s=s.cut(q)
 return s.clean()
def hexprism(af,h,x=0,y=0,z=0):return cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(h).translate((x,y,z)).val()
def holes(s,pts,d,z,h):return cut(s,[cyl(d/2,h,x,y,z) for x,y in pts])
def slot(x,y,length,width,z,h,angle=0):return cq.Workplane('XY').slot2D(length,width,angle).extrude(h).translate((x,y,z)).val()
def store(name,s,qty,material,orientation=None):
 assert s.isValid(),name
 assert len(s.Solids())==1,(name,len(s.Solids()))
 parts[name]={'shape':s,'quantity':qty,'material':material}
 cq.exporters.export(s,str(ROOT/'STEP'/f'{name}.step'))
 t=orientation(s) if orientation else s
 b=t.BoundingBox();t=t.translate((-b.xmin,-b.ymin,-b.zmin))
 cq.exporters.export(t,str(ROOT/'STL'/f'{name}.stl'),tolerance=.08,angularTolerance=.15)
 b=t.BoundingBox();parts[name]['print_size_mm']=[round(b.xlen,2),round(b.ylen,2),round(b.zlen,2)]
 assert b.xlen<=220 and b.ylen<=220,name
 return s
def add(name,s,color,kind='printed'):
 assy.add(s,name=name,color=cq.Color(*color));placed.append((name,s,kind))
BLUE=(.13,.28,.38);ORANGE=(.96,.43,.12);DARK=(.15,.16,.18);GREY=(.6,.65,.7)
# Cradle around manufacturer's external envelope; output face datum Xsrc=281.25.
# All casing features preserved; body axis remains horizontal, output toward +Y.
raw=cq.importers.importStep(str(ROOT/'reference/HX30HM_vendor.stp')).val()
servo=raw.translate((-281.25,-63.9724397566264,-106.398012374237)).rotate((0,0,0),(0,0,1),-90)
cq.exporters.export(servo,str(ROOT/'STEP/HX30HM_manufacturer_reference.step'))
hraw=cq.importers.importStep(str(ROOT/'reference/horn_brackets_vendor.stp')).val().Solids()[1]
horn=hraw.translate((-14.291330304170971,-84.63698870116,-106.105912125309)).rotate((0,0,0),(0,0,1),-90).translate((0,.7,0))
cq.exporters.export(horn,str(ROOT/'STEP/HX30HM_drive_horn_reference.step'))
# Lower U-cradle and reinforced rear hanger. No screw enters the servo casing.
cradle=fuse([box(-23,-37,-38.4,46,40.2,3),box(-23,-37,-35.4,10.3,40.2,45.8),box(12.7,-37,-35.4,10.3,40.2,45.8),box(-23,-37,-35.4,46,3.5,55.4),box(-34,-37,20,68,37,6)])
# Cable port through rear spine; vertical ribs remain on either side.
cradle=cut(cradle,[box(-10.5,-38,-23,21,6,17)])
cappts=[(x,y) for x in [-18,18] for y in [-9,-28]]
cradle=holes(cradle,cappts,3.4,3,10)
for x,y in cappts:
 cradle=cradle.cut(hexprism(5.8,2.8,x,y,4.2))
 cradle=cradle.cut(box(x if x>0 else -24,y-2.9,4.2,6,5.8,2.8))
mountpts=[(x,y) for x in [-28,28] for y in [-9,-28]]
cradle=holes(cradle,mountpts,4.5,19,8)
cradle=holes(cradle,cappts,7,19,8) # driver/head access through bridge
cradle=store('P03_servo_cradle',cradle.clean(),4,'PETG',lambda s:s.rotate((0,0,0),(1,0,0),90))
cap=holes(box(-23,-33,10.4,46,33,5),cappts,3.4,9,8)
cap=store('P04_servo_clamp_cap',cap,4,'PETG')
# Two 0.3 mm compliant shim pads nominal; adjust after fit coupon test.
shim=store('P05_servo_shim',box(-12.3,-32,-35.4,24.6,30,.25),8,'TPU')
# Split deck with upper perimeter ribs. Flat underside prints without support.
all_mount=[];all_access=[]
for sx in [-1,1]:
 for sy in [-1,1]:
  all_mount += [(sx*95+sy*x,sy*(100+y)) for x,y in mountpts]
  all_access += [(sx*95+sy*x,sy*(100+y)) for x,y in cappts]
seampts=[(x,y) for x in [-20,20] for y in [-65,0,65]]
standpts=[(x,y) for x in [-45,45] for y in [-35,35]]
for sign,label in [(1,'front'),(-1,'rear')]:
 x0=.15 if sign>0 else -150
 deck=cq.Workplane('XY').box(149.85,200,6,centered=False).edges('|Z').fillet(4).translate((x0,-100,0)).val()
 ribs=[box(x0+5,y,6,139.85,4,8) for y in [-96,92]]+[box((142 if sign>0 else -146),-92,6,4,184,8)]
 deck=fuse([deck]+ribs)
 pts=[p for p in all_mount+seampts if p[0]*sign>0]
 deck=holes(deck,pts,4.5,-1,16)
 deck=holes(deck,[p for p in standpts if p[0]*sign>0],3.4,-1,16)
 deck=holes(deck,[p for p in all_access if p[0]*sign>0],7,-1,16)
 # General M3 accessory grid, separate from servo attachment locations.
 grid=[(sign*x,y) for x in [25,50,75,100,125] for y in [-50,-25,0,25,50]]
 deck=holes(deck,grid,3.4,-1,8)
 # Battery straps: two 20 mm belts routed through paired slots.
 for yy in [-42,42]:deck=deck.cut(slot(sign*60,yy,23,4.5,-1,8,0))
 deck=store('P0'+('1' if sign>0 else '2')+'_deck_'+label,deck.clean(),1,'PETG')
 add('deck_'+label,deck.translate((0,0,86)),BLUE)
strap=holes(box(-35,-11,0,70,22,6),[(-20,0),(20,0)],4.5,-1,8)
for x in [-20,20]:strap=strap.cut(hexprism(7.3,3.4,x,0,0))
strap=store('P06_chassis_splice',strap.clean(),3,'PETG')
for i,y in enumerate([-65,0,65]):add('splice_'+str(i),strap.translate((0,y,80)),ORANGE)
# Wheel/horn adapter is separate and replaceable. Four M2 holes on 14 mm PCD.
adapter=cyl(20,6)
adapter=cut(adapter,[cyl(4,8,z=-1),cyl(9.7,1.2)])
m2pts=[(7*math.cos(t*math.pi/2),7*math.sin(t*math.pi/2)) for t in range(4)]
m3pts=[(15*math.cos(math.pi/4+t*math.pi/2),15*math.sin(math.pi/4+t*math.pi/2)) for t in range(4)]
adapter=holes(adapter,m2pts,2.4,-1,8)
adapter=holes(adapter,m3pts,3.4,-1,8)
for x,y in m3pts:adapter=adapter.cut(hexprism(5.8,2.8,x,y,0))
adapter=store('P07_horn_adapter',adapter.clean(),4,'PETG')
# Local wheels use Z axle axis for easy printing; placed with axle along Y.
rim=fuse([cyl(56,24).cut(cyl(52,26,z=-1)),cyl(56,5),cyl(57,2),cyl(57,2,z=22).cut(cyl(52,4,z=21))])
rim=rim.cut(cyl(11,26,z=-1))
for t in range(6):
 a=t*math.pi/3;rim=rim.cut(cyl(10,7,38*math.cos(a),38*math.sin(a),-1))
rim=holes(rim,m3pts,3.4,-1,7)
keys=[]
for t in range(6):keys.append(box(55.5,-2,2,2,4,20).rotate((0,0,0),(0,0,1),30+t*60))
rim=fuse([rim]+keys)
rim=store('P08_wheel_rim',rim,4,'PETG')
tyre=cyl(60,20,z=2).cut(cyl(56.15,22,z=1))
for t in range(6):tyre=tyre.cut(box(55.8,-2.2,1.9,1.9,4.4,20.2).rotate((0,0,0),(0,0,1),30+t*60))
# Shallow transverse grooves; leave 2+ mm continuous radial tyre wall.
for t in range(24):tyre=tyre.cut(box(59.1,-.65,2,2,1.3,20).rotate((0,0,0),(0,0,1),t*15))
tyre=store('P09_TPU_tyre',tyre.clean(),4,'TPU 95A')
# Sensor platform with universal slotted mounting; standoffs use M3 through bolts.
upper=box(-60,-50,0,120,100,5)
upper=holes(upper,standpts,3.4,-1,7)
for x in [-40,-20,0,20,40]:
 for y in [-20,20]:upper=upper.cut(slot(x,y,24,3.4,-1,7,90))
upper=store('P10_sensor_platform',upper.clean(),1,'PETG')
add('sensor_platform',upper.translate((0,0,142)),BLUE)
post=store('P11_platform_spacer',cyl(6,50).cut(cyl(1.7,52,z=-1)),4,'PETG')
for i,(x,y) in enumerate(standpts):add('platform_spacer_'+str(i),post.translate((x,y,92)),ORANGE)
# Individual servo modules on all four corners.
def modulepose(s,sx,sy):return s.rotate((0,0,0),(0,0,1),0 if sy>0 else 180).translate((sx*95,sy*100,60))
def axial(s,offset):return s.rotate((0,0,0),(1,0,0),-90).translate((0,offset,0))
for sx in [-1,1]:
 for sy in [-1,1]:
  tag=('front' if sx>0 else 'rear')+'_'+('left' if sy>0 else 'right')
  for n,s,c,k in [('cradle',cradle,BLUE,'printed'),('cap',cap,ORANGE,'printed'),('servo',servo,DARK,'vendor'),('horn',horn,GREY,'vendor'),('adapter',axial(adapter,5),ORANGE,'printed'),('rim',axial(rim,11),BLUE,'printed'),('tyre',axial(tyre,11),DARK,'printed')]:
   add(tag+'_'+n,modulepose(s,sx,sy),c,k)
  add(tag+'_lower_shim',modulepose(shim,sx,sy),DARK)
  add(tag+'_upper_shim',modulepose(shim.translate((0,0,45.55)),sx,sy),DARK)
# Fit coupon: M3/M4 clearance holes plus nut pockets; nominal dimensions included.
coupon=box(0,0,0,80,25,6)
for i,d in enumerate([3.2,3.4,3.6,4.3,4.5,4.7]):coupon=coupon.cut(cyl(d/2,8,8+i*12,8,-1))
for x,af in [(10,5.6),(25,5.8),(42,7.1),(60,7.3)]:coupon=coupon.cut(hexprism(af,3, x,18,3))
store('P12_fastener_fit_coupon',coupon.clean(),1,'PETG')
# Nominal unthreaded hardware representations in a separate service assembly.
hardware=cq.Assembly(name='nominal_hardware')
def bolt(d,L):return fuse([cyl(d/2,L,z=-L),cyl(d*.9,d,z=0)])
def washer(d,t):return cyl({2:2.5,3:3.5,4:4.5}[d],t).cut(cyl(d/2+.1,t+2,z=-1))
def nut(d,h):return hexprism({3:5.5,4:7}[d],h).cut(cyl(d/2,h+2,z=-1))
def hadd(n,s):hardware.add(s,name=n,color=cq.Color(*GREY))
for i,(x,y) in enumerate(all_mount):
 for n,s,z in [('bolt',bolt(4,20),92.8),('top_washer',washer(4,.8),92),('bottom_washer',washer(4,.8),79.2),('nyloc',nut(4,5),74.2)]:hadd('cradle_'+str(i)+'_'+n,s.translate((x,y,z)))
for i,(x,y) in enumerate(seampts):
 for n,s,z in [('bolt',bolt(4,16),92.8),('washer',washer(4,.8),92),('nut',nut(4,3.2),80)]:hadd('seam_'+str(i)+'_'+n,s.translate((x,y,z)))
for i,(x,y) in enumerate(standpts):
 for n,s,z in [('bolt',bolt(3,70),147.5),('top_washer',washer(3,.5),147),('bottom_washer',washer(3,.5),85.5),('nyloc',nut(3,4),81.5)]:hadd('platform_'+str(i)+'_'+n,s.translate((x,y,z)))
for sx in [-1,1]:
 for sy in [-1,1]:
  tag=('F' if sx>0 else 'R')+('L' if sy>0 else 'R')
  for i,(x,y) in enumerate(cappts):
   for n,s,z in [('bolt',bolt(3,12),15.9),('washer',washer(3,.5),15.4),('nut',nut(3,2.4),4.2)]:hadd(tag+'_cap_'+str(i)+'_'+n,modulepose(s.translate((x,y,z)),sx,sy))
  for i,(x,y) in enumerate(m3pts):
   for n,s,z in [('bolt',bolt(3,12),16.5),('washer',washer(3,.5),16),('nut',nut(3,2.4),5)]:hadd(tag+'_wheel_'+str(i)+'_'+n,modulepose(axial(s.translate((x,y,0)),z),sx,sy))
  for i,(x,y) in enumerate(m2pts):
   for n,s,z in [('bolt',bolt(2,8),11.3),('washer',washer(2,.3),11)]:hadd(tag+'_horn_'+str(i)+'_'+n,modulepose(axial(s.translate((x,y,0)),z),sx,sy))
assy.add(hardware,name='standard_fasteners_nominal')
# Store both clean main assembly and nominal hardware reference.
print('saving assembly',flush=True)
assy.save(str(ROOT/'STEP/ASSEMBLY_HX30HM_R1.step'))
hardware.save(str(ROOT/'STEP/HARDWARE_nominal_fasteners.step'))
# Export geometric summaries and reusable assembly mesh for documentation.
report={'parameters':P,'parts':{},'assembly_instances':len(placed),'status':'Engineering prototype R1; not production-released','manufacturer_model_used':True,'hardware_note':'Nominal unthreaded bolts, nuts and washers included; OEM centre retaining screws not modeled. Fastener threads and supplier spline interface excluded from volume checks.'}
for n,v in parts.items():
 s=v['shape'];q=cq.importers.importStep(str(ROOT/'STEP'/f'{n}.step')).val()
 assert q.isValid() and len(q.Solids())==1,n
 report['parts'][n]={k:v2 for k,v2 in v.items() if k!='shape'}
 report['parts'][n]['volume_mm3']=round(s.Volume(),2)
# Test printed-to-printed/vendor intersections; vendor internals and mating spline
# overlap are outside this assembly check. Pair BBoxes first for performance.
intersections=[];checked=0
for i,(na,a,ka) in enumerate(placed):
 for nb,b,kb in placed[:i]:
  # Vendor casing fit is checked conservatively by its envelope below.
  if ka=='vendor' or kb=='vendor':continue
  ba=a.BoundingBox();bb=b.BoundingBox()
  if any(getattr(ba,k+'max')<=getattr(bb,k+'min')+1e-5 or getattr(bb,k+'max')<=getattr(ba,k+'min')+1e-5 for k in 'xyz'):continue
  checked+=1
  print('checking',na,nb,flush=True)
  vol=a.intersect(b).Volume()
  if vol>.05:intersections.append({'a':na,'b':nb,'volume_mm3':round(vol,4)})
# Full servo AABB (includes shaft/connector features) conservative envelope.
b=servo.BoundingBox()
envelope=box(b.xmin,b.ymin,b.zmin,b.xlen,b.ylen,b.zlen)
report['servo_envelope_fit_mm3']={}
for n,s in [('cradle',cradle),('cap',cap),('lower_shim',shim),('upper_shim',shim.translate((0,0,45.55)))]:
 print('checking envelope',n,flush=True)
 report['servo_envelope_fit_mm3'][n]=round(envelope.intersect(s).Volume(),6)
report['interference']={'bbox_candidate_pairs_checked':checked,'threshold_mm3':.05,'overlaps':intersections}
(ROOT/'docs/validation.json').write_text(json.dumps(report,indent=2))
(ROOT/'source/nominal_dimensions.json').write_text(json.dumps(P,indent=2))
# Tessellation for fast preview (discard hidden internal servo solids).
mesh=[]
for n,s,k in placed:
 if k=='vendor' and n.endswith('_servo'):s=C.makeCompound(s.Solids()[:3])
 vv,ff=s.tessellate(.35,.35)
 mesh.append({'name':n,'v':[v.toTuple() for v in vv],'f':ff,'color':DARK if ('tyre' in n or 'servo' in n or 'shim' in n) else GREY if 'horn' in n else ORANGE if any(t in n for t in ['adapter','cap','splice','spacer']) else BLUE})
(ROOT/'docs/preview_mesh.json').write_text(json.dumps(mesh))
print(json.dumps(report,indent=2))

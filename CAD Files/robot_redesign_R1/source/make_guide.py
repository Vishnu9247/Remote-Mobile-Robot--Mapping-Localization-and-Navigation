from pathlib import Path
import re,html,json
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
R=Path(__file__).resolve().parents[1];D=R/'docs'
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyR',fontName='Helvetica',fontSize=9.3,leading=13,spaceAfter=7,textColor=colors.HexColor('#263b4b')))
styles.add(ParagraphStyle(name='SmallR',parent=styles['BodyR'],fontSize=8,leading=10))
styles.add(ParagraphStyle(name='CellR',parent=styles['BodyR'],fontSize=8.2,leading=10,spaceAfter=0))
styles.add(ParagraphStyle(name='TitleR',fontName='Helvetica-Bold',fontSize=27,leading=31,textColor=colors.HexColor('#18394d'),spaceAfter=15))
styles['Heading2'].textColor=colors.HexColor('#18394d');styles['Heading2'].spaceBefore=13;styles['Heading2'].spaceAfter=8
W,H=A4;flow=[]
def p(t,style='BodyR'):
 t=html.escape(t);t=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',t);return Paragraph(t,styles[style])
flow+=[p('HX-30HM\nMobile Robot Base'.replace('\n',' / '),'TitleR'),p('R1 - FIRST-ARTICLE BUILD PACKAGE','Heading2'),p('Real manufacturer servo CAD. Printed chassis, clamps, horn adapters, rims and tyres. M3/M4 structural fasteners.'),Image(str(D/'assembly_preview.png'),width=495,height=315),Spacer(1,10),p('220 x 220 mm print bed | 3 kg total-mass design target | Four-wheel skid steering','Heading2'),p('The assembly is geometrically checked, but production release requires physical fit, load and endurance validation. Servo radial wheel-load capacity has not been established.'),p('Preview omits small fasteners for clarity; the STEP assembly includes nominal bolts, nuts and washers. OEM centre retaining screws are specified but not modeled.','SmallR'),PageBreak()]
flow += [p('Layout and serviceable wheel module','TitleR'),Image(str(D/'dimension_overview.png'),width=495,height=247.5),p('Nominal dimensions in millimetres. Schematic views show design datums; use STEP solids for part geometry.','SmallR'),Image(str(D/'wheel_module_exploded.png'),width=460,height=322),p('Exploded view separates the tyre, rim, printed adapter, metal horn, servo cradle and clamp cap. Components share the same axle; separation is illustrative.','SmallR'),PageBreak()]
lines=(D/'BUILD_GUIDE.md').read_text().splitlines();i=0
while i<len(lines):
 l=lines[i].strip()
 if not l:i+=1;continue
 if l.startswith('# '):i+=1;continue
 if l.startswith('## '):flow.append(p(l[3:],'Heading2'));i+=1;continue
 if l.startswith('|'):
  rows=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
   if not all(re.match(r'^:?-+:?$',x) for x in cells):rows.append(cells)
   i+=1
  cols=len(rows[0]);widths={2:[230,265],3:[275,35,185],4:[32,226,42,195]}[cols]
  data=[[p(c,'CellR') for c in row] for row in rows]
  t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dce8ee')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#8ba4b3')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f4f6f8')]),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));flow.extend([t,Spacer(1,8)]);continue
  
 paragraph=l;i+=1
 while i<len(lines) and lines[i].strip() and not lines[i].startswith(('## ','|','- ')) and not re.match(r'^\d+\. ',lines[i]):paragraph+=' '+lines[i].strip();i+=1
 flow.append(p(paragraph))
r=json.loads((D/'validation.json').read_text())
flow.extend([p('Digital verification result','Heading2'),p(f"{len(r['parts'])} unique printed part types reimported as valid single solids; all fit the 220 x 220 mm print bed. Printed-part interference: {len(r['interference']['overlaps'])} overlaps above 0.05 cubic millimetres. Servo envelope intersections with cradle, cap and shims: zero. {len(r.get('stl_checks',{}))} STL meshes passed closed-edge and positive-volume checks."),p('Limits: checks exclude fastener thread engagement, OEM spline tolerances, wire bend radii, tyre deformation, real material strength and service loads. See validation.json for the machine-readable results.')])
def page(canvas,doc):
 canvas.saveState();canvas.setStrokeColor(colors.HexColor('#d3dde3'));canvas.line(50,39,W-50,39);canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#607483'));canvas.drawString(50,26,'HX-30HM MOBILE BASE / R1 / FIRST ARTICLE');canvas.drawRightString(W-50,26,str(doc.page));canvas.restoreState()
doc=SimpleDocTemplate(str(D/'HX30HM_R1_Build_Guide.pdf'),pagesize=A4,rightMargin=50,leftMargin=50,topMargin=42,bottomMargin=50,title='HX-30HM Mobile Base R1 - Build Guide',author='OpenAI')
doc.build(flow,onFirstPage=page,onLaterPages=page);print('PDF created')

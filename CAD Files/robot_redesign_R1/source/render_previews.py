from pathlib import Path
import json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Rectangle,Circle
R=Path(__file__).resolve().parents[1];D=R/'docs';mesh=json.loads((D/'preview_mesh.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
def raster(items,out,az=-52,el=28,explode=False):
 from PIL import Image
 az=np.deg2rad(az);el=np.deg2rad(el)
 eye=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
 right=np.array([-np.sin(az),np.cos(az),0.]);up=np.cross(eye,right)
 basis=np.stack([right,up,eye],axis=1)
 meshes=[];bounds=[]
 for m in items:
  v=np.array(m['v']);n=m['name']
  if explode:
   if 'tyre' in n:v[:,1]-=110
   elif 'rim' in n:v[:,1]-=65
   elif 'adapter' in n:v[:,1]-=35
   elif 'horn' in n:v[:,1]-=15
   elif 'cap' in n or 'upper_shim' in n:v[:,2]+=22
  q=v@basis;meshes.append((v,q,np.array(m['f']),m['color']));bounds.append(q)
 points=np.concatenate(bounds);low=points[:,:2].min(0);high=points[:,:2].max(0)
 width,height=1600,1050;scale=min((width-120)/(high[0]-low[0]),(height-100)/(high[1]-low[1]));mid=(high+low)/2
 zbuf=np.full((height,width),-np.inf);canvas=np.ones((height,width,3),dtype=np.uint8)*248
 light=np.array([.2,-.5,.85]);light/=np.linalg.norm(light)
 for v,q,faces,col in meshes:
  q=q.copy();q[:,0]=(q[:,0]-mid[0])*scale+width/2;q[:,1]=height/2-(q[:,1]-mid[1])*scale
  for ids in faces:
   t=q[ids];xy=t[:,:2];xmin=max(0,int(np.floor(xy[:,0].min())));xmax=min(width-1,int(np.ceil(xy[:,0].max())));ymin=max(0,int(np.floor(xy[:,1].min())));ymax=min(height-1,int(np.ceil(xy[:,1].max())))
   if xmax<xmin or ymax<ymin:continue
   x0,y0=xy[0];x1,y1=xy[1];x2,y2=xy[2];den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
   if abs(den)<1e-9:continue
   xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
   a=((y1-y2)*(xx-x2)+(x2-x1)*(yy-y2))/den;b=((y2-y0)*(xx-x2)+(x0-x2)*(yy-y2))/den;c=1-a-b
   zz=a*t[0,2]+b*t[1,2]+c*t[2,2];target=zbuf[ymin:ymax+1,xmin:xmax+1]
   mask=(a>=-1e-8)&(b>=-1e-8)&(c>=-1e-8)&(zz>target)
   if not mask.any():continue
   norm=np.cross(v[ids[1]]-v[ids[0]],v[ids[2]]-v[ids[0]]);ln=np.linalg.norm(norm)
   shade=.68+.32*abs(norm@light)/max(ln,1e-9);rgb=np.clip(np.array(col)*shade*255,0,255).astype(np.uint8)
   target[mask]=zz[mask];canvas[ymin:ymax+1,xmin:xmax+1][mask]=rgb
 Image.fromarray(canvas).save(out)
raster(mesh,D/'assembly_preview.png')
raster([m for m in mesh if m['name'].startswith('front_right_')],D/'wheel_module_exploded.png',az=-18,el=22,explode=True)
def dim(ax,a,b,text,offset=(0,0)):
 ax.annotate('',xy=a,xytext=b,arrowprops=dict(arrowstyle='<->',lw=.8,color='#596477'))
 ax.text((a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1],text,ha='center',va='center',fontsize=9,color='#263b4b',bbox=dict(facecolor='white',edgecolor='none',pad=1))
fig,axs=plt.subplots(1,2,figsize=(12,6))
a=axs[0];a.add_patch(Rectangle((-150,-100),300,200,facecolor='#d8e7ee',edgecolor='#223d50'))
a.plot([0,0],[-100,100],color='#f07a34',ls='--')
for x in [-95,95]:
 for y in [-123,123]:
  a.add_patch(Rectangle((x-60,y-12),120,24,facecolor='#444950'))
  a.plot(x,y,'+',color='white');a.plot([x,x],[-150,150],color='#9ba5ae',lw=.6,ls=':')
a.add_patch(Rectangle((-60,-50),120,100,fill=False,edgecolor='#f07a34',ls='--'))
dim(a,(-155,-159),(155,-159),'310 overall',(0,0));dim(a,(-175,-135),(-175,135),'270',(-9,0));dim(a,(-95,155),(95,155),'190 wheelbase',(0,0));dim(a,(175,-123),(175,123),'246 track',(10,0));a.text(0,180,'TOP VIEW - X forward / Y left',ha='center',weight='bold')
a.set(xlim=(-210,210),ylim=(-180,195),aspect='equal');a.axis('off')
a=axs[1];a.plot([-165,165],[0,0],color='#596477')
for x in [-95,95]:
 a.add_patch(Circle((x,60),60,fill=False,lw=2,edgecolor='#223d50'));a.add_patch(Circle((x,60),2,color='#f07a34'));a.add_patch(Rectangle((x-23,21.6),46,64.4,fill=False,edgecolor='#9ba5ae'))
a.add_patch(Rectangle((-150,86),300,6,facecolor='#d8e7ee',edgecolor='#223d50'));a.add_patch(Rectangle((-60,142),120,5,facecolor='#d8e7ee',edgecolor='#223d50'))
for x in [-45,45]:a.add_patch(Rectangle((x-6,92),12,50,facecolor='#f07a34'))
dim(a,(-95,-20),(95,-20),'190');dim(a,(173,0),(173,147),'147',(12,0));dim(a,(-95,60),( -95+42.43,60+42.43),'R60',(0,8));a.text(0,170,'SIDE VIEW - ground datum Z=0',ha='center',weight='bold');a.text(0,13,'21.6 mm minimum cradle clearance',ha='center',fontsize=8)
a.set(xlim=(-175,210),ylim=(-40,190),aspect='equal');a.axis('off')
fig.tight_layout();fig.savefig(D/'dimension_overview.png',dpi=180);plt.close(fig)
print('Rendered three previews')

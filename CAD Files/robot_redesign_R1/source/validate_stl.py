from pathlib import Path
import json,struct,numpy as np
R=Path(__file__).resolve().parents[1];out={}
for p in sorted((R/'STL').glob('*.stl')):
 data=p.read_bytes();n=struct.unpack_from('<I',data,80)[0]
 assert len(data)==84+50*n,p.name
 a=np.frombuffer(data, dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]),offset=84,count=n)['v'].astype(float)
 vv=np.round(a.reshape(-1,3)*1e4).astype(np.int64)
 _,ids=np.unique(vv,axis=0,return_inverse=True);ids=ids.reshape(-1,3)
 ed=np.concatenate([ids[:,[0,1]],ids[:,[1,2]],ids[:,[2,0]]]);ed.sort(axis=1)
 _,counts=np.unique(ed,axis=0,return_counts=True)
 non=int(np.sum(counts!=2));deg=int(np.sum(np.linalg.norm(np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]),axis=1)<1e-9))
 v=np.einsum('ij,ij->i',a[:,0],np.cross(a[:,1],a[:,2])).sum()/6
 assert non==0,(p.name,non)
 assert deg==0,(p.name,deg)
 assert v>0,(p.name,v)
 out[p.name]={'triangles':n,'nonmanifold_edges':non,'degenerate_triangles':deg,'volume_mm3':round(float(v),3)}
report=json.loads((R/'docs/validation.json').read_text());report['stl_checks']=out
(R/'docs/validation.json').write_text(json.dumps(report,indent=2));print('All',len(out),'STL meshes closed, consistently edged and positive-volume')

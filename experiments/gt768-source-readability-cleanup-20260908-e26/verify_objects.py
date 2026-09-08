"""Compile both packages without debug line metadata; require whole-object equality."""
from pathlib import Path
import subprocess,sys,hashlib,json
old,new,out=map(Path,sys.argv[1:])
out.mkdir(parents=True,exist_ok=True)
rows=[]
for src in sorted(new.iterdir()):
    if src.suffix not in ('.S','.c'): continue
    objs=[]
    for tag,root in [('before',old),('after',new)]:
        obj=out/(tag+'-'+src.name+'.o')
        subprocess.run(['cc','-O3','-fomit-frame-pointer','-I'+str(root),'-c',str(root/src.name),'-o',str(obj)],check=True)
        objs.append(obj)
    assert objs[0].read_bytes()==objs[1].read_bytes(),src.name
    rows.append({'source':src.name,'identical':True,'sha256':hashlib.sha256(objs[0].read_bytes()).hexdigest()})
print(json.dumps(rows,indent=2))

from pathlib import Path
import subprocess,tarfile,io,shutil,json,hashlib
R=Path(__file__).resolve().parent;B=R/'.build';B.mkdir(exist_ok=True)
root=R.parents[1];rel='ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768'
base='b2f9ee83350a3e11dc2eae802ae0e5d7651586d4'
raw=subprocess.check_output(['git','archive',base,rel],cwd=root)
with tarfile.open(fileobj=io.BytesIO(raw)) as t:t.extractall(B/'baseline-tree',filter='data')
shutil.copytree(B/'baseline-tree'/rel,B/'B-package')
shutil.copytree(root/rel,B/'E-package')
out={'baseline':base,'candidate_source':'561b6aa50dc0e237c3c884ec7174a208baf869e5','candidate_branch_head_before_gate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'checks':{}}
for v in ['B','E']:
 p=B/(v+'-package')
 with (B/(v+'-mac.log')).open('w') as log:subprocess.run(['make','check','BUILD_DIR='+str(B/(v+'-mac'))],cwd=p,stdout=log,stderr=subprocess.STDOUT,check=True)
 out['checks'][v]={'mac':'pass','sources':{str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()}}
(R/'preflight.json').write_text(json.dumps(out,indent=2)+'\n')
print('B/E Mac checks passed')

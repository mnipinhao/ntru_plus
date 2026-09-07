"""Compare each original assembly section against its merged owner on Linux.
Exact section bytes and normalized relocation targets must match. Does not use
instruction-count equality as a substitute for code/table equality.
"""
import sys,re,struct,subprocess,json,hashlib
from pathlib import Path
old,new,out=map(Path,sys.argv[1:4]);out.mkdir(parents=True,exist_ok=True)
groups={'pack':['pack','unpack','keygen_pack','decap_pack'],
        'base':['base','keygen_baseinv_prepare','keygen_baseinv_tree','keygen_baseinv_finish','fqinv','encap_muladd','decap_verify','decap_packed64','decap_base'],
        'ntt':['ntt','invntt','decap_ntt','decap_forward']}
def parse(path):
 d=path.read_bytes();shoff=struct.unpack_from('<Q',d,40)[0];size,n,si=struct.unpack_from('<HHH',d,58)
 hs=[struct.unpack_from('<IIQQQQIIQQ',d,shoff+i*size) for i in range(n)]
 h=hs[si];names=d[h[4]:h[4]+h[5]]
 return {names[h[0]:].split(b'\0')[0].decode():(h,d[h[4]:h[4]+h[5]]) for h in hs if h[1]!=8}
def build(root,stem,kind):
 obj=out/(kind+'-'+stem+'.o')
 subprocess.run(['gcc','-I'+str(root),'-c',str(root/(stem+'.S')),'-o',str(obj)],check=True)
 return parse(obj)
def relocations(stem,kind):
 text=subprocess.check_output(['readelf','-rW',str(out/(kind+'-'+stem+'.o'))]).decode()
 (out/(kind+'-'+stem+'.relocations')).write_text(text)
 result={};section=None
 for line in text.splitlines():
  match=re.match(r"Relocation section '([^']+)'",line)
  if match:section=match[1];result[section]=[]
  match=re.match(r'\s*([0-9a-f]{12,16})\s+[0-9a-f]+\s+(R_AARCH64_\w+)\s+[0-9a-f]+\s+(.*)',line)
  if match:result[section].append((int(match[1],16),match[2],match[3]))
 return result
records=[]
for owner,members in groups.items():
 if len(members)==1 or any((new/(m+'.S')).exists() for m in members[1:]):continue
 merged=build(new,owner,'merged')
 mr=relocations(owner,'merged')
 for m in members:
  orig=build(old,m,'original')
  sr=relocations(m,'original')
  for name,(h,data) in orig.items():
   if not (h[2]&2) or not data:continue
   target=name if name not in ['.text','.data'] else name+'.module_'+m+'_body'
   assert target in merged,(owner,m,name,target)
   nh,nd=merged[target]
   record={'owner':owner,'source':m,'old_section':name,'new_section':target,'bytes':len(data),
           'equal':data==nd,'alignment_equal':h[8]==nh[8], 'sha256':hashlib.sha256(data).hexdigest()}
   records.append(record)
   if not record['equal']:
    print('differing words',[(hex(i),data[i:i+4].hex(),nd[i:i+4].hex()) for i in range(0,max(len(data),len(nd)),4) if data[i:i+4]!=nd[i:i+4]][:24],flush=True)
   assert record['equal'] and record['alignment_equal'],record
   def normalize(rows):
    normalized=[]
    for offset,kind,target in rows:
     for mod in members:
      target=target.replace('.text.module_'+mod+'_body','.text').replace('.data.module_'+mod+'_body','.data')
      target=target.replace('module_'+mod+'_','')
     normalized.append((offset,kind,target))
    return normalized
   record['relocations_equal']=normalize(sr.get('.rela'+name,[]))==normalize(mr.get('.rela'+target,[]))
   assert record['relocations_equal'],(record,sr.get('.rela'+name),mr.get('.rela'+target))
result={'sections':records,'all_bytes_and_alignments_equal':True}
(out/'sections.json').write_text(json.dumps(result,indent=2)+'\n')
print('Exact code/table section bytes and alignments PASS:',len(records))

#!/usr/bin/env python3
import argparse,json,re,statistics,subprocess
from collections import defaultdict
from pathlib import Path
CALLS={
'official':[(0x604e,'decode'),(0x60d1,'cbd_r'),(0x60de,'ntt_r'),(0x60ee,'pack_r'),(0x78df,'hash_input_copy'),(0x6111,'sotp_m'),(0x611e,'ntt_m'),(0x6138,'basemul'),(0x614f,'add_m'),(0x615c,'pack_ct')],
'gt':[(0x9e0a,'decode_body'),(0x3da1,'cbd_r'),(0x3db6,'frontend_r'),(0x3dcb,'ntt_r'),(0x1e02a,'pack_r'),(0x3df0,'sotp_m'),(0x3e05,'frontend_m'),(0x3e1a,'ntt_m_ql2'),(0x3e34,'basemul_ql2'),(0x3e4c,'ql2_add_pack_ct')]}
MMAP=re.compile(r'\[0x([0-9a-f]+)\(0x([0-9a-f]+)\) @ 0x([0-9a-f]+).+\]: r-xp (.+)$');BR=re.compile(r'0x([0-9a-f]+)/0x([0-9a-f]+)/[^/]*/[^/]*/[^/]*/(\d+)/([^/]*)/')
def perf(data,*args):return subprocess.run(['perf','script','-i',str(data),*args],capture_output=True,text=True,check=True).stdout
def base(data,binary):
 x=[];wanted=str(binary.resolve())
 for line in perf(data,'--show-mmap-events').splitlines():
  m=MMAP.search(line)
  if m and str(Path(m.group(4)).resolve())==wanted:x.append(int(m.group(1),16)-int(m.group(3),16))
 if len(set(x))!=1:raise RuntimeError((wanted,x))
 return x[0]
def summary(v):
 if not v:return None
 v=sorted(v);return {'observations':len(v),'median':statistics.median(v),'p10':v[round((len(v)-1)*.1)],'p90':v[round((len(v)-1)*.9)]}
def trace(data,binary,impl):
 b=base(data,binary);returns={a+5:n for a,n in CALLS[impl]};v=defaultdict(list)
 for line in perf(data,'-F','brstack').splitlines():
  for m in BR.finditer(line):
   target=int(m.group(2),16)-b
   if m.group(4)=='RET' and target in returns:v[returns[target]].append(int(m.group(3)))
 return {n:summary(x) for n,x in v.items()}
def launch(rows):
 keys=sorted({k for r in rows for k in r['intervals']});return {k:summary([r['intervals'][k]['median'] for r in rows if r['intervals'].get(k)]) for k in keys}
def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();m=json.loads(a.manifest.read_text());bins={k:Path(v['path']) for k,v in m['binaries'].items()};rows=[];groups=defaultdict(list)
 for rec in m['rows']:
  impl=rec['implementation'];row={**rec,'intervals':trace(a.manifest.parent/rec['perf_data'],bins[impl],impl)};rows.append(row);groups[impl].append(row)
 s={k:launch(v) for k,v in groups.items()};o,g=s['official'],s['gt'];spec={'decode':(['decode'],['decode_body']),'cbd_r':(['cbd_r'],['cbd_r']),'r_producer':(['ntt_r'],['frontend_r','ntt_r']),'r_serializer':(['pack_r'],['pack_r']),'hash_input_copy':(['hash_input_copy'],[]),'sotp_m':(['sotp_m'],['sotp_m']),'m_producer':(['ntt_m'],['frontend_m','ntt_m_ql2']),'basemul':(['basemul'],['basemul_ql2']),'sum_and_ct_serializer':(['add_m','pack_ct'],['ql2_add_pack_ct'])};sem={}
 for name,(ok,gk) in spec.items():
  if all(k in o and o[k] for k in ok) and all(k in g and g[k] for k in gk):
   ov=sum(o[k]['median'] for k in ok);gv=sum(g[k]['median'] for k in gk);sem[name]={'official_core_cycles':ov,'gt_core_cycles':gv,'gt_minus_official':gv-ov}
 out={'schema':'gt32-rhash-aslroff-profile-145-analysis','warning':'LBR leaf medians are descriptive and non-additive','summaries':s,'semantic_leaf_map':sem,'rows':rows};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(sem,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];B=E/'build';BIN={n:B/f'measure-{n}' for n in ('control','candidate')};EX={'ntruplus768_enc_derand_impl','ntruplus768_hash_g_from_m_avx2'}
def out(c):return subprocess.check_output(c,text=True)
def symbols(p):
 r={}
 for line in out(['nm','-S','-n',str(p)]).splitlines():
  f=line.split()
  if len(f)>=4 and f[2].lower() in {'t','r'}:r[f[3]]=(int(f[0],16),int(f[1],16),f[2])
 return r
def section(p,n):
 for line in out(['readelf','-SW',str(p)]).splitlines():
  m=re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+\S+\s+(\S+)',line)
  if m and m.group(1)==n:return int(m.group(2),16),int(m.group(3),16),m.group(4)
 raise SystemExit(f'missing {n} in {p}')
def bytes_at(p,a,s):
 text=out(['objdump','-d',f'--start-address={a}',f'--stop-address={a+s}',str(p)]);b=[]
 for line in text.splitlines():
  m=re.match(r'\s*[0-9a-f]+:\s+((?:[0-9a-f]{2}\s+)+)',line)
  if m:b.extend(m.group(1).split())
 return bytes.fromhex(''.join(b))
def main():
 maps={n:symbols(p) for n,p in BIN.items()};bad=[];checked=0
 for n in sorted(set(maps['control'])&set(maps['candidate'])):
  if n in EX or n.startswith(('supercop','cpucycles')):continue
  a,b=maps['control'][n],maps['candidate'][n]
  if a!=b:bad.append({'symbol':n,'reason':'geometry','control':a,'candidate':b})
  elif a[2].lower()=='t' and a[1] and bytes_at(BIN['control'],*a[:2])!=bytes_at(BIN['candidate'],*b[:2]):bad.append({'symbol':n,'reason':'bytes'})
  else:checked+=1
 if bad or checked<80:raise SystemExit(json.dumps({'checked':checked,'mismatches':bad[:20]},indent=2))
 helper={n:maps[n]['ntruplus768_hash_g_from_m_avx2'] for n in BIN}
 if helper['control'][:2]!=helper['candidate'][:2] or bytes_at(BIN['control'],*helper['control'][:2])!=bytes_at(BIN['candidate'],*helper['candidate'][:2]):
  raise SystemExit(f'helper geometry/bytes mismatch: {helper}')
 slots={n:section(B/f'objects/encap-{n}.o','.text.ntruplus768_enc_derand_impl')[1] for n in BIN}
 if set(slots.values())!={611}:raise SystemExit(f'slot mismatch {slots}')
 tails={sec:{n:section(p,sec) for n,p in BIN.items()} for sec in ('.e0v_tail','.ql2_tail','.rhash_tail')}
 for sec,profiles in tails.items():
  if profiles['control'][:2]!=profiles['candidate'][:2]:raise SystemExit(f'{sec} mismatch')
  for v in profiles.values():
   if v[0]%4096 or 'A' not in v[2] or 'X' not in v[2] or 'W' in v[2]:raise SystemExit(f'invalid tail {sec}: {v}')
 for p in BIN.values():
  if re.search(r'RWE',out(['readelf','-lW',str(p)])):raise SystemExit(f'RWX {p}')
 anchor=B/'anchor/measure-ql2';am=symbols(anchor);anchor_bad=[];anchor_checked=0
 for n in sorted(set(am)&set(maps['control'])):
  if n in {'main','measure','printentry','printword','allocate','alignedcalloc','crash','randombytes','_start','__abi_tag'} or n.startswith(('supercop','cpucycles','ntruplus768_hash_g_from_m')):continue
  a,b=am[n],maps['control'][n]
  if a!=b:anchor_bad.append({'symbol':n,'anchor':a,'control':b,'reason':'geometry'})
  elif a[2].lower()=='t' and a[1] and bytes_at(anchor,*a[:2])!=bytes_at(BIN['control'],*b[:2]):anchor_bad.append({'symbol':n,'reason':'bytes'})
  else:anchor_checked+=1
 if anchor_bad or anchor_checked<75:raise SystemExit(json.dumps({'anchor_checked':anchor_checked,'mismatches':anchor_bad[:20]},indent=2))
 result={'status':'PASS','shared_symbols_checked':checked,'shared_mismatches':0,'production_anchor_symbols_checked':anchor_checked,'production_anchor_mismatches':0,'caller_slots':slots,'encap_symbols':{n:maps[n]['ntruplus768_enc_derand_impl'][:2] for n in BIN},'tails':{s:{n:{'address':v[0],'size':v[1],'flags':v[2]} for n,v in p.items()} for s,p in tails.items()},'helper_symbol':{n:helper[n][:2] for n in BIN},'helper_bytes_identical':True,'security':{'rwx_segment':False,'tails_page_aligned_rx':True},'elf_sha256':{n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in BIN.items()}}
 (E/'generated/audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

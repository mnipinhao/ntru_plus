#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
EXP=Path(__file__).resolve().parents[1];RAW=EXP/'raw';BINS={n:EXP/'build'/n for n in ('official','gt')}
def main():
 RAW.mkdir(exist_ok=True);rows=[];seq=0
 for block in range(1,65):
  order=('official','gt') if block%2 else ('gt','official')
  for pos,impl in enumerate(order,1):
   seq+=1;data=RAW/f'{seq:03d}-{impl}.data'
   subprocess.run(['setarch','x86_64','-R','perf','record','-q','-e','cpu_core/cycles/u','-c','50000','-j','any_call,any_ret','-o',str(data),'--','taskset','-c','1',str(BINS[impl].resolve())],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   rows.append({'block':block,'position':pos,'implementation':impl,'perf_data':str(data.relative_to(EXP))})
 m={'schema':'gt32-rhash-aslroff-profile-145','aslr':'disabled','event':'cpu_core/cycles/u period=50000 any_call,any_ret','cpu':1,'binaries':{n:{'path':str(p.resolve())} for n,p in BINS.items()},'rows':rows};(EXP/'lbr-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
if __name__=='__main__':main()

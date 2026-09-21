#!/usr/bin/env python3
"""Record linked instruction-class, section, and alignment evidence for symbols."""
from __future__ import annotations
import argparse, json, re, subprocess
from pathlib import Path
from supercop_workflow import sha256_file
ROUTING=("vperm","vpshuf","vpunpck","vpblend","vinsert","vextract")
def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--elf",type=Path,required=True)
    ap.add_argument("--symbol",action="append",required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    if a.output.exists(): raise SystemExit(f"refusing to overwrite {a.output}")
    nm=subprocess.run(["nm","-n","-S","--defined-only",str(a.elf)],text=True,stdout=subprocess.PIPE,check=True).stdout
    symbols={}
    for line in nm.splitlines():
      f=line.split()
      if len(f)==4 and f[3] in a.symbol: symbols[f[3]]=(int(f[0],16),int(f[1],16))
    missing=[s for s in a.symbol if s not in symbols]
    if missing: raise SystemExit(f"ELF lacks symbols: {missing}")
    dis=subprocess.run(["objdump","-d","-M","intel","--no-show-raw-insn",str(a.elf)],text=True,stdout=subprocess.PIPE,check=True).stdout
    lines=[]
    for line in dis.splitlines():
      m=re.match(r"\s*([0-9a-f]+):\s+([a-zA-Z0-9.]+)\s*(.*)",line)
      if m: lines.append((int(m.group(1),16),m.group(2),m.group(3)))
    audits={}
    for name,(start,size) in symbols.items():
      ins=[x for x in lines if start <= x[0] < start+size]
      c={"instructions":len(ins),"vpmullw":0,"vpmulhw":0,"vpmulhrsw":0,"routing":0,
         "constant_memory_operands":0,"memory_loads":0,"memory_stores":0,
         "stack_memory_operands":0,"calls":0,"branches":0,"vzeroupper":0,
         "indexed_memory_operands":0}
      for _,op,args in ins:
        if op in c: c[op]+=1
        if op.startswith(ROUTING): c["routing"]+=1
        if "[rip" in args: c["constant_memory_operands"]+=1
        if "[" in args:
          dest=args.split(",",1)[0]
          c["memory_stores" if "[" in dest else "memory_loads"]+=1
          if "rsp" in args or "rbp" in args: c["stack_memory_operands"]+=1
          if "*" in args: c["indexed_memory_operands"]+=1
        if op.startswith("call"): c["calls"]+=1
        if op.startswith("j"): c["branches"]+=1
      audits[name]={"address":start,"address_mod32":start%32,"address_mod64":start%64,
                    "text_bytes":size,**c}
    sections=subprocess.run(["size","-A",str(a.elf)],text=True,stdout=subprocess.PIPE,check=True).stdout
    sec={}
    for line in sections.splitlines():
      f=line.split()
      if len(f)>=2 and f[0] in (".text",".rodata") and f[1].isdigit(): sec[f[0]]=int(f[1])
    record={"schema":"ntruplus-linked-static-audit/v1","elf":str(a.elf.resolve()),
      "elf_sha256":sha256_file(a.elf),"sections":sec,"symbols":audits,
      "taxonomy_note":"multiply/reduction counts are linked mnemonic counts, not inferred semantic chains"}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print(f"audited {a.output}"); return 0
if __name__=="__main__": raise SystemExit(main())

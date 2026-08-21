#!/usr/bin/env python3
from __future__ import annotations
import argparse, difflib, hashlib, json, re, subprocess
from collections import defaultdict
from pathlib import Path

SELECTED = (
 "ntruplus768_baseinv_j1_avx2", "ntruplus768_basemul_scale_m_avx2",
 "ntruplus768_basemul_general_m_avx2", "ntruplus768_basemul_f0_j1_avx2",
 "ntruplus768_baseinv_batch_tree_avx2", "ntruplus768_invntt_m_avx2",
 "ntruplus768_invntt_tail_avx2", "ntruplus768_ntt_frontend_avx2",
 "ntruplus768_ntt_m_avx2", "ntruplus768_ntt_p_avx2",
 "ntruplus768_unpack_m_body_avx2", "ntruplus768_pack_m_centered_avx2",
 "ntruplus768_pack_m_lazy10788_avx2", "ntruplus768_pack_p_sp1_lazy10788_avx2",
)
BRANCH = re.compile(r"^(?:j\w+|loop\w*)$")
REG = re.compile(r"%(?:ymm|xmm)\d+|%(?:r(?:1[0-5]|[8-9]|[abcd]x|[sd]i|[sb]p)|e(?:[abcd]x|[sd]i|[sb]p)|[abcd][lh])")

def run(*args): return subprocess.check_output(list(args), text=True)

def symbols(elf):
    found={}
    for line in run("nm","-S","--radix=x",str(elf)).splitlines():
        f=line.split()
        if len(f)==4 and f[3] in SELECTED:
            found[f[3]]={"start":int(f[0],16),"size":int(f[1],16)}
    missing=set(SELECTED)-set(found)
    if missing: raise SystemExit(f"missing selected symbols: {sorted(missing)}")
    return found

def disassemble(elf, meta):
    out={}
    line_re=re.compile(r"^\s*([0-9a-f]+):\s*((?:[0-9a-f]{2} )+)\s*([^\s]+)\s*(.*?)\s*$")
    for name,m in meta.items():
        text=run("objdump","-d","-w",f"--start-address={m['start']}",
                 f"--stop-address={m['start']+m['size']}",str(elf))
        ins=[]
        for line in text.splitlines():
            z=line_re.match(line)
            if not z: continue
            addr=int(z.group(1),16); raw=bytes.fromhex(z.group(2)); mnemonic=z.group(3); operands=z.group(4)
            ins.append({"addr":addr,"raw":raw.hex(),"size":len(raw),"mnemonic":mnemonic,"operands":operands})
        out[name]=ins
    return out

def callers(elf):
    ans=defaultdict(set)
    current=None
    for line in run("objdump","-d","-w",str(elf)).splitlines():
        m=re.match(r"^[0-9a-f]+ <([^>]+)>:$",line.strip())
        if m: current=m.group(1); continue
        if current and "call" in line:
            for target in re.findall(r"<([^>+]+)(?:\+[^>]*)?>",line):
                if target in SELECTED: ans[target].add(current)
    return {k:sorted(v) for k,v in ans.items()}

def normalized(i, registers=False):
    op=i["operands"].split("#",1)[0].strip()
    op=re.sub(r"[-+]?0x[0-9a-f]+\(%rip\)","RIPCONST(%rip)",op)
    if BRANCH.match(i["mnemonic"]): op="LOCAL_TARGET"
    if registers:
        op=REG.sub(lambda m:"%Y" if "mm" in m.group(0) else "%G",op)
    return i["mnemonic"]+" "+op

def blocks(name, ins, start, end):
    starts={start}
    addrs={x["addr"] for x in ins}
    for idx,i in enumerate(ins):
        if BRANCH.match(i["mnemonic"]):
            m=re.search(r"\b([0-9a-f]+)\b",i["operands"])
            if m and int(m.group(1),16) in addrs: starts.add(int(m.group(1),16))
            if idx+1<len(ins): starts.add(ins[idx+1]["addr"])
        elif i["mnemonic"].startswith("ret") and idx+1<len(ins): starts.add(ins[idx+1]["addr"])
    ordered=sorted(starts); result=[]
    for n,lo in enumerate(ordered):
        hi=ordered[n+1] if n+1<len(ordered) else end
        seq=[x for x in ins if lo<=x["addr"]<hi]
        if seq:
            result.append({"symbol":name,"start":lo,"end":hi,
                           "bytes":sum(x["size"] for x in seq),"instructions":seq})
    return result

def clusters(all_blocks, mode):
    groups=defaultdict(list)
    for b in all_blocks:
        if b["bytes"]<16 or len(b["instructions"])<3: continue
        if mode=="exact": key="".join(x["raw"] for x in b["instructions"])
        else: key="\n".join(normalized(x) for x in b["instructions"])
        groups[key].append(b)
    out=[]
    for key,items in groups.items():
        if len({x["symbol"] for x in items})<2: continue
        size=min(x["bytes"] for x in items)
        out.append({"bytes_each":size,"gross_duplicate_bytes":size*(len(items)-1),
                    "members":[{"symbol":x["symbol"],"start":x["start"],"end":x["end"]} for x in items],
                    "signature_sha256":hashlib.sha256(key.encode()).hexdigest()})
    return sorted(out,key=lambda x:x["gross_duplicate_bytes"],reverse=True)

def pair_matches(meta, code, register_shape=False):
    out=[]; names=list(SELECTED)
    for ai,a in enumerate(names):
        sa=[normalized(x,register_shape) for x in code[a]]
        for b in names[ai+1:]:
            sb=[normalized(x,register_shape) for x in code[b]]
            matcher=difflib.SequenceMatcher(None,sa,sb,autojunk=False)
            for m in matcher.get_matching_blocks():
                if m.size<8: continue
                aa=code[a][m.a:m.a+m.size]; bb=code[b][m.b:m.b+m.size]
                nbytes=min(sum(x["size"] for x in aa),sum(x["size"] for x in bb))
                if nbytes<48: continue
                out.append({"symbols":[a,b],"instructions":m.size,"shareable_upper_bound_bytes":nbytes,
                            "a_range":[aa[0]["addr"],aa[-1]["addr"]+aa[-1]["size"]],
                            "b_range":[bb[0]["addr"],bb[-1]["addr"]+bb[-1]["size"]]})
    return sorted(out,key=lambda x:x["shareable_upper_bound_bytes"],reverse=True)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--elf",type=Path,required=True); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    meta=symbols(a.elf); code=disassemble(a.elf,meta); call=callers(a.elf)
    inventory=[]; all_blocks=[]
    for name in SELECTED:
        m=meta[name]; bs=blocks(name,code[name],m["start"],m["start"]+m["size"]); all_blocks+=bs
        inventory.append({"symbol":name,"start":m["start"],"size":m["size"],"instructions":len(code[name]),"basic_blocks":len(bs),"callers":call.get(name,[])})
    data={"schema":"gt32-cross-symbol-census-047-v1","elf":str(a.elf.resolve()),
          "elf_sha256":hashlib.sha256(a.elf.read_bytes()).hexdigest(),
          "selected_text_bytes":sum(x["size"] for x in inventory),"inventory":inventory,
          "exact_basic_block_duplicates":clusters(all_blocks,"exact"),
          "relocation_normalized_basic_block_duplicates":clusters(all_blocks,"normalized"),
          "long_contiguous_normalized_matches":pair_matches(meta,code,False),
          "register_shape_matches_heuristic":pair_matches(meta,code,True)}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({"selected_text_bytes":data["selected_text_bytes"],
      "exact_clusters":len(data["exact_basic_block_duplicates"]),
      "normalized_clusters":len(data["relocation_normalized_basic_block_duplicates"]),
      "normalized_long_matches":len(data["long_contiguous_normalized_matches"]),
      "register_shape_matches":len(data["register_shape_matches_heuristic"])},indent=2))
if __name__=="__main__": main()

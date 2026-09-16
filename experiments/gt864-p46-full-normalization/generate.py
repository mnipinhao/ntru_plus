#!/usr/bin/env python3
"""Generate frozen P24 Full routing with P46 USHR+MLA canonicalization."""
from __future__ import annotations
import importlib.util, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
P23=HERE.parent/"gt864-p23-tobytes-global-dag"

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); assert spec and spec.loader
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def consume(mode,output,instance,slot=None):
    assert mode=="full"
    physical=slot is not None; value=str(slot) if physical else f"r{instance}"
    vector=f"v{value}" if physical else f"V<{value}>"
    scalar_d=f"d{value}" if physical else f"D<{value}>"
    lines=[f" sqrdmulh v29.8h,{vector}.8h,v28.8h",
           f" mls {vector}.8h,v29.8h,v27.8h",
           f" ushr v29.8h,{vector}.8h,#15",
           f" mla {vector}.8h,v29.8h,v27.8h",
           f" uzp1 v30.8h,{vector}.8h,{vector}.8h",
           f" uzp2 v31.8h,{vector}.8h,{vector}.8h",
           " shl v29.8h,v31.8h,#12",
           " orr v30.16b,v30.16b,v29.16b",
           " ushr v31.8h,v31.8h,#4",
           f" tbl {vector}.16b,{{v30.16b,v31.16b}},v26.16b"]
    base=("x5","x6","x7")[output//18]; offset=12*(output%18)
    lines += [f" stur {scalar_d},[{base},#{offset}]",f" mov x9,{vector}.d[1]",f" stur w9,[{base},#{offset+8}]"]
    return lines

def main():
    gen=load("p46_p23_gen",P23/"generate.py"); search=gen.load_search()
    report=json.loads((P23/"search-results.json").read_text()); outputs,_=search.build_dag()
    result=search.simulate(outputs,report["searched_order"],report["capacity_route_registers"],with_trace=True)
    slots={i["instance"]:i["slot"] for i in result["trace"] if i["kind"]=="compute"}
    for item in result["trace"]:
        if item["kind"]=="compute": item["input_slots"]=[slots[x] for x in item["inputs"]]
        else: item["slot"]=slots[item["instance"]]
    gen.consume=consume
    symbolic=gen.emit("full",result["trace"]).replace("gt864_p23_","gt864_p46_")
    physical=gen.emit("full",result["trace"],physical=True).replace("gt864_p23_","gt864_p46_")
    (HERE/"candidate-full.sym.S").write_text(symbolic);(HERE/"candidate-full.phys.S").write_text(physical)
    print(json.dumps({"route_per_top":result["instructions"],"candidate_per_top":987,"removed_per_call":108},indent=2))
if __name__=="__main__":main()

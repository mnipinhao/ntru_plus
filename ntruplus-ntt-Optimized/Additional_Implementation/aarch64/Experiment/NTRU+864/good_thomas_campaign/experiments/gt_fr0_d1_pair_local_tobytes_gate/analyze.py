#!/usr/bin/env python3
"""Prove whether an input-once ToBytes schedule can co-complete pack16 pairs."""
from __future__ import annotations
import hashlib,importlib.util,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=Path(subprocess.check_output(["git","rev-parse","--show-toplevel"],text=True).strip());P3A=HERE.parent/"gt_fr0_d1_byte_abi_architecture/analyze_architecture.py"
def main()->None:
 spec=importlib.util.spec_from_file_location("p3a",P3A);assert spec and spec.loader;p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);official,_=p.official_map(ROOT);shuffle2=[v for s in range(0,864,48) for v in p.shuffle2_block(s)];mapping=[official[shuffle2[i]] for i in range(864)];digest=hashlib.sha256(b"".join(v.to_bytes(2,"little") for v in mapping)).hexdigest();assert digest=="087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270"
 need=[{mapping[8*q+l]//8 for l in range(8)} for q in range(54)];intersections=[sorted(need[q]&need[q+1]) for q in range(0,54,2)];assert all(not x for x in intersections)
 # In any input order, completion(q)=max(position(i) for i in need[q]).
 # Equal completion steps require the same input i to be the maximum of both
 # neighborhoods.  Disjoint neighborhoods therefore make co-completion
 # impossible for all 27 protocol pairs, independently of scheduling.
 print(json.dumps({"gate":"D1-P3B22","map_sha256":digest,"adjacent_pairs":27,"pair_neighborhood_intersections":intersections,"co_complete_pairs_under_any_single_input_step_order":0,"input_once_immediate_pack16":"impossible","alternatives":["retain_completed_partner","reread_input","coefficient_or_byte_scratch"],"fixed_contract_result":"rejected"},indent=2))
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Audit route9-pair plus byte-packing under the no-scratch/input-once ABI."""
from __future__ import annotations
import importlib.util,json,subprocess
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=Path(subprocess.check_output(["git","rev-parse","--show-toplevel"],text=True).strip())
P3A=HERE.parent/"gt_fr0_d1_byte_abi_architecture/analyze_architecture.py"
def main()->None:
 spec=importlib.util.spec_from_file_location("p3a",P3A);assert spec and spec.loader
 p3a=importlib.util.module_from_spec(spec);spec.loader.exec_module(p3a)
 # One stock shuffle2 block consumes six vectors in this fixed order.
 labels=[[(stream,lane) for lane in range(8)] for stream in range(6)]
 flat=[labels[i][lane] for i in range(6) for lane in range(8)]
 routed=[flat[i] for i in p3a.shuffle2_block(0)]
 pairs=[(routed[i],routed[i+1]) for i in range(0,48,2)]
 classes=Counter((a[0],b[0]) for a,b in pairs)
 assert classes==Counter({(0,1):8,(2,3):8,(4,5):8})
 assert all(a[1]==b[1] for a,b in pairs)
 assert all({routed[i][0]//2 for i in range(8*q,8*q+8)}=={0,1,2}
            for q in range(6))
 official,_=p3a.official_map(ROOT);components=p3a.graph_components(official)
 assert [c["official_groups"] for c in components]==[list(range(0,18,2)),list(range(1,18,2))]
 # A route9 stream fans out to one vector in each of nine 48-coefficient blocks.
 blocks=9;streams=6;route_inputs=9
 held_after_streams=[blocks*k for k in range(1,streams+1)]
 # One completed stream pair is 9*16 twelve-bit coefficients = 216 bytes.
 # Even ideal dense register storage needs 14 vectors; two pairs need 27.
 packed_pair_bytes=blocks*16*12//8
 dense_one_pair=(packed_pair_bytes+15)//16
 dense_two_pairs=(2*packed_pair_bytes+15)//16
 assert held_after_streams==[9,18,27,36,45,54]
 assert (packed_pair_bytes,dense_one_pair,dense_two_pairs)==(216,14,27)
 assert dense_two_pairs+route_inputs>32
 # Output-at-a-time avoids the fanout only by rereading every stream's nine
 # inputs for every one of the nine outputs.
 input_once_loads=streams*route_inputs
 output_at_a_time_loads=blocks*streams*route_inputs
 assert (input_once_loads,output_at_a_time_loads)==(54,486)
 print(json.dumps({"gate":"D1-P3B16","shuffle2_pair_classes":{f"{a}-{b}":n for (a,b),n in sorted(classes.items())},"every_serialized_q_needs_all_three_pair_classes":True,"route9_blocks":blocks,"route9_streams":streams,"held_vectors_after_complete_streams":held_after_streams,"packed_bytes_per_completed_stream_pair":packed_pair_bytes,"ideal_dense_vectors_one_pair":dense_one_pair,"ideal_dense_vectors_two_pairs":dense_two_pairs,"minimum_next_route_input_vectors":route_inputs,"architectural_vector_registers":32,"input_once_q_loads_per_top":input_once_loads,"output_at_a_time_q_loads_per_top":output_at_a_time_loads,"extra_q_loads_if_recomputed":output_at_a_time_loads-input_once_loads,"no_scratch_macro_DAG_gate":"rejected","scope":"complete-route9 primitive plus existing exact byte order","optimality_claim":False},indent=2,sort_keys=True))
if __name__=="__main__":main()

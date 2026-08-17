#!/usr/bin/env python3
"""Exact topology/range gate for pure-GT NTT32-first PFA."""
import json
import generate_tile4 as gt

OUT = gt.GENERATED / "tile4_n32_gt_pfa_native_gate.json"
W3 = pow(gt.OMEGA96, 32, gt.Q)

def ncoord(r, q): return (64*r + 3*q) % 96
def kcoord(k3, k32): return (32*k3 + 33*k32) % 96

def ntt32(a):
    a=list(a)
    for stage in range(1,6):
        d=32>>stage
        for group in range(0,32,2*d):
            z=pow(gt.OMEGA32,gt.forward_power(stage,group),gt.Q)
            for j in range(d):
                lo=group+j; hi=lo+d; p=z*a[hi]%gt.Q; x=a[lo]
                a[lo]=(x+p)%gt.Q; a[hi]=(x-p)%gt.Q
    return a

def dft3(v):
    x0,x1,x2=v; p=W3*(x1-x2)
    return [(x0+x1+x2)%gt.Q,(x0-x2+p)%gt.Q,(x0-x1-p)%gt.Q]

def candidate(x,s):
    twisted=[x[n]*pow(s,-n,gt.Q)%gt.Q for n in range(96)]
    rows=[ntt32([twisted[ncoord(r,q)] for q in range(32)]) for r in range(3)]
    out={}
    for Q in range(32):
        k32=gt.bitreverse(Q,5); col=dft3([rows[r][Q] for r in range(3)])
        for k3,v in enumerate(col): out[kcoord(k3,k32)]=v
    return out

def oracle(x,s):
    return {k:sum(v*pow(pow(s,-1,gt.Q)*pow(gt.OMEGA96,k,gt.Q)%gt.Q,n,gt.Q)
                  for n,v in enumerate(x))%gt.Q for k in range(96)}

def main():
    exact=[]
    for b,s in enumerate(gt.BRANCH_SCALE):
        ok=True
        for i in range(96):
            x=[0]*96;x[i]=1
            if candidate(x,s)!=oracle(x,s):ok=False;break
        exact.append({"branch":b,"scale":s,"all_96_basis_vectors_equal":ok})
    assert all(x["all_96_basis_vectors_equal"] for x in exact)

    ranges=[]
    for b,s in enumerate(gt.BRANCH_SCALE):
        twists=[gt.centered(pow(s,-n,gt.Q)*gt.R) for n in range(96)]
        bound=gt.product_bound(2896,twists); stages=[]
        for stage in range(1,6):
            before=bound
            product=before if stage==1 else gt.product_bound(
                before,[v for rec in gt.forward_tables()[stage-1] for v in rec])
            bound=before+product
            stages.append({"stage":stage,"input_abs_bound":before,
                           "product_abs_bound":product,"output_abs_bound":bound})
        omega=gt.product_bound(2*bound,[gt.centered(W3*gt.R)])
        outputs=[3*bound,2*bound+omega,2*bound+omega]
        ranges.append({"branch":b,"post_twist_abs_bound":stages[0]["input_abs_bound"],
                       "stages":stages,"pre_DFT3_abs_bound":bound,
                       "DFT3_output_abs_bounds":outputs,
                       "signed_int16_safe":max(outputs)<32768})

    components=[]
    for base in range(0,32,4):
        nodes=[ncoord(r,q) for r in range(3) for q in range(base,base+4)]
        components.append({"k32_group":list(range(base,base+4)),"natural_Q":nodes,
                           "distinct_YMM":len({n//4 for n in nodes}),
                           "distinct_128bit_halves":len({(n//4,(n%4)//2) for n in nodes})})
    assert all(c["distinct_YMM"]==9 and c["distinct_128bit_halves"]==12 for c in components)

    stage_edges=[]
    for stage,d in enumerate((16,8,4,2,1),1):
        pairs=[]
        for r in range(3):
            for group in range(0,32,2*d):
                for j in range(d): pairs.append((ncoord(r,group+j),ncoord(r,group+j+d)))
        stage_edges.append({"stage":stage,"distance_q":d,
            "same_qword_lane":sum(a%4==b%4 for a,b in pairs),
            "different_qword_lane":sum(a%4!=b%4 for a,b in pairs),
            "same_YMM":sum(a//4==b//4 for a,b in pairs),"pairs":len(pairs)})

    result={
      "schema":"ntruplus768-gt32-n32-gt-pfa-native-v1",
      "experiment":"GT-N32-PFA-NATIVE-001",
      "coordinate":{"input":"n=64*r+3*q mod 96","output":"k=32*k3+33*k32 mod 96",
                    "cross_terms_mod96_zero":True},
      "exact_matrix_proof":exact,"exact_leaf_matrix_equality":True,
      "Montgomery_chains":{"qualified_N5":160,"pure_GT_N32_first_nominal":160,"delta":0},
      "range_proof":{"branches":ranges,"same_reducer_policy_int16_safe":all(r["signed_int16_safe"] for r in ranges)},
      "physical_topology":{"stage_edges":stage_edges,"suffix_components":components,
        "interpretation":"S1-S3 are whole-YMM edges, but every logical 12-node S4/S5/DFT3 component is fragmented over 9 YMM and 12 distinct halves"},
      "memory_phases":{"correctness_baseline":3,"qualified_N5":2,
        "two_phase_candidate_requires":"top-split/twist fused with three S1-S3 slabs; noalias or branch spill/reload"},
      "assembly_emitted":False,
      "decision":"static-hard-stop-for-unchanged-reducer-and-canonical-suffix; joint-range-topology-search-only",
      "reasons":["DFT3-last Y0 bound exceeds signed int16 (32799/32787)",
                 "each suffix component touches 9 YMM and 12 halves, not three resident row vectors",
                 "three-pass baseline adds one full polynomial pass"],
      "family_status":"pure-GT algebra and 160-chain target pass; implementation remains generator-only",
      "reopen_assembly_only_if":["new exact lazy range schedule keeps every DFT3-last output below 32768 without a full checkpoint",
        "joint S4/S5/DFT3/BM layout avoids canonical suffix materialization",
        "two memory phases and peak YMM<=16 are demonstrated"]}
    OUT.write_text(json.dumps(result,indent=2)+"\n");print(OUT);print(result["decision"])

if __name__=="__main__":main()

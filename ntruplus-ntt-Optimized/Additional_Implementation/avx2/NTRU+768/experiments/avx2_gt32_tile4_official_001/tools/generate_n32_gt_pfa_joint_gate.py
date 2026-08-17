#!/usr/bin/env python3
"""Joint coordinate/stage-order/range gate for pure-GT NTT32-first."""
import json
import generate_tile4 as gt

OUT=gt.GENERATED/"tile4_n32_gt_pfa_joint_gate.json"

def ncoord(A,u,r,q): return (A*r+3*u*q)%96

def main():
    coords=[]
    for A in (32,64):
        for u in range(1,32,2):
            comps=[]
            for base in range(0,32,4):
                ns=[ncoord(A,u,r,q) for r in range(3) for q in range(base,base+4)]
                comps.append({"base":base,"YMM":len({n//4 for n in ns}),
                              "halves":len({(n//4,(n%4)//2) for n in ns})})
            early=[]
            for d in (16,8,4):
                pairs=[(ncoord(A,u,r,g+j),ncoord(A,u,r,g+j+d))
                       for r in range(3) for g in range(0,32,2*d) for j in range(d)]
                early.append({"distance":d,"same_lane":sum(a%4==b%4 for a,b in pairs)})
            coords.append({"A":A,"u":u,"B":3*u,"components":comps,
                           "total_distinct_YMM":sum(c["YMM"] for c in comps),
                           "total_distinct_halves":sum(c["halves"] for c in comps),
                           "S1_S3_all_same_lane":all(x["same_lane"]==48 for x in early)})
    best=min(coords,key=lambda x:(x["total_distinct_YMM"],x["total_distinct_halves"]))
    assert best["u"]==11 and best["total_distinct_YMM"]==24 and best["total_distinct_halves"]==48

    tables=gt.forward_tables(); schedules=[]
    for insertion in (3,4,5):
        branches=[]
        for s in gt.BRANCH_SCALE:
            b=gt.product_bound(2896,[gt.centered(pow(s,-n,gt.Q)*gt.R) for n in range(96)])
            for stage in range(1,insertion+1):
                p=b if stage==1 else gt.product_bound(b,[v for rec in tables[stage-1] for v in rec]); b+=p
            omega=gt.product_bound(2*b,[-886]); dft=[3*b,2*b+omega,2*b+omega]
            final=max(dft); safe=final<32768
            for stage in range(insertion+1,6):
                final+=gt.product_bound(final,[v for rec in tables[stage-1] for v in rec]); safe &= final<32768
            branches.append({"pre_DFT3":b,"DFT3_outputs":dft,"final_abs_bound":final,"safe":safe})
        schedules.append({"order":f"S1-S{insertion}-D3-S{insertion+1}-S5" if insertion<5 else "S1-S5-D3",
                          "DFT3_after_stage":insertion,"branches":branches,
                          "all_int16_safe":all(x["safe"] for x in branches)})

    result={"schema":"ntruplus768-gt32-n32-pfa-joint-v1","experiment":"GT-N32-PFA-JOINT-002",
      "search":{"PFA_coordinates":32,"A":[32,64],"u":"all 16 odd units mod32",
                "DFT3_insertions_after":[3,4,5],"Montgomery_chain_limit":160},
      "coordinate_candidates":coords,"best_coordinate":{"A":best["A"],"B":best["B"],"u":best["u"],
        "component_YMM":[c["YMM"] for c in best["components"]],
        "component_halves":[c["halves"] for c in best["components"]],
        "identity":"same physical geometry as current n=64*r+33*q GT mapping"},
      "stage_order_range":schedules,
      "findings":{"S3_D3_safe":schedules[0]["all_int16_safe"],"S4_D3_safe":schedules[1]["all_int16_safe"],
        "S5_D3_safe":schedules[2]["all_int16_safe"],"best_coordinate_retains_160_chains":True,
        "best_coordinate_requires_current_GT_BLEND_geometry":True,
        "deleted_GT_BLEND_instructions":0,
        "memory_phase_baseline":3},
      "assembly_emitted":False,
      "decision":"range-and-coordinate-pass-no-static-acceleration-mechanism",
      "conclusion":"Moving DFT3 after S3 or S4 repairs range, and u=11 repairs suffix locality, but u=11 is the current GT_BLEND3 geometry. The 96 blends are moved rather than deleted, while the naive schedule still adds a polynomial phase.",
      "reopen_assembly_only_if":["joint DFT3/S4 or DFT3/S5 network consumes the three natural vectors with fewer than six blends per branch/block",
        "top-split/twist/S1-S3 two-phase schedule proves peak YMM<=16 and repays branch temporary traffic",
        "BM landing removes a complete current terminal conversion"]}
    OUT.write_text(json.dumps(result,indent=2)+"\n");print(OUT);print(result["decision"])
if __name__=="__main__":main()

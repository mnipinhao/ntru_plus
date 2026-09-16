#!/usr/bin/env python3
"""Reproduce the exact-class DP certificate for the peak-26 schedule."""
from __future__ import annotations
import importlib.util,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=Path(subprocess.check_output(["git","rev-parse","--show-toplevel"],text=True).strip());P3A=HERE.parent/"gt_fr0_d1_byte_abi_architecture/analyze_architecture.py"
EXPECTED=[0,1,2,27,28,29,6,7,8,33,12,13,14,39,40,41,20,45,46,47,24,25,26,51,52,53,15,16,17,42,43,44,3,4,5,30,31,32,9,10,11,36,18,19,34,35,21,22,23,48,49,50,37,38]
def main()->None:
 spec=importlib.util.spec_from_file_location("p3a",P3A);assert spec and spec.loader;p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
 official,_=p.official_map(ROOT);shuffle2=[v for s in range(0,864,48) for v in p.shuffle2_block(s)];forward=[official[shuffle2[i]] for i in range(432)];need=[set() for _ in range(54)]
 for oq in range(54):
  for lane in range(8):need[oq].add(forward[8*oq+lane]//8)
 signatures={i:tuple(q for q in range(54) if i in need[q]) for i in range(54)};classes=[]
 for sig in dict.fromkeys(signatures.values()):classes.append([i for i in range(54) if signatures[i]==sig])
 assert len(classes)==15;full=(1<<len(classes))-1;dp=[99]*(full+1);prev=[None]*(full+1);dp[0]=0
 for mask in range(full+1):
  if dp[mask]==99:continue
  done={x for j,c in enumerate(classes) if mask>>j&1 for x in c}
  for j,c in enumerate(classes):
   if mask>>j&1:continue
   started=done|set(c);live=sum(bool(n&started) and not (n<=done and need[q^1]<=done) for q,n in enumerate(need));nm=mask|1<<j;cost=max(dp[mask],live)
   if cost<dp[nm]:dp[nm]=cost;prev[nm]=(mask,j)
 order=[];m=full
 while m:old,j=prev[m];order.append(classes[j]);m=old
 flat=[x for c in reversed(order) for x in c];assert dp[full]==26 and flat==EXPECTED
 print(f"p3b21_exact_dp=pass classes={len(classes)} peak={dp[full]}");print("classes="+repr(classes));print("input_order="+repr(flat))
if __name__=="__main__":main()

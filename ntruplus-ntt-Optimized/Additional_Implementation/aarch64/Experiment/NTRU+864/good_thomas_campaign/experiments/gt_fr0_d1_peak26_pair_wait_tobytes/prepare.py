#!/usr/bin/env python3
"""Generate the exact-DP peak-26 pair-wait ToBytes candidate."""
from __future__ import annotations
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/"gt_fr0_d1_pair_wait_tobytes/prepare.py"
ORDER=[0,1,2,27,28,29,6,7,8,33,12,13,14,39,40,41,20,45,46,47,24,25,26,51,52,53,15,16,17,42,43,44,3,4,5,30,31,32,9,10,11,36,18,19,34,35,21,22,23,48,49,50,37,38]
def main()->None:
 spec=importlib.util.spec_from_file_location("p3b15",BASE);assert spec and spec.loader
 p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
 p.generate(ORDER,26,HERE/"build")
if __name__=="__main__":main()

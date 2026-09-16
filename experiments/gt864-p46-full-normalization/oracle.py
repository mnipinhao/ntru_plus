#!/usr/bin/env python3
"""Exact arithmetic and frozen-route oracle for P46."""
from __future__ import annotations
import re, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent; Q=3457

def main():
    lo,hi=32767,-32768
    for x in range(-32768,32768):
        t=(x*9+(1<<14))>>15
        r=x-t*Q; lo=min(lo,r);hi=max(hi,r)
        old=r+((-1 if r<0 else 0)&Q)
        bit=(r&0xffff)>>15
        new=((r+bit*Q+32768)&0xffff)-32768
        assert new==old==x%Q
    assert (lo,hi)==(-3291,3291)
    subprocess.run(["python3",str(HERE.parent/"gt864-p23-tobytes-global-dag/oracle.py")],check=True)
    text="\n".join(x.split("//",1)[0] for x in (HERE/"candidate-full.phys.S").read_text().splitlines())
    assert len(re.findall(r"\bushr\b[^\n]*#15",text))==54
    assert len(re.findall(r"\bmla\b",text))==54
    assert len(re.findall(r"\bsshr\b[^\n]*#15",text))==0
    assert len(re.findall(r"\band\b",text))==0
    print(f"P46 oracle passed: all signed int16 inputs, residual [{lo},{hi}], frozen P24 route bytes")
if __name__=="__main__":main()

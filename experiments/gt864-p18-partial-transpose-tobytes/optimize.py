#!/usr/bin/env python3
"""Fixed-register timing-only Slothy scheduling for P18 class windows."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
from collections import Counter
from pathlib import Path

from slothy import Slothy
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE=Path(__file__).resolve().parent
BUILD=HERE/"build"

def between(path,start,end):
    out=[]; inside=False
    for raw in path.read_text().splitlines():
        code=raw.split("//",1)[0].strip()
        if code==start+":": inside=True; continue
        if code==end+":": break
        if inside and code and not code.startswith(".") and not code.endswith(":"): out.append(code)
    return out

def canonical(text):
    parsed=Arch.Instruction.parser(SourceLine(text))
    if len(parsed)!=1: raise RuntimeError(text)
    return parsed[0].write().lower()

def outputs(path,start,end):
    out=set()
    for text in between(path,start,end):
        parsed=Arch.Instruction.parser(SourceLine(text))[0]
        out.update(parsed.args_out); out.update(parsed.args_in_out)
    return out

def run_mode(mode):
    source=BUILD/f"p18_tobytes_{mode}.S"
    model_source=BUILD/f"p18_tobytes_{mode}.model.S"
    model_output=BUILD/f"p18_tobytes_{mode}.model.opt.S"
    output=BUILD/f"p18_tobytes_{mode}.opt.S"
    # The selected Slothy checkout lacks STUR D/W parser variants. STR with
    # the same base, immediate, width and source is used only as the scheduling
    # model; the actual emitted instruction is restored byte-for-byte to STUR.
    model_source.write_text(source.read_text().replace(" stur d", " str d")
                            .replace(" stur w", " str w"))
    logger=logging.getLogger("p18-"+mode); logger.handlers.clear(); logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(BUILD/f"slothy-{mode}.log",mode="w"))
    slothy=Slothy(Arch,Target,logger=logger)
    slothy.config.selftest=False
    slothy.config.inputs_are_outputs=True
    slothy.config.constraints.allow_spills=False
    slothy.config.constraints.allow_reordering=True
    slothy.config.constraints.allow_renaming=False
    slothy.config.constraints.functional_only=False
    slothy.config.variable_size=True
    slothy.config.timeout=30
    slothy.config.reserved_regs=[f"x{i}" for i in range(10,31)]+["sp","xzr"]
    slothy.load_source_from_file(str(model_source))
    cycles=[]
    for index in range(15):
        start=f"p18_{mode}_class_{index}_start"; end=f"p18_{mode}_class_{index}_end"
        slothy.config.outputs=outputs(model_source,start,end)
        slothy.optimize(start=start,end=end)
    slothy.write_source_to_file(str(model_output))
    output.write_text(model_output.read_text().replace("str d", "stur d")
                      .replace("str w", "stur w"))
    before=[]; after=[]
    for index in range(15):
        start=f"p18_{mode}_class_{index}_start"; end=f"p18_{mode}_class_{index}_end"
        a=between(model_source,start,end); b=between(model_output,start,end)
        assert Counter(map(canonical,a))==Counter(map(canonical,b))
        before+=a; after+=b
    cycles=[int(x) for x in re.findall(r"Expected cycles:\s*(\d+)",output.read_text())]
    assert len(cycles)==15
    return {"mode":mode,"windows":15,"instructions":len(after),
            "instruction_multiset_preserved":True,"allow_renaming":False,
            "allow_spills":False,"model_cycles":sum(cycles),"window_cycles":cycles,
            "store_model_surrogate":"STUR D/W modeled as same-address STR D/W; restored before assembly",
            "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "output_sha256":hashlib.sha256(output.read_bytes()).hexdigest()}

def main():
    if not Path(Arch.__file__).resolve().is_relative_to("/Users/chenpinhao/slothy"):
        raise RuntimeError(f"wrong Slothy checkout: {Arch.__file__}")
    result={"interpreter":sys.executable,"slothy":str(Path(__import__('slothy').__file__).resolve()),
            "arch":str(Path(Arch.__file__).resolve()),"target":str(Path(Target.__file__).resolve()),
            "modes":{mode:run_mode(mode) for mode in ("full","small")}}
    (HERE/"slothy-results.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()

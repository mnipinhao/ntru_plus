#!/usr/bin/env python3
"""Run P46 Full against frozen P24 production on Pi 5."""
from __future__ import annotations
import hashlib,importlib.util,json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
RUNNER=ROOT/"experiments/gt864-p23-tobytes-global-dag/run_pi5.py"
def load():
    spec=importlib.util.spec_from_file_location("p23_runner_for_p46",RUNNER);assert spec and spec.loader
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);return module
p23=load();p18=p23.p18;p15=p23.p15;p18.HERE=HERE;p15.HERE=HERE
p15.BUILD=HERE/"build";p15.SYNC=p15.BUILD/"sync";p15.RAW=p15.BUILD/"pi5"
p15.REMOTE="/home/pi/supercop-20260831/bench/pinhao/gt864-p46-20260916"
p18.EXPECTED_KAT="0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c"
p18.EXPECTED_MALFORMED="2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67"
def stage():
    if p15.SYNC.exists():shutil.rmtree(p15.SYNC)
    for name in ("baseline","candidate"):p15.extract(p15.SYNC/"packages"/name)
    candidate=p15.SYNC/"packages/candidate"
    text=(HERE/"candidate-full.g3.opt.S").read_text().replace("gt864_p46_tobytes_full_asm","gt864_p18_tobytes_full_asm")
    (candidate/"gt864_p18_tobytes_full.S").write_text(text)
    component=(ROOT/"experiments/gt864-native-asm/p6-zero-scratch-tobytes/p6e-pi-timing/bench.c").read_text().replace(
      'must_symbol(hc, small ? "gt864_p6d3_small_asm" : "gt864_p6d3_full_asm")',
      'must_symbol(hc, small ? "gt864_fr0_tobytes_small" : "gt864_fr0_tobytes_full")')
    (p15.SYNC/"component.c").write_text(component)
    harness=(ROOT/"experiments/gt864-official-profile-p8/full_harness.c").read_text()
    (p15.SYNC/"kem.c").write_text(harness.replace('v?"gt":"official"','v?"candidate":"baseline"'))
    shutil.copy2(ROOT/"experiments/gt864-native-asm/kem-malformed-transcript.c",p15.SYNC/"malformed.c")
    manifest={str(p.relative_to(p15.SYNC)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(p15.SYNC.rglob("*")) if p.is_file()}
    (p15.BUILD/"source-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
def audit():
    result={}
    for mode in ("full","small"):
      result[mode]={}
      for variant in ("baseline","candidate"):
        name=f"gt864_p18_tobytes_{mode}.o";d=p15.ssh(f"cd {p15.REMOTE}/packages/{variant} && objdump -d {name}")
        (p15.RAW/f"object-{variant}-{mode}.log").write_text(d)
        count=len(re.findall(r"(?m)^\s*[0-9a-f]+:\s+[0-9a-f]+\s+\S+",d));sp=len(re.findall(r"(?mi)^.*\b(?:ldr|str|ldp|stp)\s+q[^\n]*\[sp[^\n]*$",d))
        if sp:raise RuntimeError("vector spill")
        result[mode][variant]={"object_instructions":count,"q_stack_accesses":sp}
    return result
def main():
    p18.stage=stage;p18.target_audit=audit;p18.main();path=HERE/"pi-results.json";r=json.loads(path.read_text())
    r["experiment"]="GT864-P46-FULL-NORMALIZATION-20260916";r["candidate_scope"]="Full only; Small remains exact P24 production"
    r["slothy_results"]=["slothy-full-g3.json"];path.write_text(json.dumps(r,indent=2)+"\n")
if __name__=="__main__":main()

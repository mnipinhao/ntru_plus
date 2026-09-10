#!/usr/bin/env python3
"""Build and run the P4 differential oracle on the current AArch64 host."""

import json
import re
import subprocess
import tempfile
from pathlib import Path


P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

candidate = (P / "candidate-cluster.c").read_text()
baseline_region = (P / "baseline-region.c").read_text()
baseline = baseline_region.split("/* cluster_transpose_frombytes.c */\n", 1)[1].split(
    "\n/* byte_api.c checked wrapper */", 1
)[0]
assert len(re.findall(r"^x[0-5]=unpack8\(", candidate, re.M)) == 54
assert len(re.findall(r"^maximum=vmaxq_u16\(", candidate, re.M)) == 54
assert candidate.count("return vmaxvq_u16(maximum);") == 1
assert candidate.count("if (") == 0
assert candidate.count("vst1q_s16") == baseline.count("vst1q_s16") == 54
assert sorted(re.findall(r"vst1q_s16\(out\+(\d+)", candidate)) == sorted(re.findall(r"vst1q_s16\(out\+(\d+)", baseline))

with tempfile.TemporaryDirectory(prefix="gt864-p4-") as temporary:
    temporary = Path(temporary)
    baseline_source = temporary / "baseline-cluster.c"
    baseline_source.write_text(baseline)
    common = ["cc", "-O3", "-std=c11", "-march=armv8-a+simd", "-I", str(PROD)]
    subprocess.run(common + [
        "-Dgt864_fr0_cluster_transpose_frombytes=p4_baseline_decode",
        "-c", str(baseline_source), "-o", str(temporary / "baseline.o"),
    ], check=True)
    subprocess.run(common + [
        "-Dgt864_fr0_cluster_transpose_frombytes=p4_candidate_decode",
        "-Dgt864_fr0_cluster_transpose_frombytes_checked_raw=p4_candidate_checked",
        "-c", str(P / "candidate-cluster.c"), "-o", str(temporary / "candidate.o"),
    ], check=True)
    executable = temporary / "verify"
    subprocess.run(common + [
        str(P / "verify.c"), str(temporary / "baseline.o"), str(temporary / "candidate.o"), "-o", str(executable),
    ], check=True)
    output = subprocess.check_output([str(executable)], text=True).strip()

report = {
    "source_decode_vectors_per_half": 54,
    "fused_maxima_per_half": 54,
    "routing_store_offsets_preserved": True,
    "data_dependent_branches_in_candidate_source": 0,
    "oracle": output,
}
(P / "oracle-results.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))

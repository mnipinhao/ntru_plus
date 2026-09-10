#!/usr/bin/env python3
"""Generate the P4-A1 C candidate from the exact production sources."""

import hashlib
import json
import re
from pathlib import Path


P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

baseline_region = (P / "baseline-region.c").read_text()
cluster = baseline_region.split("/* cluster_transpose_frombytes.c */\n", 1)[1].split(
    "\n/* byte_api.c checked wrapper */", 1
)[0]
api = (P / "baseline-byte-api.c").read_text()
header = (P / "baseline-cluster.h").read_text()

old_signature = "__attribute__((noinline)) static void transpose_top(int16_t*out,const uint8_t*in){"
new_signature = "__attribute__((noinline)) static uint16_t transpose_top_checked(int16_t*out,const uint8_t*in){"
assert cluster.count(old_signature) == 1
cluster = cluster.replace(old_signature, new_signature)

declarations = "int16x8_t " + ",".join(f"o{i}" for i in range(16)) + ";"
assert cluster.count(declarations) == 1
cluster = cluster.replace(
    declarations,
    declarations + "\nuint16x8_t maximum=vdupq_n_u16(0);",
)

decode_pattern = re.compile(r"^(x[0-5])=unpack8\(([^;]+)\);$", re.M)
decode_count = 0


def add_maximum(match: re.Match[str]) -> str:
    global decode_count
    decode_count += 1
    register = match.group(1)
    return (
        match.group(0) + "\nmaximum=vmaxq_u16(maximum,"
        f"vreinterpretq_u16_s16({register}));"
    )


cluster = decode_pattern.sub(add_maximum, cluster)
assert decode_count == 54

old_public = "void gt864_fr0_cluster_transpose_frombytes(int16_t fr0[864],const uint8_t in[1296]){transpose_top(fr0,in);transpose_top(fr0+432,in+648);}"
new_public = """int gt864_fr0_cluster_transpose_frombytes_checked_raw(int16_t fr0[864],const uint8_t in[1296]){
 uint16_t maximum0=transpose_top_checked(fr0,in);
 uint16_t maximum1=transpose_top_checked(fr0+432,in+648);
 return (maximum0>=3457)|(maximum1>=3457);
}
void gt864_fr0_cluster_transpose_frombytes(int16_t fr0[864],const uint8_t in[1296]){
 (void)gt864_fr0_cluster_transpose_frombytes_checked_raw(fr0,in);
}"""
assert cluster.count("\n}\n" + old_public) == 1
cluster = cluster.replace("\n}\n" + old_public, "\nreturn vmaxvq_u16(maximum);\n}\n" + new_public)

old_checked = """int gt864_fr0_frombytes_checked(poly *out,const uint8_t *in)
{
    gt864_fr0_cluster_transpose_frombytes(out->coeffs,in);
    /* All unpacked lanes are unsigned 12-bit values. The permutation does not
     * affect the predicate; scan every lane, with no data-dependent early exit. */
    uint16x8_t maximum=vdupq_n_u16(0);
    for (size_t i=0;i<NTRUPLUS_N;i+=8)
        maximum=vmaxq_u16(maximum,vreinterpretq_u16_s16(vld1q_s16(out->coeffs+i)));
    return vmaxvq_u16(maximum)>=NTRUPLUS_Q;
}"""
new_checked = """int gt864_fr0_frombytes_checked(poly *out,const uint8_t *in)
{
    return gt864_fr0_cluster_transpose_frombytes_checked_raw(out->coeffs,in);
}"""
assert api.count(old_checked) == 1
api = api.replace(old_checked, new_checked)

prototype = "int gt864_fr0_cluster_transpose_frombytes_checked_raw(int16_t fr0[864],const uint8_t in[1296]);\n"
assert prototype not in header
header = header.replace("void gt864_fr0_cluster_transpose_frombytes", prototype + "void gt864_fr0_cluster_transpose_frombytes")

(P / "candidate-cluster.c").write_text(cluster)
(P / "candidate-byte-api.c").write_text(api)
(P / "candidate-cluster.h").write_text(header)
report = {
    "decoded_vectors_in_source": decode_count,
    "decoded_vectors_per_checked_call": 2 * decode_count,
    "fused_vector_maxima_per_checked_call": 2 * decode_count,
    "horizontal_maxima_per_checked_call": 2,
    "removed_output_vector_loads": 108,
    "removed_second_scan_vector_maxima": 108,
    "input_load_change": 0,
    "routing_store_change": 0,
    "candidate_cluster_sha256": hashlib.sha256(cluster.encode()).hexdigest(),
    "candidate_byte_api_sha256": hashlib.sha256(api.encode()).hexdigest(),
    "candidate_header_sha256": hashlib.sha256(header.encode()).hexdigest(),
}
(P / "generation-report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))

#!/usr/bin/env python3
"""Audit the immutable exact production C boundary captured before P4."""

import hashlib
import json
from pathlib import Path


P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

cluster_path = PROD / "cluster_transpose_frombytes.c"
api_path = PROD / "byte_api.c"
region = (P / "baseline-region.c").read_text()
cluster = region.split("/* cluster_transpose_frombytes.c */\n", 1)[1].split(
    "\n/* byte_api.c checked wrapper */", 1
)[0]
baseline_api_path = P / "baseline-byte-api.c"
baseline_header_path = P / "baseline-cluster.h"
assert hashlib.sha256(cluster.encode()).hexdigest() == "0c73eac4bc9a9f37ef75fe6d3981d7e6aa2c4aa720ca903ad054f1773ff04dc2"
assert hashlib.sha256(baseline_api_path.read_bytes()).hexdigest() == "2e210c26aabdfd4dd9ed5a90da8ef6eb88d9bb4108cba5b8c0f61a794b1d4aa9"
assert hashlib.sha256(baseline_header_path.read_bytes()).hexdigest() == "58220354ffce4746c8126c5e054931191c2b1ef196160ed8d485d0e5bf18e3a4"
assert hashlib.sha256(region.encode()).hexdigest() == "39844aeacc1ab830b7c33513be67be18b6200757665138418f620c1141240889"
report = {
    "cluster_source": str(cluster_path),
    "cluster_sha256": hashlib.sha256(cluster.encode()).hexdigest(),
    "byte_api_source": str(api_path),
    "byte_api_sha256": hashlib.sha256(baseline_api_path.read_bytes()).hexdigest(),
    "baseline_region_sha256": hashlib.sha256(region.encode()).hexdigest(),
    "current_production_cluster_sha256": hashlib.sha256(cluster_path.read_bytes()).hexdigest(),
    "current_production_byte_api_sha256": hashlib.sha256(api_path.read_bytes()).hexdigest(),
    "decoded_vectors_per_call": cluster.count("=unpack8(" ) * 2,
    "coefficients_per_vector": 8,
    "routing_vector_stores_per_call": cluster.count("vst1q_s16") * 2,
    "second_scan_vector_loads": 108,
    "second_scan_vector_maxima": 108,
    "input_bytes": 1296,
    "output_bytes": 1728,
}
assert report["decoded_vectors_per_call"] == 108
assert report["routing_vector_stores_per_call"] == 108
(P / "baseline-audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))

#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEM = (ROOT / "src/kem.c").read_text()
GENERATOR = (ROOT / "tools/generate_f0_ma2_kem.py").read_text()
RESULT = (ROOT / "results/gt9x16-prod3-h1-integration-20260827-001/kat.json")

for text in (KEM, GENERATOR):
    assert text.count("ntruplus1152_exp001_prod3_ma2_hash_h1") == 1
    assert "ntruplus1152_exp001_prod3_hash_bytes(ct" not in text
    assert "f0_prod3_hash_bridge.h" not in text

assert KEM.count("ntruplus1152_exp001_gt9x16_prod3_aos_full") == 2
assert KEM.count("ntruplus1152_exp001_f0_ma2_native_full") == 1
assert "poly_cbd1(&r, buf + NTRUPLUS_SYMBYTES);" in KEM
assert "hash_g(ct, ct);" in KEM
assert "poly_sotp_encode(&m, msg, ct);" in KEM

kat = json.loads(RESULT.read_text())
assert kat["schema"] == "ntruplus-prod3-h1-kat-evidence/v1"
assert kat["implementation"] == "avx2-gt9x16-prod3-h1-exp001"
assert kat["cases"] == 100
assert kat["passed"] is True
assert kat["native_performance_run"] is False
assert kat["request_sha256"] == kat["frozen_request_sha256"] == (
    "36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa")
assert kat["response_sha256"] == kat["frozen_response_sha256"] == (
    "2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3")
print("PROD3 H1 integration: frozen caller shape and 100-vector KAT passed")

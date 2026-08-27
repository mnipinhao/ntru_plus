#!/usr/bin/env python3
"""Regression gates for H1 control and H2/H3 ingress co-design."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
h1 = json.loads((ROOT / "generated/encap-h-decode-natural-q-asm.json").read_text())
audit = json.loads((ROOT / "generated/encap-h-decode-natural-q-asm-audit.json").read_text())
design = json.loads((ROOT / "generated/encap-h-ingress-ma2-codesign-v1.json").read_text())

assert h1["role"] == "conservative H1 control, not the target ingress architecture"
assert h1["decoder"]["pk_loads"] == 54
assert h1["decoder"]["natural_stores"] == 72
assert h1["consumer"]["removed_h_projection_loads"] == 72
assert audit["gates"] == {
    "call_free": True,
    "entries_aligned_32": True,
    "frame_free": True,
    "same_ma2_arithmetic": True,
    "spill_free": True,
    "vzeroupper_free": True,
}
delta = audit["consumer_delta"]
assert delta["vmovdqa"] == -72
assert delta["vperm2i128"] == -144
assert delta["vpshufb"] == -144
assert delta["vpor"] == -72

h3 = design["architectures"]["H3-streaming-decode-ma2"]
assert h3["resident_h_bytes"] == 0
assert h3["h_stores"] == h3["h_reloads"] == 0
assert len(h3["blocks"]) == 9
assert all(len(block["ma2_tiles"]) == 2 for block in h3["blocks"])
assert design["caller_legality"]["late_validation_external_result_can_match"]
assert design["caller_legality"]["randombytes_before_derand"]
assert design["wavefront"]["block_local_vectors"] == 72
assert design["wavefront"]["cross_block_vectors"] == 0
assert design["wavefront"]["naive_live_bound"]["total"] == 18
assert not design["wavefront"]["naive_live_bound"]["fits_16_ymm"]
assert design["wavefront"]["candidate_accumulator_wavefront_bound"]["total"] == 16
assert design["wavefront"]["candidate_accumulator_wavefront_bound"]["fits_16_ymm"]
assert design["decision"]["H3"].startswith("preferred architecture")
assert not design["decision"]["benchmark"]

print("H ingress/MA2 co-design: H1 control closed; H3 caller/block/register map passed")

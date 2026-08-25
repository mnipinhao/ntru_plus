#!/usr/bin/env python3
"""Gate the exact F0-to-encapsulation MulAdd semantic map."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated/f0-ma-consumer-map.json").read_text())

assert data["schema"] == "gt-f0-ma-consumer-map/v1"
assert data["checkpoint"] == "F0-MA-MAP"
audit = data["caller_audit"]
assert audit["caller"] == "crypto_kem_enc_derand"
assert audit["contains_inverse_transform"] is False
assert audit["downstream"] == "poly_tobytes(ct,c)"
assert audit["actual_provenance"] == {
    "h": "resident public-key NTT operand from poly_frombytes(pk)",
    "r": "fresh poly_cbd1 then F0 forward candidate",
    "m": "fresh poly_sotp_encode/poly_cbd1 then F0 forward candidate",
}
assert audit["pinned_implementation_sequence"] == [
    "poly_frombytes(&h, pk)", "poly_ntt(&r)", "poly_ntt(&m)",
    "poly_basemul(&c, &h, &r)", "poly_add(&c, &c, &m)",
    "poly_tobytes(ct, &c)",
]

relabel = data["row_relabel_proof"]
assert relabel["early_pipeline_layout_p_order"] == [0, 3, 6, 1, 4, 7, 2, 5, 8]
assert relabel["actual_f0_paper_p_order"] == [0, 3, 6, 1, 4, 7, 8, 2, 5]
assert relabel["changed_physical_rows"] == [6, 7, 8]

vectors = data["f0_vectors"]
assert len(vectors) == 72
assert [vector["vector_index"] for vector in vectors] == list(range(72))
owners = set()
f0_positions = set()
official_positions = set()
for vector in vectors:
    assert len(vector["lanes"]) == 16
    assert vector["scale"] == {"transform": 4, "montgomery_r_exponent": 0}
    for lane in vector["lanes"]:
        owner = lane["semantic_owner"]
        assert owner["branch"] == vector["branch"]
        assert owner["p"] == vector["semantic_p"]
        assert 0 <= owner["q"] < 16
        assert 0 <= owner["terminal_coefficient"] < 4
        assert len(lane["exact_f0_range_i16"]) == 2
        assert -32768 <= lane["exact_f0_range_i16"][0]
        assert lane["exact_f0_range_i16"][1] <= 32767
        owners.add(tuple(owner[key] for key in
                         ("branch", "p", "q", "terminal_coefficient")))
        f0_positions.add(lane["f0_position_i16"])
        official_positions.add(lane["official_position_i16"])

assert len(owners) == 1152
assert f0_positions == set(range(1152))
assert official_positions == set(range(1152))
assert data["bijection_proof"]["all_equal_1152"] is True

last = {(v["physical_p_row"], v["semantic_p"])
        for v in vectors if v["branch"] == 0 and v["physical_p_row"] >= 6}
assert last == {(6, 8), (7, 2), (8, 5)}
assert data["decision"]["assembly_authorized"] is False
assert data["decision"]["benchmark_authorized"] is False

print("F0-MA map: exact caller, row relabel, and 1,152-cell ownership bijections passed")

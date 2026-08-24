#!/usr/bin/env python3
"""Gate the exact C2 inverse16 to inverse-NTT9 consumer map."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads(
    (ROOT / "generated/g1c-inverse-tail-consumer-map.json").read_text())

assert data["semantic_contract"]["coordinate"] == "(b,p,t,j)"
assert data["semantic_contract"]["physical_p_order"] == [
    0, 3, 6, 1, 4, 7, 8, 2, 5]
assert data["semantic_contract"]["natural_p_reorder"] is False
assert data["producer_proof"]["C2_external_state"].endswith(
    "not persistent S/D")
assert data["producer_proof"]["linear_basis_component_checks"] == 2304
assert data["producer_proof"]["maximum_absolute_output"] == 17377
assert data["consumer_proof"]["linear_basis_checks"] == 81
assert data["consumer_proof"]["native_radix3_triads"] == [
    [0, 3, 6], [1, 4, 7], [8, 2, 5]]

for name, parameter, degree, vectors in (
        ("1152", 1152, 4, 72),
        ("864_projection", 864, 3, 54)):
    instance = data["instances"][name]
    assert instance["parameter"] == parameter
    assert instance["terminal_degree"] == degree
    assert instance["vectors"] == vectors
    assert instance["cells"] == parameter
    owners = instance["vector_owners"]
    assert len(owners) == vectors
    assert [owner["vector_index"] for owner in owners] == list(range(vectors))
    assert len(instance["consumer_invocations"]) == 2 * degree
    seen = set()
    for invocation in instance["consumer_invocations"]:
        assert invocation["physical_p_order"] == [0, 3, 6, 1, 4, 7, 8, 2, 5]
        assert len(invocation["operands"]) == 9
        for operand in invocation["operands"]:
            assert len(operand["lane_semantics"]) == 16
            for lane in operand["lane_semantics"]:
                b, p, t, j = lane["semantic"]
                assert b == invocation["branch"]
                assert p == operand["mathematical_p"]
                assert t == lane["lane"]
                assert j == invocation["terminal_j"]
                seen.add((b, p, t, j))
    assert len(seen) == parameter

direct = data["realizations"]["B_current_C2_direct_loads"]
assert direct["extra_producer_moves"] == 0
assert direct["extra_lane_routes"] == 0
assert data["realizations"]["C_redeposit_iNTT9_grouping"]["status"] == \
    "equivalent-to-B-no-separate-probe"
assert data["movement_decision"]["full_array_repack_default"] is False
assert data["movement_decision"]["inverse_NTT9_ASM_authorized"] is False
assert data["shared_boundary"]["864_warning"].endswith(
    "remain intentionally unclaimed")

print("G1C inverse tail: 1152/864 ownership bijections, 2304 inverse16 and 81 inverse9 basis checks passed")

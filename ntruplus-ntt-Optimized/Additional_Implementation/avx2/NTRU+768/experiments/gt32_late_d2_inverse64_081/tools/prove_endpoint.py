#!/usr/bin/env python3
"""Prove the sign×Q inverse64 endpoint for all six GT32 tiles."""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

Q = 3457
G = 7
BASE_W64 = pow(G, (Q - 1) // 64, Q)
# Current GT32 NTT32 uses omega96^3 = BASE_W64^(2*21), not BASE_W64^2.
# Select the compatible square root so inverse64 shares the production axis.
W64 = pow(BASE_W64, 21, Q)
OMEGA32_CURRENT = pow(675, 3, Q)
assert W64 * W64 % Q == OMEGA32_CURRENT
ROOT = Path(__file__).resolve().parents[1]
PROOF080 = ROOT.parent / "gt32_late_d2_twist_absorption_080/generated/late_d2_twist_absorption.json"
LAMBDA_INC = ROOT.parent / "avx2_gt32_tile4_official_001/generated/tile4_basemul_constants.inc"
OUT = ROOT / "generated/inverse64_endpoint.json"

# Exact physical order consumed by the selected current inverse32.  This is
# the impulse response of I0..I4, not the canonical discrete-log coordinate
# used by gate 080 to prove that the lambda values form an orbit.
PHYSICAL_TO_INVERSE32 = [
     0,  4,  2,  6, 16, 20, 18, 22,  8, 12, 10, 14, 24, 28, 26, 30,
     1,  5,  3,  7, 17, 21, 19, 23,  9, 13, 11, 15, 25, 29, 27, 31,
]


def dft(values: list[int], root: int) -> list[int]:
    n = len(values)
    return [sum(value * pow(root, k * j, Q) for j, value in enumerate(values)) % Q
            for k in range(n)]


def idft(values: list[int], root: int) -> list[int]:
    n = len(values)
    ninv = pow(n, -1, Q)
    return [ninv * sum(value * pow(root, -k * j, Q)
                       for k, value in enumerate(values)) % Q
            for j in range(n)]


proof080 = json.loads(PROOF080.read_text())
lambda_text = LAMBDA_INC.read_text().split(".Ltile4_bm_lambda:", 1)[1] \
    .split(".Ltile4_bm_lambda_qinv:", 1)[0]
lambda_mont = [int(token) % Q for line in lambda_text.splitlines()
               if ".short" in line
               for token in re.findall(r"[-+]?\d+", line.split(".short", 1)[1])]
rinv = pow((1 << 16) % Q, -1, Q)
lambdas = [value * rinv % Q for value in lambda_mont]
assert len(lambdas) == 192
rng = random.Random(0x08120260824)
tile_reports = []
checks = 0
for tile in proof080["tiles"]:
    tile_index = tile["tile"]
    tile_lambdas = lambdas[32 * tile_index:32 * (tile_index + 1)]
    roots0 = [value for value in range(Q) if value * value % Q == tile_lambdas[0]]
    assert len(roots0) == 2
    mu0 = min(roots0)
    permutation = PHYSICAL_TO_INVERSE32
    assert all((mu0 * pow(W64, permutation[physical], Q)) ** 2 % Q
               == tile_lambdas[physical] for physical in range(32))
    for _ in range(200):
        coeff = [[rng.randrange(Q) for _ in range(32)] for _ in range(4)]
        spectra = [dft(row, OMEGA32_CURRENT) for row in coeff]
        u0 = [0] * 64
        u1 = [0] * 64
        for k in range(32):
            mu = mu0 * pow(W64, k, Q) % Q
            u0[k] = (spectra[0][k] + mu * spectra[2][k]) % Q
            u1[k] = (spectra[1][k] + mu * spectra[3][k]) % Q
            u0[k + 32] = (spectra[0][k] - mu * spectra[2][k]) % Q
            u1[k + 32] = (spectra[1][k] - mu * spectra[3][k]) % Q
        y0 = idft(u0, W64)
        y1 = idft(u1, W64)
        expected0 = [value for n in range(32) for value in (coeff[0][n], mu0 * coeff[2][n] % Q)]
        expected1 = [value for n in range(32) for value in (coeff[1][n], mu0 * coeff[3][n] % Q)]
        assert y0 == expected0 and y1 == expected1
        checks += 128
    tile_reports.append({
        "tile": tile_index, "mu0": mu0,
        "canonical_lambda_orbit_index": tile["physical_to_cyclic_index"],
        "physical_to_inverse64_index": permutation,
        "common_endpoint": "even=c0/c1; odd=mu0*c2/mu0*c3",
        "late_uniform_normalization": "multiply odd positions by mu0^-1, fold into inverse64 normalization",
    })

report = {
    "schema": "ntruplus768-gt32-late-d2-inverse64-081-oracle-v1",
    "q": Q, "omega64": W64, "omega32_current": OMEGA32_CURRENT,
    "root_automorphism": "omega64=base_omega64^21; physical index comes from selected production inverse32 impulse topology",
    "tiles": tile_reports,
    "random_endpoint_checks": checks,
    "identity": {
        "input_tensor": "32 Q x 4 quartic degrees",
        "candidate_tensor": "64 sign-Q x 2 quadratic degrees",
        "inverse64_output_plane0": "[c0[0],mu0*c2[0],...,c0[31],mu0*c2[31]]",
        "inverse64_output_plane1": "[c1[0],mu0*c3[0],...,c1[31],mu0*c3[31]]",
        "standalone_crt_merge_required": False,
    },
    "work_ledger": {
        "control_inverse_butterflies_scalar": 4 * 32 * 5 // 2,
        "candidate_inverse_butterflies_scalar": 2 * 64 * 6 // 2,
        "control_explicit_crt": 0,
        "candidate_explicit_crt": 0,
        "candidate_uniform_final_mu_normalizations_per_tile": 2,
        "warning": "butterfly count is a schedule selector, not a cycle veto",
    },
    "status": "REFERENCE_ENDPOINT_PASS_EXECUTABLE_NOT_RUN",
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"checks": checks, "identity": report["identity"],
                  "work_ledger": report["work_ledger"]}, indent=2))

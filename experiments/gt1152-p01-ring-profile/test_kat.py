"""Reproduce the checked-in NTRU+1152 KAT transcript with the Python oracle.

This is the completion gate for G1: the declared oracle must reproduce
ntruplus-ntt-Optimized/KAT/NTRU+1152/PQCkemKAT_3488.rsp byte-for-byte.

Usage:
    python3 test_kat.py            # all 100 cases
    python3 test_kat.py --count 3  # first 3 cases (quick check)
"""

import argparse
import json
import sys
import time
from pathlib import Path

import ntruplus1152 as P
from nistkat import CtrDrbg, self_test as aes_self_test

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
KAT = REPO / "ntruplus-ntt-Optimized/KAT/NTRU+1152/PQCkemKAT_3488.rsp"


def parse_kat(path):
    cases = []
    current = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition(" = ")
        key = key.strip()
        if key == "count":
            if current:
                cases.append(current)
            current = {"count": int(value)}
        else:
            current[key] = bytes.fromhex(value.strip())
    if current:
        cases.append(current)
    return cases


def run(limit=None):
    aes_self_test()
    cases = parse_kat(KAT)
    if limit is not None:
        cases = cases[:limit]

    # The harness seeds one DRBG with entropy_input = 0,1,...,47 and draws one
    # 48-byte seed per case, then reseeds a fresh DRBG from that seed.
    outer = CtrDrbg(bytes(range(48)))
    seeds = [outer.randombytes(48) for _ in range(len(parse_kat(KAT)))]

    failures = []
    started = time.time()
    for case in cases:
        idx = case["count"]
        seed = seeds[idx]
        if seed != case["seed"]:
            failures.append((idx, "seed", seed.hex(), case["seed"].hex()))
            continue

        rng = CtrDrbg(seed)
        pk, sk = P.crypto_kem_keypair(rng)
        ct, ss = P.crypto_kem_enc(pk, rng)
        fail, ss_dec = P.crypto_kem_dec(ct, sk)

        for name, got, want in (
            ("pk", pk, case["pk"]),
            ("sk", sk, case["sk"]),
            ("ct", ct, case["ct"]),
            ("ss", ss, case["ss"]),
        ):
            if got != want:
                # Report the first differing byte, not a truncated prefix: these
                # arrays are up to 3488 bytes and a prefix can look identical.
                off = next((i for i in range(min(len(got), len(want)))
                            if got[i] != want[i]), min(len(got), len(want)))
                failures.append((
                    idx, name,
                    f"byte[{off}]=0x{got[off]:02x} len={len(got)}",
                    f"byte[{off}]=0x{want[off]:02x} len={len(want)}",
                ))

        if fail:
            failures.append((idx, "dec_status", str(fail), "0"))
        elif ss_dec != ss:
            failures.append((idx, "ss_roundtrip", ss_dec.hex(), ss.hex()))

        print(f"  case {idx:3d}  {'ok' if not failures or failures[-1][0] != idx else 'FAIL'}",
              flush=True)

    elapsed = time.time() - started
    report = {
        "kat_file": str(KAT.relative_to(REPO)),
        "cases_checked": len(cases),
        "cases_total_in_file": len(parse_kat(KAT)),
        "failures": [
            {"count": c, "field": f, "got": g, "want": w} for c, f, g, w in failures
        ],
        "pass": not failures,
        "seconds": round(elapsed, 1),
    }
    (HERE / "kat-report.json").write_text(json.dumps(report, indent=2) + "\n")

    if failures:
        print(f"\nFAIL: {len(failures)} mismatches", file=sys.stderr)
        for c, f, g, w in failures[:5]:
            print(f"  count={c} {f}\n    got  {g}\n    want {w}", file=sys.stderr)
        return 1

    print(f"\nPASS: {len(cases)} KAT cases reproduced exactly ({elapsed:.1f}s)")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=None)
    args = parser.parse_args()
    raise SystemExit(run(args.count))

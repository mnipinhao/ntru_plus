#!/usr/bin/env python3
"""Phase-B decision summary for one mlkem-native-Keccak NTRU+ candidate.

Inputs (all under <experiment>/results, written by the shared tools):
  extended-multi-summary-<tag>.json     default SUPERCOP compiler selection, with
                                        --paired keccak:official=keccak-vs-official-<tag>
                                        --paired keccak:base=keccak-vs-base-<tag>
  extended-multi-summary-<tag>O3.json   fixed -O3 only (okc-native-gcc-O3-only.sh)
  extended-multi-summary-<tag>O2.json   fixed -O2 only (okc-native-gcc-O2-only.sh)
  keccak-diag-normal-*/summary.json     Phase-A same-ELF diagnostic (anomaly check)
Roles: official (avx2), base (current best Official-opt export), keccak
(base + mlkem-native Keccak export); comparisons keccak:official, keccak:base,
base:official.

Decision rule (per op): robust research win iff the Native pooled StQ2 delta
vs Official under DEFAULT compiler selection is negative AND the normal-
placement ASLR-on fixed-ELF paired 95% CI vs Official lies below zero.  The
same rule is reported vs base; the fixed -O3 / -O2 Native deltas are
compiler-sensitivity evidence only.

Anomaly check (Phase A): for Encap (hash_f + hash_g + hash_h) and Decap
(hash_g + hash_h), is the Native keccak - base saving closer to the sum of the
isolated same-ELF hash deltas or to the same-ELF in-KEM base_keccak - base
delta?  Keypair has no isolated counterpart (its SHAKE256 calls are the
direct genf/geng ones) and is reported without classification.
Writes results/keccak-phase-b-summary-<tag>.json.
"""

import argparse
import json
from pathlib import Path

OPS = ("keypair_cycles", "enc_cycles", "dec_cycles")
DIAG_OP = {"keypair_cycles": "keypair", "enc_cycles": "encap", "dec_cycles": "decap"}
HASHES = {"enc_cycles": ("hash_f", "hash_g", "hash_h"), "dec_cycles": ("hash_g", "hash_h")}
SETTINGS = {"default": "", "O3": "O3", "O2": "O2"}


def native_entry(nat, op, cand, base):
    e = nat["operations"][op]
    return {"baseline_stq2": e["stq2"][base], "candidate_stq2": e["stq2"][cand],
            "delta_stq1": e["stq1"]["delta"], "delta_stq2": e["stq2"]["delta"], "delta_stq3": e["stq3"]["delta"],
            "delta_percent_stq2": e["delta_percent_stq2"],
            "ci95_launch_resampling": e["stq2_delta_ci95_launch_resampling"],
            "favourable_launches": e["candidate_launches_below_official_median"],
            "launches": e["launches_per_role"],
            "per_batch_stq2_delta": e["per_batch_stq2_delta"],
            "negative_batches": e["per_batch_summary"]["negative_batches"]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    results = args.experiment.resolve() / "results"
    multi = {s: json.loads((results / f"extended-multi-summary-{args.tag}{suffix}.json").read_text())
             for s, suffix in SETTINGS.items()}
    out = {"schema": "ntruplus-keccak-phase-b/v1", "parameter": f"NTRU+{args.param}", "tag": args.tag,
           "implementations": multi["default"]["implementations"],
           "decision_rule": "robust research win iff Native (default compiler selection) pooled StQ2 delta "
                            "vs Official < 0 AND normal-placement ASLR-on fixed-ELF paired 95% CI vs "
                            "Official below zero; vs-base verdict by the same rule; fixed -O3/-O2 Native "
                            "is compiler-sensitivity evidence",
           "compiler_picks": {}, "supercop_try": {}, "native": {}, "paired": {}, "decision": {},
           "anomaly_check": {}}
    for s, m in multi.items():
        out["supercop_try"][s] = m["supercop_try"]
        out["compiler_picks"][s] = {"policy": m["compiler_policy"],
                                    "compiler_wrapper_sha256": m["compiler_wrapper_sha256"],
                                    "round_order": m["round_order"],
                                    "per_role": {r: [{"batch": i + 1, "level": row["level"],
                                                      "measure_elf_sha256": row["measure_elf_sha256"],
                                                      "hygiene_attempt": row["hygiene"]["attempt"],
                                                      "pre_loadavg1": row["hygiene"]["pre_loadavg1"],
                                                      "duration_s": row["hygiene"]["duration_s"]}
                                                     for i, row in enumerate(rows)]
                                                 for r, rows in m["per_batch_identity"].items()}}
        out["native"][s] = {}
        for spec, comp in m["comparisons"].items():
            out["native"][s][spec] = {op: native_entry(comp["native"], op, comp["candidate"], comp["baseline"])
                                      for op in OPS}
    for spec in ("keccak:official", "keccak:base"):
        comp = multi["default"]["comparisons"][spec]
        p = comp["paired"]["normal-aslr-on"]
        out["paired"][spec] = {"dir": p["dir"], "blocks": p["blocks"], "elf_sha256": p["elf_sha256"],
                               "hygiene": p["hygiene"], "operations": p["operations"]}
        out["decision"][spec] = {}
        for op in OPS:
            d = comp["decision"][op]
            out["decision"][spec][op] = {
                "verdict": d["verdict"], "native_default_delta": d["native_pooled_stq2_delta"],
                "native_default_ci95": d["native_ci95"], "normal_aslr_on_ci95": d["normal_aslr_on_ci95"],
                "native_fixed_O3_delta": out["native"]["O3"][spec][op]["delta_stq2"],
                "native_fixed_O2_delta": out["native"]["O2"][spec][op]["delta_stq2"],
                "negative_under_all_three_compiler_settings": all(
                    out["native"][s][spec][op]["delta_stq2"] < 0 for s in SETTINGS)}
    diag_path = sorted(results.glob("keccak-diag-normal-*/summary.json"))[-1]
    diag = json.loads(diag_path.read_text())["regions"]
    out["anomaly_check"]["phase_a_source"] = str(diag_path.relative_to(args.experiment.resolve()))
    for op in OPS:
        same_elf = diag[DIAG_OP[op]]["deltas"]["base_keccak-base"]["pooled_stq2_delta"]
        entry = {"same_elf_base_keccak_minus_base": same_elf}
        for s in SETTINGS:
            entry[f"native_{s}_keccak_minus_base"] = out["native"][s]["keccak:base"][op]["delta_stq2"]
        if op in HASHES:
            iso = sum(diag[h]["deltas"]["mlkem_o3-official"]["pooled_stq2_delta"] for h in HASHES[op])
            nat = entry["native_default_keccak_minus_base"]
            entry.update({"isolated_hash_sum": iso, "hashes": list(HASHES[op]),
                          "native_default_over_isolated": nat / iso, "native_default_over_same_elf": nat / same_elf,
                          "closer_to": "same-ELF in-KEM delta" if abs(nat - same_elf) < abs(nat - iso)
                          else "isolated hash sum"})
        out["anomaly_check"][op] = entry
    path = results / f"keccak-phase-b-summary-{args.tag}.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {path}")
    for s in SETTINGS:
        print(f"== native {s}: picks " + "; ".join(
            f"{r} {','.join(b['level'] for b in rows)}" for r, rows in out["compiler_picks"][s]["per_role"].items()))
        for spec, ops in out["native"][s].items():
            for op, e in ops.items():
                print(f"  {spec:16s} {op:15s} {e['baseline_stq2']:9.1f} -> {e['candidate_stq2']:9.1f} "
                      f"{e['delta_stq2']:+9.1f} ({e['delta_percent_stq2']:+.2f}%) "
                      f"CI [{e['ci95_launch_resampling'][0]:.1f}, {e['ci95_launch_resampling'][1]:.1f}] "
                      f"fav {e['favourable_launches']}/{e['launches']} batches "
                      f"{[round(x) for x in e['per_batch_stq2_delta']]}")
    for spec, p in out["paired"].items():
        for op, o in p["operations"].items():
            print(f"paired {spec:16s} {op:15s} {o['mean']:+9.2f} [{o['ci95'][0]:.2f}, {o['ci95'][1]:.2f}] "
                  f"{o['favourable_blocks']}/{o['blocks']}")
    for spec, ops in out["decision"].items():
        for op, d in ops.items():
            print(f"decision {spec:16s} {op:15s} {d['verdict']}  all-3-compilers-negative="
                  f"{d['negative_under_all_three_compiler_settings']}")
    for op in OPS:
        a = out["anomaly_check"][op]
        print(f"anomaly {op:15s} native {a['native_default_keccak_minus_base']:+.1f} same-ELF "
              f"{a['same_elf_base_keccak_minus_base']:+.1f} isolated {a.get('isolated_hash_sum', float('nan')):+.1f} "
              f"-> {a.get('closer_to')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

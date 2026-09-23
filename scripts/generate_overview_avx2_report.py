#!/usr/bin/env python3
"""Curate the 2026-09-23 slim AVX2 overview (Official / Official-opt / GT).

Reads the local raw tree results/avx2-overview-20260923/raw/ (Git-ignored):
  native-<n>/native-ext-<role>-b<k>-ov<n>/   run_extended_native.py batches
  native-<n>/extended-multi-summary-ov<n>.json summarize_extended_multi.py
  components-<n>/summary.json                run_overview_components.py summarize
  build-<n>/build-manifest.json              run_overview_components.py build
and writes the curated, committed files next to raw/:
  native.csv, components.csv, breakdown.csv, summary.json and verbatim copies
  of the per-n summaries (native-<n>-extended-multi-summary.json,
  components-<n>-summary.json, components-<n>-metadata.json,
  components-<n>-build-manifest.json)
plus the Markdown tables printed to stdout (pasted into the doc).
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "results/avx2-overview-20260923"
RAW = OUT / "raw"
OPS = ("keypair_cycles", "enc_cycles", "dec_cycles")
OPNAME = {"keypair_cycles": "keypair", "enc_cycles": "enc", "dec_cycles": "dec"}
PARAMS = ("768", "864", "1152")
ROLES = {"768": ("official", "opt", "gt"), "864": ("official", "opt"), "1152": ("official", "opt", "gt")}
IMPL = {
    "768": {"official": "avx2", "opt": "avx2-officialopt-lazy-freeze-qual001", "gt": "avx2-gt32-clean"},
    "864": {"official": "avx2", "opt": "avx2-officialopt-lazy-codec-qual002"},
    "1152": {"official": "avx2", "opt": "avx2-officialopt-lazy-freeze-qual001",
             "gt": "avx2-gt9x16-wire-h3-pairunpack-serializer-v2-exp017-sc20260831"},
}

# ---------------------------------------------------------------- caller map
# Rows: (label, class, {role-kind: [(component, count), ...] or None}).
# Kinds: "off" = Official-path adapter (Official, Official-opt, exp017 keygen/decap),
# "gt768", "exp017enc".  Classes: hash, arith, codec, sample (CBD1/SOTP/triple),
# fused-hash-codec, fused-arith-codec.
OFF = "off"
KEYPAIR = [
    ("seed expansion shake256 (x2)", "hash", {OFF: [("shake256_coins", 2)], "gt768": [("shake256_coins", 2)]}),
    ("CBD1 (x2)", "sample", {OFF: [("cbd1", 2)], "gt768": [("cbd1", 2)]}),
    ("triple (x2)", "sample", {OFF: [("triple", 2)], "gt768": [("triple", 2)]}),
    ("Forward (x2)", "arith", {OFF: [("forward", 2)], "gt768": [("forward_p", 2)]}),
    ("BaseInv (x2)", "arith", {OFF: [("baseinv", 2)], "gt768": [("baseinv_j1", 2)]}),
    ("BaseMul (x2)", "arith", {OFF: [("basemul", 2)], "gt768": [("basemul_f0_j1", 2)]}),
    ("tobytes (x3)", "codec", {OFF: [("tobytes", 3)], "gt768": [("pack_p_sp1_lazy", 3)]}),
    ("hash_f", "hash", {OFF: [("hash_f", 1)], "gt768": [("hash_f", 1)]}),
]
ENC = [
    ("pk frombytes", "codec", {OFF: [("frombytes", 1)], "gt768": [("unpack_m", 1)], "exp017enc": None}),
    ("hash_f (pk)", "hash", {OFF: [("hash_f", 1)], "gt768": [("hash_f", 1)], "exp017enc": [("hash_f", 1)]}),
    ("hash_h", "hash", {OFF: [("hash_h", 1)], "gt768": [("hash_h", 1)], "exp017enc": [("hash_h", 1)]}),
    ("CBD1", "sample", {OFF: [("cbd1", 1)], "gt768": [("cbd1", 1)], "exp017enc": [("cbd1", 1)]}),
    ("Forward r, m (x2)", "arith", {OFF: [("forward", 2)], "gt768": [("forward_m", 2)],
                                    "exp017enc": [("gt_forward", 2)]}),
    ("r tobytes", "codec", {OFF: [("tobytes", 1)], "gt768": [("pack_m_lazy", 1)], "exp017enc": None}),
    ("hash_g", "hash", {OFF: [("hash_g", 1)], "gt768": [("hash_g", 1)], "exp017enc": None}),
    ("[exp017] Serializer V2 + hash_g (fuses r tobytes + hash_g)", "fused-hash-codec",
     {OFF: None, "gt768": None, "exp017enc": [("serializer_v2_hash_g", 1)]}),
    ("SOTP encode", "sample", {OFF: [("sotp_encode", 1)], "gt768": [("sotp_encode", 1)],
                               "exp017enc": [("sotp_encode", 1)]}),
    ("BaseMul", "arith", {OFF: [("basemul", 1)], "gt768": [("basemul_general_m", 1)], "exp017enc": None}),
    ("add", "arith", {OFF: [("add", 1)], "gt768": [("add", 1)], "exp017enc": None}),
    ("ct tobytes", "codec", {OFF: [("tobytes", 1)], "gt768": [("pack_m_highrange", 1)], "exp017enc": None}),
    ("[exp017] H4 exact egress (fuses pk frombytes + BaseMul + add + ct tobytes)", "fused-arith-codec",
     {OFF: None, "gt768": None, "exp017enc": [("h4_exact_egress", 1)]}),
]
DEC = [
    ("ct + sk frombytes (x3)", "codec", {OFF: [("frombytes", 3)], "gt768": [("unpack3_m", 1)]}),
    ("BaseMulScale", "arith", {OFF: [("basemul_scale", 1)], "gt768": [("basemul_scale_m", 1)]}),
    ("inverse", "arith", {OFF: [("inverse", 1)], "gt768": [("inverse_m", 1)]}),
    ("crepmod3", "arith", {OFF: [("crepmod3", 1)], "gt768": [("crepmod3", 1)]}),
    ("Forward m, r' (x2)", "arith", {OFF: [("forward", 2)], "gt768": [("forward_m", 2)]}),
    ("sub", "arith", {OFF: [("sub", 1)], "gt768": [("sub", 1)]}),
    ("BaseMul", "arith", {OFF: [("basemul", 1)], "gt768": [("basemul_general_m", 1)]}),
    ("recovered r tobytes", "codec", {OFF: [("tobytes", 1)], "gt768": [("pack_m_centered", 1)]}),
    ("hash_g", "hash", {OFF: [("hash_g", 1)], "gt768": [("hash_g", 1)]}),
    ("SOTP decode", "sample", {OFF: [("sotp_decode", 1)], "gt768": [("sotp_decode", 1)]}),
    ("hash_h", "hash", {OFF: [("hash_h", 1)], "gt768": [("hash_h", 1)]}),
    ("CBD1", "sample", {OFF: [("cbd1", 1)], "gt768": [("cbd1", 1)]}),
    ("re-encryption tobytes (+ verify)", "codec", {OFF: [("tobytes", 1)], "gt768": [("equal_m_modq", 1)]}),
]
STAGES = {"keypair": KEYPAIR, "enc": ENC, "dec": DEC}
KEM = {"keypair": "kem_keypair", "enc": "kem_enc", "dec": "kem_dec"}
NATIVE_OP = {"keypair": "keypair_cycles", "enc": "enc_cycles", "dec": "dec_cycles"}


def kind(n, role, op):
    if role == "gt" and n == "768":
        return "gt768"
    if role == "gt" and n == "1152" and op == "enc":
        return "exp017enc"
    return OFF


def try_lines(batch: Path):
    out = set()
    for line in (batch / "data").read_text(errors="replace").splitlines():
        w = line.split()
        if len(w) > 9 and w[6] == "try":
            out.add((w[7], w[8], w[12]))
    return out


def main() -> int:
    native, native_rows, try_status = {}, [], {}
    for n in PARAMS:
        s = json.loads((RAW / f"native-{n}" / f"extended-multi-summary-ov{n}.json").read_text())
        native[n] = {"round_order": s["round_order"], "roles": s["roles"],
                     "implementations": s["implementations"], "picks": {}, "ops": {}}
        for role in ROLES[n]:
            native[n]["picks"][role] = [r["level"] for r in s["per_batch_identity"][role]]
            status = set()
            for r in s["per_batch_identity"][role]:
                status |= try_lines(RAW / f"native-{n}" / r["dir"])
            try_status[f"{n}/{role}"] = sorted(status)
        for op in OPS:
            e0 = next(iter(s["comparisons"].values()))["native"]["operations"][op]
            row = {"official": e0["stq2"]["official"]}
            for spec, c in s["comparisons"].items():
                e = c["native"]["operations"][op]
                row[c["candidate"]] = {
                    "stq2": e["stq2"][c["candidate"]], "delta": e["stq2"]["delta"],
                    "delta_percent": e["delta_percent_stq2"],
                    "ci95": e["stq2_delta_ci95_launch_resampling"],
                    "resolved": not (e["stq2_delta_ci95_launch_resampling"][0] <= 0 <=
                                     e["stq2_delta_ci95_launch_resampling"][1]),
                    "below_official_median": e["candidate_launches_below_official_median"],
                    "launches": e["launches_per_role"],
                    "per_batch_delta": e["per_batch_stq2_delta"]}
            native[n]["ops"][op] = row
            for role in ROLES[n]:
                r = row[role] if role != "official" else None
                native_rows.append({"parameter": n, "operation": OPNAME[op], "role": role,
                                    "implementation": IMPL[n][role],
                                    "stq2": row["official"] if r is None else r["stq2"],
                                    "delta_vs_official": "" if r is None else r["delta"],
                                    "ci95_low": "" if r is None else r["ci95"][0],
                                    "ci95_high": "" if r is None else r["ci95"][1],
                                    "resolved_at_27": "" if r is None else r["resolved"],
                                    "below_official_median": "" if r is None else r["below_official_median"],
                                    "launches": 27,
                                    "compiler_picks": "/".join(native[n]["picks"][role])})
    # checksum consistency: every implementation of one n must report the same try checksum, ok
    for n in PARAMS:
        sums = {t[0] for role in ROLES[n] for t in try_status[f"{n}/{role}"]}
        oks = {t[1] for role in ROLES[n] for t in try_status[f"{n}/{role}"]}
        if len(sums) != 1 or oks != {"ok"}:
            raise SystemExit(f"try/checksum inconsistency for {n}: {sums} {oks}")

    comps, comp_rows, breakdown_rows, build = {}, [], [], {}
    for n in PARAMS:
        comps[n] = json.loads((RAW / f"components-{n}" / "summary.json").read_text())
        bm = json.loads((RAW / f"build-{n}" / "build-manifest.json").read_text())
        build[n] = {"elf_sha256": bm["elf_sha256"], "link_order": bm["link_order"],
                    "roles": {r: {k: v[k] for k in ("tree_sha256", "adapter", "adapter_defines", "sources",
                                                     "renamed_symbols")} for r, v in bm["roles"].items()}}
        for comp, roles in comps[n]["components"].items():
            for role, e in roles.items():
                d = e.get("delta_vs_baseline")
                comp_rows.append({"parameter": n, "component": comp, "role": role,
                                  "stq2": e["stq2"], "stq1": e["stq1"], "stq3": e["stq3"],
                                  "observations": e["observations"],
                                  "delta_vs_official": d["stq2"] if d else "",
                                  "ci95_low": d["ci95_launch_resampling"][0] if d else "",
                                  "ci95_high": d["ci95_launch_resampling"][1] if d else "",
                                  "favourable_launches": f"{d['favourable_launches']}/{d['launches']}" if d else ""})
    for n in PARAMS:
        C = comps[n]["components"]
        for op, rows in STAGES.items():
            for label, cls, spec in rows:
                for role in ROLES[n]:
                    k = kind(n, role, op)
                    parts = spec[k] if k in spec else spec[OFF]
                    if parts is None:
                        continue
                    cyc = sum(C[c][role]["stq2"] * m for c, m in parts)
                    breakdown_rows.append({"parameter": n, "operation": op, "stage": label, "class": cls,
                                           "role": role, "components": "+".join(f"{m}x{c}" for c, m in parts),
                                           "stq2_cycles": cyc})
            for role in ROLES[n]:
                breakdown_rows.append({"parameter": n, "operation": op, "stage": "same-ELF KEM total",
                                       "class": "total", "role": role, "components": KEM[op],
                                       "stq2_cycles": C[KEM[op]][role]["stq2"]})
                nat = native[n]["ops"][NATIVE_OP[op]]
                breakdown_rows.append({"parameter": n, "operation": op, "stage": "Native StQ2 (27 launches)",
                                       "class": "native", "role": role, "components": IMPL[n][role],
                                       "stq2_cycles": nat["official"] if role == "official" else nat[role]["stq2"]})

    def write(path, rows):
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    write(OUT / "native.csv", native_rows)
    write(OUT / "components.csv", comp_rows)
    write(OUT / "breakdown.csv", breakdown_rows)
    summary = {"schema": "ntruplus-avx2-overview/v1", "implementations": IMPL, "native": native,
               "try_checksum": try_status, "component_build": build,
               "component_run": {n: {k: comps[n]["metadata"][k] for k in
                                     ("elf_sha256", "cpu", "launches", "aslr_randomize_va_space", "placement",
                                      "cpucycles", "host_hygiene") if k in comps[n]["metadata"]}
                                 for n in PARAMS}}
    for n in PARAMS:
        for src, dst in ((RAW / f"native-{n}" / f"extended-multi-summary-ov{n}.json",
                          f"native-{n}-extended-multi-summary.json"),
                         (RAW / f"components-{n}" / "summary.json", f"components-{n}-summary.json"),
                         (RAW / f"components-{n}" / "metadata.json", f"components-{n}-metadata.json"),
                         (RAW / f"build-{n}" / "build-manifest.json", f"components-{n}-build-manifest.json")):
            shutil.copyfile(src, OUT / dst)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print_markdown(native, comps, breakdown_rows)
    return 0


def f1(x):
    return f"{x:.1f}"


def print_markdown(native, comps, breakdown_rows):
    p = print
    p("## Native\n")
    p("| n | op | Official | Official-opt | opt - Official [95% CI] | opt below Off. median | GT | GT - Official [95% CI] | GT below Off. median |")
    p("|---:|---|---:|---:|---:|---:|---:|---:|---:|")
    for n in PARAMS:
        for op in OPS:
            r = native[n]["ops"][op]
            cells = [n, OPNAME[op], f1(r["official"])]
            for role in ("opt", "gt"):
                if role not in r:
                    cells += ["N/A", "N/A", "N/A"] if role == "gt" else []
                    continue
                e = r[role]
                mark = "" if e["resolved"] else " (not resolved at 27 launches)"
                d = f"{e['delta']:+.1f} ({e['delta_percent']:+.2f}%) [{e['ci95'][0]:+.1f}, {e['ci95'][1]:+.1f}]{mark}"
                cells += [f1(e["stq2"]), d, f"{e['below_official_median']}/{e['launches']}"]
            p("| " + " | ".join(cells) + " |")
    p("\nCompiler picks (SUPERCOP default selection, batch 1/2/3):\n")
    for n in PARAMS:
        p(f"- {n}: " + "; ".join(f"{role} {'/'.join(native[n]['picks'][role])}" for role in ROLES[n])
          + f" (round order {' | '.join(native[n]['round_order'])})")
    for n in PARAMS:
        C = comps[n]["components"]
        p(f"\n## Components {n}\n")
        roles = ROLES[n]
        p("| component | " + " | ".join(roles) + " | " +
          " | ".join(f"{r} - official [95% CI] (fav.)" for r in roles[1:]) + " |")
        p("|---|" + "---:|" * (len(roles) * 2 - 1))
        for comp, e in C.items():
            cells = [comp] + [f1(e[r]["stq2"]) if r in e else "-" for r in roles]
            for r in roles[1:]:
                d = e.get(r, {}).get("delta_vs_baseline")
                cells.append(f"{d['stq2']:+.1f} [{d['ci95_launch_resampling'][0]:+.1f}, "
                             f"{d['ci95_launch_resampling'][1]:+.1f}] ({d['favourable_launches']}/{d['launches']})"
                             if d else "-")
            p("| " + " | ".join(cells) + " |")
    for n in PARAMS:
        roles = ROLES[n]
        for op in ("keypair", "enc", "dec"):
            p(f"\n### Breakdown {n} {op}\n")
            p("| stage | class | " + " | ".join(roles) + " |")
            p("|---|---|" + "---:|" * len(roles))
            rows = [r for r in breakdown_rows if r["parameter"] == n and r["operation"] == op]
            labels = list(dict.fromkeys(r["stage"] for r in rows))
            sums = {r: 0.0 for r in roles}
            cls_sum = {r: {} for r in roles}
            for label in labels:
                by = {r["role"]: r for r in rows if r["stage"] == label}
                cls = next(iter(by.values()))["class"]
                if cls in ("total", "native"):
                    continue
                for r, e in by.items():
                    sums[r] += e["stq2_cycles"]
                    cls_sum[r][cls] = cls_sum[r].get(cls, 0) + e["stq2_cycles"]
                p(f"| {label} | {cls} | " + " | ".join(
                    f"{by[r]['stq2_cycles']:.0f} ({by[r]['components']})" if r in by else "fused/absent"
                    for r in roles) + " |")
            p("| **sum of anchors** | | " + " | ".join(f"**{sums[r]:.0f}**" for r in roles) + " |")
            for label in labels:
                by = {r["role"]: r for r in rows if r["stage"] == label}
                if next(iter(by.values()))["class"] in ("total", "native"):
                    p(f"| {label} | | " + " | ".join(f"{by[r]['stq2_cycles']:.0f}" for r in roles) + " |")
            p("\nclass shares of anchor sum: " + "; ".join(
                f"{r}: " + ", ".join(f"{c} {100 * v / sums[r]:.0f}%" for c, v in sorted(cls_sum[r].items()))
                for r in roles))


if __name__ == "__main__":
    raise SystemExit(main())

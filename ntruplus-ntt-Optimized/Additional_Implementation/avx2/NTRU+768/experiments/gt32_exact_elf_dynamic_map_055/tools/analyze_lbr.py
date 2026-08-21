#!/usr/bin/env python3
"""Extract Encap call/return intervals from Intel LBR cycle metadata.

The mapping deliberately keys return edges by the instruction after a known
Encap callsite.  This avoids depending on incomplete assembler symbol sizes.
For leaf callees, the RET interval is the callee body.  For nested callees it
is only the tail after the final nested return and is labelled accordingly.
"""

import argparse
import json
import re
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path


CALLSITES = {
    "official": [
        (0x364E, "decode", "poly_frombytes", True),
        (0x36A4, "hash_f", "hash_f", False),
        (0x36BC, "hash_h", "hash_h", False),
        (0x36D1, "cbd_r", "poly_cbd1", True),
        (0x36DE, "ntt_r", "poly_ntt", True),
        (0x36EE, "pack_rhat", "poly_tobytes", True),
        (0x36F9, "hash_g", "hash_g", False),
        (0x3711, "sotp_m", "poly_sotp_encode", True),
        (0x371E, "ntt_m", "poly_ntt", True),
        (0x3738, "basemul", "poly_basemul", True),
        (0x374F, "add_m", "poly_add", True),
        (0x375C, "pack_ciphertext", "poly_tobytes", True),
        (0x3785, "clear_0", "explicit_bzero", False),
        (0x3799, "clear_1", "explicit_bzero", False),
        (0x37B0, "clear_2", "explicit_bzero", False),
        (0x37C7, "clear_3", "explicit_bzero", False),
    ],
    "gt": [
        (0xAD5F, "decode", "ntruplus768_unpack_m_avx2", False),
        (0xADAF, "hash_f", "hash_f", False),
        (0xADCC, "hash_h", "hash_h", False),
        (0xADE1, "cbd_r", "poly_cbd1", True),
        (0xADF6, "frontend_r", "ntruplus768_ntt_frontend_avx2", True),
        (0xAE0B, "ntt_r", "ntruplus768_ntt_m_avx2", True),
        (0xAE1B, "pack_rhat", "ntruplus768_pack_m_lazy10788_avx2", True),
        (0xAE26, "hash_g", "hash_g", False),
        (0xAE3B, "sotp_m", "poly_sotp_encode", True),
        (0xAE50, "frontend_m", "ntruplus768_ntt_frontend_avx2", True),
        (0xAE65, "ntt_m", "ntruplus768_ntt_m_avx2", True),
        (0xAE7F, "basemul", "ntruplus768_basemul_general_m_avx2", True),
        (0xAE9C, "add_m", "poly_add", True),
        (0xAEAC, "pack_ciphertext", "ntruplus768_pack_m_highrange12699_avx2", True),
        (0xAED5, "clear_0", "explicit_bzero", False),
        (0xAEE9, "clear_1", "explicit_bzero", False),
        (0xAF00, "clear_2", "explicit_bzero", False),
        (0xAF17, "clear_3", "explicit_bzero", False),
    ],
}

# Nested wrapper used by the GT decode path.  Its body is a leaf for the
# any_call/any_ret filter, so this interval can be reported separately.
NESTED = {
    "official": [],
    "gt": [(0x5A0A, "decode_body", "ntruplus768_unpack_m_body_avx2", True)],
}

MMAP_RE = re.compile(
    r"\[0x([0-9a-f]+)\(0x([0-9a-f]+)\) @ 0x([0-9a-f]+).*\]: r-xp (.+)$"
)
BRANCH_RE = re.compile(
    r"0x([0-9a-f]+)/0x([0-9a-f]+)/[^/]*/[^/]*/[^/]*/(\d+)/([^/]*)/"
)


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        return None
    return ordered[round((len(ordered) - 1) * fraction)]


def summarize(values):
    if not values:
        return None
    return {
        "observations": len(values),
        "median": statistics.median(values),
        "p10": percentile(values, 0.10),
        "p90": percentile(values, 0.90),
    }


def perf_output(data: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["perf", "script", "-i", str(data), *arguments],
        capture_output=True, text=True, check=True,
    )
    return result.stdout


def image_mapping(data: Path, binary: Path):
    output = perf_output(data, "--show-mmap-events")
    wanted = str(binary.resolve())
    matches = []
    for line in output.splitlines():
        match = MMAP_RE.search(line)
        if match and str(Path(match.group(4)).resolve()) == wanted:
            start, size, offset = (int(match.group(i), 16) for i in range(1, 4))
            matches.append((start, size, offset))
    if len(matches) != 1:
        raise RuntimeError(f"expected one executable mapping for {wanted}: {matches}")
    start, size, offset = matches[0]
    return {"start": start, "size": size, "offset": offset, "base": start - offset}


def analyze_trace(data: Path, binary: Path, implementation: str):
    mapping = image_mapping(data, binary)
    base = mapping["base"]
    sites = CALLSITES[implementation] + NESTED[implementation]
    calls = {address: (site, symbol, leaf) for address, site, symbol, leaf in sites}
    returns = {address + 5: (site, symbol, leaf) for address, site, symbol, leaf in sites}
    values = defaultdict(list)
    samples = 0
    output = perf_output(data, "-F", "brstack")
    for line in output.splitlines():
        if not line.strip():
            continue
        samples += 1
        for match in BRANCH_RE.finditer(line):
            source = int(match.group(1), 16) - base
            target = int(match.group(2), 16) - base
            cycles = int(match.group(3))
            branch_type = match.group(4)
            if branch_type in ("CALL", "IND_CALL") and source in calls:
                site, symbol, leaf = calls[source]
                values[(site, "caller_interval")].append(cycles)
            elif branch_type == "RET" and target in returns:
                site, symbol, leaf = returns[target]
                kind = "body" if leaf else "nested_tail"
                values[(site, kind)].append(cycles)
    return {
        "samples": samples,
        "mapping": {key: hex(value) for key, value in mapping.items()},
        "intervals": {
            f"{site}:{kind}": summarize(cycles)
            for (site, kind), cycles in sorted(values.items())
        },
    }


def launch_summary(rows, implementation):
    keys = sorted({key for row in rows for key in row["intervals"]})
    output = {}
    for key in keys:
        medians = [
            row["intervals"][key]["median"]
            for row in rows
            if row["intervals"].get(key) is not None
        ]
        output[key] = summarize(medians)
        output[key]["launches"] = len(medians)
    return output


def semantic_summary(summaries):
    off, gt = summaries["official"], summaries["gt"]
    groups = {
        "decode": (["decode:body"], ["decode_body:body", "decode:nested_tail"]),
        "cbd_r": (["cbd_r:body"], ["cbd_r:body"]),
        "r_producer": (["ntt_r:body"], ["frontend_r:body", "ntt_r:body"]),
        "rhat_serializer": (["pack_rhat:body"], ["pack_rhat:body"]),
        "sotp_m": (["sotp_m:body"], ["sotp_m:body"]),
        "m_producer": (["ntt_m:body"], ["frontend_m:body", "ntt_m:body"]),
        "basemul": (["basemul:body"], ["basemul:body"]),
        "add_m": (["add_m:body"], ["add_m:body"]),
        "ciphertext_serializer": (["pack_ciphertext:body"], ["pack_ciphertext:body"]),
    }
    result = {}
    for name, (off_keys, gt_keys) in groups.items():
        if not all(key in off for key in off_keys) or not all(key in gt for key in gt_keys):
            continue
        off_value = sum(off[key]["median"] for key in off_keys)
        gt_value = sum(gt[key]["median"] for key in gt_keys)
        result[name] = {
            "official_core_cycles": off_value,
            "gt_core_cycles": gt_value,
            "gt_minus_official": gt_value - off_value,
            "note": "sum of launch-level median LBR intervals",
        }
    result["direct_leaf_total"] = {
        "official_core_cycles": sum(
            value["official_core_cycles"] for value in result.values()
        ),
        "gt_core_cycles": sum(value["gt_core_cycles"] for value in result.values()),
        "gt_minus_official": sum(
            value["gt_minus_official"] for value in result.values()
        ),
        "note": (
            "descriptive sum of mapped leaf medians; excludes Hash/SHAKE, "
            "cleanup bodies, and non-leaf intervals"
        ),
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    root = args.manifest.parent
    binaries = {
        name: Path(details["path"])
        for name, details in manifest["binaries"].items()
    }
    rows = []
    by_implementation = defaultdict(list)
    for record in manifest["rows"]:
        implementation = record["implementation"]
        analysis = analyze_trace(
            root / record["perf_data"], binaries[implementation], implementation
        )
        row = {**record, **analysis}
        rows.append(row)
        by_implementation[implementation].append(row)

    summaries = {
        implementation: launch_summary(group, implementation)
        for implementation, group in by_implementation.items()
    }
    output = {
        "schema": "gt32-exact-elf-dynamic-map-055-analysis-v1",
        "method": {
            "event": "cpu_core/cycles/u",
            "branch_filter": manifest["branch_filter"],
            "primary_unit": "per-launch median LBR branch interval",
            "warning": (
                "Only leaf RET intervals are whole component bodies. "
                "Nested tails and caller intervals are not additive component costs."
            ),
        },
        "binaries": manifest["binaries"],
        "summaries": summaries,
        "semantic_leaf_map": semantic_summary(summaries),
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output["semantic_leaf_map"], indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Prepare an exact-commit P56 bundle from the reviewed P12 profiler."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P12 = ROOT / "experiments/gt864-p12-decaps-profile"
PRODUCTION = Path("ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864")
SYNC = HERE / "build/sync"
EXPECTED_REVISION = "9941d3bc"
EXPERIMENT = "GT864-P56-OFFICIAL-PROFILE-20260917"

FILES = (
    "pi_run.py", "generate_profile_kem.py", "full_harness.c",
    "profile_harness.c", "profile_event_harness.c", "summarize.py",
    "run_events.py", "summarize_events.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_production(destination: Path, revision: str) -> None:
    archive = subprocess.check_output(
        ["git", "archive", revision, str(PRODUCTION)], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        for member in stream.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to(PRODUCTION)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            source = stream.extractfile(member)
            assert source is not None
            target.write_bytes(source.read())


def add_fused_groups(name: str, content: str) -> str:
    if name == "generate_profile_kem.py":
        content = content.replace(
            'gt = sys.argv[2] == "gt"',
            'gt = sys.argv[2] == "gt"\n'
            'if not gt:\n'
            '    source = source.replace("static inline int verify(",\n'
            '                            "static inline int prof_real_verify(")')
        content = content.replace(
            '"hash_g", "hash_h", "SHAKE_sampling", "RNG", "cleanup", "Inverse_to_ternary",',
            '"hash_g", "hash_h", "SHAKE_sampling", "RNG", "cleanup", "Inverse_to_ternary",\n'
            '    "Full_to_hash_g", "Full_compare",')
        content = content.replace(
            '"gt864_fr0_frombytes_checked": ("FromBytes_checked", "gt864_fr0_frombytes_checked", True),',
            '"gt864_fr0_frombytes_checked": ("FromBytes_checked", "gt864_fr0_frombytes_checked", True),\n'
            '        "hash_g_fr0": ("Full_to_hash_g", "hash_g_fr0", False),\n'
            '        "gt864_fr0_tobytes_full_compare": ("Full_compare", "gt864_fr0_tobytes_full_compare", True),')
        content = content.replace(
            'else:\n    mapping.update({',
            'else:\n    mapping.update({\n'
            '        "verify": ("Full_compare", "prof_real_verify", True),')
    if name in {"profile_harness.c", "profile_event_harness.c"}:
        content = content.replace("enum { GROUPS = 22,", "enum { GROUPS = 24,")
        content = content.replace(
            '"hash_g", "hash_h", "SHAKE_sampling", "RNG", "cleanup", "Inverse_to_ternary"',
            '"hash_g", "hash_h", "SHAKE_sampling", "RNG", "cleanup", "Inverse_to_ternary",\n'
            '    "Full_to_hash_g", "Full_compare"')
    return content


def main() -> None:
    revision = subprocess.check_output(
        ["git", "rev-parse", EXPECTED_REVISION], cwd=ROOT, text=True
    ).strip()
    if not revision.startswith(EXPECTED_REVISION):
        raise RuntimeError(f"P56 revision mismatch: {revision}")
    if SYNC.exists():
        shutil.rmtree(SYNC)
    SYNC.mkdir(parents=True)
    extract_production(SYNC / "gt-source", revision)
    for name in FILES:
        content = add_fused_groups(name, (P12 / name).read_text())
        if name == "pi_run.py":
            content = content.replace('"gt_production_revision": "dd8c3146"',
                                      f'"gt_production_revision": "{revision}"')
            content = content.replace('"gt_control_revision": "1c790870"',
                                      f'"gt_control_revision": "{revision}"')
        if name == "summarize.py":
            content = content.replace("GT864-P12-DECAPS-PROFILE-20260912", EXPERIMENT)
        (SYNC / name).write_text(content)
    shutil.copytree(P12 / "compat", SYNC / "compat")
    (SYNC / "compat/gt864_poly_api.h").write_text(
        "#ifndef GT864_PROFILER_POLY_API_H\n"
        "#define GT864_PROFILER_POLY_API_H\n"
        "#include \"poly.h\"\n"
        "void gt_d1_poly_ntt(poly *, const poly *);\n"
        "void gt_d1_poly_basemul(poly *, const poly *, const poly *);\n"
        "void gt_d1_poly_basemul_add(poly *, const poly *, const poly *, const poly *);\n"
        "#endif\n"
    )
    manifest = {
        str(path.relative_to(SYNC)): sha256(path)
        for path in sorted(SYNC.rglob("*")) if path.is_file()
    }
    (HERE / "build/source-manifest.json").write_text(
        json.dumps({"revision": revision, "files": manifest}, indent=2) + "\n"
    )
    print(f"prepared P56 revision={revision} files={len(manifest)}")


if __name__ == "__main__":
    main()

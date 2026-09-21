#!/usr/bin/env python3
"""Install a namespaced NTRU+768 candidate with one shared M-to-wire encoder.

The candidate is deliberately produced from the qualified GT32 clean tree and
changes one caller edge only: Decap's recovered-r uses the already-required
lazy/high-range M encoder.  Encap still uses that exact encoder for r and the
ciphertext polynomial.  The installer also removes the now-dead centered
function emission from the disposable copy because Native SUPERCOP's selected
compiler recipe does not guarantee linker garbage collection.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import REPO_ROOT, read_lock, sha256_file, sha256_tree


SOURCE = (REPO_ROOT / "ntruplus-ntt-Optimized" / "Additional_Implementation" /
          "avx2" / "NTRU+768" / "clean" / "avx2-gt32-clean")
EXCLUDED = {
    "README.md", "SYMBOLS.md", "LAYOUTS.md", "IMPLEMENTATION.md",
    "BENCHMARK.md", "SOURCE-MANIFEST.md", "SHA256SUMS", "install-supercop.sh",
}
OLD_CALL = "ntruplus768_pack_m_centered_avx2(recovered_r, scratch->aux);"
NEW_CALL = "ntruplus768_pack_m_lazy10788_avx2(recovered_r, scratch->aux);"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument(
        "--implementation",
        default="avx2-gt32-serializer-unify-exp003-sc20260831",
    )
    args = parser.parse_args()

    root = args.campaign_root.resolve()
    marker_path = root / ".ntruplus-campaign.json"
    if not marker_path.is_file():
        raise SystemExit("installation requires a disposable SUPERCOP campaign")
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    lock = read_lock()
    if marker.get("kind") != "disposable-supercop-campaign" or \
            marker.get("supercop_version") != lock["version"]:
        raise SystemExit("campaign marker/lock mismatch")
    if args.implementation == "avx2" or "/" in args.implementation:
        raise SystemExit("implementation must be a new single-directory name")

    target = root / "crypto_kem" / "ntruplus768" / args.implementation
    if target.exists() or target.is_symlink():
        raise SystemExit(f"refusing to overwrite {target}")
    if not SOURCE.is_dir():
        raise SystemExit(f"missing qualified clean source: {SOURCE}")

    generated = SOURCE / "generated" / "tile4_inverse_tail_constants.inc"
    if not generated.is_file():
        raise SystemExit(f"missing generated clean source: {generated}")

    target.mkdir()
    for source in sorted(SOURCE.iterdir()):
        if source.name in EXCLUDED or source.name == "generated":
            continue
        if source.is_dir() or source.is_symlink():
            raise SystemExit(f"clean implementation is not flat: {source}")
        shutil.copy2(source, target / source.name)
    shutil.copy2(generated, target / generated.name)

    invntt = target / "invntt.s"
    invntt_text = invntt.read_text(encoding="utf-8")
    include = '.include "generated/tile4_inverse_tail_constants.inc"'
    if invntt_text.count(include) != 1:
        raise SystemExit("unexpected clean invntt include shape")
    invntt.write_text(
        invntt_text.replace(include, '.include "tile4_inverse_tail_constants.inc"'),
        encoding="utf-8",
    )

    decap = target / "decap.c"
    decap_text = decap.read_text(encoding="utf-8")
    if decap_text.count(OLD_CALL) != 1 or NEW_CALL in decap_text:
        raise SystemExit("unexpected clean Decap serializer call shape")
    decap.write_text(decap_text.replace(OLD_CALL, NEW_CALL), encoding="utf-8")

    # Native SUPERCOP's selected compiler recipe does not necessarily use
    # --gc-sections.  Merely making the centered entry point unreachable left
    # its 3815-byte macro expansion in the linked ELF in exp002.  Remove only
    # that now-dead function emission; the shared Q24 macros remain available
    # to the lazy encoder below.
    pack = target / "pack.s"
    pack_text = pack.read_text(encoding="utf-8")
    centered_emission = """ .section .text.ntruplus768_pack_m_centered_avx2,\"ax\",@progbits
 .p2align 5
 .globl ntruplus768_pack_m_centered_avx2
 .type ntruplus768_pack_m_centered_avx2,@function
ntruplus768_pack_m_centered_avx2:
 vmovdqa .Lq24_q(%rip), %ymm15
 Q24_ENCODE_SOA_BODY
 vzeroupper
 ret
 .size ntruplus768_pack_m_centered_avx2,.-ntruplus768_pack_m_centered_avx2
"""
    if pack_text.count(centered_emission) != 1:
        raise SystemExit("unexpected clean centered serializer emission")
    pack.write_text(pack_text.replace(centered_emission, ""), encoding="utf-8")

    for required in ("architectures", "goal-constbranch", "goal-constindex"):
        if not (target / required).is_file():
            raise SystemExit(f"installed candidate lacks {required}")
    architectures = set((target / "architectures").read_text().split())
    if not {"x86", "amd64"}.issubset(architectures):
        raise SystemExit("architectures must contain x86 and amd64")

    manifest = {
        "schema": "ntruplus768-serializer-unify-install/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "implementation": args.implementation,
        "parameter": "768",
        "source": str(SOURCE.relative_to(REPO_ROOT)),
        "source_tree_sha256": sha256_tree(SOURCE),
        "official_tree_sha256": lock["ntruplus768_avx2_tree_sha256"],
        "supercop_version": lock["version"],
        "candidate": {
            "changed_files": ["decap.c", "pack.s"],
            "old_call": OLD_CALL,
            "new_call": NEW_CALL,
            "semantic_contract": (
                "centered recovered-r is a subset of the lazy10788 input range; "
                "wire bytes must remain exact"
            ),
            "removed_symbol": "ntruplus768_pack_m_centered_avx2",
            "structural_hypothesis": (
                "one M-to-wire body serves recovered-r, Encap r, and ciphertext; "
                "the centered-only encoder emission is physically absent even "
                "when the native compiler recipe does not use linker GC"
            ),
        },
    }
    manifest_path = target / "SOURCE-MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    files = sorted(path for path in target.iterdir()
                   if path.is_file() and path.name != "SHA256SUMS")
    (target / "SHA256SUMS").write_text(
        "\n".join(f"{sha256_file(path)}  {path.name}" for path in files) + "\n",
        encoding="utf-8",
    )
    print(f"installed {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

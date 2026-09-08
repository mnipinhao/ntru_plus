#!/usr/bin/env python3

from pathlib import Path
import hashlib
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".c", ".h", ".S", ".s", ".inc", ".mk", ".md"}
BANNED_PATH_PARTS = {
    "__pycache__",
    "archive",
    "bench",
    "experiment",
    "experiments",
    "prototype",
    "slothy",
}
BANNED_FILE_SUFFIXES = {
    ".a",
    ".csv",
    ".dylib",
    ".json",
    ".log",
    ".map",
    ".o",
    ".out",
    ".perf",
    ".so",
}
BANNED_GENERATED_NAMES = {
    "PQCgenKAT_kem",
    "test_abi",
    "test_canonical",
    "test_kem",
    "test_zeroization",
    "test_support",
}
BANNED_TOKENS = (
    "GT_EXPERIMENT_",
    "GT_PRODUCTION_USE_",
    "GT_PRODUCTION_KEYGEN_LAYOUT",
    "GT_PRODUCTION_VARIANT",
)
REQUIRED_PUBLIC_SYMBOLS = (
    "poly_basemul_add_encap",
    "poly_tobytes_encap",
    "poly_frombytes_encap",
)
REQUIRED_INTERNAL_KEM_SYMBOLS = (
    "poly_ntt_encap_small_lazy",
    "poly_tobytes_encap_loose",
)
EXPECTED_KAT_RSP_SHA256 = (
    "22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8"
)


def fail(message: str) -> None:
    print(f"release-check: {message}", file=sys.stderr)
    raise SystemExit(1)


files = [path for path in ROOT.rglob("*") if path.is_file()]
include_fragments = sorted(
    path.relative_to(ROOT) for path in files if path.suffix == ".inc"
)
if include_fragments:
    fail(f"release must be flattened; found {include_fragments[0]}")

for path in files:
    relative = path.relative_to(ROOT)
    lowered = {part.lower() for part in relative.parts}
    bad_parts = sorted(lowered & BANNED_PATH_PARTS)
    if bad_parts:
        fail(f"banned path component {bad_parts[0]!r}: {relative}")
    if path.suffix.lower() in BANNED_FILE_SUFFIXES:
        fail(f"generated/result file in release: {relative}")
    if path.name in BANNED_GENERATED_NAMES:
        fail(f"generated binary in release: {relative}")
    if (
        relative.parent == Path(".")
        and relative.name in {"PQCkemKAT_2336.req", "PQCkemKAT_2336.rsp"}
    ):
        fail(f"generated KAT output in release root: {relative}")

for path in files:
    if path.suffix not in TEXT_SUFFIXES and path.name != "Makefile":
        continue
    text = path.read_text(encoding="utf-8", errors="strict")
    for token in BANNED_TOKENS:
        if token in text:
            fail(f"selector token {token!r}: {path.relative_to(ROOT)}")

headers = (ROOT / "poly.h").read_text(encoding="utf-8")
reference_header = (ROOT / "test/reference/poly_reference.h").read_text()
for symbol in ("poly_basemul", "poly_invntt"):
    if re.search(rf"\b{symbol}\s*\(", headers):
        fail(f"test-only declaration in production header: {symbol}")
    if not re.search(rf"\b{symbol}\s*\(", reference_header):
        fail(f"missing test-only declaration: {symbol}")
for symbol in REQUIRED_PUBLIC_SYMBOLS:
    if re.search(rf"\b{re.escape(symbol)}\s*\(", headers) is None:
        fail(f"missing public declaration: {symbol}")

kem_source = (ROOT / "kem.c").read_text(encoding="utf-8")
internal_headers = (ROOT / "ntt_internal.h").read_text(encoding="utf-8")
for symbol in REQUIRED_INTERNAL_KEM_SYMBOLS:
    if re.search(rf"\b{re.escape(symbol)}\s*\(", internal_headers) is None:
        fail(f"missing internal declaration: {symbol}")
    if re.search(rf"\b{re.escape(symbol)}\s*\(", kem_source) is None:
        fail(f"missing internal KEM consumer: {symbol}")

expected = {
    "ntt.S",
    "add.S",
    "base.S",
    "pack.S",
    "cbd.S",
    "crepmod3.S",
    "kem_api.S",
    "kem.c",
    "poly.h",
    "Makefile",
    "LICENSE",
    "SOURCE-MANIFEST.sha256",
    "util.h",
    "ntt_internal.h",
    "scripts/check_zeroization.py",
    "test/test_zeroization.c",
    "test/test_canonical.c",
    "test/reference/basemul.S",
    "test/reference/invntt.S",
    "test/reference/poly_reference.h",
    "kat/expected/PQCkemKAT_2336.req",
    "kat/expected/PQCkemKAT_2336.rsp",
}
missing = sorted(path for path in expected if not (ROOT / path).is_file())
if missing:
    fail(f"missing release source: {', '.join(missing)}")

kat_rsp = ROOT / "kat/expected/PQCkemKAT_2336.rsp"
kat_rsp_sha256 = hashlib.sha256(kat_rsp.read_bytes()).hexdigest()
if kat_rsp_sha256 != EXPECTED_KAT_RSP_SHA256:
    fail(
        "canonical KAT response hash mismatch: "
        f"{kat_rsp_sha256} != {EXPECTED_KAT_RSP_SHA256}"
    )

print(f"release-check: pass ({len(files)} files)")

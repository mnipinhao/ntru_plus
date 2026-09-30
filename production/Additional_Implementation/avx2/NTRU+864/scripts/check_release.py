#!/usr/bin/env python3
"""Release gates for the NTRU+864 AVX2 (avx2-opt) package.

Default: the source closure is exactly SOURCE-MANIFEST.sha256 (no build output,
experiment or selector files) and the canonical KAT hashes.
--keccak [--upstream DIR]: each vendored mlkem-native file is its comment naming
    the upstream file, then upstream b3ba7b32773e657dd37f6f87bce82528459ad8a4 minus the recorded removals
    (unused code) plus the recorded #include rewrites; no removed identifier is used, and the files equal
    the sibling packages' copies.  With --upstream (a checkout of mlkem-native at
    that commit) the removed ranges are also checked against upstream's text.
--objects OBJ...: the KEM objects define the three NIST entry points
    crypto_kem_keypair/enc/dec (plain names, as in the AArch64 packages), each
    exactly once, and every other global symbol they define carries the
    ntruplus864_avx2opt_ prefix; only the documented externals are imported.
"""
from pathlib import Path
import argparse
import hashlib
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "ntruplus864_avx2opt_"
KAT_REQ_SHA256 = "36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa"
KAT_RSP_SHA256 = "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c"

BANNED_PATH_PARTS = {"__pycache__", "archive", "bench", "build", "experiment", "experiments",
                     "prototype", "qualification", "results", "upstream"}
BANNED_SUFFIXES = {".a", ".csv", ".json", ".log", ".map", ".o", ".out", ".perf", ".so", ".i"}
CODE_SUFFIXES = {".c", ".h", ".s", ".S"}

# mlkem-native b3ba7b32773e657dd37f6f87bce82528459ad8a4: package file -> (upstream path, upstream sha256,
# sha256 of upstream minus the removals, [(first line, last line, sha256 of the
# removed lines, identifiers they define)], [(line number, upstream line, package
# line)]).  The removals are upstream line ranges: functions this build does not
# use, with their #define bindings and the macros only they use, and the
# #include lines of cbmc.h and verify.h.  The recorded lines are the only other
# differences: the #include of common.h, rewritten to mlkem_native_config.h,
# which defines what the files take from mlkem-native's headers.  Each file
# starts with VENDOR_HEADER, and the line numbers count from the end of it.
VENDOR_HEADER = ("/* Vendored from mlkem-native (commit b3ba7b32773e657dd37f6f87bce82528459ad8a4),\n"
                 " * {path}; scripts/check_release.py records any edits.\n"
                 " */\n")
MLKEM = {
    'fips202.c': ('mlkem/src/fips202/fips202.c', 'fb0654c0b33c45c929fdb2af2287807a7b8f312ac7f3baa3ddfaef0c030ef0b2',
        'd41d99fca8ea0d88b4ed52e9ceecb4b149404ed00c9d72b69dd6a83b6d2ff3ef', [
            (38, 38, 'dda2410a238eac4fe18ac434ca8330de75e66d2bfae6cc2dbfc925934cc878ed',
             ()),
            (106, 139, 'c4a91706dac3b83dcc43a4c9c874a84fbd650b8b8993c495c30f8143809bf9a5',
             ('mlk_keccak_squeezeblocks',)),
            (187, 206, '1b3d667f4b4b2b3205acba22b0385fe8d157a4a8b5eef51d555b63bf7c20161c',
             ('mlk_shake128_absorb_once', 'mlk_shake128_squeezeblocks', 'mlk_shake128_init', 'mlk_shake128_release')),
            (221, 244, '6ab01612d5b2cd669e3d7fc2512fa900f46fe52029ee63503b7a0fb71fe846b6',
             ('mlk_sha3_256', 'mlk_sha3_512')),
        ], [
            (34, '#include "../common.h"', '#include "mlkem_native_config.h"'),
        ]),
    'fips202.h': ('mlkem/src/fips202/fips202.h', 'a5efcf58893aa589dfe25a1069e11ab58408b2ad14e389014a785205300468a1',
        '24c0741a36a7c7ee174351195869fac8dfe3212d88d656b466d0bc675fcf94b6', [
            (8, 8, '2aa302d878de0fb0df64cb0d78fbea4ec6e50b00205c251cf62aaa16f2c6e11c',
             ()),
            (11, 11, '8e79b361c08d6a16ae1fab092f13470c3d4294cbf1e997124d5e572910120e71',
             ('SHAKE128_RATE',)),
            (13, 15, '798b0e2271172193d71be2830de54970d440e07163179a9557762e09fda6768e',
             ('SHA3_256_RATE', 'SHA3_384_RATE', 'SHA3_512_RATE')),
            (23, 74, '8fb0303e32cd391e5e12f1d01202dcb75e78c3b5b3ce1d846355956fdd0337a4',
             ('mlk_shake128_absorb_once', 'mlk_shake128_squeezeblocks', 'mlk_shake128_init', 'mlk_shake128_release')),
            (96, 143, 'eb02fbb443731504b1f7594aa61102a5f5ee35ba0cecff309eef19d63f2ef7dd',
             ('SHA3_256_HASHBYTES', 'mlk_sha3_256', 'SHA3_512_HASHBYTES', 'mlk_sha3_512', 'FIPS202_X4_DEFAULT_IMPLEMENTATION')),
        ], [
            (8, '#include "../common.h"', '#include "mlkem_native_config.h"'),
        ]),
    'keccakf1600.c': ('mlkem/src/fips202/keccakf1600.c', '461c278b0abb9fde098ee6b34a47056445573cb7aa5c4362d59e35041d0997e5',
        '74969a1915c9af21a290e51656857dc394580eee564e260e8abbd2f87318277c', [
            (83, 192, '486b3a277d8b5311250c9ec72ee7da32f7f861db3861e78706001f3645d0481a',
             ('mlk_keccakf1600x4_extract_bytes_c', 'mlk_keccakf1600x4_xor_bytes_c', 'mlk_keccakf1600x4_extract_bytes', 'mlk_keccakf1600x4_xor_bytes', 'mlk_keccakf1600x4_permute')),
        ], [
        ]),
    'keccakf1600.h': ('mlkem/src/fips202/keccakf1600.h', '88c06d4c546f46920a65001bcfad8cabb6173fb01ae071e02412c46043bdf54f',
        '3cdf2a30fd4883a6f89aeb86a0fe0f614f6067fddf45951f40c7509813e7c905', [
            (7, 7, '2aa302d878de0fb0df64cb0d78fbea4ec6e50b00205c251cf62aaa16f2c6e11c',
             ()),
            (11, 11, 'ea61c09ee42622078b9165c7fe0ca1ed08ba382965c9515e895597f4c0cf0d48',
             ('MLK_KECCAK_WAY',)),
            (42, 90, '2150ed9a19d9ae325a5a35daa87823bbac4680dfd299ab812b2d23de48ea7510',
             ('mlk_keccakf1600x4_extract_bytes', 'mlk_keccakf1600x4_xor_bytes', 'mlk_keccakf1600x4_permute')),
        ], [
            (7, '#include "../common.h"', '#include "mlkem_native_config.h"'),
        ]),
}
MLKEM_LICENSE_SHA256 = "1c730e3c2cd4f70e058519ef3e910d8bdd4ed822ae2ce689f3c63d32fc52314b"

# The public API: defined unprefixed, exactly once (api.h).
ENTRY_POINTS = ("crypto_kem_dec", "crypto_kem_enc", "crypto_kem_keypair")
# Imports the KEM objects may have: libc clears, the caller's randombytes, and
# (SUPERCOP builds only) crypto_declassify.
ALLOWED_UNDEFINED = {"randombytes", "explicit_bzero", "__explicit_bzero_chk", "memset", "memcpy",
                     "__stack_chk_fail", "crypto_declassify", "_GLOBAL_OFFSET_TABLE_"}


def fail(message):
    print(f"release-check: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def manifest():
    entries = {}
    for line in (ROOT / "SOURCE-MANIFEST.sha256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        entries[name] = digest
    return entries


def check_tree():
    files = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file())
    for rel in files:
        parts = {part.lower() for part in Path(rel).parts}
        if parts & BANNED_PATH_PARTS:
            fail(f"banned path component in {rel}")
        if Path(rel).suffix.lower() in BANNED_SUFFIXES:
            fail(f"generated/result file in release: {rel}")
    listed = manifest()
    have = set(files) - {"SOURCE-MANIFEST.sha256"}
    if have != set(listed):
        fail(f"manifest differs from the tree: only in tree {sorted(have - set(listed))}, "
             f"only in manifest {sorted(set(listed) - have)}")
    req = ROOT / "kat/expected/PQCkemKAT_2624.req"
    rsp = ROOT / "kat/expected/PQCkemKAT_2624.rsp"
    if sha256(req.read_bytes()) != KAT_REQ_SHA256 or sha256(rsp.read_bytes()) != KAT_RSP_SHA256:
        fail("canonical KAT hash mismatch (the expected vectors are Official's)")
    print(f"release-check: pass ({len(files)} files)")


def check_keccak(upstream_root):
    removed = set()
    for name, (up, digest, trimmed_digest, removals, rewrites) in MLKEM.items():
        text = (ROOT / name).read_text()
        header = VENDOR_HEADER.format(path=up)
        if not text.startswith(header):
            fail(f"{name}: expected the vendored-file comment naming {up}")
        lines = text[len(header):].split("\n")
        for number, up_line, flat_line in rewrites:
            if lines[number - 1] != flat_line or not flat_line.lstrip().startswith("#include"):
                fail(f"{name}:{number}: expected the recorded include rewrite")
            lines[number - 1] = up_line
        trimmed = "\n".join(lines)
        if sha256(trimmed.encode()) != trimmed_digest:
            fail(f"{name} is not upstream {up} minus its {len(removals)} recorded removals, "
                 f"modulo its {len(rewrites)} include rewrites")
        if upstream_root is not None:
            source = (upstream_root / up).read_bytes()
            if sha256(source) != digest:
                fail(f"{upstream_root / up} is not mlkem-native b3ba7b32773e657dd37f6f87bce82528459ad8a4's {up}")
            up_lines = source.decode().split("\n")
            keep = [True] * len(up_lines)
            for first, last, block_digest, _ in removals:
                block = "\n".join(up_lines[first - 1:last]) + "\n"
                if sha256(block.encode()) != block_digest:
                    fail(f"{up}: upstream lines {first}-{last} are not the recorded removal")
                keep[first - 1:last] = [False] * (last - first + 1)
            if "\n".join(ln for ln, k in zip(up_lines, keep) if k) != trimmed:
                fail(f"{name}: upstream minus the recorded removals differs")
        for *_, idents in removals:
            removed.update(idents)
    token = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    for path in sorted(ROOT.iterdir()):
        if path.suffix in CODE_SUFFIXES:
            used = removed & set(token.findall(path.read_text()))
            if used:
                fail(f"{path.name} uses removed mlkem-native identifiers {sorted(used)}")
    if sha256((ROOT / "LICENSE.mlkem-native").read_bytes()) != MLKEM_LICENSE_SHA256:
        fail("LICENSE.mlkem-native differs from upstream LICENSE")
    siblings = []
    for other in ("NTRU+768", "NTRU+864", "NTRU+1152"):
        sib = ROOT.parent / other
        if sib.resolve() == ROOT or not sib.is_dir():
            continue
        for name in list(MLKEM) + ["LICENSE.mlkem-native"]:
            if (sib / name).read_bytes() != (ROOT / name).read_bytes():
                fail(f"{name} differs from ../{other}/{name}")
        siblings.append(other)
    ranges = sum(len(r[3]) for r in MLKEM.values())
    print(f"keccak-check: {len(MLKEM)} vendored files = mlkem-native b3ba7b32773e657dd37f6f87bce82528459ad8a4 minus {ranges} "
          f"recorded removals ({len(removed)} identifiers, none used) plus include rewrites"
          f"{'; removals checked against ' + str(upstream_root) if upstream_root else ''}; "
          f"identical in {', '.join(siblings) or 'no sibling present'}")


def check_objects(objects):
    bad, undefined, entry = [], set(), {}
    count = 0
    for obj in objects:
        out = subprocess.check_output(["nm", "-P", obj], text=True)
        for line in out.splitlines():
            fields = line.split()
            if len(fields) < 2:
                continue
            name, kind = fields[0], fields[1]
            if kind == "U":
                undefined.add(name)
            elif kind.isupper() and kind not in "N":
                if name in ENTRY_POINTS:
                    entry.setdefault(name, []).append(Path(obj).name)
                    continue
                count += 1
                if not name.startswith(PREFIX):
                    bad.append(f"{Path(obj).name}:{name}")
    if bad:
        fail(f"global symbols neither a NIST entry point nor {PREFIX}*: {bad}")
    wrong = {e: entry.get(e, []) for e in ENTRY_POINTS if len(entry.get(e, [])) != 1}
    if wrong:
        fail(f"each entry point must be defined exactly once: {wrong}")
    extra = sorted(u for u in undefined if u not in ALLOWED_UNDEFINED and not u.startswith(PREFIX))
    if extra:
        fail(f"unexpected imports: {extra}")
    where = sorted({o for e in ENTRY_POINTS for o in entry[e]})
    print(f"symbols-check: {len(ENTRY_POINTS) + count} global definitions: "
          f"{', '.join(ENTRY_POINTS)} ({', '.join(where)}) and {count} x {PREFIX}*; imports "
          f"{sorted(u for u in undefined if not u.startswith(PREFIX))}")


ap = argparse.ArgumentParser()
ap.add_argument("--keccak", action="store_true")
ap.add_argument("--upstream", type=Path, help="with --keccak: an mlkem-native checkout at b3ba7b32773e657dd37f6f87bce82528459ad8a4")
ap.add_argument("--objects", nargs="+")
args = ap.parse_args()
if args.keccak:
    check_keccak(args.upstream)
elif args.objects:
    check_objects(args.objects)
else:
    check_tree()

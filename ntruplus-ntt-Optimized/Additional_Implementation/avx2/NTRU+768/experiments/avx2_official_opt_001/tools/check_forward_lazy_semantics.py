#!/usr/bin/env python3
"""Untimed Official-consumer differential for terminal-Barrett-free states.

This does not build an optimized Forward. It derives both representations
from the stage-checked scalar model and feeds them to unchanged Official
BaseInv, BaseMul, add/sub and serializer machine code.
"""

import argparse
import ctypes
import hashlib
import json
import random
import subprocess
import tempfile
from pathlib import Path

from prove_forward_lanes import R, Replay, load_zetas

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream/supercop-avx2"
OUTPUT = ROOT / "results/officialopt-forward-lazy-consumer-differential-20260921.json"
Q = 3457


class Poly:
    def __init__(self, values=None):
        self.backing = ctypes.create_string_buffer(1536 + 31)
        self.address = (ctypes.addressof(self.backing) + 31) & ~31
        self.words = (ctypes.c_int16 * 768).from_address(self.address)
        self.words[:] = values if values is not None else [0] * 768

    def residues(self):
        return [value % Q for value in self.words]


class Bytes:
    def __init__(self):
        self.backing = ctypes.create_string_buffer(1152 + 31)
        self.address = (ctypes.addressof(self.backing) + 31) & ~31
        self.words = (ctypes.c_uint8 * 1152).from_address(self.address)

    def value(self):
        return bytes(self.words)


def build(supercop_root, temp):
    library = Path(temp) / "consumers.so"
    wrapper = Path(temp) / "baseinv-export.c"
    wrapper.write_text('#include "poly.h"\n'
                       '__attribute__((visibility("default"))) '
                       'int officialopt_test_baseinv(poly *r, const poly *a) '
                       '{ return poly_baseinv(r, a); }\n')
    sources = ("poly.c", "consts.c", "baseinv.s", "basemul.s",
               "pack.s", "add.s")
    subprocess.run([
        "cc", "-O3", "-mavx2", "-fPIC", "-shared",
        "-I" + str(UPSTREAM), "-I" + str(supercop_root / "cryptoint"),
        "-I" + str(supercop_root / "include"),
        "-o", str(library), *(str(UPSTREAM / src) for src in sources),
        str(ROOT / "tests/support/crypto_declassify.c"), str(wrapper)
    ], check=True, capture_output=True)
    dll = ctypes.CDLL(str(library))
    dll.officialopt_test_baseinv.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    dll.officialopt_test_baseinv.restype = ctypes.c_int
    dll.poly_basemul.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                 ctypes.c_void_p]
    dll.poly_add.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                             ctypes.c_void_p]
    dll.poly_sub.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                             ctypes.c_void_p]
    dll.poly_tobytes.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    return dll, hashlib.sha256(library.read_bytes()).hexdigest()


def forward_pair(values, zetas):
    replay = Replay([R(x, x) for x in values], zetas).run()
    raw = [x.lo for vec in replay.pre_barrett for x in vec]
    reduced = [x.lo for vec in replay.mem for x in vec]
    if any((a - b) % Q for a, b in zip(raw, reduced)):
        raise ValueError("Forward terminal reducer changed residue")
    return Poly(raw), Poly(reduced)


def packed(dll, poly):
    output = Bytes()
    dll.poly_tobytes(output.address, poly.address)
    return output.value()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--supercop-root", required=True, type=Path)
    parser.add_argument("--cases", type=int, default=100)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing overwrite: {args.output}")
    if not (args.supercop_root / "cryptoint/crypto_int16.h").exists():
        raise SystemExit("invalid SUPERCOP root")
    zetas = load_zetas()
    rng = random.Random(0x768B4A77E77)
    with tempfile.TemporaryDirectory(prefix="officialopt-lazy-consumer-") as temp:
        dll, elf_sha = build(args.supercop_root, temp)
        counts = {"keygen_baseinv": 0, "encap_muladd_hash_ct": 0,
                  "decap_recovered_r": 0, "keygen_noninvertible": 0,
                  "targeted_zero_representative": 0}
        zero, q_representative = Poly(), Poly([Q] * 768)
        out_zero, out_q = Poly(), Poly()
        status_zero = dll.officialopt_test_baseinv(out_zero.address, zero.address)
        status_q = dll.officialopt_test_baseinv(out_q.address, q_representative.address)
        if status_zero != 1 or status_q != 1 or out_zero.residues() != out_q.residues():
            raise ValueError("BaseInv failed targeted zero-residue representative")
        counts["targeted_zero_representative"] = 1
        for _ in range(args.cases):
            for name in ("f", "g"):
                coeff = [rng.choice((-3, 0, 3)) for _ in range(768)]
                if name == "f":
                    coeff[0] = rng.choice((-2, 1, 4))
                raw, reduced = forward_pair(coeff, zetas)
                inv_raw, inv_reduced = Poly(), Poly()
                status_raw = dll.officialopt_test_baseinv(inv_raw.address, raw.address)
                status_reduced = dll.officialopt_test_baseinv(inv_reduced.address, reduced.address)
                if status_raw != status_reduced or inv_raw.residues() != inv_reduced.residues():
                    raise ValueError(f"BaseInv status/residue mismatch on {name}")
                if status_raw:
                    counts["keygen_noninvertible"] += 1
                counts["keygen_baseinv"] += 1

            r_coeff = [rng.choice((-1, 0, 1)) for _ in range(768)]
            m_coeff = [rng.choice((-1, 0, 1)) for _ in range(768)]
            r_raw, r_reduced = forward_pair(r_coeff, zetas)
            m_raw, m_reduced = forward_pair(m_coeff, zetas)
            h = Poly([rng.randrange(Q) for _ in range(768)])
            c_raw, c_reduced = Poly(), Poly()
            dll.poly_basemul(c_raw.address, h.address, r_raw.address)
            dll.poly_basemul(c_reduced.address, h.address, r_reduced.address)
            # Official separate add-m path, with disjoint buffers.
            dll.poly_add(c_raw.address, c_raw.address, m_raw.address)
            dll.poly_add(c_reduced.address, c_reduced.address, m_reduced.address)
            if (c_raw.residues() != c_reduced.residues() or
                    packed(dll, c_raw) != packed(dll, c_reduced) or
                    packed(dll, r_raw) != packed(dll, r_reduced)):
                raise ValueError("Encap arithmetic/hash/ciphertext mismatch")
            counts["encap_muladd_hash_ct"] += 1

            message = [rng.randint(-2, 2) for _ in range(768)]
            msg_raw, msg_reduced = forward_pair(message, zetas)
            ct = Poly([rng.randrange(Q) for _ in range(768)])
            hinv = Poly([rng.randrange(Q) for _ in range(768)])
            delta_raw, delta_reduced = Poly(), Poly()
            dll.poly_sub(delta_raw.address, ct.address, msg_raw.address)
            dll.poly_sub(delta_reduced.address, ct.address, msg_reduced.address)
            recovered_raw, recovered_reduced = Poly(), Poly()
            dll.poly_basemul(recovered_raw.address, delta_raw.address, hinv.address)
            dll.poly_basemul(recovered_reduced.address, delta_reduced.address, hinv.address)
            if (recovered_raw.residues() != recovered_reduced.residues() or
                    packed(dll, recovered_raw) != packed(dll, recovered_reduced)):
                raise ValueError("Decap recovered-r mismatch")
            counts["decap_recovered_r"] += 1
    args.output.write_text(json.dumps({
        "class": "untimed Official consumer differential, not full KEM/KAT",
        "cases": counts, "linked_consumer_elf_sha256": elf_sha,
        "forward_model_source_sha256": hashlib.sha256(
            (ROOT / "tools/prove_forward_lanes.py").read_bytes()).hexdigest(),
        "supercop_version_file": (args.supercop_root / "version").read_text().strip(),
        "result": "status/residue/wire bytes equal in tested cases"
    }, indent=2) + "\n")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()

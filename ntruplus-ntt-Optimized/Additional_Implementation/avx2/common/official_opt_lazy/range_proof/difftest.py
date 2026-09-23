"""Emulator (concrete/wrap mode) vs real assembled kernels.

Ported from the Phase-0 audit (difftest.py).  Validates the emulator on
exactly the code the proof replays: Official poly_ntt, the generated lazy
Forward, poly_basemul and poly_baseinv_1 (the lazy output's consumers).
"""
import ctypes
import random

from common import CFG, BASE_A, BASE_B, BASE_C, BASE_D, aligned_poly, emu, lib
from avx2emu import Val


def emu_run(fname, entry, polys, out_base, out_len):
    e = emu(fname, wrap_mode=True)
    regs = {}
    for reg, base, vals in polys:
        e.set_poly(base, [Val(v, v) for v in vals])
        regs[reg] = base
    e.run(entry, regs)
    return [v.lo for v in e.get_poly(out_base, out_len)]


def check(trials, seed):
    n = CFG["n"]
    rng = random.Random(seed)
    L = lib()
    lazy_fn = getattr(L, CFG["lazy_name"])
    counts = {"poly_ntt": 0, CFG["lazy_name"]: 0, "poly_basemul": 0, "poly_baseinv_1": 0}
    for t in range(trials):
        x = [rng.randint(-3, 4) for _ in range(n)]
        for fname, entry, fn in (("ntt.s", "poly_ntt", L.poly_ntt),
                                 ("LAZY", CFG["lazy_name"], lazy_fn)):
            b, arr, addr = aligned_poly(n, x)
            fn(ctypes.c_void_p(addr))
            got = emu_run(fname, entry, [("rdi", BASE_A, x)], BASE_A, n)
            assert list(arr) == got, (entry, t)
            counts[entry] += 1
        a1 = [rng.randint(-32768, 32767) for _ in range(n)]
        a2 = [rng.randint(-32768, 32767) for _ in range(n)]
        ba, aa, pa = aligned_poly(n, a1)
        bb, ab, pb = aligned_poly(n, a2)
        br, ar, pr = aligned_poly(n, [0] * n)
        L.poly_basemul(ctypes.c_void_p(pr), ctypes.c_void_p(pa), ctypes.c_void_p(pb))
        got = emu_run("basemul.s", "poly_basemul",
                      [("rdi", BASE_A, [0] * n), ("rsi", BASE_B, a1), ("rdx", BASE_C, a2)],
                      BASE_A, n)
        assert list(ar) == got, ("poly_basemul", t)
        counts["poly_basemul"] += 1
        ba, aa, pa = aligned_poly(n, a1)
        br, ar, pr = aligned_poly(n, [0] * n)
        bd, ad, pd = aligned_poly(18 * 16, [0] * (18 * 16))
        L.poly_baseinv_1(ctypes.c_void_p(pr), ctypes.c_void_p(pd), ctypes.c_void_p(pa))
        e = emu("baseinv.s", wrap_mode=True)
        e.set_poly(BASE_A, [Val(0, 0)] * n)
        e.set_poly(BASE_D, [Val(0, 0)] * (18 * 16))
        e.set_poly(BASE_C, [Val(v, v) for v in a1])
        e.run("poly_baseinv_1", {"rdi": BASE_A, "rsi": BASE_D, "rdx": BASE_C})
        assert list(ar) == [v.lo for v in e.get_poly(BASE_A, n)], ("baseinv r", t)
        assert list(ad) == [v.lo for v in e.get_poly(BASE_D, 18 * 16)], ("baseinv den", t)
        counts["poly_baseinv_1"] += 1
    return counts

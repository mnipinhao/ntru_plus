"""Shared loaders for the lazy-Forward range proof (NTRU+768/864/1152).

Ported from the Phase-0 read-only reduction audit.  Instead of the pristine
SUPERCOP tree it reads the experiment's imported upstream copy and the
generated candidate ASM; build products go to the experiment build dir.
Call configure() once before anything else.
"""
import ctypes
import hashlib
import re
import subprocess
from pathlib import Path

import avx2emu
from avx2emu import Emu, wrap, Q

HERE = Path(__file__).resolve().parent
CFG = {}


def configure(n, experiment, build):
    experiment = Path(experiment).resolve()
    build = Path(build).resolve()
    build.mkdir(parents=True, exist_ok=True)
    CFG.update(n=n, experiment=experiment, build=build,
               upstream=experiment / "upstream/supercop-avx2",
               lazy_name=f"ntruplus{n}_officialopt_ntt_caller_lazy")
    CFG["lazy_asm"] = experiment / f"asm/{CFG['lazy_name']}.s"
    images = build / "images.so"
    subprocess.run(["cc", "-O2", "-shared", "-fPIC", "-o", str(images), str(HERE / "images.c")],
                   check=True)
    avx2emu.set_images_lib(images)
    return CFG


def src(name):
    if name == "LAZY":
        return CFG["lazy_asm"]
    return CFG["upstream"] / name


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_consts():
    text = src("consts.c").read_text()
    defs = dict(re.findall(r"#define\s+(\w+)\s+(-?\d+)\b", text))
    defs = {k: int(v) for k, v in defs.items()}
    defs["NTRUPLUS_Q"] = Q
    defs["V"] = ((1 << 15) + Q // 2) // Q
    defs["V2"] = ((1 << 15) + 1) // 3
    tables = {}
    for name in ("zetas", "zetas_inv"):
        m = re.search(rf"const int16_t {name}\[(\d+)\][^=]*=\s*\{{(.*?)\}};", text, re.S)
        vals = [int(x) for x in re.findall(r"-?\d+", m.group(2))]
        assert len(vals) == int(m.group(1)), name
        tables[name] = vals
    rip = {}
    for name, expr in re.findall(r"const int16_t (_16x\w+)\[16\][^=]*=\s*FILL_16\(([^)]*)\)", text):
        expr = expr.strip()
        if expr in defs:
            val = defs[expr]
        elif expr == "NTRUPLUS_Q - 1":
            val = Q - 1
        else:
            try:
                val = int(expr, 0)
            except ValueError:
                continue   # masks / LOW not used by NTT kernels
        rip[name] = [wrap(val)] * 16
    return tables["zetas"], tables["zetas_inv"], rip


def emu(fname, **kw):
    z, zi, rip = load_consts()
    return Emu(str(src(fname)), z, zi, rip, **kw)


BASE_A, BASE_B, BASE_C, BASE_D = 0x10000, 0x20000, 0x30000, 0x40000

_lib = None


def lib():
    """Real assembled kernels: Official ntt/basemul/baseinv + generated lazy ASM."""
    global _lib
    if _lib is None:
        out = CFG["build"] / "kernels.so"
        files = [str(src(f)) for f in ("ntt.s", "basemul.s", "baseinv.s", "consts.c")]
        subprocess.run(["cc", "-O1", "-mavx2", "-shared", "-fPIC", "-I", str(CFG["upstream"]),
                        "-o", str(out)] + files + [str(CFG["lazy_asm"])], check=True)
        _lib = ctypes.CDLL(str(out))
    return _lib


def aligned_poly(n, values):
    buf = ctypes.create_string_buffer(2 * n + 64)
    addr = (ctypes.addressof(buf) + 31) & ~31
    arr = (ctypes.c_int16 * n).from_address(addr)
    for i, v in enumerate(values):
        arr[i] = v
    return buf, arr, addr

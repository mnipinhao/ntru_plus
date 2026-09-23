#!/usr/bin/env python3
"""Lane-granular AVX2 interval emulator for the NTRU+ Official .s kernels.

Copied from the Phase-0 read-only reduction audit; only the images.so loading
changed (built into the experiment build dir by common.configure()).

Parses the pinned SUPERCOP AT&T assembly directly and executes it with
per-16-bit-lane values.  Two modes:
  * interval mode: every lane is an integer interval; add/sub/shift are
    checked for signed-word overflow (recorded as failures, with .s line);
  * concrete mode (wrap=True, singleton lanes): bit-exact execution, used for
    differential testing against the real assembled code.

Multiplications are tracked symbolically so that the standard idioms are
recognised and bounded tightly:
  signed Montgomery by constant  vpmullw(x,c*qinv); vpmulhw(x,c); vpmulhw(q,lo); vpsubw
       -> exact image by exhaustive enumeration of x over its interval;
  signed Montgomery data*data    vpmullw(a,qinv); vpmullw(b,a'); vpmulhw(a,b); ...
       -> envelope [(Pmin-32767q)/2^16, (Pmax+32768q)/2^16];
  rounding Barrett               vpmulhrsw(x,v); vpmullw(.,q); vpsubw(x,.)
       -> exact image by enumeration;
  raw low product (forward level 0) -> exact product if it provably fits.
Any other use of a low product as an integer is flagged.
"""
import re
from functools import lru_cache

Q = 3457
QINV = 12929
V = ((1 << 15) + Q // 2) // Q   # 9
WMIN, WMAX = -32768, 32767


def wrap(x):
    return ((int(x) + 32768) & 0xFFFF) - 32768


class Val:
    __slots__ = ("lo", "hi", "const", "lvl")

    def __init__(self, lo, hi, const=False, lvl=None):
        self.lo, self.hi, self.const, self.lvl = int(lo), int(hi), const, lvl

    def single(self):
        return self.lo == self.hi


class LO:   # vpmullw result (low 16 bits of product)
    __slots__ = ("a", "b")

    def __init__(self, a, b):
        self.a, self.b = a, b


class HI:   # vpmulhw result
    __slots__ = ("a", "b")

    def __init__(self, a, b):
        self.a, self.b = a, b


class HQ:   # vpmulhw(q, LO)
    __slots__ = ("lo",)

    def __init__(self, lo):
        self.lo = lo


class RS:   # vpmulhrsw(x, v)
    __slots__ = ("x",)

    def __init__(self, x):
        self.x = x


class RSQ:  # vpmullw(RS(x), q)
    __slots__ = ("x",)

    def __init__(self, x):
        self.x = x


ZERO = Val(0, 0, True)


import ctypes as _ct
_IMG = None   # images.c compiled by common.configure(); see set_images_lib


def set_images_lib(path):
    global _IMG
    _IMG = _ct.CDLL(str(path))


@lru_cache(maxsize=None)
def mont_const_image(lo, hi, c):
    a, b = _ct.c_int(), _ct.c_int()
    _IMG.mont_image(lo, hi, c, _ct.byref(a), _ct.byref(b))
    return a.value, b.value


@lru_cache(maxsize=None)
def barrett_image(lo, hi):
    a, b = _ct.c_int(), _ct.c_int()
    _IMG.barrett_image(lo, hi, _ct.byref(a), _ct.byref(b))
    return a.value, b.value


def mont_const_image_py(lo, hi, c):
    cq = wrap(c * QINV)
    mn, mx = 1 << 30, -(1 << 30)
    for x in range(lo, hi + 1):
        m = ((x * cq + 32768) & 0xFFFF) - 32768
        r = ((x * c) >> 16) - ((m * Q) >> 16)
        if r < mn: mn = r
        if r > mx: mx = r
    return mn, mx


def barrett_image_py(lo, hi):
    rs = [x - Q * ((x * V + (1 << 14)) >> 15) for x in range(lo, hi + 1)]
    return min(rs), max(rs)


def mont_exact(a, b):
    m = wrap(a * wrap(b * QINV))
    return ((a * b) >> 16) - ((m * Q) >> 16)


def prod_range(a, b):
    c = (a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi)
    return min(c), max(c)


class Emu:
    def __init__(self, path, zetas, zetas_inv, rip_consts, wrap_mode=False,
                 skip_barrett_lines=()):
        self.path = path
        self.wrap_mode = wrap_mode
        self.skip = set(skip_barrett_lines)
        self.prog, self.labels, self.section = self.parse(path)
        self.mem = {}
        self.regs = {}
        self.ymm = [[ZERO] * 16 for _ in range(16)]
        self.failures = []
        self.stats = {}        # line -> [minlo, maxhi, kind]
        self.counts = {}       # line -> dynamic execution count
        self.cur = "input"
        self.entering = {}     # level -> [minlo, maxhi] of data values created in an earlier level
        self.syms = {}
        base = 0x100000
        for name, arr in (("zetas", zetas), ("zetas_inv", zetas_inv)):
            self.syms[name] = base
            for i, v in enumerate(arr):
                self.mem[base + 2 * i] = Val(v, v, True)
            base += 0x10000
        for name, arr in rip_consts.items():
            self.syms[name] = base
            for i, v in enumerate(arr):
                self.mem[base + 2 * i] = Val(v, v, True)
            base += 0x100

    # ------------------------------------------------------------ parsing
    @staticmethod
    def parse(path):
        prog, labels, section = [], {}, {}
        cur = "entry"
        sub = ""
        for ln, raw in enumerate(open(path), 1):
            line = raw.strip()
            m = re.match(r"#\s*(level\s*\d+)", line, re.I)
            if m:
                cur = m.group(1).replace(" ", "")
                sub = ""
                continue
            m = re.match(r"#\s*([a-z][a-z0-9 ]*)", line, re.I)
            if m:
                sub = m.group(1).strip()
                continue
            code = line.split("#", 1)[0].strip()
            if not code or code.startswith("."):
                continue
            if code.endswith(":"):
                labels[code[:-1]] = len(prog)
                if code[:-1].startswith("_looptop_start_") or code[:-1].startswith("_looptop_j_"):
                    pass
                continue
            op, _, rest = code.partition(" ")
            ops = [o.strip() for o in re.split(r",(?![^(]*\))", rest) if o.strip()]
            prog.append((ln, op, ops))
            section[ln] = (cur, sub)
        return prog, labels, section

    # ------------------------------------------------------------ memory
    def addr(self, operand):
        m = re.match(r"(-?\w*)\((%\w+)\)", operand)
        off, reg = m.group(1), m.group(2)[1:]
        if reg == "rip":
            return self.syms[off]
        return self.regs[reg] + (int(off) if off else 0)

    def load(self, operand, n=16):
        a = self.addr(operand)
        try:
            return [self.mem[a + 2 * i] for i in range(n)]
        except KeyError:
            raise RuntimeError(f"load from unmapped memory {operand} @ {a:#x}")

    def store(self, operand, lanes):
        a = self.addr(operand)
        for i, v in enumerate(lanes):
            self.mem[a + 2 * i] = self.as_val(v, None)

    def src(self, operand):
        if operand.startswith("%ymm"):
            return self.ymm[int(operand[4:])]
        return self.load(operand)

    # ------------------------------------------------------------ values
    def fail(self, ln, what, lo, hi):
        self.failures.append((ln, what, lo, hi))

    def mk(self, lo, hi, ln, what, const=False):
        if self.wrap_mode:
            assert lo == hi
            return Val(wrap(lo), wrap(lo), const)
        if lo < WMIN or hi > WMAX:
            self.fail(ln, what, lo, hi)
            lo, hi = max(lo, WMIN), min(hi, WMAX)
        return Val(lo, hi, const)

    def touch(self, x):
        if x.const or x.lvl == self.cur:
            return
        e = self.entering.setdefault(self.cur, [x.lo, x.hi])
        e[0], e[1] = min(e[0], x.lo), max(e[1], x.hi)

    def as_val(self, x, ln):
        if isinstance(x, Val):
            if ln is not None:
                self.touch(x)
            return x
        if isinstance(x, LO):
            a, b = self.as_val(x.a, ln), self.as_val(x.b, ln)
            if a.single() and b.single():
                v = wrap(a.lo * b.lo)
                return Val(v, v, a.const and b.const)
            if a.single() or b.single():
                p0, p1 = prod_range(a, b)
                if WMIN <= p0 and p1 <= WMAX:
                    self.note(ln, p0, p1, "raw_product")
                    return Val(p0, p1, lvl=self.cur)
            if ln is not None:
                self.fail(ln, "low product used as integer", WMIN, WMAX)
            return Val(WMIN, WMAX)
        if isinstance(x, HI):
            a, b = self.as_val(x.a, ln), self.as_val(x.b, ln)
            p0, p1 = prod_range(a, b)
            return Val(p0 >> 16, p1 >> 16)
        if isinstance(x, (HQ, RS, RSQ)):
            # concrete fallback
            if isinstance(x, RS):
                v = self.as_val(x.x, ln)
                if v.single():
                    r = (v.lo * V + (1 << 14)) >> 15
                    return Val(r, r)
                return Val((v.lo * V + (1 << 14)) >> 15, (v.hi * V + (1 << 14)) >> 15)
            if isinstance(x, RSQ):
                v = self.as_val(RS(x.x), ln)
                if v.single():
                    r = wrap(v.lo * Q)
                    return Val(r, r)
            if isinstance(x, HQ):
                lo = self.as_val(x.lo, ln)
                if lo.single():
                    r = (lo.lo * Q) >> 16
                    return Val(r, r)
            if ln is not None:
                self.fail(ln, f"unmatched {type(x).__name__} used as integer", WMIN, WMAX)
            return Val(WMIN, WMAX)
        raise TypeError(x)

    def note(self, ln, lo, hi, kind):
        if ln is None:
            return
        s = self.stats.get(ln)
        if s is None:
            self.stats[ln] = [lo, hi, kind]
        else:
            s[0] = min(s[0], lo)
            s[1] = max(s[1], hi)

    @staticmethod
    def is_q(x):
        return isinstance(x, Val) and x.single() and x.lo == Q

    @staticmethod
    def is_const(x, value=None):
        return isinstance(x, Val) and x.single() and (value is None or x.lo == value)

    def mullo(self, a, b, ln):
        if isinstance(a, RS) and self.is_q(b):
            return RSQ(a.x)
        if isinstance(b, RS) and self.is_q(a):
            return RSQ(b.x)
        return LO(a, b)

    def mulhi(self, a, b, ln):
        if self.is_q(a) and isinstance(b, LO):
            return HQ(b)
        if self.is_q(b) and isinstance(a, LO):
            return HQ(a)
        return HI(a, b)

    def mulhrs(self, a, b, ln):
        if self.is_const(b, V) and b.const:
            return RS(a)
        if self.is_const(a, V) and a.const:
            return RS(b)
        raise RuntimeError(f"line {ln}: vpmulhrsw with unexpected constant")

    def montgomery(self, hi, hq, ln):
        L = hq.lo
        hops = [hi.a, hi.b]
        lops = [L.a, L.b]
        # const case: data object shared by LO and HI, other operands constants
        for d in lops:
            if any(d is h for h in hops):
                cq = lops[1] if lops[0] is d else lops[0]
                c = hops[1] if hops[0] is d else hops[0]
                if isinstance(cq, Val) and isinstance(c, Val) and cq.single() and c.single() \
                        and cq.const and c.const:
                    if wrap(c.lo * QINV) != cq.lo:
                        raise RuntimeError(f"line {ln}: Montgomery companion mismatch {c.lo},{cq.lo}")
                    dv = self.as_val(d, ln)
                    if dv.single():
                        r = mont_exact(dv.lo, c.lo)
                        return Val(r, r), "mont_const"
                    lo, hi_ = mont_const_image(dv.lo, dv.hi, c.lo)
                    return Val(lo, hi_), "mont_const"
                # data case: cq = LO(z, QINV) with z the other HI operand
                if isinstance(cq, LO):
                    zs = [cq.a, cq.b]
                    for z in zs:
                        other = zs[1] if zs[0] is z else zs[0]
                        if z is c and self.is_const(other, QINV):
                            av, bv = self.as_val(d, ln), self.as_val(c, ln)
                            if av.single() and bv.single():
                                r = mont_exact(av.lo, bv.lo)
                                return Val(r, r), "mont_data"
                            p0, p1 = prod_range(av, bv)
                            lo = -((-(p0 - 32767 * Q)) // 65536)
                            hi_ = (p1 + 32768 * Q) // 65536
                            return Val(lo, hi_), "mont_data"
        raise RuntimeError(f"line {ln}: unrecognised Montgomery pattern")

    def stamp(self, v):
        if not v.const:
            v.lvl = self.cur
        return v

    def lane_sub(self, a, b, ln):
        return self.stamp(self._lane_sub(a, b, ln))

    def _lane_sub(self, a, b, ln):
        # a - b
        if isinstance(a, HI) and isinstance(b, HQ):
            v, kind = self.montgomery(a, b, ln)
            self.note(ln, v.lo, v.hi, kind)
            return v
        if isinstance(a, HQ) and isinstance(b, HI):   # negated Montgomery
            v, kind = self.montgomery(b, a, ln)
            v = Val(-v.hi, -v.lo)
            self.note(ln, v.lo, v.hi, kind + "_neg")
            return v
        if isinstance(b, RSQ) and b.x is a:
            av = self.as_val(a, ln)
            if ln in self.skip:
                self.note(ln, av.lo, av.hi, "barrett_skipped")
                return av
            if av.single():
                r = av.lo - Q * ((av.lo * V + (1 << 14)) >> 15)
                v = Val(r, r)
            else:
                v = Val(*barrett_image(av.lo, av.hi))
            self.note(ln, av.lo, av.hi, "barrett_in")
            self.stats.setdefault(("bout", ln), [v.lo, v.hi, "barrett_out"])
            s = self.stats[("bout", ln)]
            s[0], s[1] = min(s[0], v.lo), max(s[1], v.hi)
            return v
        av, bv = self.as_val(a, ln), self.as_val(b, ln)
        v = self.mk(av.lo - bv.hi, av.hi - bv.lo, ln, "sub", av.const and bv.const)
        self.note(ln, v.lo, v.hi, "sub")
        return v

    def lane_add(self, a, b, ln):
        return self.stamp(self._lane_add(a, b, ln))

    def _lane_add(self, a, b, ln):
        av, bv = self.as_val(a, ln), self.as_val(b, ln)
        v = self.mk(av.lo + bv.lo, av.hi + bv.hi, ln, "add", av.const and bv.const)
        self.note(ln, v.lo, v.hi, "add")
        return v

    # ------------------------------------------------------------ execution
    def run(self, entry, regs, max_steps=10_000_000):
        self.regs = dict(regs)
        pc = self.labels[entry]
        steps = 0
        flags = None
        while True:
            steps += 1
            if steps > max_steps:
                raise RuntimeError("step limit")
            ln, op, ops = self.prog[pc]
            pc += 1
            self.cur = self.section[ln][0]
            self.counts[ln] = self.counts.get(ln, 0) + 1
            if op == "ret":
                return
            if op in ("lea",):
                if "(%rip)" in ops[0]:
                    self.regs[ops[1][1:]] = self.addr(ops[0])
                else:
                    self.regs[ops[1][1:]] = self.addr(ops[0])
            elif op in ("add", "sub"):
                s = int(ops[0][1:]) if ops[0].startswith("$") else self.regs[ops[0][1:]]
                d = ops[1][1:]
                self.regs[d] = self.regs[d] + s if op == "add" else self.regs[d] - s
            elif op == "mov":
                self.regs[ops[1][1:]] = self.regs[ops[0][1:]]
            elif op == "cmp":
                flags = (self.regs[ops[1][1:]], self.regs[ops[0][1:]])
            elif op == "jb":
                if flags[0] < flags[1]:
                    pc = self.labels[ops[0]]
            elif op in ("vmovdqa", "vmovdqu"):
                if ops[1].startswith("%ymm"):
                    self.ymm[int(ops[1][4:])] = list(self.src(ops[0]))
                else:
                    self.store(ops[1], self.ymm[int(ops[0][4:])])
            elif op == "vpbroadcastd":
                two = self.load(ops[0], 2)
                self.ymm[int(ops[1][4:])] = two * 8
            else:
                self.vec(op, ops, ln)

    def vec(self, op, ops, ln):
        d = int(ops[-1][4:])
        if op in ("vpmullw", "vpmulhw", "vpmulhrsw", "vpaddw", "vpsubw"):
            b, a = self.src(ops[0]), self.src(ops[1])   # AT&T: op b, a, dst => a (op) b
            f = {"vpmullw": self.mullo, "vpmulhw": self.mulhi, "vpmulhrsw": self.mulhrs,
                 "vpaddw": self.lane_add, "vpsubw": self.lane_sub}[op]
            self.ymm[d] = [f(a[i], b[i], ln) for i in range(16)]
            return
        if op in ("vpsllq", "vpsrlq", "vpslld", "vpsrld", "vpsllw"):
            k = int(ops[0][1:])
            s = self.src(ops[1])
            out = [ZERO] * 16
            if op == "vpsllw":
                assert k == 1
                for i in range(16):
                    v = self.as_val(s[i], ln)
                    if v.const:
                        out[i] = Val(wrap(2 * v.lo), wrap(2 * v.hi), True)
                    else:
                        out[i] = self.stamp(self.mk(2 * v.lo, 2 * v.hi, ln, "shl1"))
                        self.note(ln, out[i].lo, out[i].hi, "shl1")
            else:
                width = 4 if op[-1] == "q" else 2
                sh = k // 16
                for g in range(0, 16, width):
                    for j in range(width):
                        if op in ("vpsllq", "vpslld"):
                            if j - sh >= 0:
                                out[g + j] = s[g + j - sh]
                        else:
                            if j + sh < width:
                                out[g + j] = s[g + j + sh]
            self.ymm[d] = out
            return
        if op in ("vpblendw", "vpblendd"):
            imm = int(ops[0][1:], 0)
            s2, s1 = self.src(ops[1]), self.src(ops[2])
            out = []
            for i in range(16):
                bit = (imm >> (i % 8)) & 1 if op == "vpblendw" else (imm >> (i // 2)) & 1
                out.append(s2[i] if bit else s1[i])
            self.ymm[d] = out
            return
        if op in ("vpunpcklqdq", "vpunpckhqdq"):
            s2, s1 = self.src(ops[0]), self.src(ops[1])
            o = 0 if op == "vpunpcklqdq" else 4
            out = []
            for h in (0, 8):
                out += s1[h + o:h + o + 4] + s2[h + o:h + o + 4]
            self.ymm[d] = out
            return
        if op == "vperm2i128":
            imm = int(ops[0][1:], 0)
            s2, s1 = self.src(ops[1]), self.src(ops[2])
            halves = [s1[0:8], s1[8:16], s2[0:8], s2[8:16]]
            self.ymm[d] = list(halves[imm & 3]) + list(halves[(imm >> 4) & 3])
            return
        raise RuntimeError(f"line {ln}: unsupported {op}")

    # ------------------------------------------------------------ helpers
    def set_poly(self, base, lanes):
        for i, v in enumerate(lanes):
            self.mem[base + 2 * i] = v

    def get_poly(self, base, n):
        return [self.as_val(self.mem[base + 2 * i], None) for i in range(n)]

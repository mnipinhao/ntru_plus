"""Exact symbolic AVX2 dataflow executor for the NTRU+ forward-NTT kernels.

Every 16-bit lane holds an interned *form*: a linear combination, with
coefficients in Z/2^16, of atoms.  Atoms are the input words, the constant 1,
signed high products `vpmulhw(x, y)` of two forms, and low products
`vpmullw(x, y)` of two non-constant forms.  The instruction semantics used
are exact:

  vpaddw / vpsubw             ring addition / subtraction in Z/2^16
  vpmullw x, c (c constant)   ring multiplication by c in Z/2^16 (linear)
  vpmulhw x, y                the atom HI(x, y) (commutative; exact product
                              >> 16 when both operands are constants)
  vpmulhrsw x, y              the atom RS(x, y) (rounded high product)
  vpsllw $k                   ring multiplication by 2^k
  shuffles / blends / shifts  exact lane moves (whole-word shifts only)

so two programs whose output lanes have the same interned form compute the
same int16 function of the input words for *every* input (bit for bit).  The
converse is not needed.  Used by generate_forward_ht.py (twiddle derivation
and the output-equality proof against the caller-lazy Forward) and by the
linked audit.  No host state is touched.
"""
import re

MASK = 0xFFFF


def s16(x):
    return ((x + 0x8000) & MASK) - 0x8000


class Forms:
    """Hash-consed linear forms over atoms (coefficients mod 2^16)."""

    def __init__(self):
        self.atom_ids, self.atoms = {}, []
        self.form_ids, self.forms = {}, []
        self.ONE = self._atom(("ONE",))
        self.ZERO = self._form({})

    def _atom(self, key):
        i = self.atom_ids.get(key)
        if i is None:
            i = self.atom_ids[key] = len(self.atoms)
            self.atoms.append(key)
        return i

    def _form(self, items):
        key = tuple(sorted((a, c & MASK) for a, c in items.items() if c & MASK))
        i = self.form_ids.get(key)
        if i is None:
            i = self.form_ids[key] = len(self.forms)
            self.forms.append(dict(key))
        return i

    def const(self, v):
        return self._form({self.ONE: v})

    def input(self, w):
        return self._form({self._atom(("IN", w)): 1})

    def value(self, f):
        """int16 value of a constant form, else None."""
        d = self.forms[f]
        if not d:
            return 0
        if len(d) == 1 and self.ONE in d:
            return s16(d[self.ONE])
        return None

    def add(self, f, g, sign=1):
        d = dict(self.forms[f])
        for a, c in self.forms[g].items():
            d[a] = d.get(a, 0) + sign * c
        return self._form(d)

    def sub(self, f, g):
        return self.add(f, g, -1)

    def scale(self, f, c):
        return self._form({a: v * c for a, v in self.forms[f].items()})

    def mullo(self, f, g):
        cf, cg = self.value(f), self.value(g)
        if cf is not None:
            return self.scale(g, cf)
        if cg is not None:
            return self.scale(f, cg)
        return self._form({self._atom(("LO", min(f, g), max(f, g))): 1})

    def mulhi(self, f, g):
        cf, cg = self.value(f), self.value(g)
        if cf is not None and cg is not None:
            return self.const((cf * cg) >> 16)
        return self._form({self._atom(("HI", min(f, g), max(f, g))): 1})

    def mulhrs(self, f, g):
        """vpmulhrsw: round(x*y / 2^15); an atom unless both are constants."""
        cf, cg = self.value(f), self.value(g)
        if cf is not None and cg is not None:
            return self.const((cf * cg + (1 << 14)) >> 15)
        return self._form({self._atom(("RS", min(f, g), max(f, g))): 1})

    def evaluate(self, fids, inputs):
        """Concrete int16 values of forms for input words `inputs` (word -> int);
        validates the symbolic semantics against the real machine."""
        memo_f, memo_a = {}, {}

        def atom(a):
            if a in memo_a:
                return memo_a[a]
            k = self.atoms[a]
            if k[0] == "ONE":
                v = 1
            elif k[0] == "IN":
                v = s16(inputs[k[1]])
            elif k[0] == "HI":
                v = s16((form(k[1]) * form(k[2])) >> 16)
            elif k[0] == "RS":
                v = s16((form(k[1]) * form(k[2]) + (1 << 14)) >> 15)
            else:
                v = s16(form(k[1]) * form(k[2]))
            memo_a[a] = v
            return v

        def form(f):
            if f not in memo_f:
                memo_f[f] = s16(sum(c * atom(a) for a, c in self.forms[f].items()))
            return memo_f[f]

        import sys
        sys.setrecursionlimit(100000)
        return [form(f) for f in fids]


def parse_asm(text):
    """(program, labels, data): program = [(line_no, op, [operands])],
    labels = name -> program index, data = label -> [int16 words] for the
    `.short` directives that follow a label."""
    prog, labels, data = [], {}, {}
    cur_data = None
    for ln, raw in enumerate(text.splitlines(), 1):
        code = raw.split("#", 1)[0].strip()
        if not code:
            continue
        if code.endswith(":"):
            name = code[:-1]
            labels[name] = len(prog)
            cur_data = name
            continue
        if code.startswith(".short"):
            if cur_data is None:
                raise ValueError(f"line {ln}: .short without a label")
            data.setdefault(cur_data, []).extend(
                s16(int(v, 0)) for v in code[len(".short"):].split(","))
            continue
        if code.startswith("."):
            if not code.startswith((".p2align", ".section", ".text", ".size", ".type",
                                    ".global", ".globl", ".ifndef", ".endif")):
                raise ValueError(f"line {ln}: unexpected directive {code}")
            if code.startswith((".section", ".text")):
                cur_data = None
            continue
        cur_data = None
        op, _, rest = code.partition(" ")
        ops = [o.strip() for o in re.split(r",(?![^(]*\))", rest) if o.strip()]
        prog.append((ln, op, ops))
    return prog, labels, data


class SymExec:
    """Executes one entry of a parsed .s on symbolic lanes.

    symbols: name -> list of int16 words (RIP-relative constant tables).
    Memory is word addressed (byte address -> form id)."""

    POLY = 0x10000

    def __init__(self, forms, text, symbols):
        self.F = forms
        self.prog, self.labels, data = parse_asm(text)
        self.mem, self.syms = {}, {}
        base = 0x1000000
        for name, words in list(symbols.items()) + list(data.items()):
            if name in self.syms:
                raise ValueError(f"duplicate symbol {name}")
            self.syms[name] = base
            for i, v in enumerate(words):
                self.mem[base + 2 * i] = forms.const(v)
            base += 0x100000
        self.ymm = [[forms.ZERO] * 16 for _ in range(16)]
        self.regs = {}
        self.hooks = {}          # program index -> callable(self), run before that instruction
        self.on_mul = None       # callable(op, data_lanes, const_lanes) for vpmullw/vpmulhw by a constant
        self.stores = set()
        self.census = {}

    # ---------------------------------------------------------------- memory
    def addr(self, operand):
        m = re.fullmatch(r"(-?\w*)\((%\w+)\)", operand)
        if not m:
            raise ValueError(f"unsupported memory operand {operand}")
        off, reg = m.group(1), m.group(2)[1:]
        if reg == "rip":
            return self.syms[off]
        if reg == "rsp":
            raise ValueError("stack access")
        return self.regs[reg] + (int(off, 0) if off else 0)

    def load(self, operand, n=16):
        a = self.addr(operand)
        try:
            return [self.mem[a + 2 * i] for i in range(n)]
        except KeyError:
            raise ValueError(f"load from unmapped memory {operand} @ {a:#x}") from None

    def src(self, operand):
        if operand.startswith("%ymm"):
            return self.ymm[int(operand[4:])]
        return self.load(operand)

    # ---------------------------------------------------------------- run
    def run(self, entry, regs, max_steps=2_000_000):
        self.regs = dict(regs)
        pc = self.labels[entry]
        flags = None
        for _ in range(max_steps):
            hook = self.hooks.get(pc)
            if hook:
                hook(self)
            ln, op, ops = self.prog[pc]
            pc += 1
            self.census[op] = self.census.get(op, 0) + 1
            if op == "ret":
                return
            if op == "lea":
                self.regs[ops[1][1:]] = self.addr(ops[0])
            elif op in ("add", "sub"):
                s = int(ops[0][1:], 0) if ops[0].startswith("$") else self.regs[ops[0][1:]]
                d = ops[1][1:]
                self.regs[d] = self.regs[d] + s if op == "add" else self.regs[d] - s
            elif op == "cmp":
                flags = (self.regs[ops[1][1:]], self.regs[ops[0][1:]])
            elif op == "jb":
                if flags[0] < flags[1]:
                    pc = self.labels[ops[0]]
            elif op in ("vmovdqa", "vmovdqu"):
                if ops[1].startswith("%ymm"):
                    self.ymm[int(ops[1][4:])] = list(self.src(ops[0]))
                else:
                    a = self.addr(ops[1])
                    if a % 32 and op == "vmovdqa":
                        raise ValueError(f"line {ln}: misaligned vmovdqa store")
                    for i, v in enumerate(self.ymm[int(ops[0][4:])]):
                        self.mem[a + 2 * i] = v
                        self.stores.add(a + 2 * i)
            elif op == "vpbroadcastd":
                self.ymm[int(ops[1][4:])] = self.load(ops[0], 2) * 8
            else:
                self.vec(ln, op, ops)
        raise RuntimeError("step limit")

    def vec(self, ln, op, ops):
        F = self.F
        d = int(ops[-1][4:])
        if op == "vpsllw":
            k = int(ops[0][1:], 0)
            self.ymm[d] = [F.scale(x, 1 << k) for x in self.src(ops[1])]
            return
        if op in ("vpaddw", "vpsubw", "vpmullw", "vpmulhw", "vpmulhrsw"):
            b, a = self.src(ops[0]), self.src(ops[1])
            if op in ("vpmullw", "vpmulhw") and self.on_mul:
                cb = [F.value(x) for x in b]
                ca = [F.value(x) for x in a]
                if all(c is not None for c in cb) and not all(c is not None for c in ca):
                    self.on_mul(op, a, cb)
                elif all(c is not None for c in ca) and not all(c is not None for c in cb):
                    self.on_mul(op, b, ca)
            f = {"vpaddw": F.add, "vpsubw": F.sub, "vpmullw": F.mullo, "vpmulhw": F.mulhi,
                 "vpmulhrsw": F.mulhrs}[op]
            self.ymm[d] = [f(a[i], b[i]) for i in range(16)]
        elif op in ("vpsllq", "vpsrlq"):
            k = int(ops[0][1:], 0)
            if k % 16:
                raise ValueError(f"line {ln}: non-word shift")
            sh, s = k // 16, self.src(ops[1])
            out = [F.ZERO] * 16
            for g in range(0, 16, 4):
                for j in range(4):
                    k2 = j - sh if op == "vpsllq" else j + sh
                    if 0 <= k2 < 4:
                        out[g + j] = s[g + k2]
            self.ymm[d] = out
        elif op in ("vpblendw", "vpblendd"):
            imm = int(ops[0][1:], 0)
            b, a = self.src(ops[1]), self.src(ops[2])
            self.ymm[d] = [b[i] if (imm >> ((i % 8) if op == "vpblendw" else (i // 2))) & 1
                           else a[i] for i in range(16)]
        elif op in ("vpunpcklwd", "vpunpckhwd", "vpunpckldq", "vpunpckhdq",
                    "vpunpcklqdq", "vpunpckhqdq"):
            b, a = self.src(ops[0]), self.src(ops[1])
            w = {"wd": 1, "dq": 2, "qdq": 4}[op[8:]]
            hi = op[7] == "h"
            out = []
            for h in (0, 8):
                base = h + (4 if hi else 0)
                for i in range(0, 4, w):
                    out += a[base + i:base + i + w] + b[base + i:base + i + w]
            self.ymm[d] = out
        elif op == "vperm2i128":
            imm = int(ops[0][1:], 0)
            if imm & 0x88:
                raise ValueError(f"line {ln}: zeroing vperm2i128")
            b, a = self.src(ops[1]), self.src(ops[2])
            halves = [a[0:8], a[8:16], b[0:8], b[8:16]]
            self.ymm[d] = list(halves[imm & 3]) + list(halves[(imm >> 4) & 3])
        else:
            raise ValueError(f"line {ln}: unsupported {op}")


def parse_consts(text):
    """Official consts.c -> {symbol: [int16 words]} for zetas, zetas_inv and
    every FILL_16 constant whose argument is a #define or integer."""
    defs = {k: int(v, 0) for k, v in re.findall(r"#define\s+(\w+)\s+(0x[0-9a-fA-F]+|-?\d+)\s*$", text, re.M)}
    defs["V"] = ((1 << 15) + 3457 // 2) // 3457       # BARRETT_V(NTRUPLUS_Q)
    defs["V2"] = ((1 << 15) + 3 // 2) // 3             # BARRETT_V(3)
    defs["NTRUPLUS_Q"] = 3457
    syms = {}
    for name in ("zetas", "zetas_inv"):
        m = re.search(rf"const int16_t {name}\[(\d+)\][^=]*=\s*\{{(.*?)\}};", text, re.S)
        vals = [int(x) for x in re.findall(r"-?\d+", m.group(2))]
        if len(vals) != int(m.group(1)):
            raise ValueError(name)
        syms[name] = vals
    for name, expr in re.findall(r"const int16_t (_16x\w+)\[16\][^=]*=\s*FILL_16\(([^)]*)\)", text):
        expr = expr.strip()
        if expr == "NTRUPLUS_Q - 1":
            val = 3456
        elif expr in defs:
            val = defs[expr]
        else:
            continue
        syms[name] = [s16(val)] * 16
    return syms

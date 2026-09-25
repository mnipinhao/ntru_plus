"""Extension of common/official_opt_ht/tools/symexec.py (imported read-only, unchanged).

FormsX adds the unsigned high product atom HU(x, y) (vpmulhuw) to the hash-consed
linear forms; SymExecX executes, in addition to what SymExec knows:

  vpslld / vpsrld $16k        exact word moves inside each dword (Official invntt.s level 6)
  vpmulhuw x, y               the atom HU(x, y) (exact when both are constants)
  vpsllw $k                   ring multiplication by 2^k (inherited)
  gcc scalar prologue/loop    movl/movq/leaq/addq/subq/cmpq/andq/xorl, jne/jb,
                              vmovd r32 -> xmm + vpbroadcastd xmm -> ymm (constants only),
                              pushq/popq/leave/endbr64/vzeroupper
  base+index addressing       off(%base) and off(sym+%rip); no index registers
  stack                       %rsp/%rbp-relative loads/stores go to a separate, word
                              addressed stack memory (recorded in .stack_offsets); every
                              stack address is a fixed offset from the entry %rsp
                              (after the 32-byte realignment) -- no data-dependent address

so a gcc-compiled kernel can be compared, word for word, with a reference program
built directly with FormsX.  Nothing in the host is touched.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "official_opt_ht/tools"))
from symexec import MASK, Forms, SymExec, parse_asm, s16  # noqa: E402,F401


def u16(x):
    return x & MASK


class FormsX(Forms):
    def mulhu(self, f, g):
        cf, cg = self.value(f), self.value(g)
        if cf is not None and cg is not None:
            return self.const((u16(cf) * u16(cg)) >> 16)
        return self._form({self._atom(("HU", min(f, g), max(f, g))): 1})

    def evaluate(self, fids, inputs):
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
            elif k[0] == "HU":
                v = s16((u16(form(k[1])) * u16(form(k[2]))) >> 16)
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

        sys.setrecursionlimit(100000)
        return [form(f) for f in fids]


def filter_gcc(text):
    """Blank the gcc-only directives symexec.parse_asm does not accept (line numbers kept)."""
    out = []
    for raw in text.splitlines():
        code = raw.split("#", 1)[0].strip()
        out.append("" if code.startswith((".align", ".cfi", ".file", ".ident")) else raw.replace("\t", " "))
    return "\n".join(out) + "\n"


class SymExecX(SymExec):
    STACK = 0x7000000

    def __init__(self, forms, text, symbols):
        super().__init__(forms, filter_gcc(text), symbols)
        self.stack = {}
        self.stack_offsets = set()
        self.gpr_const = {}          # 32/64-bit scalar constants (movl $imm)
        self.xmm_const = {}          # xmm register -> 32-bit constant (vmovd)

    # ------------------------------------------------------------ memory
    def addr(self, operand):
        m = re.fullmatch(r"(-?[\w.]*)(?:\+([\w.]+))?\((%\w+)\)", operand)
        if not m:
            raise ValueError(f"unsupported memory operand {operand}")
        off, sym, reg = m.group(1), m.group(2), m.group(3)[1:]
        if reg == "rip":
            if sym:                        # e.g. 1920+zetas(%rip)
                return self.syms[sym] + int(off, 0)
            return self.syms[off]
        if sym:
            raise ValueError(f"unsupported operand {operand}")
        base = self.regs[reg]
        a = base + (int(off, 0) if off else 0)
        if reg in ("rsp", "rbp"):
            self.stack_offsets.add(a - self.STACK)
        return a

    def is_stack(self, a):
        return self.STACK - 0x10000 <= a < self.STACK + 0x10000

    def load(self, operand, n=16):
        a = self.addr(operand)
        if self.is_stack(a):
            try:
                return [self.stack[a + 2 * i] for i in range(n)]
            except KeyError:
                raise ValueError(f"load from uninitialised stack {operand}") from None
        return super().load(operand, n)

    def store16(self, operand, lanes, op):
        a = self.addr(operand)
        if a % 32 and op == "vmovdqa":
            raise ValueError(f"misaligned vmovdqa store {operand}")
        if self.is_stack(a):
            for i, v in enumerate(lanes):
                self.stack[a + 2 * i] = v
            return
        for i, v in enumerate(lanes):
            self.mem[a + 2 * i] = v
            self.stores.add(a + 2 * i)

    # ------------------------------------------------------------ run
    def run(self, entry, regs, max_steps=2_000_000):
        F = self.F
        self.regs = dict(regs)
        self.regs["rsp"] = self.STACK
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
            if op in ("endbr64", "vzeroupper"):
                continue
            if op in ("pushq", "push"):
                self.regs["rsp"] -= 8
                continue
            if op in ("popq", "pop"):
                self.regs["rsp"] += 8
                continue
            if op == "leave":
                self.regs["rsp"] = self.regs["rbp"] + 8
                continue
            if op in ("lea", "leaq"):
                self.regs[ops[1][1:]] = self.addr(ops[0])
            elif op in ("add", "sub", "addq", "subq"):
                s = int(ops[0][1:], 0) if ops[0].startswith("$") else self.regs[ops[0][1:]]
                d = ops[1][1:]
                self.regs[d] = self.regs[d] + s if op.startswith("add") else self.regs[d] - s
            elif op in ("andq",):
                d = ops[1][1:]
                self.regs[d] = self.regs[d] & int(ops[0][1:], 0)
            elif op in ("movq", "mov"):
                if ops[0].startswith("$"):
                    self.regs[ops[1][1:]] = int(ops[0][1:], 0)
                else:
                    self.regs[ops[1][1:]] = self.regs[ops[0][1:]]
            elif op in ("movl",):
                if not ops[0].startswith("$"):
                    raise ValueError(f"line {ln}: movl from register")
                self.gpr_const[ops[1][1:]] = int(ops[0][1:], 0) & 0xFFFFFFFF
            elif op in ("xorl",):
                if ops[0] != ops[1]:
                    raise ValueError(f"line {ln}: xorl of two registers")
                self.gpr_const[ops[1][1:]] = 0
            elif op == "vmovd":
                self.xmm_const[ops[1]] = self.gpr_const[ops[0][1:]]
            elif op == "vpbroadcastd" and ops[0].startswith("%xmm"):
                v = self.xmm_const[ops[0]]
                self.ymm[int(ops[1][4:])] = [F.const(s16(v & MASK)), F.const(s16(v >> 16))] * 8
            elif op == "vpbroadcastw" and ops[0].startswith("%xmm"):
                v = self.xmm_const[ops[0]]
                self.ymm[int(ops[1][4:])] = [F.const(s16(v & MASK))] * 16
            elif op in ("cmp", "cmpq"):
                flags = (self.regs[ops[1][1:]], self.regs[ops[0][1:]])
            elif op == "jb":
                if flags[0] < flags[1]:
                    pc = self.labels[ops[0]]
            elif op == "jne":
                if flags[0] != flags[1]:
                    pc = self.labels[ops[0]]
            elif op in ("vmovdqa", "vmovdqu"):
                if ops[1].startswith("%ymm"):
                    self.ymm[int(ops[1][4:])] = list(self.src(ops[0]))
                else:
                    self.store16(ops[1], self.ymm[int(ops[0][4:])], op)
            elif op == "vpbroadcastd":
                self.ymm[int(ops[1][4:])] = self.load(ops[0], 2) * 8
            else:
                self.vec(ln, op, ops)
        raise RuntimeError("step limit")

    def vec(self, ln, op, ops):
        F = self.F
        d = int(ops[-1][4:])
        if op in ("vpslld", "vpsrld"):
            k = int(ops[0][1:], 0)
            if k != 16:
                raise ValueError(f"line {ln}: non-word dword shift")
            s = self.src(ops[1])
            out = [F.ZERO] * 16
            for g in range(0, 16, 2):
                if op == "vpslld":
                    out[g + 1] = s[g]
                else:
                    out[g] = s[g + 1]
            self.ymm[d] = out
            return
        if op == "vpmulhuw":
            b, a = self.src(ops[0]), self.src(ops[1])
            self.ymm[d] = [F.mulhu(a[i], b[i]) for i in range(16)]
            return
        if op in ("vpaddw", "vpsubw", "vpmullw", "vpmulhw", "vpmulhrsw") and len(ops) == 3 \
                and not ops[1].startswith("%ymm"):
            raise ValueError(f"line {ln}: memory operand in second position")
        super().vec(ln, op, ops)

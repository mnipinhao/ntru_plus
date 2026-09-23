"""P117: interval interpreter for the GT inverse, run on its disassembly.

Executes the expanded instruction stream with concrete integer registers and
control flow and per-lane intervals for the vector data.  Constants are read
from the object's own tables.  It proves that no add/sub leaves int16 for any
input with |x| <= B_IN, and reports the largest magnitude at every phase.

Multiplications are bounded with the exact error of each constant pair:
  fqmul   r = x*c - q*sqrdmulh(x,c'):  |r| <= q*M*|c'/2^15 - c/q| + q/2
  Barrett sqdmulh(x,19412), srshr #11, mls q: |r| <= 1729 for every int16 x
  mod 3   r - 3*sqrdmulh(r,10923): {-1,0,1} for |r| <= 1728
Anything the interpreter does not recognise is an error, not an assumption.

usage: range_interp.py OBJ SYMBOL B_IN [--drop-stage45-barrett]
"""
"""P125: interval interpreter over a linked executable (generalises P117's).

Executes the instruction stream from ENTRY with concrete integer registers and
control flow and per-lane intervals for vector data; constants are read from
the executable's own tables.  It proves that no add/sub leaves int16 for any
input with |x| <= B_IN and reports the largest magnitude per function.

ABI of the entry: x0 = out, x1 = in (the same address: decapsulation calls it
in place), x2 = caller scratch.

Multiplications are bounded with the exact error of each constant pair:
  fqmul   r = x*c - q*sqrdmulh(x,c'):  |r| <= q*M*|c'/2^15 - c/q| + q/2
  Barrett sqdmulh(x,19412), srshr #11, mls q: |r| <= 1729 for every int16 x
  mod 3   r - 3*sqrdmulh(r,10923): exhaustive over the input interval
Anything the interpreter does not recognise is an error, not an assumption.

usage: range_interp2.py EXE ENTRY N B_IN
"""
import re, subprocess, sys, bisect
from fractions import Fraction

Q = 3457
exe, sym, N, B_IN = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])

dis = subprocess.run(['objdump', '-d', '--no-show-raw-insn', exe], capture_output=True, text=True).stdout
raw = subprocess.run(['objdump', '-s', exe], capture_output=True, text=True).stdout
mem_bytes = {}
for l in raw.splitlines():
    m = re.match(r'\s*([0-9a-f]{4,}) ((?:[0-9a-f]{2,8} ){1,4})', l)
    if m:
        a = int(m.group(1), 16)
        for w in m.group(2).split():
            for i in range(0, len(w), 2):
                mem_bytes[a] = int(w[i:i+2], 16); a += 1

ins = {}; labels = {}
for l in dis.splitlines():
    m = re.match(r'^([0-9a-f]+) <(.+)>:', l)
    if m: labels[m.group(2)] = int(m.group(1), 16); continue
    m = re.match(r'\s*([0-9a-f]+):\s+(\S+)\s*(.*)', l)
    if m: ins[int(m.group(1), 16)] = (m.group(2), m.group(3).split(';')[0].split('//')[0].strip())
entry = labels.get(sym, labels.get("_" + sym))
fn_addr = sorted((a, n.lstrip('_')) for n, a in labels.items())
fn_keys = [a for a, _ in fn_addr]

def phase(pc):
    return fn_addr[bisect.bisect_right(fn_keys, pc) - 1][1]

nid = [0]
class V:
    __slots__ = ('lo', 'hi', 'id', 'tag')
    def __init__(s, lo, hi, tag=None):
        s.lo, s.hi, s.tag = lo, hi, tag; nid[0] += 1; s.id = nid[0]
    def m(s): return max(abs(s.lo), abs(s.hi))
def const(v): return V(v, v, ('c', v))
FULL = (-32768, 32767)

X = {}                       # integer registers (concrete)
VR = {i: [V(*FULL) for _ in range(8)] for i in range(32)}
MEM = {}                     # halfword address -> V
IO, SCRATCH, SP = 0x1000000, 0x3000000, 0x2000000
for i in range(N): MEM[IO + 2*i] = V(-B_IN, B_IN)
X.update(x0=IO, x1=IO, x2=SCRATCH, sp=SP, x30=0xdead)
CENTER_OK = Q + 1728          # exhaustive lemma: one correction suffices up to here
maxes = {}; errors = []; POISON_READS = set(); CENTER_IN = {}
def P(*vs): return any(v.tag and v.tag[0] == 'poison' for v in vs)
PV = lambda: V(*FULL, ('poison',))

def rd_mem(a):
    if a in MEM: return MEM[a]
    if a + 1 in mem_bytes and a in mem_bytes:
        v = mem_bytes[a] | mem_bytes[a+1] << 8
        return const(v - 65536 if v >= 32768 else v)
    if SCRATCH <= a < SCRATCH + 0x10000:          # never-written scratch: poison
        POISON_READS.add(a); return V(*FULL, ('poison',))
    errors.append(f'read of unknown memory {a:#x}'); return V(*FULL)

def xr(n):
    n = n.strip()
    if n in ('sp', 'wsp'): return 'sp'
    return 'x' + n[1:]
def xval(n):
    n = xr(n); return X.get(n, 0)
def addr(op):                      # "[x3, #0x18]" or "[x15]" or "[sp, #-0x10]!"
    m = re.match(r'\[(\w+)(?:, #(-?0x[0-9a-f]+|-?\d+))?\](!?)', op)
    b = xr(m.group(1)); off = int(m.group(2), 0) if m.group(2) else 0
    return b, off, m.group(3) == '!'

def lanes_of(r, arr):              # "v3" or "v3[1]" element
    m = re.match(r'v(\d+)(?:\[(\d+)\])?$', r.strip())
    return int(m.group(1)), (int(m.group(2)) if m.group(2) else None)

def post_index(args, b):           # "[x12], x14" or "[x1], #0x40" after the address operand
    if len(args) and args[-1][0] in 'x#' and not args[-1].startswith('['):
        t = args[-1]; X[b] += int(t.lstrip('#'), 0) if t.startswith('#') else xval(t)
def regs_list(txt):                # "{ v22, v23, v24 }" or "{ v0.8h - v3.8h }"
    m = re.match(r'\{\s*v(\d+)(?:\.\w+)?\s*-\s*v(\d+)', txt)
    if m: return list(range(int(m.group(1)), int(m.group(2)) + 1))
    return [int(x) for x in re.findall(r'v(\d+)', txt)]
def isvec(x): return isinstance(x, tuple) and x[0] == 'vec'
def ELEM(sz): return {'8h': 1, '4s': 2, '2d': 4, '16b': None}[sz]
def mod3_bound(D):
    outs = set()
    for r in range(D.lo, D.hi + 1):
        t = (2 * r * 10923 + (1 << 15)) >> 16                     # sqrdmulh
        outs.add(r - 3 * t)
    return min(outs), max(outs)

def note(pc, vs):
    vs = [v for v in vs if not P(v)]
    if not vs: return
    p = phase(pc); mx = max(v.m() for v in vs)
    maxes[p] = max(maxes.get(p, 0), mx)
    if mx > 32767: errors.append(f'{pc:#x} {phase(pc)}: |value| {mx} leaves int16')

def fq_bound(M, c, cp):
    d = abs(Fraction(cp, 1 << 15) - Fraction(c, Q))
    return int(Q * M * d + Fraction(Q, 2)) + 1

CUR = [None]
def _hook(t, v, tb):
    print(f'crash at {CUR[0][0]:#x} in {phase(CUR[0][0])}: {CUR[0][1]} {CUR[0][2]}  ({t.__name__}: {v})')
sys.excepthook = _hook
pc = entry; callstack = []; steps = 0; dropped = 0
flags = 0
while True:
    steps += 1
    if steps > 2000000: errors.append('runaway'); break
    op, a = ins[pc]; nxt = pc + 4; CUR[0] = (pc, op, a)
    args = [s.strip() for s in re.split(r',(?![^\[{]*[\]}])', a)] if a else []
    base = op.split('.')[0]; sz = op.split('.')[1] if '.' in op else ''
    # ---------- integer / control ----------
    if op in ('stp', 'ldp') and args[0][0] in 'xw' or op in ('stp', 'ldp') and args[0][0] == 'd':
        b, off, wb = addr(args[2]); ea = X[b] + off
        if op == 'ldp' and args[0][0] == 'x':
            pass
        if len(args) > 3:            # post-index
            X[b] += int(args[3].lstrip('#'), 0)
        elif wb: X[b] = ea
        if op == 'stp' and args[0][0] == 'x':
            MEM[('x', ea)] = X.get(xr(args[0]), 0); MEM[('x', ea + 8)] = X.get(xr(args[1]), 0)
        if op == 'ldp' and args[0][0] == 'x':
            X[xr(args[0])] = MEM.get(('x', ea), 0); X[xr(args[1])] = MEM.get(('x', ea + 8), 0)
    elif op == 'sub' and args[0] in ('sp',) or (op in ('add', 'sub') and args[0][0] in 'xws' and args[1][0] in 'xws'):
        s = xval(args[1]); t = int(args[2].lstrip('#'), 0) if args[2].startswith('#') else xval(args[2])
        if len(args) > 3:                                   # "#0x1, lsl #12"
            m = re.match(r'lsl #(\d+)$', args[3]); assert m, a; t <<= int(m.group(1))
        X[xr(args[0])] = s + t if op == 'add' else s - t
    elif op == 'subs':
        X[xr(args[0])] = xval(args[1]) - int(args[2].lstrip('#'), 0); flags = X[xr(args[0])]
    elif op == 'mov' and args[0][0] in 'xw':
        X[xr(args[0])] = int(args[1].lstrip('#'), 0) if args[1].startswith('#') else xval(args[1])
    elif op in ('adr', 'adrp'):
        X[xr(args[0])] = int(args[1].split()[0], 0)
    elif op in ('str', 'strh') and args[0][0] in 'xw' and isvec(X.get(xr(args[0]))):
        b, off, _ = addr(args[1]); lanes = X[xr(args[0])][1]
        n = 4 if args[0][0] == 'x' else (2 if op == 'str' else 1)
        for i in range(n): MEM[X[b] + off + 2*i] = lanes[i]
        post_index(args[2:], b)
    elif op == 'lsr' and isvec(X.get(xr(args[1]))) and args[2] == '#32':
        X[xr(args[0])] = ('vec', X[xr(args[1])][1][2:4] + [V(0, 0), V(0, 0)])
    elif op == 'str' and args[0][0] == 'x':
        b, off, _ = addr(args[1]); MEM[('x', X[b] + off)] = X.get(xr(args[0]), 0)
    elif op == 'ldr' and args[0][0] == 'x':
        b, off, _ = addr(args[1]); X[xr(args[0])] = MEM.get(('x', X[b] + off), 0)
    elif op == 'bl':
        callstack.append(nxt); nxt = int(args[0].split()[0], 0)
    elif op == 'b':
        nxt = int(args[0].split()[0], 0)
    elif op == 'b.ne':
        if flags != 0: nxt = int(args[0].split()[0], 0)
    elif op == 'ret':
        if not callstack: break
        nxt = callstack.pop()
    elif op == 'nop':
        pass
    # ---------- vector memory ----------
    elif op in ('ldr', 'str') and args[0][0] in 'qd':
        n = 8 if args[0][0] == 'q' else 4; r = int(args[0][1:])
        b, off, wb = addr(args[1]); ea = X[b] + off
        if op == 'ldr':
            VR[r] = [rd_mem(ea + 2*i) for i in range(n)] + ([V(0, 0)] * (8 - n))
        else:
            for i in range(n): MEM[ea + 2*i] = VR[r][i]
    elif op in ('stp', 'ldp') and args[0][0] == 'q':
        r0, r1 = int(args[0][1:]), int(args[1][1:]); b, off, wb = addr(args[2]); ea = X[b] + off
        for k, r in enumerate((r0, r1)):
            if op == 'ldp': VR[r] = [rd_mem(ea + 16*k + 2*i) for i in range(8)]
            else:
                for i in range(8): MEM[ea + 16*k + 2*i] = VR[r][i]
        if wb: X[b] = ea
        post_index(args[3:], b)
    elif op in ('st1.d', 'st1.h', 'st1.s') and '[' in args[0].split('}')[1]:
        m = re.match(r'\{\s*v(\d+)\s*\}\[(\d)\]', args[0]); r, e = int(m.group(1)), int(m.group(2))
        k = {'st1.d': 4, 'st1.s': 2, 'st1.h': 1}[op]; b, off, _ = addr(args[1])
        for i in range(k): MEM[X[b] + off + 2*i] = VR[r][k*e + i]
        post_index(args[2:], b)
    elif op in ('st1.8h', 'ld1.8h', 'st3.8h', 'st4.8h', 'ld3.8h', 'ld4.8h', 'st2.8h', 'ld2.8h'):
        rs = regs_list(args[0]); b, off, _ = addr(args[1]); ea = X[b] + off; n = len(rs)
        inter = op[2] != '1'
        for j, r in enumerate(rs):
            if op.startswith('ld'): VR[r] = [None] * 8
            for i in range(8):
                a_ = ea + 2 * (i * n + j if inter else 8 * j + i)
                if op.startswith('st'): MEM[a_] = VR[r][i]
                else: VR[r][i] = rd_mem(a_)
        post_index(args[2:], b)
    # ---------- vector arithmetic ----------
    elif base in ('add', 'sub') and sz == '8h':
        d, s, t = (int(x[1:]) for x in args)
        out = []
        for i in range(8):
            A, B = VR[s][i], VR[t][i]
            out.append(PV() if P(A, B) else V(A.lo + B.lo, A.hi + B.hi) if base == 'add' else V(A.lo - B.hi, A.hi - B.lo))
        VR[d] = out; note(pc, out)
    elif base == 'addp' and sz == '8h':
        d, s, t = (int(x[1:]) for x in args)
        src = VR[s] + VR[t]
        out = [PV() if P(src[2*i], src[2*i+1]) else V(src[2*i].lo + src[2*i+1].lo, src[2*i].hi + src[2*i+1].hi) for i in range(8)]
        VR[d] = out; note(pc, out)
    elif base == 'mov' and sz == '16b':
        VR[int(args[0][1:])] = list(VR[int(args[1][1:])])
    elif base == 'mov' and sz == 'd' and args[0][0] == 'x':     # mov.d x5, v21[0]
        s_, se = lanes_of(args[1], None); X[xr(args[0])] = ('vec', VR[s_][4*se:4*se+4])
    elif base == 'mov' and sz == 'd' and args[1][0] == 'x':     # mov.d v5[1], x6
        d, de = lanes_of(args[0], None); src = X[xr(args[1])]
        if not isvec(src): errors.append(f'{pc:#x} insert of non-vector GPR'); src = ('vec', [V(*FULL)] * 4)
        v = list(VR[d]); v[4*de:4*de+4] = src[1]; VR[d] = v
    elif base == 'mov' and sz == 'd':      # mov.d v3[1], v12[0]
        d, de = lanes_of(args[0], None); s, se = lanes_of(args[1], None)
        v = list(VR[d]); v[4*de:4*de+4] = VR[s][4*se:4*se+4]; VR[d] = v
    elif base == 'dup' and sz == '2d' and args[1][0] == 'x':
        src = X[xr(args[1])]
        if not isvec(src): errors.append(f'{pc:#x} dup of non-vector GPR'); src = ('vec', [V(*FULL)] * 4)
        VR[int(args[0][1:])] = src[1] + src[1]
    elif base in ('zip1', 'zip2', 'uzp1', 'uzp2', 'trn1', 'trn2') and sz in ('8h', '4s', '2d'):
        d, s, t = (int(x[1:]) for x in args); k = ELEM(sz); n = 8 // k
        A = [VR[s][i*k:(i+1)*k] for i in range(n)]; B = [VR[t][i*k:(i+1)*k] for i in range(n)]
        if base[:3] == 'zip':
            h = 0 if base == 'zip1' else n // 2
            R = [x for i in range(n // 2) for x in (A[h+i], B[h+i])]
        elif base[:3] == 'uzp':
            o = 0 if base == 'uzp1' else 1
            R = (A + B)[o::2]
        else:
            o = 0 if base == 'trn1' else 1
            R = [x for i in range(n // 2) for x in (A[2*i+o], B[2*i+o])]
        VR[d] = [v for e in R for v in e]
    elif base == 'cmgt' and sz == '8h':
        d, s, t = (int(x[1:]) for x in args); out = []
        for i in range(8):
            A, B = VR[s][i], VR[t][i]
            out.append(PV() if P(A, B) else const(-1) if A.lo > B.hi else const(0) if A.hi <= B.lo else V(-1, 0))
            for X_, K_ in ((A, B), (B, A)):             # q-centering compare against +-1728
                if K_.tag and K_.tag[0] == 'c' and abs(K_.lo) == 1728 and not P(X_):
                    CENTER_IN[phase(pc)] = max(CENTER_IN.get(phase(pc), 0), X_.m())
        VR[d] = out
    elif base == 'ext' and sz == '16b':
        d, s, t, k = args; d, s, t = int(d[1:]), int(s[1:]), int(t[1:]); k = int(k.lstrip('#'), 0) // 2
        VR[d] = (VR[s] + VR[t])[k:k+8]
    elif base == 'dup' and sz == '8h':
        v_ = X[xr(args[1])] & 0xffff; v_ = v_ - 65536 if v_ >= 32768 else v_       # low halfword, signed
        VR[int(args[0][1:])] = [const(v_) for _ in range(8)]
    elif base == 'movi':
        VR[int(args[0][1:])] = [const(int(args[1].lstrip('#'), 0)) for _ in range(8)]
    elif base in ('mul', 'sqrdmulh', 'sqdmulh') and sz == '8h':
        d = int(args[0][1:]); s = int(args[1][1:]); r, e = lanes_of(args[2], None)
        cs = [VR[r][e] if e is not None else VR[r][i] for i in range(8)]
        out = []
        for i in range(8):
            c = cs[i]
            if c.tag is None or c.tag[0] != 'c': errors.append(f'{pc:#x} non-constant multiplier'); c = const(0)
            out.append(PV() if P(VR[s][i]) else V(*FULL, (base, VR[s][i].id, VR[s][i].m(), c.lo)))
        VR[d] = out
    elif base == 'srshr' and sz == '8h':
        d, s, k = args; d, s = int(d[1:]), int(s[1:])
        out = []
        for i in range(8):
            t = VR[s][i].tag
            ok = t and t[0] == 'sqdmulh' and t[3] == 19412 and int(k.lstrip('#'), 0) == 11
            if not ok: errors.append(f'{pc:#x} srshr not in Barrett pattern')
            out.append(V(*FULL, ('bt', t[1] if t else None)))
        VR[d] = out
    elif base == 'mls' and sz == '8h':
        d = int(args[0][1:]); t = int(args[1][1:]); r, e = lanes_of(args[2], None)
        out = []
        for i in range(8):
            D, T = VR[d][i], VR[t][i]; qv = VR[r][e].lo if e is not None else VR[r][i].lo
            if P(D, T): out.append(PV())
            elif T.tag and T.tag[0] == 'bt' and qv == Q and T.tag[1] == D.id:
                b = 1728 if D.m() < 29385 else 1729
                out.append(V(-b, b))                           # Barrett, exhaustive over int16
            elif T.tag and T.tag[0] == 'sqrdmulh' and D.tag and D.tag[0] == 'mul' and qv == Q and T.tag[1] == D.tag[1]:
                bnd = fq_bound(D.tag[2], D.tag[3], T.tag[3]); out.append(V(-bnd, bnd))
            elif T.tag and T.tag[0] == 'sqrdmulh' and qv == Q and T.tag[1] == D.id:
                bnd = fq_bound(D.m(), 1, T.tag[3]); out.append(V(-bnd, bnd))   # fqmul by 1 (Barrett form)
            elif T.tag and T.tag[0] == 'sqrdmulh' and T.tag[3] == 10923 and qv == 3 and T.tag[1] == D.id:
                out.append(V(*mod3_bound(D)))
            else:
                errors.append(f'{pc:#x} mls pattern not recognised'); out.append(V(*FULL))
        VR[d] = out; note(pc, out)
    else:
        errors.append(f'{pc:#x} unhandled: {op} {a}')
    # optional: drop stage45 Barretts (skip the three instructions by turning mls into identity)
    pc = nxt

for p, v in sorted(maxes.items(), key=lambda z: fn_keys[[n for _, n in fn_addr].index(z[0])]):
    print(f'{p:32s} max |value| = {v}')
out = [MEM.get(IO + 2*i) for i in range(N)]
bad = [i for i, v in enumerate(out) if P(v)]
if bad: errors.append(f'{len(bad)} output coefficients depend on never-written scratch, first {bad[:8]}')
good = [v for v in out if not P(v)]
print('output range', min(v.lo for v in good), max(v.hi for v in good))
print(f'never-written scratch halfwords read: {len(POISON_READS)}' + (f' ({min(POISON_READS) - SCRATCH:#x}..{max(POISON_READS) - SCRATCH:#x})' if POISON_READS else ''))
for p_, v_ in sorted(CENTER_IN.items()):
    print(f'q-centering input {p_:32s} max |x| = {v_}' + ('' if v_ <= CENTER_OK else '  EXCEEDS'))
    if v_ > CENTER_OK: errors.append(f'{p_}: centering input {v_} > {CENTER_OK}, single correction is not enough')
print(f'input bound {B_IN}; steps {steps}; errors: {len(errors)}')
for e in errors[:25]: print('  ', e)
sys.exit(1 if errors else 0)

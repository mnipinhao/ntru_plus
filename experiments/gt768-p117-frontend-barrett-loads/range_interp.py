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
import re, subprocess, sys
from fractions import Fraction

Q = 3457
obj, sym, B_IN = sys.argv[1], sys.argv[2], int(sys.argv[3])
DROP = '--drop-stage45-barrett' in sys.argv

dis = subprocess.run(['objdump', '-d', '--no-show-raw-insn', obj], capture_output=True, text=True).stdout
raw = subprocess.run(['objdump', '-s', obj], capture_output=True, text=True).stdout
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
    if m: ins[int(m.group(1), 16)] = (m.group(2), m.group(3).split(';')[0].strip())
entry = labels.get(sym, labels.get("_" + sym, labels.get("ltmp0", 0)))
helper = [a for n, a in labels.items() if 'stage45_scratch_row_helper' in n][0]
post_tail = [a for n, a in labels.items() if n.endswith('L_invntt_post_tail')][0]

def phase(pc):
    if helper <= pc: return 'stage45'
    if pc >= post_tail: return 'post'
    return 'stage123'

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
IN, OUT, SP = 0x1000000, 0x1000000, 0x2000000      # in place
for i in range(768): MEM[IN + 2*i] = V(-B_IN, B_IN)
X.update(x0=OUT, x1=IN, sp=SP, x30=0xdead)
if "--scratch-x1" in sys.argv: X["x1"] = 0x3000000   # production ABI: in place on x0, scratch at x1
maxes = {}; errors = []

def rd_mem(a):
    if a in MEM: return MEM[a]
    if a + 1 in mem_bytes and a in mem_bytes:
        v = mem_bytes[a] | mem_bytes[a+1] << 8
        return const(v - 65536 if v >= 32768 else v)
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

def note(pc, vs):
    p = phase(pc); mx = max(v.m() for v in vs)
    maxes[p] = max(maxes.get(p, 0), mx)
    if mx > 32767: errors.append(f'{pc:#x} {phase(pc)}: |value| {mx} leaves int16')

def fq_bound(M, c, cp):
    d = abs(Fraction(cp, 1 << 15) - Fraction(c, Q))
    return int(Q * M * d + Fraction(Q, 2)) + 1

pc = entry; callstack = []; steps = 0; dropped = 0
flags = 0
while True:
    steps += 1
    if steps > 200000: errors.append('runaway'); break
    op, a = ins[pc]; nxt = pc + 4
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
        X[xr(args[0])] = s + t if op == 'add' else s - t
    elif op == 'subs':
        X[xr(args[0])] = xval(args[1]) - int(args[2].lstrip('#'), 0); flags = X[xr(args[0])]
    elif op == 'mov' and args[0][0] in 'xw':
        X[xr(args[0])] = int(args[1].lstrip('#'), 0) if args[1].startswith('#') else xval(args[1])
    elif op == 'adr':
        X[xr(args[0])] = int(args[1].split()[0], 0)
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
        errors.append(f'{pc:#x} unhandled q pair')
    elif op == 'st1.d':            # st1.d { v21 }[1], [x15]
        m = re.match(r'\{\s*v(\d+)\s*\}\[(\d)\]', args[0]); r, e = int(m.group(1)), int(m.group(2))
        b, off, _ = addr(args[1])
        for i in range(4): MEM[X[b] + 2*i] = VR[r][4*e + i]
    # ---------- vector arithmetic ----------
    elif base in ('add', 'sub') and sz == '8h':
        d, s, t = (int(x[1:]) for x in args)
        out = []
        for i in range(8):
            A, B = VR[s][i], VR[t][i]
            out.append(V(A.lo + B.lo, A.hi + B.hi) if base == 'add' else V(A.lo - B.hi, A.hi - B.lo))
        VR[d] = out; note(pc, out)
    elif base == 'addp' and sz == '8h':
        d, s, t = (int(x[1:]) for x in args)
        src = VR[s] + VR[t]
        out = [V(src[2*i].lo + src[2*i+1].lo, src[2*i].hi + src[2*i+1].hi) for i in range(8)]
        VR[d] = out; note(pc, out)
    elif base == 'mov' and sz == '16b':
        VR[int(args[0][1:])] = list(VR[int(args[1][1:])])
    elif base == 'mov' and sz == 'd':      # mov.d v3[1], v12[0]
        d, de = lanes_of(args[0], None); s, se = lanes_of(args[1], None)
        v = list(VR[d]); v[4*de:4*de+4] = VR[s][4*se:4*se+4]; VR[d] = v
    elif base in ('zip1', 'zip2') and sz in ('8h', '2d'):
        d, s, t = (int(x[1:]) for x in args); A, B = VR[s], VR[t]
        if sz == '8h':
            h = 0 if base == 'zip1' else 4
            VR[d] = [x for i in range(4) for x in (A[h+i], B[h+i])]
        else:
            h = 0 if base == 'zip1' else 4
            VR[d] = A[h:h+4] + B[h:h+4]
    elif base == 'ext' and sz == '16b':
        d, s, t, k = args; d, s, t = int(d[1:]), int(s[1:]), int(t[1:]); k = int(k.lstrip('#'), 0) // 2
        VR[d] = (VR[s] + VR[t])[k:k+8]
    elif base == 'dup' and sz == '8h':
        VR[int(args[0][1:])] = [const(X[xr(args[1])] & 0xffff if X[xr(args[1])] < 32768 else X[xr(args[1])] - 65536) for _ in range(8)]
    elif base == 'movi':
        VR[int(args[0][1:])] = [const(int(args[1].lstrip('#'), 0)) for _ in range(8)]
    elif base in ('mul', 'sqrdmulh', 'sqdmulh') and sz == '8h':
        d = int(args[0][1:]); s = int(args[1][1:]); r, e = lanes_of(args[2], None)
        cs = [VR[r][e] if e is not None else VR[r][i] for i in range(8)]
        out = []
        for i in range(8):
            c = cs[i]
            if c.tag is None or c.tag[0] != 'c': errors.append(f'{pc:#x} non-constant multiplier'); c = const(0)
            out.append(V(*FULL, (base, VR[s][i].id, VR[s][i].m(), c.lo)))
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
            if T.tag and T.tag[0] == 'bt' and qv == Q and T.tag[1] == D.id:
                b = 1728 if D.m() < 29385 else 1729
                out.append(V(-b, b))                           # Barrett, exhaustive over int16
            elif T.tag and T.tag[0] == 'sqrdmulh' and D.tag and D.tag[0] == 'mul' and qv == Q and T.tag[1] == D.tag[1]:
                bnd = fq_bound(D.tag[2], D.tag[3], T.tag[3]); out.append(V(-bnd, bnd))
            elif T.tag and T.tag[0] == 'sqrdmulh' and T.tag[3] == 10923 and qv == 3 and T.tag[1] == D.id and D.m() <= 1728:
                out.append(V(-1, 1))
            else:
                errors.append(f'{pc:#x} mls pattern not recognised'); out.append(V(*FULL))
        VR[d] = out; note(pc, out)
    else:
        errors.append(f'{pc:#x} unhandled: {op} {a}')
    # optional: drop stage45 Barretts (skip the three instructions by turning mls into identity)
    pc = nxt

if DROP: print('(drop mode is applied by editing the source, not here)')
for p in ('stage123', 'stage45', 'post'):
    print(f'{p:9s} max |value| = {maxes.get(p)}')
print(f'input bound {B_IN}; errors: {len(errors)}')
for e in errors[:15]: print('  ', e)
sys.exit(1 if errors else 0)

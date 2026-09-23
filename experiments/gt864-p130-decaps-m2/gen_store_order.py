"""P130: store order and store kind for NTRU+864's serializer (pack6.h).

Each lane of a group is a nine-byte run.  A run can be written with one
16-byte store when the seven bytes it writes past its run belong to a
neighbouring run that is written later (which then rewrites them):
  forward   vst1q at the run        -- garbage in the next run's head
  backward  vst1q ending at the run -- garbage in the previous run's tail
  store9    8-byte + 1-byte stores  -- otherwise
Any group order and lane order produce the same bytes, so both are searched
to maximise the single-store runs; the result is verified by simulating every
byte's last writer.  Appends the tables to pack6.h.
usage: gen_store_order.py PATH/TO/pack6.h
"""
import re, random, sys
path = sys.argv[1]; src = open(path).read()
assert 'pack6_order' not in src, 'tables already present'
off = [list(map(int, re.findall(r'\d+', l))) for l in re.findall(r'\{\s*(\d[\d,\s]*)\}', src.split('pack6_off')[1])]
off = [o for o in off if len(o) == 8][:18]
N = 1296

def plan(gorder, lorders):
    order = {}
    for g in gorder:
        for k in lorders[g]: order[off[g][k]] = len(order)
    mode = {}
    for o, t in order.items():
        nxt, prv = order.get(o + 9), order.get(o - 9)
        if nxt is not None and nxt > t and o + 16 <= N: mode[o] = 1
        elif prv is not None and prv > t and o - 7 >= 0: mode[o] = 2
        else: mode[o] = 0
    return order, mode

def score(go, lo): return sum(1 for m in plan(go, lo)[1].values() if m)

random.seed(20260923)
best = (0, None, None)
for trial in range(20000):
    go = list(range(18)); random.shuffle(go)
    lo = [random.sample(range(8), 8) for _ in range(18)] if trial % 2 else [list(range(8)) for _ in range(18)]
    sc = score(go, lo)
    if sc > best[0]: best = (sc, go, lo)
sc, go, lo = best
improved = True
while improved:
    improved = False
    for i in range(18):
        for j in range(i + 1, 18):
            g2 = go[:]; g2[i], g2[j] = g2[j], g2[i]
            if score(g2, lo) > sc: sc, go, improved = score(g2, lo), g2, True
    for g in range(18):
        for i in range(8):
            for j in range(i + 1, 8):
                l2 = [x[:] for x in lo]; l2[g][i], l2[g][j] = l2[g][j], l2[g][i]
                if score(go, l2) > sc: sc, lo, improved = score(go, l2), l2, True

order, mode = plan(go, lo)
# verify: simulate every write; each byte's last writer must be its own run
owner = [None] * N
for o, t in sorted(order.items(), key=lambda z: z[1]):
    lo_b, hi_b = {0: (o, o + 9), 1: (o, o + 16), 2: (o - 7, o + 9)}[mode[o]]
    assert 0 <= lo_b and hi_b <= N
    for b in range(lo_b, hi_b): owner[b] = o if o <= b < o + 9 else ('garbage', o)
assert all(owner[b] is not None and not isinstance(owner[b], tuple) and owner[b] <= b < owner[b] + 9 for b in range(N)), 'simulation'
kinds = [sum(1 for m in mode.values() if m == k) for k in (0, 1, 2)]
tables = f"""
/* P130 (gen_store_order.py): group processing order, lane order within each
 * group, and the store for each lane's run -- 0: 8-byte + 1-byte, 1: one
 * 16-byte store at the run (garbage in the next run, written later), 2: one
 * 16-byte store ending at the run (garbage in the previous run, written
 * later).  {kinds[1] + kinds[2]} of the 144 runs take one store; the final
 * bytes are verified by simulating every write. */
static const unsigned char pack6_order[PACK6_GROUPS] = {{{', '.join(map(str, go))}}};
static const unsigned char pack6_lane[PACK6_GROUPS][8] = {{
""" + ''.join(f"    {{{', '.join(map(str, lo[g]))}}},\n" for g in range(18)) + """};
static const unsigned char pack6_store[PACK6_GROUPS][8] = {
""" + ''.join(f"    {{{', '.join(str(mode[off[g][k]]) for k in range(8))}}},\n" for g in range(18)) + "};\n"
src = src.replace('\n#endif', tables + '\n#endif')
open(path, 'w').write(src)
print(f"single-store runs {kinds[1] + kinds[2]}/144 (forward {kinds[1]}, backward {kinds[2]}), store9 {kinds[0]}; verified")

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
usage: gen_store_order.py PATH/TO/pack6.h                 (NTRU+864, nine-byte runs)
       gen_store_order.py PATH/TO/codec_pairs.h 1152 --demote-backward
                                                            (NTRU+1152, twelve-byte blocks, P131)
  --forward-only     search for forward stores only (1152: 99 runs; costs M2 9 ns
                     of decapsulation, measured)
  --demote-backward  search with both kinds, then write the backward runs split
                     (1152: 66 forward runs; M2-neutral, measured -- the shipped one)
"""
import re, random, sys
path = sys.argv[1]; src = open(path).read()
SET = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 864
FWD_ONLY = '--forward-only' in sys.argv
DEMOTE = '--demote-backward' in sys.argv
R, N, ARR, PFX, NG = (9, 1296, 'pack6_off', 'pack6', 'PACK6_GROUPS') if SET == 864 else (12, 1728, 'pair_wire', 'pair', 'CODEC_PAIRS')
G = 16 - R                                        # bytes a 16-byte store writes past the run
assert f'{PFX}_order' not in src, 'tables already present'
off = [list(map(int, re.findall(r'\d+', l))) for l in re.findall(r'\{\s*(\d[\d,\s]*)\}', src.split(ARR)[1])]
off = [o for o in off if len(o) == 8][:18]

def plan(gorder, lorders):
    order = {}
    for g in gorder:
        for k in lorders[g]: order[off[g][k]] = len(order)
    mode = {}
    for o, t in order.items():
        nxt, prv = order.get(o + R), order.get(o - R)
        if nxt is not None and nxt > t and o + 16 <= N: mode[o] = 1
        elif not FWD_ONLY and prv is not None and prv > t and o - G >= 0: mode[o] = 2
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
if DEMOTE: mode = {o: (0 if m == 2 else m) for o, m in mode.items()}
# verify: simulate every write; each byte's last writer must be its own run
owner = [None] * N
for o, t in sorted(order.items(), key=lambda z: z[1]):
    lo_b, hi_b = {0: (o, o + R), 1: (o, o + 16), 2: (o - G, o + R)}[mode[o]]
    assert 0 <= lo_b and hi_b <= N
    for b in range(lo_b, hi_b): owner[b] = o if o <= b < o + R else ('garbage', o)
assert all(owner[b] is not None and not isinstance(owner[b], tuple) and owner[b] <= b < owner[b] + R for b in range(N)), 'simulation'
kinds = [sum(1 for m in mode.values() if m == k) for k in (0, 1, 2)]
tables = f"""
/* P130/P131 (gen_store_order.py): group processing order, lane order within
 * each group, and the store for each lane's {R}-byte run -- 0: split stores,
 * 1: one 16-byte store at the run (garbage in the next run, written later),
 * 2: one 16-byte store ending at the run (garbage in the previous run, written
 * later).  {kinds[1] + kinds[2]} of the 144 runs take one store; the final bytes
 * are verified by simulating every write. */
static const unsigned char {PFX}_order[{NG}] = {{{', '.join(map(str, go))}}};
static const unsigned char {PFX}_lane[{NG}][8] = {{
""" + ''.join(f"    {{{', '.join(map(str, lo[g]))}}},\n" for g in range(18)) + f"""}};
static const unsigned char {PFX}_store[{NG}][8] = {{
""" + ''.join(f"    {{{', '.join(str(mode[off[g][k]]) for k in range(8))}}},\n" for g in range(18)) + "};\n"
src = src.replace('\n#endif', tables + '\n#endif')
open(path, 'w').write(src)
print(f"single-store runs {kinds[1] + kinds[2]}/144 (forward {kinds[1]}, backward {kinds[2]}), split {kinds[0]}; verified")

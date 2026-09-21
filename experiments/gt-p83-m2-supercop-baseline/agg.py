import sys, collections
best = collections.defaultdict(lambda: [1e30]*3)
clk  = collections.defaultdict(lambda: [0,1e30])
acc  = collections.defaultdict(lambda: [0,0,0])
runs = collections.Counter()
for ln in open(sys.argv[1]):
    f = ln.split()
    if len(f) < 12 or f[1] != 'keygen': continue
    tag = f[0]; runs[tag] += 1
    v = [float(f[2]), float(f[4]), float(f[6])]
    for i in range(3): best[tag][i] = min(best[tag][i], v[i])
    clk[tag][0] = max(clk[tag][0], float(f[8])); clk[tag][1] = min(clk[tag][1], float(f[10]))
    for i,x in enumerate(f[12:15]): acc[tag][i] += int(x.split('/')[0])

order = ['off768_noce','off768_ce','gt768','off864_noce','off864_ce','gt864',
         'off1152_noce','off1152_ce','gt1152']
lbl = {'noce':'Official (portable Keccak)','ce':'Official + CE','gt':'GT'}
print(f"{'binary':<16}{'keygen':>9}{'encaps':>9}{'decaps':>9}{'clk_hi':>9}{'runs':>6}{'accepted':>16}")
for t in order:
    if t not in best: continue
    b = best[t]
    print(f"{t:<16}{b[0]:9.0f}{b[1]:9.0f}{b[2]:9.0f}{clk[t][0]:9.0f}{runs[t]:6d}"
          f"{acc[t][0]:6d}/{acc[t][1]}/{acc[t][2]:<6d}")
print()
for s in ('768','864','1152'):
    ce, gt = best.get(f'off{s}_ce'), best.get(f'gt{s}')
    po     = best.get(f'off{s}_noce')
    if not (ce and gt): continue
    print(f"NTRU+{s}  GT vs Official+CE : " + "  ".join(
        f"{n} {(g-c)/c*100:+.1f}%" for n,g,c in zip(('keygen','encaps','decaps'),gt,ce)))
    print(f"          GT vs Official(portable): " + "  ".join(
        f"{n} {(g-p)/p*100:+.1f}%" for n,g,p in zip(('keygen','encaps','decaps'),gt,po)))

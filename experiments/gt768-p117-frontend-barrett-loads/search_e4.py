"""P117: greedy removal of stage123 Barretts while range_interp.py still proves |x|<=2458 safe."""
import subprocess, itertools
S='/private/tmp/claude-501/-Users-chenpinhao-ntruplus/e4a12937-7b4e-47f6-8ea0-fccfc6c7a455/scratchpad'
def spec(sel): return ';'.join(f'{j}:'+','.join(str(g) for g in sorted(gs)) for j,gs in sorted(sel.items()))
def ok(sel):
    subprocess.run(['python3','make_e4.py',S+'/s.S',spec(sel)],check=True,capture_output=True)
    subprocess.run(['cc','-c',S+'/s.S','-o',S+'/s.o'],check=True)
    return subprocess.run(['python3','range_interp.py',S+'/s.o','e4_poly_invntt','2458'],capture_output=True).returncode==0
best=None
for s04 in ([0,1,2],[0,1,3],[0,1,2,3]):
    sel={j:(list(s04) if j in (0,4) else [0,1]) for j in range(8)}
    if not ok(sel): print('start fails',s04); continue
    changed=True
    while changed:
        changed=False
        for j,g in [(j,g) for j in range(8) for g in list(sel[j])]:
            t={k:[x for x in v if not (k==j and x==g)] for k,v in sel.items()}
            if ok(t): sel=t; changed=True; print('  removed',(j,g),'->',sum(map(len,sel.values()))); break
    n=sum(map(len,sel.values())); print(s04,'->',n,spec(sel))
    if best is None or n<best[0]: best=(n,spec(sel))
print('BEST',best)

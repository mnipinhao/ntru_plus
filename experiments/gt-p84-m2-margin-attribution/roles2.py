import re,subprocess,bisect,sys,collections
S="/private/tmp/claude-501/-Users-chenpinhao-ntruplus/a827c50f-9c4e-40e1-b926-99dea89f0d8e/scratchpad"
def role(n):
    l=n.lower().lstrip('._')
    if 'keccak' in l or l.startswith('shake') or l in ('hash_g','hash_h') or 'hash_fixed' in l: return 'Keccak'
    if 'crepmod' in l: return 'crepmod3'
    if 'baseinv' in l or l.startswith('binv') or 'recover' in l or 'prefix' in l: return 'baseinv'
    if 'invntt' in l or l.startswith('inverse'): return 'invNTT'
    if 'basemul' in l or l.startswith('bm_') or 'bm_tile' in l or l.startswith('base') or 'scale' in l: return 'basemul'
    if 'ntt' in l or 'top_split' in l or 'rebase' in l: return 'NTT'
    if 'pack' in l or 'frombytes' in l or 'tobytes' in l or 'transpose_top' in l or 'packed_i' in l: return 'pack/unpack'
    if 'sotp' in l or 'cbd' in l or l.startswith('loop_sub') or 'triple' in l or l.startswith('loop_add') or l=='add_asm': return 'sotp/cbd/add'
    if 'memset' in l or 'memmove' in l or 'memcpy' in l or 'chkstk' in l or 'malloc' in l or 'free' in l: return 'memory/clear'
    return 'other'
def analyse(binname, prof):
    t=open(prof).read()
    load=int(re.search(r'Load Address:\s+(0x[0-9a-f]+)',t).group(1),16)
    nm=subprocess.run(['nm','-n',f'{S}/bin/{binname}'],capture_output=True,text=True).stdout
    rows=[(int(p[0],16),p[1],p[2]) for p in (l.split() for l in nm.split('\n')) if len(p)==3 and p[1] in 'tT']
    glob=sorted((a,n) for a,ty,n in rows if ty=='T'); gk=[g[0] for g in glob]
    addr={n:a for a,ty,n in rows}
    allsym=sorted((a,n) for a,ty,n in rows); ak=[x[0] for x in allsym]
    def owner(name):
        a=addr.get(name) or addr.get('_'+name)
        if a is None: return name
        i=bisect.bisect_right(gk,a)-1
        return glob[i][1] if i>=0 else name
    def owner_addr(off):
        a=off+0x100000000
        i=bisect.bisect_right(gk,a)-1
        return glob[i][1] if i>=0 else '?'
    sec=t.split("Sort by top of stack, same collapsed (when >= 5):")[1].split("Binary Images:")[0]
    flat={}
    for ln in sec.strip().split("\n"):
        m=re.match(r'\s*(.+?)\s+\(in [^)]+\)\s+(\d+)\s*$', ln)
        if m: flat[m.group(1)]=int(m.group(2))
    dedup=flat.pop('<deduplicated_symbol>',0)
    out=collections.Counter()
    for k,v in flat.items(): out[role(owner(k))]+=v
    if dedup:
        cnt=collections.Counter()
        for m in re.finditer(r'(\d+) <deduplicated_symbol>\s+\(in [^)]+\) \+ [\d,\.]+\s+\[([^\]]+)\]', t):
            n=int(m.group(1)); a=[x for x in m.group(2).split(',') if x.startswith('0x')]
            for x in a: cnt[owner_addr(int(x,16)-load)]+=n/len(a)
        tot=sum(cnt.values()) or 1
        for k,v in cnt.items(): out[role(k)]+=dedup*v/tot
    return out
OPN={'0':'keygen','2':'decaps'}
NS={('768','0','off'):3809,('768','0','gt'):3799,('768','2','off'):3238,('768','2','gt'):3140,
    ('864','0','off'):4384,('864','0','gt'):4439,('864','2','off'):4064,('864','2','gt'):4153,
    ('1152','0','off'):6779,('1152','0','gt'):6877,('1152','2','off'):5304,('1152','2','gt'):5376}
for s in ('768','864','1152'):
  for op in ('0','2'):
    A=analyse(f'spin_off{s}',f'{S}/prof/spin_off{s}.{op}.txt')
    B=analyse(f'spin_gt{s}', f'{S}/prof/spin_gt{s}.{op}.txt')
    ta,tb=sum(A.values()),sum(B.values())
    na,nb=NS[(s,op,'off')],NS[(s,op,'gt')]
    print(f"=== NTRU+{s} {OPN[op]}  (ns/op: Official {na}, GT {nb}, diff {nb-na:+d}) ===")
    print(f"{'role':<15}{'Official':>10}{'GT':>10}{'diff ns':>10}")
    ks=sorted(set(A)|set(B), key=lambda k: -(B[k]/tb*nb - A[k]/ta*na))
    for k in ks:
        d=B[k]/tb*nb - A[k]/ta*na
        if abs(d)<3 and A[k]+B[k]<40: continue
        print(f"{k:<15}{A[k]/ta*na:10.0f}{B[k]/tb*nb:10.0f}{d:+10.0f}")
    print(f"{'non-Keccak':<15}{(ta-A['Keccak'])/ta*na:10.0f}{(tb-B['Keccak'])/tb*nb:10.0f}"
          f"{(tb-B['Keccak'])/tb*nb-(ta-A['Keccak'])/ta*na:+10.0f}\n")

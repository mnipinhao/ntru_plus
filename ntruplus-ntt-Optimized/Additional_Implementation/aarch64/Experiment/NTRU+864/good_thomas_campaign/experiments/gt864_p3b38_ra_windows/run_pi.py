"""P3B38 exact SSA/address audit and inherited same-boundary Pi harness."""
from pathlib import Path
import importlib.util, re, json, collections, hashlib, sys, contextlib, io
H = Path(__file__).resolve().parent
E = H.parent
B = H / 'build'
S = B / 'sync'
spec = importlib.util.spec_from_file_location('parent37', E/'gt864_p3b37_local_slothy/run_pi.py')
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
P.H, P.B, P.S = H, B, S
P.R.H, P.R.B, P.R.S = H, B, S
P.R.REMOTE = '/home/pi/ntruplus-experiments/gt864-p3b38-ra-windows'
LIVE = [31,1,9,26,20,24,30,29,22,19,21,23,8,10,12,6,27,0,13,14,15]

def instructions(path):
    body = path.read_text().split('p3b38_slothy_start:')[1].split('p3b38_slothy_end:')[0]
    lines = [x.split('//')[0].strip().lower() for x in body.splitlines()]
    return [x for x in lines if x]

def fingerprint(lines):
    reg = {i:f'entry-v{i}' for i in range(32)}
    ptr = {i:0 for i in range(4)}
    nodes, accesses = [], []
    def digest(x):
        return hashlib.sha256(repr(x).encode()).hexdigest()
    for original in lines:
        line = re.sub(r'\s+', '', original)
        if original.startswith(('ldr ', 'ldp ')):
            m = re.fullmatch(r'(ldr|ldp)q(\d+)(?:,q(\d+))?,\[x([0-3])(?:,#(-?\d+))?\](?:,#(-?\d+))?', line)
            assert m, original
            op, d, e, p, offset, inc = m.groups()
            p = int(p); address = ptr[p]+int(offset or 0)
            for index, dst in enumerate([d] + ([e] if e is not None else [])):
                value = ('load', p, address+16*index, 16)
                reg[int(dst)] = digest(value)
                accesses.append(value)
            ptr[p] += int(inc or 0)
            nodes.append(digest((op,p,address,inc)))
            continue
        if original.startswith('add x'):
            m = re.fullmatch(r'addx([0-3]),x([0-3]),#(\d+)', line)
            assert m, original
            d,s,n = map(int,m.groups())
            assert d == s
            ptr[d] += n
            nodes.append(digest(('pointer-add',d,n)))
            continue
        m = re.fullmatch(r'(mul|sqrdmulh|mls|add|sub|trn1|trn2|tbl|orr|mov)v(\d+)(\.[a-z0-9]+),(.*)', line)
        assert m, original
        op,d,shape,rhs = m.groups(); d = int(d)
        # Preserve all lane/arrangement syntax, including indexed constants.
        value_rhs = re.sub(r'\bv(\d+)\b', lambda x:reg[int(x[1])], rhs)
        value = digest((op,shape,value_rhs,reg[d] if op=='mls' else None))
        reg[d] = value
        nodes.append(value)
    return {'outputs':{i:reg[i] for i in LIVE}, 'pointers':ptr,
            'accesses':sorted(accesses), 'nodes':nodes}

def validate():
    before = instructions(B/'candidate.sym.S')
    alloc = instructions(B/'allocated.S')
    after = instructions(B/'scheduled.S')
    assert len(before) == len(alloc) == len(after) == 513
    proofs = [fingerprint(x) for x in (before,alloc,after)]
    for key in ('outputs','pointers','accesses'):
        assert proofs[0][key] == proofs[1][key] == proofs[2][key], key
    assert proofs[0]['nodes'] == proofs[1]['nodes'], 'RA changed DAG order'
    assert collections.Counter(proofs[1]['nodes']) == collections.Counter(proofs[2]['nodes'])
    assert not any(re.search(r'\bsp\b',x) for x in after)
    assert collections.Counter(x.split()[0] for x in before) == collections.Counter(x.split()[0] for x in after)
    result = {'gate':'P3B38','instruction_count':513,'exact_ssa_and_addresses':True,
              'RA_order_preserved':True,'no_spill':True,
              'RA_changed_lines':sum(a != b for a,b in zip(before,alloc)),
              'source_sha256':hashlib.sha256((B/'scheduled.S').read_bytes()).hexdigest()}
    (B/'post-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    return after

def prepare():
    # Reuse staging; point its baseline at P3B37 and its validator at this exact DAG check.
    code = (E/'gt864_p3b37_local_slothy/run_pi.py').read_text()
    code = code[code.index('def prepare():'):code.index('def summarize():')]
    code = code.replace('gt864_p3b36_combined', 'gt864_p3b37_local_slothy')
    namespace = dict(P.__dict__, H=H,E=E,B=B,S=S,validate=validate)
    exec(compile(code, 'inherited-staging', 'exec'), namespace)
    namespace['prepare']()

def summarize():
    with contextlib.redirect_stdout(io.StringIO()):
        P.summarize()
    data = json.loads((B/'measurement.json').read_text())
    data.update(gate='P3B38', baseline='P3B37')
    (B/'measurement.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))

if __name__ == '__main__':
    if '--validate' in sys.argv: validate()
    if '--prepare' in sys.argv: prepare()
    if '--run' in sys.argv: P.R.execute()
    if '--repeat' in sys.argv: P.R.repeat()
    if '--summarize' in sys.argv: summarize()

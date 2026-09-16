"""Exact symbolic producer plus consumer byte execution; no timing claim."""
import contextlib,importlib.util,io,json,re,random,sys
from pathlib import Path
from generate_bytes import indices
P=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
    spec=importlib.util.spec_from_file_location('old_byte_model',P.parent/'gt864-next-dag/model.py')
    model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
def code(path):return [x.strip() for x in path.read_text().splitlines() if x.startswith('    ') and not x.strip().startswith(('ret','//'))]
model.code=code(P/'tobytes_block/candidate.sym.S')
consumer=code(P/'tobytes_merge/candidate.sym.S')
def merge(scratch,top,row):
    mem={10000+i:b for i,b in enumerate(scratch)}
    mem.update({20000+i:b for i,b in enumerate(indices)})
    g={'x0':0,'x1':10000+top*648+row*24,'x2':10000+top*648+216+row*24,
       'x3':10000+top*648+432+row*24,'x4':20000}
    v={};out={}
    for line in consumer:
        op=line.split()[0];s=re.findall(r'<(\w+)>',line);im=list(map(int,re.findall(r'#(\d+)',line)))
        if op=='add':
            ptrs=re.findall(r'\bx\d+',line);g[ptrs[0]]=g[ptrs[1]]+im[0]
        elif op in ('ldr','str'):
            ptr=re.search(r'\[(x\d+)',line)[1];addr=g[ptr]+(im[0] if im else 0)
            width=8 if re.search(r'\bD<',line) else 16
            if op=='ldr':v[s[0]]=[mem[addr+i] for i in range(width)]+[0]*(16-width)
            else:
                for i in range(width):
                    assert addr+i not in out;out[addr+i]=v[s[0]][i]
        elif op=='tbl':
            table=v[s[1]]+v[s[2]]
            v[s[0]]=[table[i] if i<len(table) else 0 for i in v[s[3]]]
        elif op=='orr':v[s[0]]=[a|b for a,b in zip(v[s[1]],v[s[2]])]
        else:raise AssertionError(line)
    assert sorted(out)==list(range(72))
    return [out[i] for i in range(72)]
def main():
    small='--small' in sys.argv
    if small:model.code=code(P/'tobytes_small/candidate.sym.S')
    rng=random.Random(648)
    cases=[list(range(864)),[-32768]*864,[32767]*864,[0]*864]+[
      [rng.randrange(-32768,32768) for _ in range(864)] for _ in range(128)]
    if small:cases=[[max(-3456,min(3456,x)) for x in a] for a in cases]+[[v]*864 for v in [-3456,-3023,-1,0,1,3023,3456]]
    for inp in cases:
        scratch={}
        for top in range(2):
            for pair in range(3):model.execute(inp,top,pair,scratch,scratch_mode=True)
        assert sorted(scratch)==list(range(1296))
        scratch=[scratch[i] for i in range(1296)]
        out=[]
        for top in range(2):
            for row in range(9):out+=merge(scratch,top,row)
        oracle=[]
        for i in range(0,864,2):
            a,b=inp[model.wire[i]]%3457,inp[model.wire[i+1]]%3457
            oracle.extend([a&255,(a>>8)|((b&15)<<4),b>>4])
        assert out==oracle
    print(json.dumps(dict(status='byte_symbolic_model_pass',small=small,cases=len(cases),
      coefficient_Q_loads=108,byte_scratch_peak=648,lane_ST3=0,
      producer_full_ST3_8b=54,final_STR_Q=72,final_STR_D=18,
      extra_byte_scratch_traffic=2592,physical_assembly_execution=False),indent=2))
if __name__=='__main__':main()

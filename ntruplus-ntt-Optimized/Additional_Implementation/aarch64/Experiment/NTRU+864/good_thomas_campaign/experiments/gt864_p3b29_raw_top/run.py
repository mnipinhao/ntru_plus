#!/usr/bin/env python3
"""P3B29: proof-gated, small-input raw top only; production untouched."""
from pathlib import Path
import subprocess,shutil,json,hashlib,collections,statistics,re
HERE=Path(__file__).resolve().parent;EXP=HERE.parent
B=HERE/'build';S=B/'sync'
HOST='pi@100.99.191.9';REMOTE='/home/pi/ntruplus-experiments/gt864-p3b29-raw-top'
def run(args):
    try:return subprocess.check_output(args,text=True,stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:print(e.output,flush=True);raise
def ssh(s):return run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15',HOST,s])
def prepare():
    assert not S.exists(),'Refusing to overwrite staged sources'
    proof=EXP/'gt864_p3b28_small_input_range'
    out=run(['python3',str(proof/'prove.py')]);B.mkdir(exist_ok=True)
    (B/'range-rerun.log').write_text(out)
    assert json.loads((proof/'build/proof.json').read_text())['status']=='pass'
    old=EXP/'gt864_p3b26_alignment/build/sync'
    S.mkdir();shutil.copytree(old/'t1',S/'t1');shutil.copytree(old/'t1',S/'raw');shutil.copytree(old/'sc',S/'sc')
    for name in ('harness.c','ids.h'):shutil.copy2(old/name,S/name)
    original=(S/'raw/gt864_top_split.s').read_text()
    removed=[l for l in original.splitlines() if re.match(r'\s*(sqrdmulh|mls)\s',l)]
    assert len(removed)==8
    candidate='\n'.join(l for l in original.splitlines() if l not in removed)+'\n'
    candidate=candidate.replace('gt864_top_split_ld3','gt864_top_split_small_input')
    candidate='/* P3B29: REQUIRED input [-3,4]; P3B28 proof. Not a general-input API. */\n'+candidate
    (S/'raw/gt864_top_split.s').write_text(candidate)
    for name in ('gt864_forward_poly_ntt.S','gt864_poly_api.c'):
        p=S/'raw'/name
        p.write_text(p.read_text().replace('gt864_top_split_ld3','gt864_top_split_small_input').replace('gt864_forward_poly_ntt_all_one_mul_b3','gt864_forward_poly_ntt_small_input'))
    make=(old/'Makefile').read_text().splitlines()
    rules=[make[0],make[1],'all: bench forward t1.so t1-prof.so raw.so raw-prof.so sc.so sc-prof.so',
           'bench: harness.c ids.h','\t$(CC) -O3 -rdynamic harness.c -ldl -o bench',
           'forward: forward.c harness.c ids.h guard.h','\t$(CC) -O3 -march=armv8-a+simd -rdynamic forward.c -ldl -o forward']
    for variant in ('t1','sc'):
        block=[]
        for i,line in enumerate(make):
            if line.startswith(variant+'/') or line.startswith(variant+'.so:') or line.startswith(variant+'-prof.so:'):block.extend((line,make[i+1]))
        rules+=block
        if variant=='t1':rules += [l.replace('t1/','raw/').replace('-It1','-Iraw').replace('t1.so','raw.so').replace('t1-prof.so','raw-prof.so') for l in block]
    (S/'Makefile').write_text('\n'.join(rules)+'\n')
    f=(EXP/'gt864_p3b26_alignment/forward.c').read_text()
    f=f.replace('"gt","t1","sc"','"t1","raw","sc"')
    f=f.replace('||(v==1&&memcmp(oracle,out,sizeof oracle))','')
    f=f.replace('    int16_t oracle[864];','    guard_check();\n    int16_t oracle[864];')
    f=f.replace('int main(int argc,char **argv) {','#include "guard.h"\nint main(int argc,char **argv) {')
    # guard_check needs loaded function pointers: invoke after dlopen loop.
    f=f.replace('    puts("forward_correctness=pass cases=64 T0_T1_bitexact=pass SUPERCOP_wire_equivalence=pass");','    puts("forward_correctness=pass cases=64 T1_raw_SUPERCOP_wire_equivalence=pass");')
    (S/'forward.c').write_text(f);shutil.copy2(HERE/'guard.h',S/'guard.h')
    hashes={str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file()}
    (B/'source-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    (B/'removed.json').write_text(json.dumps(removed,indent=2)+'\n')
def execute():
    raw=B/'raw';raw.mkdir(exist_ok=True)
    ssh('mkdir -p '+REMOTE);run(['rsync','-az',str(S)+'/',HOST+':'+REMOTE+'/'])
    (raw/'build.log').write_text(ssh(f'cd {REMOTE} && make -j4 all'))
    env=ssh('uname -a; gcc --version; vcgencmd get_throttled');assert 'throttled=0x0' in env
    (raw/'environment.log').write_text(env)
    # Correctness precedes all timing, including full callers.
    check=ssh(f'cd {REMOTE} && BASE=t1 CAND=raw ./bench --check-only')
    assert 'correctness=pass' in check and 'cross_version_pk_ct_differences=0' in check
    (raw/'check.log').write_text(check)
    for kind in ('forward','kem'):
        rows=collections.defaultdict(list);profiles=collections.defaultdict(list)
        for rep in range(3):
            for order in (0,1):
                command=f'./forward {order}' if kind=='forward' else f'./bench {order}'
                out=ssh(f'cd {REMOTE} && BASE=t1 CAND=raw taskset -c 3 {command}')
                (raw/f'{kind}-{rep}-{order}.log').write_text(out)
                assert ('forward_correctness=pass' if kind=='forward' else 'correctness=pass') in out
                for line in out.splitlines():
                    p=line.split(',')
                    if p[0]=='forward':rows[p[1]].append(list(map(float,p[2:])))
                    elif p[0]=='full':rows['/'.join(p[1:3])].append(list(map(float,p[3:])))
                    elif p[0]=='profile':profiles['/'.join(p[1:4])].append(float(p[5]))
            assert 'throttled=0x0' in ssh('vcgencmd get_throttled')
            print(f'{kind} repetition {rep+1}/3 complete',flush=True)
        summary={'measurements':{k:dict(zip(('cycles','instructions','branches'),[statistics.median(x[i] for x in vals) for i in range(3)])) for k,vals in rows.items()},'profile':{k:statistics.median(v) for k,v in profiles.items()}}
        (B/(kind+'.json')).write_text(json.dumps(summary,indent=2)+'\n')
    (raw/'objects.log').write_text(ssh(f'cd {REMOTE} && sha256sum *.so bench forward && objdump -dr raw/gt864_top_split.o && objdump -dr raw/gt864_forward_poly_ntt.o && objdump -d --disassemble=gt_d1_poly_ntt raw.so && size t1/gt864_top_split.o raw/gt864_top_split.o'))
def product():
    shutil.copy2(HERE/'product.c',S/'product.c')
    run(['rsync','-az',str(S/'product.c'),HOST+':'+REMOTE+'/product.c'])
    out=ssh(f'cd {REMOTE} && gcc -O3 -march=armv8-a+simd -rdynamic product.c -ldl -o product && taskset -c 3 ./product')
    (B/'raw/product.log').write_text(out);assert 'polynomial_product=pass' in out;print(out)
if __name__=='__main__':
    import sys
    if '--prepare' in sys.argv:prepare()
    if '--run' in sys.argv:execute()
    if '--product' in sys.argv:product()

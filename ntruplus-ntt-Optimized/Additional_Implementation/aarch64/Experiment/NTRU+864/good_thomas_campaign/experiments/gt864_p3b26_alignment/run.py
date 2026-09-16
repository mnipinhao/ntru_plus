#!/usr/bin/env python3
"""P3B26 T1 and P3B27 ToBytes: independent substitutions of P3B25 GT.

No production edits. Generated sources and raw evidence stay in build/.
"""
from pathlib import Path
import subprocess, shutil, hashlib, json, os, collections, statistics

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
BUILD = HERE / 'build'
SYNC = BUILD / 'sync'
HOST = 'pi@100.99.191.9'
REMOTE = '/home/pi/ntruplus-experiments/gt864-p3b26-alignment'

def run(args):
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        print(error.output, flush=True)
        raise

def ssh(command):
    return run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15', HOST, command])

def prepare():
    assert not SYNC.exists(), 'Refusing to overwrite a staged experiment'
    source = EXP / 'gt_fr0_d1_supercop_profile/build/sync'
    shutil.copytree(source, SYNC, ignore=shutil.ignore_patterns('*.o', '*.so', 'bench', 'build'))
    tail = EXP / 'gt_tail_architecture_shootout/build'
    for variant in ('t1', 'tb'):
        shutil.copytree(SYNC / 'gt', SYNC / variant)
    (SYNC / 't1/gt864_forward_poly_ntt.S').write_text(
        (tail / 'full_t1_wrapper.S').read_text().replace(
            'gt864_forward_poly_ntt_a1_t1', 'gt864_forward_poly_ntt_all_one_mul_b3'))
    shutil.copy2(tail / 'pass2_t1.S', SYNC / 't1/gt864_forward_six_bank.S')
    shutil.copy2(tail / 'tail_variants.S', SYNC / 't1/tail_variants.S')
    byte = EXP / 'gt_fr0_d1_input_once_tobytes/build'
    for name in ('input_once_tobytes.c', 'p3b6_tables.h'):
        shutil.copy2(byte / name, SYNC / 'tb' / name)
    api = SYNC / 'tb/byte_api.c'
    api.write_text('void gt864_fr0_input_once_tobytes(unsigned char *,const short *);\n' +
                   api.read_text().replace('r9_to(out, in->coeffs)', 'gt864_fr0_input_once_tobytes(out, in->coeffs)'))
    make = (SYNC / 'Makefile').read_text()
    # Reuse exact baseline recipes/flags; only add the selected candidate object.
    lines = make.splitlines()
    for variant, extra, lang in (('t1', 'tail_variants.S', 'assembler-with-cpp'),
                                  ('tb', 'input_once_tobytes.c', 'c')):
        block = []
        for i, line in enumerate(lines):
            if line.startswith('gt/') or line.startswith('gt.so:') or line.startswith('gt-prof.so:'):
                block.extend([line, lines[i+1]])
        text = '\n'.join(block).replace('gt/', variant+'/').replace('-Igt', '-I'+variant)
        text = text.replace('gt-prof.so', variant+'-prof.so').replace('gt.so', variant+'.so')
        obj = variant+'/'+Path(extra).stem+'.o'
        output = []
        for line in text.splitlines():
            if line.startswith(variant+'.so:') or line.startswith(variant+'-prof.so:'):
                line += ' '+obj
            elif line.startswith('\t$(CC) -shared'):
                line = line.replace(' -o ', ' '+obj+' -o ')
            output.append(line)
        make += '\n'+'\n'.join(output)+'\n'+f'{obj}: {variant}/{extra}\n\t$(CC) $(CFLAGS) -I{variant} -x {lang} -c $< -o $@\n'
    make = make.replace('all: bench gt.so sc.so gt-prof.so sc-prof.so',
                        'all: bench gt.so sc.so gt-prof.so sc-prof.so t1.so t1-prof.so tb.so tb-prof.so')
    (SYNC / 'Makefile').write_text(make)
    harness = (SYNC / 'harness.c').read_text()
    old = 'struct api a[2]={load("./sc.so",0),load("./gt.so",1)},p[2]={load("./sc-prof.so",0),load("./gt-prof.so",1)}'
    new = 'const char *base=getenv("BASE"),*cand=getenv("CAND");if(!base)base="sc";if(!cand)cand="gt";char bn[64],cn[64],bp[64],cp[64];snprintf(bn,64,"./%s.so",base);snprintf(cn,64,"./%s.so",cand);snprintf(bp,64,"./%s-prof.so",base);snprintf(cp,64,"./%s-prof.so",cand);struct api a[2]={load(bn,strcmp(base,"sc")!=0),load(cn,1)},p[2]={load(bp,strcmp(base,"sc")!=0),load(cp,1)}'
    assert old in harness
    harness = harness.replace(old,new).replace('const char*names[]={"supercop","gt_p3b23"}', 'const char*names[]={base,cand}')
    (SYNC / 'harness.c').write_text(harness)
    manifest = {str(p.relative_to(SYNC)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in SYNC.rglob('*') if p.is_file()}
    (BUILD / 'source-hashes.json').write_text(json.dumps(manifest,indent=2)+'\n')

def execute():
    raw = BUILD / 'raw';raw.mkdir(exist_ok=True)
    shutil.copy2(EXP/'gt_fr0_d1_input_once_tobytes/input_once_tobytes.h', SYNC/'tb/input_once_tobytes.h')
    (BUILD/'source-hashes.json').write_text(json.dumps({str(p.relative_to(SYNC)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SYNC.rglob('*') if p.is_file()},indent=2)+'\n')
    ssh('mkdir -p '+REMOTE)
    run(['rsync','-az',str(SYNC)+'/',HOST+':'+REMOTE+'/'])
    (raw/'build.log').write_text(ssh('cd '+REMOTE+' && make -j4 all'))
    env = ssh('uname -a; gcc --version; vcgencmd get_throttled; vcgencmd measure_temp')
    assert 'throttled=0x0' in env
    (raw/'environment.txt').write_text(env)
    for base,cand in (('gt','t1'),('gt','tb'),('sc','t1')):
        full=collections.defaultdict(list);profile=collections.defaultdict(list)
        for rep in range(3):
            for order in (0,1):
                out=ssh(f'cd {REMOTE} && BASE={base} CAND={cand} taskset -c 3 ./bench {order}')
                (raw/f'{base}-{cand}-{rep}-{order}.log').write_text(out)
                assert 'correctness=pass' in out and 'cross_version_pk_ct_differences=0' in out
                for line in out.splitlines():
                    p=line.split(',')
                    if p[0]=='full':full['/'.join(p[1:3])].append(list(map(float,p[3:])))
                    if p[0]=='profile':profile['/'.join(p[1:4])].append(float(p[5]))
            assert 'throttled=0x0' in ssh('vcgencmd get_throttled')
            print(f'{base}/{cand} repetition {rep+1}/3 complete',flush=True)
        summary={'full':{k:dict(zip(('cycles','instructions','branches'),[statistics.median(x[i] for x in vals) for i in range(3)])) for k,vals in full.items()},'profile':{k:statistics.median(v) for k,v in profile.items()}}
        (BUILD/f'{base}-{cand}.json').write_text(json.dumps(summary,indent=2)+'\n')
    (raw/'objects.log').write_text(ssh(f'cd {REMOTE} && sha256sum *.so bench && objdump -dr t1/gt864_forward_poly_ntt.o && objdump -dr tb/byte_api.o && objdump -d tb/input_once_tobytes.o'))

def diagnose():
    shutil.copy2(HERE/'forward.c',SYNC/'forward.c')
    run(['rsync','-az',str(SYNC/'forward.c'),HOST+':'+REMOTE+'/forward.c'])
    raw=BUILD/'raw'
    (raw/'forward-build.log').write_text(ssh(f'cd {REMOTE} && gcc -O3 -march=armv8-a+simd -rdynamic forward.c -ldl -o forward'))
    rows=collections.defaultdict(list)
    for rep in range(3):
        for order in (0,1):
            out=ssh(f'cd {REMOTE} && taskset -c 3 ./forward {order}')
            (raw/f'forward-{rep}-{order}.log').write_text(out)
            assert 'forward_correctness=pass' in out
            for line in out.splitlines():
                p=line.split(',')
                if p[0]=='forward':rows[p[1]].append(list(map(float,p[2:])))
        assert 'throttled=0x0' in ssh('vcgencmd get_throttled')
        print(f'Forward diagnostic {rep+1}/3 complete',flush=True)
    summary={k:dict(zip(('cycles','instructions','branches'),[statistics.median(x[i] for x in vals) for i in range(3)])) for k,vals in rows.items()}
    (BUILD/'forward.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__':
    import sys
    if '--prepare' in sys.argv:prepare()
    if '--run' in sys.argv:execute()
    if '--forward' in sys.argv:diagnose()

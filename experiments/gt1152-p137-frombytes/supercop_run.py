"""P137: SUPERCOP 20260831 native timing of NTRU+1152: Official vs GT production before and after the two-register tbl decoder (unpack.S).

Adapted from E28's run.py (staging, RNG initialisation, variant selection and
data parsing unchanged); no profiler.  usage: run.py setup | run.py measure
Inputs on the Pi: /home/pi/p137/{before,after}/NTRU+1152 (main 21a1de6a and gt1152-frombytes-tbl2).
The 1152 Makefile builds in its own directory, so make check runs on a copy.
"""
from pathlib import Path
import subprocess, shutil, json, hashlib, statistics, sys
R = Path(__file__).resolve().parent; B = R / '.build'; SC = Path('/home/pi/supercop-20260831'); S = B / 'supercop'
TREES = {'gt-before': Path('/home/pi/p137/before/NTRU+1152'), 'gt-after': Path('/home/pi/p137/after/NTRU+1152')}
VARIANTS = ['official', 'gt-before', 'gt-after']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd, log, cwd=None):
    p = subprocess.run(list(map(str, cmd)), cwd=cwd, capture_output=True, text=True)
    (B / log).write_text(p.stdout + p.stderr)
    if p.returncode:
        # Targeted crypto_rng replaces work with its RNG builds; the stock driver
        # then cats the absent work/errors (E28).  Accept only that exact case.
        expected = 'cat: ' + str(S / 'bench/pinhao/work/errors') + ': No such file or directory'
        libs = S / 'bench/pinhao/lib/aarch64'
        if not (log == 'init-crypto_rng.log' and p.stderr.strip().endswith(expected)
                and 'Success. Using crypto_rng_chacha20' in p.stderr + p.stdout
                and all((libs / n).is_file() for n in ['knownrandombytes.o', 'fastrandombytes.o'])):
            raise RuntimeError(log + '\n' + (p.stdout + p.stderr)[-2500:])
    return p.stdout
def env(): return run(['sh', '-c', 'date; uname -a; vcgencmd get_throttled; vcgencmd measure_temp'], 'env-latest.log')

if sys.argv[1] == 'setup':
    B.mkdir(); S.mkdir()
    for p in SC.iterdir():
        if p.is_file(): shutil.copy2(p, S / p.name)
    for n in ['knownrandombytes', 'fastrandombytes']: shutil.copytree(SC / n, S / n)
    for n in ['bin', 'lib', 'include']: shutil.copytree(SC / 'bench/pinhao' / n, S / 'bench/pinhao' / n)
    (S / 'bench/pinhao/security').mkdir()
    for op, primitive, leaves in [('crypto_stream', 'chacha20', ['dolbeau/arm-neon', 'e/ref']),
                                  ('crypto_rng', 'chacha20', ['ref']), ('crypto_kem', 'ntruplus1152', [])]:
        dest = S / op / primitive; dest.mkdir(parents=True)
        for p in (SC / op).iterdir():
            if p.is_file(): shutil.copy2(p, S / op / p.name)
        for p in (SC / op / primitive).iterdir():
            if p.is_file(): shutil.copy2(p, dest / p.name)
        for leaf in leaves: shutil.copytree(SC / op / primitive / leaf, dest / leaf)
    origin = SC / 'crypto_kem/ntruplus1152/aarch64'
    hashes = {p.name: sha(p) for p in origin.iterdir() if p.is_file()}
    shutil.copytree(origin, B / 'official')
    for p in (B / 'official').glob('goal-*'): p.unlink()      # same timingleaks category as GT (E28)
    gt = {}
    for name, tree in TREES.items():
        shutil.copytree(tree, B / ('check-' + name))
        run(['make', 'check'], f'package-check-{name}.log', B / ('check-' + name))
        run(['python3', tree / 'scripts/export_supercop.py', B / name], f'export-{name}.log')
        gt[name] = {str(p.relative_to(tree)): sha(p) for p in sorted(tree.rglob('*')) if p.is_file() and '.build' not in p.parts}
    for name in VARIANTS: shutil.copytree(B / name, S / 'crypto_kem/ntruplus1152' / name)
    (R / 'identity.json').write_text(json.dumps({
        'official_path': str(origin), 'official_hashes': hashes, 'gt_hashes': gt,
        'driver_hashes': {n: sha(SC / n) for n in ['do-part', 'measure-anything.c', 'crypto_kem/measure.c', 'crypto_kem/try.c']}}, indent=2) + '\n')
    for op in ['crypto_stream', 'crypto_rng']:
        print('initializing', op, flush=True)
        run(['taskset', '-c', '3', 'sh', './do-part', op, 'chacha20'], 'init-' + op + '.log', S)
    assert (S / 'bench/pinhao/lib/aarch64/fastrandombytes.o').exists()
    assert (S / 'bench/pinhao/lib/aarch64/knownrandombytes.o').exists()
    print('SETUP PASS', flush=True)

elif sys.argv[1] == 'measure':
    rows = []
    for rep in range(6):
        order = VARIANTS[rep % 3:] + VARIANTS[:rep % 3]
        if rep >= 3: order = order[::-1]
        for v in order:
            dest = S / 'crypto_kem/ntruplus1152'
            for n in VARIANTS: (dest / n).chmod(0o755 if n == v else 0o1755)
            before = env(); log = f'native-{rep}-{v}.log'
            run(['taskset', '-c', '3', 'sh', './do-part', 'crypto_kem', 'ntruplus1152'], log, S)
            after = env(); data = (S / 'bench/pinhao/data').read_text()
            (B / f'native-{rep}-{v}.data').write_text(data)
            counts = {k: [] for k in ['keypair_cycles', 'enc_cycles', 'dec_cycles']}
            for line in data.splitlines():
                p = line.split()
                if len(p) > 8 and p[6] in counts: counts[p[6]].append(int(p[8]))
            assert all(len(x) == 3 for x in counts.values()), (log, counts)
            impl = [l for l in data.splitlines() if ' implementation ' in l]
            assert impl and all(('/' + v) in l or (' ' + v) in l for l in impl), (v, impl)
            row = {'rep': rep, 'variant': v, 'cycles': {k: statistics.median(x) for k, x in counts.items()},
                   'before': before, 'after': after,
                   'metadata': [l for l in data.splitlines() if ' implementation ' in l or ' compiler ' in l],
                   'sha256': hashlib.sha256(data.encode()).hexdigest()}
            rows.append(row); (R / 'benchmark-summary.json').write_text(json.dumps(rows, indent=2) + '\n')
            print(rep, v, row['cycles'], flush=True)
    identity = json.loads((R / 'identity.json').read_text())
    assert identity['official_hashes'] == {p.name: sha(p) for p in (SC / 'crypto_kem/ntruplus1152/aarch64').iterdir() if p.is_file()}
    print('TIMING COMPLETE', flush=True)

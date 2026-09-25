"""P139: SUPERCOP 20260831 native timing on the Pi 5, all three sets, three leaves each:
  official       SUPERCOP's crypto_kem/ntruplus<set>/aarch64 (NTRU+ snapshot 2026-07-23, NO_CE)
  official-main  the same leaf with GitHub main 3991b2a's crepmod3.s -- main's NO_CE build
                 (ntruplus-supercop-update.sh run on main differs from SUPERCOP's leaf only there)
  gt             GT production at main (make check on a copy, then scripts/export_supercop.py)
Staging, RNG initialisation and variant selection as P119/P135/P137's run.py.  Besides SUPERCOP's
median-of-medians this keeps every sample (each data line is a median and 32 deviations): key
generation retries (1152: 29% of candidates) make its distribution multimodal, so its mean over all
samples -- the expected cost -- is reported too.
usage: run.py setup | run.py measure
"""
from pathlib import Path
import subprocess, shutil, json, hashlib, statistics, sys, re
R = Path(__file__).resolve().parent; B = R / '.build'; SC = Path('/home/pi/supercop-20260831'); S = B / 'supercop'
TREES = Path('/home/pi/p139/trees'); MAIN_LEAVES = Path('/home/pi/p139/sc/crypto_kem')
SETS = ['768', '864', '1152']; VARIANTS = ['official', 'official-main', 'gt']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd, log, cwd=None):
    p = subprocess.run(list(map(str, cmd)), cwd=cwd, capture_output=True, text=True)
    (B / log).write_text(p.stdout + p.stderr)
    if p.returncode:
        expected = 'cat: ' + str(S / 'bench/pinhao/work/errors') + ': No such file or directory'
        libs = S / 'bench/pinhao/lib/aarch64'
        if not (log == 'init-crypto_rng.log' and p.stderr.strip().endswith(expected)
                and 'Success. Using crypto_rng_chacha20' in p.stderr + p.stdout
                and all((libs / n).is_file() for n in ['knownrandombytes.o', 'fastrandombytes.o'])):
            raise RuntimeError(log + '\n' + (p.stdout + p.stderr)[-2500:])
    return p.stdout
def env(): return run(['sh', '-c', 'date; vcgencmd get_throttled; vcgencmd measure_temp'], 'env-latest.log')

if sys.argv[1] == 'setup':
    B.mkdir(); S.mkdir()
    for p in SC.iterdir():
        if p.is_file(): shutil.copy2(p, S / p.name)
    for n in ['knownrandombytes', 'fastrandombytes']: shutil.copytree(SC / n, S / n)
    for n in ['bin', 'lib', 'include']: shutil.copytree(SC / 'bench/pinhao' / n, S / 'bench/pinhao' / n)
    (S / 'bench/pinhao/security').mkdir()
    for op, primitive, leaves in [('crypto_stream', 'chacha20', ['dolbeau/arm-neon', 'e/ref']), ('crypto_rng', 'chacha20', ['ref'])] + \
                                 [('crypto_kem', 'ntruplus' + s, []) for s in SETS]:
        dest = S / op / primitive; dest.mkdir(parents=True)
        for p in (SC / op).iterdir():
            if p.is_file(): shutil.copy2(p, S / op / p.name)
        for p in (SC / op / primitive).iterdir():
            if p.is_file(): shutil.copy2(p, dest / p.name)
        for leaf in leaves: shutil.copytree(SC / op / primitive / leaf, dest / leaf)
    ident = {'official': {}, 'official_main_crepmod3': {}, 'gt': {}}
    for s in SETS:
        D = S / f'crypto_kem/ntruplus{s}'
        origin = SC / f'crypto_kem/ntruplus{s}/aarch64'
        ident['official'][s] = {p.name: sha(p) for p in origin.iterdir() if p.is_file()}
        shutil.copytree(origin, D / 'official')
        shutil.copytree(origin, D / 'official-main')
        shutil.copy2(MAIN_LEAVES / f'ntruplus{s}/aarch64/crepmod3.s', D / 'official-main/crepmod3.s')
        ident['official_main_crepmod3'][s] = sha(D / 'official-main/crepmod3.s')
        for d in (D / 'official', D / 'official-main'):
            for g in d.glob('goal-*'): g.unlink()          # same timingleaks category as GT (E28)
        tree = TREES / f'NTRU+{s}'
        chk = B / f'check-{s}'; shutil.copytree(tree, chk)
        run(['make', 'check'] + (['BUILD_DIR=' + str(B / f'build-{s}')] if s == '768' else []), f'package-check-{s}.log', chk)
        exp = ['python3', tree / 'scripts/export_supercop.py', D / 'gt'] + (['--prefix', 'gt768_p139_'] if s == '768' else [])
        run(exp, f'export-{s}.log')
        ident['gt'][s] = {str(p.relative_to(tree)): sha(p) for p in sorted(tree.rglob('*')) if p.is_file()}
    (R / 'identity.json').write_text(json.dumps(ident, indent=2) + '\n')
    for op in ['crypto_stream', 'crypto_rng']:
        print('initializing', op, flush=True)
        run(['taskset', '-c', '3', 'sh', './do-part', op, 'chacha20'], 'init-' + op + '.log', S)
    print('SETUP PASS', flush=True)

elif sys.argv[1] == 'measure':
    rows = []
    K = ['keypair_cycles', 'enc_cycles', 'dec_cycles']
    for rep in range(6):
        for s in SETS:
            order = VARIANTS[rep % 3:] + VARIANTS[:rep % 3]
            if rep >= 3: order = order[::-1]
            for v in order:
                D = S / f'crypto_kem/ntruplus{s}'
                for n in VARIANTS: (D / n).chmod(0o755 if n == v else 0o1755)
                before = env(); log = f'native-{s}-{rep}-{v}.log'
                run(['taskset', '-c', '3', 'sh', './do-part', 'crypto_kem', 'ntruplus' + s], log, S)
                after = env(); data = (S / 'bench/pinhao/data').read_text()
                (B / f'native-{s}-{rep}-{v}.data').write_text(data)
                meds = {k: [] for k in K}; samples = {k: [] for k in K}
                for line in data.splitlines():
                    p = line.split()
                    if len(p) > 8 and p[6] in meds:
                        m = int(p[8]); meds[p[6]].append(m)
                        if len(p) > 9: samples[p[6]] += [m + int(d) for d in re.findall(r'[+-]\d+', p[9])]
                assert all(len(x) == 3 for x in meds.values()), (log, meds)
                impl = [l for l in data.splitlines() if ' implementation ' in l]
                names = {m.group(1) for l in impl for m in [re.search(r'crypto_kem/ntruplus\d+/(\S+)', l)] if m}
                assert names == {v}, (v, impl)
                row = {'set': s, 'rep': rep, 'variant': v,
                       'median': {k: statistics.median(x) for k, x in meds.items()},
                       'mean': {k: statistics.fmean(x) for k, x in samples.items()},
                       'n': {k: len(x) for k, x in samples.items()},
                       'before': before, 'after': after}
                rows.append(row); (R / 'supercop-summary.json').write_text(json.dumps(rows, indent=2) + '\n')
                print(s, rep, v, row['median'], {k: round(x) for k, x in row['mean'].items()}, flush=True)
    print('TIMING COMPLETE', flush=True)

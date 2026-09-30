#!/usr/bin/env python3
"""SUPERCOP 20260831 on the Raspberry Pi 5: the package READMEs' SUPERCOP tables.

usage: run.py setup SUPERCOP WORK [--sets 768,864,1152] [--variants official,gt]
       run.py measure WORK [--rounds 6] [--core 3]
       run.py tables WORK

setup    stages a minimal SUPERCOP tree in WORK/supercop.  It holds SUPERCOP's
         top-level scripts, the stream and RNG primitives the KEM measurement
         uses, and one directory per variant in crypto_kem/ntruplus<set>/:
           official          SUPERCOP's own leaf (crypto_kem/ntruplus<set>/aarch64), as shipped
           official-nogoals  the same leaf without its goal-constbranch/goal-constindex
                             files, to show that they do not change the cycles;
                             see README.md.
           gt                this repository's package: `make check` on a copy, then the
                             package's scripts/export_supercop.py
         SUPERCOP must be a SUPERCOP 20260831 tree already initialised on this host
         (`./do-part init`), so that bench/<host>/{bin,lib,include} exist.
measure  runs rounds.  Each round measures every variant of every set once, in an
         order rotated from round to round.  Only the variant being measured is
         enabled: SUPERCOP skips sticky directories.  Every SUPERCOP data file is
         kept under WORK/runs/.
tables   prints, per set and variant, the median over the rounds of SUPERCOP's
         median and the mean over all samples.  Key generation retries rejected
         candidates, so its distribution is multimodal; NTRU+1152's README reports
         the mean.  It also prints GT against each official variant, with the
         paired per-round differences.
"""
import argparse
import hashlib
import json
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PRODUCTION = REPO / 'production/Additional_Implementation/aarch64'
OPS = ('keypair_cycles', 'enc_cycles', 'dec_cycles')
KINDS = ('official', 'official-nogoals', 'gt')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def shorthostname():
    # SUPERCOP's do-part: hostname | sed 's/\..*//' | tr -cd '[a-z][A-Z][0-9]' | tr '[A-Z]' '[a-z]'
    h = subprocess.run(['hostname'], capture_output=True, text=True, check=True).stdout.strip()
    return re.sub(r'[^a-z0-9]', '', h.split('.')[0].lower())


class Work:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.sc = self.root / 'supercop'
        self.logs = self.root / 'logs'
        self.runs = self.root / 'runs'
        self.host = shorthostname()
        self.top = self.sc / 'bench' / self.host

    def run(self, cmd, log, cwd=None, benign_rng=False):
        p = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        (self.logs / log).write_text(p.stdout + p.stderr)
        if p.returncode and not (benign_rng and self.rng_ready(p)):
            raise RuntimeError(f'{log} failed:\n' + (p.stdout + p.stderr)[-2500:])
        return p.stdout

    def rng_ready(self, p):
        # do-part crypto_rng ends by reading a work/errors file it never wrote;
        # the RNG is ready when it reports success and both randombytes objects exist
        libs = self.top / 'lib/aarch64'
        return (p.stderr.strip().endswith(f"cat: {self.top / 'work/errors'}: No such file or directory")
                and 'Success. Using crypto_rng_chacha20' in p.stdout + p.stderr
                and all((libs / n).is_file() for n in ('knownrandombytes.o', 'fastrandombytes.o')))

    def environment(self):
        p = subprocess.run(['sh', '-c', 'date; vcgencmd get_throttled; vcgencmd measure_temp'],
                           capture_output=True, text=True)
        return p.stdout + p.stderr

    @property
    def config(self):
        return json.loads((self.root / 'config.json').read_text())


def setup(a):
    sc = Path(a.supercop).resolve()
    w = Work(a.work)
    sets = a.sets.split(',')
    variants = a.variants.split(',')
    assert all(v in KINDS for v in variants), f'variants are {KINDS}'
    if w.sc.exists():
        sys.exit(f'{w.sc} exists; use a fresh WORK')
    if not (sc / 'bench' / w.host / 'lib').is_dir():
        sys.exit(f'{sc} is not initialised on this host (bench/{w.host}/lib missing): run ./do-part init there')
    w.sc.mkdir(parents=True)
    for p in sc.iterdir():
        if p.is_file():
            shutil.copy2(p, w.sc / p.name)
    for n in ('knownrandombytes', 'fastrandombytes'):
        shutil.copytree(sc / n, w.sc / n)
    for n in ('bin', 'lib', 'include'):
        shutil.copytree(sc / 'bench' / w.host / n, w.top / n)
    (w.top / 'security').mkdir()
    for op, primitive, leaves in [('crypto_stream', 'chacha20', ['dolbeau/arm-neon', 'e/ref']),
                                  ('crypto_rng', 'chacha20', ['ref'])] + \
                                 [('crypto_kem', 'ntruplus' + s, []) for s in sets]:
        dest = w.sc / op / primitive
        dest.mkdir(parents=True)
        for p in (sc / op).iterdir():
            if p.is_file():
                shutil.copy2(p, w.sc / op / p.name)
        for p in (sc / op / primitive).iterdir():
            if p.is_file():
                shutil.copy2(p, dest / p.name)
        for leaf in leaves:
            shutil.copytree(sc / op / primitive / leaf, dest / leaf)

    identity = {'supercop': str(sc), 'repository': None, 'variants': {}}
    head = subprocess.run(['git', '-C', REPO, 'rev-parse', 'HEAD'], capture_output=True, text=True)
    if head.returncode == 0:
        identity['repository'] = head.stdout.strip()
    for s in sets:
        d = w.sc / f'crypto_kem/ntruplus{s}'
        origin = sc / f'crypto_kem/ntruplus{s}/aarch64'
        for v in variants:
            if v.startswith('official'):
                shutil.copytree(origin, d / v)
                if v == 'official-nogoals':
                    for g in (d / v).glob('goal-*'):
                        g.unlink()
            else:
                package = PRODUCTION / f'NTRU+{s}'
                check = w.root / 'check' / f'NTRU+{s}'
                shutil.copytree(package, check)
                w.run(['make', 'check'], f'make-check-{s}.log', check)
                w.run(['python3', package / 'scripts/export_supercop.py', d / v], f'export-{s}.log')
            identity['variants'].setdefault(v, {})[s] = {
                str(p.relative_to(d / v)): sha(p) for p in sorted((d / v).rglob('*')) if p.is_file()}
    (w.root / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    (w.root / 'config.json').write_text(json.dumps({'sets': sets, 'variants': variants}) + '\n')
    for op in ('crypto_stream', 'crypto_rng'):
        print('initialising', op, flush=True)
        w.run(['taskset', '-c', str(a.core), 'sh', './do-part', op, 'chacha20'], f'init-{op}.log', w.sc,
              benign_rng=(op == 'crypto_rng'))
    print('setup done:', w.root, flush=True)


def measure(a):
    w = Work(a.work)
    cfg = w.config
    sets, variants = cfg['sets'], cfg['variants']
    w.runs.mkdir(parents=True, exist_ok=True)
    summary = w.root / 'summary.json'
    rows = json.loads(summary.read_text()) if summary.exists() else []
    first = 1 + max((r['round'] for r in rows), default=-1)
    for r in range(first, first + a.rounds):
        for s in sets:
            k = r % len(variants)
            order = variants[k:] + variants[:k]
            for v in order:
                d = w.sc / f'crypto_kem/ntruplus{s}'
                for n in variants:
                    (d / n).chmod(0o755 if n == v else 0o1755)
                before = w.environment()
                w.run(['taskset', '-c', str(a.core), 'sh', './do-part', 'crypto_kem', 'ntruplus' + s],
                      f'do-part-{s}-{r}-{v}.log', w.sc)
                after = w.environment()
                data = (w.top / 'data').read_text()
                (w.runs / f'{s}-{r}-{v}.data').write_text(data)
                medians = {k: [] for k in OPS}
                samples = {k: [] for k in OPS}
                for line in data.splitlines():
                    p = line.split()
                    if len(p) > 8 and p[6] in medians:
                        m = int(p[8])
                        medians[p[6]].append(m)
                        if len(p) > 9:
                            samples[p[6]] += [m + int(x) for x in re.findall(r'[+-]\d+', p[9])]
                assert all(len(x) == 3 for x in medians.values()), (s, r, v, medians)
                names = {m.group(1) for line in data.splitlines() if ' implementation ' in line
                         for m in [re.search(r'crypto_kem/ntruplus\d+/(\S+)', line)] if m}
                assert names == {v}, (s, r, v, names)
                row = {'set': s, 'round': r, 'variant': v,
                       'median': {k: statistics.median(x) for k, x in medians.items()},
                       'mean': {k: statistics.fmean(x) for k, x in samples.items()},
                       'n': {k: len(x) for k, x in samples.items()},
                       'before': before, 'after': after}
                rows.append(row)
                summary.write_text(json.dumps(rows, indent=2) + '\n')
                print(s, r, v, row['median'], flush=True)
    print('measurement done', flush=True)


def tables(a):
    w = Work(a.work)
    rows = json.loads((w.root / 'summary.json').read_text())
    by = {}
    for row in rows:
        by.setdefault((row['set'], row['variant']), []).append(row)
    fmt = lambda xs: ' / '.join(f'{x:,.0f}' if x == int(x) else f'{x:,.1f}' for x in xs)
    for s in dict.fromkeys(r['set'] for r in rows):
        variants = [v for (s2, v) in by if s2 == s]
        rounds = len(by[(s, variants[0])])
        print(f'NTRU+{s} ({rounds} rounds; cycles, medians of SUPERCOP medians)')
        figure = {}
        for v in variants:
            rs = by[(s, v)]
            med = [statistics.median(r['median'][k] for r in rs) for k in OPS]
            n = sum(r['n']['keypair_cycles'] for r in rs)
            mean_kg = sum(r['mean']['keypair_cycles'] * r['n']['keypair_cycles'] for r in rs) / n
            figure[v] = (med, mean_kg)
            print(f'  {v:17s} {fmt(med):>30s}   keygen mean of {n} samples {mean_kg:,.0f}')
        if 'gt' in figure:
            for v in variants:
                if v == 'gt':
                    continue
                (g, gm), (o, om) = figure['gt'], figure[v]
                pct = ' / '.join(f'{(x - y) / y * 100:+.2f}%' for x, y in zip(g, o))
                paired = {}
                for k in OPS:
                    gr = {r['round']: r['median'][k] for r in by[(s, 'gt')]}
                    orr = {r['round']: r['median'][k] for r in by[(s, v)]}
                    diffs = [gr[i] - orr[i] for i in gr if i in orr]
                    paired[k] = f'{sum(d < 0 for d in diffs)}/{len(diffs)}'
                print(f'  gt vs {v:11s} {pct:>30s}   keygen mean {(gm - om) / om * 100:+.2f}%   '
                      f'rounds with gt faster: {" / ".join(paired[k] for k in OPS)}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('setup')
    p.add_argument('supercop')
    p.add_argument('work')
    p.add_argument('--sets', default='768,864,1152')
    p.add_argument('--variants', default='official,gt')
    p.add_argument('--core', default=3, type=int)
    p = sub.add_parser('measure')
    p.add_argument('work')
    p.add_argument('--rounds', default=6, type=int)
    p.add_argument('--core', default=3, type=int)
    p = sub.add_parser('tables')
    p.add_argument('work')
    a = ap.parse_args()
    {'setup': setup, 'measure': measure, 'tables': tables}[a.cmd](a)


if __name__ == '__main__':
    main()

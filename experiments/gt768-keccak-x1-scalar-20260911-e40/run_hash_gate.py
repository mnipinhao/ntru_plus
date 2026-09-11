#!/usr/bin/env python3
from pathlib import Path
import json
import statistics
import subprocess

ROOT = Path('/home/pi/gt768-keccak-x1-scalar-20260911-e40')
EXP = ROOT / 'experiment'
BUILD = ROOT / '.build' / 'hash-gate-v1'
HARNESS = Path('/home/pi/gt768-official-support-hybrid-20260910-e33/benchmark-input')
VARIANTS = {'GT-C': ROOT / 'baseline', 'GT-Keccak-Asm': ROOT / 'candidate'}
MODES = ('shake_coins', 'hash_f', 'hash_g', 'hash_h')
FLAGS = ('-march=native', '-mtune=native', '-O3', '-fomit-frame-pointer',
         '-ffunction-sections', '-fdata-sections')

BUILD.mkdir(parents=True, exist_ok=False)

def run(cmd):
    return subprocess.check_output([str(x) for x in cmd], text=True)

bins = {}
for label, source in VARIANTS.items():
    for mode in MODES:
        binary = BUILD / (label.lower().replace('-', '_') + '_' + mode)
        sources = [EXP / 'bench_hash.c', HARNESS / 'perf_counter.c',
                   source / 'symmetric.c', source / 'fips202.c']
        if label == 'GT-Keccak-Asm':
            sources.append(source / 'keccakf1600.S')
        run(['gcc', *FLAGS, '-I' + str(source), '-I' + str(HARNESS),
             '-DBENCH_MODE_STR="' + mode + '"', *sources,
             '-Wl,--gc-sections', '-o', binary])
        bins[label, mode] = binary

samples = {mode: {label: [] for label in VARIANTS} for mode in MODES}
sinks = {mode: set() for mode in MODES}
for mode in MODES:
    for order in (tuple(VARIANTS), tuple(reversed(VARIANTS))):
        for label in order:
            text = run(['taskset', '-c', '3', bins[label, mode]])
            fields = dict(line.split('=', 1) for line in text.splitlines() if '=' in line)
            samples[mode][label].extend(int(x) for x in fields['samples'].split(','))
            sinks[mode].add(fields['sink'])

assert all(len(v) == 1 for v in sinks.values()), sinks
results = {}
for mode in MODES:
    results[mode] = {}
    for label in VARIANTS:
        values = sorted(samples[mode][label])
        results[mode][label] = {
            'count': len(values), 'min': min(values),
            'p50': int(statistics.median(values)), 'max': max(values)
        }
    base = results[mode]['GT-C']['p50']
    cand = results[mode]['GT-Keccak-Asm']['p50']
    results[mode]['saved_cycles'] = base - cand
    results[mode]['improvement_percent'] = 100 * (base - cand) / base

out = {
    'experiment_id': 'gt768-keccak-x1-scalar-20260911-e40',
    'host': run(['uname', '-a']).strip(),
    'compiler': run(['gcc', '--version']).splitlines()[0],
    'core': 3, 'samples_per_variant': 62, 'iterations_per_sample': 2000,
    'warmups_per_run': 100, 'flags': FLAGS,
    'sinks': {k: next(iter(v)) for k, v in sinks.items()},
    'results': results,
    'environment_end': run(['bash', '-c', 'vcgencmd get_throttled; vcgencmd measure_temp'])
}
(BUILD / 'summary.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))

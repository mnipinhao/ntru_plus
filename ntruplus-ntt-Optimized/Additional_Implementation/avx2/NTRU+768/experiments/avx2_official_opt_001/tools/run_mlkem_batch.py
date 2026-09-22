#!/usr/bin/env python3
"""Run the local mlkem-native-style batched cycle diagnostic in fresh processes."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[5]
REGIONS = ('copy_plus_inverse', 'complete_decap')
POLICY = {
    '/sys/devices/system/cpu/cpu1/cpufreq/scaling_governor': 'performance',
    '/sys/devices/system/cpu/intel_pstate/no_turbo': '1',
    '/proc/sys/kernel/randomize_va_space': '2',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def median(values):
    return sorted(values)[len(values) >> 1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', required=True)
    parser.add_argument('--processes', type=int, default=9)
    parser.add_argument('--reversed-placement', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.processes <= 99:
        parser.error('processes must be in [1,99]')
    for name, value in POLICY.items():
        if Path(name).read_text().strip() != value:
            raise SystemExit(f'timing blocked: {name} does not equal {value}')
    target = 'build/bench_yang_stage5reuse_mlkem_batch' + ('_reversed' if args.reversed_placement else '')
    output = ROOT / 'results' / args.tag
    output.mkdir(exist_ok=False)
    build = subprocess.run(['make', target], cwd=ROOT, text=True, capture_output=True)
    (output / 'build.log').write_text(build.stdout + build.stderr)
    build.check_returncode()
    elf = ROOT / target
    shutil.copy2(elf, output / 'measure.elf')
    processes = []
    for launch in range(args.processes):
        for name, value in POLICY.items():
            if Path(name).read_text().strip() != value:
                raise SystemExit(f'timing blocked during campaign: {name}')
        run = subprocess.run(['taskset', '-c', '1', str(elf)], cwd=ROOT,
                             text=True, capture_output=True)
        (output / f'launch-{launch}.out').write_text(run.stdout)
        (output / f'launch-{launch}.err').write_text(run.stderr)
        run.check_returncode()
        assert 'preflight=pass' in run.stderr
        assert 'warmup=50 iterations=300 tests=20' in run.stderr
        rows = {region: [] for region in REGIONS}
        for line in run.stdout.splitlines():
            if not line.startswith('raw,'):
                continue
            _, region, test, control, candidate = line.split(',')
            assert region in rows and int(test) == len(rows[region])
            rows[region].append((int(control), int(candidate)))
        assert all(len(rows[region]) == 20 for region in REGIONS)
        processes.append({'backend': next(s for s in run.stderr.splitlines() if s.startswith('cpucycles=')),
                          'regions': {region: {
                              'control_cycles': median([row[0] for row in rows[region]]) / 300,
                              'candidate_cycles': median([row[1] for row in rows[region]]) / 300,
                              'delta_cycles': (median([row[1] for row in rows[region]]) -
                                               median([row[0] for row in rows[region]])) / 300,
                              'paired_batch_deltas': [(b-a)/300 for a,b in rows[region]],
                          } for region in REGIONS}})
    summary = {'class': 'mlkem-native-inspired batched SUPERCOP-counter diagnostic, NOT Native SUPERCOP',
               'warmup': 50, 'iterations': 300, 'tests': 20,
               'processes': processes,
               'summary': {region: {
                   'median_launch_delta': median([p['regions'][region]['delta_cycles'] for p in processes]),
                   'favorable_launches': sum(p['regions'][region]['delta_cycles'] < 0 for p in processes),
                   'launches': len(processes),
               } for region in REGIONS}}
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    sources = [REPO / 'bench/mlkem_batch.h', REPO / 'bench/mlkem_batch.c',
               ROOT / 'bench/bench_yang_mlkem_batch.c', ROOT / 'yang.mk',
               ROOT / 'asm/ntruplus768_officialopt_invntt_yang_pair32.s',
               ROOT / 'asm/ntruplus768_officialopt_invntt_yang_stage5reuse.s',
               REPO / 'bench/supercop.lock']
    metadata = {'source_sha256': {str(path.relative_to(REPO)): sha(path) for path in sources},
                'elf_sha256': sha(elf), 'counter': processes[0]['backend'],
                'cpu': 1, 'cpu1_siblings': Path('/sys/devices/system/cpu/cpu1/topology/thread_siblings_list').read_text().strip(),
                'policy': POLICY, 'compiler': subprocess.check_output(['cc', '--version'], text=True).splitlines()[0],
                'placement': 'reversed, ASLR on' if args.reversed_placement else 'normal, ASLR on',
                'copy_plus_inverse_contract': '1536-byte input copy counted per operation',
                'complete_decap_contract': 'valid prepared CT/SK, no reset inside timed batch',
                'source_method': 'mlkem-native test/bench/bench_components_mlkem.c defaults; paired AB/BA extension'}
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(summary['summary'], indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Fixed-relative-layout A/B with fresh processes and SUPERCOP CPU cycles."""
import argparse
import json
import random
import shutil
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from audit_yang_fixed_layout import IMAGES, ROOT, main as audit

REGIONS = ('copy_plus_inverse', 'complete_decap')


def host():
    governor = Path('/sys/devices/system/cpu/cpu1/cpufreq/scaling_governor').read_text().strip()
    no_turbo = Path('/sys/devices/system/cpu/intel_pstate/no_turbo').read_text().strip()
    aslr = Path('/proc/sys/kernel/randomize_va_space').read_text().strip()
    if (governor, no_turbo, aslr) != ('performance', '1', '2'):
        raise RuntimeError(f'host timing gate failed: governor={governor}, no_turbo={no_turbo}, aslr={aslr}')
    return {'cpu': 1, 'governor': governor, 'no_turbo': no_turbo, 'aslr': aslr}


def capture(variant, index, directory, aslr):
    command = ['taskset', '-c', '1']
    if aslr == 'off':
        command += ['setarch', 'x86_64', '-R']
    command += [str(IMAGES[variant])]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    (directory / f'{index:03d}-{variant}.stdout').write_text(result.stdout)
    (directory / f'{index:03d}-{variant}.stderr').write_text(result.stderr)
    assert 'preflight=pass' in result.stderr
    backend = [line for line in result.stderr.splitlines() if line.startswith('cpucycles=')]
    assert len(backend) == 1
    raw = {key: [] for key in REGIONS}
    for line in result.stdout.splitlines():
        fields = line.split(',')
        if len(fields) == 4 and fields[0] == 'raw':
            assert fields[1] in raw
            assert int(fields[2]) == len(raw[fields[1]])
            raw[fields[1]].append(int(fields[3]))
    assert all(len(raw[key]) == 20 for key in REGIONS)
    return {'variant': variant, 'backend': backend[0], 'raw': raw,
            'cycles_per_op': {key: sorted(values)[len(values) // 2] / 300
                              for key, values in raw.items()}}


def ci(values):
    rng = random.Random(76820260923)
    draws = sorted(statistics.median(rng.choices(values, k=len(values))) for _ in range(10000))
    return [draws[249], draws[9750]]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', required=True)
    parser.add_argument('--blocks', type=int, default=10,
                        help='each block has ABBA or BAAB, two fresh launches per arm')
    parser.add_argument('--aslr', choices=('on', 'off'), default='on',
                        help='off uses per-process setarch -R; never changes sysfs')
    args = parser.parse_args()
    assert args.blocks >= 2 and '/' not in args.tag and args.tag not in ('.', '..')
    machine = host()
    subprocess.run(['make', '-j2', 'build/bench_yang_fixed_control',
                    'build/bench_yang_fixed_candidate'], cwd=ROOT, check=True)
    layout = audit()
    directory = ROOT / 'results' / args.tag
    directory.mkdir(parents=True, exist_ok=False)
    for variant, image in IMAGES.items():
        shutil.copy2(image, directory / f'{variant}.elf')
    records = []
    blocks = []
    for block in range(args.blocks):
        order = ('control', 'candidate', 'candidate', 'control') if block % 2 == 0 else (
            'candidate', 'control', 'control', 'candidate')
        group = []
        for variant in order:
            record = capture(variant, len(records), directory, args.aslr)
            record['block'] = block
            records.append(record)
            group.append(record)
        assert len(set(r['backend'] for r in group)) == 1
        block_delta = {region: statistics.mean(r['cycles_per_op'][region]
                        for r in group if r['variant'] == 'candidate') -
                        statistics.mean(r['cycles_per_op'][region]
                        for r in group if r['variant'] == 'control') for region in REGIONS}
        blocks.append({'block': block, 'order': order, 'delta': block_delta})
        print(f'block {block+1}/{args.blocks}: ' + ', '.join(
              f'{region} {block_delta[region]:+.2f}' for region in REGIONS), flush=True)
    assert len(set(r['backend'] for r in records)) == 1
    summary = {}
    for region in REGIONS:
        deltas = [b['delta'][region] for b in blocks]
        arms = {variant: statistics.median(r['cycles_per_op'][region] for r in records
                if r['variant'] == variant) for variant in IMAGES}
        summary[region] = {'arm_process_medians': arms,
                           'median_block_delta': statistics.median(deltas),
                           'bootstrap_95_percent_block_median_ci': ci(deltas),
                           'favorable_blocks': sum(x < 0 for x in deltas),
                           'blocks': len(deltas)}
    output = {'class': 'SUPERCOP-derived fixed-relative-layout diagnostic',
              'date_utc': datetime.now(timezone.utc).isoformat(),
              'machine': machine, 'aslr_for_benchmark': args.aslr,
              'layout': layout, 'backend': records[0]['backend'],
              'batch': {'warmup': 50, 'iterations': 300, 'tests': 20},
              'records': records, 'blocks': blocks, 'summary': summary,
              'interpretation_limit': ('fixed relative ELF layout; process ASLR varies' if args.aslr == 'on'
                                       else 'fixed relative ELF layout and per-process ASLR disabled; other process state varies')}
    (directory / 'summary.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()

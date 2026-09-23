#!/usr/bin/env python3
"""Compile and inspect the local AVX2 q-half butterfly arithmetic probe."""

import hashlib
import json
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from probe_inverse_ct_gauge import ROOT

SOURCE = ROOT / 'tests/test_qhalf_butterfly.c'
RESULT = ROOT / 'results/yang-true-y-twist-qhalf-probe-20260923.json'
FLAGS = ['-O3', '-mavx2', '-Wall', '-Wextra', '-Werror']


def main():
    with tempfile.TemporaryDirectory(prefix='officialopt-qhalf-audit-') as td:
        elf = Path(td) / 'qhalf_probe'
        subprocess.run(['cc', *FLAGS, '-o', str(elf), str(SOURCE)],
                       check=True, capture_output=True)
        test = subprocess.run([str(elf)], check=True, capture_output=True,
                              text=True).stdout.strip()
        symbol = subprocess.check_output(['nm', '-S', str(elf)], text=True)
        probes = {}
        for name in ('officialopt_qhalf_butterfly',
                     'officialopt_qhalf_butterfly_floor'):
            disasm = subprocess.check_output([
                'objdump', '-d', '--no-show-raw-insn',
                '--disassemble=' + name, str(elf)], text=True)
            rows = re.findall(r'^\s*[0-9a-f]+:\s+(\w+)\s*(.*)$', disasm, re.M)
            ops = Counter(op for op, _ in rows)
            assert ops['vpaddw'] >= 2 and ops['ret'] == 1
            assert not any(op.startswith('call') or op == 'vzeroupper' for op in ops)
            assert not any('%rsp' in args or '%rbp' in args for _, args in rows)
            size = int(re.search(
                r'^\S+\s+([0-9a-f]+)\s+T\s+' + name + r'$',
                symbol, re.M)[1], 16)
            probes[name] = {
                'symbol_size_bytes': size,
                'dynamic_instruction_rows_one_call_excluding_ret': len(rows) - 1,
                'opcode_counts': dict(sorted(ops.items())),
                'register_names_used': sorted(set(re.findall(r'%ymm\d+', disasm))),
                'no_stack_spill_call_or_vzeroupper': True,
            }
        assert probes['officialopt_qhalf_butterfly']['opcode_counts']['vpavgw'] == 2
        assert probes['officialopt_qhalf_butterfly_floor']['opcode_counts'].get('vpavgw', 0) == 0
        result = {
            'evidence_class': 'local_AVX2_arithmetic_probe_not_full_inverse_schedule_or_cycles',
            'compiler': subprocess.check_output(['cc', '--version'], text=True).splitlines()[0],
            'flags': FLAGS,
            'probes': probes,
            'test_output': test,
            'test_vectors': 100081,
            'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
            'scope_limit': 'inputs are already-twiddled a,t; full twiddle, routing, tail, constants, scale and 16-YMM allocation remain open',
        }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

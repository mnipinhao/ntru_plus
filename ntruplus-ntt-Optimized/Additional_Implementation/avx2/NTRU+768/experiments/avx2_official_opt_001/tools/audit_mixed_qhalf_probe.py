#!/usr/bin/env python3
"""Inspect the actual linked AVX2 stage-6 mixed butterfly micro-probe."""

import hashlib
import json
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from probe_inverse_ct_gauge import ROOT

SOURCE = ROOT / 'tests/test_mixed_qhalf_butterfly.c'
RESULT = ROOT / 'results/yang-true-y-twist-mixed-qhalf-probe-20260923.json'
NAME = 'officialopt_mixed_qhalf_butterfly'
FLAGS = ['-O3', '-mavx2', '-Wall', '-Wextra', '-Werror']


def main():
    with tempfile.TemporaryDirectory(prefix='officialopt-mixed-qhalf-') as td:
        elf = Path(td) / 'probe'
        subprocess.run(['cc', *FLAGS, '-o', str(elf), str(SOURCE)],
                       check=True, capture_output=True)
        test = subprocess.check_output([str(elf)], text=True).strip()
        disasm = subprocess.check_output([
            'objdump', '-d', '--no-show-raw-insn',
            '--disassemble=' + NAME, str(elf)], text=True)
        rows = re.findall(r'^\s*[0-9a-f]+:\s+(\w+)\s*(.*)$', disasm, re.M)
        ops = Counter(op for op, _ in rows)
        assert ops['vpavgw'] == 2
        assert sum(op.startswith('vpblend') for op in ops) >= 1
        assert ops['ret'] == 1
        assert not any(op.startswith('call') or op == 'vzeroupper'
                       for op in ops)
        assert not any('%rsp' in args or '%rbp' in args for _, args in rows)
        symbols = subprocess.check_output(['nm', '-S', str(elf)], text=True)
        size = int(re.search(r'^\S+\s+([0-9a-f]+)\s+T\s+' + NAME + r'$',
                             symbols, re.M)[1], 16)
        result = {
            'evidence_class': 'isolated_linked_stage6_mixed_butterfly_not_full_inverse_allocation_or_cycles',
            'compiler': subprocess.check_output(['cc', '--version'],
                                                text=True).splitlines()[0],
            'flags': FLAGS,
            'test_output': test,
            'test_vectors': 100025,
            'symbol_size_bytes': size,
            'instruction_rows_excluding_ret': len(rows) - 1,
            'opcode_counts': dict(sorted(ops.items())),
            'register_names_used': sorted(set(re.findall(r'%ymm\d+', disasm))),
            'no_spill_call_or_vzeroupper': True,
            'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
            'scope_limit': 'one stage-6 vector pair; twiddle constants, stage routing and full inverse liveness not included',
        }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

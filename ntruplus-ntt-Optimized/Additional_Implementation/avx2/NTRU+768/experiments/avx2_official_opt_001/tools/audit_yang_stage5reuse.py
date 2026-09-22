#!/usr/bin/env python3
"""Audit the linked stage-5 reuse delta against pair32 in one ELF."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from close_yang_contract import ROOT
from generate_yang_stage5reuse import CONTROL, NAME, OUTPUT, SOURCE


def command(*args):
    return subprocess.check_output(args, text=True)


def rows(elf, symbol):
    dis = command('objdump', '-d', '--no-show-raw-insn', '--disassemble=' + symbol, str(elf))
    result = []
    for line in dis.splitlines():
        match = re.match(r'\s*([0-9a-f]+):\s+(\w+)\s*(.*)', line)
        if match:
            result.append((int(match[1], 16), match[2], match[3]))
    return result, dis


def table_bytes(elf, start, length):
    dump = command('objdump', '-s', '--start-address=' + str(start),
                   '--stop-address=' + str(start + length), str(elf))
    data = bytearray()
    for line in dump.splitlines():
        if re.match(r'^\s+[0-9a-f]+\s', line):
            for group in line.split()[1:5]:
                if re.fullmatch('[0-9a-f]{8}', group):
                    data += bytes.fromhex(group)
    return bytes(data[:length])


def main():
    generation = json.loads((ROOT / 'results/yang-stage5reuse-generation.json').read_text())
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == generation['control_sha256']
    assert hashlib.sha256(OUTPUT.read_bytes()).hexdigest() == generation['asm_sha256']
    elf = ROOT / 'build/test_yang_stage5reuse_raw'
    nm = command('nm', '-S', str(elf))

    def symbol(name):
        match = re.search(r'^([0-9a-f]+)(?: ([0-9a-f]+))? [Ttr] ' + re.escape(name) + '$', nm, re.M)
        assert match, name
        return int(match[1], 16), int(match[2], 16) if match[2] else 0

    control_addr, control_size = symbol(CONTROL)
    candidate_addr, candidate_size = symbol(NAME)
    assert control_addr % 32 == candidate_addr % 32 == 0
    control_rows, control_dis = rows(elf, CONTROL)
    candidate_rows, candidate_dis = rows(elf, NAME)
    assert not re.search(r'%rsp|%rbp|%rbx|%r1[2-5]|\bcall\b|vzeroupper', candidate_dis)
    control_vector = [row for row in control_rows if row[1].startswith('v')]
    candidate_vector = [row for row in candidate_rows if row[1].startswith('v')]
    assert len(control_vector) - len(candidate_vector) == 2
    removed = [row for row in control_vector if row[1] == 'vmovdqa' and
               re.search(r'0x(?:c0|e0)\(%r10\),%ymm(?:15|2)$', row[2])]
    assert len(removed) == 2, removed
    assert [(op, re.findall(r'%ymm\d+', arg)) for _, op, arg in control_vector if
            (_, op, arg) not in removed] == [
            (op, re.findall(r'%ymm\d+', arg)) for _, op, arg in candidate_vector]
    assert [op for _, op, _ in control_rows if op.startswith('j')] == [
        op for _, op, _ in candidate_rows if op.startswith('j')]
    for label in ('yang_pair32_stage5', 'yang_stage5reuse_stage5'):
        assert symbol(label)[0] % 32 == 0
    control_table, _ = symbol('yang_pair32_stage5')
    candidate_table, _ = symbol('yang_stage5reuse_stage5')
    ctable = table_bytes(elf, control_table, 6 * 4 * 64)
    ntable = table_bytes(elf, candidate_table, 6 * 4 * 64)
    assert ctable == ntable and len(ctable) == 1536
    for packet in range(6):
        start = packet * 256
        assert ctable[start + 128:start + 192] == ctable[start + 192:start + 256]
    result = {'class': 'linked same-ELF structural audit, not cycle evidence',
              'control': CONTROL, 'candidate': NAME,
              'entry_alignment': 32,
              'control_symbol_bytes': control_size, 'candidate_symbol_bytes': candidate_size,
              'control_instruction_rows': len(control_rows),
              'candidate_instruction_rows': len(candidate_rows),
              'control_vector_rows': len(control_vector),
              'candidate_vector_rows': len(candidate_vector),
              'removed_static_loads': 2, 'stage5_public_iterations': 6,
              'removed_dynamic_constant_loads': 12,
              'unchanged_other_opcode_and_YMM_defuse': True,
              'byte_identical_stage5_constant_tables': True,
              'no_stack_call_vzeroupper_or_callee_saved_clobber': True,
              'control_constant_table_sha256': hashlib.sha256(ctable).hexdigest(),
              'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
              'candidate_asm_sha256': generation['asm_sha256']}
    (ROOT / 'results/yang-stage5reuse-linked.json').write_text(json.dumps(result, indent=2) + '\n')
    (ROOT / 'results/yang-stage5reuse-disassembly.txt').write_text(candidate_dis)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

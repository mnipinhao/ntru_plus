#!/usr/bin/env python3
"""Prove that fixed-layout A/B images differ only inside the inverse symbol."""
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from close_yang_contract import ROOT

SYMBOL = 'ntruplus768_officialopt_invntt_yang_fixed'
IMAGES = {v: ROOT / 'build' / f'bench_yang_fixed_{v}' for v in ('control', 'candidate')}


def run(*args):
    return subprocess.check_output(args, text=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(image):
    result = {}
    for line in run('nm', '-S', '-n', str(image)).splitlines():
        fields = line.split()
        if len(fields) == 4 and fields[2].lower() in ('t', 'r', 'd', 'b'):
            result[fields[3]] = (int(fields[0], 16), int(fields[1], 16), fields[2])
    return result


def section(image, name):
    for line in run('objdump', '-h', str(image)).splitlines():
        m = re.match(r'\s*\d+\s+' + re.escape(name) + r'\s+([0-9a-f]+)\s+([0-9a-f]+)', line)
        if m:
            return int(m[2], 16), int(m[1], 16)
    raise AssertionError(f'missing {name}: {image}')


def section_bytes(image, name, directory):
    target = directory / f'{image.name}.{name}'
    run('objcopy', '--dump-section', f'{name}={target}', str(image))
    return target.read_bytes()


def main():
    generation = json.loads((ROOT / 'results/yang-fixed-layout-generation.json').read_text())
    for variant, metadata in generation['variants'].items():
        assert sha(ROOT / metadata['overlay_path']) == metadata['overlay_sha256']
    syms = {v: symbols(p) for v, p in IMAGES.items()}
    assert syms['control'] == syms['candidate'], 'symbol addresses/sizes differ'
    address, size, _ = syms['control'][SYMBOL]
    assert address % 32 == 0 and size == 2692
    assert section(IMAGES['control'], '.text') == section(IMAGES['candidate'], '.text')
    assert section(IMAGES['control'], '.rodata') == section(IMAGES['candidate'], '.rodata')
    with tempfile.TemporaryDirectory(prefix='yang-fixed-audit-') as temp:
        directory = Path(temp)
        texts = {v: section_bytes(p, '.text', directory) for v, p in IMAGES.items()}
        rodata = {v: section_bytes(p, '.rodata', directory) for v, p in IMAGES.items()}
    assert rodata['control'] == rodata['candidate'], '.rodata differs'
    text_start, _ = section(IMAGES['control'], '.text')
    offset = address - text_start
    assert texts['control'][:offset] == texts['candidate'][:offset], 'code before inverse differs'
    assert texts['control'][offset + size:] == texts['candidate'][offset + size:], 'code after inverse differs'
    changed = [i for i in range(size) if texts['control'][offset+i] != texts['candidate'][offset+i]]
    assert changed, 'inverse has no byte difference'
    result = {
        'class': 'linked fixed-relative-layout audit',
        'symbol': SYMBOL, 'address': address, 'size': size,
        'text_section': {'start': text_start, 'size': len(texts['control'])},
        'rodata_size': len(rodata['control']),
        'all_sized_symbols_equal': True, 'text_outside_symbol_bit_exact': True,
        'rodata_bit_exact': True, 'changed_function_bytes': len(changed),
        'changed_offsets_first_last': [changed[0], changed[-1]],
        'image_sha256': {v: sha(p) for v, p in IMAGES.items()},
        'source_manifest': generation,
        'limitation': 'ASLR absolute base remains independently randomized across processes'
    }
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    main()

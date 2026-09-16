#!/usr/bin/env python3
"""P3B24: reuse frozen P3B12 harness, substitute only FromBytes."""
from pathlib import Path
import json
HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'gt_fr0_d1_input_once_frombytes_full_kem'
P23 = HERE.parent / 'gt_fr0_d1_cluster_transpose_frombytes'

def main():
    config = HERE / 'build/config'
    config.mkdir(parents=True, exist_ok=True)
    wrapper = (BASE / 'byte_api.c').read_text()
    wrapper = wrapper.replace('#include "input_once_frombytes.h"', '#include "input_once_frombytes.h"\n#include "cluster_transpose_frombytes.h"')
    wrapper = wrapper.replace('    gt864_fr0_input_once_frombytes(out->coeffs, in);', '    gt864_fr0_cluster_transpose_frombytes(out->coeffs, in);')
    wrapper = wrapper.replace('    c1_from(out->coeffs, in);', '    gt864_fr0_input_once_frombytes(out->coeffs, in);')
    (config / 'byte_api.c').write_text(wrapper)
    makefile = (BASE / 'pi5-Makefile').read_text().replace('BYTE := ', 'BYTE := $(BUILD)/cluster_transpose_frombytes.o ')
    (config / 'pi5-Makefile').write_text(makefile)
    source = (BASE / 'run_pi5.py').read_text()
    anchor = '    sources = {\n'
    assert source.count(anchor) == 1
    source = source.replace(anchor, '    command(["python3", str(P23 / "prepare.py")])\n' + anchor + '        "cluster_transpose_frombytes.c": P23 / "build/cluster_transpose_frombytes.c",\n        "cluster_transpose_frombytes.h": P23 / "cluster_transpose_frombytes.h",\n')
    source = source.replace('"experiment": "D1-P3B12"', '"experiment": "D1-P3B24"')
    namespace = {'__file__': str(BASE / 'run_pi5.py'), '__name__': 'frozen_p3b12'}
    exec(compile(source, str(BASE / 'run_pi5.py'), 'exec'), namespace)
    namespace.update(HERE=config, OUT=HERE/'build', P23=P23,
                     REMOTE='/home/pi/ntruplus-experiments/gt864-p3b24-transpose-full-kem')
    import sys
    if '--audit-only' not in sys.argv:
        namespace['main']()
    audit = namespace['ssh']('cd /home/pi/ntruplus-experiments/gt864-p3b24-transpose-full-kem && objdump -dr build/byte_api.o && objdump -dr build/kem_gt_base.o && objdump -dr build/kem_gt_bytes.o && objdump -d build/cluster_transpose_frombytes.o && sha256sum build/test-kem build/bench-kem')
    (HERE/'build/raw/substitution-audit.log').write_text(audit)
    assert 'gt864_fr0_input_once_frombytes' in audit
    assert 'gt864_fr0_cluster_transpose_frombytes' in audit
    calls = {}
    import re
    for variant in ('base', 'bytes'):
        obj = audit.split(f'build/kem_gt_{variant}.o:',1)[1].split('build/',1)[0]
        functions = {}
        for match in re.finditer(r'^\w+ <([^>]+)>:\n(.*?)(?=\n\n|\Z)', obj, re.M|re.S):
            functions[match.group(1)] = re.findall(r'R_AARCH64_(?:CALL26|JUMP26)\s+(\S+)', match.group(2))
        target = 'p3b12_base_frombytes' if variant == 'base' else 'p3b12_candidate_frombytes'
        def count_calls(symbol, seen=()):
            assert symbol not in seen
            return sum(1 if callee == target else count_calls(callee.removeprefix('.text.'), seen+(symbol,)) if callee.removeprefix('.text.') in functions else 0 for callee in functions[symbol])
        for suffix, expected in (('keypair',0), ('enc',1), ('dec',3)):
            symbol = f'gt_{variant}_crypto_kem_{suffix}'
            count = count_calls(symbol)
            assert count == expected, (symbol,count,expected)
            calls[symbol] = count
    (HERE/'build/call-ledger.json').write_text(json.dumps(calls,indent=2)+'\n')
    print('p3b24_substitution_and_call_ledger=pass')

if __name__ == '__main__':
    main()

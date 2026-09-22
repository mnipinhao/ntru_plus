#!/usr/bin/env python3
"""Keep the equal stage-5 twiddle pair resident across two CT butterflies."""
import hashlib
import json
from pathlib import Path

from close_yang_contract import ROOT

CONTROL = 'ntruplus768_officialopt_invntt_yang_pair32'
NAME = 'ntruplus768_officialopt_invntt_yang_stage5reuse'
SOURCE = ROOT / 'asm' / (CONTROL + '.s')
OUTPUT = ROOT / 'asm' / (NAME + '.s')
PREFIX = 'vmovdqa 128(%r10), %ymm15\nvmovdqa 160(%r10), %ymm2\n'
REMOVED = 'vmovdqa 192(%r10), %ymm15\nvmovdqa 224(%r10), %ymm2\n'


def generate():
    control = SOURCE.read_text()
    research = json.loads((ROOT / 'results/yang-constant-reuse-research.json').read_text())
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == research['source_sha256'][str(SOURCE.relative_to(ROOT))]
    assert research['stage5_same_packet_reuse']['removed_loads_per_call'] == 12
    stage5 = control.split('# CT stage 5:', 1)[1].split('#shuffle', 1)[0]
    assert stage5.count(PREFIX) == stage5.count(REMOVED) == 1
    between = stage5.split(PREFIX, 1)[1].split(REMOVED, 1)[0]
    assert not any(line.strip().endswith(('%ymm15', '%ymm2')) for line in between.splitlines())
    # The table-byte identity and six-packet traversal are checked by the
    # research proof and independently again by the linked audit.
    output = control.replace(REMOVED, '', 1).replace('yang_pair32', 'yang_stage5reuse')
    assert output.count('vmovdqa 192(%r10), %ymm15') == 0
    assert output.count('vmovdqa 224(%r10), %ymm2') == 0
    OUTPUT.write_text(output)
    result = {'class': 'namespaced same-DAG ASM candidate, not linked or cycle evidence',
              'name': NAME, 'control': CONTROL,
              'removed_stage5_loads_per_loop': 2, 'stage5_iterations': 6,
              'removed_constant_vector_loads_per_inverse': 12,
              'control_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'asm_sha256': hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
              'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT / 'results/yang-stage5reuse-generation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    generate()

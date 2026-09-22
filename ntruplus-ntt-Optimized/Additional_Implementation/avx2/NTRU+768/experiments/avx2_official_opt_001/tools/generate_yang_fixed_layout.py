#!/usr/bin/env python3
"""Create same-name inverse overlays for separate fixed-layout ELF builds."""
import hashlib
import json
from pathlib import Path

from close_yang_contract import ROOT

FIXED = 'ntruplus768_officialopt_invntt_yang_fixed'
SOURCES = {
    'control': ('ntruplus768_officialopt_invntt_yang_pair32', 'yang_pair32'),
    'candidate': ('ntruplus768_officialopt_invntt_yang_stage5reuse', 'yang_stage5reuse'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = {'class': 'fixed-symbol research overlays; no timing',
              'symbol': FIXED, 'variants': {}}
    for variant, (symbol, prefix) in SOURCES.items():
        source = ROOT / 'asm' / (symbol + '.s')
        target = ROOT / 'asm' / ('yang_fixed_' + variant + '.s')
        content = source.read_text()
        assert content.count(symbol + ':') == 1
        content = content.replace(symbol, FIXED).replace(prefix, 'yang_fixed')
        assert '.p2align 5\n' + FIXED + ':' in content
        target.write_text(content)
        result['variants'][variant] = {
            'source_sha256': sha(source), 'overlay_sha256': sha(target),
            'overlay_path': str(target.relative_to(ROOT))}
    control = (ROOT / 'asm/yang_fixed_control.s').read_text()
    candidate = (ROOT / 'asm/yang_fixed_candidate.s').read_text()
    removed = 'vmovdqa 192(%r10), %ymm15\nvmovdqa 224(%r10), %ymm2\n'
    assert control.replace(removed, '', 1) == candidate
    result['only_source_change'] = 'remove two stage-5 constant loads'
    result['generator_sha256'] = sha(Path(__file__))
    (ROOT / 'results/yang-fixed-layout-generation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

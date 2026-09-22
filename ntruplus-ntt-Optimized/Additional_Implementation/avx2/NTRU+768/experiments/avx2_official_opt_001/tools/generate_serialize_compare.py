#!/usr/bin/env python3
"""Pinned, same-arithmetic serializer with a read-only wire comparison sink."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    control = ROOT / 'qualification/avx2-officialopt-caller-lazy-qual001'
    manifest = json.loads(control.with_suffix('.json').read_text())
    for name, expected in manifest['files_sha256'].items():
        assert sha(control / name) == expected, name
    source = ROOT / 'upstream/supercop-avx2/pack.s'
    assert sha(source) == manifest['files_sha256']['pack.s']
    body = source.read_text().split('.global poly_frombytes')[0]
    body = body.replace('poly_tobytes', 'ntruplus768_officialopt_serialize_compare')
    body = body.replace('.global ', '.text\n.p2align 5\n.global ', 1)
    body = body.replace('vmovdqa _16xv', 'xor %eax, %eax\nvmovdqa _16xv', 1)
    start = body.index('vmovdqu %ymm0,')
    end = body.index('add $192, %rdi', start)
    sink = ''.join(f'vpxor {32*i}(%rdi), %ymm{i}, %ymm{i}\n' for i in range(6))
    sink += ''.join(f'vpor %ymm{i}, %ymm0, %ymm0\n' for i in range(1,6))
    sink += 'vptest %ymm0, %ymm0\nsetnz %dl\nmovzbl %dl, %edx\nor %edx, %eax\n\n'
    body = body[:start] + sink + body[end:]
    body += '.size ntruplus768_officialopt_serialize_compare, .-ntruplus768_officialopt_serialize_compare\n.section .note.GNU-stack,"",@progbits\n'
    (ROOT / 'asm/ntruplus768_officialopt_serialize_compare.s').write_text(body)
    kem = (control / 'kem.c').read_text()
    old = '\tpoly_tobytes(buf2, &f);\n\t\n\tfail |= verify(buf1, buf2, NTRUPLUS_POLYBYTES);'
    assert kem.count(old) == 1
    kem = kem.replace(old, '\tfail |= ntruplus768_officialopt_serialize_compare(buf1, &f);')
    kem = kem.replace('#include "poly.h"', '#include "poly.h"\nint ntruplus768_officialopt_serialize_compare(const uint8_t *, const poly *);')
    (ROOT / 'src/kem_serialize_compare.c').write_text(kem)
    out = ROOT / 'results/serialize-compare-control.json'
    out.write_text(json.dumps({'control': manifest, 'scope': 'research; no promotion',
        'pack_source_sha256': sha(source),
        'asm_sha256': sha(ROOT / 'asm/ntruplus768_officialopt_serialize_compare.s'),
        'kem_sha256': sha(ROOT / 'src/kem_serialize_compare.c'),
        'per_call': {'blocks': 6, 'removed_vector_stores': 36,
                     'wire_vector_loads': 36, 'packing_arithmetic': 'unchanged'},
        'contract': 'wire input 1152 bytes, polynomial aligned 32 bytes; readonly; returns 0/1'}, indent=2)+'\n')

if __name__ == '__main__':
    main()

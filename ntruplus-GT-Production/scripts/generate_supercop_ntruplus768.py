#!/usr/bin/env python3
"""Materialize the NTRU+768 Official-shell / GT-polynomial SUPERCOP leaf."""
from pathlib import Path
import argparse, subprocess, tempfile

OFFICIAL_COPY = (
    'api.h','params.h','util.h','fips202.c','fips202.h','symmetric.c',
    'symmetric.h','cbd.s','architectures','goal-constbranch','goal-constindex')
GT_COPY = (
    'kem.c','keygen.c','keygen_lambda.c','basemul_lambda.c','poly.h','layout.h',
    'ntt.h','decap_verify.h','keygen.h')
GT_ASM = {'ntt.S':'ntt.s','base.S':'base.s','pack.S':'pack.s',
          'add.S':'add.s','kem_api.S':'kem_api.s'}

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data if isinstance(data,bytes) else data.encode())

def build(gt,official,target):
    assert not target.exists(), f'use a fresh package root: {target}'
    leaf=target/'crypto_kem/ntruplus768/aarch64'
    leaf.mkdir(parents=True)
    def add(name,data):
        write(leaf/name,data)
    for name in OFFICIAL_COPY:
        add(name,(official/name).read_bytes())
    crep=(official/'crepmod3.s').read_bytes()
    renamed=crep.replace(b'poly_crepmod3',b'official_poly_crepmod3')
    add('crepmod3.s',renamed)
    for name in GT_COPY:
        add(name,(gt/name).read_bytes())
    for source,name in GT_ASM.items():
        data=subprocess.check_output(['gcc','-E','-P','-x','assembler-with-cpp',
                                      '-I'+str(gt),str(gt/source)])
        add(name,data)
    adapter='''#include "poly.h"\n#include <string.h>\n\nextern void official_poly_crepmod3(poly *r);\n\n/* GT uses a two-pointer exact-alias contract; Official is in-place. */\nvoid poly_crepmod3(poly *out, const poly *in)\n{\n    if (out != in)\n        memcpy(out, in, sizeof(*out));\n    official_poly_crepmod3(out);\n}\n'''
    add('crepmod3_adapter.c',adapter)
    add('LICENSE',(gt/'LICENSE').read_bytes())
    write(target/'README.md','''# NTRU+768 AArch64 Official-shell / GT-polynomial package

Drop `crypto_kem/ntruplus768/aarch64` into a SUPERCOP tree. Official CBD/SOTP,
centered mod-3, NO_CE hash, utility clearing and public headers are retained.
The NTT, inverse NTT, base arithmetic, pack/unpack and their operation-specific
KEM call sites use the GT Production backend.
''')

def compare(expected,actual):
    e={str(x.relative_to(expected)):x.read_bytes() for x in expected.rglob('*') if x.is_file()}
    a={str(x.relative_to(actual)):x.read_bytes() for x in actual.rglob('*') if x.is_file()}
    if e!=a:
        missing=sorted(set(e)-set(a));extra=sorted(set(a)-set(e))
        changed=sorted(k for k in set(e)&set(a) if e[k]!=a[k])
        raise SystemExit(f'package drift: missing={missing} extra={extra} changed={changed}')

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('generate','check'))
    p.add_argument('--gt-root',type=Path,required=True);p.add_argument('--official-root',type=Path,required=True)
    p.add_argument('--package-root',type=Path,required=True);a=p.parse_args()
    if a.mode=='generate':build(a.gt_root.resolve(),a.official_root.resolve(),a.package_root.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='gt768-supercop-check-') as d:
            generated=Path(d)/'SUPERCOP';build(a.gt_root.resolve(),a.official_root.resolve(),generated)
            compare(generated,a.package_root.resolve())
        print('materialized package: deterministic match')
if __name__=='__main__':main()

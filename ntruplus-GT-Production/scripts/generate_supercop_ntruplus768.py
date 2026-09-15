#!/usr/bin/env python3
"""Materialize the NTRU+768 Official-shell / GT-polynomial SUPERCOP leaf."""
from pathlib import Path
import argparse, subprocess, tempfile

OFFICIAL_COPY = (
    'api.h','params.h','util.h','symmetric.h','cbd.s','architectures',
    'goal-constbranch','goal-constindex')
GT_COPY = (
    'kem.c','keygen.c','keygen_lambda.c','basemul_lambda.c','poly.h','layout.h',
    'ntt.h','decap_verify.h','keygen.h','fips202.c','fips202.h','symmetric.c')
GT_ASM = {'ntt.S':'ntt.s','base.S':'base.s','pack.S':'pack.s',
          'add.S':'add.s','kem_api.S':'kem_api.s',
          'keccakf1600.S':'keccakf1600.s'}
# Keep feature-gated assembly in preprocessed form.  SUPERCOP supplies the
# effective target flags (normally -march=native) for each compiler record;
# preprocessing this file while packaging would freeze the packager host's
# feature set into the checked-in leaf.
GT_FEATURE_ASM = ('keccakf1600_v84a.S',)

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
        # The checked-in SUPERCOP leaf targets ELF AArch64.  Do not let the
        # packaging host (for example macOS) select Mach-O assembly branches.
        data=subprocess.check_output(['gcc','-E','-P','-x','assembler-with-cpp',
                                      '-U__APPLE__','-D__ELF__=1',
                                      '-I'+str(gt),str(gt/source)])
        if source == 'keccakf1600.S':
            data=b'''/*
 * Copyright (c) The mlkem-native project authors
 * Copyright (c) 2021-2022 Arm Limited
 * Copyright (c) 2022 Matthias Kannwischer
 * SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT
 * Upstream revision: 0924122d0e92b2d682fab5d5e5e2593ec84c8a1f
 */
'''+data
        add(name,data)
    for name in GT_FEATURE_ASM:
        add(name,(gt/name).read_bytes())
    adapter='''#include "poly.h"\n#include <string.h>\n\nextern void official_poly_crepmod3(poly *r);\n\n/* GT uses a two-pointer exact-alias contract; Official is in-place. */\nvoid poly_crepmod3(poly *out, const poly *in)\n{\n    if (out != in)\n        memcpy(out, in, sizeof(*out));\n    official_poly_crepmod3(out);\n}\n'''
    add('crepmod3_adapter.c',adapter)
    add('LICENSE',(gt/'LICENSE').read_bytes())
    write(target/'README.md','''# NTRU+768 AArch64 Official-shell / GT-polynomial package

Drop `crypto_kem/ntruplus768/aarch64` into a SUPERCOP tree. Official CBD/SOTP,
centered mod-3, NO_CE hash, utility clearing and public headers are retained.
The NTT, inverse NTT, base arithmetic, pack/unpack and their operation-specific
KEM call sites use the GT Production backend. The public SHAKE and symmetric
hash APIs remain unchanged. Hash-f/hash-h retain their existing construction;
hash-g uses the fixed-size register-resident AArch64 sponge. Generic SHAKE uses
the standalone AArch64 x1 Keccak-f[1600] backend. The lowercase scalar
assembly is always available. The uppercase feature-gated assembly and
`fips202.c` select the Arm SHA3 backend only when the SUPERCOP compiler flags
define `__ARM_FEATURE_SHA3`; otherwise the leaf remains safe on Cortex-A76.
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

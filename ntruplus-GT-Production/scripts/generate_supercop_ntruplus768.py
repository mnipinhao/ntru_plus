#!/usr/bin/env python3
"""Materialize the NTRU+768 Official-shell / GT-polynomial SUPERCOP leaf."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, tempfile

OFFICIAL_COPY = (
    'api.h','params.h','util.h','fips202.c','fips202.h','symmetric.c',
    'symmetric.h','cbd.s','architectures','goal-constbranch','goal-constindex')
GT_COPY = (
    'kem.c','keygen.c','keygen_lambda.c','basemul_lambda.c','poly.h','layout.h',
    'ntt.h','decap_verify.h','keygen.h')
GT_ASM = {'ntt.S':'ntt.s','base.S':'base.s','pack.S':'pack.s',
          'add.S':'add.s','kem_api.S':'kem_api.s'}
GENERATED_METADATA = ('SOURCE-MAP.json','SOURCE-MAP.md','SOURCE-MANIFEST.sha256',
                      'FUNCTION-MAP.md','BUILD-CONTRACT.md')

def sha(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data if isinstance(data,bytes) else data.encode())

def build(gt,official,target,gt_revision,official_identity):
    assert not target.exists(), f'use a fresh package root: {target}'
    leaf=target/'crypto_kem/ntruplus768/aarch64'
    meta=target/'metadata/ntruplus768-aarch64-gt';leaf.mkdir(parents=True);meta.mkdir(parents=True)
    mapping=[]
    def add(name,data,origin,source,transform='copy'):
        write(leaf/name,data);mapping.append({'output':name,'origin':origin,
          'source':source,'transform':transform,'source_sha256':sha(data) if transform=='copy' else None,
          'output_sha256':sha(data)})
    for name in OFFICIAL_COPY:
        data=(official/name).read_bytes();add(name,data,'Official',name)
    crep=(official/'crepmod3.s').read_bytes()
    renamed=crep.replace(b'poly_crepmod3',b'official_poly_crepmod3')
    add('crepmod3.s',renamed,'Official','crepmod3.s','symbol rename only')
    mapping[-1]['source_sha256']=sha(crep)
    for name in GT_COPY:
        add(name,(gt/name).read_bytes(),'GT Production',name)
    for source,name in GT_ASM.items():
        data=subprocess.check_output(['gcc','-E','-P','-x','assembler-with-cpp',
                                      '-I'+str(gt),str(gt/source)])
        add(name,data,'GT Production',source,'Linux GCC preprocessing')
        mapping[-1]['source_sha256']=sha((gt/source).read_bytes())
    adapter='''#include "poly.h"\n#include <string.h>\n\nextern void official_poly_crepmod3(poly *r);\n\n/* GT uses a two-pointer exact-alias contract; Official is in-place. */\nvoid poly_crepmod3(poly *out, const poly *in)\n{\n    if (out != in)\n        memcpy(out, in, sizeof(*out));\n    official_poly_crepmod3(out);\n}\n'''
    add('crepmod3_adapter.c',adapter,'generated','Official/GT ABI seam','generated adapter')
    add('LICENSE',(gt/'LICENSE').read_bytes(),'GT Production','LICENSE')
    manifest=''.join(f"{sha((leaf/m['output']).read_bytes())}  crypto_kem/ntruplus768/aarch64/{m['output']}\n"
                     for m in sorted(mapping,key=lambda x:x['output']))
    source_map={'format':1,'parameter_set':'NTRU+768','architecture':'aarch64',
      'gt_revision':gt_revision,'official_identity':official_identity,
      'policy':'Official support/hash/public API; GT operation-specific polynomial backend',
      'files':sorted(mapping,key=lambda x:x['output'])}
    write(meta/'SOURCE-MAP.json',json.dumps(source_map,indent=2)+'\n')
    rows=['# Source map','','| Output | Origin | Source | Transformation |','|---|---|---|---|']
    rows += [f"| `{m['output']}` | {m['origin']} | `{m['source']}` | {m['transform']} |"
             for m in source_map['files']]
    write(meta/'SOURCE-MAP.md','\n'.join(rows)+'\n')
    write(meta/'SOURCE-MANIFEST.sha256',manifest)
    write(meta/'FUNCTION-MAP.md','''# Function map

The public SUPERCOP ABI is unchanged. `kem_api.s` preserves the public-call
ABI and dispatches to the operation-specific GT orchestration in `kem.c`.

| KEM path | Serialization / support | Transform and base arithmetic |
|---|---|---|
| `crypto_kem_keypair` | Official `poly_cbd1`; GT `poly_tobytes_keygen_cq` | `poly_ntt_keygen_cq`, `poly_baseinv_keygen_cq_scaled_r`, `poly_basemul_keygen_cq_scaled_r` |
| `crypto_kem_enc` | Official `poly_cbd1`; GT checked `poly_frombytes_encap` and loose/canonical pack | `poly_ntt_encap_small_lazy`, `poly_ntt_loose`, `poly_basemul_add_encap` |
| `crypto_kem_dec` | Official SOTP and centered `crepmod3`; GT ciphertext unpack/pack | `poly_ntt_decap`, `poly_frombytes_basemul_decap_scale`, `poly_basemul_decap`, `poly_invntt_decap_scale` |

Assembly ownership:

- `ntt.s`: operation-specific forward and inverse GT transforms and tables.
- `base.s`: Keygen inversion helpers and Encap/Decap base multiplication.
- `pack.s`: checked public-key decode and operation-specific serialization.
- `add.s`: polynomial subtraction and tripling used by the GT call sites.
- `cbd.s`: byte-for-byte Official CBD/SOTP source.
- `crepmod3.s`: Official centered mod-3 body with an internal symbol rename;
  `crepmod3_adapter.c` supplies the GT two-pointer contract.

There is deliberately no generic `poly_ntt`/generic basemul compatibility
layer in this leaf. The public boundary is the three SUPERCOP KEM functions.
''')
    write(meta/'BUILD-CONTRACT.md','''# Build contract

- Target: Linux AArch64, NTRU+768.
- Compile every top-level `.c` and `.s` in the leaf; SUPERCOP supplies
  `crypto_kem.h`, `randombytes.h`, randombytes and cryptoint support.
- Required public symbols: `crypto_kem_keypair`, `crypto_kem_enc`,
  `crypto_kem_dec`.
- `kem_api.s` preserves d8-d15 once at each public KEM boundary.
- No namespace adapter is present: this leaf is one standalone implementation.
- Recreate assembly with Linux `gcc -E -P -x assembler-with-cpp`.
''')
    write(target/'README.md','''# NTRU+768 AArch64 Official-shell / GT-polynomial package

Drop `crypto_kem/ntruplus768/aarch64` into a SUPERCOP tree. Official CBD/SOTP,
centered mod-3, NO_CE hash, utility clearing and public headers are retained.
The NTT, inverse NTT, base arithmetic, pack/unpack and their operation-specific
KEM call sites use the GT Production backend. See `metadata/` for provenance.
''')

def compare(expected,actual):
    e={str(x.relative_to(expected)):x.read_bytes() for x in expected.rglob('*') if x.is_file()}
    a={str(x.relative_to(actual)):x.read_bytes() for x in actual.rglob('*') if x.is_file()
       and x.name!='VALIDATION.md'}
    if e!=a:
        missing=sorted(set(e)-set(a));extra=sorted(set(a)-set(e))
        changed=sorted(k for k in set(e)&set(a) if e[k]!=a[k])
        raise SystemExit(f'package drift: missing={missing} extra={extra} changed={changed}')

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('generate','check'))
    p.add_argument('--gt-root',type=Path,required=True);p.add_argument('--official-root',type=Path,required=True)
    p.add_argument('--package-root',type=Path,required=True);p.add_argument('--gt-revision',required=True)
    p.add_argument('--official-identity',required=True);a=p.parse_args()
    if a.mode=='generate':build(a.gt_root.resolve(),a.official_root.resolve(),a.package_root.resolve(),a.gt_revision,a.official_identity)
    else:
        with tempfile.TemporaryDirectory(prefix='gt768-supercop-check-') as d:
            generated=Path(d)/'SUPERCOP';build(a.gt_root.resolve(),a.official_root.resolve(),generated,a.gt_revision,a.official_identity)
            compare(generated,a.package_root.resolve())
        print('materialized package: deterministic match')
if __name__=='__main__':main()

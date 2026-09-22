#!/usr/bin/env python3
"""Archive exact hashed compile inputs, including pre-hook harness revisions.

The old harness is recovered only if its content hash matches the recorded
compile input. No raw observations, metadata or old summary is overwritten.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

def digest(data):return hashlib.sha256(data).hexdigest()

def prior_bench(text):
    # The two additions were conditional identity14-only blocks. Remove only
    # those blocks to reconstruct the original eager harness byte-for-byte.
    lines=text.splitlines(keepends=True);out=[];active=True;inside=False
    for line in lines:
        if line=='#ifdef FN_PACK_IDENTITY14\n':assert not inside;inside=True;active=False
        elif inside and line=='#else\n':active=True
        elif inside and line=='#endif\n':inside=False;active=True
        elif active:out.append(line)
    assert not inside
    return ''.join(out)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('campaign',type=Path);a=ap.parse_args()
    root=a.campaign.resolve();meta=json.loads((root/'metadata.json').read_text())
    target=root/'compile-inputs';target.mkdir(exist_ok=True)
    manifest={}
    for n,(name,expected) in enumerate(meta['source_sha256'].items()):
        p=Path(name);data=p.read_bytes();method='current source matches recorded digest'
        candidates=[data]
        if p.name=='bench_encap_fn.c':
            text=data.decode();candidates.append(prior_bench(text).encode())
            candidates.append(text.replace('void ntruplus768_exp001_pack_identity14_highrange(uint8_t*,const int16_t*);\n','').replace(
                'ntruplus768_exp001_pack_identity14_highrange(s->cb,s->c);','ntruplus768_exp001_pack_identity14(s->cb,s->c);').encode())
        if p.name=='pack_identity14.S':
            candidates.append(re.sub(r'\.section \.text.gt768_pack_identity14_highrange,.*?(?=\.section \.rodata)',
                                     '',data.decode(),flags=re.S).encode())
        matches=[v for v in candidates if digest(v)==expected]
        assert matches,('cannot reconstruct exact recorded source',name,expected)
        data=matches[0]
        if data!=p.read_bytes():method='historical harness/source revision reconstructed and SHA-256 verified'
        filename=f'{n:02d}-{p.name}';dest=target/filename
        if dest.exists():assert dest.read_bytes()==data
        else:dest.write_bytes(data)
        manifest[name]={'saved':filename,'sha256':expected,'method':method}
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print('PASS all recorded compile-input hashes archived',root.name)

if __name__=='__main__':main()

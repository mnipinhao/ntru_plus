#!/usr/bin/env python3
"""Install only the proved mask/store serializer into a new disposable impl."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from install_encap_eager import EXP,REPO,CLEAN,sha
from generate_pack_triad import build

NAME='avx2-gt32-maskstore-exp-sc20260831'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--campaign-root',type=Path,required=True)
    a=ap.parse_args()
    qualified=EXP/'results/pack-maskstore-triad-serious-20260922'
    meta=json.loads((qualified/'metadata.json').read_text())
    results=json.loads((qualified/'summary.json').read_text())
    assert meta['fresh_processes']==9
    assert results['full_polynomial_island']['deltas']['M-C']['favorable']==9
    assert all(sha(CLEAN/p)==h for p,h in meta['clean_manifest'].items())
    assert sha(EXP/'generated/pack_triad.S')==meta['source_sha256'][str(EXP/'generated/pack_triad.S')]
    subprocess.run([sys.executable,str(REPO/'scripts/install_supercop_768_clean.py'),
        '--campaign-root',str(a.campaign_root),'--implementation',NAME],check=True)
    target=a.campaign_root/'crypto_kem/ntruplus768'/NAME
    path=target/'pack.s';original=path.read_text()
    symbol='ntruplus768_pack_m_lazy10788_avx2'
    begin=original.index(symbol+':\n')
    end=original.index(' .size '+symbol,begin)
    _,model=build()
    # Keep original section, symbol, 5120-byte cage, inherited vzeroupper,
    # highrange tail jump and all other functions. Do not copy 3 test bodies.
    body='\n'.join(model['paths']['m']).replace('.Lmask_228','.Lq24_pack_mask')
    for imm in (30,75,177):body=body.replace(f'.Lmask_{imm}',f'.Lqualified_mask_{imm}')
    text=original[:begin]+symbol+':\n.Lq24_lazy_cage_begin:\n'+body+'\n .org .Lq24_lazy_cage_begin + 5120, 0x90\n'+original[end:]
    text+='\n.section .rodata.gt768_qualified_masks,"a",@progbits\n'
    for imm in (30,75,177):
        values,_=model['constants'][f'.Lmask_{imm}']
        text+=f'.p2align 5\n.Lqualified_mask_{imm}:\n.byte '+','.join(map(str,values))+'\n'
    path.write_text(text)
    manifest=target/'SOURCE-MANIFEST.json';record=json.loads(manifest.read_text())
    record.update(qualification='experimental, not clean promotion',delta={
        'files':['pack.s'],'callers':'Encap lazy/highrange only; Decap centered and Keygen P serializer unchanged',
        'kernel_sha256':sha(EXP/'generated/pack_triad.S'),'serious_metadata_sha256':sha(qualified/'metadata.json'),
        'extra_mask_bytes':96,'same_original_section_and_cage':True,'test_wrapper_installed':False,
        'eager':False,'prefixed_hash_buffer':False})
    manifest.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    (target/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(target.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))
    print(target)

if __name__=='__main__':main()

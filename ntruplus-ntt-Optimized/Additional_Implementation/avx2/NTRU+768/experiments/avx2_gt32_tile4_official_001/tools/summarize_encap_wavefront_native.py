#!/usr/bin/env python3
"""Summarize the three serial Native runs without mixing in island cycles."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def main():
    ap=argparse.ArgumentParser();ap.add_argument('campaign',type=Path)
    args=ap.parse_args();root=args.campaign
    out=root/'summary.json'
    if out.exists():raise SystemExit(f'refusing overwrite: {out}')
    records={}
    for name in ('official','current-gt','wavefront1'):
        path=root/f'native-{name}'
        result=json.loads((path/'stq-summary.json').read_text())
        sizes={}
        for line in subprocess.check_output(['size','-A',str(path/'measure')],text=True).splitlines():
            parts=line.split()
            if parts and parts[0] in ('.text','.rodata'):sizes[parts[0]]=int(parts[1])
        records[name]={'identity':result['measure_identity'],'operations':result['operations'],
                       'elf_sha256':hashlib.sha256((path/'measure').read_bytes()).hexdigest(),
                       'sections':sizes}
    deltas={}
    for operation in ('keypair_cycles','enc_cycles','dec_cycles'):
        xs={name:r['operations'][operation]['stq2'] for name,r in records.items()}
        deltas[operation]={'wavefront_minus_current':xs['wavefront1']-xs['current-gt'],
                           'wavefront_minus_official':xs['wavefront1']-xs['official'],
                           'current_minus_official':xs['current-gt']-xs['official']}
    result={'label':'supercop-native-kem','fresh_processes_per_implementation':9,
            'records':records,'deltas':deltas,
            'decision':'no-promotion-Encap-regresses-vs-current-and-Official',
            'scope':'only Encap Forward source changed; Keygen/Decap deltas are not arithmetic credit',
            'limitations':['serial Native compiler-selected runs, not paired causal attribution',
                           'footprint/placement may contribute but are not established mechanisms',
                           'no placement confirmation: Native winner prerequisite failed'],
            'validation':{name:json.loads((root/f'{name}.json').read_text()) for name in ('kat','api')}}
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(deltas,indent=2))


if __name__=='__main__':main()

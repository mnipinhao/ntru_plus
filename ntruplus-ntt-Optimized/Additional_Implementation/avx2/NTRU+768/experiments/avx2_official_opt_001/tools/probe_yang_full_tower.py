#!/usr/bin/env python3
"""Linked Official impulse map for the current materialized Forward/inverse pair.

This measures exact maps modulo q, not cycles. `inverse(Forward(x))` is probed
as a diagnostic; it is *not* assumed to be identity because the inverse entry
is scaled for BaseMulScale's Montgomery-domain contract.
"""

import ctypes
import hashlib
import json
import random
import struct
import subprocess
import tempfile
from pathlib import Path

from probe_inverse_ct_gauge import Q, RINV, ROOT


def aligned_words():
    backing=ctypes.create_string_buffer(1536+31)
    ptr=(ctypes.addressof(backing)+31)&~31
    return backing,ptr,(ctypes.c_int16*768).from_address(ptr)


def main():
    sources=[ROOT/'upstream/supercop-avx2'/name
             for name in ('ntt.s','invntt.s','consts.c')]
    with tempfile.TemporaryDirectory(prefix='yang-official-map-') as temp:
        shared=Path(temp)/'tower.so'
        subprocess.run(['cc','-shared','-fPIC','-mavx2','-o',str(shared),
                        *map(str,sources)],check=True,capture_output=True)
        lib=ctypes.CDLL(str(shared))
        forward=lib.poly_ntt;inverse=lib.poly_invntt_scale
        forward.argtypes=inverse.argtypes=[ctypes.c_void_p]
        backing,ptr,words=aligned_words()
        fhash=hashlib.sha256();ihash=hashlib.sha256()
        forward_ranges=[];compositions=[]
        for index in range(768):
            words[:]=[int(k==index) for k in range(768)]
            forward(ptr)
            transformed=list(words)
            assert all(-32768<=x<=32767 for x in transformed)
            forward_ranges.append(max(map(abs,transformed)))
            for x in transformed:fhash.update(struct.pack('<H',x%Q))
            inverse(ptr)
            composed=[x%Q for x in words]
            for x in composed:ihash.update(struct.pack('<H',x))
            nonzero=[(k,x) for k,x in enumerate(composed) if x]
            compositions.append({'input':index,'nonzero_count':len(nonzero),
                                 'single_output':nonzero[0] if len(nonzero)==1 else None})
        simple=sum(v['nonzero_count']==1 for v in compositions)
        same_index=sum(v['single_output'] is not None and
                       v['single_output'][0]==v['input'] for v in compositions)
        rng=random.Random(20260923)
        for _ in range(100):
            original=[rng.randrange(-1,2) for _ in range(768)]
            words[:]=original
            forward(ptr);inverse(ptr)
            assert all(x%Q==3310*y%Q for x,y in zip(words,original))
        result={'evidence_class':'linked_Official_basis_map_not_a_new_tower_candidate',
                'forward_basis_matrix_mod_q_sha256':fhash.hexdigest(),
                'inverse_after_forward_matrix_mod_q_sha256':ihash.hexdigest(),
                'composition_single_nonzero_columns':simple,
                'composition_same_index_columns':same_index,
                'composition_distinct_single_values':sorted(set(
                    v['single_output'][1] for v in compositions
                    if v['single_output'] is not None)),
                'composition_scalar_equals_R_mod_q':
                    simple==768 and same_index==768 and
                    all(v['single_output'][1]*RINV%Q==1 for v in compositions),
                'random_small_composition_cases':100,
                'composition_first_columns':compositions[:12],
                'max_forward_impulse_raw_abs':max(forward_ranges),
                'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sources+[Path(__file__)]}}
        (ROOT/'results/yang-official-full-tower-basis-20260923.json').write_text(
            json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))


if __name__=='__main__':main()

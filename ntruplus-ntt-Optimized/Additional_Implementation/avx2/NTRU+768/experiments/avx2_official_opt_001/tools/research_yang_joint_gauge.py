#!/usr/bin/env python3
"""Track exact CT-prefix gauge ancestry and solve inverse-input gauge constraints.

Each output gauge is factor * H[ancestor] over F_3457. Equalizing radix-3
triples is a weighted union-find problem. This proves feasibility only for the
radix-2 gauge map; consumer arithmetic and i16 range are separate gates.
"""

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from probe_inverse_ct_gauge import Q, RINV, ROOT, compute, route, zetas_inv


class Ratios:
    def __init__(self, count):
        self.parent = list(range(count))
        self.weight = [1] * count  # value[i] = weight[i] * value[parent[i]]
        self.size = [1] * count

    def find(self, i):
        if self.parent[i] != i:
            p = self.parent[i]
            root, factor = self.find(p)
            self.weight[i] = self.weight[i] * factor % Q
            self.parent[i] = root
        return self.parent[i], self.weight[i]

    def require(self, x, y, ratio):
        """Require value[x] = ratio * value[y]."""
        rx, wx = self.find(x)
        ry, wy = self.find(y)
        if rx == ry:
            return wx == ratio * wy % Q
        if self.size[rx] < self.size[ry]:
            self.parent[rx] = ry
            self.weight[rx] = ratio * wy * pow(wx, -1, Q) % Q
            self.size[ry] += self.size[rx]
        else:
            self.parent[ry] = rx
            self.weight[ry] = wx * pow(ratio * wy % Q, -1, Q) % Q
            self.size[rx] += self.size[ry]
        return True


def ancestry():
    zetas = zetas_inv()
    owners = [[16*k+l for l in range(16)] for k in range(48)]
    factors = [[1]*16 for _ in range(48)]
    for stage in (6, 5, 4, 3, 2):
        next_owner = [[0]*16 for _ in range(48)]
        next_factor = [[0]*16 for _ in range(48)]
        for packet in range(6):
            base = packet*8
            z_index = ({6:16, 5:208, 4:400, 3:592}[stage]+packet*32
                       if stage != 2 else 770+packet*4)
            stored = zetas[z_index:z_index+16] if stage != 2 else [zetas[z_index]]*16
            zvec = [v*RINV%Q for v in stored]
            upper_owner = []
            upper_factor = []
            lower_owner = []
            lower_factor = []
            for pair in range(4):
                owner = owners[base+pair]
                factor = factors[base+pair]
                upper_owner.append(owner[:]);lower_owner.append(owner[:])
                upper_factor.append(factor[:])
                lower_factor.append([a*b%Q for a,b in zip(factor,zvec)])
            staged_owner = upper_owner+lower_owner
            staged_factor = upper_factor+lower_factor
            if stage == 2:
                next_owner[base:base+8] = staged_owner
                next_factor[base:base+8] = staged_factor
            else:
                for pair in range(4):
                    lo,hi = route(stage,staged_owner[2*pair],staged_owner[2*pair+1])
                    next_owner[base+pair],next_owner[base+pair+4] = lo,hi
                    lo,hi = route(stage,staged_factor[2*pair],staged_factor[2*pair+1])
                    next_factor[base+pair],next_factor[base+pair+4] = lo,hi
        owners,factors = next_owner,next_factor
    return owners,factors


def replay_gauges(initial):
    """Independent numeric five-stage CT gauge replay, including routing."""
    zetas=zetas_inv()
    gauges=[row[:] for row in initial]
    for stage in (6,5,4,3,2):
        following=[[0]*16 for _ in range(48)]
        for packet in range(6):
            base=packet*8
            off=({6:16,5:208,4:400,3:592}[stage]+packet*32
                 if stage!=2 else 770+packet*4)
            z=zetas[off:off+16] if stage!=2 else [zetas[off]]*16
            upper=[gauges[base+k][:] for k in range(4)]
            lower=[[a*b*RINV%Q for a,b in zip(gauges[base+k],z)]
                   for k in range(4)]
            values=upper+lower
            if stage==2:following[base:base+8]=values
            else:
                for pair in range(4):
                    lo,hi=route(stage,values[2*pair],values[2*pair+1])
                    following[base+pair],following[base+pair+4]=lo,hi
        gauges=following
    return gauges


def main():
    owner,factor=ancestry()
    assert replay_gauges([[1]*16 for _ in range(48)]) == \
        compute()['stages'][-1]['output_gauges']
    rng=random.Random(20260923)
    for trial in range(32):
        initial=[[rng.randrange(1,Q) for _ in range(16)] for _ in range(48)]
        actual=replay_gauges(initial)
        assert all(actual[k][lane] == factor[k][lane] *
                   initial[owner[k][lane]//16][owner[k][lane]%16] % Q
                   for k in range(48) for lane in range(16)), trial
    rows=[]
    for domain in ('radix3_triples', 'radix3_and_level0'):
        dsu=Ratios(768)
        failures=[];edges=0
        for cohort in range(8):
            for lane in range(16):
                for half in (0,1):
                    group=[cohort+24*half+8*j for j in range(3)]
                    k0=group[0]
                    for k in group[1:]:
                        # factor[k0]*H[owner[k0]] = factor[k]*H[owner[k]]
                        ratio=factor[k][lane]*pow(factor[k0][lane],-1,Q)%Q
                        if not dsu.require(owner[k0][lane],owner[k][lane],ratio):
                            failures.append([cohort,lane,half,k0,k])
                        edges+=1
                if domain=='radix3_and_level0':
                    upper,lower=cohort,cohort+24
                    # Align the unweighted j=0 upper/lower outputs. This is
                    # necessary for eliminating its post-radix3 repair.
                    ratio=factor[lower][lane]*pow(factor[upper][lane],-1,Q)%Q
                    if not dsu.require(owner[upper][lane],owner[lower][lane],ratio):
                        failures.append([cohort,lane,'level0_j0',upper,lower])
                    edges+=1
        roots=Counter(dsu.find(k)[0] for k in range(768))
        inactive=set(range(768))-set(x for vector in owner for x in vector)
        rows.append({'constraint_family':domain,'constraints':edges,
                     'contradictions':len(failures),
                     'first_contradictions':failures[:8],
                     'free_gauge_components':len(roots),
                     'active_ancestor_count':768-len(inactive),
                     'largest_component':max(roots.values())})
    source=[Path(__file__),ROOT/'tools/probe_inverse_ct_gauge.py',
            ROOT/'upstream/supercop-avx2/consts.c']
    result={'evidence_class':'exact_modular_gauge_ancestry_and_constraint_screen',
            'scope':'fixed current five CT radix2 layers and their routing; arbitrary nonzero input diagonal gauge; no consumer or machine schedule claim',
            'final_ancestor_reuse':dict(Counter(
                len(set(owner[k][lane] for k in range(48))) for lane in range(16))),
            'random_nonzero_initial_gauge_replays':32,
            'impossibility_witness':{
                'cohort':0,'lanes':[0,4],
                'upper_vector_indices':[0,8,16],
                'same_input_ancestors':[[owner[k][lane] for k in (0,8,16)]
                                        for lane in (0,4)],
                'fixed_factor_vectors':[[factor[k][lane] for k in (0,8,16)]
                                        for lane in (0,4)],
                'reason':'lane 0 requires H[0]=H[128]=H[256], while lane 4 has the same ancestors and three unequal fixed factors'},
            'families':rows,
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source}}
    (ROOT/'results/yang-joint-gauge-ancestry-20260923.json').write_text(
        json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))


if __name__=='__main__':main()

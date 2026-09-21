#!/usr/bin/env python3
"""Semantic packet ABI gate; ownership counts are NOT instruction estimates."""
import hashlib
import json
import random
from pathlib import Path
import generate_tile4 as gt

ROOT = Path(__file__).resolve().parent.parent


def pack(values):
    out = bytearray()
    for a, b in zip(values[::2], values[1::2]):
        a, b = a % 3457, b % 3457
        out.extend((a & 255, (a >> 8) | ((b & 15) << 4), b >> 4))
    return bytes(out)


def mul(a, b, lam):
    out = [0]*4
    for i in range(4):
        for j in range(4):
            out[(i+j)%4] += a[i]*b[j]*(lam if i+j >= 4 else 1)
    return [v % 3457 for v in out]


def main():
    aos, m, records = gt.serialized_mappings()
    codec = json.loads((ROOT/'generated/tile4_q24_codec.json').read_text())
    # W: contiguous wire quartics, four quartics per YMM.
    # WP: sixteen consecutive wire leaves, one YMM per quartic degree.
    wp = [64*(s//64) + 16*(s%4) + (s%64)//4 for s in range(768)]
    maps = dict(M=m, W=list(range(768)), WP=wp)
    for mapping in maps.values():
        assert sorted(mapping) == list(range(768))
    blocks = []
    for block in range(12):
        leaves = records[64*block:64*(block+1):4]
        groups = {r['bm_soa_group'] for r in leaves}
        assert len(groups) == 1
        order = [r['bm_soa_lane'] for r in leaves]
        assert sorted(order) == list(range(16))
        blocks.append(dict(wire_block=block, byte_interval=[96*block,96*(block+1)],
                           M_block=next(iter(groups)), WP_lane_to_M_lane=order,
                           WP_half_crossing_words_per_plane=sum((i//8)!=(v//8) for i,v in enumerate(order)),
                           lambda_R=[gt.lambda_montgomery(r['k3'],r['physical_q'],r['branch']) for r in leaves]))
    # Independently check the imported codec packet's exact qword ownership.
    for packet in codec['packets_detail']:
        p = packet['packet']
        actual = aos[16*p:16*(p+1)]
        assert {v//16 for v in actual} == {packet['destination_vector']}
        assert [actual[4*j]%16//4 for j in range(4)] == packet['source_to_destination_qword']
    rng = random.Random(76820260921)
    # Unique labels prove every ownership location, not merely residues.
    for mapping in maps.values():
        physical = [None]*768
        for s, dest in enumerate(mapping): physical[dest] = s
        assert [physical[dest] for dest in mapping] == list(range(768))
    for trial in range(128):
        h = [rng.randrange(3457) for _ in range(768)]
        r = [rng.randrange(-15592,15593) for _ in range(768)]
        addend = [rng.randrange(-15592,15593) for _ in range(768)]
        expected = []
        for leaf in range(192):
            rec=records[4*leaf]
            lam=gt.lambda_montgomery(rec['k3'],rec['physical_q'],rec['branch'])*pow(65536,-1,3457)%3457
            expected.extend((v+addend[4*leaf+j])%3457 for j,v in enumerate(mul(h[4*leaf:4*leaf+4],r[4*leaf:4*leaf+4],lam)))
        for mapping in maps.values():
            ph, pr, pm = ([0]*768 for _ in range(3))
            for s,d in enumerate(mapping):ph[d],pr[d],pm[d]=h[s],r[s],addend[s]
            out=[0]*768
            before=pr[:]
            for leaf in range(192):
                ids=mapping[4*leaf:4*leaf+4]
                rec=records[4*leaf]
                lam=gt.lambda_montgomery(rec['k3'],rec['physical_q'],rec['branch'])*pow(65536,-1,3457)%3457
                vals=mul([ph[d] for d in ids],[pr[d] for d in ids],lam)
                for j,d in enumerate(ids):out[d]=(vals[j]+pm[d])%3457
            assert pack([out[d] for d in mapping])==pack(expected)
            assert pack([pr[d] for d in mapping])==pack(r) and pr==before
    report=dict(schema='768-encap-packet-abi-gate-v1', scope='semantic architecture gate, not machine pricing',
        blocks=blocks, maps=maps, first_packet_owners=records[:16],
        validation=dict(full_ownership_bijection=768,codec_packets=48,random_semantic_cases=128,
                        ciphertext_bytes_exact=True,r_bytes_exact=True,r_immutable=True),
        candidates={
            'M':dict(status='frozen-control',producer='current M terminal',h='Q24 decode plus M transpose',
                     arithmetic='unchanged B3',egress='current Q24 M pack',allocation='existing linked implementation'),
            'W':dict(status='semantic-feasible-schedule-open',producer='must deposit AoS wire packets directly, not M then adapter',
                     h='wire quartic packets with validation',arithmetic='new AoS quartic consumer required',
                     egress='contiguous 16-coefficient / 24-byte packets; canonicalization still required',
                     allocation=None,cycles=None),
            'WP':dict(status='semantic-feasible-cost-open',producer='plane lane order must change',
                      h='wire AoS to planes still required',arithmetic='lane-permuted B3 with offline lambda reorder',
                      egress='plane to wire AoS still required',allocation=None,cycles=None),
            'asymmetric_D01':dict(status='existing-realization-not-reopened',
                      legacy_edge_instruction_delta=96,legacy_net_representation_routes=0,
                      caveat='instruction delta is not a cycle rejection; old 10788 range metadata is stale',
                      reopen_requires='new direct decoder pair formation, reduction/compaction, or scale mechanism')},
        accounting=dict(unit='per Encap',multiplicity=dict(r_producer=1,m_producer=1,h_decode=1,r_hash_pack=1,ciphertext_pack=1),
                        structural_only='12 blocks, 4 vectors/block, 48 vectors/polynomial; not an instruction ledger',
                        missing=['W arithmetic instruction schedule and range','producer terminal exact redeposit schedule',
                                 'whole-edge allocation and validation lifetime','compact implementation and cycle pricing']),
        decision='no-ASM-yet; select W direct-terminal plus quartic consumer schedule as bounded next gate',
        no_performance_claim=True,
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                       [Path(__file__),Path(gt.__file__),ROOT/'generated/tile4_q24_codec.json']})
    (ROOT/'generated/tile4_encap_packet_abi_gate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(validation=report['validation'],block_order=[b['M_block'] for b in blocks],decision=report['decision'])))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    main()

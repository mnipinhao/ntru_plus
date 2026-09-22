"""Recompute serious results from raw observations; compare ELF section payloads."""
import csv
import json
import struct
from collections import defaultdict
from run_pack_triad import EXP,sha,stq

def sections(path):
    data=path.read_bytes()
    assert data[:6]==b'\x7fELF\x02\x01'
    offset=struct.unpack_from('<Q',data,40)[0]
    size,count,names=struct.unpack_from('<HHH',data,58)
    headers=[struct.unpack_from('<IIQQQQIIQQ',data,offset+i*size) for i in range(count)]
    strings=headers[names]; table=data[strings[4]:strings[4]+strings[5]]
    out={}
    for h in headers[1:]:
        name=table[h[0]:].split(b'\0',1)[0].decode()
        out[name]={'type':h[1],'flags':h[2],'address':h[3],'size':h[5],
            'payload':b'' if h[1]==8 else data[h[4]:h[4]+h[5]]}
    return out

if __name__=='__main__':
    root=EXP/'results/pack-maskstore-triad-serious-20260922'
    old=EXP/'results/pack-maskstore-triad-20260922'
    meta=json.loads((root/'metadata.json').read_text())
    summary=json.loads((root/'summary.json').read_text())
    groups=defaultdict(list); launches=defaultdict(list)
    orders=[(0,1,2),(1,2,0),(2,0,1),(2,1,0),(1,0,2),(0,2,1)]
    for k in range(9):
        seen=set()
        for row in csv.DictReader((root/f'launch-{k}.csv').open()):
            r,v,block,pos,c=(int(row[x]) for x in ('region','variant','block','position','cycles'))
            assert v==orders[block%6][pos] and c>=0
            key=(r,block,pos);assert key not in seen;seen.add(key)
            groups[r,v].append(c);launches[k,r,v].append(c)
        assert len(seen)==4*96*3
    for r,name in enumerate(['r_pack','c_pack','r_state_hashbytes','full_polynomial_island']):
        for v in range(3):
            assert len(groups[r,v])==864
            assert stq(groups[r,v])==summary[name]['stq'][str(v)]
        for label,a,b in [('I-C',1,0),('M-I',2,1),('M-C',2,0)]:
            d=[stq(launches[k,r,a])[1]-stq(launches[k,r,b])[1] for k in range(9)]
            assert d==summary[name]['deltas'][label]['launches']
    a,b=sections(old/'measure'),sections(root/'measure')
    changed=[key for key in a if a[key]!=b.get(key)]
    assert set(a)==set(b)
    allocated_equal=all(a[key]==b[key] for key in a if a[key]['flags']&2)
    assert allocated_equal and sha(root/'measure')==meta['elf_sha256']
    report={'raw_recomputed':True,'observations_per_variant_region':864,
        'all_six_cyclic_orders_verified':True,'same_allocated_sections_as_short':allocated_equal,
        'ELF_section_differences_vs_short':changed,
        'whole_ELF_same_as_short':sha(old/'measure')==sha(root/'measure'),
        'explanation':'Non-allocated build metadata may differ; loaded code/data/address geometry identical.',
        'Native':'not run','production':'unchanged'}
    (root/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

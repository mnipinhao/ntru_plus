"""Full-vector wire chunks; layout feasibility, not a routing implementation.

Every 32 coefficients give 16 a/b pairs, hence three 16-byte vectors for full
ST3 or three pre-interleaved STR Q. Quantify input reload risk explicitly.
"""
import json,re
from pathlib import Path
P=Path(__file__).resolve().parent
prod=P.parents[1]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
s=(prod/'tables.h').read_text().split('map_f',1)[1].split('=',1)[1].split(';',1)[0]
wire=list(map(int,re.findall(r'-?\d+',s)))
assert len(wire)==864 and sorted(wire)==list(range(864))
chunks=[];written=[]
for start in range(0,864,32):
    src=wire[start:start+32]
    channels=[[],[],[]]
    for i in range(16):
        # Distinct tags identify byte order independently of numeric values.
        for byte in range(3):channels[byte].append((start//2+i,byte))
    full_st3=[channels[b][lane] for lane in range(16) for b in range(3)]
    assert full_st3==[(k,b) for k in range(start//2,start//2+16) for b in range(3)]
    qstores=[full_st3[i:i+16] for i in range(0,48,16)]
    assert sum(qstores,[])==full_st3
    written.extend(range(3*start//2,3*start//2+48))
    chunks.append({'output_offset':3*start//2,'source_q_vectors':sorted(set(x//8 for x in src)),
       'a_fr0_indices':src[::2],'b_fr0_indices':src[1::2]})
assert written==list(range(1296))
print(json.dumps({'status':'wire-map-pass','full_ST3_Q_count':27,'STR_Q_alternative_count':81,
  'lane_stores':0,'tail_bytes':0,'naive_chunk_Q_loads':sum(len(c['source_q_vectors']) for c in chunks),
  'distinct_input_Q_vectors':108,'max_source_Q_per_chunk':max(len(c['source_q_vectors']) for c in chunks),
  'warning':'not a register-feasible DAG; source reuse and packing cost remain to be solved',
  'first_chunk':chunks[0]},indent=2))

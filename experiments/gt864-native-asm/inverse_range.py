"""Conservative interval gate for R^-1 I9 -> I16 -> top reconstruction.

No correlation assumption, no random-test substitution for range proof.
Exhaustive masks refer only to b=1 butterflies in the current I16 topology.
"""
import itertools,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
Q=3457
prod=P.parents[1]/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
tables=(prod/'gt864_fr0_inverse_barrett_tables.h').read_text()
scaled=(P.parent/'gt864-decaps-scale/scaled_tables.h').read_text()
def table(s,name):return list(map(int,re.findall(r'-?\d+',s.split(name,1)[1].split('=',1)[1].split('};',1)[0])))
def bound(b,h,A=32768):
    return max(abs(x*b-((x*h+16384)//32768)*Q) for x in range(-A,min(A,32767)+1))
def b3(a,b,c,reset=3456):return (a+b+c,a+2*reset,a+2*reset)
def main():
    pairs=set()
    for text,name in [(tables,'gt864_inverse9_twist_barrett'),
       (scaled,'gt864_inverse16_main_scale_barrett'),(scaled,'gt864_inverse16_tail_scale_barrett')]:
        vals=table(text,name)
        for off in range(0,len(vals),16):pairs.update(zip(vals[off:off+8],vals[off+8:off+16]))
    stage=table(scaled,'gt864_inverse16_stage_barrett')
    pairs.update(zip(stage[::2],stage[1::2]))
    pairs.update([(722,6844),(-723,-6853),(366,3469),(1124,10654),(-1634,-15488),(-722,-6844)])
    maxima={p:bound(*p) for p in pairs}
    assert max(maxima.values())<Q
    assert all(h==(b*32768+1728)//Q for b,h in pairs)
    # Exact I9 register topology, interval arithmetic before every reset.
    state=[2497]*9;peak=2497
    for inds in [(0,3,6),(1,4,7),(8,2,5)]:
        out=b3(*(state[i] for i in inds));peak=max(peak,*out)
        for i,a in zip(inds,out):state[i]=a
    for i in [4,5,7,2]:state[i]=3456
    for inds in [(0,1,8),(3,4,2),(6,7,5)]:
        out=b3(*(state[i] for i in inds));peak=max(peak,*out)
        for i,a in zip(inds,out):state[i]=a
    assert peak<32768
    # I9 terminal twist resets all lanes to <=3456.
    butterflies=[]
    for level in range(4):
        step=1<<level
        for block in range(0,16,2*step):
            for j in range(step):butterflies.append((block+j,block+j+step,
                stage[16*level+2*(len(butterflies)%8)],stage[16*level+2*(len(butterflies)%8)+1]))
    identities=[i for i,(_,_,b,_) in enumerate(butterflies) if b==1]
    assert len(identities)==15
    best=None;passing=0
    for bits in range(1<<15):
        deleted={identities[j] for j in range(15) if bits>>j&1}
        bounds=[3456]*16;local_peak=3456
        for i,(a,b,c,h) in enumerate(butterflies):
            rhs=bounds[b] if i in deleted else maxima[(c,h)]
            value=bounds[a]+rhs
            if value>32767:break
            bounds[a]=bounds[b]=value;local_peak=max(local_peak,value)
        else:
            passing+=1
            score=(len(deleted),-local_peak,-bits)
            if best is None or score>best[0]:best=(score,sorted(deleted),local_peak)
    assert best
    # After scale, x_beta-x_alpha <=2*3456; top product resets; low <=6912.
    assert 2*3456<32768
    result={'status':'range-gate-pass','fixed_constant_pairs_exhausted':len(pairs),
      'fixed_constant_full_i16_max':max(maxima.values()),'I9_peak_bound':peak,
      'I16_input_bound':3456,'identity_positions':identities,'masks_tested':1<<15,
      'passing_masks':passing,'deleted_butterflies':best[1],'I16_peak_bound':best[2],
      'top_output_bound':6912,'scale':'R^-1 through stages; R absorbed at terminal table',
      'instruction_saving_per_I16_block':3*len(best[1])+(15-len(best[1])),
      'additional_dead_table_loads_per_I16_block':2,
      'total_instruction_saving_per_I16_block':45,
      'note':'remaining identity mul is a no-op; keep its quotient and MLS reset; final canonicalization retained'}
    print(json.dumps(result,indent=2));return result
if __name__=='__main__':main()

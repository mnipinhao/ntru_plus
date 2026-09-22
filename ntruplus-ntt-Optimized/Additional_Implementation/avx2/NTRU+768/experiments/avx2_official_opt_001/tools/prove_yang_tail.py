#!/usr/bin/env python3
"""Executable Yang-inspired tail proof. No new ASM and no timing.

Scope: fixed CT prefix, paired input gauge, delayed radix-3 alpha, exact
trinomial shear composed with final scaling. Conditional prefix input bound.
"""
import hashlib,json,random,re,ctypes,subprocess,tempfile
from pathlib import Path
from math import ceil
from probe_inverse_ct_gauge import ROOT,Q,R,RINV,compute,route,zetas_inv
from prove_inverse_ct_range import repaired_replay,barrett_bound
from prove_forward_lanes import mont_word,barrett_word,signed16

def word(f):return signed_center(f*R%Q)
def signed_center(x):return x-Q if x>Q//2 else x
def mb(b,f):return ceil(b*abs(word(f))/65536)+1729
def mul(x,f):
    assert -32768<=x<=32767
    y=mont_word(x,word(f));assert -32768<=y<=32767
    assert (y-x*f)%Q==0
    return y
def add(a,b):
    c=a+b;assert -32768<=c<=32767,c
    return c
def sub(a,b):return add(a,-b)

class Schedule:
    """SSA instruction schedule with memory constants and linear-scan YMM map."""
    def __init__(self):self.ops=[];self.n=0
    def op(self,op,*src):
        dst=f't{self.n}';self.n+=1;self.ops.append((op,list(src),dst));return dst
    def mont(self,x,label):
        lo=self.op('vpmullw',x,'mem:'+label+'.qinv')
        hi=self.op('vpmulhw',x,'mem:'+label+'.word')
        red=self.op('vpmulhw',lo,'q')
        return self.op('vpsubw',hi,red)
    def allocate(self):
        last={}
        for i,(_,src,_) in enumerate(self.ops):
            for s in src:
                if not s.startswith('mem:'):last[s]=i
        regs={'q':0};free=list(range(1,16));peak=1;rows=[]
        for i,(op,src,dst) in enumerate(self.ops):
            reads={s:regs[s] for s in src if not s.startswith('mem:')}
            for s in set(reads):
                if last[s]==i and s!='q':free.append(regs.pop(s))
            assert free,'allocation exceeds 16 YMM'
            reg=min(free);free.remove(reg);regs[dst]=reg;peak=max(peak,len(regs))
            rows.append(dict(op=op,inputs=src,read_registers=reads,output=dst,register=reg))
            if dst not in last:free.append(regs.pop(dst))
        return {'peak_ymm_including_q':peak,'instructions':rows,'note':'VEX 3-operand last-use reuse; constants memory-form; model not linked proof'}

def main():
    data=compute();prefix=repaired_replay(7644,data)
    bounds=prefix['stages'][-1]['per_vector_max_abs_bound']
    gauges=data['stages'][-1]['output_gauges'];z=zetas_inv()
    alpha=[[1,z[794+8*b]*RINV%Q,z[798+8*b]*RINV%Q] for b in range(2)]
    phi=z[810]*RINV%Q;n=1679*RINV%Q;w=(-886)*RINV%Q
    assert (w*w+w+1)%Q==0
    rows=[];tables=[];maxpre=0;maxout=0;checks=0;factored_maxpre=0;factored_maxout=0
    def tail(v,gs,g,candidate):
        triples=[]
        for b in range(2):
            x,y,zz=[v[3*b+j] if gs[3*b+j]==g and b==0 and j==0 else mul(v[3*b+j],gs[3*b+j]*pow(g,-1,Q)%Q) for j in range(3)]
            t=mul(sub(y,zz),w)
            vals=[barrett_word(add(add(x,y),zz)),sub(sub(x,y),t),add(sub(x,zz),t)]
            if not candidate:vals=[vals[0],mul(vals[1],alpha[b][1]),mul(vals[2],alpha[b][2])]
            triples.append(vals)
        out=[]
        for j in range(3):
            u,vv=triples[0][j],triples[1][j]
            if candidate=='factored' and j:
                a,b=alpha[0][j],alpha[1][j]
                vv=mul(vv,b*pow(a,-1,Q)%Q)
                t=mul(sub(u,vv),phi)
                out.extend([mul(sub(add(u,vv),t),n*g*a%Q),mul(t,2*n*g*a%Q)])
            elif candidate and j:
                a,b=alpha[0][j],alpha[1][j]
                c=[n*g*(1-phi)*a%Q,n*g*(1+phi)*b%Q,2*n*g*phi*a%Q,-2*n*g*phi*b%Q]
                out.extend([add(mul(u,c[0]),mul(vv,c[1])),add(mul(u,c[2]),mul(vv,c[3]))])
            else:
                t=mul(sub(u,vv),phi)
                out.extend([mul(sub(add(u,vv),t),n*g%Q),mul(t,2*n*g%Q)])
        return out
    def semantic(v,gs):
        out=[];ts=[]
        for b in range(2):
            x,y,zz=[v[3*b+j]*gs[3*b+j]%Q for j in range(3)]
            ts.append([(x+y+zz)%Q,alpha[b][1]*(x-y-w*(y-zz))%Q,alpha[b][2]*(x-zz+w*(y-zz))%Q])
        for j in range(3):
            u,v=ts[0][j],ts[1][j];t=phi*(u-v)%Q
            out.extend([n*(u+v-t)%Q,2*n*t%Q])
        return out
    rng=random.Random(20260922)
    for i in range(8):
        matrix_vectors=[[] for _ in range(8)]
        for lane in range(16):
            indices=[i,i+8,i+16,i+24,i+32,i+40]
            gs=[gauges[k][lane] for k in indices];g=gs[0]
            bs=[];pre=[]
            for b in range(2):
                xx=bounds[indices[3*b]] if b==0 else mb(bounds[indices[3*b]],gs[3*b]*pow(g,-1,Q)%Q)
                yy=mb(bounds[indices[3*b+1]],gs[3*b+1]*pow(g,-1,Q)%Q)
                zz=mb(bounds[indices[3*b+2]],gs[3*b+2]*pow(g,-1,Q)%Q)
                t=mb(yy+zz,w)
                s=xx+yy+zz;u=xx+yy+t;v=xx+zz+t
                pre.extend([yy+zz,xx+yy,xx+zz,s,u,v]);bs.append([barrett_bound(s),u,v])
            output_bounds=[];coeff=[];factored_bounds=[]
            for j in (1,2):
                a,b=alpha[0][j],alpha[1][j]
                c=[n*g*(1-phi)*a%Q,n*g*(1+phi)*b%Q,2*n*g*phi*a%Q,-2*n*g*phi*b%Q]
                coeff.append(c)
                output_bounds += [mb(bs[0][j],c[0])+mb(bs[1][j],c[1]),mb(bs[0][j],c[2])+mb(bs[1][j],c[3])]
                for k,value in enumerate(c):matrix_vectors[4*(j-1)+k].append(value)
                u=bs[0][j];v=mb(bs[1][j],b*pow(a,-1,Q)%Q)
                pair=u+v;t=mb(pair,phi);shear=pair+t
                outputs=[mb(shear,n*g*a%Q),mb(t,2*n*g*a%Q)]
                assert max(pair,shear,*outputs)<=32767
                factored_maxpre=max(factored_maxpre,*pre,pair,shear,*outputs)
                factored_maxout=max(factored_maxout,*outputs)
                factored_bounds.append({'j':j,'relative_ratio':b*pow(a,-1,Q)%Q,'relative_output':v,'pair':pair,'shear':shear,'outputs':outputs})
            pair=bs[0][0]+bs[1][0];t=mb(pair,phi)
            degree0_outputs=[mb(pair+t,n*g%Q),mb(t,2*n*g%Q)]
            factored_maxout=max(factored_maxout,*degree0_outputs)
            factored_maxpre=max(factored_maxpre,pair,pair+t,*degree0_outputs)
            pre.extend([pair,pair+t]);output_bounds.extend(degree0_outputs)
            pre+=output_bounds;assert max(pre)<=32767
            maxpre=max(maxpre,max(pre));maxout=max(maxout,max(output_bounds))
            # Exact linear-map proof: 6 basis columns per physical lane,
            # with the independent Official tail formula as oracle.
            cases=[[0]*6]
            for j in range(6):
                for sign in (-1,1):
                    v=[0]*6;v[j]=sign;cases.append(v)
            for mask in range(64):cases.append([bounds[k]*(1 if mask>>j&1 else -1) for j,k in enumerate(indices)])
            cases += [[rng.randint(-bounds[k],bounds[k]) for k in indices] for _ in range(64)]
            for v in cases:
                ref=semantic(v,gs)
                assert [x%Q for x in tail(v,gs,g,False)]==ref
                assert [x%Q for x in tail(v,gs,g,True)]==ref
                assert [x%Q for x in tail(v,gs,g,'factored')]==ref
                checks+=1
            rows.append({'cohort':i,'lane':lane,'physical_vectors':indices,'gauges':gs,'paired_gauge':g,'alpha':alpha,'matrix_constants_j1_j2':coeff,'post_r3_lazy_bounds':bs,'max_i16_preoperation':max(pre),'output_bounds':output_bounds,'factored_bounds':factored_bounds})
        tables.extend(matrix_vectors)
    s=Schedule();u=s.op('vmovdqa','mem:u');v=s.op('vmovdqa','mem:v')
    a=s.mont(u,'c00');b=s.mont(v,'c01');o=s.op('vpaddw',a,b);s.op('store',o)
    a=s.mont(u,'c10');b=s.mont(v,'c11');o=s.op('vpaddw',a,b);s.op('store',o)
    schedule=s.allocate()
    # Independent machine anchor: replay prefix and tail, compare the existing
    # wresident ASM (compiled unchanged in a temporary directory). No new ASM.
    def pipeline(values,candidate):
        mem=[values[k:k+16] for k in range(0,768,16)]
        for sd in data['stages']:
            stage=sd['stage'];new=[[0]*16 for _ in range(48)]
            for packet in range(6):
                base=packet*8;outputs=[];lower=[]
                for pair in range(4):
                    a=mem[base+pair][:];b=mem[base+pair+4][:]
                    repair=prefix['plan'][stage][pair]
                    if repair['a']:a=list(map(barrett_word,a))
                    if repair['b']:b=list(map(barrett_word,b))
                    tw=sd['twiddles'][packet*4+pair]
                    if tw!=[1]*16:b=[mul(x,f) for x,f in zip(b,tw)]
                    outputs.append([add(x,y) for x,y in zip(a,b)])
                    lower.append([sub(x,y) for x,y in zip(a,b)])
                outputs+=lower
                if stage==2:new[base:base+8]=outputs
                else:
                    for pair in range(4):
                        lo,hi=route(stage,outputs[2*pair],outputs[2*pair+1])
                        new[base+pair],new[base+pair+4]=lo,hi
            mem=new
        result=[[0]*16 for _ in range(48)]
        for i in range(8):
            indices=[i,i+8,i+16,i+24,i+32,i+40]
            for lane in range(16):
                gs=[gauges[k][lane] for k in indices]
                out=tail([mem[k][lane] for k in indices],gs,gs[0],candidate)
                for j in range(3):
                    result[i+8*j][lane]=out[2*j]
                    result[i+24+8*j][lane]=out[2*j+1]
        return sum(result,[])
    anchor_cases=0
    with tempfile.TemporaryDirectory(prefix='yang-tail-proof-') as td:
        library=Path(td)/'anchor.so'
        subprocess.run(['cc','-shared','-fPIC','-mavx2','-o',str(library),
            str(ROOT/'asm/ntruplus768_officialopt_invntt_ct_wresident.s'),
            str(ROOT/'upstream/supercop-avx2/crepmod3.s'),
            str(ROOT/'upstream/supercop-avx2/consts.c')],check=True,capture_output=True)
        lib=ctypes.CDLL(str(library))
        buf=ctypes.create_string_buffer(1536+31);ptr=(ctypes.addressof(buf)+31)&~31
        array=(ctypes.c_int16*768).from_address(ptr)
        inverse=lib.ntruplus768_officialopt_invntt_ct_wresident
        inverse.argtypes=[ctypes.c_void_p]
        crep=lib.poly_crepmod3;crep.argtypes=[ctypes.c_void_p]
        fixtures=[]
        for j in range(768):
            v=[0]*768;v[j]=1;fixtures.append(v)
        fixtures += [[rng.randint(-7644,7644) for _ in range(768)] for _ in range(16)]
        for values in fixtures:
            array[:]=values;inverse(ptr);raw=list(array)
            model=pipeline(values,False);candidate=pipeline(values,True)
            # Raw equality anchors Montgomery constants, route, and shear.
            assert model==raw
            assert all((x-y)%Q==0 for x,y in zip(raw,candidate))
            factored=pipeline(values,'factored')
            assert all((x-y)%Q==0 for x,y in zip(raw,factored))
            crep(ptr);reference_bytes=list(array)
            array[:]=candidate;crep(ptr);assert list(array)==reference_bytes
            array[:]=factored;crep(ptr);assert list(array)==reference_bytes
            anchor_cases+=1
        # New lazy terminal bound is wider than wresident. Exhaustively check
        # the unchanged machine consumer against centered-equivalent inputs.
        consumer_bound=max(maxout,factored_maxout)
        vals=list(range(-consumer_bound,consumer_bound+1))
        for start in range(0,len(vals),768):
            chunk=vals[start:start+768];chunk+= [0]*(768-len(chunk))
            array[:]=chunk;crep(ptr);actual=list(array)
            array[:]=[signed_center(x%Q) for x in chunk];crep(ptr)
            assert actual==list(array)
    # Montgomery table exponent and low-word companion identities, no R drift.
    encoded=[]
    for vec in tables:
        words=[word(c) for c in vec];companions=[signed16(t*12929) for t in words]
        assert all(t*RINV%Q==c for t,c in zip(words,vec))
        encoded.append({'semantic':vec,'montgomery_words':words,'qinv_companions':companions})
    sources=[ROOT/'upstream/supercop-avx2/invntt.s',ROOT/'upstream/supercop-avx2/consts.c',ROOT/'asm/ntruplus768_officialopt_invntt_ct_wresident.s',Path(__file__)]
    result={'kind':'conditional_executable_tail_proof_not_ASM_or_performance','q':Q,'R':R,'phi':phi,'nscale':n,'omega':w,'prefix_input_abs_bound':7644,'prefix_bound_status':'inherited conditional contract; BaseMulScale machine-level closure still required','cases':checks,'basis_columns':768,'lanes':rows,'matrix_tables':encoded,'max_tail_preoperation':maxpre,'max_output_abs':maxout,'factored_max_preoperation':factored_maxpre,'factored_max_output':max(factored_maxout,2336),'matrix_schedule':schedule,
      'ledger':{'wresident':{'prefix_mont':78,'relative_mont':40,'omega_mont':16,'alpha_mont':32,'phi_mont':24,'final_mont':48,'total_mont':238,'barrett':40,'added_table_bytes':11264,'tail_constant_operands_excluding_q_v':124},'delayed_alpha_direct_matrix':{'prefix_mont':78,'relative_mont':40,'omega_mont':16,'alpha_mont':0,'degree0_phi_final_mont':24,'degree1_2_matrix_mont':64,'total_mont':222,'barrett':40,'added_table_bytes':15360,'tail_constant_operands_excluding_q_v':244},'delta':{'mont':-16,'table_bytes':4096,'tail_constant_operands':120,'routing':0,'data_passes':0},'constant_policy':'simple non-deduplicated aligned tables; memory-form matrix constants; hypothetical schedule, not linked census'},
      'linked_control_anchor':{'cases':anchor_cases,'wresident_raw_exact':True,'candidate_residue_exact':True,'candidate_crepmod3_exact':True,'consumer_exhaustive_words':2*maxout+1},
      'gate':{'algebra':'pass','tail_range':'conditional pass','matrix_allocation':'pass','full_new_radix3_schedule':'not lowered; inherited pre-alpha operations, stores now before alpha','crepmod3_new_representatives':'exhaustive machine check over proven terminal envelope passed','caller_input_closure':'BaseMulScale-to-prefix proof remains conditional','ASM_recommendation':'hold: chain credit real but substantial constant traffic; no free-lunch claim'},'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    result['ledger']['delayed_alpha_factored']={'total_mont':222,'prefix_mont':78,'relative_pre_r3_mont':40,'omega_mont':16,'relative_post_r3_mont':16,'phi_mont':24,'final_mont':48,'barrett':40,'added_table_bytes':13312,'tail_constant_operands_excluding_q_v':184,'delta_mont':-16,'delta_table_bytes':2048,'delta_tail_constant_operands':60,'traversal':'three public j groups, eight pairs each; ratio/phi resident within group; final table per pair','allocation_status':'full loop lowering pending, not claimed linked feasible'}
    result['factored_max_output']=factored_maxout
    result['linked_control_anchor']['consumer_exhaustive_words']=2*consumer_bound+1
    # Two new ratios, each with word/companion broadcast operands. Reserve a
    # complete aligned 32-byte block; do not assume reuse of upstream constants.
    ratios=[alpha[1][j]*pow(alpha[0][j],-1,Q)%Q for j in (1,2)]
    result['factored_ratio_table']=[{'semantic':f,'word':word(f),'qinv':signed16(word(f)*12929)} for f in ratios]
    result['ledger']['delayed_alpha_factored'].update(added_table_bytes=13344,delta_table_bytes=2080,ratio_table_aligned_bytes=32)
    out=ROOT/'results/yang-tail-proof-20260922.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('cases','basis_columns','max_tail_preoperation','max_output_abs','ledger','gate')},indent=2))
if __name__=='__main__':main()

"""Caller-specific range review, fixed P3B37 plus opt-in deletion masks."""
from pathlib import Path
import importlib.util,json,itertools,hashlib,re
H=Path(__file__).resolve().parent;E=H.parent;B=H/'build'
s=importlib.util.spec_from_file_location('p35',E/'gt864_p3b35_liveness_consumer/reachable.py')
R=importlib.util.module_from_spec(s);s.loader.exec_module(R);P=R.P;G=P.G;C=P.C
def i16(x):assert -32768<=x[0]<=x[1]<=32767,x;return x
def i32(x):assert -2**31<=x[0]<=x[1]<2**31,x;return x
def mont(x):
    i32(x);i32(G.add(x,(-32768*3457,32767*3457)))
    return i16(G.montgomery_bound(x))
def fm(a,b):return mont(G.multiply(a,b))
def baseinv_bound():
    # baseinv_1 materializes int16 numerator and denominator vectors.
    full=(-32768,32767);chain=[full]
    for _ in range(35):chain.append(fm(chain[-1],full))
    a=chain[-1];t1=fm(a,a);t2=fm(t1,t1);t2=fm(t2,t2);t3=fm(t2,t2)
    t1=fm(t1,t2);t2=fm(t1,t3);t2=fm(t2,t2);t2=fm(t2,a)
    t1=fm(t1,t2)
    for _ in range(6):t2=fm(t2,t2)
    t2=fm(t2,t1)
    vals=[G.BASE.fixed(x,(-1571,-14891)) for x in range(t2[0],t2[1]+1)]
    inv=i16((min(vals),max(vals)));den=[]
    for i in range(35,0,-1):
        den.append(fm(chain[i-1],inv));inv=fm(inv,full)
    den.append(inv)
    out=[fm(full,d) for d in den]
    return {'batch_prefix':chain,'denominator_inverse':den,
            'output':[min(x[0] for x in out),max(x[1] for x in out)],
            'premise':'unchanged baseinv_1 int16 stored values; centered input; existing algebraic correctness reused'}
def producers():
    vals=set()
    for a,b in itertools.product(range(256),repeat=2):
        for shift in (0,1):
            word=(((a>>shift)&85)+85-((b>>shift)&85))&255
            vals.update(((word>>k)&3)-1 for k in (0,2,4,6))
    assert vals=={-1,0,1}
    centered=set()
    for x in range(-32768,32768):
        v=G.BASE.fixed(x,(1,9));v+=3457 if v<0 else 0
        v-=3457 if v>1728 else 0
        assert -1728<=v<=1728 and (v-x)%3457==0
        quo=(v*21845)//32768;quo=(quo+1)//2
        rem=v-3*quo;assert rem in (-1,0,1) and (rem-v)%3==0
        centered.add(rem)
    return {'CBD1_and_SOTP_exhaustive_byte_pairs':sorted(vals),
            'inverse_centered_then_crepmod3':sorted(centered),
            'f_superset':list(range(-3,5)),'g_exact_scalar_set':[-3,0,3],
            'r_m_crepmod3_set':[-1,0,1]}
def ntt(domain,top,kind,skip,a):
    raw={lo+(-722 if top==0 else 723)*hi for lo in domain for hi in domain}
    state=[None]*16;support=[None]*16
    for t in range(16):
        state[G.BASE.REVERSE4[t]]=raw if kind=='main' and t==0 and 'main.twist0' in skip else {G.BASE.fixed(x,C['twist16'][top][t]) for x in raw}
        support[G.BASE.REVERSE4[t]]={t}
    for stage,length in enumerate((2,4,8,16)):
        for start in range(0,16,length):
            for j in range(length//2):
                l=start+j;r=l+length//2;x,y=state[l],state[r]
                assert support[l].isdisjoint(support[r])
                support[l]=support[r]=support[l]|support[r]
                delete=j==0 and ((kind=='main' and f'main.stage{stage}.node{start}' in skip) or (kind=='tail' and stage==0 and 'tail.stage0' in skip))
                if not delete:y={G.BASE.fixed(v,C['stage16'][stage][j]) for v in y}
                state[l],state[r]=R.combine(x,y,1),R.combine(x,y,-1)
                for k in (l,r):a.note(f'{kind}.ntt16.{stage}.{k}','exact-set',P.atom(min(state[k]),max(state[k])))
    return state
def forward(domain,skip):
    P.ATOMS.clear();a=P.Analyzer();leaves=[]
    try:
        for top in range(2):
            main=ntt(domain,top,'main',skip,a);tail=ntt(domain,top,'tail',skip,a)
            for col in range(16):
                block,lane=divmod(col,8);sets=[main[col]]+[{G.BASE.fixed(v,C['twist9'][top][block][s][lane]) for v in (tail[col] if s==8 else main[col])} for s in range(1,9)]
                f=[a.note('twist9','exact-set',P.atom(min(v),max(v))) for v in sets]
                aa=a.b3_one_product('A',f[0],f[3],f[6]);bb=a.b3_one_product('B',f[1],f[4],f[7]);cc=a.b3_one_product('C',f[8],f[2],f[5])
                g0=a.b3_one_product('g0',aa[0],bb[0],cc[0])
                g1=a.b3_one_product('g1',aa[1],a.mul('etaB',bb[1],C['eta']),a.mul('etaC',cc[1],C['eta_inv']))
                g2=a.b3_one_product('g2',aa[2],a.mul('etaB2',bb[2],C['eta_inv']),a.mul('etaC2',cc[2],C['eta']))
                leaves.extend((v.low,v.high) for v in (g0[0],g1[0],g2[1],g0[1],g1[1],g2[2],g0[2],g1[2],g2[0]))
        return {'status':'pass','leaves':leaves,'peak':max(v['interval'][1] for v in a.nodes),
                'abs_peak':max(max(abs(x) for x in v['interval']) for v in a.nodes)}
    except (P.Failure,AssertionError) as e:return {'status':'not_proven','reason':str(e)}
def bm(a,b,c=None):
    product=G.multiply(a,b);cross=G.add(product,product)
    red0,red1=mont(cross),mont(product);z=(-1728,1728)
    accum=[G.add(G.multiply(red0,z),product),G.add(G.multiply(red1,z),product,product),G.add(product,product,product)]
    for v in accum:i32(v)
    if c is not None:accum=[i32(G.add(v,c)) for v in accum]
    return accum
def caller(name,aa,bb,cc=None):
    try:
        values=[bm(a,b,None if cc is None else cc[i]) for i,(a,b) in enumerate(zip(aa,bb))]
        return {'caller':name,'status':'pass','D1_input_union':[min(x[0] for row in values for x in row),max(x[1] for row in values for x in row)],'D1_output':[-3023,3023]}
    except AssertionError as e:return {'caller':name,'status':'not_proven','reason':str(e)}
def main():
    B.mkdir(exist_ok=True);prod=producers();bi=baseinv_bound();print('BaseInv',bi['output'],flush=True)
    raw=E/'gt864_p3b37_local_slothy/build/sync/raw'
    table=(raw/'gt864_fr0_basemul_tables.h').read_text().split('gt864_fr0_zetas_mul[36][8] = {')[1].split('};')[0]
    zetas=list(map(int,re.findall(r'-?\d+',table)))
    assert len(zetas)==288 and max(map(abs,zetas))<=1728
    assert 'gt864_fr0_cluster_transpose_frombytes(out->coeffs, in)' in (raw/'byte_api.c').read_text()
    assert 'vdupq_n_u16(4095)' in (raw/'cluster_transpose_frombytes.c').read_text()
    theorem=P.D.exact_barrett_residual_range(-2**31,2**31-1,621199)
    assert max(abs(theorem['residual_low']),abs(theorem['residual_high']))==3023
    inv=G.inverse_barrett_chain(3023)
    base=set(json.loads((E/'gt864_p3b35_liveness_consumer/build/reachable-main.twist0.json').read_text())['skip'])
    extra=['main.stage1.node0','main.stage2.node0','main.stage3.node0'];records=[]
    for mask in range(8):
        deleted=[extra[i] for i in range(3) if mask>>i&1];skip=base|set(deleted)
        fw={name:forward(domain,skip) for name,domain in [('f',range(-3,5)),('g',[-3,0,3]),('small',[-1,0,1])]}
        packed=[(0,4095)]*288;ib=[tuple(bi['output'])]*288;calls=[]
        for n,operand in [('keygen_h','g'),('keygen_hinv','f')]:
            calls.append(caller(n,fw[operand]['leaves'],ib) if fw[operand]['status']=='pass' else {'caller':n,'status':'not_proven','reason':'Forward '+fw[operand]['reason']})
        calls.append(caller('decap_first',packed,packed))
        if fw['small']['status']=='pass':
            small=fw['small']['leaves']
            calls.append(caller('encap',packed,small,small))
            try:
                sub=[i16((0-v[1],4095-v[0])) for v in small]
                dec=caller('decap_second',sub,packed)
                dec['subtraction_union']=[min(v[0] for v in sub),max(v[1] for v in sub)]
                calls.append(dec)
            except AssertionError as e:calls.append({'caller':'decap_second','status':'not_proven','reason':'subtraction '+str(e)})
        else:
            calls += [{'caller':n,'status':'not_proven','reason':'Forward '+fw['small']['reason']} for n in ('encap','decap_second')]
        result={'extra':deleted,'forward':fw,'calls':calls,'all_callers_closed':all(x['status']=='pass' for x in calls)}
        records.append(result);print('mask',mask,'fw',[(k,v['status']) for k,v in fw.items()],'calls',[(x['caller'],x['status']) for x in calls],flush=True)
    sources=[Path(__file__),Path(R.__file__),Path(P.__file__)]
    sources += [raw/x for x in ('kem_stock.c','poly.c','base.s','cbd.s','crepmod3.s','add.s','gt864_poly_api.c','gt864_fr0_basemul_d1.c','gt864_fr0_basemul_tables.h','byte_api.c','byte_boundary.c','cluster_transpose_frombytes.c','gt864_forward_six_bank.S','gt864_fr0_inverse9_block.S','gt864_inverse16_blocks.s')]
    (B/'proof.json').write_text(json.dumps({'scope':'explore/review; no assembly changes','producers':prod,'baseinv':bi,'D1_theorem':theorem,'M5E':inv,'results':records,'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}},indent=2)+'\n')
if __name__=='__main__':main()

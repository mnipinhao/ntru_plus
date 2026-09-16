"""Default-off exact fixed-scale conversion gate; does not edit production."""
import sys, pathlib, json, contextlib, io, hashlib
P=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent))
import generate as g
import verify as v
Q=3457; R=65536
def fixed(a,b):
    bh=(2*b*32768+Q)//(2*Q)
    t=max(-32768,min(32767,(a*bh+16384)//32768))
    return v.signed(v.signed(a*b)-t*Q)
ledger={}
for name,b,lo,hi,old in [('input_R',-147,-32768,32767,867),
                         ('inverse_Rinv',v.center(pow(R,-1,Q)),-2000,2000,1)]:
    values=[];different=0
    for x in range(lo,hi+1):
        y=fixed(x,b);z=v.redc(x*old)
        assert (y-z)%Q==0
        values.append(y);different+=y!=z
    bound=max(map(abs,values))
    assert bound <= 4000, (name,bound)
    ledger[name]={'b':b,'bhat':(2*b*32768+Q)//(2*Q),'input':[lo,hi],
                  'output':[min(values),max(values)],'tested':hi-lo+1,
                  'different_integer_representatives':different}

class FixedDAG(g.DAG):
    def __init__(self):
        self.fixed_constants={}
        super().__init__()
    def constant(self,name,value):
        if name in ('r2','one'):return name  # replaced conversion has no use for these
        return super().constant(name,value)
    def fixed(self,a,b):
        if b not in self.fixed_constants:
            c=self.constant(self.fresh(),b)
            h=self.constant(self.fresh(),(2*b*32768+Q)//(2*Q))
            self.fixed_constants[b]=(c,h)
        c,h=self.fixed_constants[b]
        z=self.binary('mul',a,c)
        t=self.binary('sqrdmulh',a,h)
        self.emit(f'mls V<{z}>.8h, V<{t}>.8h, V<q>.8h')
        return z
    def mm(self,a,b,bqi=None):
        if b=='r2':return self.fixed(a,-147)
        if b=='one':return self.fixed(a,v.center(pow(R,-1,Q)))
        return super().mm(a,b,bqi)

# Generate models with only the two fixed-scale operation sites replaced.
saved=g.DAG;g.DAG=FixedDAG
candidate={k:fn().lines for k,fn in [('baseinv_num',g.numerator),('baseinv_finish',g.finish)]}
g.DAG=saved
oldcodes={k:v.CODES[k] for k in candidate}
for k,fn in [('baseinv_num',g.numerator),('baseinv_finish',g.finish)]:
    assert oldcodes[k]==fn().lines, 'generator/baseline model drift'
v.CODES.update(candidate)
capture=io.StringIO()
with contextlib.redirect_stdout(capture):v.main()
full=json.loads(capture.getvalue())
# verify.main also reruns the OLD conversion's range test. Distinguish it
# explicitly from the new exhaustive conversion ledger above.
full['initial_REDC_bound_is_old_baseline_only']=True
# Analytic envelope closes the changed boundary for ALL inputs, not just tests.
# Every later product has |a|,|b|<=4000. Signed REDC correction is <=32768*q.
correction=32768*Q
assert 4000**2+correction<2**31
assert (4000**2+correction)//R==1972
# Numerator differences and denominator's pre-product sum <=2*1972<4000;
# final denominator sum <=3944. Prefix/recovery products return <=1972.
# Finish's three products are inside (-q,q), retaining unique centered output.
for x in range(-1972,1973):
    y=x+(Q if x<0 else 0)
    y-=Q if y>1728 else 0
    assert y==v.center(x)
result={'status':'model-and-range-pass','production_changed':False,
 'conversion_ledger':ledger,'full_symbolic_gate':full,
 'range':{'later_operand_abs':4000,'REDC_abs':1972,'sum_abs':3944,
          'int32_numerator_abs':4000**2+correction,'finish_output_abs':1728},
 'arithmetic_saving_per_BaseInv':36*(3*4+4),
 'exact_model_instruction_counts':{k:{'old':len(oldcodes[k]),'new':len(candidate[k]),
     'saved_per_call':36*(len(oldcodes[k])-len(candidate[k]))} for k in candidate},
 'note':'576 fewer arithmetic instructions is a pre-lowering projection; constants and scheduling not counted.',
 'source_hashes':{str(f.relative_to(P.parent)):hashlib.sha256(f.read_bytes()).hexdigest()
   for f in [P.parent/'generate.py',P.parent/'verify.py',P/'prove.py']}}
(P/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
(P/'candidate-model.json').write_text(json.dumps(candidate,indent=2)+'\n')
print(json.dumps(result,indent=2))

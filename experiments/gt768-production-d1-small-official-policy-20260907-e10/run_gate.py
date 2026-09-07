"""Source-derived package and full SUPERCOP gate; run on Pi, not live SC tree."""
import sys, re, json, hashlib, shutil, statistics
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,'/home/pi/gt768-four-gates-20260907-e09')
import common as c
c.R=R; c.B=R/'.build'; c.B.mkdir(exist_ok=True)
B=c.B; SRC=R/'NTRU+768'; ORIGINAL=c.PROD
OFF=c.SC/'crypto_kem/ntruplus768/aarch64'
def sources(root):
    text=(root/'Makefile').read_text().replace('\\\n',' ')
    variables=dict(re.findall(r'^(\w+)\s*:=\s*(.*)$',text,re.M))
    def expand(v): return re.sub(r'\$\((\w+)\)',lambda m:expand(variables[m[1]]),v)
    return [root/x for x in expand(variables['KEM_SOURCES']).split()]
result={'id':R.name,'production_revision':'0bdc5798d848c25c09e308ab4a9de2cda250d0c1','tests':{},'exports':{}}
def save(): c.save('gate',result)
result['tests']['package']=c.run(['make','check','BUILD_DIR='+str(B/'package'),'CFLAGS=-O3 -march=native -mtune=native -fwrapv -fPIC -fPIE -std=c99 -Wall -Wextra -Wpedantic -ffunction-sections -fdata-sections'],'package-check.log',SRC)
print('source package make check PASS',flush=True); save()
adapter=(c.P/'gt-production/adapter.c').read_text()
leaves=[]
for name,root in [('e10-production',ORIGINAL),('e10-candidate',SRC)]:
    dest=B/name; dest.mkdir(exist_ok=True); provenance={}
    for i,p in enumerate(sources(root)):
        asm=p.suffix=='.S'
        cmd=['gcc','-O3','-std=c99','-E','-P','-I'+str(root),'-I'+str(root/'internal')]
        if asm: cmd+=['-x','assembler-with-cpp']
        out=c.run(cmd+[p],name+'-preprocess-'+str(i)+'.log')
        for symbol in ['crypto_kem_keypair','crypto_kem_enc','crypto_kem_dec']:
            out=re.sub(r'\b'+symbol+r'\b','gt_policy_'+symbol,out)
        n='unit_%02d'%i+('.s' if asm else '.c'); (dest/n).write_text(out)
        provenance[n]={'source':str(p),'source_sha256':c.sha(p),'export_sha256':c.sha(dest/n)}
    for n in ['api.h','params.h']: shutil.copy2(root/n,dest/n)
    (dest/'adapter.c').write_text(adapter);(dest/'architectures').write_text('aarch64\n')
    result['exports'][name]=provenance
    c.PROD=root
    result['tests'][name]=c.validate(dest)
    leaves.append(dest);save()
# Copy raw Official source; omit goal markers only in isolated benchmark copy
# so all three builds use the same SUPERCOP timing classification.
official=B/'e10-official';official.mkdir(exist_ok=True)
for p in OFF.iterdir():
    if p.is_file() and not p.name.startswith('goal-'):shutil.copy2(p,official/p.name)
result['official_sources']={p.name:c.sha(p) for p in OFF.iterdir() if p.is_file()}
c.PROD=ORIGINAL
original_compile=c.compile_cmd
def with_supercop_support(leaf):
    cmd=original_compile(leaf)
    if leaf==official:
        cmd += ['-I'+str(c.SC/'bench/pinhao/include'),
                '-I'+str(c.SC/'bench/pinhao/include/aarch64')]
        cmd += sorted((c.SC/'bench/pinhao/lib/cryptoint/aarch64').glob('*.o'))
    return cmd
c.compile_cmd=with_supercop_support
result['tests']['e10-official']=c.validate(official,abi=False)
leaves.append(official)
# Actual candidate link must contain two Encap-small calls and Q31 reciprocal.
obj=c.run(['objdump','-d',B/'e10-candidate-kat'],'candidate-disassembly.log')
assert len(re.findall(r'\bbl\s+[^\n]*<gt_internal_poly_ntt_encap_small>',obj))==2
assert 'gt_decap_poly_basemul' in obj
result['linked_audit']='two Encap-small BL sites, Decap basemul present; raw disassembly retained'
# Policy clear trace must exactly match previous validated same-policy leaf.
expected=(Path('/home/pi/gt768-four-gates-20260907-e09/.build/g2r-small-coverage.log')).read_text()
assert result['tests']['e10-candidate']['coverage']==expected
save();print('all leaf correctness / six-path cleanup / linkage PASS',flush=True)
result['runs']=c.benchmark('e10',leaves)
result['aggregate']={leaf.name:{op:statistics.median(r['median'][op] for r in result['runs'] if r['variant']==leaf.name) for op in ['keypair_cycles','enc_cycles','dec_cycles']} for leaf in leaves}
save();print('COMPLETE',result['aggregate'],flush=True)

"""ELF retained-section/reference equality and exported-leaf KAT gate."""
from pathlib import Path
import subprocess,re,json,hashlib
R=Path(__file__).resolve().parent; B=R/'.build'; P=B/'NTRU+768'
OLD=Path('/home/pi/gt768-source-readability-cleanup-20260908-e26/.build/NTRU+768')
def run(args):return subprocess.check_output(list(map(str,args)),text=True)
def compile(root,name,tag):
    obj=B/(tag+'.o')
    subprocess.run(['gcc','-O3','-I'+str(root),'-c',str(root/name),'-o',str(obj)],check=True)
    return obj
def sections(obj):
    out={}
    for line in run(['readelf','-SW',obj]).splitlines():
        m=re.search(r'\]\s+(\S+)\s+PROGBITS\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)\s+\S+\s+(\S+)',line)
        if m and 'A' in m[3] and int(m[2],16):
            tmp=B/'section.bin'
            subprocess.run(['objcopy','-O','binary','--only-section='+m[1],obj,tmp],check=True)
            out[m[1]]=tmp.read_bytes()
    return out
def relocs(obj,exclude=()):
    rows=[];section=''
    for line in run(['readelf','-rW',obj]).splitlines():
        if line.startswith('Relocation section '):section=line.split("'")[1]
        parts=line.split()
        if len(parts)>=5 and parts[2].startswith('R_AARCH64') and section not in exclude:
            rows.append((section,parts[0],*parts[2:]))
    return rows
result={'baseline':'52117af3733f842e70e2cea322268320bfb97ff0','objects':{}}
for name,removed,ref in [('base.S','.text.module_base_body','basemul.S'),('ntt.S','.text.module_invntt_body','invntt.S')]:
    a=compile(OLD,name,'before-'+name);b=compile(P,name,'after-'+name)
    c=compile(P,'test/reference/'+ref,'reference-'+name)
    sa,sb,sc=sections(a),sections(b),sections(c)
    assert removed not in sb
    assert sa.pop(removed)==sc[removed]
    assert sa==sb,(name,'retained sections differ')
    assert relocs(a,('.rela'+removed,))==relocs(b),(name,'retained relocations differ')
    assert [x for x in relocs(a) if x[0]=='.rela'+removed]==relocs(c)
    result['objects'][name]={'retained_sections':{k:hashlib.sha256(v).hexdigest() for k,v in sb.items()},
      'moved_section':removed,'moved_bytes':len(sc[removed]),'reference_bytes_identical':True,'relocations_identical':True}
leaf=B/'leaf'
subprocess.run(['python3',P/'scripts/export_supercop.py',leaf,'--prefix','gt768_e27_'],check=True)
objects=[]
for src in sorted(leaf.iterdir()):
    if src.suffix not in ('.c','.s'):continue
    obj=B/('leaf-'+src.name+'.o')
    subprocess.run(['gcc','-O3','-I'+str(leaf),'-I/home/pi/gt768-production-policy-threeway-20260907-e08/.build/shim','-I/home/pi/supercop-20260627/bench/pinhao/include','-I/home/pi/supercop-20260627/bench/pinhao/include/aarch64','-c',src,'-o',obj],check=True)
    objects.append(obj)
symbols=run(['nm','-g','--defined-only',*objects])
for name in ['poly_basemul','poly_invntt','gt_block_major_poly_invntt']:
    assert not re.search(r'\bgt768_e27__?'+name+r'$',symbols,re.M),name
assert 'gt768_e27_gt_rowbitrev_lambda' in symbols
kat=B/'export-kat';kat.mkdir()
subprocess.run(['gcc','-O3','-I'+str(leaf),'-I'+str(P/'kat'),P/'kat/PQCgenKAT_kem.c',P/'kat/rng.c',P/'kat/aes.c',*objects,'-o',kat/'kat'],check=True)
subprocess.run([kat/'kat'],cwd=kat,check=True)
for ext in ['req','rsp']:
    assert (kat/('PQCkemKAT_2336.'+ext)).read_bytes()==(P/'kat/expected'/('PQCkemKAT_2336.'+ext)).read_bytes()
result['export']={'reference_symbols_absent':True,'shared_lambda_present':True,'kat_req_rsp_exact':True}
(R/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

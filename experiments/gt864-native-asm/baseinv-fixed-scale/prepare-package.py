"""Build an isolated package; never overwrite the production source tree."""
import pathlib,shutil,hashlib,json,re
p=pathlib.Path(__file__).resolve().parent;r=p.parents[2]
prod=r/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
b=p/'build/package';b.mkdir(parents=True,exist_ok=True)
shutil.copytree(prod,b,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.o','*.so','PQCkemKAT*','test_kem','PQCgenKAT_kem','check-*'))
audit={}
for k,kid in [('baseinv_num','binv_num_tile'),('baseinv_finish','binv_finish_tile')]:
 src=p/k/'candidate.opt.S'
 lines=[s.split('//')[0].rstrip() for s in src.read_text().splitlines()]
 clean='\n'.join(s for s in lines if s.strip())+'\n'
 assert not re.search(r'\b[VQ]<',clean)
 assert not re.search(r'\[sp\b',clean)
 ops=[s.strip().split()[0] for s in lines if s.strip() and not s.strip().startswith('.') and not s.strip().endswith(':')]
 assert ops.count('ldr')==4
 assert ops.count('str')==(4 if k=='baseinv_num' else 3)
 assert not any(x in ('bl','blr') for x in ops)
 audit[k]={'instructions_including_ret':len(ops),'q_loads':ops.count('ldr'),'q_stores':ops.count('str'),'spill':False,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()}
 (b/f'gt864_native_{k}.S').write_text(f'#ifdef __APPLE__\n#define {kid} _{kid}\n#endif\n'+clean)
manifest=[]
for line in (prod/'SOURCE-MANIFEST.sha256').read_text().splitlines():
 name=line.split('  ',1)[1];manifest.append(hashlib.sha256((b/name).read_bytes()).hexdigest()+'  '+name)
(b/'SOURCE-MANIFEST.sha256').write_text('\n'.join(manifest)+'\n')
(p/'physical-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit,indent=2))

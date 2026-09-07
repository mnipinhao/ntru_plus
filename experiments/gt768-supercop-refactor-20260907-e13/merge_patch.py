"""R3: namespace file-private assembler identifiers and merge one family.

Print only an apply_patch proposal. Preserve instruction order and constants;
fresh object section audits and runtime gates remain mandatory.
"""
import sys,re,difflib,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2]
P=R/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768'
groups={
 'pack':['pack.S','unpack.S','keygen_pack.S','decap_pack.S'],
 'base':['base.S','keygen_baseinv_prepare.S','keygen_baseinv_tree.S','keygen_baseinv_finish.S','fqinv.S','encap_muladd.S','decap_verify.S','decap_packed64.S','decap_base.S'],
 'ntt':['ntt.S','invntt.S','decap_ntt.S','decap_forward.S'],
}
files=groups[sys.argv[1]]
parts=[]
for name in files:
 s=(P/name).read_text(); prefix='module_'+Path(name).stem+'_'
 exports=set(re.findall(r'^\s*\.(?:global|globl|weak)\s+(\w+)',s,re.M))
 labels=set(re.findall(r'^\s*([\w.$]+):',s,re.M))
 macros=set(re.findall(r'^\s*\.macro\s+(\w+)',s,re.M))
 aliases=set(re.findall(r'^\s*(\w+)\s+\.req\b',s,re.M))
 equs=set(re.findall(r'^\s*\.(?:equ|set)\s+(\w+)',s,re.M))
 names=(labels|macros|aliases|equs)-exports
 names={x for x in names if not x.isdigit()}
 rename={x:prefix+x for x in names}
 if names:
  pattern=re.compile(r'(?<![\w.$])('+ '|'.join(map(re.escape,sorted(names,key=len,reverse=True)))+r')(?![\w.$])')
  s=pattern.sub(lambda m:rename[m[0]],s)
 # Original input objects each had an independent default text/data section.
 for section,flags in [('text','ax'),('data','aw')]:
  s=re.sub(r'^\s*\.'+section+r'\s*$', '#ifdef __APPLE__\n.'+section+'\n#else\n.section .'+section+'.'+prefix+'body,"'+flags+'",%progbits\n#endif',s,flags=re.M)
 initial='#ifdef __APPLE__\n.text\n#else\n.section .text.'+prefix+'body,"ax",%progbits\n#endif\n'
 parts.append('/* BEGIN original '+name+'; private namespace '+prefix+' */\n'+initial+s+'\n/* END original '+name+' */\n')
changes={P/files[0]:'\n'.join(parts)}
make=(P/'Makefile').read_text()
for name in files[1:]:make=re.sub(r'^\t'+re.escape(name)+r'\s*\\?\n','',make,flags=re.M)
changes[P/'Makefile']=make
# Source-coverage checks must inspect the new owner without changing needles.
for script in (P/'scripts').glob('*.py'):
 s=script.read_text()
 for name in files[1:]:s=s.replace(name,files[0])
 if s!=script.read_text():changes[script]=s
removed={P/n for n in files[1:]}
manifest=P/'SOURCE-MANIFEST.sha256'
changes[manifest]=''.join(hashlib.sha256(changes.get(f,f.read_text()).encode()).hexdigest()+'  ./'+str(f.relative_to(P))+'\n' for f in sorted(P.rglob('*')) if f.is_file() and f!=manifest and f not in removed)
print('*** Begin Patch')
for f,after in changes.items():
 print('*** Update File: '+str(f))
 for l in list(difflib.unified_diff(f.read_text().splitlines(),after.splitlines()))[2:]:print('@@' if l.startswith('@@') else l)
for f in removed:print('*** Delete File: '+str(f))
print('*** End Patch')

#!/usr/bin/env python3
"""Export readable C + Linux-preprocessed assembly to a fresh external leaf.

Run on AArch64 Linux. No randombytes implementation, test mains, goals, or
objects are included. Each exported definition gets a private namespace;
the three public API names are supplied through SUPERCOP's crypto_kem.h.
"""
import argparse,hashlib,json,re,subprocess,tempfile,platform
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('destination',type=Path)
p.add_argument('--prefix',default='gt768_e13_')
a=p.parse_args();root=Path(__file__).resolve().parents[1]
assert platform.system()=='Linux' and platform.machine()=='aarch64', 'Requires Linux AArch64 GCC'
assert re.fullmatch('[A-Za-z_][A-Za-z0-9_]*',a.prefix)
assert not a.destination.exists(), 'Use a fresh destination; never overwrite a leaf'
assert not a.destination.resolve().is_relative_to(root), 'Export must be outside source package'
sources=subprocess.check_output(['make','-s','--no-print-directory','-f','Makefile','-f','-','export_sources'],cwd=root,
 input=b'export_sources:\n\t@echo $(KEM_SOURCES)\n').decode().split()
assert 'randombytes.c' not in sources
assert all(not Path(name).parts[0] == 'test' for name in sources), 'Test source in KEM closure'
defined=set()
with tempfile.TemporaryDirectory(prefix='gt768-export-') as temp:
 for i,name in enumerate(sources):
  obj=Path(temp)/f'{i}.o'
  subprocess.run(['gcc','-O3','-I'+str(root),'-c',str(root/name),'-o',str(obj)],check=True)
  nm=subprocess.check_output(['nm','-g','--defined-only',str(obj)]).decode()
  defined.update(line.split()[-1] for line in nm.splitlines() if len(line.split())>=3)
assert 'randombytes' not in defined
assert not ({'poly_basemul', '_poly_basemul', 'poly_invntt', '_poly_invntt',
             'gt_block_major_poly_invntt', '_gt_block_major_poly_invntt'} & defined), 'Reference kernel in export'
a.destination.mkdir(parents=True)
ns=a.destination/'namespace.h'
ns.write_text('#ifndef GT768_EXPORT_NAMESPACE_H\n#define GT768_EXPORT_NAMESPACE_H\n'+
 ''.join('#define '+name+' '+a.prefix+name+'\n' for name in sorted(defined))+'#endif\n')
provenance={}
for name in sources:
 src=root/name
 if src.suffix=='.S':
  output=subprocess.check_output(['gcc','-E','-P','-x','assembler-with-cpp','-I'+str(root),'-include',str(ns),str(src)])
  dest=a.destination/src.with_suffix('.s').name
 else:
  output=('#include "namespace.h"\n'+src.read_text()).encode()
  dest=a.destination/name
 dest.write_bytes(output)
 provenance[dest.name]={'source':name,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(output).hexdigest()}
for header in root.glob('*.h'):
 if header.name=='randombytes.h':continue
 (a.destination/header.name).write_bytes(header.read_bytes())
public=['crypto_kem_keypair','crypto_kem_enc','crypto_kem_dec']
adapter='#include "crypto_kem.h"\n'
adapter+='extern int '+a.prefix+public[0]+'(unsigned char*,unsigned char*);\n'
for name in public[1:]:adapter+='extern int '+a.prefix+name+'(unsigned char*,unsigned char*,const unsigned char*);\n'
adapter+='int crypto_kem_keypair(unsigned char*p,unsigned char*s){return '+a.prefix+public[0]+'(p,s);}\n'
adapter+='int crypto_kem_enc(unsigned char*c,unsigned char*s,const unsigned char*p){return '+a.prefix+public[1]+'(c,s,p);}\n'
adapter+='int crypto_kem_dec(unsigned char*s,const unsigned char*c,const unsigned char*k){return '+a.prefix+public[2]+'(s,c,k);}\n'
(a.destination/'adapter.c').write_text(adapter)
(a.destination/'architectures').write_text('aarch64\n')
(a.destination/'LICENSE').write_bytes((root/'LICENSE').read_bytes())
# Metadata is beside, never inside the implementation leaf.
a.destination.with_suffix('.export.json').write_text(json.dumps({'prefix':a.prefix,'symbols':sorted(defined),'files':provenance},indent=2)+'\n')
print(a.destination)

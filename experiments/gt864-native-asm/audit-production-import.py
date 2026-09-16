"""Verify production core instructions equal the tested scheduled artifacts."""
import pathlib,re,subprocess,tempfile,hashlib,json
p=pathlib.Path(__file__).resolve().parent;r=p.parents[1]
prod=r/'ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864'
def normalized(s):
 return [l.strip() for line in s.splitlines() if (l:=line.split('//')[0]).strip()]
results=[]
with tempfile.TemporaryDirectory(prefix='gt864-import-elf-') as tmp:
 for k in ['baseinv_num','baseinv_prefix','baseinv_inverse','baseinv_recover','baseinv_finish','basemul','center32','inverse9','inverse16_lazy','inverse_tail_lazy']:
  src=(p.parent/'gt864-next-dag/inverse9' if k=='inverse9' else p/k)/'candidate.opt.S'
  dest=prod/f'gt864_native_{k}.S'
  text=dest.read_text();assert normalized('\n'.join(text.splitlines()[4:]))==normalized(src.read_text()),k
  assert not re.search(r'\b(?:sp|wsp)\b','\n'.join(text.splitlines()[4:])),k
  subprocess.run(['clang','--target=aarch64-linux-gnu','-c',str(dest),'-o',str(pathlib.Path(tmp)/(k+'.o'))],check=True)
  results.append({'core':k,'instruction_identity':'pass','ELF_assembly':'pass','stack_spills':0,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
 assert (prod/'gt864_native_public.S').read_bytes()==(p/'integration/public.S').read_bytes()
 subprocess.run(['clang','--target=aarch64-linux-gnu','-c',str(prod/'gt864_native_public.S'),'-o',str(pathlib.Path(tmp)/'wrapper.o')],check=True)
 assert (prod/'gt864_native_scaled_tables.h').read_text().replace('GT864_NATIVE_SCALED_TABLES_H','GT864_FR0_INVERSE_BARRETT_TABLES_H')==(r/'experiments/gt864-decaps-scale/scaled_tables.h').read_text()
print(json.dumps({'cores':results,'wrapper_identity':'pass','scale_table_identity':'pass'},indent=2))

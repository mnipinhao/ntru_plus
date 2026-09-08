"""Fail closed on residual symbols, stack traffic, hidden calls or bad encoding.

This checks allocation artifacts, not cycles or mathematical equivalence.
"""
import pathlib,re,subprocess,tempfile,json,sys
p=pathlib.Path(__file__).resolve().parent
suffix='opt' if '--scheduled' in sys.argv else 'alloc'
files=sorted(p.glob(f'*/candidate.{suffix}.S'))+[p.parent/f'gt864-next-dag/inverse9/candidate.{suffix}.S']
result=[]
with tempfile.TemporaryDirectory(prefix='gt864-objects-') as tmp:
    for i,f in enumerate(files):
        code='\n'.join(l.split('//')[0].strip() for l in f.read_text().splitlines())
        assert not re.search(r'[VQDXW]<',code),f
        assert not re.search(r'\b(?:sp|wsp|x18|x19|x2[0-9])\b',code),f
        assert not re.search(r'^\s*(?:bl|blr|push|pop)\b',code,re.M),f
        subprocess.run(['clang','--target=aarch64-linux-gnu','-c',str(f),'-o',f'{tmp}/{i}.o'],check=True)
        ins=[l for l in code.splitlines() if l and not l.startswith('.') and not l.endswith(':')]
        result.append({'source':str(f.relative_to(p.parent)),'instructions_including_ret':len(ins),
          'vector_registers':sorted(set(map(int,re.findall(r'\b[vqd](\d+)\b',code)))),
          'coefficient_stack_spills':0,'elf_assembly':'pass'})
print(json.dumps(result,indent=2))

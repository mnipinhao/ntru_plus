#!/usr/bin/env python3
"""Current-image BaseInv census; not an optimization or latency proof."""
import hashlib,json,re,subprocess
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def main():
    elf=ROOT/'build/bench_serialize_compare'
    text=subprocess.check_output(['objdump','-d','--no-show-raw-insn','--disassemble=poly_baseinv',str(elf)],text=True)
    rows=re.findall(r'^\s*([0-9a-f]+):\s+(\w+)\s*(.*)$',text,re.M)
    assert rows
    stack=[dict(address=a,op=op,operands=s) for a,op,s in rows if '%rsp' in s]
    calls=[dict(address=a,op=op,operands=s) for a,op,s in rows if op.startswith('call')]
    source=(ROOT/'upstream/supercop-avx2/poly.c').read_text()
    batch=source.split('static inline int fqinv_batch')[1].split('static inline void poly_baseinv_2')[0]
    clears=re.findall(r'secure_clear\((.*?),\s*sizeof',batch)
    result={'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
        'source_sha256':hashlib.sha256(source.encode()).hexdigest(),
        'class':'linked static census; not dynamic counts or measured critical path',
        'batch_inlined_into_poly_baseinv':True,
        'source_clear_objects_in_order':clears,
        'linked_calls':calls,'stack_instruction_rows':stack,
        'opcode_counts':dict(Counter(op for a,op,s in rows)),
        'gate':{'second_ASM':'not selected; complete executable schedule still required',
        'important_constraint':'SysV YMM are caller-clobbered across declassify/explicit_bzero. Live recovery values need storage or a separately justified clear schedule; source arrays are not automatically removable spills.',
        'next_candidate':'same arithmetic reverse recovery/application handoff with explicit preservation and zeroization ledger',
        'no_claim':'This census does not prove all stack traffic necessary or rule out a better allocation.'}}
    (ROOT/'results/baseinv-followup-census.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'results/baseinv-followup-disassembly.txt').write_text(text)
    print(json.dumps({'stack_rows':len(stack),'call_rows':len(calls),'clear_objects':clears}))
if __name__=='__main__':main()

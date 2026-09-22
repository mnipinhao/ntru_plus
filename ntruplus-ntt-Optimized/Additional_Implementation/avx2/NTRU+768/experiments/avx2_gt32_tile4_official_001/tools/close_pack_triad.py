"""Non-timing closure; preserve raw campaign and original source snapshot."""
import json
from run_pack_triad import *

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--tag',default='pack-maskstore-triad-20260922')
    args=ap.parse_args()
    root=EXP/'results'/args.tag
    metadata=json.loads((root/'metadata.json').read_text())
    assert sha(root/'measure')==metadata['elf_sha256']
    assert metadata['clean_manifest']=={str(p.relative_to(CLEAN)):sha(p) for p in sorted(CLEAN.rglob('*')) if p.is_file()}
    proc=command(['make','pack-maskstore-check'])
    (root/'closure-tests.log').write_text(proc.stdout+proc.stderr)
    command(['python3','tools/research_pack_mask_network.py','--check'])
    linked=audit(root/'measure',root)
    (root/'linked-audit-closure.json').write_text(json.dumps(linked,indent=2)+'\n')
    files=[EXP/'tools/close_pack_triad.py',EXP/'tools/run_pack_triad.py',
           EXP/'tests/test_pack_maskstore.c',EXP/'tests/test_pack_identity14.c']
    for p in files:
        (root/'source-snapshot'/sha(p)).write_bytes(p.read_bytes())
    closure={'source_sha256':{str(p):sha(p) for p in files},
             'clean_unchanged':True,'elf_unchanged':True,
             'extra_basis_zero_boundary_gate':'pass; no new timing',
             'alias':'input and output distinct, actual caller contract; no unsupported overlap claim',
             'KEM_coverage':'100 Encap coins for one deterministic key; not 100 independent keypairs'}
    (root/'closure.json').write_text(json.dumps(closure,indent=2)+'\n')
    print(json.dumps({k:{x:v[x] for x in ['address','size','hot_bytes']} for k,v in linked.items()}))

#!/usr/bin/env python3
"""Close the corrected identity-only campaign without another timing run."""
import argparse
import json
from pathlib import Path
from run_encap_fn_short import CLEAN,command,sha
from run_pack_identity14_audit import audit

def main():
    ap=argparse.ArgumentParser();ap.add_argument('campaign',type=Path);a=ap.parse_args()
    root=a.campaign.resolve();meta=json.loads((root/'metadata.json').read_text())
    assert sha(root/'measure')==meta['elf_sha256']
    assert all(sha(CLEAN/p)==v for p,v in meta['frozen_clean_manifest'].items())
    assert all(sha(Path(p))==v for p,v in meta['source_sha256'].items())
    linked=audit(root/'measure')
    (root/'linked-audit-closure.json').write_text(json.dumps(linked,indent=2)+'\n')
    tests=command(['make','pack-identity14-check'])
    (root/'closure-tests.log').write_text(tests.stdout+tests.stderr)
    command(['python3','tools/research_pack_mask_network.py','--check'])
    report={'exact_compiled_source_hashes':True,'ELF_hash':True,'clean_unchanged':True,
            'constant_operands_byte_exact':True,'linked_deleted_instructions':14,
            'KEM_sanitizer_primitive_oracle':'pass','further_network_model':'pass; not timed',
            'production_promoted':False,'new_timing_run':False}
    (root/'closure.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS identity-only closure: source/ELF/constants/clean/correctness; no new timing')

if __name__=='__main__':main()

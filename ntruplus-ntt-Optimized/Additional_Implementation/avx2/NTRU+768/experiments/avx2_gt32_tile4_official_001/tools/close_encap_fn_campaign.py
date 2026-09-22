#!/usr/bin/env python3
"""Verify a saved campaign against current sources; add independent closure evidence."""
import argparse
import json
from pathlib import Path
from run_encap_fn_short import EXP,CLEAN,command,sha,audit

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("campaign",type=Path)
    args=ap.parse_args()
    root=args.campaign.resolve()
    meta=json.loads((root/"metadata.json").read_text())
    for path,value in meta["source_sha256"].items():
        assert sha(Path(path))==value,("compiled source drift",path)
    for path,value in meta["frozen_clean_manifest"].items():
        assert sha(CLEAN/path)==value,("clean drift",path)
    assert sha(root/"measure")==meta["elf_sha256"]
    command(["python3",str(EXP/"tools/generate_encap_fn_eager.py"),"--check"])
    linked=audit(root/"measure")
    assert linked==json.loads((root/"linked-audit.json").read_text())
    proof=command(["python3",str(EXP/"tests/test_encap_fn_model.py"),"-v"])
    gates=command(["make","encap-fn-eager-check","encap-fn-eager-sanitize"])
    (root/"closure-tests.log").write_text(proof.stdout+proof.stderr+gates.stdout+gates.stderr)
    report=dict(compiled_source_hashes="pass",frozen_clean_recursive_hashes="pass",
        measured_ELF_hash="pass",linked_audit_replay="identical",
        model_and_KEM_sanitizer="pass",
        cpu_topology=json.loads(command(["lscpu","-J"]).stdout),
        generator_sha256=sha(EXP/"tools/generate_encap_fn_eager.py"),
        proof_artifact_sha256=sha(EXP/"generated/encap_fn_eager.json"),
        timed_source_unchanged=True,new_timing_run=False)
    (root/"closure.json").write_text(json.dumps(report,indent=2)+"\n")
    print("PASS: source/ELF/frozen clean hashes, linked replay, correctness and sanitizer closure")

if __name__=="__main__":
    main()

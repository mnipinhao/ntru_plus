#!/usr/bin/env python3
"""Same-DAG BaseMul prototype: finalize each coefficient before its only store."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from vector_mapping_source_ledger import Source, replay_loop, stats, current_ledger, operands
import generate_tile4 as gt

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT.parent.parent / "clean/avx2-gt32-clean"
NAME = "ntruplus768_exp001_basemul_eager_m"

def dag_outputs(lines):
    """Exact expression identity over signed-word instructions, no numeric truncation model.

    A Mont low word is represented by vpmullw, NOT mathematical unbounded multiply.
    Thus identical output expressions prove identical bit patterns including intentional wrap.
    """
    regs = {}
    memory = {}
    operations = Counter()
    for line in replay_loop(lines, 1, ".Leager_bm_b3_loop" if
                            any(".Leager_" in x for x in lines) else ".Ltile4_bm_b3_loop"):
        words=line.split(None,1)
        if not words or not words[0].startswith("v") or words[0]=="vzeroupper":
            continue
        op=words[0]
        args=[x.strip() for x in operands(words[1])]
        def get(x):
            if x.startswith("%ymm"):
                return regs[x]
            x=x.replace(".Leager_",".Ltile4_")
            return memory.get(x,("input",x))
        if op.startswith("vmov"):
            value=get(args[0])
        else:
            assert op in ("vpmullw","vpmulhw","vpaddw","vpsubw"),op
            value=(op,*(get(x) for x in args[:-1]))
            operations[value]+=1
        if args[-1].startswith("%ymm"):
            regs[args[-1]]=value
        else:
            assert args[-1].endswith("(%rdi)")
            memory[args[-1]]=value
    return [memory[f"{i}(%rdi)"] for i in (0,32,64,96)],operations

def build():
    source = (CLEAN / "basemul.s").read_text()
    control = Source(source).function("ntruplus768_basemul_general_m_avx2")
    body = "\n".join(control)
    finalizer = "\n".join(Source(source).expand(["TILE4_MONT_RSQ"]))
    # This uses only existing scratch ymm13/14 and accumulator ymm15.
    # No input or QINV companion is overwritten.
    for off in (0, 32, 64):
        old = f"vmovdqu %ymm15, {off}(%rdi)"
        assert body.count(old) == 1
        body = body.replace(old, finalizer + "\n" + old)
    late = "\n".join(Source(source).expand(["TILE4_OUTPUT_SOA_LATE_RSQ"]))
    assert body.count(late) == 1
    body = body.replace(late, finalizer + "\nvmovdqu %ymm15, 96(%rdi)")
    # Preserve the selected production leaf's existing return-boundary vzeroupper.
    body = body.replace(".Ltile4_", ".Leager_")
    baseline_dag,baseline_operations=dag_outputs(control)
    candidate_dag,candidate_operations=dag_outputs(body.splitlines())
    assert baseline_dag==candidate_dag
    assert baseline_operations==candidate_operations
    start = source.index(".Ltile4_bm_q:\n")
    end = source.index(".Ltile4_bm_lambda_qpair02:\n", start)
    constants = source[start:end].replace(".Ltile4_", ".Leager_")
    constants = constants.replace(".Leager_bm_lambda:\n",
        ".globl ntruplus768_exp001_eager_lambda\nntruplus768_exp001_eager_lambda:\n.Leager_bm_lambda:\n")
    asm = ('/* Generated; research only. Same arithmetic, different finalizer schedule. */\n'
        '.section .text.gt768_fn_eager,"ax",@progbits\n.p2align 5\n'
        f'.globl {NAME}\n.type {NAME},@function\n{NAME}:\n{body}\n'
        f'.size {NAME},.-{NAME}\n.section .rodata\n.p2align 5\n'
        + constants + '\n.section .note.GNU-stack,"",@progbits\n')
    before = stats(replay_loop(control, 12, ".Ltile4_bm_b3_loop"), ("r8","r9"))
    after = stats(replay_loop(body.splitlines(), 12, ".Leager_bm_b3_loop"), ("r8","r9"))
    assert before["opcodes"]["vpmulhw"] == after["opcodes"]["vpmulhw"]
    assert before["opcodes"]["vpmullw"] == after["opcodes"]["vpmullw"]
    assert after["peak_live_YMM"] <= 16
    aos,mapping,owners=gt.serialized_mappings()
    lambda_text=source.split(".Ltile4_bm_lambda:\n",1)[1].split(".Ltile4_bm_lambda_qinv:\n",1)[0]
    lambda_values=[int(x) for line in lambda_text.splitlines() if ".short" in line
                   for x in line.split(".short",1)[1].split(",")]
    assert len(lambda_values)==192
    for w,owner in enumerate(owners):
        index=mapping[w]
        b,l=index//64,index%16
        expected=gt.lambda_montgomery(owner["k3"],owner["physical_q"],owner["branch"])
        assert lambda_values[b*16+l]==expected
        lam=expected*pow(gt.R,-1,gt.Q)%gt.Q
        assert (pow(lam,192,gt.Q)-pow(lam,96,gt.Q)+1)%gt.Q==0
    stages=current_ledger(CLEAN)
    # Independent add function remains, including both input reads.
    add_text=(CLEAN/"add.s").read_text().split("poly_add:\n",1)[1].split(".global poly_sub",1)[0]
    add_lines=[x.strip() for x in add_text.splitlines() if x.strip()]
    begin=add_lines.index("_looptop_add:")
    end=next(i for i,x in enumerate(add_lines) if x.startswith("jb "))
    add_ledger=stats(add_lines[:begin]+add_lines[begin+1:end+1]*8+add_lines[end+1:])
    stages["add_m"]=add_ledger
    multiplicity={"frontend":2,"NTT32_terminal":2,"decode":1,"Mul":1,"add_m":1,"pack":2}
    total={}
    for key,count in multiplicity.items():
        for field,n in stages[key]["classes"].items():
            total[field]=total.get(field,0)+count*n
    total["GPR_control_call_ret"]+=1 # highrange -> lazy serializer tail jump
    report = dict(candidate=NAME, control=before, candidate_ledger=after,
        range_certificate=dict(method="exact signed-word instruction expression identity",
            output_expressions_equal=True, identical_arithmetic_expression_multiset=True,
            arithmetic_operations_per_block=sum(baseline_operations.values()),
            implication="all bit patterns raw-exact; all pre-operation values unchanged",
            inherited_proof="generated/tile4_encap_range_refined.json",
            inherited_proof_sha256=hashlib.sha256((ROOT/"generated/tile4_encap_range_refined.json").read_bytes()).hexdigest(),
            low_word_wrap="vpmullw retained as 16-bit instruction operator",
            safety="no new arithmetic/reduction and no altered consumer input"),
        stage_ledgers=stages, caller_multiplicity=multiplicity,
        caller_source_classes=total,
        ownership=dict(all_768_owners=owners,wire_to_M=mapping,
            first_wire_packet_M_words=mapping[:16],lambda_identities_verified=192),
        class_delta={k:after["classes"].get(k,0)-before["classes"].get(k,0)
                     for k in set(before["classes"])|set(after["classes"])},
        frozen_clean_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest()
                            for f in sorted(CLEAN.iterdir()) if f.is_file()},
        contract=dict(layout="M unchanged", exponent=0, arithmetic="same DAG, raw exact",
            alias="out may equal h or r: complete 128-byte block loaded before first store",
            range="all arithmetic operands identical; finalizer scratch only ymm13/14",
            boundary="BaseMul only; separate add-m and serializer retained",
            mechanism="36 raw stores and 36 reloads removed; finalizer parallelism reduced",
            new_ASM_prototypes=1))
    return asm, json.dumps(report,indent=2,sort_keys=True)+"\n"

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    asm,report=build()
    for path,data in [(ROOT/"generated/encap_fn_eager.S",asm),
                      (ROOT/"generated/encap_fn_eager.json",report)]:
        if args.check:
            assert path.read_text()==data,path
        else:
            path.write_text(data)
    print("PASS: deterministic eager-finalizer source/model")

# P3B41 — K1 / K2 KEM-only implementations

Status: **Pi correctness and paired measurements completed after explicit authorization**.
K1 is the preferred experimental candidate. Production and generic P3B37 remain
unchanged; no commit or promotion was performed.

## Pi results

Pi 5, GCC 14.2.0, core 3; three repetitions in both execution orders.
Values are medians of six process medians, cycles per call. Forward includes
the identical input-reset overhead. Compare each candidate to its own same-run
P3B37 baseline, not across the two campaigns.

| Operation | K1 baseline | K1 | Saved cycles | K2 baseline | K2 | Saved cycles |
|---|---:|---:|---:|---:|---:|---:|
| Forward | 3517.601 | 3492.255 | 25.346 | 3517.677 | 3516.713 | 0.964 |
| Keygen | 54222.000 | 54162.250 | 59.750 | 54356.625 | 54329.375 | 27.250 |
| Encaps | 46118.300 | 46062.300 | 56.000 | 46132.175 | 46112.050 | 20.125 |
| Decaps | 44461.975 | 44412.475 | 49.500 | 44480.375 | 44434.700 | 45.675 |

K1 Forward improves 0.72%; K2 Forward is essentially neutral (0.027%).
All six Forward paired process medians improve for each, but K2's effect
is tiny. Do not attribute all full-KEM differences to twice an isolated
Forward delta: context and measurement boundaries differ.

Both pass 32 valid/tampered KEM cases, pk/ct/sk byte equality, instrumentation
equivalence, and 32 additional malformed ciphertext comparisons. Every
Forward process passes 256 guard cases and 64 serialized equivalence cases.
This is the existing differential harness, not a newly generated standard KAT.

PMU confirms -12 instructions per Forward and -24 per measured KEM operation;
branch counts are unchanged within each matched comparison. Both Pass-2
objects remain 4544 text bytes due to layout/alignment. Linked symbols show
the intended kem_only wrappers. Final throttle status is 0x0, temperature
61.5 C for both campaigns.

The frozen SUPERCOP Forward comparator is approximately 3854.25 cycles in
these runs. It is the unchanged 20260627/SHAKE256 campaign source, not verified
as upstream latest. Full-KEM table above compares to P3B37, not SUPERCOP.

Decision: retain K1 as the preferred KEM-only experimental candidate.
K2 is correct for the tested caller boundary but adds no meaningful isolated
Forward benefit. Neither is promoted automatically; candidate scores remain
investigate because no aggregate Slothy expected-cycle estimate is available.

## Exact lowering

Both candidates start from frozen P3B37, not from P3B38.
The two top branches are audited independently to resolve the actual loaded
constant pair to (1,9). Main-input support sets identify the mathematical
stage, rather than relying on stale source line numbers.

| Candidate | Removed reduction | Input support t | Replacement |
|---|---|---|---|
| K1 | main.stage1.node0 | {4,12} | ORR v18.16b,v24.16b,v24.16b |
| K2 | main.stage2.node0 | {2,6,10,14} | ORR v6.16b,v7.16b,v7.16b |

K1 replaces:

    mul       v18.8h, v24.8h, v11.h[0]
    sqrdmulh  v25.8h, v24.8h, v11.h[1]
    mls       v18.8h, v25.8h, v14.8h

K2 replaces:

    mul       v6.8h, v7.8h, v10.h[0]
    sqrdmulh  v8.8h, v7.8h, v10.h[1]
    mls       v6.8h, v8.8h, v14.8h

The original instructions are not necessarily adjacent in the scheduled
baseline. SSA checks verify the MUL and SQRDMULH consume the same input
version, the quotient has only its matching MLS consumer, and the constant
lanes belong to the same table load. The copy stays at the original MUL
position to preserve lifetime. No speculative copy coalescing is included.

Per helper: 513 → **511 instructions**. Each candidate removes one MUL,
one SQRDMULH, one MLS and adds one ORR copy.
Across six helper calls: six Algorithm-10 multiplications removed,
**net 12 instructions fewer**. Loads, tables, pointer updates, transpose,
wrapper save/restore and memory boundaries are unchanged.

This is mod-q equivalence, not raw representative equality.
P3B40 provides caller-specific range closure; it does not permit using these
outputs as both operands of generic 2F polynomial multiplication.

## Isolation

Staged K1 exports gt864_forward_poly_ntt_p41_k1_kem_only.
Staged K2 exports gt864_forward_poly_ntt_p41_k2_kem_only.
Their isolated poly API source calls the corresponding named wrapper.
The staged t1 comparator remains P3B37. Production and the original
P3B37 artifact are untouched. These are opt-in experiment libraries,
not general-purpose replacements for all GT consumers.

## Completed gates

- Baseline extraction, kernel contracts and static authoring gates.
- Both-top (b,bhat) provenance and reduction-consumer SSA audit.
- P3B40 source hash and passing caller mask linkage.
- Exhaustive scalar congruence check for the removed (1,9) product over
  all signed halfword inputs.
- Local Mac Slothy fixed-register window scheduling:
  K1 33.371 s, K2 33.101 s. No spill; full DFG selfcheck passes.
- Independent scheduled-versus-lowered SSA, load-address and live-out check.
- Local clang --target=aarch64-linux-gnu assembly of each candidate's
  Pass-2 and outer wrapper.

Slothy uses the repository venv and neoverse_n1_experimental proxy. Optional
LLVM execution selftest was not enabled; DFG selfcheck is not an execution test.
Generic log-parser timeout-configuration false positives are preserved and
explicitly reviewed. No aggregate cycle estimate is invented from overlapping
windows. Candidate scores remain investigate.

## Pi authorization history

Safety review rejected upload of the newly generated K1/K2 source bundle
without explicit authorization for this payload to pi@100.99.191.9.
The initial remote command was not executed and no workaround was attempted.
The user subsequently explicitly authorized the upload; the planned remote
commands then completed sequentially in the two named experiment directories.

Executed tests:

- 32 valid/tampered KEM cases, cross-version pk/ct/sk equality.
- Instrumented versus uninstrumented equivalence.
- 32 additional deterministic malformed/noncanonical ciphertext cases,
  comparing rejection status and output bytes.
- Guard and modular Forward checks, serialized equality with P3B37 and
  frozen SUPERCOP.
- Three paired repetitions, both orders, complete Forward and full KEM PMU.
- Linked-object hashes, sizes, disassembly and named-symbol audit.

Generic two-new-Forward polynomial multiplication is deliberately not run
as a candidate acceptance test: P3B39 proves that unrestricted pairing is
outside this contract. The original generic baseline remains available.
Full KEM differential correctness has now passed for both candidates.

## Files and commands

Persistent sources:

- campaign.py: reproducible lowering, gates, local Slothy orchestration,
  staging and explicitly invoked Pi runner.
- finish_local.py: offline assembly, proof linkage, log review and pending scores.

Generated under build/K1/ and build/K2/:

- kernel-contract.yml, baseline-contract.yml, candidate-contract.yml,
  instruction-dag.yml, iteration.yml, candidate-score.yml.
- build/candidate.sym.S: lowered solver input.
- build/scheduled.S: Slothy result.
- build/lowering.json, schedule-audit.json, local-assemble.json.
- build/slothy.log, solver-result.json, source-hashes.json.
- build/sync/raw/gt864_forward_six_bank.S: integrated candidate Pass-2.
- build/sync/raw/gt864_forward_poly_ntt.S: named KEM-only wrapper.
- build/sync/raw/gt864_poly_api.c: explicit wrapper binding.
- build/sync/t1/: unchanged P3B37 comparator.

From this experiment directory, preparation expects a fresh staging tree:

    python3 campaign.py --prepare
    /Users/chenpinhao/slothy_and_ra/.venv/bin/python campaign.py --optimize K1
    /Users/chenpinhao/slothy_and_ra/.venv/bin/python campaign.py --optimize K2
    python3 campaign.py --stage K1
    python3 campaign.py --stage K2
    python3 finish_local.py

Only after explicit upload authorization, run sequentially, not concurrently:

    python3 campaign.py --pi K1
    python3 campaign.py --pi K2

Remote targets are limited to
/home/pi/ntruplus-experiments/gt864-p3b41-k1 and
/home/pi/ntruplus-experiments/gt864-p3b41-k2.

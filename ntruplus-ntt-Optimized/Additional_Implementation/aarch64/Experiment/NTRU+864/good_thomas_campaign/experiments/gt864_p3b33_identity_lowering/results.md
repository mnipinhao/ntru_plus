# P3B33 — proof-selected identity bypass lowering

## Decision

**keep-experimental; assembly/correctness/object/Forward-PMU gate passed.**
P3B29-derived small-input Forward with P3B32's 12 selected identity reductions
bypassed is now the fastest measured candidate at this boundary. No production
change, Slothy execution, or full-KEM timing claim in this gate.

## Hypothesis and scope

- Action: optimize-arithmetic, not rescheduling or layout redesign.
- Observation: P3B29 measured ~4045 cycles; P3B32 closes the range chain after
  bypassing 12 all-one products per bank.
- Hypothesis: removing these reduction dependencies improves complete Forward
  even with conservative moves preserving the original allocation.
- Change: replace 11 Algorithm-10 triplets with moves, delete one in-place
  triplet; retain all constants/loads and every other scheduled instruction.
- Static expectation: 36 arithmetic instructions removed, 11 moves added,
  net 25 instructions per bank, 150 per complete Forward.
- Register pressure: no new registers or longer source lifetime; quotient
  temporaries disappear. No attempt to exploit freed registers yet.
- Correctness: P3B28 input `[-3,4]`, P3B32 range theorem; modular FR0/R0 identity
  unchanged, signed representatives may differ. General input is not supported.
- Falsifiers: failed differential/full multiplication, extra memory or spill,
  wrong PMU instruction delta, or no complete-Forward speed improvement.

## Register lowering

Stages are zero-based, lengths 2/4/8/16. Nodes are the bit-reversed scalar DIT
positions from P3B32, not coefficient addresses or register numbers.

| P3B32 node | Original MUL line | Replacement |
|---|---:|---|
| tail.stage0 | 192 | v22 ← v28 |
| main.stage0.node0 | 293 | v2 ← v27 |
| main.stage0.node2 | 298 | v2 ← v24 |
| main.stage0.node8 | 303 | v29 ← v22 |
| main.stage0.node4 | 306 | v0 ← v7 |
| main.stage0.node6 | 311 | v25 ← v9 |
| main.stage0.node10 | 316 | v10 ← v12 |
| main.stage0.node12 | 323 | v26 ← v21 |
| main.stage0.node14 | 328 | v26 ← v11 |
| main.stage1.node8 | 354 | v27 ← v3 |
| main.stage1.node12 | 362 | v6 ← v8 |
| main.stage2.node8 | 393 | v5 already holds input; no instruction |

Example: tail previously did `sqrdmulh v12,v28,v30; mul v22,v28,v22;
mls v22,v12,v14`. It now does only `mov v22.16b,v28.16b`. The subsequent
add/sub consumers still read v22 at their original positions. The copied
halfwords are interpreted as eight signed int16 values; copying does not
change layout or scale. It deliberately no longer changes representatives.

The generator tracks physical-register SSA definitions/uses and main-input
support sets. It identifies the approved right-hand subtree at each selected
multiply, checks quotient and multiply read the same input SSA version, checks
the quotient has only its MLS consumer, and checks the low product has only
that MLS consumer. The original paired scalar constant operands share their
table-register version. P3B31's source-hashed constant audit identifies the
all-one products. All 12 approved nodes must match exactly once.

## Object evidence

Linked with GCC 14.2.0, `-O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE
-fPIC -ffunction-sections -fdata-sections` and unchanged parent linking rules.

- Per helper: MUL/SQRDMULH/MLS each 90 → 78; 11 additional MOVs.
- Runtime helper instructions including RET: 553 → 528.
- Complete Forward PMU instructions: 4537.148 → 4387.148, exactly -150.
- Pass-2 object text including tables/wrapper: 4704 → 4608 bytes.
  The executed body shrinks 100 bytes; alignment before the following standalone
  wrapper adds one non-executed NOP after RET, giving net -96 object bytes.
- LDR/LDP, coefficient stores, TRN/TBL and branches unchanged; no Pass-2 stack
  access. The unchanged public wrapper retains its d8–d15 save/restore.
- Generated `t1` and `raw` bundles differ only in `gt864_forward_six_bank.S`.
  Here **t1 means P3B29 raw-top champion**, not the older general-input T1.

## Correctness

Before Forward timing, the new binary passed:

- full-KEM: 8 independent valid/tampered cases, instrumentation equivalence,
  cross-version public-key/ciphertext differences = 0;
- 32 complete `2F + D1 BaseMul + I` products vs int64 schoolbook;
- each Forward process: 256 guard-page cases, both allocation edges,
  disjoint and exact alias, modular comparison;
- each Forward process: 64 input cases, including all -3/all 4, serialized
  equality against the champion and frozen SUPERCOP.

P3B32 proof and P3B31 audit were rerun during staging. This is not exhaustive
KAT or a new cryptographic-security proof. P3B32's producer/inverse premises
continue to apply; assembly tests supplement rather than replace that proof.

## Pi 5 measurements

Host `pi@100.99.191.9`, Cortex-A76, CPU 3 affinity, GCC 14.2.0,
`throttled=0x0` before/after, final temperature 58.2°C.
Three paired repetitions, both variant orders, each process 61 samples of
400 calls after 32 warmups per sample. Report median of six process medians.
The common 1728-byte input reset is inside all Forward boundaries; no
reset subtraction. This is PMU component measurement, not SUPERCOP full-KEM.

| Variant | Cycles | Instructions | Branches |
|---|---:|---:|---:|
| P3B29 raw-top champion | 4045.350 | 4537.148 | 68.032 |
| P3B33 identity bypass | 3604.898 | 4387.148 | 68.032 |
| Frozen SUPERCOP | 3853.236 | 3736.137 | 57.030 |

P3B33 saves 440.453 cycles (10.89%) vs champion, and 248.338 cycles (6.44%)
vs this SUPERCOP Forward boundary. Candidate process medians span
3603.972–3608.650 cycles; every process wins against both comparisons.
This establishes a reduction-deletion benefit before Slothy, not an attribution
of every cycle to an individual instruction. Instructions remain higher than
SUPERCOP despite the lower measured cycles.

SUPERCOP source is the unchanged staged `sc` snapshot inherited through
P3B29/P3B26 from the local SUPERCOP 20260627 comparison campaign, SHAKE256
policy. **It is not verified to be latest upstream.** No new upstream fetch.

## Reproduction and provenance

Workspace HEAD at run: `cf8d3dba459bf9e5fc8e3e67dc84519b50f776f7` with existing
uncommitted campaign work; HEAD alone is not the experiment identity.
Parent Pass-2 SHA256:
`1cf9efd21be0774ee094f4683b7cf7f0db1670d7f1e48ab997098496d16a84d3`.
Candidate shared-object SHA256:
`f9f496f0d4f56e38629aecc6d187fe205bc7c7a4d4461758b4d7bd8c021bb0e2`.

From this directory:

```sh
python3 run.py --prepare
python3 run.py --run
python3 run.py --repeat --summarize
```

Prepare refuses to overwrite an existing staged bundle. Generated source,
source-hashes.json, lowering.json, dry-run/build logs, disassemblies,
correctness logs, six PMU logs and summary.json are in gitignored `build/`.
Remote scope: `/home/pi/ntruplus-experiments/gt864-p3b33-identity-lowering`.
The driver only uploads that named source bundle, not the whole repository.

Next gate: freeze this as the unscheduled experimental comparator; evaluate
the new DAG with the canonical Slothy workflow, or separately measure its
full-KEM cycle impact. Do not mix either with ToBytes/FromBytes changes or
silently promote to production.

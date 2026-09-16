# P3B36 — combined copy/load cleanup and twist0 deletion

## Decision

**Keep as the fastest measured experimental Forward candidate.** User explicitly
authorized combining the optimizations; no attempt is made to attribute cycles
to each constituent change. P3B33 fixed baseline, P3B34 source and production
remain unchanged. No Slothy or full-KEM timing in this gate.

| Same-run complete Forward | Cycles | Instructions | Branches |
|---|---:|---:|---:|
| P3B34 comparator | 3574.415 | 4375.148 | 68.032 |
| P3B36 combined candidate | 3524.834 | 4303.148 | 68.032 |
| Frozen SUPERCOP snapshot | 3853.254 | 3736.137 | 57.030 |

Difference of aggregate medians: -49.582 cycles (-1.39%) vs P3B34;
-328.421 cycles (-8.52%) vs this SUPERCOP Forward boundary. Each of six paired
process comparisons improves; paired savings range 49.465–52.777 cycles.
All timings include the same 1728-byte input reset; no reset subtraction.

## Combined hypothesis

Observation: P3B35 identified nine individually coalescible moves, three dead
constant loads and a newly proved input-twist identity bypass. The user wants
the fastest combined result, not isolated attribution. Hypothesis: jointly
remove unnecessary copies, table reads and reduction work while preserving
all coefficient addresses, R0 representation and original instruction order.
Expected effects: fewer instructions/table reads, no extra vector registers
or coefficient pass. Failure of structural equivalence, correctness, object
delta or paired complete-Forward improvement rejects the candidate.

## Actual lowering

The generator starts from the frozen P3B34 `gt864_forward_six_bank.S` and first
applies P3B35's proved `main.twist0` change:

```asm
// Old t=0 input multiplication by one:
sqrdmulh v8.8h, v31.8h, v12.h[1]
mul      v3.8h, v31.8h, v12.h[0]
mls      v3.8h, v8.8h, v14.8h
// New:
mov      v3.16b, v31.16b
```

This move must remain: v31 is overwritten before all later consumers of v3.
The generator then recomputes register-version liveness after **each** copy
substitution. Nine old copies can jointly be eliminated, with their consumers
reading the original source instead. The three previously blocked copies
remain. There are four remaining vector MOVs, including the new twist0 move.

| Removed copy, original P3B34 line | Destination ← source | Consumer lines rewritten |
|---:|---|---|
| 192 | v22 ← v28 | 194,195 |
| 293 | v2 ← v27 | 295,296 |
| 303 | v29 ← v22 | 308,309 |
| 306 | v0 ← v7 | 313,314 |
| 311 | v25 ← v9 | 317,318 |
| 316 | v10 ← v12 | 320,321 |
| 342 | v28 ← v29 | 346,347 |
| 354 | v27 ← v3 | 356,357 |
| 362 | v6 ← v8 | 369,370 |

Dead constant loads at lines 187/188 become one `add x2,x2,#32`; line 291
becomes `add x2,x2,#16`. All other table reads retain their original addresses.
No table repacking or increment folding into another live load was attempted.
This removes three q-vector reads per bank without shifting subsequent zetas.

Net per bank relative to P3B34:

| Opcode | Delta |
|---|---:|
| MUL | -1 |
| SQRDMULH | -1 |
| MLS | -1 |
| MOV | -8 |
| LDR | -3 |
| ADD, GPR pointer increments | +2 |
| Total | -12 |

Six banks: **-72 executed instructions**, **-18 constant-vector loads**.
The latter is 288 bytes of load-instruction traffic, not a claim of 288 fewer
DRAM bytes. Coefficient loads/stores, routing, arithmetic add/sub, branches
and the d8–d15 public-wrapper save/restore remain unchanged.

## Proof and equivalence gates

P3B35 reachable-set proof was rerun before staging. Input remains [-3,4],
not general int16. The changed reduction schedule has Forward bound 26731,
M5C maximum accumulator 2143639083, D1 input upper bound 2143665212,
D1 output bound 3023 and M5E maximum intermediate 17220. P3B34's existing
full-int16 serializer-normalization proof remains applicable.

After this separately proved modular bypass, the generator constructs an exact
structural operation-DAG fingerprint for all 18 output vector registers plus
the preserved v13/v14/v15 registers. MOV is identity; other instructions retain
their opcode, lane/arrangement and input-register versions. Every copy rewrite
must preserve this fingerprint. This is not a solver proof of the modular
bypass itself: P3B35 owns that obligation.

Loads are identified by input/table base and byte offset, not destination
register names. The final copy/load cleanup must preserve the same output
fingerprint and x0/x1/x2/x3 pointer states. Thus a dead post-increment load
cannot simply disappear without compensating its pointer effect.

## Object and correctness

The Pi object's opcode delta matches the generated ledger exactly; no extra
NOP delta. Pass-2 object text including tables/wrapper: 4592 → 4544 bytes.
No Pass-2 SP references/spill and no new branches. PMU confirms exactly 72
fewer instructions per complete Forward.

Before timing, full-KEM correctness passed 8 independent valid/tampered cases,
instrumentation equivalence, and cross-version pk/ct differences = 0.
Complete 2F+D1+I passed 32 int64-schoolbook comparisons. Each of six Forward
processes passed 256 guard-page cases (both edges, disjoint/exact alias), and
64 serialized comparisons against both P3B34 and frozen SUPERCOP.
These tests are not an exhaustive KAT or cryptographic security proof.

## Environment and reproducibility

Pi 5 Cortex-A76 at `pi@100.99.191.9`, CPU 3 affinity, GCC 14.2.0;
same parent Makefile, -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE
-fPIC -ffunction-sections -fdata-sections. Three repetitions, both variant
orders, 61 samples/process, 400 calls/sample after 32 warmups. Report median
of six process medians. throttled=0x0, final temperature 62°C.

The comparator binary SHA256 exactly matches P3B34:
`bbda0db6b31623bd1a3e1b36ad42fd0377c06ce9ee1b614707fd9e01dcea13a2`.
Candidate shared object SHA256:
`4f5dfdbdf7bf160278ba8cb855f3feca85d6b3a3af39468383659c83baf8e6c9`.
SUPERCOP is the unchanged 20260627 campaign SHAKE256 snapshot, **not verified
as latest upstream**. Artifact names t1/raw mean P3B34/P3B36 in this run.

```sh
python3 run.py --prepare
python3 run.py --run --repeat --summarize
```

Prepare refuses existing staging. `run.py` preserves parent sources and reuses
the established P3B33 test driver with a new isolated remote directory:
`/home/pi/ntruplus-experiments/gt864-p3b36-combined`.

Generated assembly is `build/sync/raw/gt864_forward_six_bank.S`; the unchanged
comparator is `build/sync/t1/gt864_forward_six_bank.S`. `build/lowering.json`
records every rewrite, `source-hashes.json` identifies all staged files,
`range-rerun.log` records the proof, and build/correctness logs, disassemblies,
six Forward PMU logs and `measurement.json` retain execution evidence.
All generated artifacts are gitignored. No production edit or commit.

Next: use this combined candidate for full-KEM performance confirmation or a
separate canonical Slothy scheduling gate. The two reductions rejected by
P3B35's reachable BaseMul extremes remain present; speed goals do not remove
their accumulator-safety obligation.

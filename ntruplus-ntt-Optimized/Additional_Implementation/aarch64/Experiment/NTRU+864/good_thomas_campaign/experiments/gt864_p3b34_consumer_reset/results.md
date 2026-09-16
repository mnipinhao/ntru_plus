# P3B34 — consumer-aware reset audit, fixed P3B33 baseline

## Outcome

**keep-experimental: one additional identity multiplication per bank passes
proof, lowering, correctness and same-boundary Pi 5 measurement.** P3B33 is
unchanged. No production change, scale/ABI change, Slothy or full-KEM timing.

| Complete Forward, common reset included | Cycles | Instructions | Branches |
|---|---:|---:|---:|
| P3B33, rebuilt frozen comparator | 3605.811 | 4387.148 | 68.032 |
| P3B34, one more bypass per bank | 3576.382 | 4375.148 | 68.032 |
| Frozen SUPERCOP comparison snapshot | 3853.233 | 3736.137 | 57.030 |

Difference of aggregate medians: -29.429 cycles (-0.82%) vs P3B33;
-276.851 cycles (-7.18%) vs this SUPERCOP Forward boundary. All six process
comparisons improve; paired savings span 25.658–31.495 cycles. Do not compare
against a historical P3B33 timing from a different run.

## What the supplied research direction changes

The useful question is whether the next consumer remains legal, not whether
every intermediate is reduced. However, the supplied text contains no title,
authors, URL or full theorem. This experiment does not certify its paper
attributions or infer unprovided theorem preconditions. It exhaustively checks
our actual signed instructions/constants instead.

P3B33 does not contain the text's illustrative "40 reductions" or a generic
21333 envelope. Its Pass-2 helper has 78 Algorithm-10 products. The raw top
already has no SQRDMULH/MLS reductions, only its required plain fixed products.
No SHSUB or Montgomery scale normalization is present in the Forward helper.
Therefore doubled Montgomery is a separate representation research campaign,
not a local instruction deletion for this Forward.

## Reduction ledger

Per P3B33 helper, repeated for six banks:

| Class | Count | Reason / treatment |
|---|---:|---|
| all-one fixed multiplication | 5 | RANGE / CONSUMER candidates; necessity not presumed |
| mixed identity/nonidentity lanes | 4 | TWIDDLE + RANGE; cannot delete whole vector product |
| no identity lanes | 69 | TWIDDLE + RANGE; deleting multiplication changes algebra |

The 156 records in `build/proof.json` cover both top constant sets (78 each),
shared by three components. Source line numbers refer to the source-hashed
P3B31/P3B29 parent, with P3B33's 12 deletions filtered out. Tags are functional
roles, not claims that every RANGE-tagged reset is indispensable.

No Forward canonicalization requirement was found. Canonicalization lives at
the serialization consumer. No REPRESENTATION/SCALE normalization is being
removed here; every edge remains R0. The model does not mistakenly count
the low MUL's modular wrap as signed mathematical overflow.

## Machine theorems and state model

Scope: `explore/design`, then an isolated arithmetic implementation under the
proved contract. Ring Z_3457[x]/(x^864-x^432+1), 864 signed int16 coefficients,
input [-3,4], raw-top intervals [-2891,2170] / [-2172,2896]. Inputs are secret;
all addresses, table selections and control flow remain public/fixed.

For 276 fixed `(b,bhat)` pairs in the model's constant set (a superset of
retained Forward constants), exhaust all 65536 signed halfwords:

    t = floor((a*bhat + 16384)/32768)
    r = signed_low16(a*b - t*3457)

Check quotient does not saturate, the mathematical residual fits int16,
machine low-half semantics agree, and r ≡ ab mod 3457. The maximum observed
absolute residual across this exhaustive domain is **3436 < 3457**. This is
bounded, not necessarily centered/canonical. The search itself still uses
exact per-input-interval products, not a blanket 3436 or 1.5q reset.

Edge state includes interval, R0 scale, i16 width, canonicality classification
and an affine expression over named bounded atoms. Add/sub retain shared
producer coefficients, so (x+y)+(x-y)=2x. A fixed multiplication creates a
fresh bounded atom, relaxing its nonlinear relationship to its input. Separate
NTT9 rows are explicitly cloned to independent coefficient producers; equal
intervals do not mean equal variables. Unit assertions check cancellation and
row independence. This is sound **affine-with-reset overapproximation**, not
complete nonlinear correlation reasoning or an exact reachable-set proof.

`baseline-edges.json` and `mask-2.json` retain node expressions, reset input
expressions, atom domains and all 288 output-leaf intervals.

## Why one previously unproved candidate now passes

P3B32 reused a D1 domain theorem bounded by about ±1.961e9. Exceeding that
domain meant "not proved", not "D1 is invalid". We now check D1's actual
reciprocal 621199 across the full signed-int32 domain using every quotient
transition boundary. Its residual is bounded by **3023**. SQRDMULH cannot
saturate with this reciprocal. MLS uses low-half modular arithmetic; only
the final residual needs to fit before the non-saturating narrow.

For serialization, the unchanged `byte_boundary.c` computes b=1 Barrett then
adds q for a negative result. Exhausting all 65536 halfwords proves this exact
implementation returns `a % 3457` in [0,3456]. Hence the historical leaf
envelope ±25569 is not a hard ToBytes precondition. No extra normalization
instruction is added.

| Candidate chain | Proven enclosure |
|---|---:|
| Forward maximum intermediate | 25740 |
| M5C maximum absolute accumulator | 1987642800 |
| D1 BaseMul / BaseMulAdd input union | [-1985815236,1987668540] |
| D1 output, conservative full-int32 theorem | [-3023,3023] |
| M5E maximum halfword intermediate | 17220 |
| Existing serialization normalization output | [0,3456] |

The existing variable-product/Montgomery cross reductions stay intact. The
M5C accumulator gates are still enforced before D1. M5E uses its previously
proved universal fixed-product bound 3444 and a newly propagated input bound;
its constant exhaustion is not repeated here. No claim that fixed-twiddle
Barrett permits deleting variable-variable BaseMul reductions.

The new success comes from strengthening the consumer theorems, not replacing
an old 1.5q model (P3B32 already used exact multiplication bounds). Affine
tracking is infrastructure for further reasoning; this result does not
attribute the saving to it alone.

## Search and exact assembly change

Keep P3B33's 12 bypasses fixed. Enumerate all 32 subsets of the remaining five
all-one groups: input twist0, length-4 nodes 0/4, length-8 node 0, length-16
node 0. Only baseline and **main.stage1.node4** pass this model. Other masks
fail an int16 or M5C-int32 enclosure. These are not concrete overflow witnesses
and do not prove global minimality; alternate DAGs or stronger correlations
may recover more.

Stage 1 means the length-4 DIT stage. At node 4, j=0, v29 holds the right
subtree (t6/t14) independently in the eight main `s=0..7` lanes.

    before: sqrdmulh v9.8h, v29.8h, v11.h[1]
            mul      v28.8h, v29.8h, v11.h[0]
            mls      v28.8h, v9.8h, v14.8h
    after:  mov      v28.16b, v29.16b

The actual scheduled instructions have intervening unrelated work; only these
three sites are replaced, not moved. The driver checks unique matches, source
hash, and no intervening v9 quotient use or v29 overwrite. Downstream add/sub
still consume v28 in their original locations. Source lifetime is not extended,
no register is added, and the representative changes only modulo q.

Object audit: MUL/SQRDMULH/MLS each -1, MOV +1 per helper; net -2 × 6 = -12
runtime instructions/Forward, confirmed by PMU. One alignment NOP also
disappears; object text 4608 → 4592 bytes. No Pass-2 SP access/spill; no changed
coefficient or table load/store, routing, wrapper, ABI, or branch path.

## Validation and reproducibility

- Full-KEM: 8 independent valid/tampered cases, instrumentation equivalence,
  cross-version pk/ct differences = 0.
- 32 full 2F+D1+I products vs int64 schoolbook.
- Each of six Forward processes: 256 guard-page edge/alias cases and 64
  serialized comparisons against both frozen P3B33 and SUPERCOP.
- Pi 5 Cortex-A76, CPU3, GCC 14.2.0, unchanged P3B33 Makefile and wrappers,
  -O3 -march=armv8-a+simd. Three repetitions/both orders; 61 samples/process,
  400 calls/sample with 32 warmups. Median of process medians.
- Common 1728-byte reset included; no reset subtraction. throttled=0x0,
  final temperature 62°C. No full-KEM performance measurement.

The rebuilt comparator shared object SHA256 exactly matches P3B33:
`f9f496f0d4f56e38629aecc6d187fe205bc7c7a4d4461758b4d7bd8c021bb0e2`.
Candidate: `bbda0db6b31623bd1a3e1b36ad42fd0377c06ce9ee1b614707fd9e01dcea13a2`.
SUPERCOP is the unchanged 20260627 campaign SHAKE256 snapshot; latest upstream
remains unverified. Artifact names `t1` / `raw` mean P3B33 / P3B34 in this run.

From this directory:

```sh
python3 prove.py
python3 run.py --prepare
python3 run.py --run --repeat --summarize
```

Prepare refuses existing staging. Generated files, source hashes, proofs,
edge ledger, dry-run/build logs, disassemblies and raw PMU stay in ignored
`build/`. Remote directory is the isolated
`/home/pi/ntruplus-experiments/gt864-p3b34-consumer-reset`.

Next arithmetic gate should target the remaining **four** all-one groups with
stronger reachable-set/correlation reasoning, first distinguishing the
M5C-int32 gate from Forward-int16 gates. Do not promise they are removable.
Alternatively schedule this proved DAG as a separate Slothy experiment. Keep
doubled-Montgomery work separate because it changes representation and has no
direct SHSUB deletion target in the present Forward.

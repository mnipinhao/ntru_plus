# P7-C0 — Inverse arithmetic and range re-closure

Date: 2026-09-12. Arithmetic baseline: production P7-B1, commit `ecea7bbc`.
Decision: **algebra/range gate passes; keep the new DAG experimental**.
Production assembly is unchanged. No new timing or physical candidate is claimed.

## Findings

The old `inverse_range.py` already exhausts all signed-int16 inputs for its
266 constant pairs and establishes `<3457` (maximum 3444), rather than using
the obsolete `3q/2` bound. Updating that coarse theorem alone deletes nothing.
The useful improvement in this gate is propagating each actual interval through
each fixed constant, including all 32 `(top,column)` terminal-table contexts.

More importantly, production inverse NTT9 still implements each B3 with **four**
Algorithm-10 multiplications. A one-product B3 keeps the same ordered modular
outputs and saves three mulmods, while adding one add/sub instruction.

| Quantity | Previous published bound | Re-closed P7-B1 | One-product B3, mask 0 |
|---|---:|---:|---:|
| BaseMul R^-1 input absolute bound | 2497 | 2497 | 2497 |
| I9 arithmetic peak | 22473 | 22473 | 22473 |
| I9 terminal output | 3456 | 2311 | 2617 |
| I16 arithmetic peak | 30939 | 19545 | 21397 |
| Raw natural R0 output | 6912 | 4485 | 4577 |
| Centered natural R0 output | 1728 | 1728 | 1728 |

These are sound interval upper bounds, not claims that every bound is attainable.
The arithmetic uses exact signed scalar images for fixed multiplications and
ordinary interval addition/subtraction; it does not assume correlations between
separate reduced values. MUL's intentional low-half wrap is handled inside the
matched Algorithm-10 triple, not misclassified as an add/sub overflow.

## Exact one-product B3

For `q=3457`, let `r=722`, `r2=-723`. Machine checks establish
`r^3=1`, `r^2=r2`, and `r+r2=-1` modulo q. Current B3 outputs are:

```text
y0 = a + b + c
y1 = a + mulmod(b, 722) + mulmod(c, -723)
y2 = a + mulmod(b,-723) + mulmod(c,  722)
```

The candidate is:

```text
d  = b - c
t  = mulmod(d, 722)
y0 = (a + b) + c
y1 = (a - c) + t
y2 = (a - b) - t
```

Every intermediate add/sub is checked, including the enlarged `b-c` input.
Representatives can differ by multiples of q. The proof carries the new ranges
through the unchanged terminal tables and actual main/tail I16 assembly; it
does not require intermediate bit identity. Centered complete-Inverse model
outputs agree exactly.

The six B3 instances are first-level `(0,3,6)`, `(1,4,7)`, `(8,2,5)` and
second-level `(0,1,8)`, `(3,4,2)`, `(6,7,5)`. The existing four eta products and
nine terminal products remain. The logical terminal order is
`[0,3,7,1,4,5,8,2,6]`; the source arithmetic checker verifies this rather than
assuming natural register ordering.

| Arithmetic ledger, per NTT9 block | P7-B1 | Candidate |
|---|---:|---:|
| Six B3 mulmods | 24 | 6 |
| Eta mulmods | 4 | 4 |
| Terminal mulmods | 9 | 9 |
| Total mulmods | 37 | 19 |
| B3 add/sub instructions | 36 | 42 |
| Total arithmetic instructions | 147 | 99 |

This is **-48 arithmetic instructions/block**, or **-576 per complete Inverse**.
It removes 216 Algorithm-10 invocations across 12 blocks (648 multiply/reduction
instructions), but adds 72 add/sub instructions. Constant materialization, moves,
allocation, scheduling and exact final body size remain to be measured. The
existing 284-instruction body must not be confused with the 147-instruction
arithmetic subtotal.

The model also checks all `2^6=64` choices between two equivalent one-product
orientations. The alternate uses `t=mulmod(b-c,-723)`,
`y1=(a-b)-t`, `y2=(a-c)+t`. All 64 preserve every output linear map and close
the complete chain. Thirty-two masks bound I9/I16/raw by `2596/21255/4572`;
the other 32 give `2617/21397/4577`. Mask 8 is the first tighter candidate,
using the alternate only in the second-level first B3. Mask 0 remains the
simple first candidate because it requires only one root/magic constant pair
inside B3. The tighter mixed orientation has no established cycle advantage.
This is a bounded B3-orientation search, not an exhaustive search of every
possible CT/GS NTT9 topology.

## Reduction decisions

| Region | Decision | Reason |
|---|---|---|
| I9 B3 weighted products | Rewrite four products to one | Exact `r+r2=-1` identity and consumer range closure |
| I9 four eta products | Retain | Nonidentity roots are part of the current linear map |
| I9 nine terminal products | Retain | Inverse scaling/twist and I16 representative bounds |
| I16 fourteen already omitted identity multiplications | Keep omitted | Re-closed through actual source |
| I16 final identity SQRDMULH+MLS | Retain | Explicit overflow witness under the closed input contract |
| I16 nonidentity products and terminal scale | Retain | DFT weights, inverse twist and R^-1→R0 correction |
| Top recombination products | Retain | Required two-branch CRT map |
| center864 | Retain in this gate | Required centered output; raw-to-ternary remains P8 |

The last identity reset cannot be removed merely because the new I16 peak is
smaller. Give **every column** of top 0 the valid nine-input box vector:

```text
[2497,2497,2497,2497,2497,2497,2497,2497,2489]
```

Both B3 DAGs produce `s=0 = 2112` after the terminal `(-384,-3640)` pair.
Without the remaining identity reset, the final NTT16 sum is
`16*2112 = 33792 > 32767`. This vector lies within the established BaseMul
output box. We do not assert that this entire joint vector is reachable from
actual KEM c/f inputs. Deleting the reset would require a stronger producer
relationship proof, beyond the current box contract.

## Binding to production and validation

`audit.py` reads the active production files and emits their SHA-256 identities.
The package Makefile and `gt864_native.c` select these native cores for the
first Decaps product/Inverse pair. The source-selection dry run is:

```sh
make -Bn -C ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864 libgt864.so
```

The checker performs:

- All 266 current fixed `(b,h)` pairs over all 65,536 signed inputs; validates
  `h=round(b*32768/q)` and strict output `<q`.
- Current P7-B1 physical I9 arithmetic trace for 32 `(top,column)` contexts.
  It handles Q/V aliases, destructive read-before-write and interleaved
  MUL/SQRDMULH/MLS; all 288 terminal linear maps and interval endpoints agree
  with the independent B3 topology model.
- Complete physical main/tail I16 source tracing for both row-halves and tail,
  including EXT, the lone identity reduction, scalar extraction and every
  natural-output STRH address. Every output linear map agrees with independent
  inverse-DFT coefficients and the two-branch CRT map, under both input bounds.
- 288 leaf-root identities against the Montgomery-encoded BaseMul table;
  41,472 inverse coefficient weights; inverse9 geometric twist, inverse16
  terminal scale, R correction, and alpha/beta CRT constants.
- All 64 one-product B3 orientations, with complete I9→I16→top interval chains.
- 512 corner and 1,024 random I9 model cases; 71 complete 864-coefficient
  Inverse model cases; exhaustive 13,825-value current centering domain.

No candidate physical assembly or KAT was run: this gate changes the machine
model and documentation only. Existing I9 routing/public-wrapper memory and ABI
validation remains inherited from P7/P7-B1. This is not binary-level formal
verification, and the Isabelle paper's arithmetic theorem does not prove the
whole transform automatically.

Reproduce the compact checked result:

```sh
python3 experiments/gt864-native-asm/inverse-p7c0-range/audit.py
```

For every arithmetic node, including source line/lane and multiplication input
and output intervals, add `--detail`. Keep that generated ~3 MB trace under a
temporary/build directory; only the compact results are tracked.

## Next gate and retained work

**P7-C1: one-product inverse NTT9 physical implementation.** Author its symbolic
DAG, preserve existing terminal tables and P8 stores, allocate without spill,
then schedule locally with `/Users/chenpinhao/slothy`. Compare final centered
Inverse outputs, alias/cleanup/KAT and malformed-ciphertext behavior. Only after
correctness, measure complete Inverse and Decaps on Pi 5 against frozen P7-B1.
Keep the last I16 identity reset. Gate success requires a smaller final DAG and
real same-boundary cycle improvement; the arithmetic saving alone is not timing.

P8 raw-Inverse-to-ternary follows the core attempt. P9 ToBytes routing and P10
Keygen BaseInv remain queued. Selected Official remains
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`, with upstream-latest
status unverified; this turn adds no Official benchmark.

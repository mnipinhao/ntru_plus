# U01 Stage12 -> Stage345 Block0 Contract

Date: 2026-07-09

## Active Artifact

Source-order scaffold:

```text
experiments/forward_ntt_phase123_u01/phase123_stage12_block0_first_allrows.sym.s
```

Callable candidate:

```text
asm/gt/experiment/u01_block_first_candidate.S
```

Generated table/vector artifacts:

```text
asm/gt/experiment/u01_block_first_tables.inc
experiments/forward_ntt_phase123_u01/u01_block_first_vectors.inc
experiments/forward_ntt_phase123_u01/generate_u01_block_first_artifacts.py
```

Verifier:

```text
experiments/forward_ntt_phase123_u01/verify_stage12_block0_first_symbolic.py
```

Layout map:

```text
experiments/forward_ntt_phase123_u01/u01_layout_map.json
```

## ABI For The First Callable Candidate

The first callable wrapper exposes a benchmark-only ABI:

```c
void u01_block_first_candidate(int16_t scratch[768],
                               const int16_t input[768]);
```

The future production same-coverage oracle should expose:

```c
void u01_block_first_production_oracle(int16_t scratch[768],
                                       const int16_t input[768]);
```

The caller owns `scratch`.  The candidate writes post-Stage12 row-major
scratch:

```text
row0: scratch[0..255]
row1: scratch[256..511]
row2: scratch[512..767]
```

Each row has 32 Q vectors:

```text
Qk = 8 int16 coefficients
byte offset = row_base + 16*k
```

## Internal Register Contract

The current symbolic region assumes:

```text
x1  = input base
x3  = Phase123 twist table base
x12 = NTT32 stage12 twiddle vector base
x13 = row-major scratch base
v0  = q/constants
```

The callable wrapper must set these explicitly before entering the generated
region.  It must not rely on ambient state from `poly_ntt`.

## Scratch Contract

The first prototype keeps scratch.  It is intentionally not all-row
no-scratch.

Before Stage12:

```text
x13 row-major scratch contains raw Q0..Q31 for rows0/1/2
```

After Stage12:

```text
x13 row-major scratch contains post-Stage12 Q0..Q31 for rows0/1/2
```

The block0-ready subset is:

```text
row0 Q0..Q7: byte offsets    0..112
row1 Q0..Q7: byte offsets  512..624
row2 Q0..Q7: byte offsets 1024..1136
```

This subset is exactly Stage345 block0 input.

## Stage12 Output Mapping

For each stripe `s`:

```text
inputs: Q[s], Q[s+8], Q[s+16], Q[s+24]
out0 -> Q[s]     -> Stage345 block0
out1 -> Q[s+8]   -> Stage345 block1
out2 -> Q[s+16]  -> Stage345 block2
out3 -> Q[s+24]  -> Stage345 block3
```

Therefore Stage345 block0 is:

```text
out0 from stripe0..7
```

This is the central block-first rule.

## Correctness Boundary

The first C test should compare only:

```text
block0 Q0..Q7 for rows0/1/2
```

against a production same-coverage partial oracle.  The current C test uses
generated production-oracle vectors; the callable production oracle remains the
next implementation step.  It should not compare full `poly_ntt` output until
Stage345 block0 and the remaining blocks are connected.

Current Python oracle compares all post-Stage12 Q0..Q31 values and already
passes:

```sh
python3 experiments/forward_ntt_phase123_u01/verify_stage12_block0_first_symbolic.py --seeds 64
```

Expected:

```text
phase123_stage12_block0_first_ok seeds=64 rows=3 outputs=96 block0_outputs=24 later_outputs=72
```

Current Pi 5 callable candidate gates:

```text
make test_u01_block_first
  u01_block_first_block0_mismatches=0
  mismatches = 0

make test_u01_block_first_oracle
  u01_block_first_block0_mismatches=0
  mismatches = 0

make test_u01v2_block_first_oracle
  u01_block_first_block0_mismatches=0
  mismatches = 0
```

## PMU Boundary

PMU should compare two functions with the same observable output:

```text
production source-order same-coverage partial oracle
U01 block-first candidate
```

Metrics:

```text
cycles per call
instructions per call
CPI
text size
static instruction count inside the callable region
register pressure notes
```

Do not compare this partial prototype directly against full `poly_ntt`; that
would measure a different boundary.

Current Pi 5 PMU result, core 3, `NTESTS=61`, `NITERATIONS=10000`:

```text
production_source_order_same_coverage:
  cycles median       1454
  instructions median 1830
  CPI                 0.794536

u01_block_first_candidate:
  cycles median       1568
  instructions median 1843
  CPI                 0.850787
  delta vs oracle     +114 cycles
```

The callable oracle is source-order and semantic.  It is not the optimized
production `poly_ntt` schedule.  Still, this is enough to reject the current
block-first scaffold as-is: it fails to beat even the same-boundary source-order
oracle.

U01v2 keeps the production Phase123 shared-prefix and only reorders
iterations into even/odd block-first groups:

```text
iter0,2,4,6 -> Stage12 stripes0..3
iter1,3,5,7 -> Stage12 stripes4..7
```

Current Pi 5 PMU result, core 3, `NTESTS=61`, `NITERATIONS=20000`:

```text
production_source_order_same_coverage:
  cycles median       1454
  instructions median 1831

u01v2_shared_prefix_evenodd:
  cycles median       1456
  instructions median 1872
  delta vs oracle     +2 cycles
```

This makes U01v2 a correct structural baseline, not a speedup.  It proves that
the large U01v1 regression came from breaking shared-prefix reuse, but pure
even/odd block-first ordering still does not pay by itself.

## Out0 Store Diagnostic

To measure whether the Stage12->Stage345 boundary is worth touching, there is
a diagnostic variant that omits only the Stage12 block0 `out0` stores:

```text
3 rows * 8 stripes = 24 q stores removed
```

It is not a correctness candidate.  It intentionally does not write Q0..Q7 to
scratch.

Pi 5 PMU, core 3, `NTESTS=61`, `NITERATIONS=20000`, second run:

```text
production_source_order_same_coverage:
  cycles median       1466
  instructions median 1833

u01v2_shared_prefix_evenodd:
  cycles median       1458
  instructions median 1874
  delta vs oracle     -8 cycles

u01v2_no_out0_store_diag:
  cycles median       1441
  instructions median 1850
  delta vs oracle     -25 cycles
```

This says the store side of the boundary can matter by roughly 17 cycles
relative to U01v2 in the same binary.  The next real candidate must preserve
correctness by feeding those omitted Q0..Q7 values directly into Stage345
block0 instead of dropping them.

## Register Pressure Notes

The no-scratch version is deliberately deferred.

All-row U01 direct no-scratch would need to keep at least:

```text
3 rows * 4 iterations * 2 slots = 24 raw Q vectors
```

live before Stage12, before counting twist values and Stage12 temporaries.
The block-first scratch prototype is the smaller gate that decides whether
this route is worth a deeper Slothy attempt.

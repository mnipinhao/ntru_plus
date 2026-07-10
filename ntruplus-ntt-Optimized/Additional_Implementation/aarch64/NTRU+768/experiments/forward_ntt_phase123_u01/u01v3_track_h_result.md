# U01v3 Track H Result

Status: complete. Production default is unchanged. No correctness candidate
was emitted.

## Starting Point

G1 remains the trusted F0123 baseline:

```text
shape: E3/F012 live handoff + block3 from Stage12 scratch
correctness: pass
ABI: pass
block3 q loads: 24
vs production same coverage: -13 cycles, -92 instructions
```

Track H asked whether changing Phase123/Stage12 producer order could remove
those 24 block3 loads without raw reloads, a prefix memory boundary, or the
E4 live-all register failure.

## H0 Load-Elision Upper Bound

H0 is generated as an independent diagnostic symbol. It mechanically removes
the eight Stage345 block3 input loads in each of three rows while leaving
Stage345 arithmetic and scatter unchanged.

```text
symbol: u01v3_f0123_h0_block3_load_elision
removed instructions: 24 q loads
G1 static executable instructions: 3727
H0 static executable instructions: 3703
local AArch64 assembly: pass
correctness: intentionally skipped
Pi5 PMU: complete
```

H0 uses stale register values as a stand-in for a hypothetical free upstream
handoff. It is an optimistic whole-path timing bound, not a candidate that can
be promoted.

Pi5 core 3, `NTESTS=61`, `NITERATIONS=20000`, `NWARMUP=300`; two
consecutive runs gave identical medians:

| ID | Cycles | Instructions | CPI | Delta vs G1 | Text size | addr mod32/mod64 |
|---|---:|---:|---:|---:|---:|---:|
| P | 2724 | 3836 | 0.7101 | +28 | 15272 | 0 / 32 |
| V | 2727 | 3876 | 0.7036 | +31 | 15432 | 0 / 0 |
| G1 | 2696 | 3744 | 0.7201 | 0 | 14904 | 0 / 0 |
| H0 | 2694 | 3720 | 0.7242 | -2 | 14808 | 16 / 48 |

H0 removes exactly 24 retired instructions but saves only two cycles. This is
the attachment's `0-5 cycles` low-headroom case: the block3 q loads are mostly
not on the whole-path critical path.

## Semantic Lifetime

For every row and Stage12 stripe:

```text
t0 = reduce(B + D)
t1 = twisted_reduce(B - D)
t2 = A + C
t3 = A - C

Q0  = t2 + t0
Q8  = t2 - t0
Q16 = t3 + t1
Q24 = t3 - t1
```

The register holding raw D is reused for `t3=A-C`, but only after D's last
current semantic use. The longer-lived raw D scratch slot is overwritten later
by Q24. Therefore the current implementation does not contain a free early
overwrite that H1 can simply move.

Given Q0..Q23, Q24..Q31 retain eight independent vector dimensions per row.
The smallest exact state is one vector per stripe: eight vectors per row and
24 vectors over all rows. G1 already stores that final basis directly.

## Candidate Gates

| Track | Best shape | Result | Main blocker |
|---|---|---|---|
| H1 | delayed out3 overwrite | reject | 24 F012 + 8 basis values = 32 data vectors; only 31 available |
| H2a | strict block-major | reject | +483 instructions and 288 raw reloads |
| H2b | pair-major 01/23 | reject | +57 instructions and 96 raw reloads |
| H2c | E3/F012 + delayed out3 | reject | same +201-instruction shape as G3a |
| H3 | minimal reconstruction basis | reject | rank requires 8 vectors; 1-4 vectors cannot reconstruct block3 |

H1/H2/H3 all fail before the physical-candidate gate. No Track H ASM,
correctness test, ABI sentinel, full `poly_ntt` differential, or PMU candidate
was generated from those tracks.

## Decision

```text
current F0123 best: G1
Track H correctness candidate: none
H0: measured load-cost diagnostic, -2 cycles vs G1
production default: unchanged
```

H0 shows only two cycles of optimistic headroom, and none of the current
H1/H2/H3 forms passes the stated hard gates. Reopening this line requires a
materially different Phase123 representation or transform decomposition, not
another register rename or local producer reorder.

Evidence:

- `u01v3_track_h_semantic_ir.json`
- `u01v3_track_h_overwrite_map.json`
- `u01v3_track_h_h1_candidates.json`
- `u01v3_track_h_h2_candidates.json`
- `u01v3_track_h_h3_candidates.json`
- `u01v3_track_h_candidate_registry.json`

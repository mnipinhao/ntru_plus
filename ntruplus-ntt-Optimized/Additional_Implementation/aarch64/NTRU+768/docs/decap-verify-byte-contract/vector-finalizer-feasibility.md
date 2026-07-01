# Decap Verify Vector Finalizer Feasibility

Status: audit only.  No V2 ASM was implemented.

## Starting Point

The first direct byte finalizer prototype is correctness-pass but rejected for
PMU:

```text
symbol: gt_decap_verify_basemul_tobytes_direct_candidate
prototype: asm/gt_decap_verify_basemul_tobytes_direct_candidate.S
gate: GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_DIRECT
status: rejected_pmu_regression
```

Correctness:

```text
verify_basemul_tobytes_mismatches=0
decap_verify_contract_total_mismatches=0,valid_cases=256,invalid_cases=1280
```

Pi5 PMU:

| window | cycles p50 | cycles IQR | instr p50 |
| --- | ---: | ---: | ---: |
| `decap_verify_basemul_plus_tobytes_r2` | 3288 | 0 | 3290 |
| `decap_verify_contract_direct_candidate` | 4355 | 1 | 5947 |
| `full_decap_current` | 33352 | 11 | 75217 |
| `full_decap_contract_direct_candidate` | 34487 | 15 | 77875 |

Regression:

```text
local delta vs basemul_plus_tobytes = +1067 cycles
full decap delta vs current         = +1135 cycles
```

The direct byte contract is therefore correct, but the scalar finalizer shape is
not performance-useful.

## Scalar Prototype Cost

The rejected prototype uses this path for every 64-coefficient `poly_tobytes`
chunk:

```text
basemul loop A -> st4 32 coeffs to stack
basemul loop B -> ld4 staged 32 coeffs from stack
normalize 64 centered int16 coeffs
pack 32 12-bit pairs with scalar extraction and byte stores
```

The scalar packing macro has this static body per packed coefficient pair:

```text
umov  x 2
strb  x 3
lsr   x 2
orr   x 1
```

Per 64-coefficient chunk:

| category | count |
| --- | ---: |
| `umov` | 64 |
| `strb` | 96 |
| scalar `lsr` | 64 |
| scalar `orr` | 32 |
| scalar extract/pack total | 256 |
| stack `st4` | 1 |
| stack `ld4` | 1 |
| vector normalize | 24 |

For the full 768-coefficient polynomial:

| category | count |
| --- | ---: |
| `umov` | 768 |
| `strb` | 1152 |
| scalar `lsr` | 768 |
| scalar `orr` | 384 |
| scalar extract/pack total | 3072 |
| stack `st4` | 12 |
| stack `ld4` | 12 |

This explains the PMU instruction regression:

```text
baseline basemul_plus_tobytes instr = 3290
scalar direct candidate instr       = 5947
delta                               = +2657 instr
```

The scalar route should stay rejected.

## Production `poly_tobytes` Strategy

Production `poly_tobytes` is:

```text
symbol: poly_tobytes
source: asm/slothy/support_kernels/support_kernels.n1.opt.S
```

Per 64-coefficient loop, the scheduled support kernel uses:

| mnemonic class | count |
| --- | ---: |
| `ld1` | 2 |
| `sshr` | 8 |
| `and` | 8 |
| `add` | 8 |
| `shl` | 6 |
| `ushr` | 4 |
| `eor` | 6 |
| `trn1` | 9 |
| `trn2` | 9 |
| output `st1` | 2 |

The loop is about 60 vector instructions inside the Slothy marker plus two
vector stores and loop control.  The important property is that it never
extracts per-coefficient values into scalar registers; it keeps the 12-bit
packing in Neon lanes.

Input shape after `poly_tobytes` loads one 64-coefficient memory chunk:

```text
v9  = memory coeffs 0..7
v10 = memory coeffs 8..15
v11 = memory coeffs 16..23
v12 = memory coeffs 24..31
v26 = memory coeffs 32..39
v27 = memory coeffs 40..47
v28 = memory coeffs 48..55
v29 = memory coeffs 56..63
```

Its vector pack network expects this contiguous-memory-vector input, not the
`st4` register shape produced by `poly_basemul`.

## Basemul Register Shape

At the direct-finalizer cut point, each plain `poly_basemul` loop has four
centered output vectors:

```text
out0 = v23
out1 = v24
out2 = v25
out3 = v26
```

A normal `st4 {out0,out1,out2,out3}` writes memory as:

```text
out0[0], out1[0], out2[0], out3[0],
out0[1], out1[1], out2[1], out3[1],
...
out0[7], out1[7], out2[7], out3[7]
```

Therefore two basemul loops produce the same 64 coefficients that
`poly_tobytes` later reads as eight contiguous vectors, but the values are in a
different register layout.

## Can The Vector Pack Logic Be Reused?

Yes, but only with an explicit register-layout conversion.

For one 32-coefficient half, convert four `st4`-shape output vectors into four
contiguous-memory vectors using a small zip network:

```text
t01_lo = zip1(out0.8h, out1.8h)
t23_lo = zip1(out2.8h, out3.8h)
t01_hi = zip2(out0.8h, out1.8h)
t23_hi = zip2(out2.8h, out3.8h)

mem0 = zip1(t01_lo.4s, t23_lo.4s)  // coeffs 0..7
mem1 = zip2(t01_lo.4s, t23_lo.4s)  // coeffs 8..15
mem2 = zip1(t01_hi.4s, t23_hi.4s)  // coeffs 16..23
mem3 = zip2(t01_hi.4s, t23_hi.4s)  // coeffs 24..31
```

This is six vector zip instructions per 32-coefficient half, or twelve per
64-coefficient chunk.  After doing this for two consecutive basemul loops, the
existing `poly_tobytes` vector normalize/pack network can be reused with the
loads removed.

This is a real vector strategy because it avoids:

```text
large stack staging
byte-by-byte scalar stores
per-coefficient scalar extraction
```

But it is not obviously a large win: it trades the removed r2 memory boundary
for extra permutation work.

## V2 Design Options

### V2A: Virtual `st4` To `ld1` Shape, Then Reuse Support Pack

Shape:

```text
two basemul loops produce:
  A0..A3 = first 32 coeffs in st4 register shape
  B0..B3 = second 32 coeffs in st4 register shape

zip network:
  A0..A3 -> mem0..mem3
  B0..B3 -> mem4..mem7

support pack network:
  normalize mem0..mem7
  shift/eor/trn pack
  st1 96 bytes
```

Estimated per 64-coefficient chunk:

| category | count |
| --- | ---: |
| st4-shape to memory-vector zip | 12 |
| normalize | 24 |
| shift/eor pack | 16 |
| transpose pack | 18 |
| output `st1` | 2 |
| scalar extraction | 0 |
| stack staging | 0 |

Relative to current `basemul + poly_tobytes`, V2A removes:

```text
2 basemul output st4 stores per 64 coeffs
2 poly_tobytes ld1 loads per 64 coeffs
```

but adds:

```text
12 zip instructions per 64 coeffs
```

Full-polynomial projection:

```text
removed memory ops: 24 st4 + 24 ld1
added vector zips:  144
scalar pack removed vs V1: 3072 scalar instructions
```

V2A should be much faster than the rejected scalar prototype.  Against the
production `basemul + poly_tobytes` baseline, expected movement is small:

```text
local expected delta: roughly -50 to +100 cycles
```

This estimate is intentionally conservative because the removed r2 memory
traffic is L1-hot and the added zip network increases shuffle pressure.

### V2B: Rewrite Pack Network To Consume `st4` Shape Directly

This route avoids the explicit twelve-zip conversion by deriving a new
shift/eor/trn network directly from:

```text
A0..A3, B0..B3 in st4 register shape
```

It is technically feasible, but it needs a new lane-map proof:

```text
input tags: out{0..3}_{half A/B}_lane{0..7}
output tags: exact POLYBYTES byte positions
```

V2B may recover the only meaningful headroom in this route.  If it can reduce
or absorb most of the twelve conversion zips, the possible local saving becomes:

```text
local expected delta: roughly -100 to -250 cycles
```

That is still a small full-decap gain:

```text
100 cycles / 33352 ~= 0.30%
250 cycles / 33352 ~= 0.75%
```

## Feasibility Decision

Decision:

```text
feasible_vector_v2
```

Reason:

```text
The production vector `poly_tobytes` network can be reused after a documented
st4-register to contiguous-vector conversion, and a more aggressive direct-SoA
network is possible with a lane-map proof.
```

However, this is not a strong next optimization target:

```text
V2A likely has weak or neutral PMU movement.
V2B requires non-trivial lane-map work for at most sub-1% full-decap gain.
```

Recommendation:

```text
Do not write V2 ASM unless this route is explicitly approved as a small
benchmark-only experiment.  If approved, implement V2A first only as a
correctness/PMU sanity check; continue to V2B only if V2A is non-regressing or
the lane-map suggests fewer than twelve additional permutation instructions.
```

## Required Checks Before Any V2 ASM

```text
1. Tagged-lane model for st4-shape basemul outputs to POLYBYTES.
2. Differential against production poly_tobytes for random and boundary inputs.
3. Direct byte oracle:
     gt_decap_verify_basemul_tobytes_vector_candidate
     ==
     poly_tobytes(poly_basemul(...))
4. Full valid/invalid decap differential.
5. Pi5 PMU versus decap_verify_basemul_plus_tobytes_r2, not versus scalar V1.
```

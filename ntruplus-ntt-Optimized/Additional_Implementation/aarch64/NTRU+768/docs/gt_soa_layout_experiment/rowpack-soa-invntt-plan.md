# GT Rowpack SoA InvNTT Plan

Scope: redesign the transformed-domain layout so InvNTT can consume SoA without
scalar halfword gather.  This is a layout and oracle gate only; it does not add
a production assembly candidate.

## Problem With Chunk-Local SoA

The first SoA experiment used:

```text
chunk = physical_j / 8
vlane = physical_j % 8
index = branch*384 + chunk*32 + lane*8 + vlane
```

That layout is good for pointwise basemul over eight consecutive
`physical_j` values, but the inverse row NTT consumes rows:

```text
physical_j(row, k32) = (32*row + 3*k32) mod 96
```

The current inverse row vector for one `physical_j` packs:

```text
[branch0 lane0..lane3, branch1 lane0..lane3]
```

In chunk-local SoA those eight values live in eight different halfword slots, so
the wrapper must do `8x ldrh + 8x mov.h` per row vector.  The measured local
sanity result was slower than block-major input.

## Rowpack SoA Layout

Use the inverse row decomposition as the public transformed layout:

```text
physical_j(row, k32) = (32*row + 3*k32) mod 96
row(physical_j) = 2 * (physical_j mod 3) mod 3

rowpack_index(branch, row, lane, k32) =
  branch*384 + row*128 + lane*32 + k32
```

Each `(branch,row,lane)` plane is one contiguous 32-halfword inverse-row input.
Each Neon load of eight halfwords contains:

```text
k32 = chunk*8 + [0..7]
physical_j = (32*row + 3*k32) mod 96
```

This gives InvNTT native row loads:

```text
q0 = ld1 rowpack[branch,row,lane,k32=0..7]
q1 = ld1 rowpack[branch,row,lane,k32=8..15]
q2 = ld1 rowpack[branch,row,lane,k32=16..23]
q3 = ld1 rowpack[branch,row,lane,k32=24..31]
```

No scalar gather is needed.

## Basemul Under Rowpack SoA

Basemul does not require consecutive `physical_j` in memory.  It requires the
four quartic planes and the matching lambda for each `physical_j`.

For each `(branch,row,chunk)`:

```text
lambda_vec[vlane] =
  gt_rowbitrev_lambda[branch][physical_j(row, chunk*8 + vlane)]
```

Then the same eight-way plane basemul shape applies:

```text
a0..a3 = ld1 rowpack[branch,row,lane0..lane3,k32 chunk]
b0..b3 = ld1 rowpack[branch,row,lane0..lane3,k32 chunk]
r0..r3 = st1 rowpack[branch,row,lane0..lane3,k32 chunk]
```

This keeps the pointwise kernel on contiguous vector loads/stores and changes
only table order.

Local sanity from `bench_gt_basemul_soa` on this machine:

| target | median `cntvct` ticks/call | avg wall ns/call |
| --- | ---: | ---: |
| `gt_basemul_ld4_intrinsic` | 8.828 | 423.83 |
| `gt_basemul_soa_ld1_intrinsic` | 6.047 | 256.20 |
| `gt_basemul_rowpack_soa_ld1_intrinsic` | 5.219 | 227.85 |
| `gt_basemul_rowpack_soa_canonical_ld1_intrinsic` | 5.594 | 243.53 |
| `gt_basemuladd_ld4_intrinsic` | 6.312 | 274.12 |
| `gt_basemuladd_soa_ld1_intrinsic` | 4.984 | 217.75 |
| `gt_basemuladd_rowpack_soa_ld1_intrinsic` | 5.016 | 216.61 |
| `gt_basemuladd_rowpack_soa_canonical_ld1_intrinsic` | 5.625 | 245.83 |
| `gt_block_to_soa_3_inputs` | 8.672 | 368.49 |
| `gt_block_to_rowpack_3_inputs` | 11.391 | 487.05 |
| `gt_soa_to_block_1_output` | 3.281 | 139.71 |
| `gt_rowpack_to_block_1_output` | 3.141 | 134.87 |

The local counter is not a Pi5 cycle measurement.  It is enough to show that
rowpack SoA does not destroy the pointwise-kernel benefit of plane loads.  The
conversion rows also show why this direction only makes sense if Forward NTT
produces rowpack and InvNTT consumes rowpack directly.

## InvNTT Row Kernel Shape

The current row kernel vectorizes across eight independent transforms:

```text
lanes = [branch0 lane0..lane3, branch1 lane0..lane3]
vectors = 32 k32 positions
```

Rowpack SoA vectorizes within one transform:

```text
lanes = eight k32 positions
vectors = four chunks per (branch,row,lane)
```

That removes input gather, but it changes the row NTT instruction shape:

- stages 1..3 become in-vector butterflies at distances 1, 2, and 4;
- stages 4..5 become cross-vector butterflies between chunks;
- twiddles become per-lane vectors instead of scalar lane constants;
- the final row output is already in row/lane planes for the inverse DFT3
  stage to consume or for a later rowpack-to-post fusion.

This is not a small patch to `DIRECT_STAGE123_VEC`; it is a new row-kernel
contract.

`test_invntt32_rowpack_kernel_model` now provides the first executable model of
that contract:

- input is four contiguous q-vectors holding `k32 = 0..31` for one
  `(branch,row,lane)` plane;
- stage 1 uses `rev32`-shape lane swaps;
- stage 2 uses `rev64`-shape lane swaps;
- stage 3 uses `ext #8`-shape half-vector swaps;
- stages 4 and 5 use cross-vector butterflies with per-lane twiddle vectors;
- row-input Barrett normalization is fused into the row kernel, so current raw
  basemul/add outputs do not need a caller pre-pass;
- row-end Barrett reduction matches the scalar assembly-operation model.

The model compares exactly against the scalar `sqrdmulh/mul/mls` row model for
patterns and random rows.  This proves the rowpack instruction shape is
algebraically viable before any Slothy scheduling.

`test_gt_rowpack_soa_invntt32_fullpath` wires the generated Slothy row kernel
into the complete inverse path:

- emit Forward NTT directly into rowpack SoA and compare that direct layout
  against `block_to_rowpack(ntt_gt_rowbitrevlayout())`;
- run one InvNTT32 row kernel for every `(branch,row,lane)` plane;
- prove rowpack scalar basemul/add layout matches block-major basemul/add;
- run direct-rowpack Forward NTT -> rowpack basemul/add -> rowpack InvNTT
  product and product-add roundtrips;
- run inverse DFT3 across the three rows;
- apply untwist and the final two-branch merge;
- compare against `invntt_gt_rowbitrevlayout_exact` and the original natural
  input modulo `q`.

Both the RA-only `.alloc.S` and scheduled `.opt.S` row kernels pass this gate
locally.  Product and product-add roundtrips now call the row kernel directly;
the generated row kernel absorbs row-input Barrett normalization at entry.

`rowpack-basemul-output-range-proof.md` records the no-normalization variant
condition.  The current raw basemul/add convention can emit lanes outside
`[-1728, 1728]`, so it still needs either fused row-kernel normalization or a
new canonical basemul/add output convention.

That canonical convention now has an executable full-path gate:
`test_gt_rowpack_soa_invntt32_fullpath_canonical`.  It compiles the same
rowpack full-path oracle with `ROWPACK_CANONICAL_BASEMUL` and links the
no-entry-normalization row kernel
`kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.opt.S`.  The gate proves
product and product-add roundtrips without row-input Barrett inside the row
kernel.  The tradeoff measured locally is that canonical rowpack basemul/add
adds about 0.38 and 0.61 median `cntvct` ticks/call respectively, while the
row-kernel model drops from 162 instructions / 40 expected cycles for the
scheduled fused-normalization kernel to 150 instructions / 37 expected cycles
for the scheduled no-entry variant.

The same full-path oracle also has opt-in benchmark targets that compare the
two ABI choices on one operation path:

```sh
make bench_gt_rowpack_pipeline_compare
make bench_gt_rowpack_pipeline_add_compare
```

These targets measure direct rowpack Forward NTT, rowpack basemul/add, rowpack
InvNTT, and the combined pipeline.  They are still experimental because the
Forward NTT side is C oracle code, not production rowpack assembly, but they
make the fused vs canonical ABI comparison reproducible on Pi5.

Latest local sanity:

| target | basemul median | invntt median | pipeline median |
| --- | ---: | ---: | ---: |
| fused rowpack product | 7.250 | 33.000 | 490.594 |
| canonical/no-entry rowpack product | 9.453 | 31.438 | 507.109 |
| fused rowpack product-add | 7.625 | 32.969 | 700.453 |
| canonical/no-entry rowpack product-add | 9.938 | 32.766 | 711.016 |

The canonical path pays more in basemul/add and wins only a small amount in the
row-kernel portion.  On this local sanity run the full product pipeline is
slower for canonical/no-entry, while product-add is close.  Treat these as hook
validation numbers, not Pi5 production conclusions.

Pi5 cycle-counter run:

```sh
make bench_gt_rowpack_pipeline_cycles_compare
make bench_gt_rowpack_pipeline_add_cycles_compare
```

| target | ntt median cycles | basemul/add median cycles | invntt median cycles | pipeline median cycles |
| --- | ---: | ---: | ---: | ---: |
| fused rowpack product | 77597.688 | 9981.281 | 17022.188 | 182243.891 |
| canonical/no-entry rowpack product | 77924.375 | 11696.453 | 16721.391 | 183369.734 |
| fused rowpack product-add | 77577.734 | 10835.609 | 17025.266 | 260366.719 |
| canonical/no-entry rowpack product-add | 77626.047 | 12303.625 | 16707.172 | 261614.141 |

The Pi5 cycle result confirms the local direction.  The no-entry row kernel
saves about 300-318 cycles in InvNTT, but canonical basemul/add costs about
1468-1715 cycles, and the full pipeline becomes about 1126-1247 cycles slower.
Do not promote the canonical/no-entry ABI.  Keep the fused row-input Barrett
normalization row kernel as the active rowpack candidate unless a later
basemul/add implementation removes the canonicalization cost.

The next diagnostic compares the active rowpack fused oracle against the
promoted GT production path under the same Linux hardware cycle counter:

```sh
make bench_gt_rowpack_vs_production_cycles_compare
```

This target runs:

- `gt_baseopt_ntt_mul_pipeline_cycles`
- `gt_rowpack_fused_ntt_mul_pipeline_cycles`
- `gt_baseopt_ntt_basemul_add_pipeline_cycles`
- `gt_rowpack_fused_ntt_basemul_add_pipeline_cycles`

Interpret this as a production-comparability diagnostic, not as promotion or
rejection evidence for the rowpack layout.  The GT side is production assembly,
while the rowpack side still uses C oracle glue for the Forward NTT and
pointwise layer.  Absolute rowpack oracle cycles can show that the current hook
is not production-equivalent, but they must not be used to reject the rowpack
layout itself.

Pi5 result for that gate:

| target | ntt median cycles | basemul/add median cycles | invntt median cycles | pipeline median cycles |
| --- | ---: | ---: | ---: | ---: |
| promoted GT product | 2700.578 | 2812.172 | 4018.406 | 12251.656 |
| rowpack fused oracle product | 77497.422 | 10027.281 | 17097.844 | 182189.328 |
| promoted GT product-add | 2701.016 | 2907.250 | 4021.875 | 14985.078 |
| rowpack fused oracle product-add | 77500.000 | 10836.031 | 17133.969 | 260635.906 |

The rowpack fused oracle is far behind the promoted GT production path in this
diagnostic:

| pipeline | rowpack - promoted GT | ratio |
| --- | ---: | ---: |
| product | +169937.672 cycles | 14.87x |
| product-add | +245650.828 cycles | 17.39x |

Most of the observed gap comes from the oracle Forward NTT path.  Product mode
pays two rowpack oracle Forward NTTs, each about 74797 cycles slower than the
promoted GT assembly NTT.  The rowpack basemul/add and InvNTT glue are also
still much slower than production.  This proves the current fullpath bench is
oracle/glue dominated and not production-comparable; it does not prove the
rowpack layout is bad.

The corrected decision is:

- keep the fused row-input normalization ABI if rowpack work continues;
- reject canonical/no-entry ABI under the current same-framework comparison;
- do not use promoted-GT-vs-rowpack-oracle absolute cycles as rowpack rejection
  evidence;
- use the component productionization dashboard before choosing any rowpack ASM
  prototype.

The dashboard is tracked in
`docs/gt_soa_layout_experiment/component-productionization-dashboard.md`.

## Expected Cost Tradeoff

Per transformed polynomial, the memory shape becomes:

| operation | block-major/current | chunk-local SoA | rowpack SoA |
| --- | ---: | ---: | ---: |
| basemul input/output | `ld4/st4` | `ld1/st1` planes | `ld1/st1` planes |
| InvNTT input | `2x ldr d + mov d[1]` per row vector | scalar halfword gather | `ld1` row-plane vectors |
| InvNTT row arithmetic | cross-vector butterflies, no row shuffles | same as current after gather | in-vector early butterflies plus per-lane twiddles |

The rowpack layout removes the known bad gather.  The remaining question is
whether the in-vector butterfly and twiddle-vector cost is lower than the old
input layout plus `ld4/st4` pointwise traffic in the full pipeline.

## Validation Gates

1. `test_gt_rowpack_soa_oracle`:
   - proves `physical_j <-> (row,k32)` mapping;
   - proves rowpack block roundtrip;
   - proves rowpack InvNTT reference equals block-major InvNTT reference;
   - prints row-order lambda vectors for table generation.
2. `bench_gt_basemul_soa` rowpack paths:
   - same arithmetic as current SoA basemul;
   - lambda loaded in rowpack order;
   - confirms rowpack pointwise basemul/add remain `ld1/st1` plane kernels.
3. `test_invntt32_rowpack_kernel_model`:
   - stages 1..3 in-vector;
   - stages 4..5 cross-vector;
   - compare row outputs against the scalar assembly-operation row model.
4. `test_gt_rowpack_soa_invntt32_fullpath`:
   - calls the generated row kernel across all 24 rowpack planes;
   - proves direct rowpack Forward NTT matches block-major plus conversion;
   - proves rowpack basemul/add layout matches block-major basemul/add;
   - proves DFT3, untwist, and branch merge still match the exact inverse;
   - proves product and product-add roundtrips through fused row-input
     normalization in the generated row kernel.
5. `test_gt_rowpack_soa_invntt32_fullpath_nativebasemul`:
   - replaces scalar/helper rowpack basemul/add with the native rowpack NEON
     prototype;
   - keeps the fused row-input normalization ABI;
   - proves product and product-add roundtrips through the same fullpath oracle.
6. `analyze_gt_rowpack_basemul_output_ranges`:
   - proves the canonical basemul/add output convention is sufficient for a
     future no-row-input-normalization row kernel;
   - records a deterministic counterexample showing current raw basemul/add
     output is not sufficient.
7. `test_gt_rowpack_soa_invntt32_fullpath_canonical`:
   - proves canonical rowpack basemul/add output satisfies the no-entry row
     kernel input contract;
   - proves product and product-add full-path roundtrips with the no-entry
     `.opt.S` row kernel.
8. `bench_gt_rowpack_pipeline_compare` and
   `bench_gt_rowpack_pipeline_add_compare`:
   - benchmark fused row-kernel normalization and canonical/no-entry ABI on the
     same rowpack oracle path;
   - keep correctness checks inside each benchmark binary before timing.
9. `bench_gt_rowpack_component_cycles_dashboard`:
   - records promoted GT production component cycles beside rowpack fused
     oracle component cycles;
   - includes scalar/helper and native NEON rowpack pointwise variants;
   - classifies rowpack pieces as production assembly, oracle, scalar/helper,
     or wrapper/glue;
   - must not be used as rowpack layout rejection evidence.
10. `test_gt_forward_rowpack_output_contract`:
   - proves the Forward NTT block-major output to rowpack SoA mapping;
   - proves the existing NTT32 row-vector scatter boundary can be interpreted
     as either current block-major scatter or target rowpack scatter;
   - proves direct rowpack Forward NTT output equals
     `block_to_rowpack(ntt_gt_rowbitrevlayout(input))`.
11. Only after a component prototype is production-equivalent should full
   rowpack pipeline benchmarking drive promotion or rejection.

## Current Recommendation

Continue with rowpack SoA as the only plausible full-layout SoA direction, but
do not use the current oracle fullpath absolute cycles to accept or reject it.
Stop pursuing chunk-local SoA for public Forward NTT output unless a separate
conversion amortization use case appears.

The normalization decision is settled for now: keep fused row-input Barrett
normalization in the row kernel, and do not promote the canonical/no-entry ABI
unless rowpack basemul/add canonicalization later becomes essentially free.

The rowpack basemul/add NEON prototype is component-positive on the latest Pi5
cycle run, so the next production-facing step is Forward NTT output packing.
Do not rewrite the whole transform first.  Start from the existing NTT32 row
boundary in `asm/my_ntt.s` / `asm/slothy/my_32ntt.opt.s`, where each row emits
32 vectors with branch0 quartic lanes in the low D half and branch1 quartic
lanes in the high D half.  The next prototype should replace only the final
block-major scatter with rowpack SoA output packing and then use
`bench_ntt_pipeline.c`-style cycle accounting for production-equivalent
comparisons.

# Register flow

## 1. Frozen NTT16 producer entry

| Register | Content |
| --- | --- |
| `x0` | main P8 vectors for this bank |
| `x1` | exact strided tail start, `&p8[768 + bank]` |
| `x2` | top-specific public NTT16 table |
| `x3` | case-specific CF5 table; producer leaves it unchanged |
| `x4` | public stride `16` for exact tail halfword loads |
| `v13` | byte-index table used by final tail bit reversal |
| `v14` | eight copies of `q=3457` |
| `v15` | packed M5R-D roots; also needed again by later banks |

The producer executes the unchanged M5R-D tail gather, branch twist, tail
NTT16, main sixteen-column branch twist, main NTT16, and the two 8x8
transposes.  It performs 345 instructions and no coefficient store.

## 2. Exact NTT16 boundary

For `s=0..8` and lane `l=0..7`:

- `lo_f{s}_raw.h[l]` is row `s`, NTT16 column `l`;
- `hi_f{s}_raw.h[l]` is row `s`, NTT16 column `8+l`.

All values are R0 representatives with proven absolute bound 9342.  The tail
NTT16 results are the `s=8` values themselves, not two additional live
vectors.  Slothy selected this exact physical coloring:

| Logical value | Register | Logical value | Register |
| --- | ---: | --- | ---: |
| `lo_f0_raw` | `v5` | `hi_f0_raw` | `v17` |
| `lo_f1_raw` | `v31` | `hi_f1_raw` | `v23` |
| `lo_f2_raw` | `v4` | `hi_f2_raw` | `v12` |
| `lo_f3_raw` | `v16` | `hi_f3_raw` | `v6` |
| `lo_f4_raw` | `v26` | `hi_f4_raw` | `v0` |
| `lo_f5_raw` | `v18` | `hi_f5_raw` | `v21` |
| `lo_f6_raw` | `v28` | `hi_f6_raw` | `v8` |
| `lo_f7_raw` | `v30` | `hi_f7_raw` | `v11` |
| `lo_f8_raw` | `v19` | `hi_f8_raw` | `v7` |

`v13/v14/v15` retain bitrev/q/roots.  There is no `mov`, `orr`, spill, stack
access, or coefficient memory operation at this boundary.

## 3. Consumer entry and table layout

The same `x3` address instruction that M5R-D already executes now points to a
case table with this physical order:

1. one common Algorithm-10 pair pack for top 0, or three packs for top 1;
2. block-0 lane-dependent `(b,bprime)` vectors in exact DAG consumption order;
3. block-1 lane-dependent `(b,bprime)` vectors in exact DAG consumption order.

Therefore common constants do not need another pointer or another `adr`.
Top-0 advances `x3` by 1104 bytes; top-1 advances it by 624 bytes.

Each consumer first loads its common packs, then computes:

1. the fused input twist/FR-ISO2 factors;
2. oriented level-1 `B3` nodes `A`, `B`, and paper-oriented `C`;
3. the `eta` corrections selected by the CF1 witness;
4. oriented level-2 `B3` nodes;
5. the final composite factors directly into `out0..out17`.

Every modular fixed-constant multiply uses exactly `mul`, `sqrdmulh`, `mls`.
The two input blocks are sequential: `out0..out8` stay live throughout block
1, and `out9..out17` are then produced from the high-column inputs.

## 4. Consumer output coloring

| Case | `out0..out17` physical registers |
| --- | --- |
| `t0c1` | `v19,v5,v28,v10,v2,v22,v30,v18,v29,v4,v17,v3,v12,v21,v0,v16,v24,v27` |
| `t0c2` | `v27,v24,v20,v16,v22,v28,v2,v5,v29,v6,v1,v23,v11,v31,v12,v30,v9,v10` |
| `t1c1` | `v31,v5,v1,v10,v27,v22,v28,v26,v16,v6,v20,v18,v30,v19,v4,v11,v24,v7` |
| `t1c2` | `v20,v31,v19,v3,v29,v26,v2,v16,v27,v24,v22,v30,v11,v17,v9,v12,v5,v0` |

None uses `v13`, `v14`, or `v15`; those constants are intact for the next
bank.  Stores consume these output registers directly, so no canonical-output
copy is required.

## 5. Cost boundary

| Region | Instructions | N1 proxy cycles |
| --- | ---: | ---: |
| producer | 345 | 86 |
| top-0 consumer | 309 | 77 |
| top-1 consumer | 279 | 69 |

The proxy sums are 163 and 155.  These are separated-region Neoverse-N1 model
figures, not Cortex-A76 measurements and not a prediction of the final shared
producer layout.

Four scaled banks add `2*(309-224) + 2*(279-224) = 280` instructions to the
4446-instruction M5R-D Forward.  Since `x3` table setup is reused, the current
dynamic estimate is 4726, twelve below CF0's 4738.

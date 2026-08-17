# CleanGT Encap retired-load attribution (2026-08-13)

## Result

The previously observed CleanGT Encap load debt is now closed exactly:

| Placement | CleanGT - Official retired loads |
|---|---:|
| Normal | +763.0 loads/encapsulation |
| Reversed | +763.0 loads/encapsulation |

The measurement uses in-process perf-event counters. Counters are reset and
enabled immediately before the repeated semantic prefix and disabled
immediately after it. Process startup, KAT setup and correctness checks are
outside the counted region.

The harness has 18 byte-exact cumulative checkpoints. Normal and reversed
ELFs both pass every checkpoint. Each checkpoint was measured with 10,000
iterations and eight paired Official/CleanGT samples. Incremental results are
paired adjacent-prefix differences.

## Exact load decomposition

The instruction/load counts are effectively integral and identical in both
placements:

| Component | Official loads | CleanGT loads | Delta |
|---|---:|---:|---:|
| Decode public key h | 58 | 164 | **+106** |
| Copy coins | 3 | 3 | 0 |
| hash_f | 3,419 | 3,419 | 0 |
| hash_h | 799 | 800 | +1 |
| CBD r | 10 | 10 | 0 |
| Forward r | 267 | 446 | **+179** |
| Serialize rhat | 52 | 148 | **+96** |
| hash_g | 3,790 | 3,790 | 0 |
| SOTP-produce m | 14 | 16 | +2 |
| Forward m | 267 | 446 | **+179** |
| General BaseMul | 246 | 351 | **+105** |
| Add m | 99 | 98 | -1 |
| Serialize ciphertext | 53 | 148 | **+95** |
| Copy shared secret | equal | equal | 0 |
| Clear msg | 6 | 7 | +1 |
| Clear buf, r, m | equal | equal | 0 |

Grouped closure:

| Family | Extra loads |
|---|---:|
| Decode | +106 |
| Two Forward calls | **+358** |
| Two Q24 serializers | **+191** |
| BaseMul + add | **+104** |
| All hashes | +1 |
| CBD + SOTP | +2 |
| Copies + clears | +1 |
| **Total** | **+763** |

There is no single 300--500-load component. The two Forward calls form the
largest repeated family at +358 loads. The next largest targets are the two
serializers (+191), Decode (+106), and BaseMul/add (+104).

## Spill and scratch audit

Disassembly of these executed GT symbols contains zero stack-pointer memory
references:

- gt32_q24_decode_soa_body_cage
- gt32_tile4_frontend_wide_raw_asm
- gt32_tile4_attr_forward_all_bm_soa_asm
- gt32_q24_encode_soa_lazy10788_asm
- gt32_tile4_basemul_general_soa_soa_to_soa_asm

The extra retired loads are therefore not hidden AVX2 register spills.

The C caller deliberately allocates h, r, m, c, and work stack objects. These
are semantic scratch arrays, not compiler spill slots. The N5 core explicitly
reloads eight YMM vectors for each of six tiles from the frontend scratch: 48
scratch-vector loads per Forward, or 96 across the two Encap Forward calls.
The remaining Forward-family debt consists of the source/constant/table load
profile of the two-stage GT implementation relative to Official.

## What this changes

The +0.75--0.78K observation is no longer a broad caller/glue hypothesis.
Hashes, copies and secure clears account for only four extra loads in total.
The debt belongs almost entirely to the GT polynomial representation:

1. GT-unpack;
2. the two-stage N5 producer;
3. Q24 packet serializers;
4. M-domain B3.

This does not prove that all 763 loads are cycle-critical. They are retired
load instructions, not L1 misses. The independent cumulative endpoints have
placement-sensitive cycle differences even though their load deltas are exact.
Any optimization proposal must therefore show both a lower load count and a
caller-level core-cycle improvement.

## Decision and next gate

- Do not reopen butterfly or BaseMul algebra.
- Do not target hash/copy/clear; their load delta is effectively zero.
- Do not pursue stack-spill elimination; the target ASM has no stack spills.
- Treat the two Forward calls as the largest load family, but retain the prior
  hard stop on giant frontend/core fusion. A candidate must stay compact and
  reusable.
- A bounded candidate should eliminate at least about 64 retired loads per
  Encap and must not duplicate a large code body.
- Before implementation, measure whether the four load-heavy components also
  own the load-stall signal (L1 miss, L1D pending cycles,
  ld_blocks/store-forward, and backend-bound slots). This separates
  load-count debt from critical load-latency debt.

Artifacts:

- bench/bench_encap_load_attribution.c
- tools/run_encap_load_attribution_pmu.py
- results/tile4-encap-load-attribution-pmu.json

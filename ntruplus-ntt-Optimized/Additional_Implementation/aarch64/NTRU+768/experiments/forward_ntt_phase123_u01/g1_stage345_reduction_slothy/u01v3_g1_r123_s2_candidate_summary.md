# G1R123+S2 Production Summary

Status: promoted GT production forward NTT.

## Independent variants

- G1: full U01v3 G1 `poly_ntt` with stack-local Stage12 scratch.
- G1+S2: G1 plus audited high-half `umov+str` stores.
- G1R123: G1 with Slothy-scheduled Stage345 block1/2/3 reduction tails.
- G1R123+S2: G1R123 plus audited high-half `umov+str` stores.

All four named wrappers and drop-in wrappers remain independently selectable.
The frozen SHA-256 inventory is in
`u01v3_g1_r123_s2_frozen_manifest.json`.

## Frozen correctness and ABI gates

- Full `poly_ntt` differential: pass.
- Out-of-place and in-place: pass.
- G1/G1+S2 ABI sentinel: pass, mask `0x0`.
- G1R123/G1R123+S2 ABI sentinel: pass, mask `0x0`.
- Drop-in KEM correctness for all four variants: pass.
- Slothy block1/2/3 self-check and instruction-multiset gate: pass.
- Block0: unchanged after inherited-stack-handoff window was infeasible.
- G1 S2 audit: 27 safe sites and 5 retained `ext+str` sites per row.
- G1R123 S2 audit: 28 safe sites and 4 retained `ext+str` sites per row.
- S2 temporary registers: caller-saved, dead at site, no address alias.

## Same-binary contract

- Production and G1R123+S2 compile from separate namespaced `kem.c`
  translation units in one binary.
- Each measured KEM entry has two statically resolved forward-NTT calls.
- There is no runtime dispatch branch inside either measured `poly_ntt`.
- AB/BA calls reuse identical buffers and deterministic random streams.
- A preparation-only capture namespace records the four real forward-NTT
  inputs; it is not used in measured KEM calls.

## Same-binary full-KEM result

Pi 5 Cortex-A76, core 3 pinned, 61 paired samples, 2000 calls per sample.
The harness alternates AB/BA, replays identical deterministic randomness, uses
the same aligned buffers, and checks correctness after every pair.

| Scope | A production p50 | B candidate p50 | paired delta p10/p50/p90 | win rate |
|---|---:|---:|---:|---:|
| encap cycles | 37718.332 | 37614.476 | -113.653 / -106.243 / -100.240 | 100% |
| decap cycles | 33315.364 | 33225.502 | -101.116 / -88.853 / -82.876 | 100% |
| encap instructions | 105607.019 | 105081.019 | -526 | 100% |
| decap instructions | 75199.018 | 74673.018 | -526 | 100% |

The four captured forward-NTT sites retain median paired wins of
`-45.294`, `-45.767`, `-44.489`, and `-44.977` cycles. Each site retires
263 fewer instructions and wins all 61 cycle samples.

Correctness: 0 mismatches across 2562 paired checks. The same-binary linkage
audit passes and confirms that no dispatch branch is present inside either
measured `poly_ntt` path.

Detailed normalized distributions are in
`aarch64-bench/results/u01v3_g1_r123_paired_kem/summary.md`; raw counters and
the symbol/call-graph audit are retained in the same directory.

## Frontend/backend interpretation

- Candidate `poly_ntt` is a 14904-byte self-contained symbol. Production's
  48-byte symbol is a wrapper around the existing row kernel.
- Candidate median L1I refills increase by 0.147 per encap and 0.172 per decap.
- Median backend stalls decrease by 53.314 per encap and 16.203 per decap.
- Branch-miss and frontend-stall deltas are too small/noisy to explain the
  cycle result. The stable cycle and retired-instruction wins remain the
  promotion signal despite the I-cache cost.

## Production integration

The default GT build now links:

```text
asm/gt/poly_ntt_g1_r123_s2.S
asm/gt/poly_ntt_g1_r123_s2_tables.inc
```

The promoted `.text` is byte-identical to the frozen G1R123+S2 candidate. The
original GT production NTT remains available for regression comparison with:

```text
GT_PRODUCTION_USE_LEGACY_NTT=1
```

The promoted and legacy deterministic KAT response files are byte-identical:

```text
dca76b32748655990289002a05f7b1d648334d7ded05845c7fe3f1449d26690f
```

The three-way Pi5 benchmark against legacy GT and KPQC final is in
`aarch64-bench/results/gt_production_g1r123s2_threeway/summary.md`. No keypair
improvement is attributed to G1R123+S2 because the optimized keypair triple
path does not call generic `poly_ntt`.

Frozen manifest SHA-256:
`7bc2eee5315357e2c2f7a77a073bcc6339e48384c6d887df2f0fd005e4af738b`.

# Checkpoint G1C-ITAIL-D0-M2

## Decision

Close the current D8-to-inverse9 boundary-fusion search class. M2 proves that
M1's large regression was mostly an immediate-triad scheduling failure, but a
late-layer zero-copy schedule still loses robustly to the materialized M0
control. No D0-M3/M4 tail-local search is authorized. Keep B1 as the selected
materialized inverse9 control and move to F0-to-consumer-native BaseMul.

## Exact proof and executable gates

M2 first produces and retains all nine physical-P D8 vectors for one
`(branch,j)` wavefront, then applies all input reductions and the three B1
layer-1 radix-3 groups in B1's original order. Its generated
instruction-by-instruction proof preserves the exact C2+B1 arithmetic DAG and
the `R^-1` range chain `[-17377,17377]`, with peak 14/16 live YMM and no spill.

M0, M1, and M2 pass 1,003 real-producer differentials against C2+B1, including
in-place alias, input immutability, canary, ASan, and UBSan. The linked-object
audit records:

| Property | M0 | M1 | M2 |
| --- | ---: | ---: | ---: |
| Static instructions | 3675 | 3531 | 3531 |
| D1 input loads | 72 | 72 | 72 |
| D8 boundary stores | 72 | 0 | 0 |
| B1 boundary reloads | 72 | 0 | 0 |
| Final stores | 72 | 72 | 72 |
| Peak live YMM | 14 | 14 | 14 |

M2 retains M1's exact deletion of 72 stores and 72 reloads. Its non-move
arithmetic instruction multiset is identical to M0/M1, and all three leaves
are call-, branch-, frame-, stack-, spill-, and `vzeroupper`-free.

## SUPERCOP-derived serious price

The three-way measure uses pinned SUPERCOP 20260627, fixed O3GC, CPU 1,
performance governor, turbo disabled, one fixed measure ELF, and nine fresh
launches. A Latin-square call order places every variant first, second, and
third once per loop. Each combined variant has 2,592 observations.

| Repaired-D1 -> inverse16 tail -> inverse9 | StQ2 cycles |
| --- | ---: |
| M0 materialized control | 1636.6698 |
| M1 immediate-triad linked | 2004.5926 |
| M2 retained-nine late-layer linked | 1789.2855 |

The per-launch median `M2-M0` is `+152.9722` cycles; M2 loses to M0 in 9/9
launches. The median `M2-M1` is `-215.1528` cycles; M2 beats M1 in 9/9. Thus
restoring layer-level parallelism recovers much of M1's scheduling loss, but
zero boundary materialization has no cycle credit under this contract. The
materialized boundary acts as a useful execution-schedule decoupling point.

This is `supercop-derived-itail-d0-m2`, not a native SUPERCOP KEM result and not
production qualification.

## Search-space interpretation and next gate

The B1P ten-chain lower bound applies only to the current B ABI, two-radix3
family, and current scale/output contract. Other inverse9 arithmetic families
remain mathematically open but are not the next priority. R2's identity
residual gauge means its phase freedom is already internalized at the measured
boundary, not that phase/orientation design was irrelevant.

The project is now in local architecture convergence. The next ordered work is:

1. adapt F0 persistent forward output directly to consumer-native quartic
   BaseMul/BaseInv arithmetic without paying F1 canonicalization;
2. integrate one physical-representation chain for `2F+B+I`;
3. price that full polynomial island with SUPERCOP-derived polynomial measure;
4. only then enter native KEM and fixed-ELF promotion gates.

Do not add isolated tail candidates merely because they delete instructions;
schedule credit must be demonstrated in the complete caller path.

## Hwa / related-technique map

| Technique | Current 1152 status | Action |
| --- | --- | --- |
| Good-Thomas axis decomposition | Core `9x16` design | Retain |
| Cyclic orientation / phase convention | R2 plus all 729 current-family orientations searched | Retain scoped result |
| Avoid cosmetic natural order | F0 and physical P/Q repeatedly favored | Retain |
| Consumer-native representation | BMScale-to-D1 and repaired inverse16 show credit | Extend to BaseMul |
| Permutation-friendly SIMD | Semantic coefficient plane proved; global physical ABI remains open | Decide per edge |
| Interleave/transpose only where consumed | Full F0-to-BaseMul edge missing | Highest-priority experiment |
| Fuse permutation/twist with arithmetic | Direct physical-P inverse9 works; D8 fusion loses | Apply locally, benchmark schedule |
| Reduce distinct live constants | R2 benefit established | Track register pressure as well as cycles |
| Layer merging / register residence | Forward C2 works; inverse M1/M2 are counterexamples | Never infer credit from zero-copy alone |
| Base-case specialization | Consumer-native quartic BaseMul/BaseInv missing | Compare schoolbook, Karatsuba-like, coefficient-plane, and F0-S/D-native forms |
| Alternative incomplete transform / leaf degree | Outside current caller path | Defer |
| Rader-17 | No 17-axis in NTRU+ | Not applicable |
| Bruun / CT / Karatsuba leaf selection | General co-design lesson applies; formulas do not transfer directly | Re-evaluate for the quartic leaf |
| TMVP | Neon result depends on different ISA strengths | Do not assume an AVX2 win |
| Zero skipping / early dropping | No matching structural zeros or dropped outputs in current path | Not applicable now |

For NTRU+1152 the immediate leaf question is multiplication modulo
`x^4-lambda`; NTRU+864 will require a separate cubic consumer modulo
`x^3-lambda`. Do not copy 1152 physical decisions into 864 until the shared
GT9x16 semantic ABI and generators are stable.

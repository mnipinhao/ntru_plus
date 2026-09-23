# NTRU+768: mixed-gauge CT inverse decision gate

This gate follows the [twiddle-half absorption experiment](ntruplus768-twiddle-half-absorption.md). It asks whether the mixed-gauge true-`y=x⁴` CT candidate is ready for a full namespaced AVX2 inverse. The answer is **not yet**: its complete scalar semantics and signed-range tail now close, but its whole-kernel 16-YMM allocation, linked constant traffic, and Decap cycles do not. Official GS and the caller-lazy implementation remain unchanged.

**Superseded physical replay:** the next [physical two-schedule gate](ntruplus768-true-twist-physical-schedule.md) fixes the selective-control root/scale mapping, verifies both sides on 101 inputs, and corrects the mixed stage-5 constant-profile count. The paragraphs below preserve this checkpoint's original evidence boundary; use the newer report for the current decision.

## What is now closed

The physical six `y³²` roots in Official leaf order are `[1886,1937,3091,2333,257,867]`. An independent six-root CRT matrix and the factored radix-3/trinomial tail agree on all six basis columns. The mixed radix-2 recipe carries a `1/4` scale, so its final scale is `R/48 = 213 (mod 3457)`, whose Montgomery residue is `3259` (centered signed word `-198`). The complete tail includes a full-vector `y³²` untwist **even in identity lanes**. Omitting that multiply would leave the raw-range proof unjustified.

The per-cell proof over the independently established BaseMulScale output intervals gives the following absolute bounds. These are conservative bounds, not measured cycle costs.

| Boundary | Signed absolute bound |
| --- | ---: |
| Mixed radix-2 output before `y³²` untwist | 29,708 |
| After mandatory untwist | 2,507 |
| Largest radix-3/trinomial pre-operation | 6,703 |
| Final coefficient output | 1,747 |

On 101 outputs of compiled Official BaseMulScale, the candidate's machine-word scalar result matches the linked Official inverse modulo `q`, and the subsequent linked `crepmod3` result is byte-exact. The tail's exact ownership is also closed: eight packets each hold four consecutive `k` values with quartic degrees in AoS lane order. The inherited CT routes already create that geometry; the tail stores to six coefficient-vector slots without a further transpose. This is ownership replay, **not** a linked whole-inverse def/use or spill proof.

An isolated stage-6 mixed AVX2 butterfly passed 100,025 vector tests. Its linked probe is 134 bytes, uses YMM0–YMM8, and has no spill, call, or `vzeroupper`. That demonstrates the mixed plain/half arithmetic can be expressed in AVX2; it does not demonstrate a complete kernel fits in 16 YMM or wins cycles.

## What the AVX2 geometry actually costs

The earlier 480 versus 1,536 **scalar** modular-half count cannot be read as a vector instruction reduction. Stage 6 has mixed half/plain lanes in each of its 24 vector pairs, requiring per-lane selection. Stage 2 has 24 full-vector modular-half pairs. Stage 5 is mixed in semantic scale but can use one vector Montgomery operation with lane-specific constants.

| Radix-2 stage | Plain CT vector Montgomery | Mixed candidate | Change |
| --- | ---: | ---: | ---: |
| 6 | 0 | 0 | 0 |
| 5 | 12 | 24 | +12 |
| 4 | 18 | 24 | +6 |
| 3 | 24 | 24 | 0 |
| 2 | 24 | 24 | 0 |
| **Total** | **78** | **96** | **+18** |

The factored top tail conservatively contains another 168 vector Montgomery operations: 48 mandatory `y³²` untwists, 48 radix-3 operations and 72 level-0/final operations. That gives **264 modeled vector Montgomery operations** for this realization, plus 16 top-tail Barrett vectors and the modular-half work. The tail schedule currently materializes the radix-3/level-0 boundary (96 vector loads and 96 stores); these are explicit conservative costs, not a claim that no better schedule exists. This checkpoint's **2→10** stage-5 profile estimate used the incorrect numerical-minimum root orientation; the corrected physical count is **2→2**. Scalar constant-residue counts still are not load-uop estimates.

These totals are not directly comparable to `stage5reuse`'s 222 chains/32 Barrett as a cycle prediction: the latter uses a different gauge and linked schedule. They do show that the mixed recipe has **not** yet demonstrated a machine-work deletion merely by reducing the number of scalar modular-half butterflies. The code/constant footprint and critical path still require a whole linked object.

As a range-cost counterpoint, a greedy *whole-vector* Barrett screen on the plain true-twist CT topology uses 24 vector repairs (12 on stage-4 inputs and 12 on stage-3 inputs) and bounds its final radix-2 output by 24,856, followed by the mandatory untwist bound of 2,336. At this checkpoint, a naive top-tail replay with `R/192` had 21 residue mismatches against the linked Official inverse on the canonical `c=3449,f=3349` witness (first at coefficient 4: `0` versus `-865`). The next gate shows that the problem was the numerical-minimum `ξ/ζ` choice rather than the repair topology; the repaired physical replay passes 101 cases. No Decap cycles exist for either realization.

The Montgomery word model was corrected to use a **centered 16-bit constant word** consistently with the bound model. The previous absolute encoded word and the interval routine used different representatives. The corrected correlated/mixed checks still pass, but their regenerated result hashes supersede the earlier exploratory JSONs.

## Decision

Do **not** promote the mixed-gauge schedule to full inverse ASM or claim a performance win in this gate. It passes semantic and range closure, plus a local linked AVX2 feasibility probe; it does not pass full 16-YMM allocation, constant-traffic, or complete Decap pricing. The 264-operation modeled Montgomery total, mixed-lane selection, and new constant profiles give concrete reasons to demand that proof before implementation.

The next discriminating work is to repair the exact physical owner/scale replay of the **selective-repair control**, then lower both candidates to complete 16-YMM def/use and constant-operand schedules. Only if the mixed realization offers a concrete dependency or movement advantage over that valid control should one full namespaced ASM be written and priced at `inverse → crepmod3 → Decap`. A failure of this particular mixed realization does not reject all CT butterflies or Forward/inverse twisted-tower pairings.

Reproduce from `ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001`:

```sh
python3 tools/research_mixed_gauge_full_tail.py
python3 tools/research_mixed_gauge_vector_schedule.py
python3 tools/research_true_twist_selective_repair.py
python3 tools/audit_mixed_qhalf_probe.py
```

The corresponding machine-readable artifacts are in `results/yang-true-y-twist-mixed-*` and `results/yang-true-y-twist-selective-repair-20260923.json`. No full inverse ASM, Native SUPERCOP measurement, or clean production change was made.

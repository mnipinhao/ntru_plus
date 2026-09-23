# NTRU+768 true-twist CT: correlated range and butterfly research

This is a research gate on `avx2-official-opt`, not a linked inverse candidate or a cycle result. It follows the [existing-multiply repair gate](ntruplus768-defuse-repair-gate.md). The true `y=x^4` tower has already passed factor, scale and materialized-Official-ABI mapping tests; its no-repair AVX2 inverse range was still open.

## The old proof failure is a real arithmetic hazard

The independently compiled Official `poly_basemul_scale` gives a reproducible witness. Set every canonical decoded `c` coefficient to 3449 and every canonical decoded `f` coefficient to 3349. All 192 degree-3 output cells are raw 7596. On the identity-twiddle path of the proposed unrepaired CT inverse, the size-2, size-4 and size-8 sums are 15192, 30384 and 60768. A signed 16-bit `vpaddw` at size 8 instead gives −4768; the difference is 65536, which is not divisible by 3457. Thus the residue is corrupted. This witness is in the decoder's canonical domain, though it is not claimed to be an honestly generated KEM pair.

The script checks the actual compiled BaseMulScale against its source replay before using the witness. It also proves that CT butterfly operands at each node have disjoint quartic-leaf supports (480 checks). That does **not** prove their raw ranges are independent or rule out all tighter correlation proofs. It does show why one cannot simply assume the two operands are negatively correlated. More importantly, the concrete witness already rules out this particular no-repair CT schedule for the accepted input contract.

## A redesigned modular-half butterfly

For a signed i16 `a` and an already-twiddled signed i16 `t`, define the desired outputs as `(a+t)/2` and `(a−t)/2` in `F_3457`. An unsigned `vpavgw` after xor-biasing by `0x8000` computes signed `ceil((a±t)/2)` without first doing an overflowing add. Both signs have the same parity bit `(a xor t)&1`. When odd, add 1728, since `1728 ≡ −1/2 (mod 3457)`. The two outputs can share parity work. A signed floor-average realization using `and/xor/srai` was also checked.

The executable word model matched an independent scalar CT/CRT oracle on 101 actual BaseMulScale inputs × 24 cohort/degree blocks. A local AVX2 probe passed 100,081 vector tests; the two compiler realizations each have 23 disassembly instruction rows per isolated call (including entry/constant setup and two stores, excluding `ret`), use YMM0–7, and have no stack spill or `vzeroupper`. This is **not** the cost of an integrated butterfly: constants, twiddles, routing and register reuse may change after inlining.

With all five radix-2 levels halved, conservative uniform signed bounds are 9372, 11100, 12828, 14556 and 16284 after sizes 2, 4, 8, 16 and 32; the final `y^32` untwist is bounded by 2159. These establish the radix-2 block only. Radix-3, trinomial level-0, final normalization, full 16-YMM allocation and exact output range still require a complete schedule.

Halving changes scale. The prior algebraic final factor `R/192 = 2646 (mod q)` becomes `R/12 = 852` if four levels are halved, or `R/6 = 1704` if all five are halved. The corresponding Montgomery words are 2665 and 1873, versus 1679 originally. These are scale anchors, **not** approved replacement constants for an unchanged tail; the whole tail must be regenerated and checked.

## How much halving is needed in this restricted family?

An exhaustive 32-subset search over the five uniform CT levels, using the 768 proved BaseMulScale cell intervals, found that no choice with at most three halved levels closes all signed-i16 bounds without other repair. All five four-level choices and the five-level choice close the screened radix-2 block. Four levels imply 1536 scalar butterfly operations, ideally 96 16-lane groups, with a deferred factor of two. These are **structural lower-accounting units**, not linked AVX2 instructions or cycle predictions. The result is restricted to uniform stage choices, this interval proof and no alternative repair; mixed cell-level schedules or a different butterfly remain possible.

| Mechanism | Result | Remaining cost/problem |
| --- | --- | --- |
| Refine current no-repair CT bounds | Concrete size-8 overflow | Cannot validate this schedule by a tighter bound alone |
| Existing twiddle moved before hazard | All 24 first hazards have identity twiddle | No existing machine multiplication to move at those nodes |
| Modular-half CT butterfly | Correct local arithmetic and safe radix-2 bound | At least four uniform levels, new parity/bias work, scale/tail rewrite |
| Local AVX2 probe | Correct, spill-free isolated butterfly | Full instruction schedule and complete Decap cycles unknown |

The next useful gate is therefore **selective repair versus modular-half co-design**, not immediate full inverse ASM. It should search cell/stage-specific repair and one- or two-level redesigned butterfly schedules, close the top radix-3/trinomial tail and its scale, then replay def/use and constants within 16 YMM. Only a complete schedule with a concrete cost mechanism warrants a namespaced inverse implementation and Decap timing. Keygen and Encap remain on the existing caller-lazy control in this gate; no new Native or production claim follows.

The later [twiddle-half absorption experiment](ntruplus768-twiddle-half-absorption.md)
constructs one such mixed-gauge schedule. It absorbs the lower-child half-scale
into existing nonidentity twiddles at two levels, while explicitly paying for
identity-path multiplications. This reduces local modular-half butterflies,
but its linked AVX2 and full-tail costs remain open.

## Reproduce

From `ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_001`:

```sh
python3 tools/research_correlated_ct_butterfly.py
python3 tools/search_ct_half_stages.py
python3 tools/audit_qhalf_probe.py
```

Machine-readable evidence is in `results/yang-true-y-twist-{correlated-butterfly,half-stage-search,qhalf-probe}-20260923.json`. The probe source is `tests/test_qhalf_butterfly.c`. Each artifact records source hashes and its evidence limit.

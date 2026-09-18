# NTRU+1152 Good-Thomas campaign roadmap

Persistent work ledger for the NTRU+1152 AArch64 Good-Thomas port. Update it
after every gate. A gate may be removed only with a recorded reason; failed
attempts move to `Dropped` rather than disappearing.

**Branch:** `neon-1152`, created in place from `neon-864`, no worktree.
**Port source:** `ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864`
(17,095 lines, 58 gates, currently beating selected Official).
**Performance baseline:** SUPERCOP official 1152,
`crypto_kem/ntruplus1152/aarch64`. Prior Pi 5 data:
`bench/results/supercop-pi5-official-main-20260728/data-ntruplus1152-20260728`.
**Milestone 1 scope:** a complete, runnable, KAT-passing 1152 GT KEM. No
performance optimization.

Status meanings, matching `NTRU+864/docs/OPTIMIZATION-ROADMAP.md`:

- `Active`: current gate.
- `Next`: ordered work after the active gate.
- `Deferred`: retained, not on the immediate critical path.
- `Done`: passed all required gates.
- `Dropped`: rejected, with evidence and a reopen condition.

## Ordered work

| ID | Status | Work | Completion gate |
|---|---|---|---|
| G0 | Done | Create `neon-1152`; establish campaign ledger | Branch exists at a recorded base; this file records the structural conclusions and the decisions ledger |
| G1 | Done | Ring profile, structural proof, and the declared Python oracle | 100/100 KAT cases reproduced byte-for-byte; 10/10 structural checks; evidence in `gt1152-p01-ring-profile/` |
| G2 | Done — ordered early | Degree-4 range and scale bound chain | Model self-validates against 864's documented 2497; zero int32/int16 violations over four input domains; D7 resolved; `ring-profile.yml` ranges filled. Evidence in `gt1152-p02-degree4-bounds/`. **Note:** these bounds constrain the Tier 2/3 assembly kernels, none of which exist yet, so the gate delivered no progress toward a runnable KEM. Kept because the work is correct and G4–G6 need it; not repeated |
| G3a | Done | Measure the GT transform-domain layout | 864 GT forward built and run on the local arm64 host; permutation is a bijection, exact mod q with no scale factor, stable over 6 random inputs, and independently confirmed by `base_tables.h`. 1152 layout derived. Evidence in `gt1152-p03-gt-layout/` |
| G3b | Done | Forward NTT eight-bank port (`ntt_top.S`, `ntt_tail.S`, `ntt9.S`, `ntt.S`) | 24 cases x 1152 coefficients match the G1 oracle under the predicted layout, which simultaneously confirms the transform, the layout formula and the permutation; forward output bound measured and fed back into G2. Evidence in `gt1152-p04-forward-8bank/` |
| G4 | Done | Degree-4 `basemul` / `basemul_add` (NEON intrinsics C) | 14 cases x 6 modes x 1152 coefficients match the G1 oracle, including every aliasing pattern; NTRU+864's Barrett reciprocal re-proved for the degree-4 accumulator union. Evidence in `gt1152-p05-basemul/` |
| G5 | Done | Degree-4 `basemul_rinv` and BaseInv | Matches the G1 oracle over 10 cases with exact aliasing; D7 normalization applied and measured; reject path returns 1 with a zeroed output. Evidence in `gt1152-p06-baseinv/`. **Owed:** a targeted per-leaf failure suite equivalent to 864's 808 cases |
| G6a | Done | Establish whether the inverse Slothy artifacts can be remapped | NTRU+864's chain validated end to end on the local host; per-call accounting settles D6; immediate maps derived for the two kernels that transfer. Evidence in `gt1152-p07-inverse/` |
| G6b | Done | Port the inverse NTT | Full decapsulation chain `forward -> basemul_rinv -> invntt_ternary` equals `crepmod3(schoolbook)` over 16 cases x 1152 coefficients. Evidence in `gt1152-p08-inverse-port/` |
| G7 | Done | Pack / unpack for the degree-4 layout | 7 checks: exact wire bytes over every int16 extreme, round trip, 3456-case canonical rejection sweep, constant-time compare. Evidence in `gt1152-p09-pack/` |
| G8a | Done | KEM assembly and KAT, local | **KAT reproduced byte for byte** (sha256 `2ddfc810c4...64c3`) plus 64 KEM round trips with tampered rejection, on macOS/arm64. Evidence in `gt1152-p10-kem/` |
| G8b | Done | Release gates on Linux/AArch64 | On Pi 5 Cortex-A76 / GCC 14.2.0: KAT byte-identical, 64 KEM round trips, **288/288 per-leaf non-invertibility**, 13,824 canonical cases, zeroization, **8/8 ABI sentinels**. Evidence in `gt1152-p10-kem/pi-results.json`. Manifest and SUPERCOP export move to G9 |
| G9 | Done | SUPERCOP packaging and first honest measurement | SUPERCOP validated the KEM byte contract against its built-in `ntruplus1152` checksum; GT 142,741 vs official 111,341 cycles, +28.2%. Evidence in `gt1152-p10-kem/supercop-results.json`. **Superseded by P20** |
| P11 | Done | Component profile: where the 28% goes | PMU attribution on Pi 5. **Polynomial multiplication is at parity (+787); serialization is +30,750.** Evidence in `gt1152-p11-profile/` |
| P12 | Done — *recorded late* | NEON codec: replace the scalar gather | Lane-indexed LD4/ST4 per leaf. Serialize went from +30,750 to +10,909. Evidence in `gt1152-p12-codec-neon/` |
| P13 | Done — *recorded late* | NEON sampling leaves | Broadcast-the-byte against `vtst`, avoiding an 8-way bit-plane interleave. sample/misc went from +6,500 to +565. Evidence in `gt1152-p13-sample-neon/` |
| P14 | Done — Option A rejected | Should the transform output natural order? | Measured: net -1,612 cycles (0.85%) for a major `ntt9.S` restructure. Codec fusion recovers ~5,066 with no contract change. Evidence in `gt1152-p14-layout-study/` |
| P16 | Done — closed | Is there headroom left in `ntt9.S`? | **No.** It is multiply-throughput bound at 93% of the A76 floor (484 vs 450 cycles/bank). Slothy is worth at most 0.85% of the KEM. Evidence in `gt1152-p16-ntt9-study/` |
| P15 | Done — rejected | Fuse the codec's passes with byte-granular lane stores | Measured 12,129 cycles worse: `vst3_lane_u8` doubles 8 halfword lane stores into 16 byte lane stores. Evidence in `gt1152-p15-codec-fused/` |
| P17 | Done | Why did 864 beat the official pre-hash and 1152 does not? | **No structural penalty.** At 864's pre-hash per-category ratios 1152 would stand at -3.68% against its measured +8.76%; 64.9% of the shortfall is the serializer. Evidence in `gt1152-p17-vs-864-parity/` |
| P18 | Done | Rewrite the serializer with the permutation in registers, 864's way | **Serialize +10,909 -> +911; whole KEM +7.9% -> +1.8%; encaps now -1.0%, faster than the official.** Byte-identical to P12 on all four entry points; all 7 oracle checks and every package gate pass. Evidence in `gt1152-p18-codec-registers/` |
| P20 | Done | Fresh SUPERCOP measurement, superseding G9 | **GT 112,107 vs official 111,351, +0.68%** under SUPERCOP's own measurement, down from G9's +28.2%; encaps **-1.77%**. Agrees with the profiler to within 0.2pp on every operation. Evidence in `gt1152-p20-supercop-fresh/` |
| P19 | Done — asm rejected | Should the serializer be hand-written in assembly? | **No.** Measured issue floor puts the codec at 90-100%; scheduling is worth under 10%. Cutting instructions instead took **serialize +911 -> -1,034 and the KEM +1.8% -> +0.65%**, encaps -1.97%. Evidence in `gt1152-p19-serializer-floor/` |
| P21 | Done — analysis | Where is the remaining deficit, per operation? | **Only decaps loses.** keygen +454 (all of it `baseinv`, which is keygen-only), encaps -1,271, decaps +2,085. The C `invntt16_tail` measures **1,469 cycles** alone, against 864's 592-instruction assembly; `poly_sotp_decode` is 2.6x the official because it does 144 horizontal reductions where the official uses a bit-transpose. Evidence in `gt1152-p21-decaps-targets/` |
| P22 | Done | Port `invntt16_tail` from C to assembly | **311 cycles against the C version's 1,469, 4.7x.** `inverse` +1,134 -> **-14**; decaps +3.11% -> +0.90%; **whole KEM +0.65% -> +0.00%**. 512,000 outputs agree mod q with the C contract. Evidence in `gt1152-p22-tail-asm/` |
| P23 | Done | `poly_sotp_decode` without horizontal reductions | **484 cycles against P13's 1,332, and below the official's 508.** +835 -> **-17**; **decaps +0.90% -> -0.53%**; **KEM +0.00% -> -0.44%**. 20,000 differential trials against the reference. Evidence in `gt1152-p23-sotp-decode/` |
| P24 | Done | `poly_basemul_rinv`: why it trailed | **Not the arithmetic — the official issues identical multiplies.** D7's Barrett cost 16 VEC0 cycles a group; a conditional subtract honours D7 exactly with no multiply. 3,378 -> **3,054**, +827 -> **+634**. What remains is a real scheduling gap (M2-2). Evidence in `gt1152-p24-basemul-rinv/` |
| P25 | Done — analysis | Is `baseinv` next, and does `inverse` still have headroom? | **`baseinv` yes, two separate problems**: 1,928 cycles of strictly serial batch inversion (needs 864's 12x3 ILP split) plus both parallel phases at ~78% of their multiply floor. **`inverse` is level with the official** (6,293 vs 6,292) with ~1,200 cycles of absolute headroom and no competitive gap. Evidence in `gt1152-p25-baseinv-inverse-floors/` |
| P26 | Done | `baseinv`: split the batch inversion into three chains | Serial phase **1,928 -> 1,191**; `poly_baseinv` **+2,397 -> +850**; **keygen +1.09% -> -1.65%**, **KEM -0.53% -> -1.55%**. **All three operations now beat the official.** Evidence in `gt1152-p26-baseinv-ilp/` |
| P27 | Done — **first SLOTHY run of this campaign** | M2-2: schedule `basemul_rinv` | **3,054 -> 2,744 cycles**; `poly_basemul_rinv` +634 -> **+232**; decaps -0.86% -> **-1.68%**; KEM -1.55% -> **-1.79%**. Byte-identical to the C oracle over 4,000 trials. Evidence in `gt1152-p27-slothy-basemul-rinv/` and `dev/` |
| P28 | Done — second target not justified | Does a per-microarchitecture schedule pay? | **A76: scheduling worth ~10%, target choice irrelevant** (2,744 vs 2,739). **M2 Pro: all three identical** at ~278 ns. SLOTHY's M1 model predicts 81 cycles/group where Apple silicon measures 25. Evidence in `gt1152-p28-cross-target/` |
| P29 | Done | SUPERCOP after the assembly and scheduling work | **GT 109,446 vs official 111,401, -1.75%** — GT is now faster under SUPERCOP's own measurement, from +28.2% at G9 and +0.68% at P20. Per operation keygen **-3.13%**, enc **-1.87%**, dec **-1.75%**; the q1 sum is -2.26% against the profiler's -2.29%. Evidence in `gt1152-p29-supercop-final/` |
| P30 | Done | Survey `poly_frombytes`, the last losing component | **P19's "structural, ~100% of floor" was wrong on both counts.** It was at 90%, and one of four per-lane operations was avoidable: reading each block as eight 16-bit windows instead of four 24-bit ones lets one `ushl` with a per-lane count replace `ushr` + `uzp1`. **723 -> 645; +895 -> +599; KEM -2.29% -> -2.51%.** Evidence in `gt1152-p30-frombytes-survey/` |
| P31 | Done | Was D7's normalization ever needed? | **No.** Its 2752 bound assumed inputs on [0,4095], but the only caller aborts unless both `poly_frombytes` decode, so inputs are canonical and the bound is 2458 < 2497. Removing it: `poly_basemul_rinv` **+227 -> -142**, decaps -2.21% -> **-2.75%**, KEM **-2.69%**. Evidence in `gt1152-p31-basemul-rinv-bound/` |
| P32 | Done | M2-1: fused fixed-size SHAKE256 for hash_f and hash_g | **hash +998 -> -21,082.** `hash_f` 17,754 -> 11,947 and `hash_g` 20,339 -> 13,765 per call. **keygen -11.36%, encaps -20.57%, decaps -13.96%, KEM -15.25%** — within a percentage point of NTRU+864 on every operation. Evidence in `gt1152-p32-hash-fused/` |
| P33 | Done | SUPERCOP after the hash campaign | **GT 92,079 vs official 111,403, -17.35%.** Per operation keygen -12.12%, enc **-20.39%**, dec -13.77%; q1 sum -15.53% against the profiler's -15.25%. Within a percentage point of NTRU+864 on every operation. Evidence in `gt1152-p33-supercop-hash/` |
| P34 | Done | Why did the forward's static multiply advantage not cash out? | **It did. The 25.4% static figure was my arithmetic error** -- wrong file and wrong loop bounds. True static advantage **9.96%** (1,880 vs 2,088 multiply ops), measured **9.04%**, and the 16-cycle residual is accounted for: both sides sit at the same distance above their own issue floor (GT 86.4%, official 87.3%). **The forward is closed**: `ntt_top` 95.7% of floor, `ntt9` 92.9%, total headroom ~294 of 4,348 cycles per call. Evidence in `gt1152-p34-forward-attribution/` |
| M1 | **Complete** | Milestone 1: a runnable, KAT-passing, SUPERCOP-validated NTRU+1152 GT KEM | All correctness gates pass on Pi 5; performance is measured and honest, not yet competitive |
| M2-1 | **Done** (P32) | Hash fusion: fixed-size SHAKE256 1728 -> 288/32 | 4,000-input differential against the generic sponge, zero mismatches; KEM -2.69% -> **-15.25%** |
| M2-2 | **Done for `basemul_rinv`** (P27) | First Slothy gate: degree-4 `basemul_rinv` | 3,054 -> 2,744, 310 of the predicted ~500 taken. `baseinv`'s two loops remain |

## Decisions ledger

| # | Decision | Rationale | Recorded |
|---|---|---|---|
| D1 | Branch `neon-1152` in place, no worktree | 864 sources travel with the branch, so a second checkout buys nothing; the Pi 5 is a single shared resource so parallel benchmarking is impossible anyway. Repo convention reserves `.worktrees/` for same-champion gate fan-out | 2026-09-17 |
| D2 | Work lives in repo-root `experiments/gt1152-pNN-*` | Mirrors the newest 864 convention (p41–p58). Deliberate deviation from `parameter-profiles.md`, which suggests the `Experiment/NTRU+1152/` lane | 2026-09-17 |
| D3 | Performance baseline is SUPERCOP official 1152 | Matches how 864's P58 claim is stated; the only basis valid for an external claim | 2026-09-17 |
| D4 | Milestone 1 uses no Slothy at all | The reused inverse cores keep their 864 schedule (see D6); new degree-4 arithmetic is written as NEON intrinsics C, exactly as 864's production `base.c` is | 2026-09-17 |
| D5 | Pack/unpack starts from the simple stock-shaped codec | 864's 7,751 lines of routing exist only to work around degree-3 lane misalignment, which 1152 does not have. G9's profile decides whether more is needed | 2026-09-17 |
| D6 | **Corrected by G6.** Immediate remap works for `packed_i9` and `invntt16_asm` only. `invntt16_tail_asm` must grow from 96 to 128 outputs | Static `strh` counts: 864 is 6x128 + 96 = 864; 1152 needs 8x128 + 128 = 1152. The first two kernels are driven by a per-component loop so their per-call work is invariant; the tail is called once and covers all components, so its work grows with the component count. The original reasoning (component count and total both grow 4/3) only applies to the per-component kernels. Mitigating: the tail's vector arithmetic is already eight-lane and matches the main kernel's (309 vs 311 ops), so the two lanes 864 leaves as padding already hold correct results - the gap is exactly 32 umov/strh pairs | 2026-09-17, corrected 2026-09-17 |
| D7 | **Withdrawn by P31.** The normalization it added was never needed: its 2752 output bound assumed inputs on [0,4095], but the only caller guarantees canonical inputs, for which the bound is 2458, inside the 2497 contract | **Resolved: add one `barrett_reduce` at `basemul_rinv` output.** 1152's output is ≤ 2752 against 864's ≤ 2497 inverse input contract (ratio 1.102); barrett brings it to `[−1729,1728]`, tighter than 2497 | The 864 inverse chain (I9 2617, I16 21397, ternary 5143) then holds a fortiori instead of needing re-derivation. Sound because the inverse operates on the 288-point transform — leaf degree changes bank and component counts, but every coefficient passes the same butterfly network, so its bound chain depends only on input magnitude, not leaf degree. Cost ~3–4 instructions per vector over 36 tiles, Decaps-only. Re-deriving at 2752 is deferred to M2 | 2026-09-17 |

## Structural findings that the port rests on

All verified mechanically in `gt1152-p01-ring-profile/proof.py`.

| | NTRU+864 | NTRU+1152 |
|---|---|---|
| Ring | `Z_q[X]/(X⁸⁶⁴−X⁴³²+1)` | `Z_q[X]/(X¹¹⁵²−X⁵⁷⁶+1)` |
| q | 3457 | 3457 |
| Level 0 | α/β CRT on `y²−y+1`, y = X⁴³² | same, y = X⁵⁷⁶ |
| Transform | Good-Thomas 9×16 = 144 per half | **the same** 9×16 = 144 |
| Leaf | degree 3 | degree 4 |
| Leaves | 288 | 288 |
| Leaf zeta window | `zetas[144..287]` ± | **identical** |

- α = 723, β = 2735, α+β ≡ 1, ord(α) = 6. All n-independent.
- `z¹⁴⁴ − α` is literally the same polynomial for both (z = X³ vs z = X⁴), so
  the 288 leaf roots coincide.
- **`ord(z) = 864` for both.** That 864 is `144 × ord(α) = 144 × 6`, not the
  parameter n. Do not rescale twiddles; there is nothing to rescale. A
  generator searching for an order-n root fails outright at n = 1152.
- `ntt9.S`'s `.Lntt16_top{0,1}` / `.Lntt9_top{0,1}` are selected by the α/β
  half only, never by component, so 3 branches → 4 branches needs zero new
  twiddle data — only two more bank invocations.
- 1152's basemul is a 16-product schoolbook against 864's 9-product, so base
  multiplication is where 1152 gets harder.
- **GT output layout (G3a, measured):**
  `864: index = top*432 + row*48 + halfcol*24 + component*8 + lane`
  `1152: index = top*576 + row*64 + halfcol*32 + component*8 + lane`
  The leaf ordering is identical — it is fixed by `.Lntt_one_bank` and the 9×16
  enumeration, neither of which depends on component count or leaf degree.
  Therefore **`base_tables.h` copies verbatim**, verified.
- **Correction to an earlier claim.** The roadmap previously said 1152's
  degree-4 leaves make the 864 pack complexity "largely disappear", citing the
  stock lanes. That evidence is about the *stock* layout, which has no GT
  permutation, so it does not carry. Measured instead: one GT vector's 8 leaves
  land at natural-order starts `0,48,96,…,336` for 864 and `0,64,128,…,448` for
  1152 — **the scatter is structurally identical**, only multiplied by leaf
  degree. What genuinely improves is granularity: 8 bytes per leaf is one
  `d`-register store and 6 whole bytes packed, against 864's 6 bytes stored and
  4.5 bytes packed, which straddle boundaries and force ST3 and TBL routing.
  Expect the 1152 pack to be simpler, not trivial; size it from a real design.

## Which 864 files are Slothy artifacts

Decides whether a gate is a hand edit or a solver re-run. Scanned for
`slothy_start` / `Expected cycles` markers.

**Solver output — never hand-edit:** `pack_full.S`, `pack_small.S`,
`pack_compare.S` (37 windows each); `inverse16.S`, `inverse16_tail.S` (3 each);
`inverse9.S`, `baseinv_prefix.S`, `baseinv_recover.S`, `basemul_rinv.S`,
`crepmod3_raw.S` (1 each).

**Hand-written:** `ntt_top.S`, `ntt_tail.S`, **`ntt9.S`**, `inverse.S`,
`baseinv_num.S`, `baseinv_inverse.S`, `baseinv_finish.S`, `cbd.S`, `add.S`,
`crepmod3.S`, `keccakf1600.S`, `support_abi.S`, `ntt.S`.

The entire forward NTT is hand-written, so G3 is a direct edit.

## Log

### 2026-09-17

- **G0 done.** Created `neon-1152` from `neon-864` at `6204d70d`. Working tree
  was clean; four uncommitted 864 SUPERCOP-export changes seen mid-session
  turned out to be the user's own work, committed by them as `2ec451bf`
  (P58 formal SUPERCOP). No stash was needed. Later merged
  `origin/neon-864` (`0d53a61d`, Keccak notices in the SUPERCOP export) into
  `neon-1152` as a fast-forward; G1 re-verified clean afterwards.

- **G1 done.** `experiments/gt1152-p01-ring-profile/`, `make check`.

  - **KAT: 100/100 cases reproduced byte-for-byte** against
    `KAT/NTRU+1152/PQCkemKAT_3488.rsp` (sha256 `2ddfc810c4…64c3`) — pk, sk, ct,
    ss and the decapsulation status. Runtime ~6 s.
  - `ntruplus1152.py` is the **declared oracle**. It parses its zeta table from
    `Reference_Implementation/NTRU+1152/ntt.c` rather than embedding a copy, and
    reproduces C int16 wrap and arithmetic-shift semantics, which
    `barrett_reduce` and `crepmod3` depend on.
  - `nistkat.py` implements AES-256 and CTR_DRBG so the transcript needs no C
    toolchain; it reproduces the FIPS-197 C.3 AES-256 vector.
  - Supporting checks: `ntt`→`invntt` is the identity on ternary inputs;
    `invntt(basemul(ntt(a),ntt(b)))` agrees with an independent schoolbook
    multiply in `Z_q[x]/(x¹¹⁵²−x⁵⁷⁶+1)`.
  - **Negative control:** perturbing one zeta by 1 breaks ct, ss and the
    decapsulation status, so the comparison is not vacuous.
  - **Proof: 10/10 structural checks** → `proof-report.json`. Includes the
    finding that both parameter sets index the *same* `zetas[144..287]` window
    with the same ± pair, and that all eight reference constants
    (`R`, `RINV`, `RSQ`, `QINV`, `OMEGA`, `ZMINUSZ5INV`, `NINV`, `2NINV`)
    are identical between the two `ntt.c` files.

  Two corrections made during the gate:

  - The KAT failure report truncated hex to 64 characters, so a 1728- or
    3488-byte mismatch could display as identical. Now reports the first
    differing byte offset.
  - The `ntt9.S` twiddle-table audit initially assumed whole-row
    twiddle/Shoup alternation. `.Lntt16_top0` has 168 values in 21 rows and
    mixes two packing styles (whole-row pairs in rows 1–12, lane-interleaved
    pairs in rows 13–21). The audit was rewritten to be layout-agnostic: every
    non-zero value must be either a twiddle whose order divides 864, or the
    exact `round(t·2¹⁵/q)` constant of such a twiddle.

  **Scope limit recorded in the gate itself:** the table audit proves the
  tables' *contents* are functions of `(q, z¹⁴⁴−α)` alone. It does not
  reverse-engineer `.Lntt_one_bank` to reconstruct the table *ordering* — the
  port copies that body byte-identically, so ordering is fixed by the algorithm
  rather than by n.

- **G2 done.** `experiments/gt1152-p02-degree4-bounds/`, `make check`.

  - `bounds.py` models `montgomery_reduce` exactly (worst case over the int16
    `t`, floor shift) rather than with the loose `|a|/2¹⁶ + q/2`. Leaf zeta
    interval taken from the real table: `[−1727, 1727]`.
  - **Method self-validated before use:** run at degree 3 over `[0,4095]²` the
    model gives 2496, against the 2497 documented in 864's `inverse.h`.
  - **Zero int32 overflows and zero int16 storage violations** over four input
    domains.

    | domain | `basemul_rinv` | `basemul` | `basemul_add` | `baseinv` |
    |---|---:|---:|---:|---:|
    | `frombytes²` `[0,4095]²` | **2752** | 1764 | 1768 | 1781 |
    | `reference_ntt` `[−1729,1729]²` | 1913 | 1754 | 1758 | 1777 |
    | `decaps_sub × frombytes` | 3184 | 1770 | 1774 | 1784 |
    | `gt864_lazy_forward` (comparison) | 3008 | 1769 | 1773 | 1782 |

    Only `basemul_rinv` carries the input magnitude through, because it stops at
    the R⁻¹ boundary by design; everything else is re-reduced by its final
    Montgomery rescale.
  - **D7 resolved** — see the decisions ledger. The campaign plan's earlier
    ~3008 estimate was computed over the wrong domain: `inverse.h` states the
    inputs are raw 12-bit `poly_frombytes` values, not forward-NTT outputs.
    3008 is in fact the `gt864_lazy_forward` row.
  - **`instrument.py` caught a gap in the analytic model.** It observed a
    `basemul` input of 5108, outside every domain listed in the first version.
    Source: `crypto_kem_dec` computes `poly_sub(c, m2)` with `c` from
    `poly_frombytes` and `m2 = ntt(crepmod3(...))`, giving `[−1729, 5824]`.
    `decaps_sub_x_frombytes` was added. This is why both halves are run: the
    model proves, the instrumentation catches what the model omitted.

  **Scope limit recorded in the gate:** the forward NTT output bound is an
  *input* to this model, not an output. G3 must feed the real eight-bank
  forward bound back into `bounds.py`.

- **Direction corrected.** After G2 the user pushed back: the gate derived bounds
  for kernels that do not exist, so it moved nothing toward a runnable KEM.
  A three-tier inventory was produced (Tier 1 package scaffolding, Tier 2 GT
  transform, Tier 3 fused optimizations) and the work returned to Tier 2.
  Recorded facts from that inventory: NTRU+864's `kem.c` is fully
  parameter-neutral (27 `NTRUPLUS_*` macros, zero bare size literals) and needs
  18 entry points; 12 already exist for 1152 in both reference C and stock NEON;
  of the 5 missing, 4 are 864 fusions with straightforward adapters and one —
  the checked `poly_frombytes` with canonical rejection — is a real security
  property the reference lacks.

- **G3a done.** `experiments/gt1152-p03-gt-layout/`, `make check`.

  - The local host is arm64, so the NTRU+864 GT forward was **built and run**
    rather than reverse-engineered. `.Lntt_one_bank` is 617 instructions of
    Slothy output; guessing its ordering was avoidable.
  - Measured 864 layout: `top*432 + row*48 + halfcol*24 + component*8 + lane`,
    read off `ntt9.S`'s 18 stores per bank (9 rows × 2 half-columns at a 48-byte
    stride) and confirmed against the running kernel.
  - The GT→reference leaf permutation is a bijection over all 288 leaves,
    **exact mod q with no scale factor**, and stable over 6 random inputs.
  - **Independent confirmation:** `base_tables.h`'s `basemul_zetas[36][8]` is
    exactly the reference leaf zetas reordered by this permutation. That table
    was written by the 864 campaign with no involvement from this probe.
  - 1152 layout derived: `top*576 + row*64 + halfcol*32 + component*8 + lane`,
    8 banks at 0,256,…,1792 bytes, tail at +2048, scratch 2304 bytes, store
    stride 128. `base_tables.h` transfers verbatim, verified.
  - The pack-complexity claim was measured and corrected — see the structural
    findings above.

  **Scope limit:** the 1152 layout is predicted, not measured. G3b must re-run
  the probe method against the real eight-bank forward and reproduce
  `perm864.txt`.

  **Caveat:** the 864 package targets Linux/AArch64; `ntt_tail.S` defines only
  `_ntt_tail_asm` under `__APPLE__` while `ntt.S` calls the unprefixed name.
  `darwin_shim.S` adds that alias for the probe only.

- **G3b done.** `experiments/gt1152-p04-forward-8bank/`, `make check`.

  - **24 cases x 1152 coefficients match the G1 declared oracle** under the
    layout predicted in G3a. One check establishes three things: the transform
    is correct, the predicted layout formula is what the kernel produces, and
    the GT leaf permutation equals the measured 864 one. Cases cover the
    `[-3,4]` contract extremes, deltas at 0/1/575/576/1151, 8 ternary and 8
    full-contract random inputs.
  - `ntt_tail.S`: same transpose network, 12 -> 16 stores. The register-to-bank
    mapping was not guessed -- `probe_tail.c` measured the 864 kernel first
    (`out[16*bank+t] = in[8*t+bank]`, banks 6 and 7 left untouched), then the
    1152 version was verified against that contract.
  - `ntt9.S` is **generated**; `generate_ntt9.py` emits only the 8-bank driver
    and asserts that `.Lntt_one_bank` and all four twiddle tables appear
    byte-identical to 864's in its output.
  - Where 1152 is genuinely simpler: four halfwords is one `LDR d`, so 864's
    three-part `s=8` tail load collapses to one instruction; and 2 tops x 4
    branches fills all eight lanes, so `MOVI` + six `INS` becomes two `MOV`.
    The `s=8` tail itself does not disappear -- it exists because 9 is odd.
    Also dropped: 864 dups constants into `v29`/`v31` and never uses them.

  **Correction to G2, found here.** G2 used `[-4577, 4577]` as the GT forward
  domain, labelled "NTRU+864 lazy forward". 4577 is not a forward bound -- it is
  the raw ternary-consumer limit in 864's *inverse* chain
  (`2497/2617/21397/4577`). Measured by running both kernels over the `[-3,4]`
  contract: **864 reaches 15951, 1152 reaches 14607**, over three times larger.
  G2 now reads the measured value from `forward-bound.json`.

  That correction produced a quantified headroom result: degree-4 `basemul`
  tolerates inputs up to **22551** against degree-3's **26039** (one more
  product in both the zeta fold and the final sum), so the measured forward
  output uses 71% of the budget -- a margin of only **1.41x**. Any future
  lazier forward spends from that margin.

  **Scope limit:** the forward bound is observed, not proved. A proof needs an
  interval model of `.Lntt_one_bank`'s 617 instructions, which no gate has
  built. What is argued is narrower: the core is byte-identical and sees the
  same input contract, so the range is the same -- and both were measured.

- **G4 done.** `experiments/gt1152-p05-basemul/`, `make check`.

  - **14 cases x 6 modes x 1152 coefficients match the G1 oracle.** Modes cover
    `basemul`, `basemul_add` and four aliasing patterns: output aliased with
    `a`, with `b`, with `c` in the add form, and `a` squared against itself.
    Operands are pushed through the real G3b GT forward first, so they are
    genuine transform-domain values. Observed output `[-1765, 1778]`.
  - Written as NEON intrinsics C following 864's `base.c`: wide int32
    accumulators kept to the end and reduced straight to R0, no R0 -> R^-1
    detour. Group stride 32 int16 against 864's 24; 36 groups either way,
    because both parameter sets have 288 leaves. `basemul_zetas` copied
    verbatim per G3a.
  - **NTRU+864's Barrett reciprocal 621199 re-proved for degree 4.**
    `621199 * 3457 = 2^31 + 1295`, so `|out| <= q/2 + |x|*1295/2^31`. The
    constant transfers across the whole int32 range; only the bound changes,
    from 864's documented 2911 to **2342** over the domain 1152 actually
    reaches. No new constant search was needed.
  - **A real constraint the check found:** `VMLS` computes `value - qhat*q` in
    int32, and `qhat*q` does *not* fit across all of int32 — at `x = -2^31` it
    is 2147484943. Bisected threshold: safe for `|x| <= 2147481919`, all but
    the last 1729 values. The widest reachable degree-4 accumulator is
    2034190404, inside with 113291515 to spare. Safe, but not unconditionally
    so: a lazier forward spends from this margin as well as from G2's 1.41x.

- **G5 done.** `experiments/gt1152-p06-baseinv/`, `make check`.

  - `baseinv` and `basemul_rinv` as NEON intrinsics C, matching the G1 oracle
    under the GT layout over 10 cases, each also run with exact `out == in`
    aliasing. 3 of the 10 inputs were genuinely non-invertible and returned 1
    with a fully zeroed output; an all-zero transform input does the same.
  - **Degree 4 is simpler than degree 3 here.** `X^4 - zeta` is a quadratic
    tower (u = X^2, u^2 = zeta), so inversion is two nested quadratic
    conjugations; degree 3 needs a cubic resultant. The `+,-,+,-` sign pattern
    on the four outputs *is* that conjugation, deferred to the final scaling.
  - **The scale trap was settled before writing C.** The batch inversion's
    running multiply is `fqmul`, which is Montgomery and carries `R^-i` into the
    prefix. Checked in Python against the oracle: the batch result is exactly
    elementwise `fqinv`, because the `R` powers cancel across prefix, inversion
    and walk-back; and separately, `fqinv(a) = a^-1` with no scale factor at
    all. Getting this wrong would have produced a uniformly scaled, entirely
    plausible-looking wrong answer.
  - **D7 applied and measured.** `basemul_rinv` stops one Montgomery stage
    before R0, so it carries the input magnitude through (G2: 2752 over the
    decapsulation domain, above 864's 2497 contract). The `barrett_reduce`
    brings it to `[-1729,1728]`, observed here as `[-1727,1728]`.
  - Phases mirror 864's (numerator, prefix, inverse, recover, finish) so
    assembly can be swapped in piece by piece. 864's 12-step x 3-chain split is
    an ILP optimization and is left to a later gate; this uses 36 sequential
    groups with one 8-lane inversion.

  **Owed:** a targeted per-leaf non-invertibility suite equivalent to NTRU+864's
  808-case failure/alias/wipe gate. G8 must not claim the failure path is
  covered without it.

- **G6a done.** `experiments/gt1152-p07-inverse/`, `make check`.

  - **NTRU+864's decapsulation arithmetic chain validated end to end on this
    host**: `forward -> basemul_rinv -> invntt_ternary` equals
    `crepmod3(schoolbook product)` over 6 random ternary cases. This pins the
    I/O contract before anything is remapped.
  - **D6 is wrong about the tail.** Static `strh` counts give
    `864 = 6x128 + 96` and `1152 = 8x128 + 128`, so `invntt16_tail_asm` must
    produce 128 outputs where 864 produces 96. Its instruction multiset cannot
    be preserved. `packed_i9` and `invntt16_asm` are unaffected - both are
    driven by a per-component loop, so their per-call work really is invariant.
  - **The damage is small.** The tail's vector arithmetic is already eight-lane
    and essentially identical to the main kernel's (309 vs 311 ops): NTRU+864
    computes all eight lanes and simply never stores two of them. The gap is
    exactly `128 - 96 = 32 = 2 padding lanes x 16 t`, in `umov`/`strh` pairs.
  - Immediate maps derived for the two kernels that do transfer:
    `inverse9.S` needs one change, `[x2, #96k] -> [x2, #128k]`, the
    Good-Thomas row stride; every other base uses 16-byte strides.
    `inverse16.S` has all 128 `strh` offsets as multiples of 6 (the branch is
    folded into the base pointer by the driver), so they scale by 8/6 exactly.
    `inverse16_tail.S` decomposes as `6m + 2b` with `b` in 0..2, and 1152 needs
    0..3 - which is exactly why its store count grows.

  **Decision taken (D8):** rewrite the tail in intrinsics C for M1, assembly
  still the target. Its structure was then measured rather than read.
  `invntt16_tail_asm` emits raw values (`crepmod3_raw.S` does the ternary step),
  so it is linear in its scratch input and recoverable by delta probes.
  Findings: each bank reaches 32 outputs and banks overlap completely, because
  the terminal does the alpha/beta inverse CRT; **the three branch maps are
  byte-for-byte identical**; every column has exactly 32 non-zero entries at
  output m indices that are all multiples of 9, the s=8 row. So the kernel is
  three copies of one *2 banks x 16 t -> 32 outputs* map, and **1152 is the same
  map run four times**. The map carries over unchanged because the 16-point
  inverse and the CRT are leaf-degree independent and n/d = 288 for both. That
  turns the rewrite from 1205 lines of Slothy output into a measured 32x32 map
  per branch. Cost stated honestly: 1024 multiplies x 4 branches against 589
  assembly instructions - correct, directly derived, and materially slower.

- **G6b done.** `experiments/gt1152-p08-inverse-port/`, `make check`.

  - **The whole NTRU+1152 decapsulation arithmetic chain runs**:
    `forward -> basemul_rinv -> invntt_ternary` equals
    `crepmod3(schoolbook product)` over 16 cases x 1152 coefficients, exactly,
    against a model sharing no code with any of it.
  - `inverse9.S` (8 offsets), `inverse16.S` (127 offsets) and `crepmod3_raw.S`
    (loop 27 -> 36) are generated remaps with the instruction multiset asserted
    unchanged. `inverse_ntt.S` is generated from 864's driver under 13 declared
    rules. The driver stays assembly because `packed_i9` and `invntt16_asm`
    clobber v8-v15; a C driver would violate AAPCS64.
  - **Slothy annotations stripped, not carried over.** They describe the
    schedule produced for 864; no solver ran for 1152. A first version of the
    generator silently rewrote offsets inside those comments as well (256 strh
    lines: 128 real, 128 commented) - stripping removes the problem instead of
    papering over it.
  - **The C tail came from measurement, not from reading solver output.** The
    kernel emits raw values so it is linear; 128 delta probes recover it, and
    superposition was checked to hold mod q on random inputs (not bit-exact,
    because lazy reduction picks different representatives - congruence is what
    the contract asks). Cost: 4096 multiply-accumulates against 589 assembly
    instructions. Assembly stays the target.

- **G7 done.** `experiments/gt1152-p09-pack/`, `make check`. Seven checks:
  exact wire bytes over 17 cases including every int16 extreme and the measured
  Forward bound; Small agreeing with Full on `(-q, q)`; round trip; a
  **3456-case canonical rejection sweep** covering every one of the 1152
  positions carrying each of `q`, `q+1`, `4095`; and a constant-time compare
  that catches 256 sampled single-bit corruptions.

  - Plain C with a table-lookup scatter, per D5 - not a port of 864's 7,751
    lines and 111 Slothy windows. Those exist because degree-3 leaves are 6
    bytes stored and 4.5 bytes packed, neither aligned. Degree 4 is 8 bytes
    stored and 6 whole bytes packed. **The scatter itself does not improve**:
    G3a measured a GT vector's eight leaves at natural starts 0, 64, ..., 448,
    structurally identical to 864.
  - Full and Small are genuinely different, not aliases. `kem.c` calls Full on
    raw Forward output (+/-14607 per G3b), so it must reduce arbitrary int16;
    Small is called on basemul/baseinv output bounded at 1764/1768/1781 by G2
    and G4, so it only folds the sign bit.
  - **A correction the gate produced:** `full_exact_bytes` failed first time and
    the fault was in the test. The G1 oracle's `poly_tobytes` is the reference
    serializer, defined only on `(-q, q)`; comparing Full against it over
    arbitrary int16 was the wrong model. The right model is the canonical
    representative of `x mod q`, and the oracle now cross-checks it where it is
    defined.

- **G8a done.** `experiments/gt1152-p10-kem/`, `make check`.

  **A complete, runnable NTRU+1152 Good-Thomas KEM reproduces the checked-in
  KAT byte for byte**, sha256 `2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3`,
  the value recorded in G1's ring profile. 64 KEM round trips with tampered
  ciphertext rejection also pass. This is Milestone 1's correctness milestone.

  - `kem.c` and the symmetric/randombytes/secure_clear layer are verbatim from
    the 864 package; `params.h` verbatim from the 1152 reference. The transform,
    leaf arithmetic, inverse and codec come from G3b through G7.
  - New here: `symmetric.c` (generic sponge, not 864's fixed-size
    specialization - that is M2-1), `support.c` (cbd1, sotp, sub, triple,
    transcribed from the 1152 reference) and `api_glue.c`. Headers were split
    the way 864 splits them: `*_asm.h` for the raw-array kernels, `pack.h` and
    `inverse.h` for the `poly *` API `kem.c` compiles against.
  - **Scope:** this ran on macOS/arm64 and is not the 864 release gate. G8b owes
    manifest, ABI sentinels, package-level canonical sweep, zeroization,
    deterministic SUPERCOP export, and the per-leaf non-invertibility suite
    outstanding since G5. A `-D__STDC_WANT_LIB_EXT1__=1` flag was needed for
    `secure_clear` here; the Linux path should be confirmed, not assumed.
  - Not promoted: this lives in `experiments/`, not in the GT-Production tree.

- **G8b done.** On `pi@100.99.191.9`, Cortex-A76, Linux 6.18.33, GCC 14.2.0,
  `throttled=0x0`, host idle. Record in `gt1152-p10-kem/pi-results.json`.

  | gate | result |
  |---|---|
  | KAT | byte-identical, sha256 `2ddfc810c4...64c3` |
  | `test_kem` | 64 round trips and tampered rejection |
  | `test_baseinv_fail` | 288/288 leaves reject with 1 and clear, aliased and not |
  | `test_canonical` | 13,824 cases, 0 failures |
  | `test_zeroization` | 26 clear calls, 37,526 bytes, 0 nonzero after |
  | `test_abi` | 8/8 sentinels `mask=0x00000` |

  - **The Linux build caught a real defect**: `-D_DEFAULT_SOURCE` was missing,
    so `explicit_bzero` and `syscall` were implicitly declared. macOS took a
    different branch of `secure_clear.h` and never noticed. 864's Makefile has
    the flag; this one had dropped it.
  - **The per-leaf non-invertibility debt from G5 is paid.** Every one of the
    288 leaves is zeroed inside an otherwise invertible polynomial and must
    reject with a cleared output, then again through an exact alias. Previous
    coverage was incidental.
  - **The ABI sentinels validate the riskiest structural choice**: all eight
    public entry points preserve every callee-saved register, which is what
    makes `SAVE_PUBLIC` correct around leaves that clobber v8-v15 and calling
    the C tail from assembly safe.

  Still owed: source manifest and deterministic SUPERCOP export, both folded
  into G9. No performance measurement of any kind was taken.

- **G9 done.** `crypto_kem/ntruplus1152/aarch64-gt1152` on supercop-20260831,
  Pi 5 core 3, GCC 14.2.0 `-march=native`, goal `constbranchindex`. Evidence in
  `gt1152-p10-kem/supercop-results.json`, raw data `supercop-1152-data.txt`.

  **SUPERCOP validated the KEM byte contract against its own built-in
  `ntruplus1152` checksum** `2275d102...3ad8` - an independent confirmation
  stronger than the KAT, covering keypair, enc and dec under SUPERCOP's
  randomness discipline. The `ntruplus1152repo` checksum gap recorded earlier
  turned out to be moot: SUPERCOP ships a checksum for this scheme, so the GT
  leaf was added as a sibling implementation rather than a separate scheme.

  | implementation | cycles (best, -O3) | vs official |
  |---|---:|---:|
  | `aarch64` (official) | 111,341 | - |
  | `aarch64-gt1152` | **142,741** | **+28.2%** |
  | `opt` | 193,389 | +73.7% |
  | `ref` | 297,607 | +167.3% |

  **The port is 28% slower than the official NEON implementation**, 26% faster
  than `opt` and 52% faster than `ref`. That is the expected result and every
  reason is on record: the hash is the generic sponge (864's fixed-size version
  was worth ~4358 + ~4103 cycles, its single largest lever, reached at gate 53
  of 58); `inverse16_tail` is C at 4096 MACs against 589 assembly instructions;
  the codec is plain C where 864 spends 45% of its source on routed assembly;
  BaseInv has no ILP split; and nothing was ever Slothy-scheduled for 1152.
  For scale, 864's GT beats its official by 11-21% after 58 gates.

  Owed: per-operation attribution of the 28%, which needs a fresh-date run
  because SUPERCOP caches by version/host/date.

- **P11 done.** `experiments/gt1152-p11-profile/`. Component profiler adapted
  from `bench/aarch64/gt864-production-profile`, PMU cycles on Pi 5 core 3, 41
  samples per point, `cross_implementation_wire_differences=0` and
  `instrumentation_equivalence=pass`.

  Built to answer: with the hash left unoptimized, how much is polynomial
  multiplication actually worth? **The answer inverted the assumed priority.**

  | category | official | GT | delta | share of the 44,106 gap |
  |---|---:|---:|---:|---:|
  | serialize | 10,054 | 40,804 | **+30,750** | **69.7%** |
  | sample/misc | 3,891 | 10,391 | +6,500 | 14.7% |
  | hash | 84,781 | 90,636 | +5,855 | 13.3% |
  | **polynomial multiplication** | **61,921** | **62,708** | **+787** | **1.8%** |

  - **`poly_ntt` is 2,592 cycles FASTER than the official's.** The Good-Thomas
    port does what it was built to do. basemul is a wash at -180; the inverse
    (+1,145) and baseinv (+2,414) give a little back, both with known causes -
    the C tail at 4096 MACs and the missing 12x3 ILP split.
  - The deficit is `poly_frombytes` (2,021 -> 16,820, eight times slower) and
    `poly_tobytes_small` (+14,620), plus `poly_cbd1` and `poly_sotp_decode`.
    All of it is the plain C that D5 and Milestone 1's scope deliberately left
    in place, against the official's `pack.s` and `cbd.s`.
  - Hash rows need care: GT's `hash_g_fr0` serializes inside the hash boundary,
    so part of its 25,808 is really serialization. Whole hash paths compare as
    39,629 official against 45,521 GT.

  **Consequence for the plan: further polymul work buys almost nothing.** The
  measured order is codec first, sampling second, hash fusion third.

  Limit: about 15,500 cycles per implementation sit in uninstrumented glue
  (`kem.c`, direct `shake256`, `verify`, `memcpy`). The residual is nearly
  identical for both (15,469 against 15,683), which is what makes the
  attribution trustworthy for comparison.

- **P14 done, Option A rejected.** `experiments/gt1152-p14-layout-study/`.

  The proposal was to have the inverse NTT output natural order so the codec's
  permutation disappears. It was aimed at the wrong end: `poly_invntt_ternary`
  **already** stores natural order, and its result never reaches the codec.
  Every codec call is fed by the forward or by basemul, so the real question is
  whether the *forward* should store natural order.

  Measured, per 1152-coefficient pass: contiguous copy 156 (the floor), permute
  GT to natural 941, permute natural to GT 1418, 12-bit pack 461, SoA with
  LD1x4/ST1x4 160, SoA with LD4/ST4 472. So the net permutation is 780 writing
  and 1265 reading, and LD4/ST4 costs 312 more than LD1/ST1.

  Option A accounting: save 9,741 on the codec, pay 2,183 moving basemul and
  baseinv to LD4/ST4, 4,682 turning the forward's 144 `str q` into 288
  lane-indexed ST4 across six calls, and 1,265 on `packed_i9`. **Net -1,612
  cycles, 0.85% of 190,214** - and that is before the structural problem:
  `ntt9.S` processes one bank at a time and a bank is one component, but the
  natural-order interleave needs all four components of a group live together,
  so the 846-line kernel would need restructuring at four times the live output
  registers.

  Option B, fusing the existing codec's three passes, reaches a floor of 15,958
  against today's 21,024 - **about 5,066 recoverable** with no contract change
  and the existing byte oracle still applying. Roughly three times the payoff at
  a small fraction of the risk.

  Honest limit either way: at its floor GT's serialize is 15,958 against the
  official's 10,086, and that residual +5,872 is the permutation. It is
  structural, because the official does none at all.

  **Reopen condition: void as of P16.** Option A was parked behind "worth
  revisiting only if `ntt9.S` is being restructured for another reason, so the
  four-component grouping is paid for anyway". P16 measured `ntt9.S` at 93% of
  the hardware multiply-throughput floor, so no such reason exists and none can
  arise. Option A stays rejected on its own -1,612.

- **P16 done, `ntt9.S` closed.** `experiments/gt1152-p16-ntt9-study/`.

  P11 found `poly_ntt` is GT's biggest win (-2,592 vs official). This gate asked
  whether more is available and by what mechanism. The forward NTT is `ntt9.S`
  and almost nothing else: `ntt_top` 449, `ntt_tail` 35, **`ntt9` 3,871 cycles
  per call, 89.1%** -- 484 cycles per bank over 8 banks.

  One bank (`ntt9.S:233-745`) is 512 instructions, of which **225 are multiplies**:
  75 Barrett-Shoup triples `mul` / `sqrdmulh` / `mls`, one per twiddle
  multiplication. The Slothy A76 model pins all three to `ExecutionUnit.V0()`, a
  single pipe, at inverse throughput 2.

  **Confirmed on the hardware, not just the model.** Twelve independent chains:
  `sqrdmulh` 2.000 cycles/op, `mul` 2.000, `add` 0.500, `trn1` 0.500 -- and
  `sqrdmulh` mixed with an equal count of `add` or `trn1` is still **2.000 per
  multiply**. Non-multiply vector work is free; it hides in the multiply pipe's
  shadow.

  So the floor is 225 x 2 = **450 cycles per bank against 484 measured, 93.0%**.
  The other 219 vector ops and 66 loads fit inside it with room to spare.

  | | cycles |
  |---|---:|
  | measured, per bank | 484 |
  | multiply-pipe floor, per bank | 450 |
  | slack per bank | 34 |
  | slack per `poly_ntt` call (8 banks) | 271 |
  | **slack across the KEM (6 calls)** | **1,626 = 0.85% of 190,214** |

  That 0.85% is the *unreachable* ceiling on Slothy-scheduling `ntt9.S`. D4's
  choice to run no solver in Milestone 1 costs at most this, and the question is
  now closed rather than deferred.

  The only other lever is issuing fewer multiplies, and it is nearly exhausted
  as well. Both NEON int16 modular-multiply idioms cost the same 6 VEC0 cycles:
  Barrett-Shoup `mul`(2)+`sqrdmulh`(2)+`mls`(2), and widening Montgomery
  `smull`(1)+`smull2`(1)+`mul`(2)+`smlal`(1)+`smlal2`(1). The widening form's
  cheaper per-op throughput is exactly cancelled by needing five ops for 8 lanes
  instead of three. And 75 vector twiddle multiplications is 600
  lane-multiplications for 144 points against ~516 for an idealised radix-2
  transform with perfect packing -- within 16% of a bound that already ignores
  the 9-into-8 packing loss that forces `ntt_tail` to exist.

  **The forward NTT is finished.** Remaining effort belongs to M2-1 (hash, ~45%
  of total) and the items P11 ranked.

- **P17 done, the 864 comparison settled.** `experiments/gt1152-p17-vs-864-parity/`.

  The question: 864's GT lane was already ahead of the selected official *before*
  its hash campaign (P53/P55). 1152's is not. Is that the parameter set or
  unfinished work?

  **Unfinished work. There is no structural penalty.** 1152 was re-profiled for
  this gate because P12 and P13 landed after P11 and were never entered here; the
  current standing is keygen +5.6%, encaps +3.5%, decaps +15.7%, **total
  +7.9% (176,200 official vs 190,181 GT)**.

  Both campaigns under one category mapping -- 864 at P52, the checkpoint
  immediately before its hash work:

  | category | 864 off | 864 GT | delta | 1152 off | 1152 GT | delta |
  |---|---:|---:|---:|---:|---:|---:|
  | hash | 69,959 | 70,856 | +897 | 84,789 | 86,642 | +1,852 |
  | forward | 22,556 | 20,373 | **-2,183** | 28,884 | 26,277 | **-2,607** |
  | inverse | 4,603 | 4,760 | +157 | 6,295 | 7,419 | +1,125 |
  | basemul | 11,944 | 10,449 | **-1,495** | 16,134 | 15,963 | -171 |
  | baseinv | 8,349 | 8,337 | -12 | 10,592 | 12,992 | +2,399 |
  | **serialize** | 10,934 | 8,700 | **-2,234** | 10,066 | 20,975 | **+10,909** |
  | sample | 4,430 | 4,062 | -368 | 3,895 | 4,460 | +565 |
  | **SUM** | 132,775 | 127,537 | **-5,238** | 160,657 | 174,729 | **+14,072** |

  **864 won pre-hash because its serializer was a win.** At -2,234 it was 864's
  second largest advantage after the forward NTT. 1152's is +10,909, sign
  reversed, and alone it exceeds the whole deficit. The official side is not
  harder here: official serialize is 10,934 at 864 and 10,066 at 1152.

  Transferring 864's pre-hash ratio in each category onto 1152's official
  baseline gives **-3.68%**, against 864's own -3.95%. The forward NTT shows it
  directly: ratio 0.903 at 864, **0.910 at 1152**. Where the 19,981 sits:
  serialize +12,966 (64.9%), baseinv +2,415, basemul +1,848, inverse +909,
  sample +889, hash +766, forward +188.

  **The mechanism, from the source.** 864's `pack.c` is twelve lines of wrapper;
  `pack_full_top` performs the GT-to-natural permutation *in registers* with 200
  `trn`, 108 `uzp`, 54 `tbl` and 24 `ext`, fused with the Barrett reduce and the
  12-bit pack, storing wire bytes as plain full-vector `stur`. No intermediate
  array. 1152's P12 codec declares `uint16_t nat[1152]` in all three entry points
  and runs two passes over memory. Measured per call: `poly_frombytes` 2,185
  against the official's 509, `poly_tobytes_small` 1,817 and `poly_tobytes` 2,368
  against 1,147. P14's pieces, against a 156-cycle copy floor: pack alone 461,
  permute GT->natural 941, natural->GT 1,418.

  **P15's rejection does not close the fused route.** P15 fused within the
  lane-indexed store family (`vst3_lane_u8`, 8 halfword lane stores becoming 16
  byte lane stores). 864 uses no lane-indexed store at all. That route is
  untried at 1152, and degree-4 should suit it better than degree-3 -- 864 needs
  its 54 `tbl` and 24 `ext` precisely because three-coefficient leaves do not
  align. It is not cheap either way: 864 reached -2,234 with 7,751 lines of
  Slothy-scheduled assembly over roughly twenty gates.

  **The hash is not what separates the campaigns.** 1152's hash ratio is 1.022
  against 864's pre-hash 1.013; the whole category is 766 of the 19,981. M2-1 is
  a large win *on top of* parity, as it was for 864 (-3.95% to -11/-21/-13%).

- **P18 done, the serializer rewritten.** `experiments/gt1152-p18-codec-registers/`.

  P17 named the mechanism: 864 never materialises natural order, it permutes
  inside the register file; 1152's P12 codec materialised `uint16_t nat[1152]`
  and ran two passes. This gate does it 864's way.

  **The tiling** (verified exhaustively in `generate_pairs.py`, which fails the
  build if it stops holding): the 36 Good-Thomas groups pair as **(g, g+9)**, 18
  pairs covering all 36 exactly once, and for every pair and every lane the two
  leaves are consecutive with the first even. A leaf is four coefficients, so a
  pair's lane is eight consecutive natural coefficients = **exactly twelve
  contiguous wire bytes** at `6m`, 12-byte aligned. The 144 blocks tile the 1728
  byte output with no overlap and no gap, so every store is independent.

  That is the degree-4 dividend the campaign plan predicted and P12 only partly
  collected. 864's three-coefficient leaves are 4.5 wire bytes and never align,
  which is why its `pack_full_top` needs 54 `tbl` and 24 `ext` to route them.

  **The kernel.** Per pair: 8 loads, one 8x8 int16 transpose (24 `trn`, three
  levels, verified symbolically against NEON `trn1`/`trn2` before any code was
  written; a transpose is an involution so one network serves both directions),
  8 twelve-byte stores, no scratch. Rows are loaded as `(c0,c2)` of g, `(c0,c2)`
  of g+9, then `(c1,c3)` of each, so a transposed lane reads out as four even
  coefficients then four odd -- the operand order the encoding wants, free.
  Encoding is then four instructions, with `vshll_high_n_u16(x, 12)` doing the
  widen and the 12-bit shift at once so the 24-bit little-endian pair that *is*
  the wire format falls out with no masking.

  | entry point | P12 | **P18** | saving | official |
  |---|---:|---:|---:|---:|
  | `tobytes_full` | 2,376 | **1,471** | -905 | 1,147 |
  | `tobytes_small` | 1,822 | **990** | -832 | 1,147 |
  | `tobytes_compare` | 2,608 | **1,431** | -1,177 | - |
  | `frombytes` | 2,219 | **956** | -1,263 | 509 |

  `tobytes_small` is now faster than the official's `poly_tobytes` while still
  paying for a permutation the official never performs.

  **Whole KEM**, profiler re-run after integration:

  | operation | official | GT | delta | was |
  |---|---:|---:|---:|---:|
  | keygen | 64,082 | 65,195 | +1.7% | +5.6% |
  | **encaps** | 59,438 | **58,855** | **-1.0%** | +3.5% |
  | decaps | 52,533 | 55,245 | +5.2% | +15.7% |
  | **total** | **176,054** | **179,294** | **+1.8%** | +7.9% |

  serialize +10,909 -> **+911**; every other category unchanged within noise.

  **Correctness.** All seven P09 oracle checks pass first run, including the
  3,456-case canonical rejection sweep and 256 single-bit compare corruptions.
  Byte-identical to P12 on all four entry points. Package gates on the Pi: KAT
  sha256 `2ddfc810c4...64c3`, 64 round trips, 13,824 canonical cases, 11/11 ABI
  sentinels, 288/288 baseinv, zeroization clean, 44-file manifest verifies.

  **What is left.** Serialize's ratio is 1.091 against 864's 0.796, so ~2,960
  cycles remain there -- 864 reached its figure with 7,751 lines of
  Slothy-scheduled assembly and this is intrinsics C. Of the remaining +3,391,
  **baseinv is now the largest single item at +2,405**, cause on record from
  G5/P11: no ILP split where 864 uses 12x3. Then hash +1,143, inverse +1,136,
  serialize +911, sample +568, basemul -168, forward -2,604.

  Owed: a fresh-date SUPERCOP run. G9's +28.2% predates P12, P13 and this gate.

- **P19 done, serializer assembly rejected and the gap closed anyway.**
  `experiments/gt1152-p19-serializer-floor/`.

  The question was whether to hand-write the P18 codec in assembly as 864 did
  with 7,751 Slothy-scheduled lines. Measurement said no, and redirected the
  target.

  **Measured A76 costs** (independent chains, so latency never binds): `tbl` with
  1 or 2 sources **0.500**, 3 sources 1.000, 4 sources 1.500;
  `trn1`/`zip1`/`uzp1`/`umin`/`add`/`and`/`cmhi` 0.500; `ushr` (and `ushll`)
  1.000; `umlal2` 1.000. **Two corrections to the Slothy A76 model:** it gives
  `(vtbl, vtbl_2): 1` where the hardware issues at 0.5, so it is pessimistic
  about `tbl` by 2x; and mixing a pipe-pinned op with a general one costs more
  than either alone -- `umlal2` x12 with `trn1` x12 measures 0.708 per op, and
  `ushr` x12 with `and` x12 the same, where free dual issue would predict 0.5.

  **The floor, measured rather than derived.** `pipe3.c` issues the exact
  per-pair instruction mix of `tobytes_small` -- same mnemonics, same counts,
  all chains independent, loads and stores included:

  | | cycles |
  |---|---:|
  | one pair, issue-limited floor | 44.00 |
  | x18 pairs | 792 |
  | measured `tobytes_small` | 878 |
  | **utilisation** | **90.2%** |

  A model-based estimate had predicted 32 cycles/pair. The hardware says 44, so
  scheduling the existing mix is worth at most 86 cycles per call, under 10%.
  The transpose-free restructure (one four-source `tbl` per lane replacing the
  8x8 transpose, 40 vector ops instead of 64) measures a 41-cycle floor against
  44 -- **rejected at 3 cycles a pair**, because `tbl4` at 1.5 nearly cancels the
  24 `trn` at 0.5 it removes.

  **The profile said the target was wrong.** Per entry point: GT's three
  `tobytes` entry points cost 7,022 over 6 calls against the official's 8,037
  over 7 -- **already 1,015 ahead**. The entire +911 was `frombytes`, 986 per
  call against 505. Writing `tobytes` in assembly would have optimised the half
  that was winning.

  **Five instruction-count cuts instead.** Canonical as `umin(a, a+q)` read
  unsigned, two ops not three, valid because every input is in (-q, q) so `a+q`
  never wraps. Widen-shift-combine as one `vmlal_high_n(y, x, 4096)`, since a
  widening multiply-accumulate by 4096 *is* widen-and-shift-and-add and produces
  the wire format directly. In `frombytes`: a plain 16-byte `ldr q` for the
  block, four bytes wider than the twelve the table lookup reads, with only the
  last block (lane 7 of pair 17, the final iteration) keeping the two-load path;
  `ushr` + `uzp1` + one `and` replacing `and` + `ushr` + `and` + `uzp1`, because
  `y >> 12` is the odd coefficient exactly and needs no mask; and a running
  `vmaxq_u16` with one `vmaxvq_u16(hi) >= Q` at the end replacing a compare and
  an or in every lane. Plus `#pragma GCC unroll 18` on the `tobytes` loop only --
  applied to all three it had cost `tobytes_compare` 410 cycles to register
  pressure.

  | entry point | P18 | **now** | saving |
  |---|---:|---:|---:|
  | `tobytes_full` | 1,471 | **1,333** | -138 |
  | `tobytes_small` | 990 | **836** | -154 |
  | `tobytes_compare` | 1,431 | **1,332** | -99 |
  | `frombytes` | 956 | **723** | -233 |

  **Whole KEM**, byte-identical to P18 on all four entry points:

  | operation | official | GT | delta | was |
  |---|---:|---:|---:|---:|
  | keygen | 64,073 | 64,764 | +1.08% | +1.7% |
  | **encaps** | 59,498 | **58,325** | **-1.97%** | -1.0% |
  | decaps | 52,538 | 54,171 | +3.11% | +5.2% |
  | **total** | **176,109** | **177,260** | **+0.65%** | +1.8% |

  **serialize +911 -> -1,034**: it is now a win, which is the property P17
  identified as the reason 864 beat its official before any hash work.

  All seven oracle checks and every package gate pass. Of the remaining +1,268,
  **baseinv at +2,406 is larger than the whole deficit** and is the only item
  with a known unexploited fix (no ILP split where 864 uses 12x3).

- **P20 done, the SUPERCOP record refreshed.** `experiments/gt1152-p20-supercop-fresh/`.

  G9's +28.2% predated P12, P13, P18 and P19. Only `pack.c`, `support.c` and the
  new `codec_pairs.h` changed in the package since commit `fdb1a87e`, confirmed
  with `git diff --name-only`, so the SUPERCOP leaf's `.s` files needed no
  reconversion; the three files were copied in and test-compiled first. SUPERCOP
  caches by version/host/date and G9 ran on this same date, so the bench data was
  archived and the cached `crypto_kem_ntruplus1152*` objects removed before each
  run. Two runs: all four implementations present for the selection-level A/B,
  then GT isolated, because SUPERCOP produces detailed records only for the
  implementation it selects and the official still wins selection.

  | implementation | flags | cycles | G9 |
  |---|---|---:|---:|
  | `aarch64` (official) | -O3 | **111,351** | 111,341 |
  | **`aarch64-gt1152`** | -O3 | **112,107** | 142,741 |
  | `opt` | -O3 | 193,424 | 193,389 |
  | `ref` | -O3 | 297,517 | 297,607 |

  **GT +756 cycles, +0.68%**, against G9's +31,400 and +28.2%. The official moved
  by 10 cycles in 111,341 between the two runs, 0.009%, so the measurement is
  stable and the whole change is GT's. GT's isolated-run figure was 112,074,
  0.03% from 112,107. All sixteen `try` records carry one checksum
  `2275d102...3ad8`, so SUPERCOP validated the byte contract for every
  implementation including GT.

  **Per operation**, SUPERCOP's own stabilized quartiles, 96 samples a side:

  | operation | stat | official | GT | % |
  |---|---|---:|---:|---:|
  | keypair | q1 | 57,199 | 57,866 | **+1.17%** |
  | **enc** | q1/median/q3 | 58,975 | **57,929** | **-1.77%** |
  | dec | q1/median/q3 | 52,549 | 54,276 | **+3.29%** |

  enc and dec are flat across all three quartiles. **Keypair must be read at q1:**
  NTRU+ keygen retries when the sampled polynomial is not invertible, so the
  sample is bimodal -- 46 of 96 official and 52 of 96 GT samples land at the
  no-retry cost, and the median therefore moves with a particular run's retry
  count (it reads -6.63%, which is an artefact). q1 compares the no-retry mode.

  **Independent agreement with the P19 component profiler**, different harness,
  different statistic, to within 0.2 percentage points on every operation:
  keygen +1.08% vs +1.17%, encaps -1.97% vs -1.77%, decaps +3.11% vs +3.29%,
  total +0.65% vs +0.68%.

  The 28.2% closed to 0.68% with **no change to any assembly** -- P12, P13, P18
  and P19 are all C. NTRU+864 for scale stood at -3.95% before its hash campaign
  and reached -11%/-21%/-13% after it; 1152's hash is still the generic sponge.

- **P21 done, the next targets identified.** `experiments/gt1152-p21-decaps-targets/`.

  P19's aggregate ranked `baseinv` (+2,406) first. Per operation that is
  misleading: **`baseinv` is keygen-only, and keygen is the operation least
  behind.** keygen +454 attributed (SUPERCOP +1.17% q1), encaps -1,271 (-1.77%),
  **decaps +2,085 (+3.29%)** -- decapsulation is the only operation still losing.

  Decaps, component by component: `poly_invntt_ternary` 7,433 against
  `poly_invntt` + `poly_crepmod3` 6,299 (**+1,134**); `poly_sotp_decode` 1,343
  against 508 (**+835**); `poly_basemul_rinv` 3,385 against `poly_basemul_scale`
  2,551 (**+834**); `poly_frombytes` +663; against `poly_ntt` -869 and
  `poly_basemul` -263.

  **Two new measurements.** The C `invntt16_tail` costs **1,469 cycles per call**
  standalone -- more than the entire inverse deficit. 864's `inverse16_tail.S` is
  592 instructions with a Slothy estimate of 147 cycles, and D6 already
  established that 1152 needs the *same* vector arithmetic plus exactly 32
  `umov`/`strh` pairs (96 outputs to 128), so it is 656 instructions of
  known-correct arithmetic rather than a re-derivation.

  And the cause of `poly_sotp_decode`'s 2.6x: P13's version does a horizontal
  `vaddvq_u16` **per output byte**, 144 of them, packing eight 0/1 lanes by
  multiplying by `{1,2,...,128}` and reducing. The official's `cbd.s` has no
  horizontal reduction at all -- `sqxtn` to narrow, a bit-transpose network
  (`trn` at .4s, .8h, .16b), then `add`/`shl`/`orr`. The same substitution P18
  made in the codec.

  `poly_frombytes` (+663) is **not a target**: P19 measured it at its issue
  floor, the cost being the Good-Thomas permutation the official never performs.

  **Recommended order:** `invntt16_tail` to assembly (largest, measured, shaped
  by D6, and D8's declared plan), then `poly_sotp_decode` (cheapest, no new
  mathematics), then `poly_basemul_rinv` (M2-2, the first Slothy gate). If all
  three reach parity decaps goes from +2,085 to roughly -900 and every operation
  beats the official before the hash campaign. `baseinv` follows, to turn
  keygen's +454 into a clear win.

- **P22 done, the tail is assembly and the KEM is at parity.**
  `experiments/gt1152-p22-tail-asm/`.

  P21 ranked this first: the C tail measured 1,469 cycles alone, more than the
  whole inverse deficit. D8 always named assembly as the target.

  **The port is two changes, not a rewrite.** Of 864's 589 instructions only two
  kinds are not element-wise. The fold over `top`: 864 packs the tail scratch as
  `lane = 3*top + branch` and folds with `ext #6` (rotate three halfwords) plus
  `add`; 1152 packs `lane = 4*top + branch`, so the rotation becomes **`#8`**.
  Exactly 32 such `ext` exist, all self-rotates, each paired with its `add`, and
  the generator asserts it. The output extraction: 864 writes three halfwords per
  output, six bytes, never a clean store width, so it spends 96 `umov` and 96
  `strh`; 1152's four branches are **eight contiguous bytes, one `str d`** --
  192 instructions become 32, the same degree-4 dividend P18 collected in the
  codec. 589 instructions become 430.

  **One table needed repacking, and the kernel says which.** `x3`
  (`invntt16_constants`) is loaded 6 times and all 35 uses are lane-indexed, so
  it is a constant pool and carries unchanged. `x4`
  (`invntt16_tail_constants`) is loaded 64 times and all 64 uses are
  full-vector, so its lanes line up with the data: every row is repacked
  `[A,A,A,B,B,B,0,0]` -> `[A,A,A,A,B,B,B,B]`, asserted row by row, no value
  changed. `invntt16_main_constants` is left alone and verified byte-identical --
  `invntt16_asm` packs its lanes by the 16-axis, not by (top, branch).

  **Two defects the unit differential caught, not the KAT.** The table packing
  (4,352 mod-q mismatches of 8,192, outputs equal to raw table values), and then
  store placement: the generator had put each `str d` where the first `strh`
  was, but Slothy reuses these vector registers and several are overwritten
  between an output's `umov` and its `strh`. Moving the store to the `umov`
  position, where the value is provably live, fixed the last 511.

  **Correctness.** 4,000 trials x 128 outputs = 512,000, inputs uniform on
  [-2617, 2617] plus 200 trials at the extremes: **mod-q mismatches 0**, max
  output 3920 against the 5028 the ternary consumer declares. Exact mismatches
  are expected -- the C applies a final Barrett to pick one representative, the
  assembly emits its own, and `crepmod3` reduces mod q. Every package gate green,
  ABI sentinels included.

  | | cycles |
  |---|---:|
  | tail, C | 1,469 |
  | **tail, assembly** | **311** |

  | operation | official | GT | delta | was |
  |---|---:|---:|---:|---:|
  | keygen | 64,061 | 64,737 | +1.06% | +1.08% |
  | **encaps** | 59,482 | **58,340** | **-1.92%** | -1.97% |
  | decaps | 52,584 | 53,055 | **+0.90%** | +3.11% |
  | **total** | **176,127** | **176,132** | **+0.00%** | +0.65% |

  `inverse` is now **-14** where it was +1,134. **The KEM is at parity with the
  official**, five cycles apart on 176,000, with the hash still generic.

- **P23 done, decapsulation now beats the official too.**
  `experiments/gt1152-p23-sotp-decode/`.

  P21 found the cause: P13's version does a horizontal `vaddvq_u16` **per output
  byte**, 144 of them. But the reference's message is just
  `msg[i] = packLSB(a[8i..8i+7]) ^ buf[144+i] ^ buf[i]` -- no bit-plane expansion
  is needed at all.

  Following the official's `cbd.s`, the coefficients are carried as `a + 1` in
  **two-bit fields, four to a byte**. A buf byte then lines up directly, its even
  bits as `b2 & 0x55` and its odd bits as `(b2 >> 1) & 0x55`, so nothing is
  `dup`ped from a scalar. With `f = a + 1 + b2 = t4 + 1`, bit 0 of
  `f ^ (f >> 1)` is 1 exactly for f in {1,2}, that is t4 in {0,1} -- **the
  failure test falls out of the same packing**, and the message bit is the
  complement of the field's bit 0.

  **Non-ternary coefficients are handled, not assumed away.** Two-bit fields
  would overflow on one, but the reference fails on any such coefficient anyway,
  since `t4 = a + b2` read as uint16 then exceeds 1 whichever way b2 falls. A
  saturating narrow preserves that and a running `vmaxq_u8` reports it.

  **One defect, and how it was caught.** The three `uzp` levels leave the planes
  in the order **0,2,1,3,4,6,5,7**, not the bit-reversal assumed. It survived the
  first differential because that test's only accepted cases were the all-zero
  polynomial, where every field is valid whatever the order. Simulating
  `uzp1`/`uzp2` symbolically settled it, and the test was strengthened to build
  genuinely valid encodings (pick the message bit m, set a = m - b2 so t4 = m).

  | | cycles |
  |---|---:|
  | P13, horizontal reduction | 1,332 |
  | **P23, two-bit fields** | **484** |
  | official | 508 |

  | operation | official | GT | delta | was |
  |---|---:|---:|---:|---:|
  | keygen | 64,061 | 64,775 | +1.12% | +1.06% |
  | **encaps** | 59,551 | **58,337** | **-2.04%** | -1.92% |
  | **decaps** | 52,498 | **52,218** | **-0.53%** | +0.90% |
  | **total** | **176,109** | **175,331** | **-0.44%** | +0.00% |

  20,000 differential trials against the reference across four modes -- valid
  encodings, valid with one coefficient corrupted, random ternary, and
  out-of-range -- with zero mismatches on return code and all 144 message bytes.
  Every package gate green.

  **Two of three operations now beat the official and so does the total**, with
  the hash still generic. `baseinv` (+2,406, keygen-only) is what keeps keygen
  positive.

- **P24 done, and the third P21 target closes the set.**
  `experiments/gt1152-p24-basemul-rinv/`.

  **The gap was not the degree-4 arithmetic.** Compiled per group, the official's
  `poly_basemul_scale` issues exactly our multiplies -- 19 `smlal`, 19 `smlal2`,
  7 `smull`, 7 `smull2`, 7 `mul`, 7 `uzp1`, 7 `uzp2` -- and differs only in
  having **no** `sqdmulh`/`srshr`/`mls`. Those four centered Barretts cost 16
  VEC0 cycles a group on the measured A76 costs, putting our floor at 82 cycles
  a group, 2,952 for 36 -- **already above the official's 2,551 measurement**, so
  no schedule could have closed it.

  **D7 does not need a Barrett.** Its purpose is only to bring the output, which
  G2 bounds at 2752, inside 864's documented inverse input contract of 2497. A
  single conditional subtract does that with no multiply at all: with
  |x| <= 2752 < 1728 + q, one of `x-q`, `x+q` or `x` lands in **[-1728, 1728]**,
  one tighter than the Barrett's [-1729, 1729]. **No bound is re-derived** -- the
  change rests on G2's already-proved 2752. Probed over 20,000 trials on the
  declared [0,4095] input domain including the all-4095 case: max
  pre-normalization 2536 (bound 2752, valid to 5185), max post-normalization 1728
  exactly as derived.

  Plus a dependency rewrite at no instruction cost: pre-multiplying zeta into b
  once per group replaces the serial `cross -> reduce -> xzeta -> accumulate ->
  reduce` with three shared `bz` values and four independent accumulations.
  Algebraically identical, and it is the form the official's histogram matches.

  | | cycles |
  |---|---:|
  | P21 baseline (Barrett) | 3,378 |
  | conditional subtract | 3,118 |
  | **+ zeta pre-multiply** | **3,054** |
  | official | 2,551 |
  | issue floor | 2,376 |

  **What is left here is a genuine scheduling gap, the campaign's first**: 78% of
  floor, with the official proving 2,551 reachable on the same instructions.
  That is M2-2, worth about 500 cycles. GCC's `unroll` pragma has no effect at
  1, 2, 3 or 4.

  **All three P21 targets are now done.**

  | operation | official | GT | delta |
  |---|---:|---:|---:|
  | keygen | 64,053 | 64,748 | +1.09% |
  | **encaps** | 59,531 | **58,319** | **-2.03%** |
  | **decaps** | 52,508 | **52,087** | **-0.80%** |
  | **total** | **176,092** | **175,155** | **-0.53%** |

  | category | official | GT | delta | at P21 |
  |---|---:|---:|---:|---:|
  | **baseinv** | 10,599 | 12,996 | **+2,397** | +2,405 |
  | hash | 84,801 | 85,703 | +902 | +985 |
  | inverse | 6,292 | 6,309 | +18 | +1,134 |
  | basemul | 16,131 | 15,781 | **-350** | -160 |
  | serialize | 10,075 | 9,039 | **-1,036** | -1,034 |
  | sample | 3,893 | 3,622 | **-270** | +556 |
  | forward | 28,884 | 26,294 | **-2,590** | -2,618 |

  **`baseinv` at +2,397 is now larger than every other loss combined and is what
  keeps keygen positive.** It is keygen-only; cause on record from G5/P11, no ILP
  split where 864 uses 12x3.

- **P25 done, the next target confirmed and `inverse` measured.**
  `experiments/gt1152-p25-baseinv-inverse-floors/`.

  **`baseinv` has two separate problems.** Phase timing with PMU reads inside the
  function: numerator loop 3,783 (53.8%), **prefix + inversion + recover 1,928
  (27.4%)**, finish loop 1,087 (15.4%).

  The serial phase is a *latency* problem: a 35-step `fqmul` prefix chain, then
  `fqinv`'s addition chain for exponent 3455, then 35 recover steps each carrying
  `inv = fqmul(inv, di)` -- every one strictly serial, one vector in flight, the
  multiply pipe idle. That is what "no ILP split" means, and 864's 12x3
  decomposition runs three independent chains so the latency divides by about
  three.

  The other two phases are throughput-bound and under-scheduled at the same ~78%
  seen elsewhere: numerator 21 wide pairs + 10 reductions = 82 V0 cycles a group,
  2,952 for 36 against 3,783 measured; finish 4 `fqmul` = 24 a group, 864 against
  1,087. So roughly **1,100 cycles from the ILP split and ~800 from scheduling**,
  which would put baseinv near 4,500 against the official's 5,300 per call and
  flip keygen negative.

  **`inverse` is level and has no competitive gap.** `poly_invntt_ternary`
  measures 6,293 against the official's `poly_invntt` + `poly_crepmod3` at 6,292.
  Its multiply-pipe floor, from the shipped kernels and the driver's confirmed
  call counts -- `packed_i9` 16 calls x 57, `invntt16_asm` 8 x 151, the tail 149,
  `crepmod3` 36 x 8 = **2,557 multiply-class ops, 5,114 cycles** -- puts it at
  **81%**. About 1,200 cycles of absolute headroom, but taking it changes no
  standing.

  **One apparent cheap win is not available.** `inverse16.S` still spends 128
  `umov` + 128 `strh` per call, the extraction P22 replaced with 32 `str d` in
  the tail. It does not transfer: the tail's four branches are four *contiguous*
  int16, while `invntt16_asm`'s 128 outputs are **8 bytes apart** -- one component
  across leaves, gaps of 8 (96 times) and 48 (31 times), no aligned run of four.
  Making them contiguous means one call producing all four components, the
  four-components-live restructure P14 rejected for `ntt9.S`.

  **Next: `baseinv`, and the ILP split before the scheduling** -- the larger of
  its two levers, known in shape from 864, and a restructure rather than a
  re-derivation, so it carries no bound risk.

- **P26 done. Every operation now beats the official.**
  `experiments/gt1152-p26-baseinv-ilp/`.

  P25 measured `baseinv`'s batch inversion at 1,928 cycles of strictly serial
  work. Splitting the 36 groups into K chains is **the same algorithm one level
  up**: each chain builds its own prefix product, and the K chain products are
  batch-inverted by the identical routine.

  **Correct by associativity, with the Montgomery bookkeeping unchanged.**
  `cpre[K-1] = P_0...P_(K-1) R^-(K-1) = (prod of all 36) R^-(K(M-1)+K-1) =
  (prod of all 36) R^-(KM-1)` -- exactly what the single chain fed to `fqinv`, so
  `fqinv` sees the same value in the same representation, and the inner inversion
  yields `ip[c] = P_c^-1 R^-m`, precisely the initial carry each recover loop
  needs. **No range or representation change, so no bound is re-derived.** The
  non-invertibility test moves to the same product and stays exact: a residue of
  0 has one representative in (-q,q) whatever the multiplication order.

  | K | chain | serial depth | cycles |
  |---|---:|---:|---:|
  | 1 | 36 | 70 | ~6,550 |
  | 2 | 18 | 36 | 5,904 |
  | **3** | 12 | 26 | **5,793** |
  | 4 | 9 | 22 | 5,792 |
  | 6 | 6 | 20 | 5,813 |

  K=3 and K=4 tie within noise; K=3 taken, matching 864's documented 12x3.

  **The differential needed correcting, not the code.** A byte comparison reports
  mismatches on 1.5-2.7% of trials, rising with K. They are all **congruences**:
  `montgomery_reduce`'s output lies in (-q,q), which is not a unique
  representative -- 100 and -3357 are both in range and congruent -- so a
  different multiplication order legitimately lands on a different one. Checked
  properly over 4,000 trials (1,909 invertible, 2,091 with a leaf forced
  singular): **zero real mismatches**. The KAT confirms it byte for byte.

  Phases: numerator 3,783 -> 3,711, **serial 1,928 -> 1,191**, finish 1,087 ->
  1,095. Only the serial phase moves, by 737, as designed.

  **What is left is scheduling**: numerator 3,711 against a 2,952 floor and
  finish 1,095 against 864, both 79%. Unrolling does not reach it -- at 2, 3 and
  4 groups per iteration and with `-funroll-loops` the result lands between 5,751
  and 5,783 against 5,793, run-to-run noise. The remaining ~990 cycles belong to
  M2-2 with `basemul_rinv`'s 503.

  | operation | official | GT | delta | was |
  |---|---:|---:|---:|---:|
  | **keygen** | 64,074 | **63,020** | **-1.65%** | +1.09% |
  | **encaps** | 59,533 | **58,316** | **-2.05%** | -2.03% |
  | **decaps** | 52,492 | **52,039** | **-0.86%** | -0.80% |
  | **total** | **176,100** | **173,374** | **-1.55%** | -0.53% |

  **Every operation now beats the official, with the hash still the generic
  sponge.** For scale, NTRU+864 stood at -3.95% before its hash campaign and
  reached -11%/-21%/-13% after it. Remaining: hash +902 (M2-1), ~990 + ~503 of
  scheduling (M2-2), `frombytes` +659 structural, `inverse` level.

- **P27 done. The campaign's first SLOTHY run, and a `dev/clean/opt` tree to
  hold it.** `experiments/gt1152-p27-slothy-basemul-rinv/`, `dev/`.

  Everything shipped until now either carried 864's schedule with remapped
  immediates, was hand-written and never scheduled, or was intrinsics C.

  **The structure**, after mlkem-native's `dev/aarch64_{clean,opt}`, with two
  deliberate differences. Its clean tier is handwritten assembly with `.req`
  aliases, so registers are allocated and SLOTHY only reorders; ours is
  `V<name>` symbolic registers from a generator that authors data-flow, and
  SLOTHY does allocation *and* scheduling in two passes -- which means the
  symbolic tier cannot be assembled, and the `ra` output stands in for it. And
  mlkem-native targets one microarchitecture; here each gets its own directory,
  because SUPERCOP selects among sibling implementations per host.

  **That second difference is so far structure without content.** SLOTHY's
  `neoverse_n1` and both Apple M1 models have **no widening-multiply classes** --
  the M1 firestorm model is 480 lines against `cortex_a76`'s 869 and has no
  `Vmull`, `Vmlal`, `Vmul`, `Vmla` or `Vqdmulh` at all -- and every kernel
  admitted here is built on `smull`/`smlal`. Extending them would have to be
  measured rather than guessed, and this repository's host is an **Apple M2
  Pro**, a different microarchitecture from either M1 core. The Pi 5's
  Cortex-A76 is the only target that can be both scheduled and measured here.

  **Why this kernel.** P24 showed the official's `poly_basemul_scale` issues an
  identical multiply multiset and reaches 2,551 where our C reached 3,054 against
  a 2,376 floor. 78% of floor with the instruction count already minimal is a
  scheduling problem by elimination, and the official's number proves the
  schedule exists. The campaign had rejected scheduling four times on
  measurement -- `ntt9` at 93% (P16), the codec at 90% and ~100% (P19) -- and
  this is the first time it was the answer.

  **Three SLOTHY constraints, now encoded in the generator** so the next kernel
  does not rediscover them: symbolic registers cannot be defined outside the
  optimized region (so the four constants are physical `v0-v3`, reserved);
  `stp d8, d9, [sp, #-64]!` does not parse, there being no pre-index writeback
  form, so the kernel stashes nothing and reserves `v8-v15`; and **`t0`...`tN`
  are SLOTHY hint registers**, so naming temporaries `tN` makes every
  instruction parse and then fail its type check, through an error path that
  itself raises.

  | | cycles |
  |---|---:|
  | `ra` only, allocated but unscheduled | 3,155 |
  | intrinsics C | 3,054 |
  | **SLOTHY, `Arm_Cortex_A76`** | **2,744** |
  | official | 2,551 |
  | floor | 2,376 |

  `ra` took 2.1 seconds, `timing` 372.7. Correctness: 4,000 trials x 1,152 on
  the declared [0,4095] plus all-4095 and random extremes, **byte-identical** to
  the C oracle -- not merely congruent -- and max |out| 1728. Every package gate
  green, `basemul-inverse` ABI sentinel included, which is what confirms SLOTHY
  respected the `v8-v15` reservation.

  | operation | official | GT | delta | was |
  |---|---:|---:|---:|---:|
  | keygen | 64,082 | 63,009 | -1.67% | -1.65% |
  | encaps | 59,541 | 58,348 | -2.00% | -2.05% |
  | **decaps** | 52,512 | **51,629** | **-1.68%** | -0.86% |
  | **total** | **176,135** | **172,986** | **-1.79%** | -1.55% |

  Installed behind `NTRUPLUS1152_ASM_BASEMUL_RINV`: without the define the C is
  used and every gate still passes, so the assembly is an optimization rather
  than a dependency. Still 193 above the official and 368 above the floor.

- **P28 done. The per-target schedule does not pay, and that is now measured.**
  `experiments/gt1152-p28-cross-target/`.

  The `dev/clean/opt` tree exists to produce a schedule per microarchitecture.
  This gate asks whether that is worth anything: one kernel, two schedules, two
  machines.

  `basemul_rinv` from one symbolic source, scheduled for `Arm_Cortex_A76`
  (373s, 355 instructions) and `Apple_M1_firestorm_experimental` (733s, 241 --
  different software-pipelining depths of the same 115-instruction body). The
  M1 run is only possible because of the seven-class model patch.

  **On the Pi 5**, both schedules byte-identical to the C oracle over 4,000
  trials:

  | | cycles |
  |---|---:|
  | intrinsics C | 3,054 |
  | SLOTHY, `cortex_a76` | **2,744** |
  | SLOTHY, `apple_m1_firestorm` | **2,739** |
  | official | 2,551 |
  | floor | 2,376 |

  Scheduling is worth ~310 cycles, 10%. **Which target it was solved for makes
  no measurable difference.** The expectation was that the M1 schedule would be
  worse here; it is not.

  **On the Apple M2 Pro**, three consecutive runs with the candidates measured
  alternately and minimised: intrinsics C 278.8 / 277.0 / 277.9 ns, `cortex_a76`
  277.4 / 277.2 / 278.5, `apple_m1_firestorm` 277.6 / 278.8 / 280.8. **All three
  identical**, spread 1.4%. Neither schedule buys anything.

  **Why they disagree.** The A76 is four-wide with a ~128-entry reorder buffer
  and the loop body is 115 instructions, so barely one iteration fits the window
  and a static schedule has real work to do. Apple's P-core is far wider with a
  reorder buffer several hundred deep: it finds the parallelism at run time. That
  also explains why the target choice does not matter on the A76 -- both
  schedules were solved against the same dependency graph and are mostly doing
  the same thing, spreading the seven Montgomery reductions' serial chains far
  enough apart to fill the multiply pipe.

  **The M1 model is a three-fold pessimistic predictor.** It solved to 81 cycles
  per group; the M2 Pro measures about 25. M2 Pro is Avalanche and not
  Firestorm, so the model is not being accused of being wrong about M1, but it
  cannot be used to predict Apple performance for this kernel.

  **Conclusions.** Scheduling is worth ~10% on the A76 and nothing on Apple
  silicon for this kernel, so the SLOTHY work stays pointed at the Pi 5.
  **Shipping a second, Apple-targeted implementation is not justified**: the
  schedule is no better than the A76 one on the only Apple machine available,
  from a model that mispredicts by three. The tree keeps the capability; nothing
  ships. The multi-target structure still earned its place -- it is what made
  this measurable rather than a guess.

- **P29 done. GT beats the official under SUPERCOP.**
  `experiments/gt1152-p29-supercop-final/`.

  P20 measured +0.68%. Since then P22, P23, P24, P26, P27 and the two scheduled
  `baseinv` loops landed.

  | implementation | cycles | P20 | G9 |
  |---|---:|---:|---:|
  | **`aarch64-gt1152`** | **109,446** | 112,107 | 142,741 |
  | `aarch64` (official) | 111,401 | 111,351 | 111,341 |
  | `opt` | 193,469 | 193,424 | 193,389 |
  | `ref` | 297,624 | 297,517 | 297,607 |

  **GT -1,955 cycles, -1.75%.** The official has moved by 60 cycles in 111,341
  across all three runs, 0.05%, so the measurement is stable and the whole change
  is GT's. The campaign reads **+28.2% -> +0.68% -> -1.75%**.

  GT won selection this time, so the all-implementations run's detailed records
  are GT's; a third round with the official isolated gives both sides from the
  same session.

  | operation | stat | official | GT | % |
  |---|---|---:|---:|---:|
  | keypair | **q1** | 57,262 | **55,472** | **-3.13%** |
  | **enc** | q1/med/q3 | 59,016 | **57,915** | **-1.87%** |
  | **dec** | q1/med/q3 | 52,485 | **51,565** | **-1.75%** |

  enc and dec are flat across all three quartiles. Keypair is still read at q1
  for P20's reason: keygen retries on a non-invertible sample, so the median and
  q3 move with a run's retry count.

  **Agreement with the component profiler**: keygen -3.09% vs -3.13%, encaps
  -1.98% vs -1.87%, decaps -1.67% vs -1.75%, **total -2.29% vs -2.26%** — within
  0.11 percentage points on every operation and 0.03 on the total. That total is
  the sum of the three q1 figures, 168,763 against 164,952, not the selection
  metric, which is a single aggregate weighted differently and reads -1.75%.

  **Two things SUPERCOP's build does differently**, now handled by
  `refresh_leaf.py`: it compiles every source in the directory with its own
  flags, so the `NTRUPLUS1152_ASM_*` selectors are prepended to the leaf's
  `inverse.c` rather than passed on the command line -- verified by `inverse.o`
  carrying the three kernel names as undefined symbols, which only happens when
  they are active; and the leaf's lowercase `.s` is assembled without the
  preprocessor, so `#ifdef __APPLE__` becomes a second `.global` and a second
  label. The leaf was test-compiled first: 20 objects, no errors, all four
  kernel symbols defined.

- **P30 done. The last losing component was not structural after all.**
  `experiments/gt1152-p30-frombytes-survey/`.

  P19 called `frombytes` structural and at "~100% of its issue floor", and every
  gate since repeated it. **Both halves were wrong.**

  **The permutation genuinely cannot be skipped**: all four call sites feed
  `poly_basemul` or `poly_basemul_rinv`, which read the Good-Thomas layout. And
  P14's Option A is now *more* firmly rejected than when it was measured -- its
  accounting credited 9,741 cycles of codec saving, but after P18 and P19 the
  codec is 9,033 against the official's 10,067, already a win, so the credit is
  gone while the 8,130 it must pay is not.

  **But the floor was not where P19 put it.** Issuing the exact per-pair mix with
  every chain independent, and removing one piece at a time:

  | variant | cycles/pair | x18 |
  |---|---:|---:|
  | full mix | 36.50 | **657** |
  | without the 24-op transpose | 25.50 | 459 |
  | without the 8 V1-pinned `ushr` | 32.00 | 576 |
  | without the 8 offset-table loads | 37.50 | 675 |

  The permutation costs **198**, the shift **81**, the offset table nothing. And
  723 against 657 is **90.4%**, not ~100%.

  **What was avoidable.** The decode read each twelve-byte block as four 24-bit
  values, needing a shift to separate the pair, a `uzp1` to collect, and a mask:
  four operations a lane. Read as **eight 16-bit windows** instead and the shift
  and the collection merge -- lanes 0..3 take bytes `(3j, 3j+1)` whose low twelve
  bits are the even coefficient, lanes 4..7 take `(3m+1, 3m+2)` which hold the
  odd one shifted up by four, and one `ushl` with a per-lane count
  `{0,0,0,0,-4,-4,-4,-4}` fixes both at once. Three operations a lane, same
  output order, index still inside the twelve bytes.

  Floor 657 -> 576, measured **723 -> 645**, same 90% utilisation.

  **What is left**: the 198-cycle transpose is minimal -- an 8x8 transpose of
  16-bit elements from two-input shuffles needs `log2(8) x 8 = 24` operations and
  uses exactly that, and `st4` cannot substitute because it writes
  `x[4i+j] = v[j][i]` where the layout needs `x[8c+k] = u[k][c]`. Plus ~69 cycles
  of scheduling headroom, which makes `frombytes` a candidate for `dev/`.

  | operation | official | GT | delta | was |
  |---|---:|---:|---:|---:|
  | keygen | 64,087 | 62,042 | -3.19% | -3.09% |
  | encaps | 59,483 | 58,264 | -2.05% | -1.98% |
  | **decaps** | 52,516 | **51,353** | **-2.21%** | -1.67% |
  | **total** | **176,086** | **171,660** | **-2.51%** | -2.29% |

  `poly_frombytes` is +599 where it was +895. Every package gate green and the
  codec's seven oracle checks pass unchanged, including the 3,456-case canonical
  rejection sweep, which a wrong unpack index would break first.

- **P31 done. D7's normalization was never needed.**
  `experiments/gt1152-p31-basemul-rinv-bound/`.

  P24 found the official's `poly_basemul_scale` issues an identical multiply
  multiset and differs only by having no reduction, and concluded the rest was
  scheduling. P27 scheduled it, leaving +227. **That +227 was D7's
  normalization, and D7's premise was wrong.**

  D7 added it because the output was bounded at 2752, above the inverse's
  inherited 2497 contract. **That 2752 assumes inputs on [0,4095]**, which is
  what `inverse.h` declared -- and the declaration was looser than the truth. The
  only caller is decapsulation, which calls `poly_frombytes` three times under a
  short-circuiting `||` and aborts on any failure; `poly_frombytes` rejects any
  coefficient `>= q`. So both operands are **canonical**.

  With `|a|,|b| <= q-1` the accumulator is at most `4(q-1)^2 = 47,775,744` and
  the signed Montgomery bound is `q/2 + 4(q-1)^2/2^16 = 1728.5 + 729.0 = 2458`,
  inside the contract with 39 to spare, so the 864 chain still holds a fortiori
  and **nothing is re-derived**. Probed over 20,000 trials on that domain
  including the all-`q-1` case: **max output 2266**.

  `inverse.h` and `inverse_asm.h` now state the canonical precondition instead of
  [0,4095] -- the actual change is a declaration corrected to match what the
  caller already guarantees.

  The kernel loses 24 operations a group, so the clean source went 126 -> 98
  instructions and SLOTHY re-solved in 191s.

  | | cycles |
  |---|---:|
  | with normalization, scheduled (P27) | 2,744 |
  | intrinsics C, no normalization | 2,485 |
  | **scheduled, no normalization** | **2,379** |
  | official | 2,551 |

  | operation | official | GT | delta | was |
  |---|---:|---:|---:|---:|
  | keygen | 64,044 | 62,046 | -3.12% | -3.19% |
  | encaps | 59,547 | 58,248 | -2.18% | -2.05% |
  | **decaps** | 52,496 | **51,051** | **-2.75%** | -2.21% |
  | **total** | **176,087** | **171,345** | **-2.69%** | -2.51% |

  `poly_basemul_rinv` is **-142** where it was +227. Of the three components
  still losing, `basemul_rinv` is now a win, `frombytes` is +599 with ~69 cycles
  a call of scheduling left and then a minimal transpose, and `hash_g_fr0`'s
  +1,090 is M2-1's territory.

  **Worth recording separately: a declared contract looser than the caller's
  actual guarantee cost 227 cycles, and three gates reasoned from the
  declaration without checking it against the call site.**

- **P32 done. M2-1, and the campaign lands where NTRU+864 did.**
  `experiments/gt1152-p32-hash-fused/`.

  The last large item, pointed at by every gate since P11. Hash was 49.9% of
  GT's cycles.

  864's P53 and P55 built their fused kernels by adapting NTRU+768's with
  anchored replacements; this does the same for 1152, so the lineage is
  768 -> 864 -> 1152 and the Keccak core is untouched at each step. Both
  `fips202.c` files are byte-identical between 864 and 1152, so none of 864's
  hash advantage came from a faster permutation -- it is all in the fusion.

  The kernels hash one domain byte plus exactly `NTRUPLUS_POLYBYTES` with the
  whole 25-word state **live in registers**: no state array, no length
  arithmetic, and **no copy to prepend the domain byte** -- it is folded into the
  first absorbed word with `lsl #8` (plus `orr #1` for hash_g), so every later
  load is a `ldur` at offset `7 mod 8` and the 1728-byte message is never
  duplicated.

  | | 768 | 864 | **1152** |
  |---|---:|---:|---:|
  | input + prefix | 1153 | 1297 | **1729** |
  | full absorb blocks | 8 | 9 | **12** |
  | tail bytes | 65 | 73 | **97** |
  | hash_g output | 192 | 216 | **288** |
  | squeeze blocks | 1 + 56 | 1 + 80 | **2 + 16** |

  `generate_keccak.py` makes five anchored edits, each asserted to match exactly
  once or twice. **1152 is the first of the three to need two full squeeze
  blocks**, so hash_g's squeeze dispatch becomes a range test and
  `Lhash_g_squeeze_first` increments the stage counter instead of assigning it.

  **Correctness**: 4,000 inputs including all-zero and all-ones, differential
  against the generic sponge, **zero mismatches** on both kernels. Every package
  gate green. `clear_calls` falls 26 -> 23 and `clear_bytes` 37,526 -> 32,338
  because hash_f and hash_g no longer allocate and wipe a 1729-byte copy of the
  message -- less secret material duplicated, not more. `hash_h` keeps the
  generic sponge deliberately: 176 bytes is one block, with nothing to amortize.

  | | generic | fused | |
  |---|---:|---:|---:|
  | `hash_f`, 32 out | 17,754 | **11,947** | 1.49x |
  | `hash_g`, 288 out | 20,339 | **13,765** | 1.48x |

  Both larger than 864's -4,103 and -4,358, as a 33% longer input predicts.

  | operation | official | GT | delta | was |
  |---|---:|---:|---:|---:|
  | keygen | 64,056 | 56,781 | **-11.36%** | -3.12% |
  | **encaps** | 59,522 | **47,278** | **-20.57%** | -2.18% |
  | decaps | 52,511 | 45,181 | **-13.96%** | -2.75% |
  | **total** | **176,089** | **149,240** | **-15.25%** | -2.69% |

  Against NTRU+864 after its own hash campaign (P58's formal SUPERCOP run):
  keygen -11.41% vs **-11.36%**, encaps -21.05% vs **-20.57%**, decaps -13.06%
  vs **-13.96%**. Within a percentage point on every operation.

  Hash is now 42.7% of GT's cycles. A fresh SUPERCOP run is owed; P29's -1.75%
  predates this and P31.

- **P33 done. SUPERCOP confirms the hash campaign: -17.35%.**
  `experiments/gt1152-p33-supercop-hash/`.

  P29 measured -1.75%, before P30, P31 and P32.

  | implementation | cycles | P29 | P20 | G9 |
  |---|---:|---:|---:|---:|
  | **`aarch64-gt1152`** | **92,079** | 109,446 | 112,107 | 142,741 |
  | `aarch64` (official) | 111,403 | 111,401 | 111,351 | 111,341 |
  | `opt` | 193,359 | 193,469 | 193,424 | 193,389 |
  | `ref` | 297,704 | 297,624 | 297,517 | 297,607 |

  **-19,324 cycles, -17.35%.** The official has moved by 62 cycles in 111,341
  across all four runs, 0.06%. The campaign reads **+28.2% -> +0.68% -> -1.75%
  -> -17.35%**.

  | operation | stat | official | GT | % |
  |---|---|---:|---:|---:|
  | keypair | **q1** | 57,240 | **50,301** | **-12.12%** |
  | **enc** | q1/med/q3 | 58,992 | **46,964** | **-20.39%** |
  | **dec** | q1/med/q3 | 52,469 | **45,243** | **-13.77%** |

  For the first time **every keypair quartile is negative too** -- it is still
  read at q1 for P20's reason, but the hash saving now dominates the retry
  spread.

  **Agreement with the profiler**: keygen -11.36% vs -12.12%, encaps -20.57% vs
  -20.39%, decaps -13.96% vs -13.77%, **total -15.25% vs -15.53%** -- within 0.28
  percentage points on the total. That total is the q1 sum, 168,701 against
  142,507, not the selection metric.

  **Against NTRU+864** after its own hash campaign (P58): keygen -11.41% vs
  **-12.12%**, encaps -21.05% vs **-20.39%**, decaps -13.06% vs **-13.77%** --
  within a percentage point everywhere, and ahead of 864 on keygen and
  decapsulation.

  One procedural note: `keccakf1600.S` is the only source with live preprocessor
  branches, and the leaf uses lowercase `.s`, which gcc assembles without the
  preprocessor. It is expanded with `gcc -E -P -x assembler-with-cpp` **on the
  target** and the result asserted to contain no directive, rather than
  pattern-matched. The leaf was test-compiled first: 22 objects, no errors, the
  three selectors active in `inverse.o`, `symmetric.o` referencing both fused
  hashes that `keccakf1600.o` defines.

## Standing rules

- Evidence is per-parameter. A pass for 864 does not validate 1152.
- Slothy model cycles, macOS timing and emulated timing cannot substantiate
  Pi 5 / A76 performance. All performance numbers come from the Pi 5.
- The declared oracle is `gt1152-p01-ring-profile/ntruplus1152.py` plus the
  checked-in KAT vectors. Comparing two implementations that share a bug is not
  validation.
- Checked-in KAT vectors are never modified.
- Correctness precedes performance in every gate.

## Not established

- A *proof* of the forward NTT output bound. G3b measured it and G2 consumes
  the measurement, but no interval model of `.Lntt_one_bank` exists.
- The inverse NTT's internal bounds. Inherited from 864 under D7's
  normalization. G6b validated the chain by differential over 16 cases x 1152
  coefficients, which is evidence of agreement, not an interval proof.
- The *count* of twiddle multiplications in `ntt9.S` is not proved minimal.
  P16 bounds it within ~16% of an idealised radix-2 count, which is an
  estimate, not a lower-bound proof for the 9x16 Good-Thomas decomposition.

- **P34 done. The forward transform is closed, and the "unexplained 16 points"
  never existed.** `experiments/gt1152-p34-forward-attribution/`.

  The P33 follow-up analysis claimed the forward had a 25.4% static multiply
  advantage that only cashed out as 8.9% measured, and called that the one item
  with a clear ceiling and no explanation. **The 25.4% was wrong.** It came from
  slicing line ranges out of the *local* `ntruplus-ntt-Optimized` copy of
  `ntt.s` -- not the SUPERCOP leaf that is actually benchmarked -- on the
  assumption that `_looptop_012` began right after `mov counter, #128`. The
  label is 2 lines further down with a 19-line preamble in between, and the
  slice also ran past `b.ne` into the next stage. Reading the labels instead of
  assuming them:

  | | multiply ops |
  |---|---:|
  | official `poly_ntt` (936 + 1,152) | **2,088** |
  | GT forward (`ntt9` 1,800 + `ntt_top` 80 + `ntt_tail` 0) | **1,880** |
  | | **-9.96%** |

  Measured standalone on core 3, min over 30 interleaved passes, bit-identical
  across three consecutive runs:

  | | cycles |
  |---|---:|
  | official `poly_ntt` | 4,780.0 |
  | GT `ntt_asm` | **4,347.7** |
  | &nbsp;&nbsp;`ntt_top_asm` | 447.0 |
  | &nbsp;&nbsp;`ntt_tail_asm` | 32.7 |
  | &nbsp;&nbsp;`ntt9_asm` | 3,872.5 |
  | floor, GT multiply multiset (1,880 ops) | 3,757.0 |
  | floor, official multiply multiset (2,088 ops) | 4,173.0 |
  | floor, `ntt_top` instruction mix | 428.0 |

  Both floors land on 2.000 cycles per multiply to within 0.1%, which
  re-confirms the campaign's single-pipe VEC0 cost independently. And the delta
  closes exactly:

  ```
  predicted from multiply count       416.0
  overhead delta (607.1 - 590.7)       16.4
                                      -----
                                      432.4   measured 432.3
  ```

  The profiler was never diluted either -- `run-fwd.csv` records **2 calls per
  operation on both sides**, so per call GT 4,382 vs official 4,813 = -8.95%,
  against -9.04% standalone.

  **Headroom, and why the forward is now closed:**

  | stage | measured | floor | of floor | headroom/call |
  |---|---:|---:|---:|---:|
  | `ntt_top` | 447.0 | **428.0** | **95.7%** | 19.0 |
  | `ntt_tail` | 32.7 | ~0 | -- | ~33 |
  | `ntt9` | 3,872.5 | 3,597.1 | **92.9%** | 275.4 |

  I expected `ntt_top` to be latency-bound -- 39 instructions per iteration, 5
  of them multiplies, everything downstream of two `ld4 {4 x 8H}`, no software
  pipelining, 27.9 cycles per iteration against a single-resource bound near 10.
  **Wrong again.** The identical mix with every chain independent still costs
  428: the three binding resources do not overlap on this core (10 `str q` per
  iteration on the one 128-bit store pipe, 5 `mul` on VEC0, two 4-register `LD4`
  de-interleaves). `ntt9`'s 92.9% reproduces P16's 93% independently, and P16
  rejected scheduling at that figure. Only a decomposition issuing fewer than
  1,880 multiplies or fewer than 160 stores could move this, not a better
  schedule.

  **Harness lesson, recorded because it cost two builds:** `ntt9_asm` clobbers
  `d8`-`d15` without saving them -- legitimate, since `ntt.S` wraps it and does
  the save -- so calling it directly from C violates AAPCS. GCC had spilled the
  harness's live `double` into the callee-saved half of the vector file, and
  three candidates came back as ~6e252 rather than a time. **A measurement that
  reads as absurd is more often an ABI violation in the harness than a surprise
  in the code.**

  **Follow-up: is the shipped package clean? Yes.** `api_glue.c` declares only
  `ntt_asm`, which is the wrapper that does the save; the three inner kernels
  are reached only from assembly. `gt1152-p34-forward-attribution/audit_abi.py`
  proves this for every exported symbol rather than by grep -- it expands
  `.macro` bodies, splits each `.S` by exported label, and propagates "clobbers"
  along the `bl` graph with a save/restore pair as a barrier. **0 violations**,
  and a negative control (a C wrapper calling `ntt9_asm` directly) makes it
  report the violation and exit 1, so the zero is a result.

  Three greps I tried first were each wrong in a way the tool is not: a bare
  grep hits a **comment** in `inverse16_tables.h`; a `.global` regex assuming a
  bare name misses `inverse_ntt.S`, which exports through a `C(name)` macro; and
  a save-detector that does not expand macros misses `SAVE_PUBLIC`.

  **One real gap: `test/abi_sentinel.S` did not cover the two fused SHAKE256
  entry points P32 added.** They are correct -- they save `x19`-`x28` and never
  touch `v8`-`v15`, Keccak being all scalar -- but nothing asserted it.
  Sentinels added, `SOURCE-MANIFEST.sha256` refreshed; the ABI gate now reads
  **13/13 masks zero** and `make check` is green on the Pi throughout.

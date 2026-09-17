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
| G9 | Done | SUPERCOP packaging and first honest measurement | SUPERCOP validated the KEM byte contract against its built-in `ntruplus1152` checksum; **GT 142,741 vs official 111,341 cycles, +28.2%**. Evidence in `gt1152-p10-kem/supercop-results.json` |
| P11 | Done | Component profile: where the 28% goes | PMU attribution on Pi 5. **Polynomial multiplication is at parity (+787); serialization is +30,750.** Evidence in `gt1152-p11-profile/` |
| P12 | Done — *recorded late* | NEON codec: replace the scalar gather | Lane-indexed LD4/ST4 per leaf. Serialize went from +30,750 to +10,909. Evidence in `gt1152-p12-codec-neon/` |
| P13 | Done — *recorded late* | NEON sampling leaves | Broadcast-the-byte against `vtst`, avoiding an 8-way bit-plane interleave. sample/misc went from +6,500 to +565. Evidence in `gt1152-p13-sample-neon/` |
| P14 | Done — Option A rejected | Should the transform output natural order? | Measured: net -1,612 cycles (0.85%) for a major `ntt9.S` restructure. Codec fusion recovers ~5,066 with no contract change. Evidence in `gt1152-p14-layout-study/` |
| P16 | Done — closed | Is there headroom left in `ntt9.S`? | **No.** It is multiply-throughput bound at 93% of the A76 floor (484 vs 450 cycles/bank). Slothy is worth at most 0.85% of the KEM. Evidence in `gt1152-p16-ntt9-study/` |
| P15 | Done — rejected | Fuse the codec's passes with byte-granular lane stores | Measured 12,129 cycles worse: `vst3_lane_u8` doubles 8 halfword lane stores into 16 byte lane stores. Evidence in `gt1152-p15-codec-fused/` |
| P17 | Done | Why did 864 beat the official pre-hash and 1152 does not? | **No structural penalty.** At 864's pre-hash per-category ratios 1152 would stand at -3.68% against its measured +8.76%; 64.9% of the shortfall is the serializer. Evidence in `gt1152-p17-vs-864-parity/` |
| P18 | Done | Rewrite the serializer with the permutation in registers, 864's way | **Serialize +10,909 -> +911; whole KEM +7.9% -> +1.8%; encaps now -1.0%, faster than the official.** Byte-identical to P12 on all four entry points; all 7 oracle checks and every package gate pass. Evidence in `gt1152-p18-codec-registers/` |
| P19 | Done — asm rejected | Should the serializer be hand-written in assembly? | **No.** Measured issue floor puts the codec at 90-100%; scheduling is worth under 10%. Cutting instructions instead took **serialize +911 -> -1,034 and the KEM +1.8% -> +0.65%**, encaps -1.97%. Evidence in `gt1152-p19-serializer-floor/` |
| M1 | **Complete** | Milestone 1: a runnable, KAT-passing, SUPERCOP-validated NTRU+1152 GT KEM | All correctness gates pass on Pi 5; performance is measured and honest, not yet competitive |
| M2-1 | Deferred | Hash fusion: fixed-size SHAKE256 1728 → 288/32 | Byte identity against generic `fips202.c` plus paired Pi 5 PMU |
| M2-2 | Deferred | First Slothy gate: degree-4 `basemul_rinv` | Reproducible Pi 5 PMU improvement over the G4/G5 intrinsics baseline |

## Decisions ledger

| # | Decision | Rationale | Recorded |
|---|---|---|---|
| D1 | Branch `neon-1152` in place, no worktree | 864 sources travel with the branch, so a second checkout buys nothing; the Pi 5 is a single shared resource so parallel benchmarking is impossible anyway. Repo convention reserves `.worktrees/` for same-champion gate fan-out | 2026-09-17 |
| D2 | Work lives in repo-root `experiments/gt1152-pNN-*` | Mirrors the newest 864 convention (p41–p58). Deliberate deviation from `parameter-profiles.md`, which suggests the `Experiment/NTRU+1152/` lane | 2026-09-17 |
| D3 | Performance baseline is SUPERCOP official 1152 | Matches how 864's P58 claim is stated; the only basis valid for an external claim | 2026-09-17 |
| D4 | Milestone 1 uses no Slothy at all | The reused inverse cores keep their 864 schedule (see D6); new degree-4 arithmetic is written as NEON intrinsics C, exactly as 864's production `base.c` is | 2026-09-17 |
| D5 | Pack/unpack starts from the simple stock-shaped codec | 864's 7,751 lines of routing exist only to work around degree-3 lane misalignment, which 1152 does not have. G9's profile decides whether more is needed | 2026-09-17 |
| D6 | **Corrected by G6.** Immediate remap works for `packed_i9` and `invntt16_asm` only. `invntt16_tail_asm` must grow from 96 to 128 outputs | Static `strh` counts: 864 is 6x128 + 96 = 864; 1152 needs 8x128 + 128 = 1152. The first two kernels are driven by a per-component loop so their per-call work is invariant; the tail is called once and covers all components, so its work grows with the component count. The original reasoning (component count and total both grow 4/3) only applies to the per-component kernels. Mitigating: the tail's vector arithmetic is already eight-lane and matches the main kernel's (309 vs 311 ops), so the two lanes 864 leaves as padding already hold correct results - the gap is exactly 32 umov/strh pairs | 2026-09-17, corrected 2026-09-17 |
| D7 | **Resolved: add one `barrett_reduce` at `basemul_rinv` output.** 1152's output is ≤ 2752 against 864's ≤ 2497 inverse input contract (ratio 1.102); barrett brings it to `[−1729,1728]`, tighter than 2497 | The 864 inverse chain (I9 2617, I16 21397, ternary 5143) then holds a fortiori instead of needing re-derivation. Sound because the inverse operates on the 288-point transform — leaf degree changes bank and component counts, but every coefficient passes the same butterfly network, so its bound chain depends only on input magnitude, not leaf degree. Cost ~3–4 instructions per vector over 36 tiles, Decaps-only. Re-deriving at 2752 is deferred to M2 | 2026-09-17 |

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

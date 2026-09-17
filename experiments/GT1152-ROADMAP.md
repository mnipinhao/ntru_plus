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
| G9 | Next | SUPERCOP packaging and first honest measurement | SUPERCOP accepts the scheme (not `unknown`); stabilized quartiles against official 1152 on one host, compiler and SUPERCOP revision |
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
  normalization, to be re-verified in G6.
- Any GT-domain byte layout or wire permutation for 1152 (G3).
- Any performance measurement whatsoever. Nothing has run on hardware.

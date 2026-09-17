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
| G5 | Active | Degree-4 `basemul_rinv` and BaseInv | Oracle differential; non-invertible-input failure path constant-time and zeroizing; alias and wipe |
| G6 | Next | Inverse NTT immediate remap (`inverse9.S`, `inverse16.S`, `inverse16_tail.S`, `inverse.S`) | Instruction-multiset audit shows zero difference from 864 except declared immediates; bounds re-verified at the G2 input contract; oracle differential exact |
| G7 | Next | Pack / unpack for the degree-4 layout | Exact byte oracle including every output byte position corrupted independently; canonical and malformed rejection; alias |
| G8 | Next | KEM assembly and KAT — the correctness milestone | `make check` green on Pi 5: manifest, KEM, canonical, zeroization, KAT byte-identical, export self-check |
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
| D6 | Inverse NTT is an immediate remap, not a reschedule | Per-call work is invariant: `invntt16_asm` handles 864/6 = 1152/8 = 144 coefficients either way; `packed_i9` handles 72 values either way. Instruction multiset unchanged, so the A76 schedule stays legal | 2026-09-17 |
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

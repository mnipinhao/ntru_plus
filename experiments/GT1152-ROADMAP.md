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
| G2 | Active | Degree-4 range and scale bound chain | Every bound stated with its proof method and witness; the `basemul_rinv` normalization decision resolved; `ring-profile.yml` ranges section filled |
| G3 | Next | Forward NTT eight-bank port (`ntt_top.S`, `ntt_tail.S`, `ntt9.S`, `ntt.S`) | Standalone differential against the G1 oracle on Pi 5 over all 1152 coefficients, random and boundary inputs; ABI and memory contract recorded. No performance claim |
| G4 | Next | Degree-4 `basemul` / `basemul_add` (NEON intrinsics C) | Oracle differential plus the G2 bounds holding in practice, including alias tests |
| G5 | Next | Degree-4 `basemul_rinv` and BaseInv | Oracle differential; non-invertible-input failure path constant-time and zeroizing; alias and wipe |
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
| D7 | Proposed: normalize `basemul_rinv` output to abs ≤ 2497 | Lets the whole 864 inverse bound chain be inherited and re-verified instead of re-derived. **Not yet confirmed — G2 owns this** | 2026-09-17 |

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
- 864's degree-3 leaves do not tile an 8-lane int16 vector; 1152's degree-4
  leaves tile exactly 2 per vector. This is why `pack_*.S` is 45% of the 864
  codebase and why 1152 should not inherit it.
- Conversely 1152's basemul is a 16-product schoolbook against 864's 9-product,
  so base multiplication is where 1152 gets harder.

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

- Any degree-4 range or scale bound (G2).
- Any GT-domain byte layout or wire permutation for 1152 (G3).
- Any performance measurement whatsoever. Nothing has run on hardware.

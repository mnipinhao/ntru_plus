# NTRU+768 Official AVX2: HT Forward, keygen R² fold and HT inverse on the Keccak candidate

Date 2026-09-24, branch `official-opt-lazy-864-1152` (from `c3b9fdc` = `origin/avx2-official-opt`, not pushed).
This covers Phase A (code and correctness) and a same-ELF diagnostic. No SUPERCOP campaign and no
Native timing were run.

| | |
|---|---|
| Experiment | `NTRU+768/experiments/avx2_official_opt_freeze_001` (`ht_candidate:` section of `STATUS.yml`) |
| Base | `avx2-officialopt-lazy-freeze-keccak-768-exp001` (`src/kem_lazy_freeze2op_keccak.c`, unchanged) |
| Candidate | `avx2-officialopt-lazy-freeze-keccak-ht-768-exp001` = base + HT Forward + keygen R² fold + HT inverse (`src/kem_lazy_r2fold_freeze2op_keccak_ht_htinv.c`) |
| Controls | `ht_only`, `r2fold_only`, `htinv_only`, `ht_r2fold` (= candidate without the inverse) |
| Shared tooling | `common/official_opt_ht/` (new): `ht.mk`, `tools/`, `tests/`, `range_proof_ht/`, `bench/` |

All paths are under `ntruplus-ntt-Optimized/Additional_Implementation/avx2/`. The source study is the
scratch `hwang-gt768` prototype (exchange-network searches, pass fusion, BaseMul R² timing). Hwang's
`NTRU_Prime_truncation` (CC0) was read for reference only; no code was copied.

## The changes

### 1. HT Forward (`asm/ntruplus768_officialopt_ntt_ht.s`)

This is a drop-in for the caller-lazy Forward. It keeps the same decomposition, twiddle
representatives, Montgomery domain, output layout and caller contract (no terminal Barrett). It
changes two things:

- **Pass A.** Level 0 (the x^768 − x^384 + 1 split, with its raw `zeta1` product) and the level-1
  radix-3 butterflies are fused into one pass that handles 6 vectors per iteration. The radix-3
  constants are the Official broadcast dwords. They are stored as 32-byte vectors so they can be
  memory operands, because all 16 YMM registers are live.
- **Official level 2, verbatim.**
- **One block pass for levels 3–6 on each 128-coefficient block**, taking natural input order.
  It uses the unpack-only exchange network: `L(d32) L(d16) vperm2i128 L(d8) unpck{l,h}wd
  unpck{l,h}dq unpck{l,h}dq L(d4)`. That is 32 shuffle uops per block, against Official's 48.
  The output layout is exactly Official's (register r, lane l of block b = coefficient 128b + 8l + r).

Per call, dynamic instructions drop from 2003 to 1710. Of that, `vmovdqa` goes from 436 to 304 and
shuffles from 288 to 192. The arithmetic is identical.

### 2. Keygen R² fold

Official `poly_basemul` works in two steps. It first computes a Montgomery core, where every
coefficient is congruent to the base product times R⁻¹, with R = 2¹⁶. It then runs a separate pass
that multiplies by R in the Montgomery domain: `mont(c, R2)`, 48 vectors.

Both keygen products multiply by a BaseInv output. BaseInv's single field inversion first scales
its input by R3 = R³ (`fqinv_batch`: `inv = fqmul(pc2[2], R3)`). The fold changes that one constant
pair to R2 = R² (867 / 2787), and keygen uses the BaseMul core without the R² pass
(`asm/ntruplus768_officialopt_basemul_nor2.s`). Encap and Decap keep Official `poly_basemul`.
The saving is 2 × 48 Montgomery vectors per keypair, with nothing added.

Proof (`tools/prove_keygen_r2fold.py` → `results/ht-phase-a/r2fold-proof.json`):

1. `fqmul(a, b) · R ≡ a·b (mod q)` for all int16 a, b. Here `a·b − m·q ≡ 0 (mod 2¹⁶)`, so the
   difference of the two high halves is exact. This was checked exhaustively for every constant
   used, plus on 2²² random pairs.
2. `fqinv(x) ≡ x^(q−2) · R⁻³⁴ (mod q)`, checked exhaustively over all 65536 int16 x. So for a
   unit u, `fqinv(u·x) ≡ u⁻¹ · fqinv(x)`, and `fqinv(x) ≡ 0` iff `x ≡ 0`.
3. Outside `fqmul`, `fqinv_batch` and `poly_baseinv_2` contain no addition (audited on the
   generated source). The value `inv` enters every output exactly once. `fqmul(P, R2) ≡ R⁻¹ ·
   fqmul(P, R3)`, so `inv' = R·inv` and `finv' ≡ R·finv` in every lane. The zero check runs before
   the fold, so the status and the zeroed failure output are unchanged.
4. The core is bilinear: `core(a, R·finv) ≡ R·core(a, finv) ≡ poly_basemul(a, finv) (mod q)`.
5. `poly_tobytes` (and the 2-op-freeze variant) is canonical on every int16, so pk and sk are
   byte-identical.

Bounds: `finv'` is an fqmul output (|x| ≤ 18112; observed [−2278, 2230]). An interval replay of
`basemul_nor2` on the keygen f̂/ĝ domain and the BaseInv envelope has no signed-word overflow and
gives output [−10446, 10448].

### 3. HT inverse (`asm/ntruplus768_officialopt_invntt_ht.s`, optional item)

Official `poly_invntt_scale` has four passes. The HT inverse replaces the first two with one block
pass for levels 6–2 on each 128-coefficient block. The pass starts from the NTT layout and ends in
natural order, using the matching unpack network:

`L(d4, Barrett) unpck wd (register bit 1) unpck wd (bit 0) unpck qdq (bit 2) L(d8) L(d16)
L(d32, Barrett) vperm2i128 L(d64)`

It needs 32 shuffle uops per block against Official's 48, and there is no separate level-2 pass.
Levels 1 and 0 are Official's code, verbatim. Dynamic instructions drop from 2465 to 2226.

The fused level-1+0 pass (Hwang style, 6 vectors per iteration) was also built and proven
bit-identical, but it was slower and was dropped:

- quick rdtsc: 1164 TSC against Official's 1119 (the block-only form: 1096);
- the cause was not isolated (all 16 YMM live, 28 constant memory operands per iteration);
- `generate_inverse_ht.py --emit-rejected-fused PATH` regenerates it for re-measurement.

## How bit-identity is proven

`tools/symexec.py` executes the AVX2 assembly exactly and symbolically:

- every lane is an interned linear form over Z/2¹⁶;
- the atoms are the inputs, `vpmulhw` / `vpmulhrsw` products, and non-constant `vpmullw` products;
- add, sub, multiply-by-constant and word shifts are ring operations;
- shuffles are exact lane moves.

If two programs give equal output forms, they compute the same int16 function for every input.
The executor's semantics were validated against the real lazy Forward and the real Official inverse
on random full-int16 inputs.

The generators work as follows:

- **Twiddles.** They take the twiddles from the reference: every per-lane (ζ, ζ·qinv) is the pair the
  lazy Forward (or Official inverse) applies to the same operand form. No twiddle is recomputed.
- **Output check.** They require that all 768 output words of the emitted asm have the reference's
  forms. This holds for the HT Forward against the lazy Forward, and for the HT inverse against Official.

The lazy Forward's range proof carries over unchanged. The interval replay (`range_proof_ht/prove_ht.py`,
which reuses `official_opt_lazy/range_proof` read only) confirms this independently:

- the HT and lazy per-lane intervals are identical on all 5 caller domains;
- the bounds equal `EXPECTED_LAZY[768]`;
- the inverse intervals equal Official's on the Decap domain (output [−1891, 1891], consumed by
  crepmod3, which is total on int16).

## Gates (all pass)

| Gate | Result | Evidence (`results/ht-phase-a/`) |
|---|---|---|
| 1 generators `--check` + structure/proof | pass. The HT Forward and HT inverse symbolic equality hold for all 768 words. Every existing generator's `--check` still passes. | `ht-forward-generation.json`, `ht-inverse-generation.json`, `r2fold-generation.json` |
| 1 Forward differential | 55375 cases, HT == lazy word for word | `closure-tests.log` |
| 1 range proof | pass (interval replay + consumers + fold BaseMul + inverse) | `ht-range-proof-summary.json` |
| 2 R² fold proof + keygen differential | pass | `r2fold-proof.json`, `closure-tests.log` |
| 3 KEM, candidate + 4 controls | 100 vectors byte-exact vs Official; invalid/noncanonical PK/CT/SK; forced g and f retries | `closure-tests.log` |
| 3b inverse differential | 26539 cases bit-exact vs Official | `closure-tests.log` |
| 4 ASan + UBSan + LSan | 13 binaries pass | `closure-tests.log` |
| 4 linked audit | pass | `ht-linked-summary.json` |
| mutation | 12/12 rejected | `ht-mutation-check.json` |

Details for the table rows:

- **Forward differential coverage.** The 55375 cases are:
  - the 5 lazy caller domains, 5075 cases each;
  - 10000 real producer outputs (cbd1, triple, f+1, sotp_encode, crepmod3);
  - 20000 uniform int16 polys.

  They also check that Barrett(HT) == Official on the caller domains, with canaries.
- **Keygen differential coverage.**
  - 12000 keygen f/g seeds, plus 4000 uniform and 2000 zero-base BaseInv inputs. The status is
    identical in every case (2007 failures). `finv'` == R·`finv`, `nor2` == BaseMul (mod q), and
    tobytes matches.
  - 10000 KAT-DRBG keypair seeds, on each of 3 fold KEMs (lazy_r2fold, r2fold_only, candidate),
    byte-exact against Official. This includes 104 forced g = 0 retries and 112 forced f failures,
    and randombytes consumption is equal.
- **Linked audit contents.**
  - Entries and RIP tables are 32-byte aligned. Each entry has one ret, and no stack use, calls or
    vzeroupper.
  - The linked stream equals the assembled source.
  - Candidate KEM calls: 6 × HT Forward, 0 × lazy / `poly_ntt`, 1 × HT inverse, 0 ×
    `poly_invntt_scale`, 2 × fold BaseInv, 0 × `poly_baseinv`, 2 × `nor2`, 2 × `poly_basemul`
    (Encap/Decap), and 7 × freeze2op tobytes.
- **Mutation check.**
  - 5 Forward and 4 inverse mutants: rejected by both the symbolic proof and the C differential.
  - 3 fold / `nor2` mutants: rejected by the keygen differential.

## Same-ELF diagnostic (`supercop-derived`, not Native)

Setup:
- `common/official_opt_ht/bench/bench_ht_diag.c`, `ht.mk` `ht-bench` (O3GC recipe);
- cpucycles `default-perfevent` from the read-only campaign `supercop-campaign-lazy-864-1152-20260923-001`;
- CPU 1, ASLR on, 31 fresh launches per link order, 14 blocks × 32 observations per variant per launch;
- both batches ran under `phase_b_batch.py` and were clean on attempt 0.

Every delta is between identical `cpucycles()` anchors, so the null-call overhead cancels.
The keypair region reseeds the KAT DRBG per bank for every variant, so it is seed-matched.
Deltas are pooled StQ2 cycles, with favourable launches out of 31 in brackets.

### Components

| | normal | reversed | Reference StQ2 |
|---|---|---|---|
| Forward: HT − lazy | −28.4 (31) | −28.9 (31) | 850 / 852 |
| keygen BaseMul: nor2 on R·finv − Official | −81.0 (31) | −81.6 (31) | 722 / 725 |
| BaseInv: fold − Official (same code, separate TU) | +14.8 (0) | +0.8 (6) | 1243 / 1247 |
| inverse: HT − Official | −24.4 (31) | −16.8 (31) | 961 / 967 |

### KEM, variant − base

| | keypair normal | keypair reversed | encap normal | encap reversed | decap normal | decap reversed |
|---|---|---|---|---|---|---|
| candidate | −326.5 (31) | −197.9 (31) | −49.8 (31) | −50.4 (30) | −74.7 (31) | −79.5 (31) |
| ht_only | −133.0 (31) | −63.1 (30) | −55.3 (31) | −60.5 (31) | −77.7 (31) | −71.7 (31) |
| r2fold_only | −236.6 (31) | −97.7 (29) | −3.4 (17) | −18.2 (23) | −3.7 (19) | −13.8 (25) |
| htinv_only | −18.7 (20) | +42.6 (8) | −6.9 (20) | −21.4 (24) | +12.3 (10) | −6.0 (22) |
| ht_r2fold | −281.6 (31) | −160.7 (31) | −56.0 (31) | −66.8 (31) | −85.4 (31) | −44.0 (31) |

The inverse increment inside the candidate is measured as candidate − ht_r2fold:

| | normal | reversed |
|---|---|---|
| keypair | −44.8 (27) | −37.3 (26) |
| encap | +6.2 (10) | +16.4 (7) |
| decap | +10.7 (8) | −35.5 (30) |

Candidate − Official: keypair −4869 / −4613, encap −7615 / −7885, decap −4286 / −4404 (normal / reversed).

### Reading

- **HT Forward.** The Forward component gain, −28 to −29 per call, holds in 31/31 launches in both
  link orders. It shows up at KEM level as about −50 to −78 per op (2 Forwards each) in both orders.
- **R² fold.** The fold removes −81 per keygen BaseMul in both orders. The r2fold_only keypair
  delta is −237 / −98. Expected is 2 × −81 plus BaseInv noise, and the keypair is the most
  placement-sensitive op.
- **Base-invariant ops.** r2fold_only encap and decap (which it does not change) sit at −4 to −18.
  That is the placement noise floor.
- **HT inverse.** The inverse is a robust component win (31/31 both orders). Its expected
  ~−20 per Decap is below that noise floor: htinv_only − base on decap is +12 / −6, and
  candidate − ht_r2fold on decap is +11 / −36. It stays in the candidate because it is
  bit-identical and cheaper as a component. Its KEM-level effect is **not resolved**.
  `ht_r2fold` is the ready-made candidate without it.
- **Next step.** Deciding any of this for production needs Native SUPERCOP (Phase B). No promotion.

## Reproduce

```
E=ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_freeze_001
L=../../../common/official_opt_lazy/tools; H=../../../common/official_opt_ht/tools
cd $E
make ht-phase-a        # generators --check, all HT tests (release + ASan/UBSan/LSan), range proof,
                       # R^2 fold proof, linked audit, mutation check
make ht-record         # the same, then copies curated evidence to results/ht-phase-a/
make ht-bench
python3 $L/phase_b_batch.py --result-dir results/ht-diag-normal-TAG --metadata metadata.json -- \
  python3 $H/run_ht_diag.py --experiment . --launches 31 --result-dir {RESULT}
python3 $L/phase_b_batch.py --result-dir results/ht-diag-reversed-TAG --metadata metadata.json -- \
  python3 $H/run_ht_diag.py --experiment . --launches 31 --binary build/bench_ht_diag_swapped --result-dir {RESULT}
make generate-ht       # regenerate (writes) asm/src from the pinned inputs
python3 $H/generate_inverse_ht.py --experiment . --check --emit-rejected-fused /tmp/fused.s   # dropped variant
```

Notes:
- The shared KEM test prints its "caller-lazy KEM byte differential" banner for every variant. The
  binary name tells you which one was tested.
- The HT Forward and inverse assume the Official 32-byte `poly` alignment (`vmovdqa`), the same as
  Official.
- The keygen test and the diagnostic put the AVX2 `poly.h` before the reference KAT include
  directory. The reference `poly.h` has no alignment attribute.

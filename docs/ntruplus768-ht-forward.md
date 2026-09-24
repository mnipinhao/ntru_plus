# NTRU+768 Official AVX2: HT Forward, keygen R² fold and HT inverse on the Keccak candidate

Date 2026-09-24, branch `official-opt-lazy-864-1152` (from `c3b9fdc` = `origin/avx2-official-opt`, not pushed).
This covers Phase A (code and correctness) and a same-ELF diagnostic (2026-09-24), and Phase B
(qualification export, Native SUPERCOP and ASLR-on fixed-ELF paired timing, 2026-09-25); see
[Phase B](#phase-b-native-supercop-2026-09-25). Result: a robust research win vs the Keccak base for
keypair, encap and decap under the decision rule; the encap gain (−75 cycles, −0.4%) is small and its
reversed-placement paired CI is positive (flagged). `promotion: none`.

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
- **Next step.** Deciding any of this for production needs Native SUPERCOP (Phase B, below). No promotion.

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

## Phase B: Native SUPERCOP (2026-09-25)

Worktree `ntru_plus-official-opt-864-1152`, branch `official-opt-lazy-864-1152`, from `34ba1a8`
(= `origin/avx2-official-opt`). Not pushed. Everything ran on CPU 1 of the Core Ultra 7 155H with ASLR on
(`randomize_va_space=2`). The host controls were read and left unchanged (`performance` governor,
`intel_pstate/no_turbo=1`). Every timing batch ran under `phase_b_batch.py`, strictly one after another,
with nothing built while timing ran. Campaign: `/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001`.

### Qualification export

`common/official_opt_ht/tools/export_ht_flat.py` (`make ht-qualification`; `make ht-qualification-check`
regenerates into a temporary directory and requires the export and manifest to be identical) writes
`qualification/avx2-officialopt-lazy-freeze-keccak-ht-qual001` and its manifest (`kind: ht-qualification-source`).
It runs no compiler and refuses to overwrite.

| | |
|---|---|
| Export | `avx2-officialopt-lazy-freeze-keccak-ht-qual001`, tree SHA-256 `50b22a3f2000bca8325ac9431deb906880b61b24a13892252999726e10304bb6` |
| Base export | `avx2-officialopt-lazy-freeze-keccak-qual001` (tree `6209ebac…`), all 36 files kept except `kem.c` |
| Added (exact Phase-A bytes) | `ntt_ht.s` (`8f4bdb30…`), `invntt_ht.s` (`999388bb…`), `basemul_nor2.s` (`f40f77a2…`), `baseinv_r2fold.c` (`4138c98f…`) |
| `kem.c` | the two Phase-A overlay heads (`#define poly_invntt_scale …_invntt_ht`, `#define …_ntt_caller_lazy …_ntt_ht`) + the base `kem.c` with its verbatim `src/kem_lazy.c` body replaced by the verbatim `src/kem_lazy_r2fold.c` |

What the exporter checks:

- the base manifest matches `bench/supercop.lock`, and the base tree matches its manifest (tree and every file);
- the base `kem.c` is exactly `src/kem_lazy_freeze2op.c` with `src/kem_lazy.c` inlined;
- each added file's SHA-256 equals its `results/ht-phase-a/*-generation.json` record, and
  `generate_ht_overlays.py --check` and `generate_keygen_r2fold.py --check` pass;
- each overlay head is a comment plus exactly one `#define`. The only Phase-A chain lines not carried over
  are the three repo-only Keccak includes of `src/kem_lazy_r2fold_freeze2op_keccak.c` (`util.h`,
  `fips202_mlkem.h`, `keccak_names.h`). In the flat tree `fips202.h` *is* the mlkem-native adapter and
  `hash_f/g/h` keep their Official names, exactly as in the base export.

The `kem.c` diff against the base export is 26 added and 4 changed lines: 13 lines of overlay heads (comments plus
two `#define`s), the r2fold comment, 2 prototypes and the 4 keygen call lines (2 × `poly_baseinv` →
`…_baseinv_r2fold`, 2 × `poly_basemul` → `…_basemul_nor2`). The full unified diff is in the manifest
(`kem_c.unified_diff_vs_base`).

**The flat tree is what Phase A tested** (`make ht-flat-record` → `results/ht-phase-b/`):

- **KEM test.** Every export file is compiled from the export directory (its own `fips202.h`). Only
  `kem.c` is renamed to `official_lazy_*`. It is linked against the pinned Official `kem.c` (`official_ref_*`,
  with its `hash_*` renamed so that both copies link) and driven by the shared `test_kem_lazy.c`. Result: 100
  vectors pk/sk/ct/ss byte-exact, invalid PK/CT/noncanonical CT/SK, forced g retry and one-shot f injection.
  It passes in release and ASan+UBSan+LSan builds (`closure-tests.log`).
- **Linked audit** (`audit_ht_linked.py` flat mode, `flat-linked-summary.json`). The entries match the
  export's `.s` assembled alone (the same sizes as Phase A: 1526 / 1179 / 1733 bytes). The flat `kem.c` object
  has 6 × HT Forward, 1 × HT inverse, 2 × fold BaseInv, 2 × `nor2`, 2 × `poly_basemul` (Encap/Decap),
  7 × freeze2op tobytes and 0 × lazy / `poly_ntt` / `poly_invntt_scale` / `poly_baseinv`.
- **Object identity.** The flat `kem.o`, `baseinv_r2fold.o`, `symmetric.o`, `mlk_fips202.o` and
  `mlk_keccakf1600.o` equal the Phase-A objects (`kem_lazy_r2fold_freeze2op_keccak_ht_htinv.o`, the fold BaseInv,
  `symmetric_keccak.o`, the vendored mlk objects) in section headers, contents, relocations and symbols. The
  only differences are the file symbol and the repo-only `ntruplus768_keccak_hash_*` → `hash_*` names. A
  negative control (the flat `kem.o` against the `ht_r2fold` object) is rejected.
- **do-part try emulation** (scratch, `flat-supercop-try.json`). The export and both reversed copies compile
  with 0 warnings and reproduce the pinned checksums for O3/Os/O2/O.

`install_qualification.py` now accepts `ht-qualification-source`, and existing kinds are unchanged. It installed the
export into the campaign, and the installed base export re-hashes to its manifest. `install_reversed_placement.py` now
accepts `--param 768` (the same renames as the 768 experiment tool) and renames `ntt_ht.s` → `bbb_ntt_ht.s` and
`basemul_nor2.s` → `zzz_basemul_nor2.s`, next to the files they replace. `invntt_ht.s` stays, like `invntt.s`.
Reversed copies: `avx2-officialopt-lazy-freeze-keccak{,-ht}-qual001-reversed` (`PLACEMENT.json` in each).

**SUPERCOP try passes.** In all 27 Native batches `try` reported `ok` for O3/Os/O2/O with
checksumsmall/checksumbig equal to the pinned `crypto_kem/ntruplus768/checksum*` (= Official), and so did the
five O3GC fixed builds (`summarize_extended_multi.py` fails on any mismatch).

### Design

- **Native:** roles `official` (`avx2`), `base` (`avx2-officialopt-lazy-freeze-keccak-qual001`) and `ht`
  (`avx2-officialopt-lazy-freeze-keccak-ht-qual001`). Each role had 81 fresh launches: 9 rounds of one
  9-launch `run_supercop_benchmark.py --mode native-kem` batch per role, with the role order rotated. SUPERCOP
  used its default compiler selection and the unmodified `measure.c`. Roles are pooled independently. CIs
  resample launches within each role (2,000 resamples). Tag `20260925h`.
- **Compiler picks:** official O2 ×8, O3 ×1; base O3 ×9 (`243d2fcd…`); ht O3 ×9 (`3b64cb27…`). Base and ht always
  got the same compiler, so the picks are not confounded and no fixed-`-O3` run was needed.
- **Paired:** one O3GC fixed ELF per role and placement (`bench/supercop/okc-o3gc.sh`, `--fresh-launches 1`).
  The official (`d9fba9ad…`) and base (`708a4f1b…`) ELFs are byte-identical to the Keccak Phase-B builds; ht is
  `4aa840db…`, base-reversed `a775dd0c…` and ht-reversed `d5fb9db3…`. `run_paired_aslr_on.py` ran 48 ABBA/BAAB blocks
  (192 fresh launches) per run: ht vs base with normal placement (primary), ht vs base reversed (secondary), and
  ht vs official normal.
- **Hygiene:** 35 batches (27 Native, 5 fixed builds, 3 paired), all accepted on attempt 0 and none contaminated.
  Pre-batch 1-minute load was 0.25–0.50. The campaign `okc-amd64` was re-checked after every batch and was unchanged (`82f1eea7…`).

### Native, default SUPERCOP compiler selection (81 launches per role)

| Op | Official | Base | HT | HT − Base [95% CI] fav./81 | HT − Official [95% CI] fav./81 | Base − Official |
|---|---:|---:|---:|---:|---:|---:|
| Keypair | 21,611.5 | 16,862.3 | 16,598.9 | **−263.4** (−1.56%) [−275.4, −251.8] 81/81 | −5,012.7 (−23.2%) [−5,030.2, −4,996.9] 81/81 | −4,749.3 |
| Encap | 28,174.3 | 20,531.1 | 20,455.9 | **−75.2** (−0.37%) [−94.2, −58.0] 67/81 | −7,718.4 (−27.4%) [−7,756.9, −7,686.6] 81/81 | −7,643.1 |
| Decap | 19,461.7 | 15,051.0 | 14,960.0 | **−91.0** (−0.60%) [−102.3, −80.3] 79/81 | −4,501.7 (−23.1%) [−4,515.5, −4,486.7] 81/81 | −4,410.7 |

The values are pooled StQ2 cycles. "fav." counts candidate launches below the baseline's median launch. All
9 per-batch HT − Base deltas are negative for every op:

- keypair: −217 … −284, SD 20;
- encap: −38 … −127, SD 28;
- decap: −62 … −117, SD 20.

### Fixed-ELF paired, O3GC, ASLR on, 48 blocks (mean [block-bootstrap 95% CI] favourable/48)

| Op | HT vs Base, normal (primary) | HT vs Base, reversed (secondary) | HT vs Official, normal |
|---|---:|---:|---:|
| Keypair | **−292.8** [−302.6, −282.9] 48/48 | −187.6 [−200.5, −174.3] 48/48 | −5,098.3 [−5,116.8, −5,081.6] 48/48 |
| Encap | **−61.0** [−78.7, −44.1] 42/48 | **+24.4 [+6.2, +42.4] 14/48** | −7,725.2 [−7,760.3, −7,693.2] 48/48 |
| Decap | **−99.1** [−106.8, −91.7] 48/48 | −106.8 [−116.5, −97.3] 48/48 | −4,449.8 [−4,467.2, −4,432.6] 48/48 |

Restricted to the retry-0 stratum (no BaseInv retry), the normal-placement keypair delta is −288.6 [−298.5, −278.5], 48/48.
For comparison, the Phase-A same-ELF diagnostic (normal /
reversed link order) gave keypair −327 / −198, encap −50 / −50 and decap −75 / −80.

### Decision (rule: Native default-selection pooled HT − Base < 0 AND normal-placement ASLR-on paired 95% CI < 0)

| Op | Native HT − Base | Paired normal | Paired reversed | Verdict |
|---|---|---|---|---|
| Keypair | −263.4 [−275.4, −251.8] | [−302.6, −282.9] | [−200.5, −174.3] | **robust research win** |
| Encap | −75.2 [−94.2, −58.0] | [−78.7, −44.1] | [+6.2, +42.4] | **robust research win**, flagged: reversed disagrees |
| Decap | −91.0 [−102.3, −80.3] | [−106.8, −91.7] | [−116.5, −97.3] | **robust research win** |

Against Official, the same rule gives a robust research win for all three ops (−23% / −27% / −23%). This is
the Keccak win plus the HT increment.

Reading:

- **Keypair** is the largest effect, and it is conclusive without the seed-matched harness: Native CI far below zero,
  81/81 launches, every batch. The Native value (−263) sits between the two same-ELF link orders (−327 / −198),
  and so does the paired normal/reversed pair (−293 / −188). Most of it is the R² fold (2 × −81) plus
  2 × HT Forward (−28 each).
- **Decap** is consistent everywhere (−91 Native; −99 / −107 paired), a little more than 2 × HT Forward
  (−57) + HT inverse (−24).
- **Encap** is a small effect, −75 Native (0.37%), with 67/81 launches favourable. The normal-placement paired CI
  is below zero, but the reversed-placement build is **slower by +24 [+6, +42]**. The same-ELF diagnostic
  gave −50 in both link orders, so the HT Forward arithmetic saving (2 × −28) is real. At SUPERCOP's archive
  member order, though, it is small enough that code placement can cancel or reverse it. The encap verdict
  passes the rule as written but is **placement-sensitive**.
- **HT inverse.** It is not separately resolved in Phase B: only the full candidate was exported. Decap's
  Native increment (−91) is consistent with including it, but it was not isolated.

`promotion: none`, and `clean/` was not touched. Details: `STATUS.yml` `ht_candidate.phase_b` and
`results/extended-multi-summary-20260925h.json`.

### Reproduce Phase B

```sh
REPO=/home/nuc/src/ntru_plus-official-opt-864-1152
A=$REPO/ntruplus-ntt-Optimized/Additional_Implementation/avx2; T=$A/common/official_opt_lazy/tools
E=$A/NTRU+768/experiments/avx2_official_opt_freeze_001; R=$E/results
C=/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001; TAG=20260925h
B=avx2-officialopt-lazy-freeze-keccak-qual001; H=avx2-officialopt-lazy-freeze-keccak-ht-qual001
(cd $E && make ht-qualification-check && make ht-phase-a && make ht-flat-record)   # export committed; make ht-qualification recreates it
python3 $T/install_qualification.py --param 768 --campaign-root $C --export-root $E/qualification/$H
python3 $T/install_reversed_placement.py --param 768 --campaign-root $C --baseline $B --candidate $H
python3 $T/run_extended_native.py --param 768 --experiment $E --campaign-root $C --tag $TAG --batches 9 --order rotate \
  --role official=avx2 --role base=$B --role ht=$H
for spec in official:normal:avx2 base:normal:$B ht:normal:$H base:reversed:$B-reversed ht:reversed:$H-reversed; do
  role=${spec%%:*}; rest=${spec#*:}; place=${rest%%:*}; impl=${rest#*:}
  python3 $T/phase_b_batch.py --result-dir $R/fixed-ht-$role-$place-$TAG --metadata metadata.json -- \
    python3 $REPO/scripts/run_supercop_benchmark.py --campaign-root $C --parameter 768 --implementation $impl \
    --cpu 1 --mode native-kem --fresh-launches 1 --compiler-wrapper $REPO/bench/supercop/okc-o3gc.sh \
    --require-frequency-control --result-dir {RESULT}
done
pair() { # name baseline-elf candidate-elf placement
  python3 $T/phase_b_batch.py --result-dir $R/paired-aslr-on-$4-$1-$TAG --metadata manifest.json -- \
    python3 $T/run_paired_aslr_on.py --official $2 --candidate $3 --placement $4 --cpu 1 --blocks 48 \
    --compiler-recipe O3GC --output {RESULT}
  python3 $REPO/scripts/summarize_supercop_paired.py --campaign $R/paired-aslr-on-$4-$1-$TAG --parameter 768; }
pair ht-vs-base $R/fixed-ht-base-normal-$TAG/measure $R/fixed-ht-ht-normal-$TAG/measure normal
pair ht-vs-base $R/fixed-ht-base-reversed-$TAG/measure $R/fixed-ht-ht-reversed-$TAG/measure reversed
pair ht-vs-official $R/fixed-ht-official-normal-$TAG/measure $R/fixed-ht-ht-normal-$TAG/measure normal
python3 $T/summarize_extended_multi.py --param 768 --experiment $E --tag $TAG --order rotate --roles official,base,ht \
  --comparison ht:base --comparison ht:official --comparison base:official \
  --paired ht:base=ht-vs-base-$TAG --paired ht:official=ht-vs-official-$TAG
```

Curated evidence: `results/ht-phase-b/` (flat KEM test log, flat linked audit + object identity, try emulation),
`results/native-ext-{official,base,ht}-b{1..9}-20260925h/`, `results/fixed-ht-*-20260925h/`,
`results/paired-aslr-on-{normal,reversed}-ht-vs-base-20260925h/`, `results/paired-aslr-on-normal-ht-vs-official-20260925h/`
(`metadata.json` / `manifest.json`, `stq-summary.json` / `summary.json`, `supercop.lock`) and
`results/extended-multi-summary-20260925h.json`. Raw launch output, `data`, `run.out`, the `measure` ELFs and
`host-hygiene.json` stay local (Git-ignored).

### Deviations and notes

- **No seed-matched keypair run.** Keypair was conclusive under the rule.
- **Test-only renames in the flat KEM test.** The Official reference's `hash_f/g/h` were renamed so that it can
  link beside the flat tree's own `symmetric.c`. The flat side is compiled from the export unchanged except for the
  `crypto_kem_*` rename every KEM test uses. It is compiled without `-DSUPERCOP`, like Phase A; the `-DSUPERCOP`
  path is covered by `try`.
- **do-part try emulation.** It reuses `export_keccak_flat.py`'s `try_tree()` as a library call in scratch, so no
  new tool was added for it. The real `try` evidence is the Native batches.
- **Unused members.** The base export's unused `ntt_caller_lazy.s` (and Official `ntt.s`/`invntt.s`) stay in the tree.
  Only archive members that resolve a symbol are linked, as in the base export.
- **Reversed placement is secondary.** It is a different archive member order, not a mirror of the normal
  order, so its encap sign flip is a placement observation and not a failure of the rule.

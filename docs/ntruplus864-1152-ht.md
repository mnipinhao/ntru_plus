# NTRU+864 / NTRU+1152 Official AVX2: HT Forward and keygen R² fold on the Keccak candidates

Date 2026-09-25, branch `official-opt-lazy-864-1152` (from `17ff1b8`, local, not pushed). This is the port of
the NTRU+768 HT work ([ntruplus768-ht-forward.md](ntruplus768-ht-forward.md)) to NTRU+864 and NTRU+1152:
**HT Forward + keygen R² fold, no HT inverse.** Each parameter went through Phase A (code and correctness),
a same-ELF diagnostic, a flat qualification export and Phase B (Native SUPERCOP and ASLR-on fixed-ELF paired
timing), in that order, one parameter at a time for all timing. `promotion: none`.

**Result.** Both items are robust component wins for both parameters (same-ELF, 31/31 launches in both link
orders). Under the decision rule (Native default-selection pooled HT − Base < 0 AND normal-placement ASLR-on paired
95% CI < 0) all six (parameter, op) pairs are **robust research wins** vs the Keccak base and vs Official:

| HT − Base | Keypair | Encap | Decap |
|---|---|---|---|
| NTRU+864 Native (81/role) | **−383.0** [−396.5, −369.3] | **−93.7** [−112.1, −75.8] | **−137.5** [−150.5, −124.5] |
| NTRU+864 paired normal / reversed | −376.5 / −307.2 | −133.8 / −147.7 | −161.2 / −196.8 |
| NTRU+1152 Native (81/role) | **−259.9** [−549.8, +30.4] | **−144.7** [−176.4, −108.8] | **−116.7** [−132.6, −101.9] |
| NTRU+1152 paired normal / reversed | −260.8 [−508.3, −4.0] / −262.7 [−552.6, +30.7] | −133.6 / −89.8 | −109.5 / −23.9 |

The **1152 keypair is the weak one**: it passes the rule as written, but only just (paired normal CI upper bound
−4.0), its Native CI and its reversed-placement paired CI both cross zero, because of the BaseInv retry tail. The
clearly labelled supporting seed-matched harness (identical coins, so identical retries, on both sides) gives
**−325.9 [−350.1, −299.4], 18/18 launches**, negative in every retry stratum. All other CIs are below zero in both
placements.

| | NTRU+864 | NTRU+1152 |
|---|---|---|
| Experiment | `NTRU+864/experiments/avx2_official_opt_001` | `NTRU+1152/experiments/avx2_official_opt_001` |
| Base | `avx2-officialopt-lazy-codec-keccak-864-exp001` (`src/kem_lazy_codec_direct_keccak.c`: lazy Forward, direct 12-bit codec, mlkem-native Keccak) | `avx2-officialopt-lazy-freeze-keccak-1152-exp001` (`src/kem_lazy_freeze2op_keccak.c`: lazy Forward, 2-op freeze, mlkem-native Keccak) |
| Candidate | `avx2-officialopt-lazy-codec-keccak-ht-864-exp001` = `src/kem_lazy_r2fold_codec_direct_keccak_ht.c` | `avx2-officialopt-lazy-freeze-keccak-ht-1152-exp001` = `src/kem_lazy_r2fold_freeze2op_keccak_ht.c` |
| Controls | `ht_only` = `src/kem_lazy_codec_direct_keccak_ht.c`, `r2fold_only` = `src/kem_lazy_r2fold_codec_direct_keccak.c` | `ht_only` = `src/kem_lazy_freeze2op_keccak_ht.c`, `r2fold_only` = `src/kem_lazy_r2fold_freeze2op_keccak.c` |
| Base export | `avx2-officialopt-lazy-codec-keccak-qual001` (tree `0deb127b…`) | `avx2-officialopt-lazy-freeze-keccak-qual001` (tree `e88c9c6d…`) |
| HT export | `avx2-officialopt-lazy-codec-keccak-ht-qual001` (tree `847f5757…`) | `avx2-officialopt-lazy-freeze-keccak-ht-qual001` (tree `3aa2d6ae…`) |

All paths below are under `ntruplus-ntt-Optimized/Additional_Implementation/avx2/`. The scratch feasibility study
(`scratchpad/ht-864-1152/`: `gen_fwd.py`, `net864*.py`, `foldtest.c`, `bench.c`) was exploratory; the repo versions
are the deterministic, pinned generators of `common/official_opt_ht/` (below).

## Why no HT inverse

A read-only study (2026-09-24) found no 4-stage unpack-only inverse network for 864 (its block mixes base-3 and
base-2 index bits), and the 1152 inverse, where the 768 network carries over, measured 62 cycles *slower* than
Official (there is no radix-2 level 2 to fuse). The inverse stays Official `poly_invntt_scale` in both candidates.

## The changes

### 1. HT Forward

Drop-in for the caller-lazy Forward: same decomposition, twiddle representatives, Montgomery domain, output layout
and caller contract (no terminal Barrett). Both parameters have a trinomial level 0, two radix-3 levels (1 and 2) and
four radix-2 levels (3–6).

- **Pass A.** Level 0 (the x^N − x^(N/2) + 1 split with its raw `zeta1` product) fused with the level-1 radix-3
  butterflies, 6 rows per iteration, rows N/6 coefficients apart (864: 9 iterations of 288-byte rows; 1152: 12 of
  384). All 16 YMM registers are live, so the radix-3 constants (the Official broadcast dwords) are 32-byte memory
  operands, exactly as in 768.
- **Pitfall: the level-1 registers.** Unlike 768 (radix-2 level 2), the Official radix-3 level 2 of 864/1152 reuses
  `ymm2`/`ymm3` (w·qinv, w) that the Official level-1 *prologue* loads (`ntt.s:57-58`). Pass A keeps w/w·qinv in
  `ymm13`/`ymm14`, so it restores `ymm2 ← ymm14`, `ymm3 ← ymm13` before the verbatim level 2. The generator checks
  that the extracted level-2 body reads exactly `ymm0`, `ymm2`, `ymm3` before writing them, and the mutation check
  has a mutant that drops the restore (rejected by the symbolic proof and by the C differential).
- **Level 2:** the Official lazy radix-3 level-2 pass, verbatim (labels renamed).
- **Block pass (levels 3–6).**
  - **NTRU+1152:** 128-coefficient blocks in 8 registers, distances 32/16/8/4, the HT768 network unchanged:
    `L(d32) L(d16) vperm2i128 L(d8) unpck{l,h}wd unpck{l,h}dq unpck{l,h}dq L(d4)`, 32 shuffle uops per block against
    Official's 48, nine blocks. Only the twiddles differ.
  - **NTRU+864 (new network):** 96-coefficient blocks in 6 registers (two 48-groups), distances 24/12/6/3, cubic
    leaves: `vperm2i128, L(d24), unpck{l,h}wd, L(d12), unpck{l,h}wd, L(d6), unpck{l,h}wd, L(d3)`. Every stage and every
    level pairs logical registers (i, i+3), i = 0..2, and writes its lo/hi outputs to logical registers 2i / 2i+1 (a
    renaming, no instruction). 24 shuffle uops per block against Official's 36; the scratch exhaustive search found it
    to be the unique 4-stage solution. Output: register r lane l of block b = coefficient 96b + 6l + r, the lazy
    Forward's layout (stored at 32·r), so the direct 12-bit codec (which reads that layout) sees the same words.
  - Twiddles: 864 needs one (zeta, zeta·qinv) slot per level (4 slots, 256 B/block, 2304 B), 1152 the 768 slot set
    (11 slots, 704 B/block, 6336 B); plus 256 B of pass-A constants. `.rodata`, `.p2align 5`, local symbols.

| per Forward call (dynamic, symbolic executor) | 864 lazy | 864 HT | 1152 lazy | 1152 HT |
|---|---:|---:|---:|---:|
| instructions | 2524 | 2239 | 3301 | 2872 |
| `vmovdqa` | 508 | 402 | 652 | 456 |
| data-movement uops per block (vperm2i128, unpacks, 64-bit shifts, blends) | 36 | 24 | 48 | 32 |
| linked size (bytes / instruction rows) | | 1267 / 238 | | 1462 / 268 |

The arithmetic (every multiply, add and sub) is the lazy Forward's.

### 2. Keygen R² fold

Identical in structure to 768: `fqinv_batch` is textually identical in all three parameters (R3 = 460 / −16436,
`poly.c:13-14`); the fold changes the one fqinv input scale R3 → R2 (867 / 2787), which multiplies every BaseInv
output by R, and keygen uses the Official BaseMul core without its R² pass:

| | NTRU+864 | NTRU+1152 |
|---|---|---|
| fold BaseInv | `src/ntruplus864_officialopt_baseinv_r2fold.c` = `poly.c:1-371` minus `poly.c:16-39` (the `poly_tobytes`/`poly_frombytes` pack/unpack wrappers, which are not BaseInv and would duplicate poly.c symbols) | `src/ntruplus1152_officialopt_baseinv_r2fold.c` = `poly.c:1-358` |
| `poly_baseinv_2` | 3 rows per base, `fqmul` | 4 rows per base, `fqmul` / `fqmul_neg` |
| keygen BaseMul | `asm/ntruplus864_officialopt_basemul_nor2.s` = `basemul.s:1-224`, R² pass `basemul.s:226-265` removed (18 × 3 = 54 vectors) | `asm/ntruplus1152_officialopt_basemul_nor2.s` = `basemul.s:1-373`, R² pass `375-420` removed (18 × 4 = 72 vectors) |
| KEM | `src/kem_lazy_r2fold.c`: 2 × keygen BaseInv → fold, 2 × keygen BaseMul → nor2 (`kem.c:127,130`); Encap/Decap unchanged | same |

Proof (`tools/prove_keygen_r2fold.py --param N` → `results/ht-phase-a/r2fold-proof.json`): the 768 argument
unchanged (Montgomery identity exhaustive for every constant used plus 2²² random pairs; `fqinv(x) ≡ x^(q−2)·R⁻³⁴`
exhaustive over int16, hence `finv' ≡ R·finv`; BaseInv addition-free outside fqmul; the core is bilinear;
`poly_tobytes` canonical on every int16). New for 864/1152: the proof also checks that `fqmul`, `fqsqr` and `fqinv`
in the generated source are byte-for-byte the modelled 768 text.

Bounds, redone on the **lazy/HT-g domain** (the feasibility `foldtest.c` used Official `poly_ntt` for g, so its
bounds did not apply): `range_proof_ht/prove_ht.py --param N` replays `basemul_nor2` with the keygen f̂/ĝ of the HT
(= lazy, per lane) Forward and the ledger's BaseInv output envelope:

| | NTRU+864 | NTRU+1152 |
|---|---|---|
| BaseInv output envelope | \|x\| ≤ 5176 | \|x\| ≤ 4787 |
| nor2 output interval (proved) | [−8936, 8936] | [−11250, 11250] |
| Official BaseMul, same inputs | [−1838, 1838] | [−1865, 1865] |
| observed (keygen differential) finv′ / nor2 | [−2456, 2423] / [−5285, 5365] | [−2283, 2269] / [−6937, 6906] |

No signed-word overflow; the nor2 output feeds only `poly_tobytes` (pk) and the `f ⊙ ginv` tobytes (sk).

## Gates (all pass for both parameters)

| Gate | NTRU+864 | NTRU+1152 | Evidence (`results/ht-phase-a/`) |
|---|---|---|---|
| generators `--check` (pinned inputs) | pass; every existing generator `--check` still passes | pass | `ht-forward-generation.json`, `r2fold-generation.json` |
| symbolic bit-identity HT vs caller-lazy | all 864 output words | all 1152 output words | `ht-forward-generation.json` |
| interval range proof, 5 caller domains | per-lane intervals identical to lazy, = `EXPECTED_LAZY` | same | `ht-range-proof-summary.json` |
| fold identity proof + bounds (lazy/HT-g domain) | pass | pass | `r2fold-proof.json`, `ht-range-proof-summary.json` |
| Forward C differential | 57295 cases | 63055 cases | `closure-tests.log` |
| keygen differential | 12000 f/g seeds, 4000 uniform + 2000 zero-base BaseInv inputs; 10000 KAT-DRBG keypairs × 3 fold KEMs | same | `closure-tests.log` |
| shared `test_kem_lazy.c` (CANDIDATE_SHAKE256, CANDIDATE_BASEINV), candidate + 2 controls | 100 vectors byte-exact, invalid PK/CT/SK, forced g retry, forced f failure | same (85 natural keygen retries in the 100 vectors) | `closure-tests.log` |
| ASan + UBSan + LSan | 8 binaries | 8 binaries | `closure-tests.log` |
| linked audit | pass | pass | `ht-linked-summary.json` |
| mutation | 9/9 rejected | 9/9 rejected | `ht-mutation-check.json` |

Details:

- **Forward differential:** the 5 lazy caller domains (constants, alternating, all 4N impulses, 1000 random, 1000
  extreme each; 5459 / 6611 cases per domain), 10000 real producer outputs (cbd1, cbd1+triple, +1, sotp_encode,
  crepmod3) and 20000 uniform int16 polys; HT == lazy word for word, Barrett(HT) == Official on the caller domains,
  canaries intact.
- **Keygen differential:** BaseInv status identical in every case (864: 2000 failures = the 2000 forced zero bases;
  1152: 9935 failures, 2000 of them forced; the zero-base layout is per parameter: 48-word chunks of degree-3 bases for
  864, 64-word degree-4 for 1152); `finv' ≡ R·finv`; nor2 ≡ BaseMul (mod q) and tobytes equal (864: 24000 products,
  1152: 17183); 10000 KAT-DRBG seeds on `lazy_r2fold`, `r2fold_only` and the candidate byte-exact against Official,
  with 104 forced g = 0 retries and 112 forced f failures and equal randombytes consumption (1152: 7822 genuine
  BaseInv failures per KEM, identical across KEMs).
- **Linked audit:** entries and RIP tables 32-byte aligned, one ret, no stack/call/vzeroupper, linked stream ==
  assembled source. Candidate KEM object: 6 × HT Forward, 0 × lazy / `poly_ntt`, 2 × fold BaseInv, 0 × `poly_baseinv`,
  2 × nor2, 2 × `poly_basemul` (Encap/Decap), 1 × `poly_invntt_scale`; 864: 7 × `tobytes_direct` and 4 ×
  `frombytes_direct` call sites (the static `declassify_poly_frombytes` is inlined: 1 Encap + 3 Decap), 0 ×
  `poly_tobytes`/`poly_frombytes`; 1152: 7 × freeze2op tobytes. Controls checked likewise.
- **Mutants (9 per parameter):** 6 Forward mutants (block twiddle word, pass-A radix-3 constant operand, unpack lo/hi
  swap — `vpunpcklwd` on 864, which has no dword unpacks —, store row, level-2 twiddle offset, pass-A `ymm2` restore
  dropped), each rejected by both the symbolic proof and the C differential; 3 fold mutants (R2 → R3, companion
  qinv, a nor2 zeta/zeta·qinv load) rejected by the keygen differential.
- **864 direct codec unaffected:** the codec consumes `poly_tobytes`/`poly_frombytes` operands in the lazy Forward's
  6-way layout. The HT Forward output is bit-identical to the lazy output (same words, same layout), so every codec
  input is unchanged; the KEM test (pk/sk/ct/ss byte-exact against Official) and the audit's codec call counts confirm it.

## Shared tooling changes (NTRU+768 outputs unchanged)

`common/official_opt_ht/`: `generate_forward_ht.py`, `generate_keygen_r2fold.py`, `generate_ht_overlays.py`,
`prove_keygen_r2fold.py`, `range_proof_ht/prove_ht.py`, `audit_ht_linked.py`, `mutate_ht.py`, `run_ht_diag.py` take
`--param 768|864|1152` (default 768); `tests/test_keygen_r2fold.c` and `bench/bench_ht_diag.c` select names, bounds,
layouts and the variant set from `NTRUPLUS_N`; `ht.mk` accepts PARAM 768/864/1152 and passes `--param` to every tool
except for 768. New: `tools/export_ht_flat_param.py` (864/1152 front end of `export_ht_flat.py`, which is left
byte-identical because its own SHA-256 is recorded in the committed 768 manifest). `install_reversed_placement.py`
needed no change: its HT renames (`ntt_ht.s` → `bbb_ntt_ht.s`, `basemul_nor2.s` → `zzz_basemul_nor2.s`) already
apply whenever the files exist, next to the existing 864 `codec_direct.s` → `ccc_codec_direct.s`.

Proof that NTRU+768 is unchanged (run in `NTRU+768/experiments/avx2_official_opt_freeze_001`):

- `make -n -B` of `ht-phase-a`, `ht-bench`, `ht-flat`, `ht-qualification-check` and `generate-ht` is byte-identical
  before and after.
- `make ht-phase-a ht-qualification-check` passes. The regenerated `ht-forward-generation.json`,
  `ht-inverse-generation.json`, `r2fold-generation.json`, `r2fold-proof.json` and `ht-mutation-check.json` are
  byte-identical to the committed `results/ht-phase-a/` files. `ht-range-proof-summary.json` differs only in the
  `tool_sha256` of `prove_ht.py`, and `ht-linked-summary.json` only in `elf_sha256` (linked test ELFs are not
  bit-reproducible: gcc temp names in `.strtab`; the same happens with the unchanged sources). The export regenerates
  identical with an identical manifest.
- All HT test/bench objects and binaries rebuilt before and after the change are identical (objects in full, ELFs in
  `.text`/`.rodata`/`.data`), except the sanitizer `test_keygen_r2fold`, whose `.text` is identical and whose
  `.rodata`/`.data` differ by UBSan source-line records (the test file gained lines).

## Same-ELF diagnostic (`supercop-derived`, not Native)

Setup, as for 768: `common/official_opt_ht/bench/bench_ht_diag.c` (without `HT_INV`: regions forward, keygen
BaseMul, BaseInv, keypair, encap, decap; KEM variants Official, base, candidate, ht_only, r2fold_only; 20 blocks × 32
observations per variant per launch), `ht.mk ht-bench` (O3GC), cpucycles `default-perfevent` from the campaign (read
only), CPU 1, ASLR on, 31 fresh launches per link order, every batch under `phase_b_batch.py` (all four clean on
attempt 0). Deltas are pooled StQ2 between identical `cpucycles()` anchors; favourable launches of 31 in brackets.
The keypair region reseeds the KAT DRBG per bank for every variant (seed-matched).

### Components

| | 864 normal | 864 reversed | 1152 normal | 1152 reversed |
|---|---|---|---|---|
| Forward: HT − lazy | −69.8 (31) | −77.4 (31) | −42.5 (31) | −43.3 (31) |
| (lazy reference) | 999.3 | 1012.7 | 1244.7 | 1249.8 |
| keygen BaseMul: nor2 on R·finv − Official | −90.5 (31) | −86.4 (31) | −127.3 (31) | −137.9 (31) |
| (Official reference) | 660.4 | 652.9 | 989.2 | 984.0 |
| BaseInv: fold − Official (same code, separate TU) | −0.8 (20) | −9.0 (31) | +0.8 (10) | −1.1 (24) |

The feasibility study (scratch `bench.c`, core cycles) measured −79 (864) / −50 (1152) per Forward and −95 / −122 per
keygen BaseMul; these SUPERCOP-cpucycles figures (TSC-based, a different harness) are close but not equal: Forward
−70..−77 / −43, nor2 −86..−91 / −127..−138.

### KEM, variant − base

| | 864 normal | 864 reversed | 1152 normal | 1152 reversed |
|---|---|---|---|---|
| keypair candidate | −340.6 (31) | −493.3 (31) | −216.8 (21) | −341.4 (26) |
| keypair ht_only | −136.7 (31) | −173.1 (30) | −117.4 (18) | +23.7 (12) |
| keypair r2fold_only | −149.0 (31) | −323.1 (31) | −310.6 (22) | −166.2 (22) |
| encap candidate | −145.4 (31) | −166.8 (31) | −98.4 (31) | −124.6 (31) |
| encap ht_only | −150.5 (31) | −160.9 (31) | −106.1 (31) | −102.3 (31) |
| encap r2fold_only | −2.8 (14) | −14.5 (24) | −10.0 (21) | −9.5 (20) |
| decap candidate | −134.6 (31) | −158.0 (31) | −89.2 (31) | −60.9 (29) |
| decap ht_only | −139.6 (31) | −136.0 (31) | −68.0 (29) | −41.7 (28) |
| decap r2fold_only | −9.2 (22) | +18.6 (4) | −47.6 (31) | −4.4 (20) |

Candidate − Official: 864 keypair −5817 / −5863, encap −9657 / −9729, decap −6266 / −6434; 1152 keypair −7807 / −7851,
encap −11945 / −11941, decap −6717 / −6950 (normal / reversed). Diagnostic ELF `.text`: 864 `1485529f…` / `dad92254…`,
1152 `a966c598…` / `b3933daa…`.

Reading:

- **Both items are component wins for both parameters**, 31/31 launches in both link orders, so both parameters went
  on to Phase B.
- **Encap/Decap** (2 Forwards each, no keygen) move by about 2 × the Forward gain (864 −135..−167, 1152 −61..−125);
  r2fold_only, which does not change them, sits at the placement noise floor (−15..+19; one outlier, 1152 normal
  decap −48).
- **Keypair** is 2 × nor2 + (2 + retries) × Forward. 864 is clean (−341 / −493, 31/31). 1152 keypair is ~87k cycles
  with a heavy BaseInv retry mix even seed-matched, and its launch spread (quartiles several hundred cycles wide) makes
  the per-control splits unreliable (ht_only reversed +24, 12/31); the candidate is still −217 / −341.

## Phase B: Native SUPERCOP (2026-09-25)

Everything ran on CPU 1 of the Core Ultra 7 155H with ASLR on (`randomize_va_space=2`); host controls were read and left
unchanged (`performance` governor, `intel_pstate/no_turbo=1`). Every timing batch ran under `phase_b_batch.py`, strictly
one after another, one parameter at a time (all 1152 timing, then all 864 timing), with nothing built or tested while
timing ran. Campaign: `/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001`. Tag `20260925ht`.

### Qualification exports

`common/official_opt_ht/tools/export_ht_flat_param.py --param N` (`make ht-qualification`; `make ht-qualification-check`
regenerates into a temporary directory and requires the export and manifest to be identical) runs every check of
`export_ht_flat.py` (lock, base manifest and tree, per-file hashes, Phase-A generation records, refuse-overwrite) with the
parameter's names. `kind: ht-qualification-source`; the manifest records both exporters' hashes.

| | NTRU+864 | NTRU+1152 |
|---|---|---|
| Export (tree SHA-256) | `avx2-officialopt-lazy-codec-keccak-ht-qual001` (`847f5757faa81fb1686027bec2f46eb609f3f28446c464b3cf88aa0f616f361f`) | `avx2-officialopt-lazy-freeze-keccak-ht-qual001` (`3aa2d6ae8b7590c72ca4d5339c71cca82d8dfadfcedf26c64679ef048b185473`) |
| Base export | `avx2-officialopt-lazy-codec-keccak-qual001` (`0deb127b…`), 36 files, all kept except `kem.c` | `avx2-officialopt-lazy-freeze-keccak-qual001` (`e88c9c6d…`), same |
| Added (exact Phase-A bytes) | `ntt_ht.s`, `basemul_nor2.s`, `baseinv_r2fold.c` | same |
| `kem.c` vs base | 20 added, 4 changed lines: the HT overlay head (comment + `#define …_ntt_caller_lazy …_ntt_ht`), the r2fold header comment, 2 prototypes, 2 × `poly_baseinv` → `…_baseinv_r2fold`, 2 × keygen `poly_basemul` → `…_basemul_nor2` (full diff in the manifest) | same shape |

The only Phase-A chain lines not carried over are the three repo-only Keccak includes of the r2fold_only overlay; its
base `#define` lines (864: direct-codec tobytes/frombytes; 1152: freeze2op tobytes) are already in the base `kem.c`.

**The flat tree is what Phase A tested** (`make ht-flat-record` → `results/ht-phase-b/`):

- **Flat KEM test** (every export file compiled from the export directory, `kem.c` renamed to `official_lazy_*`, against the
  pinned Official `kem.c`; shared `test_kem_lazy.c`): 100 vectors byte-exact, invalid PK/CT/noncanonical CT/SK, forced g
  retry and f injection, release and ASan+UBSan+LSan (`closure-tests.log`).
- **Flat linked audit** (`flat-linked-summary.json`): entries equal the export's `.s` assembled alone (864: 1267 / 645
  bytes; 1152: 1462 / 1179); the flat `kem.o` has 6 × HT Forward, 2 × fold BaseInv, 2 × nor2, 2 × `poly_basemul`,
  1 × `poly_invntt_scale`, the base codec bindings and 0 × lazy / `poly_ntt` / `poly_baseinv`.
- **Object identity:** flat `kem.o`, `baseinv_r2fold.o`, `symmetric.o`, `mlk_fips202.o`, `mlk_keccakf1600.o` equal the
  Phase-A objects up to the file symbol and `ntruplusN_keccak_hash_*` → `hash_*`. Negative control (flat `kem.o` vs the
  r2fold_only object): rejected, for both parameters.
- **do-part try emulation** (`flat-supercop-try.json`, scratch, `export_keccak_flat.try_tree()` on the installed trees):
  the export and both reversed copies compile with 0 warnings and reproduce the pinned checksums for O3/Os/O2/O.

Installed with `install_qualification.py` (the installed base exports re-hash to their manifests);
`install_reversed_placement.py` made `{base,ht}-reversed` for each parameter (`PLACEMENT.json`; renames `ntt.s` → `aaa_`,
`ntt_caller_lazy.s` → `bbb_`, `pack.s` → `yyy_`, `basemul.s` → `zzz_`, `ntt_ht.s` → `bbb_ntt_ht.s`, `basemul_nor2.s` →
`zzz_basemul_nor2.s`, and on 864 `codec_direct.s` → `ccc_codec_direct.s`).

**SUPERCOP try passes:** in all 27 Native batches per parameter `try` reported `ok` for O3/Os/O2/O with
checksumsmall/checksumbig equal to the pinned `crypto_kem/ntruplusN/checksum*` (= Official); so did the O3GC fixed builds.

### Design

- **Native:** roles `official` (`avx2`), `base`, `ht`; 81 fresh launches each = 9 rotated rounds of one 9-launch
  `run_supercop_benchmark.py --mode native-kem` batch per role (`run_extended_native.py --batches 9 --order rotate`),
  default compiler selection, unmodified `measure.c`, independent pools, CIs by launch resampling (2,000).
- **Compiler picks:** 864 official/base/ht O3 × 9 each; 1152 official O2 × 2, O3 × 7, base O3 × 9, ht O3 × 9. Base and ht
  always got the same compiler, so no fixed `-O3` run was needed.
- **Paired:** one O3GC fixed ELF per role and placement (`bench/supercop/okc-o3gc.sh`, `--fresh-launches 1`);
  `run_paired_aslr_on.py`, 48 ABBA/BAAB blocks (192 fresh launches) per run: ht vs base normal (primary), ht vs base
  reversed (secondary), ht vs Official normal. The Official and base fixed ELFs are byte-identical to the Keccak Phase-B
  builds (864 `9bf4b8b7…` / `83370edd…`, 1152 `fe8de722…` / `f6bb8b81…`); ht `51eff93a…` (864) / `6ca2c90b…` (1152).
- **Hygiene:** 35 batches per parameter (27 Native, 5 fixed builds, 3 paired) plus the 1152 seed-matched batch. All
  accepted on attempt 0 except one 1152 Native batch (base, round 2), rejected once for a 0.52 pre-batch load and
  accepted on attempt 1. The campaign `okc-amd64` was unchanged after every batch (`82f1eea7…`).

### Native, default SUPERCOP compiler selection (81 launches per role; pooled StQ2)

| n | Op | Official | Base | HT | HT − Base [95% CI] fav./81 | HT − Official [95% CI] fav./81 |
|---|---|---:|---:|---:|---:|---:|
| 864 | Keypair | 23,737.3 | 17,977.6 | 17,594.6 | **−383.0** (−2.13%) [−396.5, −369.3] 81/81 | −6,142.7 (−25.9%) [−6,160.1, −6,125.7] 81/81 |
| 864 | Encap | 32,913.0 | 23,394.0 | 23,300.3 | **−93.7** (−0.40%) [−112.1, −75.8] 71/81 | −9,612.7 (−29.2%) [−9,644.8, −9,586.0] 81/81 |
| 864 | Decap | 23,668.9 | 17,460.4 | 17,322.9 | **−137.5** (−0.79%) [−150.5, −124.5] 81/81 | −6,346.1 (−26.8%) [−6,368.6, −6,326.4] 81/81 |
| 1152 | Keypair | 34,708.6 | 27,112.6 | 26,852.7 | **−259.9** (−0.96%) [−549.8, +30.4] 44/81 | −7,855.9 (−22.6%) [−8,167.9, −7,491.4] 81/81 |
| 1152 | Encap | 43,100.7 | 31,217.1 | 31,072.5 | **−144.7** (−0.46%) [−176.4, −108.8] 74/81 | −12,028.3 (−27.9%) [−12,061.1, −11,995.8] 81/81 |
| 1152 | Decap | 30,530.6 | 23,470.0 | 23,353.3 | **−116.7** (−0.50%) [−132.6, −101.9] 78/81 | −7,177.3 (−23.5%) [−7,192.9, −7,160.8] 81/81 |

"fav." counts candidate launches below the baseline's median launch. Per-batch HT − Base deltas (9 batches):

- 864: keypair −337 … −427 (SD 23), encap −28 … −133 (SD 33), decap −99 … −150 (SD 16), all 27 negative;
- 1152: keypair −714 … +262 (SD 321, 7/9 negative), encap −100 … −181 (SD 28), decap −86 … −176 (SD 29).

### Fixed-ELF paired, O3GC, ASLR on, 48 blocks (mean [block-bootstrap 95% CI] favourable/48)

| n | Op | HT vs Base, normal (primary) | HT vs Base, reversed (secondary) | HT vs Official, normal |
|---|---|---:|---:|---:|
| 864 | Keypair | **−376.5** [−387.7, −364.7] 48/48 | −307.2 [−329.8, −279.2] 47/48 | −6,293.5 [−6,328.8, −6,269.4] 48/48 |
| 864 | Encap | **−133.8** [−151.2, −115.3] 46/48 | −147.7 [−165.4, −127.3] 46/48 | −9,560.6 [−9,596.8, −9,526.1] 48/48 |
| 864 | Decap | **−161.2** [−173.9, −148.9] 48/48 | −196.8 [−214.8, −179.4] 48/48 | −6,534.8 [−6,569.9, −6,505.1] 48/48 |
| 1152 | Keypair | **−260.8** [−508.3, −4.0] 29/48 | −262.7 [−552.6, +30.7] 27/48 | −7,768.8 [−8,049.1, −7,497.4] 48/48 |
| 1152 | Encap | **−133.6** [−151.2, −116.8] 47/48 | −89.8 [−115.3, −60.0] 42/48 | −11,914.6 [−11,951.7, −11,880.5] 48/48 |
| 1152 | Decap | **−109.5** [−121.0, −97.6] 48/48 | −23.9 [−37.5, −8.8] 37/48 | −7,069.4 [−7,094.8, −7,046.1] 48/48 |

### NTRU+1152 keypair: seed-matched supporting evidence (`supercop-derived`, not Native)

SUPERCOP's `measure` uses per-process kernel-seeded `fastrandombytes`, so the i-th keypair of two launches gets different
coins and a different number of BaseInv retries; with about half of all 1152 keypairs retrying at least once (48% of the seed-matched iterations below), the pooled StQ2 of 81 launches moves
by hundreds of cycles with the retry composition (see
[ntruplus864-1152-official-opt.md](ntruplus864-1152-official-opt.md#ntru1152-keypair-controlling-the-baseinv-retry-tail)).
`tools/run_ht_keypair_seedmatched.py` (new; `make ht-bench-keypair`) links the shared, unchanged
`bench_keypair_seedmatched.c` with A = base, B = HT candidate; every iteration gives both byte-identical coins
(SHAKE256(seed ‖ iteration)), so both hit identical retries, and times four keypairs in ABBA/BAAB order (the harness traps
unless pk/sk and the randombytes call counts match). 9 launches per link order × 5000 iterations, one
`phase_b_batch.py` batch (clean, attempt 0):

| | mean d = HT − Base [two-stage bootstrap 95% CI] | median d | favourable launches |
|---|---:|---:|---:|
| normal link order | −280.5 [−295.3, −264.8] | −283.0 | 9/9 |
| swapped link order | −371.3 [−393.6, −348.0] | −374.0 | 9/9 |
| pooled | **−325.9 [−350.1, −299.4]** | −327.5 | 18/18 |

By retry stratum (mean d): 0 retries −303.6 (46388 iterations), 1 retry −334.7 (26079), 2 retries −362.4 (11108),
3+ −388.0 (6425). The growth per retry (about −30) is consistent with one more HT Forward per retry (a retry redoes the sampling and the Forward; −43 per Forward in the diagnostic).
`results/ht-keypair-seedmatched-20260925ht/`.

### Decision (rule: Native default-selection pooled HT − Base < 0 AND normal-placement ASLR-on paired 95% CI < 0)

| n | Op | Native HT − Base | Paired normal | Paired reversed | Verdict |
|---|---|---|---|---|---|
| 864 | Keypair | −383.0 [−396.5, −369.3] | [−387.7, −364.7] | [−329.8, −279.2] | **robust research win** |
| 864 | Encap | −93.7 [−112.1, −75.8] | [−151.2, −115.3] | [−165.4, −127.3] | **robust research win** |
| 864 | Decap | −137.5 [−150.5, −124.5] | [−173.9, −148.9] | [−214.8, −179.4] | **robust research win** |
| 1152 | Keypair | −259.9 [−549.8, +30.4] | [−508.3, −4.0] | [−552.6, +30.7] | **robust research win (marginal)**, flagged: Native CI and reversed paired CI cross zero; seed-matched −325.9 [−350.1, −299.4] supports it |
| 1152 | Encap | −144.7 [−176.4, −108.8] | [−151.2, −116.8] | [−115.3, −60.0] | **robust research win** |
| 1152 | Decap | −116.7 [−132.6, −101.9] | [−121.0, −97.6] | [−37.5, −8.8] | **robust research win** (reversed much smaller, −24) |

Against Official the same rule gives a robust research win for all six (864 −25.9% / −29.2% / −26.8%, 1152 −22.6% /
−27.9% / −23.5%): the Keccak and lazy/codec/freeze wins plus the HT increment.

Reading:

- **NTRU+864** is the clean case: Native, both paired placements and the same-ELF diagnostic agree for every op.
  Keypair −383 Native is somewhat more than 2 × nor2 (−90) + 2 × Forward (−70..−77) ≈ −326; encap −94 Native is below the paired
  −134/−148 and the same-ELF −145/−167, so part of the encap gain is placement-dependent at SUPERCOP's archive order,
  but every Native batch is negative.
- **NTRU+1152 encap/decap** are consistent (Native −145 / −117; paired normal −134 / −110). Reversed-placement decap is
  only −24, much smaller than normal: the decap increment is placement-sensitive, though still below zero.
- **NTRU+1152 keypair** is conclusive only with the seed-matched harness. Its Native and paired values (−260 / −261 /
  −263) sit where expected (2 × −130 nor2 + 2 × −43 Forward ≈ −345 at 0 retries) but their CIs are dominated by the
  retry mixture.

`promotion: none`, and `clean/` was not touched. Details: `STATUS.yml` `ht_candidate` of each experiment and
`results/extended-multi-summary-20260925ht.json`.

## Reproduce

```sh
REPO=/home/nuc/src/ntru_plus-official-opt-864-1152
A=$REPO/ntruplus-ntt-Optimized/Additional_Implementation/avx2; T=$A/common/official_opt_lazy/tools; H=$A/common/official_opt_ht/tools
C=/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001; TAG=20260925ht
# per parameter p (864: B=avx2-officialopt-lazy-codec-keccak-qual001, X=avx2-officialopt-lazy-codec-keccak-ht-qual001;
#                  1152: B=avx2-officialopt-lazy-freeze-keccak-qual001, X=avx2-officialopt-lazy-freeze-keccak-ht-qual001)
E=$A/NTRU+$p/experiments/avx2_official_opt_001; R=$E/results
(cd $E && make generate-ht)             # regenerate asm/src from the pinned inputs (writes)
(cd $E && make ht-record)               # Phase A: generators --check, tests (release + ASan/UBSan/LSan), range proof,
                                        # fold proof, linked audit, mutation check -> results/ht-phase-a/
(cd $E && make ht-bench)
(cd $E && python3 $T/phase_b_batch.py --result-dir results/ht-diag-normal-TAG --metadata metadata.json -- \
  python3 $H/run_ht_diag.py --param $p --experiment . --launches 31 --result-dir {RESULT})
(cd $E && python3 $T/phase_b_batch.py --result-dir results/ht-diag-reversed-TAG --metadata metadata.json -- \
  python3 $H/run_ht_diag.py --param $p --experiment . --launches 31 --binary build/bench_ht_diag_swapped --result-dir {RESULT})
(cd $E && make ht-qualification-check && make ht-flat-record)   # export committed; make ht-qualification recreates it
python3 $T/install_qualification.py --param $p --campaign-root $C --export-root $E/qualification/$X
python3 $T/install_reversed_placement.py --param $p --campaign-root $C --baseline $B --candidate $X
python3 $T/run_extended_native.py --param $p --experiment $E --campaign-root $C --tag $TAG --batches 9 --order rotate \
  --role official=avx2 --role base=$B --role ht=$X
for spec in official:normal:avx2 base:normal:$B ht:normal:$X base:reversed:$B-reversed ht:reversed:$X-reversed; do
  role=${spec%%:*}; rest=${spec#*:}; place=${rest%%:*}; impl=${rest#*:}
  python3 $T/phase_b_batch.py --result-dir $R/fixed-ht-$role-$place-$TAG --metadata metadata.json -- \
    python3 $REPO/scripts/run_supercop_benchmark.py --campaign-root $C --parameter $p --implementation $impl \
    --cpu 1 --mode native-kem --fresh-launches 1 --compiler-wrapper $REPO/bench/supercop/okc-o3gc.sh \
    --require-frequency-control --result-dir {RESULT}
done
pair() { # name baseline-elf candidate-elf placement
  python3 $T/phase_b_batch.py --result-dir $R/paired-aslr-on-$4-$1-$TAG --metadata manifest.json -- \
    python3 $T/run_paired_aslr_on.py --official $2 --candidate $3 --placement $4 --cpu 1 --blocks 48 \
    --compiler-recipe O3GC --output {RESULT}
  python3 $REPO/scripts/summarize_supercop_paired.py --campaign $R/paired-aslr-on-$4-$1-$TAG --parameter $p; }
pair ht-vs-base $R/fixed-ht-base-normal-$TAG/measure $R/fixed-ht-ht-normal-$TAG/measure normal
pair ht-vs-base $R/fixed-ht-base-reversed-$TAG/measure $R/fixed-ht-ht-reversed-$TAG/measure reversed
pair ht-vs-official $R/fixed-ht-official-normal-$TAG/measure $R/fixed-ht-ht-normal-$TAG/measure normal
python3 $T/summarize_extended_multi.py --param $p --experiment $E --tag $TAG --order rotate --roles official,base,ht \
  --comparison ht:base --comparison ht:official --comparison base:official \
  --paired ht:base=ht-vs-base-$TAG --paired ht:official=ht-vs-official-$TAG
# 1152 keypair supporting evidence
(cd $E && make ht-bench-keypair && python3 $T/phase_b_batch.py --result-dir results/ht-keypair-seedmatched-$TAG \
  --metadata metadata.json -- python3 $H/run_ht_keypair_seedmatched.py --param 1152 --experiment . --iterations 5000 \
  --result-dir {RESULT})
```

The same-ELF diagnostic directories use tag `20260925` (`results/ht-diag-{normal,reversed}-20260925/`). The do-part try
emulation was a scratch script around `export_keccak_flat.try_tree()` (as for 768); its record is
`results/ht-phase-b/flat-supercop-try.json`. Curated evidence: `results/ht-phase-a/`, `results/ht-phase-b/`,
`results/ht-diag-*-20260925/`, `results/native-ext-{official,base,ht}-b{1..9}-20260925ht/`,
`results/fixed-ht-*-20260925ht/`, `results/paired-aslr-on-*-20260925ht/`, `results/extended-multi-summary-20260925ht.json`,
and for 1152 `results/ht-keypair-seedmatched-20260925ht/` (`metadata.json` / `manifest.json`, `stq-summary.json` /
`summary.json` / `summary.csv`, `supercop.lock`). Raw launch output, `data`, `run.out`, the `measure` ELFs and
`host-hygiene.json` stay local (Git-ignored).

## Deviations and notes

- **No HT inverse**, by design (see above). The 864/1152 candidates therefore have no `htinv_only` / `ht_r2fold`
  controls; the candidate is the ht_r2fold combination.
- **Separate exporter.** `export_ht_flat.py` could not be generalised in place without breaking the NTRU+768
  `ht-qualification-check` (its own hash is part of the committed 768 manifest), so the 864/1152 exports use the front end
  `export_ht_flat_param.py`, which imports it.
- **New timing tool:** `run_ht_keypair_seedmatched.py` + `ht-bench-keypair` (the task's `run_keypair_seedmatched.py` is
  hard-wired to Official vs caller-lazy, and `analyze_keypair_retry_strata.py` to the older `native-lazy-qual-*` /
  `fixed-lazy-paired-*` layouts; the new runner reports retry strata itself). Supporting evidence only.
- **1152 base b2** Native batch was rejected once by the hygiene check (pre-batch load 0.52 > 0.5) and accepted on the
  rerun.
- **Diagnostic block count.** The 864/1152 diagnostic uses 20 blocks (balanced for the 2- and 5-variant rotations)
  instead of 768's 14.
- **Reversed placement is secondary** (a different archive member order, not a mirror). The 1152 reversed decap increment
  (−24) and keypair CI crossing zero are placement observations, not failures of the rule.
- **Test-only renames in the flat KEM test** (Official `hash_f/g/h` renamed so both copies link), as for 768; the flat
  side is compiled without `-DSUPERCOP`, whose path is covered by `try`.

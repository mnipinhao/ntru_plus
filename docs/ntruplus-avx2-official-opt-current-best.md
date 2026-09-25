# NTRU+768 / 864 / 1152 AVX2 Official-opt: current best (2026-09-25)

The HT candidates were made the current best for all three parameter sets on 2026-09-25.
They replace the Keccak-only exports (`…-keccak-qual001`), which were the current best since
2026-09-24.

This is a **research** status. Every row below is a robust research win under the decision rule in
[Methodology](#methodology). There is no `clean/` package, no production promotion
(`promotion: none` in every STATUS.yml) and no full constant-time review of the packaged trees yet.

This page is the current overview. [`ntruplus-avx2-overview-20260923.md`](ntruplus-avx2-overview-20260923.md)
is a dated snapshot taken before Keccak and HT: 27 launches, and it has the GT comparison and the
component profiler.

## 1. Current best per parameter

All paths are relative to `ntruplus-ntt-Optimized/Additional_Implementation/avx2/`. The exports are flat
SUPERCOP trees under the experiment's `qualification/`, each with a `<name>.json` manifest
(kind `ht-qualification-source`). They are installed in the disposable campaign
`/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001`.

| n | candidate | SUPERCOP export | tree sha256 | experiment | supersedes |
|---:|---|---|---|---|---|
| 768 | `avx2-officialopt-lazy-freeze-keccak-ht-768-exp001` | `avx2-officialopt-lazy-freeze-keccak-ht-qual001` | `50b22a3f2000bca8325ac9431deb906880b61b24a13892252999726e10304bb6` | `NTRU+768/experiments/avx2_official_opt_freeze_001` | `avx2-officialopt-lazy-freeze-keccak-qual001` (`6209ebac…`) |
| 864 | `avx2-officialopt-lazy-codec-keccak-ht-864-exp001` | `avx2-officialopt-lazy-codec-keccak-ht-qual001` | `847f5757faa81fb1686027bec2f46eb609f3f28446c464b3cf88aa0f616f361f` | `NTRU+864/experiments/avx2_official_opt_001` | `avx2-officialopt-lazy-codec-keccak-qual001` (`0deb127b…`) |
| 1152 | `avx2-officialopt-lazy-freeze-keccak-ht-1152-exp001` | `avx2-officialopt-lazy-freeze-keccak-ht-qual001` | `3aa2d6ae8b7590c72ca4d5339c71cca82d8dfadfcedf26c64679ef048b185473` | `NTRU+1152/experiments/avx2_official_opt_001` | `avx2-officialopt-lazy-freeze-keccak-qual001` (`e88c9c6d…`) |

The Official baselines are the pinned SUPERCOP 20260831 `avx2` trees (`bench/supercop.lock`): 768
`8db00172…`, 864 `13e0d983…`, 1152 `78daf6b9…`. In every Native batch and every O3GC build, SUPERCOP
`try` reported `ok`, and checksumsmall/checksumbig equalled the pinned Official values.

## 2. What changed against Official

### Techniques

The "Saving" column holds same-ELF component diagnostics, in core cycles per call against the step
before. Each figure comes from its own experiment ELF, so it is not additive and not Native.

| # | Technique | 768 | 864 | 1152 | Saving per call (768 / 864 / 1152) | Doc |
|---:|---|:-:|:-:|:-:|---|---|
| 1 | Caller-bounded lazy Forward (terminal Barrett dropped; range-proved per caller) | ✓ | ✓ | ✓ | −103 / −91 / −135 vs Official `poly_ntt` | [864/1152](ntruplus864-1152-official-opt.md) |
| 2a | 2-op canonical freeze in `poly_tobytes` (`vpaddw q; vpminuw`) | ✓ | – | ✓ | −14 / – / −22 per `tobytes` | [freeze2op](ntruplus768-1152-freeze2op.md) |
| 2b | Direct 12-bit codec, `tobytes` + `frombytes` (in-lane, no cross-lane permutes) | – | ✓ | – | 864: −253 `tobytes`, −276 `frombytes` | [direct codec](ntruplus768-1152-direct-codec.md) |
| 3 | mlkem-native x1 C Keccak (`b3ba7b32`, Apache-2.0 OR ISC OR MIT) replaces XKCP AVX2 | ✓ | ✓ | ✓ | about 90% of the total gain (in-KEM; see §4) | [Keccak](ntruplus-avx2-keccak-mlkem-native.md) |
| 4 | HT Forward: fused level 0 + first radix-3 pass, plus an unpack-only block exchange network; output bit-identical to #1 | ✓ | ✓ (new 24-uop network) | ✓ (768 network) | −28 / −70 / −43 vs lazy Forward | [768](ntruplus768-ht-forward.md), [864/1152](ntruplus864-1152-ht.md) |
| 5 | Keygen R² fold: BaseInv input scale R³ → R², keygen BaseMul without its R² pass (`basemul_nor2`) | ✓ | ✓ | ✓ | −81 / −91 / −127 per keygen BaseMul | same |
| 6 | HT inverse block pass (levels 6..2 from the NTT layout) | ✓ | – (no 4-stage network exists) | – (bit-exact but +62 slower) | 768: −24 vs `poly_invntt_scale` | [768](ntruplus768-ht-forward.md) |

The lazy Forward's arithmetic still runs in every tree. HT Forward (#4) produces the same output
words with the same arithmetic. It fuses the first two passes and replaces the block pass's data movement.

### Call sites in `kem.c`

| Call | Official | Current best |
|---|---|---|
| Forward NTT (keygen f, g; encap r; decap ×2 + re-encryption; 6 in total) | `poly_ntt` | `ntruplus<N>_officialopt_ntt_ht` |
| BaseInv (keygen f, g) | `poly_baseinv` | `ntruplus<N>_officialopt_baseinv_r2fold` |
| BaseMul (keygen ×2) | `poly_basemul` | `ntruplus<N>_officialopt_basemul_nor2` |
| BaseMul (encap/decap) | `poly_basemul` | unchanged |
| `poly_tobytes` (7) | `pack.s` | 768/1152 `…_tobytes_freeze2op`, 864 `…_tobytes_direct` |
| `poly_frombytes` | `pack.s` | 768/1152 unchanged, 864 `…_frombytes_direct` |
| Inverse NTT (decap) | `poly_invntt_scale` | 768 `…_invntt_ht`, 864/1152 unchanged |
| SHAKE256 (`hash_*`, keygen seed) | XKCP `KeccakP-1600-AVX2.s` via `fips202.c` | `mlk_shake256` via the `fips202.h` adapter |

The `kem.c` rebinding is a preprocessor overlay (`#define` of the call names), plus the three keygen
call-site edits for the R² fold.

### Files in the exported tree

The file set is the same for all three trees apart from the codec files. "Unchanged" means
byte-identical to Official.

| | files |
|---|---|
| Added | `ntt_ht.s`, `ntt_caller_lazy.s`, `basemul_nor2.s`, `baseinv_r2fold.c`, `mlk_{cbmc,common,context,fips202,keccakf1600,params,sys,verify}.h`, `mlk_fips202.c`, `mlk_keccakf1600.c`, `mlkem_native_config.h`, `LICENSE.mlkem-native`; 768/1152 `tobytes_freeze2op.s`; 864 `codec_direct.s`; 768 `invntt_ht.s` |
| Removed | `KeccakP-1600-AVX2.s`, `KeccakP-1600-SnP.h`, `fips202.c` |
| Changed | `kem.c` (call rebinding), `fips202.h` (drop-in adapter to mlkem-native) |
| Unchanged | `add.s`, `api.h`, `architectures`, `baseinv.s`, `basemul.s`, `cbd.s`, `consts.c`, `consts.h`, `crepmod3.s`, `goal-*`, `invntt.s`, `ntt.s`, `pack.s`, `params.h`, `poly.c`, `poly.h`, `symmetric.c`, `symmetric.h`, `util.h` |

Some of this code is no longer called: `ntt_caller_lazy.s` (every forward call is macro-rebound to
`ntt_ht`), the Official `poly_ntt` in `ntt.s`, the 768 Official `poly_invntt_scale`, and the 864 Official
`poly_tobytes`/`poly_frombytes`. The linked audits show 0 calls to any of them. The research exports
keep these files so that the base export's files stay byte-identical. A production package should drop them.

## 3. Performance against Official (Native, 2026-09-25)

SUPERCOP 20260831 Native on an Intel Core Ultra 7 155H, CPU 1, performance governor, turbo off,
ASLR on. It used the unmodified `measure.c` and SUPERCOP's default compiler selection. Each role
had **81 fresh launches** (9 rotating 9-launch batches) under `phase_b_batch.py`.

Values are pooled StQ2 cycles. The CI is a 95% interval from resampling launches within each role
(2,000 resamples). "fav." counts current-best launches below the median Official launch.

| n | op | Official | Current best | Δ vs Official [95% CI] | fav. |
|---:|---|---:|---:|---:|---:|
| 768 | keypair | 21,611.5 | 16,598.9 | **−5,012.7 (−23.2%)** [−5,030.2, −4,996.9] | 81/81 |
| 768 | encap | 28,174.3 | 20,455.9 | **−7,718.4 (−27.4%)** [−7,756.9, −7,686.6] | 81/81 |
| 768 | decap | 19,461.7 | 14,960.0 | **−4,501.7 (−23.1%)** [−4,515.5, −4,486.7] | 81/81 |
| 864 | keypair | 23,737.3 | 17,594.6 | **−6,142.7 (−25.9%)** [−6,160.1, −6,125.7] | 81/81 |
| 864 | encap | 32,913.0 | 23,300.3 | **−9,612.7 (−29.2%)** [−9,644.8, −9,586.0] | 81/81 |
| 864 | decap | 23,668.9 | 17,322.9 | **−6,346.0 (−26.8%)** [−6,368.6, −6,326.4] | 81/81 |
| 1152 | keypair | 34,708.6 | 26,852.7 | **−7,855.9 (−22.6%)** [−8,167.9, −7,491.4] | 81/81 |
| 1152 | encap | 43,100.7 | 31,072.5 | **−12,028.2 (−27.9%)** [−12,061.1, −11,995.8] | 81/81 |
| 1152 | decap | 30,530.6 | 23,353.3 | **−7,177.3 (−23.5%)** [−7,192.9, −7,160.8] | 81/81 |

Fixed-ELF paired control: O3GC ELFs, ASLR on, normal placement, 48 ABBA/BAAB blocks, current best
minus Official. It agrees with Native within 3%, and all 9 (n, op) pairs are 48/48 favourable.

| n | keypair | encap | decap |
|---:|---:|---:|---:|
| 768 | −5,098.3 [−5,116.8, −5,081.6] | −7,725.2 [−7,760.3, −7,693.2] | −4,449.8 [−4,467.2, −4,432.6] |
| 864 | −6,293.5 [−6,328.8, −6,269.4] | −9,560.6 [−9,596.8, −9,526.1] | −6,534.8 [−6,569.9, −6,505.1] |
| 1152 | −7,768.8 [−8,049.1, −7,497.3] | −11,914.6 [−11,951.7, −11,880.5] | −7,069.4 [−7,094.8, −7,046.0] |

Compiler picks under default selection: the current best took O3 in 9/9 batches for every n. Official
took O2 in 8/9 batches (768), O3 in 9/9 (864), and O3 in 7/9 with O2 in 2/9 (1152). The Native Δ is
therefore the production-relevant default-selection difference. The paired rows fix the compiler at O3GC.

## 4. Contribution by step

Each step is measured against the step before it, in its own Native campaign, as pooled StQ2 Δ.

- Steps 1+2 (lazy + freeze2op or direct codec) and step 3 (Keccak) come from the 2026-09-24
  campaign `20260924k`, with 27 launches per role.
- The HT steps come from `20260925h` (768) and `20260925ht` (864/1152), with 81 launches per role.

The three steps add up to the direct Δ in §3 within the noise of the separate runs. For example,
768 keypair: −214.7 − 4,536.4 − 263.4 = −5,014.5, against −5,012.7 measured directly.

| n | op | 1+2: lazy + freeze/codec vs Official | 3: + mlkem-native Keccak | 4–6: + HT (vs Keccak base) [95% CI] |
|---:|---|---:|---:|---:|
| 768 | keypair | −214.7 | −4,536.4 | −263.4 [−275.4, −251.8] |
| 768 | encap | −159.6 | −7,467.4 | −75.2 [−94.2, −58.0] |
| 768 | decap | −318.9 | −4,103.7 | −91.0 [−102.3, −80.3] |
| 864 | keypair | −849.7 | −4,923.4 | −383.0 [−396.5, −369.3] |
| 864 | encap | −813.5 | −8,702.1 | −93.7 [−112.1, −75.8] |
| 864 | decap | −1,335.9 | −4,886.7 | −137.5 [−150.5, −124.5] |
| 1152 | keypair | −540.7 (CI crosses 0) | −7,059.9 | −259.9 [−549.8, +30.4] |
| 1152 | encap | −444.9 | −11,438.4 | −144.7 [−176.4, −108.8] |
| 1152 | decap | −397.8 | −6,649.8 | −116.7 [−132.6, −101.9] |

What the steps show:

- **Keccak dominates.** mlkem-native Keccak is about 90% of the total gain. SHAKE was 64–86% of every
  Official operation (the 2026-09-23 overview, §2).
- **Ranking of the non-hash levers:**
  - 864's direct codec is the largest (−814 to −1,336 per op).
  - HT is next (−75 to −383 per op), largest for keypair, where the R² fold applies.
  - For 768/1152, the lazy Forward and 2-op freeze give −160 to −541 per op.

HT paired control, current best minus Keccak base, O3GC, ASLR on, 48 blocks. Normal placement is
primary; reversed placement is secondary.

| n | op | normal | reversed |
|---:|---|---:|---:|
| 768 | keypair | −292.8 [−302.6, −282.9] | −187.6 [−200.5, −174.3] |
| 768 | encap | −61.0 [−78.7, −44.1] | **+24.4 [+6.2, +42.4]** |
| 768 | decap | −99.1 [−106.8, −91.7] | −106.8 [−116.5, −97.3] |
| 864 | keypair | −376.5 [−387.7, −364.7] | −307.2 [−329.8, −279.2] |
| 864 | encap | −133.8 [−151.2, −115.2] | −147.7 [−165.4, −127.3] |
| 864 | decap | −161.2 [−173.9, −148.8] | −196.8 [−214.8, −179.4] |
| 1152 | keypair | −260.8 [−508.3, −4.0] | −262.7 [−552.6, +30.7] |
| 1152 | encap | −133.6 [−151.2, −116.8] | −89.8 [−115.3, −60.0] |
| 1152 | decap | −109.5 [−121.0, −97.6] | −23.9 [−37.5, −8.8] |

## 5. Known flags

- **768 encap is placement-sensitive.** HT saves −75 (Native) and −61 (paired, normal), but the
  reversed-placement build is +24 slower. The saving is real (same-ELF −50 in both link orders), but it
  is small enough that SUPERCOP code placement can cancel it.
- **1152 keypair is marginal at KEM level.** The Native and reversed paired CIs cross zero, because of
  the BaseInv retry heavy tail. The normal paired CI only just excludes zero. The seed-matched harness
  gives −325.9 [−350.1, −299.4] (18/18). This is supporting evidence only, since SUPERCOP's
  `fastrandombytes` cannot be seed-matched.
- **1152 decap, reversed placement, is small:** −24 against −110 with normal placement.
- **The 768 HT inverse is not resolved at KEM level on its own.** It is a component win (−24 / −17)
  and bit-identical, and it is kept by user decision. Only the full candidate was exported.
- **Keccak is compiler-sensitive.** The mlkem-native C Keccak depends on `-O3` vectorising its byte
  loops. With SUPERCOP's default selection, the current best picks O3 every time. Fixed `-O2` still wins,
  by less; see the Keccak doc.
- **Dead code remains in the exported trees** (§2).

## 6. Correctness evidence

Every technique passed its Phase A gate set before export. The gates are:

- deterministic generators with pinned inputs and `--check`;
- symbolic-execution bit-identity for every asm change (HT Forward = lazy Forward on all N words;
  768 HT inverse = Official);
- interval range proofs on every caller domain;
- the R² fold identity proof, including the lazy/HT-g domain;
- C differentials;
- the shared KEM test (100 vectors pk/sk/ct/ss byte-exact against Official, invalid PK/CT/SK, forced
  g retry and f failure);
- a keygen differential over KAT-DRBG seeds;
- ASan + UBSan + LSan;
- a linked-call audit;
- mutation checks.

Each flat export was then shown to equal what Phase A tested: a flat-tree KEM test, a flat linked
audit, and object identity against the Phase A objects. The details are in each experiment's
STATUS.yml (`ht_candidate`, `keccak_*`, `freeze2op`/`codec` sections).

## Methodology

**Decision rule (research win).** A change counts as a robust research win when both of these hold:

- the pooled Native Δ is below zero, with default compiler selection;
- the fixed-ELF paired 95% CI, with normal placement and ASLR on, lies entirely below zero.

Reversed placement is reported alongside, and disagreements are flagged. ASLR-off runs are not used.

## Evidence

| n | Native + paired summary | Phase B doc |
|---:|---|---|
| 768 | `NTRU+768/experiments/avx2_official_opt_freeze_001/results/extended-multi-summary-20260925h.json` | [ntruplus768-ht-forward.md](ntruplus768-ht-forward.md) |
| 864 | `NTRU+864/experiments/avx2_official_opt_001/results/extended-multi-summary-20260925ht.json` | [ntruplus864-1152-ht.md](ntruplus864-1152-ht.md) |
| 1152 | `NTRU+1152/experiments/avx2_official_opt_001/results/extended-multi-summary-20260925ht.json` | [ntruplus864-1152-ht.md](ntruplus864-1152-ht.md) |

Step 1–3 figures: `results/extended-multi-summary-20260924k.json` in each experiment, and
[ntruplus-avx2-keccak-mlkem-native.md](ntruplus-avx2-keccak-mlkem-native.md).

## Next toward production (not done)

1. **Clean package.** Build a `clean/` tree per parameter with the dead files removed, the call names
   bound directly instead of through overlay macros, and a single `kem.c`.
2. **Constant-time review.** Review the whole package. The new asm has fixed trip counts and no
   data-dependent branches or addresses by construction, but this has not been audited as a
   package. The mlkem-native Keccak hash path had its own review (`audit_keccak_ct.py`, see the Keccak doc).
3. **Re-confirm with Native.** Run a release-package Native re-confirmation against these research exports.

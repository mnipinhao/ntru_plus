# NTRU+768 / 864 / 1152 AVX2 Official-opt: current best (2026-09-25)

On 2026-09-25 the **fused-inverse + Shoup** candidates became the current best for all three parameter sets.
They build on the HT exports (`…-keccak-ht-qual001`), which had been the current best earlier the same day.

This is **research** status. Every Encap/Decap change below is a robust research win under the decision rule in
[Methodology](#methodology). What is missing before production:

- a `clean/` package;
- promotion to production (every STATUS.yml says `promotion: none`);
- a full constant-time review of the packaged trees.

This page is the current overview. [`ntruplus-avx2-overview-20260923.md`](ntruplus-avx2-overview-20260923.md)
is a dated snapshot from before Keccak, HT, the fused inverse and Shoup. It used 27 launches, and it holds the
GT comparison and the component profiler.

## 1. Current best per parameter

Paths are relative to `ntruplus-ntt-Optimized/Additional_Implementation/avx2/`.

- Each export is a flat SUPERCOP tree under its experiment's `qualification/`.
- Each has a `<name>.json` manifest of kind `invshoup-qualification-source`.
- The exports are installed, with reversed-placement copies, in the disposable campaign
  `/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001`.

| n | candidate source (`src/`) | SUPERCOP export | tree sha256 | experiment | supersedes |
|---:|---|---|---|---|---|
| 768 | `kem_lazy_r2fold_invcrep_shoup_freeze2op_keccak_ht.c` | `avx2-officialopt-lazy-freeze-keccak-ht-invc-shoup-qual001` | `d107a77fddbec827333a660fea4c93eebf0a8f4d594539adcf35e3a0ab6b23d8` | `NTRU+768/experiments/avx2_official_opt_freeze_001` | `avx2-officialopt-lazy-freeze-keccak-ht-qual001` (`50b22a3f…`) |
| 864 | `kem_lazy_r2fold_invcrep_shoup_codec_direct_keccak_ht.c` | `avx2-officialopt-lazy-codec-keccak-ht-invd-shoup-qual001` | `b1d546b3e88abf9fde6a6035317c3a2705086fe88aca7e668da96eea15aa0cc4` | `NTRU+864/experiments/avx2_official_opt_001` | `avx2-officialopt-lazy-codec-keccak-ht-qual001` (`847f5757…`) |
| 1152 | `kem_lazy_r2fold_invcrep_shoup_freeze2op_keccak_ht.c` | `avx2-officialopt-lazy-freeze-keccak-ht-invd-shoup-qual001` | `94fc539de23a604f00560016109d2f1fc4f1f921d2f569d1adf3176f82946b75` | `NTRU+1152/experiments/avx2_official_opt_001` | `avx2-officialopt-lazy-freeze-keccak-ht-qual001` (`3aa2d6ae…`) |

The Official baselines are the pinned SUPERCOP 20260831 `avx2` trees (`bench/supercop.lock`): 768
`8db00172…`, 864 `13e0d983…`, 1152 `78daf6b9…`. SUPERCOP `try` reported `ok` in every Native batch and every
O3GC build, with checksumsmall and checksumbig equal to the pinned Official values.

## 2. What changed against Official

### Techniques

The "Saving" column gives same-ELF component diagnostics in core cycles per call, each against the step before.
Each figure comes from its own experiment ELF, so the figures are neither additive nor Native.

| # | Technique | 768 | 864 | 1152 | Saving per call (768 / 864 / 1152) | Doc |
|---:|---|:-:|:-:|:-:|---|---|
| 1 | Caller-bounded lazy Forward: drops the terminal Barrett, range-proved per caller | ✓ | ✓ | ✓ | −103 / −91 / −135 vs Official `poly_ntt` | [864/1152](ntruplus864-1152-official-opt.md) |
| 2a | 2-op canonical freeze in `poly_tobytes` (`vpaddw q; vpminuw`) | ✓ | – | ✓ | −14 / – / −22 per `tobytes` | [freeze2op](ntruplus768-1152-freeze2op.md) |
| 2b | Direct 12-bit codec for `tobytes` and `frombytes` (in-lane, no cross-lane permutes) | – | ✓ | – | 864: −253 `tobytes`, −276 `frombytes` | [direct codec](ntruplus768-1152-direct-codec.md) |
| 3 | mlkem-native x1 C Keccak (`b3ba7b32`, Apache-2.0 OR ISC OR MIT) replaces XKCP AVX2 | ✓ | ✓ | ✓ | 72–95% of the total gain per op (in-KEM; see §4) | [Keccak](ntruplus-avx2-keccak-mlkem-native.md) |
| 4 | HT Forward: fused level 0 + first radix-3 pass, plus an unpack-only block exchange network; output bit-identical to #1 | ✓ | ✓ (new 24-uop network) | ✓ (768 network) | −28 / −70 / −43 vs lazy Forward | [768](ntruplus768-ht-forward.md), [864/1152](ntruplus864-1152-ht.md) |
| 5 | Keygen R² fold: BaseInv input scale R³ → R², keygen BaseMul without its R² pass (`basemul_nor2`) | ✓ | ✓ | ✓ | −81 / −91 / −127 per keygen BaseMul | same |
| 6 | Fused inverse NTT + crepmod3 (`invntt_crep`): σ = Ns·R⁻¹ folded into level-1 twiddles, 8-op level 0, 5-op `crep5` fused into level 0; 864/1152 also split the block pass into two memory passes ("Inverse D") | ✓ (on the HT inverse block, "invc") | ✓ | ✓ | −139 / −252 / −279 vs previous inverse + `crepmod3` | [fused inverse + Shoup](ntruplus-avx2-invd-shoup.md) |
| 7 | Shoup BaseMul for Encap and the 2nd Decap BaseMul: Barrett-companion products, lazy accumulation, canonical scale, no R² pass | ✓ | ✓ | ✓ | −117 / −106 / −193 vs Official `poly_basemul` | same |

In every tree the lazy Forward's arithmetic still runs. HT Forward (#4) produces the same output words with the same
arithmetic; it fuses the first two passes and replaces the data movement in the block pass. The earlier 768
HT inverse block pass is kept inside #6. Its Official levels 1 and 0 are the part that #6 rewrites.

### Call sites in `kem.c`

| Call | Official | Current best |
|---|---|---|
| Forward NTT (keygen f, g; encap r; decap ×2 + re-encryption; 6 in total) | `poly_ntt` | `ntruplus<N>_officialopt_ntt_ht` |
| BaseInv (keygen f, g) | `poly_baseinv` | `ntruplus<N>_officialopt_baseinv_r2fold` |
| BaseMul (keygen ×2) | `poly_basemul` | `ntruplus<N>_officialopt_basemul_nor2` |
| BaseMul (Encap `h·r̂`; Decap 2nd `(c − f̂)·hinv`) | `poly_basemul` | `ntruplus<N>_officialopt_basemul_shoup` |
| BaseMulScale (Decap 1st `c·f`) | `poly_basemul_scale` | unchanged (the fused-inverse range proof depends on its output range) |
| `poly_tobytes` (7) | `pack.s` | 768/1152 `…_tobytes_freeze2op`, 864 `…_tobytes_direct` |
| `poly_frombytes` | `pack.s` | 768/1152 unchanged, 864 `…_frombytes_direct` |
| Inverse NTT + crepmod3 (Decap) | `poly_invntt_scale(&m); poly_crepmod3(&m);` | one call, `ntruplus<N>_officialopt_invntt_crep(&m)` |
| SHAKE256 (`hash_*`, keygen seed) | XKCP `KeccakP-1600-AVX2.s` via `fips202.c` | `mlk_shake256` via the `fips202.h` adapter |

The `kem.c` changes are of three kinds:

- a preprocessor overlay (`#define` of the Forward and codec names);
- the three keygen call-site edits for the R² fold;
- two Shoup call sites and one fused-inverse call site.

The KEM flow itself is Official's. The only structural change is that the Decap inverse and `crepmod3`, which were
already adjacent, are now one call.

### Files in the exported tree

Apart from the codec files, all three trees have the same file set. "Unchanged" means byte-identical to Official.

| | files |
|---|---|
| Added | `ntt_ht.s`, `ntt_caller_lazy.s`, `basemul_nor2.s`, `basemul_shoup.s`, `invntt_crep.s`, `baseinv_r2fold.c`, `mlk_{cbmc,common,context,fips202,keccakf1600,params,sys,verify}.h`, `mlk_fips202.c`, `mlk_keccakf1600.c`, `mlkem_native_config.h`, `LICENSE.mlkem-native`; 768/1152 `tobytes_freeze2op.s`; 864 `codec_direct.s` |
| Removed | `KeccakP-1600-AVX2.s`, `KeccakP-1600-SnP.h`, `fips202.c` (and, in 768, the previous `invntt_ht.s`, now subsumed by `invntt_crep.s`) |
| Changed | `kem.c` (call rebinding), `fips202.h` (drop-in adapter to mlkem-native) |
| Unchanged | `add.s`, `api.h`, `architectures`, `baseinv.s`, `basemul.s`, `cbd.s`, `consts.c`, `consts.h`, `crepmod3.s`, `goal-*`, `invntt.s`, `ntt.s`, `pack.s`, `params.h`, `poly.c`, `poly.h`, `symmetric.c`, `symmetric.h`, `util.h` |

**`basemul_shoup.s` is committed and shipped as assembly.** SUPERCOP assembles it directly, and no compiler
regenerates it at build time. It was produced once by pinned gcc 15.2.0
(`-O3 -mavx2 -mtune=alderlake -fschedule-insns -fsched-pressure …`) from a generated C file. The generator's
`--check` recompiles that C with the same pinned compiler and requires byte identity with the committed `.s`,
which documents where the file came from. The committed `.s` spills to 2 (864) or 5 (768/1152) fixed stack slots
at fixed `%rsp` offsets. The slots are not cleared on return, the same as compiler spills in the C KEM.

**Code that is no longer called.** The linked audits show 0 calls to any of the following:

- `ntt_caller_lazy.s`: every forward call is macro-rebound to `ntt_ht`;
- the Official `poly_ntt` (`ntt.s`), `poly_invntt_scale` (`invntt.s`) and `poly_crepmod3` (`crepmod3.s`);
- the Official `poly_basemul` in `basemul.s`, where only `poly_basemul_scale` is still used;
- in 864, the Official `poly_tobytes`/`poly_frombytes`.

The research exports keep these files so that the base export's files stay byte-identical. A production package
should drop them.

## 3. Performance against Official (Native, 2026-09-25)

Setup:

- SUPERCOP 20260831 Native on an Intel Core Ultra 7 155H, CPU 1, performance governor, turbo off, ASLR on;
- unmodified `measure.c` and SUPERCOP's default compiler selection;
- **81 fresh launches per role** (9 rotating 9-launch batches) under `phase_b_batch.py`, campaign tag `20260925is`.

Values are pooled StQ2 cycles. The CI is a 95% interval from resampling launches within each role, with 2,000
resamples. "fav." counts current-best launches below the median Official launch.

| n | op | Official | Current best | Δ vs Official [95% CI] | fav. |
|---:|---|---:|---:|---:|---:|
| 768 | keypair | 21,607.3 | 16,592.4 | **−5,014.9 (−23.2%)** [−5,033.1, −4,999.2] | 81/81 |
| 768 | encap | 28,182.5 | 20,359.8 | **−7,822.6 (−27.8%)** [−7,866.8, −7,784.4] | 81/81 |
| 768 | decap | 19,456.1 | 14,725.0 | **−4,731.1 (−24.3%)** [−4,749.2, −4,714.4] | 81/81 |
| 864 | keypair | 23,749.1 | 17,621.6 | **−6,127.5 (−25.8%)** [−6,143.1, −6,110.9] | 81/81 |
| 864 | encap | 32,940.4 | 23,172.8 | **−9,767.6 (−29.7%)** [−9,806.2, −9,734.2] | 81/81 |
| 864 | decap | 23,674.9 | 16,889.8 | **−6,785.1 (−28.7%)** [−6,808.1, −6,764.1] | 81/81 |
| 1152 | keypair | 34,624.2 | 26,732.2 | **−7,891.9 (−22.8%)** [−8,217.7, −7,560.3] | 81/81 |
| 1152 | encap | 43,116.9 | 30,958.0 | **−12,158.9 (−28.2%)** [−12,189.7, −12,131.4] | 81/81 |
| 1152 | decap | 30,550.4 | 22,973.3 | **−7,577.0 (−24.8%)** [−7,591.4, −7,563.8] | 81/81 |

The fixed-ELF paired control (O3GC ELFs, ASLR on, normal placement, 48 ABBA/BAAB blocks, current best minus
Official) agrees with Native within 3%. All 9 (n, op) pairs are 48/48 favourable.

| n | keypair | encap | decap |
|---:|---:|---:|---:|
| 768 | −5,031.1 [−5,047.4, −5,015.1] | −7,801.5 [−7,824.2, −7,777.7] | −4,753.3 [−4,771.4, −4,735.5] |
| 864 | −6,288.7 [−6,298.4, −6,279.3] | −9,660.8 [−9,693.3, −9,631.9] | −6,908.0 [−6,925.4, −6,891.4] |
| 1152 | −7,802.5 [−8,071.1, −7,521.3] | −12,074.3 [−12,121.3, −12,033.1] | −7,472.1 [−7,510.3, −7,440.9] |

Compiler picks under default selection:

- The current best took O3 in 9/9 batches for every n.
- Official took O2 in 8/9 batches for 768, O3 in 6/9 and O2 in 3/9 for 864, and O3 in 9/9 for 1152.

The Native Δ is therefore the default-selection difference, which is the one that matters for production. The
paired rows fix the compiler at O3GC.

## 4. Contribution by step

Each step is measured against the step before it, in its own Native campaign (pooled StQ2 Δ).

| Step | Campaign | Launches per role |
|---|---|---:|
| 1+2 (lazy + freeze/codec) and 3 (Keccak) | `20260924k` | 27 |
| 4–5 (HT) | `20260925h` (768), `20260925ht` (864/1152) | 81 |
| 6–7 (fused inverse + Shoup) | `20260925is` | 81 |

The four columns add up to the direct Δ in §3 within the noise of the separate runs. For example, 768 decap:
−318.9 − 4,103.7 − 91.0 − 230.6 = −4,744.2, against −4,731.1 measured directly.

| n | op | 1+2: lazy + freeze/codec vs Official | 3: + mlkem-native Keccak | 4–5: + HT (vs Keccak base) | 6–7: + fused inverse + Shoup (vs HT) [95% CI] |
|---:|---|---:|---:|---:|---:|
| 768 | keypair | −214.7 | −4,536.4 | −263.4 | −6.3 [−21.4, +8.8] (no keygen change) |
| 768 | encap | −159.6 | −7,467.4 | −75.2 | **−91.7** [−108.9, −72.7] |
| 768 | decap | −318.9 | −4,103.7 | −91.0 | **−230.6** [−242.3, −218.3] |
| 864 | keypair | −849.7 | −4,923.4 | −383.0 | +19.7 [+3.9, +34.7] (no keygen change) |
| 864 | encap | −813.5 | −8,702.1 | −93.7 | **−131.3** [−149.2, −113.2] |
| 864 | decap | −1,335.9 | −4,886.7 | −137.5 | **−425.2** [−437.5, −413.6] |
| 1152 | keypair | −540.7 (CI crosses 0) | −7,059.9 | −259.9 | −8.0 [−289.8, +271.1] (no keygen change) |
| 1152 | encap | −444.9 | −11,438.4 | −144.7 | **−116.8** [−149.7, −86.1] |
| 1152 | decap | −397.8 | −6,649.8 | −116.7 | **−376.0** [−393.8, −359.9] |

What the steps show:

- **Keccak dominates.** mlkem-native Keccak is 72–95% of the total gain per op (lowest: 864 decap, where the codec is large). SHAKE took 64–86% of every Official
  operation (2026-09-23 overview, §2).
- **Non-hash levers, by gain per op:**
  - the 864 direct codec (−814 to −1,336);
  - the fused inverse + Shoup at Decap (−231 to −425);
  - the 768/1152 lazy Forward + 2-op freeze (−160 to −541);
  - HT (−75 to −383, largest at keypair);
  - the fused inverse + Shoup at Encap (−92 to −131).

Paired controls, candidate minus previous step (O3GC, ASLR on, 48 blocks). Normal placement is primary, reversed
is secondary.

| n | op | HT vs Keccak base, normal / reversed | fused inverse + Shoup vs HT, normal [CI] / reversed |
|---:|---|---|---|
| 768 | keypair | −292.8 / −187.6 | +50.2 [+39.5, +61.3] / +33.8 (placement; no keygen change) |
| 768 | encap | −61.0 / **+24.4** | −118.6 [−146.7, −76.8] / −169.2 |
| 768 | decap | −99.1 / −106.8 | −303.2 [−315.2, −292.0] / −324.6 |
| 864 | keypair | −376.5 / −307.2 | −7.2 [−17.8, +3.3] / +42.1 (placement) |
| 864 | encap | −133.8 / −147.7 | −126.3 [−138.1, −114.6] / −89.6 |
| 864 | decap | −161.2 / −196.8 | −391.4 [−400.5, −382.6] / −328.7 |
| 1152 | keypair | −260.8 / −262.7 | −178.9 [−392.8, +33.9] / +116.6 (retry tail) |
| 1152 | encap | −133.6 / −89.8 | −147.6 [−162.1, −133.0] / −83.4 |
| 1152 | decap | −109.5 / −23.9 | −396.1 [−408.5, −383.4] / −419.0 |

## 5. Known flags

- **Keypair got nothing from steps 6–7.** No keygen code changed, so the keypair deltas are placement noise.
  768's paired keypair is +50 / +34 and 864's reversed is +42. These fail the rule and are reported, not claimed.
- **HT on 768 encap is placement-sensitive.** With reversed placement it is +24. Steps 6–7 then add −92 (Native),
  and both link orders are below zero, so the current best's 768 encap is a robust win over the Keccak base.
- **1152 keypair is noisy** because of the BaseInv retry heavy tail. For HT, seed-matched supporting evidence gives
  −325.9 [−350.1, −299.4] (18/18).
- **The 768 fused inverse** builds on the HT inverse block pass. The HT inverse itself was never resolved at KEM
  level on its own. The fused level 1/0 adds −162 / −134 at Decap on top of Shoup (31/31).
- **Two proofs depend on caller ranges:**
  - The fused inverse assumes its input is the unchanged `poly_basemul_scale(c, f)` output with canonical c and f.
  - Shoup assumes the `a` operand stays inside the proven lazy/HT Forward envelopes and that `b` is canonical
    (`frombytes`-checked pk/sk).
  - Any change to those producers requires re-proving.
- **Keccak is compiler-sensitive.** It needs `-O3` vectorisation of the mlkem-native byte loops. With SUPERCOP's
  default selection the current best picks O3 every time.
- **Dead code remains in the exported trees** (§2).
- **Relation to `AGENTS.md`.** `AGENTS.md` asks this branch to keep Official's Montgomery domain and terminal factors.
  The R² fold (#5), the fused inverse's σ-fold (#6) and Shoup (#7) move or remove Montgomery/terminal scale factors
  *inside* a function. Every function's output still equals Official's. It is bit-identical after `crepmod3` and
  `tobytes`, and the Shoup and nor2 outputs are equal mod q in Official's scale. Wire format and KEM API are unchanged.

## 6. Correctness evidence

Every technique passed its Phase A gate set before export:

- deterministic generators with pinned inputs and `--check` (Shoup: pinned-compiler recompile);
- symbolic-execution identity for every asm change;
- interval range proofs on every caller domain;
- algebraic identity proofs: the R² fold, the σ-fold, the Shoup per-term bounds, and a mod-q basis check;
- exhaustive `crep5` domain;
- C differentials;
- the shared KEM test: 100 vectors pk/sk/ct/ss byte-exact against Official; invalid PK; tampered and noncanonical
  CT/SK; forced g retry and f failure;
- ASan + UBSan + LSan;
- a linked-call audit;
- mutation checks.

Each flat export was then shown to be exactly what Phase A tested, by three checks:

- a flat-tree KEM test in release and sanitizer builds;
- a flat linked audit;
- object identity against the Phase A objects.

The details are in each experiment's STATUS.yml, in the `invshoup_candidate`, `ht_candidate`, `keccak_*` and
`freeze2op`/codec sections.

## Methodology

**Decision rule (research win).** A change is a robust research win only if both of these hold:

- the pooled Native Δ is below zero, with the default compiler selection;
- the fixed-ELF paired 95% CI, with normal placement and ASLR on, lies entirely below zero.

Reversed placement is reported alongside, and any disagreement is flagged. ASLR-off runs are not used.

## Evidence

| n | Native + paired summary (current best) | earlier steps | docs |
|---:|---|---|---|
| 768 | `NTRU+768/experiments/avx2_official_opt_freeze_001/results/extended-multi-summary-20260925is.json` | `…-20260925h.json`, `…-20260924k.json` | [invd-shoup](ntruplus-avx2-invd-shoup.md), [HT 768](ntruplus768-ht-forward.md) |
| 864 | `NTRU+864/experiments/avx2_official_opt_001/results/extended-multi-summary-20260925is.json` | `…-20260925ht.json`, `…-20260924k.json` | [invd-shoup](ntruplus-avx2-invd-shoup.md), [HT 864/1152](ntruplus864-1152-ht.md) |
| 1152 | `NTRU+1152/experiments/avx2_official_opt_001/results/extended-multi-summary-20260925is.json` | `…-20260925ht.json`, `…-20260924k.json` | same |

Keccak: [ntruplus-avx2-keccak-mlkem-native.md](ntruplus-avx2-keccak-mlkem-native.md).

## Studied but not adopted (2026-09-25)

- **Joint f/g batch inversion (keygen).** Bit-identical and about −200 per keygen at component level, but it reorders
  the keypair flow and its KEM gain is placement-sensitive. On hold.
- **Codec fusions:**
  - I2 (`poly_add` + `tobytes` at Encap) is on hold, because it fuses across the KEM flow.
  - I3 (R² + `tobytes` at Decap) is superseded by Shoup.
  - I1, a hand-asm 768/1152 pack, is on hold until an unexplained store-forwarding interaction with `hash_g` is
    resolved.
- **Not worth it:** `frombytes` redesign, lazy Barrett in the inverse, the 864 5-stage inverse network, Karatsuba,
  `vpmaddwd` BaseMul, and Shoup for the Decap `basemul_scale`.

## Next toward production (not done)

1. **Clean package.** Build a `clean/` tree per parameter with the dead files removed, the call names bound
   directly instead of through overlay macros, and a single `kem.c`. Decide whether Shoup's stack spill slots must
   be cleared.
2. **Constant-time review.** Review the whole package. The new asm has fixed trip counts and no data-dependent
   branches or addresses by construction, but the package as a whole has not been audited. The mlkem-native Keccak
   hash path had its own review (`audit_keccak_ct.py`; see the Keccak doc).
3. **Re-confirm with Native.** Run a Native re-confirmation of the release package against these research exports.

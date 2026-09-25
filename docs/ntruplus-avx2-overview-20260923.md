# NTRU+768 / 864 / 1152 AVX2 overview: Official vs Official-opt vs GT (2026-09-23)

> **Dated snapshot.** The Official-opt rows below are the 2026-09-23 exports, from before the mlkem-native Keccak,
> HT, fused-inverse and Shoup changes. The current best and its comparison against Official are in
> [ntruplus-avx2-official-opt-current-best.md](ntruplus-avx2-official-opt-current-best.md) (2026-09-25).
> The GT comparison and the component profiler here are still the latest of their kind.

Branch `official-opt-lazy-864-1152`, SUPERCOP 20260831, Intel Core Ultra 7 155H, CPU 1,
performance governor, turbo off (checked, not changed), ASLR on (`randomize_va_space=2`),
normal placement only. This is a quick overview, not a full qualification. It has no fixed-ELF
paired controls and no reversed-placement runs. Curated data is in
[`results/avx2-overview-20260923/`](../results/avx2-overview-20260923/); raw launches stay
local under `results/avx2-overview-20260923/raw/` (Git-ignored).

## Implementations

All directories below are under `ntruplus-ntt-Optimized/Additional_Implementation/avx2/`.
Installed into the disposable campaign `/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001`.

| n | role | SUPERCOP implementation | source | tree sha256 (installed) |
|---:|---|---|---|---|
| 768 | Official | `avx2` | pinned SUPERCOP (`bench/supercop.lock`) | `8db00172…d576e7` |
| 768 | Official-opt | `avx2-officialopt-lazy-freeze-qual001` | candidate `avx2-officialopt-lazy-freeze-768-exp001` (lazy Forward + 2-op freeze `poly_tobytes`), exported from `NTRU+768/experiments/avx2_official_opt_freeze_001/qualification/` (manifest `avx2-officialopt-lazy-freeze-qual001.json`) | `2d9fa350…666d5f` |
| 768 | GT | `avx2-gt32-clean` | `NTRU+768/clean/avx2-gt32-clean` (unchanged since `66de7d6`; source tree `bd0b07d5…2d639f`), installed with `scripts/install_supercop_768_clean.py` | `5b1ca00f…ed1ecc` (includes the time-stamped `SOURCE-MANIFEST.json`) |
| 864 | Official | `avx2` | pinned SUPERCOP | `13e0d983…107006` |
| 864 | Official-opt | `avx2-officialopt-lazy-codec-qual002` | candidate exp002 (lazy Forward + direct 12-bit codec), already installed | `ece23c1a…9c06c0` |
| 864 | GT | none | no GT KEM candidate, so N/A | – |
| 1152 | Official | `avx2` | pinned SUPERCOP | `78daf6b9…5c365010` |
| 1152 | Official-opt | `avx2-officialopt-lazy-freeze-qual001` | candidate `avx2-officialopt-lazy-freeze-1152-exp001`, exported from `NTRU+1152/experiments/avx2_official_opt_001/qualification/` | `3e8068bb…0f76a9914` |
| 1152 | GT | `avx2-gt9x16-wire-h3-pairunpack-serializer-v2-exp017-sc20260831` | tracked flat tree `NTRU+1152/experiments/avx2_gt9x16_official_001/candidates/…` at `72d7eb7` (branch `avx2-gt-ntt`), extracted with `git archive`; `sha256sum -c SHA256SUMS` passes, and `SHA256SUMS` / `SOURCE-MANIFEST.json` hashes (`285330f5…`, `414f58f3…`) equal the 2026-09-20 Native run | `380282be…0421ec` |

The two lazy-freeze exports were made with the existing exporter, which now has a
`--variant lazy-freeze` option for 768/1152 (`kem.c` = `src/kem_lazy_freeze2op.c` flattened, plus
`ntt_caller_lazy.s` and `tobytes_freeze2op.s`). They were installed with `install_qualification.py`.
SUPERCOP `try` reported `ok` for every implementation in every batch, with one checksum per n
shared by all implementations (768 `aa9f61a0…/3a04f700…`, 864 `b0cdac76…/206acd11…`,
1152 `2275d102…/16659d2c…`). There were no `tryfails` or `measurefails`.

## 1. Native (measured)

The unmodified `measure.c` and SUPERCOP's default compiler selection were used. Each
implementation got 27 fresh launches, as 3 batches of 9. The role order rotated per round
(A,B,C / C,A,B / B,C,A; for 864, A,B / B,A / A,B). Every batch ran under `phase_b_batch.py`, and
all 24 batches were accepted on attempt 0 with no contamination.

The delta is the pooled StQ2 of the candidate minus Official. The CI is a 95% interval from
resampling launches within each role (2000 resamples). "Below median" counts the candidate's
launches whose StQ2 is below the median Official launch.

| n | op | Official | Official-opt | opt − Official [95% CI] | below median | GT | GT − Official [95% CI] | below median |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 768 | keypair | 21612.2 | 21358.6 | −253.6 (−1.17%) [−281.7, −230.3] | 27/27 | 21266.8 | −345.4 (−1.60%) [−375.6, −314.7] | 27/27 |
| 768 | enc | 28178.5 | 28067.6 | −110.9 (−0.39%) [−215.5, −28.9] | 24/27 | 28383.4 | +204.9 (+0.73%) [+87.7, +305.1] | 1/27 |
| 768 | dec | 19449.3 | 19193.1 | −256.2 (−1.32%) [−290.7, −218.7] | 27/27 | 19204.1 | −245.2 (−1.26%) [−278.7, −205.5] | 26/27 |
| 864 | keypair | 23745.8 | 22881.3 | −864.6 (−3.64%) [−907.6, −828.4] | 27/27 | N/A | N/A | N/A |
| 864 | enc | 32901.8 | 32107.2 | −794.6 (−2.42%) [−853.2, −752.5] | 27/27 | N/A | N/A | N/A |
| 864 | dec | 23681.8 | 22340.6 | −1341.2 (−5.66%) [−1392.7, −1300.3] | 27/27 | N/A | N/A | N/A |
| 1152 | keypair | 34626.0 | 34312.1 | −313.9 (−0.91%) [−810.8, +159.7] **not resolved at 27 launches** | 19/27 | 34319.9 | −306.1 (−0.88%) [−845.5, +244.3] **not resolved at 27 launches** | 16/27 |
| 1152 | enc | 43114.9 | 42403.6 | −711.2 (−1.65%) [−834.0, −648.2] | 27/27 | 43905.2 | +790.3 (+1.83%) [+679.3, +862.9] | 0/27 |
| 1152 | dec | 30540.3 | 29970.1 | −570.2 (−1.87%) [−600.6, −544.2] | 27/27 | 30551.6 | +11.3 (+0.04%) [−14.1, +31.4] **not resolved at 27 launches** | 7/27 |

No conclusion is drawn from the three unresolved rows. 1152 keypair is dominated by the BaseInv
retry heavy tail (per-batch opt deltas −576 / −285 / −77; GT −351 / +34 / −609). The GT keypair
path is byte-identical Official code, so any keypair delta there is noise.

Compiler picks (SUPERCOP default selection, batches 1/2/3):

- 768: Official O2/O2/O2; opt O2/O2/O3; GT O3/O2/O2.
- 864: Official O3/O3/O3; opt O2/O3/O2.
- 1152: Official O3/O3/O3; opt O2/O2/O2; GT O3/O3/O3.

The 768 opt enc delta depends on the pick. Its per-batch deltas are −294 and −95 in the two O2
batches and −37 in the O3 batch, so its size is uncertain even though the CI excludes zero.

## 2. Component profiler (supercop-derived, diagnostic)

There is one ELF per n that contains every implementation. Each tree is compiled in full with
its own headers and a small adapter (`bench/overview/adapter_*.c`), using the O3GC recipe
(`gcc -march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -ffunction-sections -fdata-sections
-gdwarf-4 -Wall`, linked with `--gc-sections`). The tree is archived and the adapter pulls only
the members it needs, as SUPERCOP's library link does. Every defined global symbol is then
prefixed with the role (`objcopy --redefine-syms`), and the result is linked with
`bench/overview/harness.c` and the campaign's `libcpucycles`.

The harness gives every implementation the same seeded `randombytes`. A preflight traps unless,
over 8 seeds, all roles produce byte-identical pk/sk/ct/ss and identical hash_f/g/h. It passed
in every launch.

Each launch times one call per observation: 4 warm-ups, then 32 calls over 16 banks, with
untimed preparation before each call (for example, restoring an in-place input). There are
12 blocks per component, and the implementations rotate order in each block. The runs used
15 fresh launches per n under `phase_b_batch.py` (attempt 0 each), for 5,760 observations per
(component, role).

The CI is a 95% interval from resampling launches jointly, since every launch measures every
role. "fav." counts launches where the role's StQ2 is below Official's.

ELF sha256: 768 `fa5ddbac…94e3830`, 864 `7b8c3538…76b00ca`, 1152 `9e6bbd7c…e5015b4`.

"Forward" is the version each implementation actually calls:

- Official: `poly_ntt`.
- Official-opt: the lazy caller Forward.
- GT768: `forward_p` (frontend + P terminal, keygen) and `forward_m` (frontend + M terminal,
  encap/decap).
- exp017: `gt_forward` (top split + prod3 lazy reduce) in Encap, and Official `poly_ntt` in
  keygen/decap.

"tobytes" / "frombytes" are the bound codecs. Official-opt 768/1152 uses freeze2op `tobytes`
and Official `frombytes`. 864 opt uses the direct 12-bit codec both ways.

### Common primitives (StQ2 cycles per call)

| n | role | forward | BaseMul | BaseMulScale | BaseInv | inverse | frombytes | tobytes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 768 | Official | 953.3 | 725.8 | 643.6 | 1248.5 | 962.0 | 358.8 | 424.9 |
| 768 | opt | 850.7 (−102.6, 15/15) | 733.2 (+7.4) | 645.2 (+1.6) | 1262.4 (+13.9) | 969.1 (+7.1) | 364.4 (+5.6) | 410.6 (−14.3, 15/15) |
| 768 | GT32 | m 892.6 / p 906.6 | general_m 740.7 / f0_j1 621.5 | scale_m 642.6 | j1 1196.5 | inverse_m 968.6 | unpack_m 404.6; unpack3_m 802.4 (= 3 decodes) | pack_m_lazy 473.2 / highrange 477.2 / centered 416.2 / pack_p 457.0 |
| 864 | Official | 1093.8 | 677.0 | 580.6 | 1182.3 | 1153.4 | 671.1 | 692.2 |
| 864 | opt | 1003.0 (−90.8, 15/15) | 677.7 (+0.7) | 571.7 (−8.8) | 1181.9 (−0.5) | 1145.9 (−7.6) | 395.4 (−275.7, 15/15) | 438.9 (−253.2, 15/15) |
| 1152 | Official | 1388.6 | 995.4 | 858.1 | 1608.2 | 1425.7 | 437.3 | 541.1 |
| 1152 | opt | 1253.8 (−134.8, 15/15) | 995.6 (+0.2) | 868.2 (+10.1) | 1605.0 (−3.2) | 1419.1 (−6.6) | 445.5 (+8.2) | 519.0 (−22.1, 15/15) |
| 1152 | exp017 | Encap `gt_forward` 1492.3; keygen/decap Official 1389.8 | Encap: fused in H4; else Official 993.4 | Official 858.9 | Official 1601.0 | Official 1409.8 | Encap: fused in H4; else 441.6 | Encap: r fused in Serializer V2 (alone 702.0), ct fused in H4; else 543.1 |

GT768 does not isolate an equality-free re-encryption `tobytes`. Instead, `equal_m_modq`
(331.9) replaces the re-encryption `tobytes` + `verify` in Decap.

exp017 fused blocks: `serializer_v2_hash_g` 18337.0 (r tobytes + hash_g) and `h4_exact_egress`
1993.6 (pk frombytes + BaseMul + add + ct tobytes).

### Caller building blocks (StQ2 cycles per call)

| n | role | hash_f | hash_g | hash_h | shake256 (keygen seed) | SOTP enc | SOTP dec | CBD1 | triple | crepmod3 | add | sub |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 768 | Official | 10932.8 | 12133.3 | 2659.0 | 2609.1 | 336.6 | 372.2 | 328.2 | 245.6 | 390.9 | 294.1 | 291.2 |
| 768 | opt | 10948.2 | 12151.4 | 2661.7 | 2607.0 | 328.8 | 372.4 | 330.5 | 235.0 | 392.1 | 293.1 | 295.0 |
| 768 | GT32 | 10950.6 | 12179.5 | 2655.6 | 2598.6 | 330.3 | 372.3 | 324.0 | 241.3 | 392.4 | 297.8 | 290.0 |
| 864 | Official | 12148.6 | 13374.1 | 3823.2 | 2613.5 | 378.0 | 437.6 | 364.7 | 243.5 | 413.4 | 299.8 | 301.5 |
| 864 | opt | 12142.7 | 13313.1 | 3843.3 | 2606.8 | 376.1 | 428.0 | 370.6 | 242.9 | 419.6 | 296.9 | 301.2 |
| 1152 | Official | 15736.0 | 18142.7 | 4992.9 | 3771.6 | 422.2 | 496.0 | 422.7 | 288.2 | 493.9 | 357.9 | 352.9 |
| 1152 | opt | 15712.2 | 18117.7 | 5002.5 | 3776.5 | 424.0 | 493.9 | 415.9 | 284.4 | 489.5 | 358.0 | 358.3 |
| 1152 | exp017 | 15662.9 | 18001.2 | 4969.5 | 3764.7 | 419.7 | 499.4 | 424.5 | 285.6 | 489.1 | 355.7 | 354.5 |

Some of these roles compile the same source. The Official-opt exports' `fips202.c`,
`symmetric.c`, `cbd.s`, `add.s` and `crepmod3.s` are Official's. exp017's `fips202.c`,
`symmetric.c`, `ntt.s`, `basemul.s`, `baseinv.s`, `invntt.s`, `pack.s`, `poly.c` and `consts.c`
are byte-identical to Official. Their same-ELF deltas are therefore placement effects and set the
noise floor of this diagnostic: up to about ±10 cycles on small primitives and ±25 cycles on
hashes (768/864), and down to −141 on 1152 `hash_g` and −157 on 1152 `kem_dec` for exp017. The
per-role CIs are tight because they cover launch-to-launch noise only, not address placement.

### Same-ELF KEM (StQ2, 15 launches, seed-matched)

| n | op | Official | opt (Δ [CI], fav.) | GT (Δ [CI], fav.) |
|---:|---|---:|---:|---:|
| 768 | keypair | 21609.2 | 21383.9 (−225.3 [−242.6, −211.7], 15/15) | 21332.0 (−277.2 [−307.4, −235.3], 15/15) |
| 768 | enc | 28442.5 | 28373.0 (−69.5 [−97.9, −43.4], 15/15) | 28620.9 (+178.4 [+138.0, +227.2], 0/15) |
| 768 | dec | 19495.4 | 19333.9 (−161.5 [−179.8, −144.4], 15/15) | 19367.1 (−128.2 [−168.8, −77.9], 13/15) |
| 864 | keypair | 23835.1 | 22931.4 (−903.7 [−911.8, −893.5], 15/15) | N/A |
| 864 | enc | 33285.4 | 32241.1 (−1044.4 [−1068.6, −1015.8], 15/15) | N/A |
| 864 | dec | 23867.2 | 22329.3 (−1537.9 [−1552.3, −1516.9], 15/15) | N/A |
| 1152 | keypair | 34590.8 | 34222.6 (−368.2 [−397.0, −337.6], 15/15) | 34630.2 (+39.4 [+12.7, +63.9], 3/15; Official code) |
| 1152 | enc | 43232.0 | 42967.3 (−264.8 [−314.4, −226.7], 15/15) | 43996.8 (+764.8 [+719.7, +812.7], 0/15) |
| 1152 | dec | 30603.7 | 30217.6 (−386.1 [−414.2, −357.3], 15/15) | 30446.8 (−156.9 [−174.5, −134.0], 15/15; Official code) |

The keypair is seed-matched: every role gets the same randomness, so BaseInv retries are
identical across roles.

### Caller-level breakdown (anchors = count × isolated StQ2)

Each anchor is an isolated building block measured from its own warm state. The anchors are not
cumulative cut points, and their sum is not a waterfall. The full per-stage table for every n,
op and role, with component names and counts, is in
[`breakdown.csv`](../results/avx2-overview-20260923/breakdown.csv). The condensed view below
shows where each candidate spends or saves cycles against Official (anchor sum Δ), and how that
compares with the same-ELF KEM and Native deltas.

| n | op | role | main anchor savings (−) / costs (+) vs Official | anchor-sum Δ | same-ELF KEM Δ | Native Δ |
|---:|---|---|---|---:|---:|---:|
| 768 | keypair | opt | Forward ×2 −205, tobytes ×3 −43, triple −21; BaseInv ×2 +28, BaseMul ×2 +15 | −211 | −225 | −254 |
| 768 | keypair | GT | BaseMul f0_j1 ×2 −209, BaseInv j1 ×2 −104, forward_p ×2 −93; pack_p ×3 +96 | −330 | −277 | −345 |
| 768 | enc | opt | Forward ×2 −205, tobytes ×2 −28 | −191 | −70 | −111 |
| 768 | enc | GT | forward_m ×2 −121; pk unpack +46, pack_m_lazy +48, pack_m_highrange +52, hash_g +46 (noise) | +94 | +178 | +205 |
| 768 | dec | opt | Forward ×2 −205, tobytes ×2 −28; frombytes ×3 +17 | −172 | −162 | −256 |
| 768 | dec | GT | unpack3_m −274 (vs 3 frombytes), forward_m ×2 −121, equal_m −93 (vs tobytes) | −437 | −128 | −245 |
| 864 | keypair | opt | tobytes ×3 −760, Forward ×2 −182 | −949 | −904 | −865 |
| 864 | enc | opt | frombytes −276, tobytes ×2 −506, Forward ×2 −182 | −1009 | −1044 | −795 |
| 864 | dec | opt | frombytes ×3 −827, tobytes ×2 −506, Forward ×2 −182 | −1570 | −1538 | −1341 |
| 1152 | keypair | opt | Forward ×2 −270, tobytes ×3 −66 | −377 | −368 | −314 (unresolved) |
| 1152 | enc | opt | Forward ×2 −270, tobytes ×2 −44 | −349 | −265 | −711 |
| 1152 | enc | exp017 | gt_forward ×2 +207 vs Official Forward (in-place); Serializer V2 + hash_g 18337 vs tobytes + hash_g 18684 (−347); H4 egress 1994 vs frombytes + BaseMul + add + tobytes 2332 (−338); hash_f/hash_h −96 (identical code, placement) | −575 | +765 | +790 |
| 1152 | dec | opt | Forward ×2 −270, tobytes ×2 −44; frombytes ×3 +25 | −309 | −386 | −570 |

Two points explain the table:

- The anchor sum exceeds the same-ELF KEM total for 768/864 by 11–15%. Isolated SHAKE calls
  are slower than the same calls inside the KEM, as the 2026-09-20 report also noted. For
  1152 keypair the sum is below the total because retries are not counted.
- For exp017 Encap, the fused blocks save about 685 cycles as isolated anchors. Even so, the
  same-ELF and Native Encap are about +770 to +790 slower. That is the known
  fanout/tail/caller-integration debt: the GT Forward costs +207 (two calls), and the rest is
  not visible in isolated anchors. The isolated Official Forward excludes the preserve-input
  copy (restored untimed), whereas `gt_forward` writes out-of-place. The 2026-09-20 report
  compared a copy-inclusive Official Forward and found −2.8.

### Where the time goes (share of the Official anchor sum)

| n | op | hash (hash_f/g/h, keygen shake) | polynomial arithmetic (Forward, BaseMul*, BaseInv, inverse, add/sub, crepmod3) | codec (frombytes/tobytes) | CBD1 / triple / SOTP |
|---:|---|---:|---:|---:|---:|
| 768 | keypair | 66% | 24% | 5% | 5% |
| 768 | enc | 84% | 10% | 4% | 2% |
| 768 | dec | 66% | 22% | 9% | 3% |
| 864 | keypair | 65% | 22% | 8% | 5% |
| 864 | enc | 83% | 9% | 6% | 2% |
| 864 | dec | 64% | 20% | 13% | 3% |
| 1152 | keypair | 68% | 23% | 5% | 4% |
| 1152 | enc | 86% | 9% | 3% | 2% |
| 1152 | dec | 69% | 21% | 7% | 3% |

Per n:

- **768.** SHAKE is two thirds of keygen/decap and 84% of Encap. Official-opt saves mostly in
  Forward (−103/call) and a little in tobytes (−14/call). GT32 saves more in keygen
  (f0_j1 BaseMul, j1 BaseInv) and decap (fused unpack3, `equal_m` instead of re-encoding). But
  its M-domain pack codecs cost +50–90 per call over Official `tobytes`, which is why GT Encap
  is slower.
- **864.** Codec is the largest non-hash lever: 13% of Official decap and 8% of keygen. The
  direct 12-bit codec cuts `frombytes`/`tobytes` by 41%/37% (−276/−253 per call). That, plus
  the lazy Forward (−91/call), accounts for essentially the whole Native win (−865 / −795 / −1341).
- **1152.** Hash is 68–86%. Official-opt saves in Forward (−135/call) and tobytes (−22/call).
  exp017's fused Encap blocks are cheaper in isolation, but the integrated Encap stays about
  +790 slower, so its debt is outside the isolated anchors.

In every n the remaining polynomial arithmetic is only 9–24% of an operation, and what is left
after these optimizations is mostly SHAKE.

## Caveats

- 27 Native launches per implementation (3 batches) is small. A 9-launch pool drifts by about
  ±70 cycles, and the 1152 keypair retry tail needs far more launches or seed matching. Rows
  marked "not resolved at 27 launches" carry no conclusion. There were no fixed-ELF paired
  controls, so compiler-pick effects (for example 768 opt enc) are not separated out.
- Normal placement and ASLR on only. No reversed placement was run, and the component ELFs use a
  single link order (Official, opt, GT).
- Component numbers are supercop-derived diagnostics (O3GC fixed compiler, one ELF, warm
  isolated calls), not Native. Identical-code comparisons show placement noise of up to about
  150 cycles on hashes and KEM totals in the 1152 ELF. Anchors are not additive.
- The GT768 re-encryption `tobytes` + `verify` is not isolated; the fused `equal_m_modq` is
  shown instead. The exp017 Encap pk-decode, BaseMul, add and ct-tobytes stages exist only
  inside `h4_exact_egress`. `verify` (a byte loop in `kem.c`) is not isolated for any role.
- The lazy-freeze exports were not re-run through Phase A. Their sources are the Phase-A-gated
  experiment files, byte-copied by the exporter (manifest hashes). The SUPERCOP `try` checksum
  and the same-ELF KEM byte-equality preflight are the correctness checks done here.

## Reproduction

```sh
R=/home/nuc/src/ntru_plus-official-opt-864-1152
T=$R/ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/official_opt_lazy/tools
C=/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001; K=$C/crypto_kem
O=$R/results/avx2-overview-20260923/raw
# exports + installs
(cd $R/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_freeze_001 &&
  python3 $T/export_caller_lazy_qualification.py --param 768 --experiment . --output-root qualification --variant lazy-freeze)
(cd $R/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/experiments/avx2_official_opt_001 &&
  python3 $T/export_caller_lazy_qualification.py --param 1152 --experiment . --output-root qualification --variant lazy-freeze)
python3 $T/install_qualification.py --param 768 --campaign-root $C --export-root <768 export dir>
python3 $T/install_qualification.py --param 1152 --campaign-root $C --export-root <1152 export dir>
(cd $R/scripts && python3 install_supercop_768_clean.py --campaign-root $C)
P=ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/experiments/avx2_gt9x16_official_001/candidates/avx2-gt9x16-wire-h3-pairunpack-serializer-v2-exp017-sc20260831
git -C $R archive 72d7eb7 $P | tar -x -C /tmp/x && cp -r /tmp/x/$P $K/ntruplus1152/ && (cd $K/ntruplus1152/avx2-gt9x16-*-exp017-* && sha256sum -c SHA256SUMS)
# Native (example 768; 864 has two roles, 1152 uses the exp017 name for gt)
python3 $T/run_extended_native.py --param 768 --results-dir $O/native-768 --campaign-root $C --tag ov768 \
  --batches 3 --order rotate --role official=avx2 --role opt=avx2-officialopt-lazy-freeze-qual001 --role gt=avx2-gt32-clean
python3 $T/summarize_extended_multi.py --param 768 --results-dir $O/native-768 --tag ov768 --order rotate \
  --roles official,opt,gt --comparison opt:official --comparison gt:official
# components (example 768)
python3 $R/scripts/run_overview_components.py build --param 768 --campaign-root $C --build-dir $O/build-768 \
  --role official=$K/ntruplus768/avx2:official \
  --role opt=$K/ntruplus768/avx2-officialopt-lazy-freeze-qual001:official:OVB_FORWARD=ntruplus768_officialopt_ntt_caller_lazy,OVB_TOBYTES=ntruplus768_officialopt_tobytes_freeze2op \
  --role gt=$K/ntruplus768/avx2-gt32-clean:gt768
#   864 opt: OVB_FORWARD=ntruplus864_officialopt_ntt_caller_lazy,OVB_TOBYTES=ntruplus864_officialopt_tobytes_direct,OVB_FROMBYTES=ntruplus864_officialopt_frombytes_direct
#   1152 gt: --role gt=$K/ntruplus1152/avx2-gt9x16-...-exp017-sc20260831:exp017
python3 $T/phase_b_batch.py --result-dir $O/components-768 --metadata metadata.json -- \
  python3 $R/scripts/run_overview_components.py run --binary $O/build-768/overview-components-768 \
  --launches 15 --cpu 1 --result-dir {RESULT}
python3 $R/scripts/run_overview_components.py summarize --param 768 --result-dir $O/components-768 \
  --output $O/components-768/summary.json
# curated files + tables
python3 $R/scripts/generate_overview_avx2_report.py
```

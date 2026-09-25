# NTRU+768 / 864 / 1152 AVX2 Official-opt: fused inverse (Inverse D) and Shoup BaseMul

Date 2026-09-25, branch `official-opt-lazy-864-1152` (from `60ae07c`; pushed as `d7d69f8`). Two changes on top of the
current best ([ntruplus-avx2-official-opt-current-best.md](ntruplus-avx2-official-opt-current-best.md), the HT
exports), each taken through Phase A (code and correctness), a same-ELF diagnostic, a flat qualification export and
Phase B (Native SUPERCOP and ASLR-on fixed-ELF paired timing), one parameter at a time for all timing:

1. **Fused inverse NTT + crepmod3** in the Decap: `poly_invntt_scale(&m); poly_crepmod3(&m);` becomes one call.
   - NTRU+864 / 1152: **Inverse D** (sigma fold into level 1, 8-op level 0, fused 5-op crepmod3, block pass split in
     two memory passes).
   - NTRU+768: the same level-1/level-0 changes (sigma fold, 8-op level 0, fused crep5) applied to the current best's
     HT inverse (whose block pass already fuses radix-2 level 2; no split). Adopted: it passed every gate and won its
     component diagnostic.
2. **Shoup BaseMul** (Barrett-companion products, lazy accumulation, no R² pass) for the Encap BaseMul and the second
   Decap BaseMul, all three parameters. The Decap `poly_basemul_scale` and the keygen `basemul_nor2` are unchanged.

The user made these candidates the current best on 2026-09-25 (`current_best` in STATUS.yml,
[ntruplus-avx2-official-opt-current-best.md](ntruplus-avx2-official-opt-current-best.md)); `promotion: none` (research status).

**Result.** Both changes are component wins in both link orders for every parameter (31/31 launches). Under the decision
rule (Native default-selection pooled cand − base < 0 AND normal-placement ASLR-on paired 95% CI < 0), **Encap and Decap
are robust research wins for all three parameters**. Keypair runs no changed code; its deltas are placement noise and do
not pass the rule (reported, not claimed):

| cand − base (current best) | Keypair | Encap | Decap |
|---|---|---|---|
| NTRU+768 Native (81/role) | −6.3 [−21.4, +8.8] | **−91.7** [−108.9, −72.7] | **−230.6** [−242.3, −218.3] |
| NTRU+768 paired normal / reversed | +50.2 / +33.8 | −118.6 / −169.2 | −303.2 / −324.6 |
| NTRU+864 Native (81/role) | +19.7 [+3.9, +34.7] | **−131.3** [−149.2, −113.2] | **−425.2** [−437.5, −413.6] |
| NTRU+864 paired normal / reversed | −7.2 / +42.1 | −126.3 / −89.6 | −391.4 / −328.7 |
| NTRU+1152 Native (81/role) | −8.0 [−289.8, +271.1] | **−116.8** [−149.7, −86.1] | **−376.0** [−393.8, −359.9] |
| NTRU+1152 paired normal / reversed | −178.9 / +116.6 | −147.6 / −83.4 | −396.1 / −419.0 |

| | NTRU+768 | NTRU+864 | NTRU+1152 |
|---|---|---|---|
| Experiment | `NTRU+768/experiments/avx2_official_opt_freeze_001` | `NTRU+864/experiments/avx2_official_opt_001` | `NTRU+1152/experiments/avx2_official_opt_001` |
| Base (current best) | `src/kem_lazy_r2fold_freeze2op_keccak_ht_htinv.c`, export `avx2-officialopt-lazy-freeze-keccak-ht-qual001` (`50b22a3f…`) | `src/kem_lazy_r2fold_codec_direct_keccak_ht.c`, export `avx2-officialopt-lazy-codec-keccak-ht-qual001` (`847f5757…`) | `src/kem_lazy_r2fold_freeze2op_keccak_ht.c`, export `avx2-officialopt-lazy-freeze-keccak-ht-qual001` (`3aa2d6ae…`) |
| Candidate | `src/kem_lazy_r2fold_invcrep_shoup_freeze2op_keccak_ht.c` (fused inverse + Shoup) | `src/kem_lazy_r2fold_invcrep_shoup_codec_direct_keccak_ht.c` | `src/kem_lazy_r2fold_invcrep_shoup_freeze2op_keccak_ht.c` |
| Controls | shoup (`…_shoup_freeze2op_keccak_ht_htinv.c`, HT inverse kept), invcrep_only (`…_invcrep_freeze2op_keccak_ht.c`) | invd_only (`…_invcrep_…`), shoup_only (`…_shoup_…`) | same |
| Export (tree SHA-256) | `avx2-officialopt-lazy-freeze-keccak-ht-invc-shoup-qual001` (`d107a77fddbec827333a660fea4c93eebf0a8f4d594539adcf35e3a0ab6b23d8`) | `avx2-officialopt-lazy-codec-keccak-ht-invd-shoup-qual001` (`b1d546b3e88abf9fde6a6035317c3a2705086fe88aca7e668da96eea15aa0cc4`) | `avx2-officialopt-lazy-freeze-keccak-ht-invd-shoup-qual001` (`94fc539de23a604f00560016109d2f1fc4f1f921d2f569d1adf3176f82946b75`) |

The 768 export name uses `invc` (not `invd`) because the 768 inverse is the HT inverse with the level-1/0 changes, not
Inverse D (no split). Paths below are relative to `ntruplus-ntt-Optimized/Additional_Implementation/avx2/`. The scratch
prototypes (`scratchpad/remaining-invntt/`, `scratchpad/remaining-basemul-baseinv/`) were exploratory; the repo versions
are the deterministic generators of `common/official_opt_invshoup/`.

## 1. Fused inverse

### Arithmetic

Official Decap computes `m = crepmod3(invntt_scale(basemul_scale(c, f)))`. Official levels 1 (radix-3) and 0 (the
x^N − x^(N/2) + 1 split) are, per coefficient pair:

- level 1: `X+Y+Z` Barrett-reduced; `α⁻¹(X−Y−w(Y−Z))`, `α⁻²(X−Z+w(Y−Z))` Montgomery by the broadcast dword twiddles;
- level 0: `t = mont(A−B, z0)`, `out_a = mont(A+B−t, Ns)`, `out_b = mont(t, 2Ns)` (Ns = `NINV_SCALE`).

The inverse is linear, so the final `·Ns·R⁻¹` scale can be applied at level 1 instead:

- **(C) sigma fold.** σ = Ns·R⁻¹. Every level-1 α⁻¹/α⁻² twiddle word z becomes `cmod_q(z·Ns·R⁻¹)` with its z·qinv
  companion (a new 32-byte `.rodata` table, 2 iterations × 16 bytes), and the level-1 `X+Y+Z` Barrett becomes a
  Montgomery multiply by Ns. All three level-1 outputs are then scaled by σ (σ mod q = −1693 for 864/1152, −811 for
  768).
- **8-op level 0.** `t = mont(A−B, z0); out_a = A+B−t; out_b = t+t`.
- **crep5 fused into level 0**, 5 ops per vector before the stores:
  `k = mulhrs(mulhw(x, 4853), 128)` (= round(x/q)); `y = x − k` (q ≡ 1 mod 3, so y ≡ x − kq mod 3);
  `r = mulhrs(mullw(y, −21845), −1)` (−21845 = 3⁻¹ mod 2¹⁶).
- **(B) split block pass** (864/1152 only): the Official levels-6..3 block loop is split before level 4 into two memory
  passes (L6, L5) and (L4, L3), arithmetic unchanged (the pass is latency-bound). 768 keeps the HT inverse's single
  levels-6..2 block pass.

Levels 6..2 are verbatim (864/1152: Official `invntt.s`; 768: the HT inverse `asm/ntruplus768_officialopt_invntt_ht.s`),
only labels renamed. Registers: ymm0 = q, ymm1/ymm2 = z0 qinv/z0, ymm3..6 = the crep5 constants, ymm7..15 data.

| per call | 768 | 864 | 1152 |
|---|---:|---:|---:|
| dynamic instructions (symexec): fused / Official invntt alone | 2318 / 2465 | 3292 / 3043 | 4311 / 3993 |
| linked size (bytes / rows) | 1747 / 335 | 1843 / 337 | 2131 / 389 |

(The fused count includes the whole crepmod3; the split adds 2 × 6/8 stores + loads per block on 864/1152.)

### Generator and proof

`tools/generate_invntt_crep.py --param N` (`make generate-invshoup`, `check-invshoup-generate`): pinned sha256 of
`upstream/…/invntt.s`, `crepmod3.s`, `consts.c` (768 also the HT inverse asm); every edit is an exact, counted textual
anchor; the level-1 twiddle offsets are read by symbolically executing Official (`rdx` at the level-1/0 loop heads). It
emits the candidate and two proof variants (`pre` = without the crep5 ops, `nosplit` = without the split; build dir
only) and proves symbolically (`symexec.py` through `tools/symexec_ext.py`, which adds `vpslld/vpsrld $16` and
`vpmulhuw` without changing symexec.py):

- candidate == nosplit on all N words (the split is bit-identical for every input; 864/1152);
- candidate == crep5(pre) on all N words;
- the memory at the level-1 entry == Official's (levels 6..2 unchanged).

`tools/prove_invntt_crep.py` (`results/invshoup-phase-a/invcrep-proof.json`) proves candidate(x) ==
Official `crepmod3(invntt_scale(x))` for every Decap input:

1. emulator (`range_proof/avx2emu.py` via `prove_ht.EmuHT`) == machine on `pre` and Official invntt;
2. per-lane interval replay of Official invntt and `pre` on the Decap domain (kem.c's `basemul_scale(c, f)` with
   c, f canonical): 0 signed-word failures, and every multiply is consumed by a Montgomery-by-constant or Barrett
   idiom (an `EmuLin` subclass rejects any product used as an integer). Each such step is exact mod q, so both
   programs are Z_q-linear maps of the input on the domain;
3. basis: `pre(e_i) ≡ Official(e_i) (mod q)` natively for all N unit vectors (plus 2000 random box inputs), hence
   `pre ≡ invntt_scale (mod q)` on the whole domain;
4. crep5 == cmod3(cmod_q(x)) exactly on [−16388, 16391] (exhaustive, instruction semantics) ⊇ pre's range; Official
   crepmod3 (native, all int16) == cmod3(cmod_q(x)) on [−5185, 5185] ⊇ Official invntt's range; cmod3(cmod_q(·))
   depends on x mod q only; native candidate == crep5(native pre) on 2000 inputs.

| | 768 | 864 | 1152 |
|---|---|---|---|
| Decap domain (basemul_scale output) | [−6956, 7640] | [−5231, 5730] | [−6959, 7640] |
| pre-crep range (proved) | [−6055, 6055] | [−6123, 6123] | [−6123, 6123] |
| Official invntt range on the domain | [−1891, 1891] | [−1731, 1731] | [−1731, 1731] |

The fused inverse is **not** a general-input `poly_invntt_scale`: its contract is the Decap domain, and the
`basemul_scale(c, f)` call that produces it stays unchanged.

## 2. Shoup BaseMul

`void ntruplus<N>_officialopt_basemul_shoup(poly *r, const poly *a, const poly *b)`: r = a·b per base in
Z_q[x]/(x^D − ζ) (D = 3 for 864, 4 for 768/1152), **in the canonical scale** (Official `poly_basemul`'s output scale, so
the R² pass disappears); b canonical ([0, q)), a lazy (proven envelope); r must not overlap a or b; all 32-byte aligned.

- companion `b'' = mulhu(16b, 38825)` (38825 = ⌈2²⁷/q⌉, b'' ≈ b·2¹⁵/q);
- each term `lo16(a·b) − lo16(q·mulhrs(a, b''))` = a·b − q·round(a·b''/2¹⁵) exactly (mod 2¹⁶);
- every output word is `Σ lo16(a_i b_j) − lo16(q · Σ mulhrs(a_i, b''_j))` plus the ζ terms with a precomputed
  (ζ, round(ζ·2¹⁵/q)) pair: lo16 parts and quotients are accumulated lazily, one `vpmullw(q)` and one subtract per output;
- ζ = cmod_q(ζR·R⁻¹) from the Official basemul zeta block (`zetas + 1888` bytes for 864/1152, `+1248` for 768; +ζ for
  the first base of each pair, −ζ for the second); `static const` in the source (no runtime init).

Call sites (the signature puts the canonical operand last): Encap `basemul_shoup(&c, &r, &h)`, Decap
`basemul_shoup(&f, &c, &hinv)`.

### Codegen (pinned compiler)

gcc's default schedule spills on the quartic kernel and loses the gain; hand-ordered asm was slower in the scratch
study. The repo therefore commits both the generated intrinsics source `src/ntruplus<N>_officialopt_basemul_shoup.c`
and its compiled `asm/ntruplus<N>_officialopt_basemul_shoup.s`, derived by `tools/generate_basemul_shoup.py`:

- compiler pinned to `gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0`, flags `-O3 -mavx2 -mtune=alderlake -fschedule-insns
  -fsched-pressure -fno-asynchronous-unwind-tables -fcf-protection=none -fno-stack-protector -S`; `--check` refuses any
  other compiler version and requires byte identity of both files;
- post-processing: `.file`/`.ident` dropped, function entry `.p2align 5`, header comment;
- the loop bodies are instruction-for-instruction the scratch-measured `shoup_v2_*.s` (-O3 -march=native
  -fschedule-insns -fsched-pressure; `-mtune=alderlake` is what `-march=native` resolves to here);
- the generator executes the .s symbolically and requires every output word to have the interned form of the reference
  formula (bit-identical for every input).

| per call | 768 | 864 | 1152 |
|---|---:|---:|---:|
| dynamic instructions | 1313 | 1257 | 1961 |
| linked size (bytes / rows) | 614 / 125 | 398 / 84 | 614 / 125 |
| stack slots (constant / data) | 2 / 3 | 1 / 1 | 2 / 3 |

**Stack audit.** gcc spills: `push %rbp; mov %rsp,%rbp; and $-32,%rsp; [sub $40,%rsp]; … leave`, then constant-
displacement `%rsp` slots (red zone / realigned frame). The linked audit (`audit_invshoup_linked.py`) requires exactly
this frame, constant displacements only, no index registers, no scalar memory access, one ret, one `vzeroupper` before
it, one conditional branch (the loop back edge on pointers), no call. So no address or branch depends on data. The data
slots hold secret-derived intermediates (quotient partial sums) and are not cleared on return, like compiler spills in
the C KEM code.

### Range proof

`tools/prove_basemul_shoup.py` (`results/invshoup-phase-a/shoup-proof.json`):

1. symbolic: committed .s == reference formula (all inputs), ζ table re-derived from the pinned Official files; every
   output word depends only on its own base and lane;
2. evaluator == machine on random full-int16 inputs (validates the `vpmulhuw` modelling);
3. exhaustive per-term bounds (`tools/shoup_bounds.c`, instruction semantics) over the caller's whole a envelope ×
   b ∈ [0, q), and every ζ term over the triangle-bounded s range for each (ζ, companion) pair;
4. triangle bounds for every s_k and output word; all true values are int16, so the mod-2¹⁶ accumulation returns the
   exact integer ≡ a·b (mod q);
5. mod q vs Official: native Shoup == `poly_basemul` (mod q) on all D² unit-coefficient patterns (bilinearity + step 1's
   support ⇒ equality on the whole domain) and on 4000 random caller-domain inputs.

Caller envelopes are the HT (= lazy) Forward interval replays (`prove_ht`/`ledger` domains): Encap a = r̂ of the
[−1, 1] domain; Decap a = c − f̂ with f̂ of the [−2, 2] domain and c ∈ [0, q−1].

| | 768 | 864 | 1152 |
|---|---|---|---|
| Encap a envelope / \|term\| / output | ±13636 / ±3140 / ±12560 | ±15580 / ±3344 / ±10032 | ±15580 / ±3344 / ±13376 |
| Encap poly_add(c, m̂) | ±26196 | ±25612 | **±28956** (tightest) |
| Decap a envelope / term / output | [−14449, 17905] / [−3224, 3584] / [−12896, 14336] | [−16385, 19838] / [−3443, 3800] / [−10329, 11400] | [−16385, 19838] / [−3443, 3800] / [−13772, 15200] |

Consumers: Encap `poly_add` stays int16 (above), and `tobytes` (Barrett + canonical freeze) is canonical on every int16.

## 3. Gates (all pass, all three parameters)

| Gate | 768 | 864 | 1152 | Evidence (`results/invshoup-phase-a/`) |
|---|---|---|---|---|
| generators `--check` (pinned inputs, pinned gcc) + every existing generator `--check` | pass | pass | pass | `invcrep-generation.json`, `shoup-generation.json`, `invshoup-kems-generation.json` |
| inverse: symbolic (== crep5(pre); 864/1152 == nosplit), interval, mod-q basis, crep domains | pass | pass | pass | `invcrep-proof.json` |
| Shoup: symbolic, exhaustive per-term + triangle, mod-q basis | pass | pass | pass | `shoup-proof.json` |
| inverse C differential: 5000 real Decap inputs, 100000 box-uniform, 50000 box corners, bit-exact vs Official crepmod3(invntt), canaries, outputs in {−1, 0, 1} | 155000 | 155000 | 155000 | `closure-tests.log` |
| Shoup C differential mod q + tobytes byte-exact: 5000 Encap, 5000 Decap, 40000 adversarial envelope (ends / uniform / b ∈ {0, 1, q−1, (q−1)/2}), outputs in the proven ranges, canaries, inputs unchanged | 50000 | 50000 | 50000 | `closure-tests.log` |
| shared `test_kem_lazy.c`, candidate + 2 controls, release: 100 vectors pk/sk/ct/ss byte-exact vs Official, invalid PK, tampered / noncanonical CT, noncanonical SK, forced g retry, forced f failure | pass | pass | pass | `closure-tests.log` |
| ASan + UBSan + LSan (same binaries) | pass | pass | pass | `closure-tests.log` |
| linked audit (entries, frame/stack rules, rip symbols, KEM call relocations of all 3 variants) | pass | pass | pass | `invshoup-linked-summary.json` |
| mutation check (symbolic AND C differential reject every mutant) | 9/9 | 11/11 | 11/11 | `invshoup-mutation-check.json` |

Linked audit bindings (candidate): the current-best bindings (6 × HT Forward, 2 × fold BaseInv, 2 × nor2, codec, SHAKE)
with Decap `poly_invntt_scale` (768: the HT inverse) and `poly_crepmod3` 1 → 0, `invntt_crep` 0 → 1,
`poly_basemul` 2 → 0, `basemul_shoup` 0 → 2, `poly_basemul_scale` 1 (unchanged). Keygen is unchanged.
Mutants: inverse — σ table word, level-1 Montgomery companion, σ pointer advance dropped, `out_b = 2t → t`, crep5
constant operand, and (864/1152) split reload, split zeta rewind; Shoup — ζ table word, operand row load offset, final
`q·h` multiply dropped, spill-reload slot. A Shoup companion change alone keeps a·b mod q (only the symbolic check sees
it), so it is not used as a differential mutant.

## 4. Same-ELF diagnostic (`supercop-derived`, not Native)

`bench/bench_invshoup_diag.c` + `tools/run_invshoup_diag.py` (`make invshoup-bench`): regions inverse (current best vs
fused), Encap and second-Decap BaseMul (Official vs Shoup on the real operands), keypair (seed-matched) / encap / decap
for Official, base and three variants; 20 blocks × 32 observations; O3GC; cpucycles `default-perfevent`; CPU 1, ASLR on;
31 fresh launches per link order, each batch under `phase_b_batch.py` (all accepted on attempt 0). Pooled StQ2 deltas,
favourable launches of 31, normal / reversed:

| | 768 | 864 | 1152 |
|---|---|---|---|
| inverse: fused − current best | −138.6 (31) / −153.0 (31) | −252.0 (31) / −245.1 (31) | −279.0 (31) / −283.0 (31) |
| (current-best reference) | 1130.5 (HT inverse + crepmod3) | 1369.5 | 1697.6 |
| Encap BaseMul: Shoup − Official | −116.5 (31) / −129.1 (31) | −106.1 (31) / −102.5 (31) | −192.7 (31) / −190.6 (31) |
| Decap BaseMul: Shoup − Official | −116.3 (31) / −127.6 (31) | −108.9 (31) / −103.8 (31) | −189.9 (31) / −190.7 (31) |
| (Official BaseMul reference) | 724.9 | 658.1 | 987.8 |

KEM, variant − base:

| | 768 normal / reversed | 864 normal / reversed | 1152 normal / reversed |
|---|---|---|---|
| encap candidate | −112.6 (31) / −99.2 (31) | −140.0 (31) / −111.6 (31) | −173.8 (31) / −155.0 (31) |
| encap shoup(_only) | −104.3 (31) / −100.9 (31) | −146.1 (31) / −110.5 (31) | −187.9 (31) / −156.1 (31) |
| encap invcrep/invd_only | −5.1 (20) / +12.1 (10) | −7.3 (17) / −2.9 (19) | −11.5 (20) / +0.9 (14) |
| decap candidate | −280.1 (31) / −242.2 (31) | −398.3 (31) / −387.5 (31) | −459.5 (31) / −487.6 (31) |
| decap shoup(_only) | −118.5 (31) / −108.0 (31) | −169.3 (31) / −131.1 (31) | −194.6 (31) / −215.2 (31) |
| decap invcrep/invd_only | −158.5 (31) / −138.1 (31) | −251.9 (31) / −248.3 (31) | −287.4 (31) / −294.4 (31) |
| keypair candidate | +36.0 (6) / −42.3 (28) | +6.1 (15) / −6.0 (21) | +83.3 (10) / +64.5 (11) |

For NTRU+768 the "candidate" row is invcrep_shoup; the 768 fused inverse alone is −158.5 / −138.1 at Decap and
candidate − shoup is −161.6 / −134.2 (0/31 launches favour shoup-only), so the inverse was adopted.

Reading: both components are wins in both link orders for every parameter; Encap moves by about one Shoup call, Decap
by one Shoup call + one fused inverse (roughly additive). Keypair runs no changed code: its ±40 (768/864) and the 1152
+65..+83 at 10–11/31 (BaseInv retry mixture) are placement noise.

## 5. Phase B

Everything ran on CPU 1 of the Core Ultra 7 155H, ASLR on (`randomize_va_space=2`), host controls only read
(`performance`, `no_turbo=1`); every batch under `phase_b_batch.py`, strictly sequential, one parameter at a time
(864, then 1152, then 768), nothing built or tested while timing ran. Campaign
`/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001`. Tag `20260925is`.

### Qualification exports

`tools/export_invshoup_flat.py` (`make invshoup-qualification`; `invshoup-qualification-check` regenerates into a temp
dir and requires identity): kind `invshoup-qualification-source`; from the HT export (lock, manifest, tree and per-file
hashes checked): every file kept except `kem.c`; added `invntt_crep.s` and `basemul_shoup.s` with the exact Phase-A bytes
(sha256 == the Phase-A generation records; the Shoup C source is recorded in the manifest, not exported, since SUPERCOP
compiles every .c/.s); `kem.c` = the HT export `kem.c` with its verbatim `src/kem_lazy_r2fold.c` body replaced by the
verbatim `src/kem_lazy_r2fold_invcrep_shoup.c` (the Phase-A chain is checked to be the current-best chain with only the
`#include` lines rebound). `kem.c` diff vs the base export: +2 prototypes, 4 call-site lines (Encap BaseMul, Decap
inverse pair → 1 line, Decap BaseMul) and a 7-line comment (12 added / 4 removed). NTRU+768 also drops the HT-inverse
overlay head (a `#define` that is dead once the Decap inverse call is gone) and the then unreferenced `invntt_ht.s`
(12 added / 11 removed).

**The flat tree is what Phase A tested** (`make invshoup-flat-record` → `results/invshoup-phase-b/`): flat KEM test
(every export file compiled from the export dir, `kem.c` renamed, against pinned Official `kem.c`; release and
ASan+UBSan+LSan); flat linked audit (entries == the export's `.s` assembled alone; flat `kem.o` bindings); object identity
of flat `kem.o`, `baseinv_r2fold.o`, `symmetric.o`, `mlk_fips202.o`, `mlk_keccakf1600.o` with the Phase-A objects up to
the file symbol and the repo-only hash names; do-part try emulation (`tools/try_invshoup_flat.py`, around
`export_keccak_flat.try_tree()`) of the installed export and its reversed copy: 0 warnings, pinned checksums for
O3/Os/O2/O (`flat-supercop-try.json`).

Installed with `install_qualification.py`; reversed copies with `install_reversed_placement.py` (new rename
`basemul_shoup.s` → `zzz_basemul_shoup.s`, next to `zzz_basemul.s`; `invntt_crep.s` stays, like `invntt.s`).
**SUPERCOP try: ok** in all 27 Native batches per parameter (O3/Os/O2/O) and in the 5 O3GC fixed builds, checksums ==
pinned Official.

### Design

- Native: roles official (`avx2`), base (the HT export), cand; 81 fresh launches each (`run_extended_native.py --batches 9
  --order rotate`), default compiler selection, unmodified `measure.c`; CIs by launch resampling (2,000).
- Compiler picks: base and cand O3 in 9/9 batches for every parameter; Official 768 O2 8 / O3 1, 864 O3 6 / O2 3, 1152 O3 9.
  Base and cand always got the same compiler, so no fixed `-O3` check was needed.
- Paired: O3GC fixed ELFs (`okc-o3gc.sh`), `run_paired_aslr_on.py`, 48 ABBA/BAAB blocks per run: cand vs base normal
  (primary), cand vs base reversed (secondary), cand vs Official normal. The base fixed ELFs are byte-identical to the
  HT Phase-B cand ELFs (864 `51eff93a…`, 1152 `6ca2c90b…`); cand normal 768 `ae880b8b…`, 864 `60bfe0d1…`, 1152 `3e5db89b…`.
- Hygiene: 35 batches per parameter; 864: two Native base batches (b2, b6) rejected once for pre-batch load 0.53/0.54 >
  0.5 and accepted on the rerun; 1152 and 768: all on attempt 0.

### Native, default compiler selection (81 launches per role; pooled StQ2)

| n | Op | Official | Base | Cand | Cand − Base [95% CI] fav./81 | Cand − Official [95% CI] fav./81 |
|---|---|---:|---:|---:|---:|---:|
| 768 | Keypair | 21,607.3 | 16,598.7 | 16,592.4 | −6.3 (−0.04%) [−21.4, +8.8] 45/81 | −5,014.9 (−23.2%) [−5,033.1, −4,999.2] 81/81 |
| 768 | Encap | 28,182.5 | 20,451.5 | 20,359.8 | **−91.7** (−0.45%) [−108.9, −72.7] 71/81 | −7,822.6 (−27.8%) [−7,866.8, −7,784.4] 81/81 |
| 768 | Decap | 19,456.1 | 14,955.6 | 14,725.0 | **−230.6** (−1.54%) [−242.3, −218.3] 81/81 | −4,731.1 (−24.3%) [−4,749.2, −4,714.4] 81/81 |
| 864 | Keypair | 23,749.1 | 17,601.9 | 17,621.6 | +19.7 (+0.11%) [+3.9, +34.7] 27/81 | −6,127.5 (−25.8%) [−6,143.1, −6,110.9] 81/81 |
| 864 | Encap | 32,940.4 | 23,304.1 | 23,172.8 | **−131.3** (−0.56%) [−149.2, −113.2] 77/81 | −9,767.6 (−29.7%) [−9,806.2, −9,734.2] 81/81 |
| 864 | Decap | 23,674.9 | 17,314.9 | 16,889.8 | **−425.2** (−2.46%) [−437.5, −413.6] 81/81 | −6,785.1 (−28.7%) [−6,808.1, −6,764.1] 81/81 |
| 1152 | Keypair | 34,624.2 | 26,740.2 | 26,732.2 | −8.0 (−0.03%) [−289.8, +271.1] 39/81 | −7,891.9 (−22.8%) [−8,217.7, −7,560.3] 81/81 |
| 1152 | Encap | 43,116.9 | 31,074.8 | 30,958.0 | **−116.8** (−0.38%) [−149.7, −86.1] 73/81 | −12,158.9 (−28.2%) [−12,189.7, −12,131.4] 81/81 |
| 1152 | Decap | 30,550.4 | 23,349.3 | 22,973.3 | **−376.0** (−1.61%) [−393.8, −359.9] 81/81 | −7,577.0 (−24.8%) [−7,591.4, −7,563.8] 81/81 |

"fav." counts candidate launches below the baseline's median launch. Per-batch cand − base (9 batches): 768 encap −38 …
−115 (SD 24), decap −180 … −256 (SD 23), keypair −29 … +12 (SD 14); 864 encap −83 …
−170 (SD 30), decap −396 … −455 (SD 17), keypair −21 … +65 (SD 28, 3/9 negative); 1152 encap −57 … −203 (SD 45), decap
−331 … −428 (SD 35), keypair −725 … +533 (SD 412, 4/9 negative).

### Fixed-ELF paired, O3GC, ASLR on, 48 blocks (mean [block-bootstrap 95% CI] favourable/48)

| n | Op | Cand vs Base, normal (primary) | Cand vs Base, reversed (secondary) | Cand vs Official, normal |
|---|---|---:|---:|---:|
| 768 | Keypair | +50.2 [+39.5, +61.3] 5/48 | +33.8 [+19.5, +49.7] 11/48 | −5,031.1 [−5,047.4, −5,015.1] 48/48 |
| 768 | Encap | **−118.6** [−146.7, −76.8] 46/48 | −169.2 [−179.9, −158.6] 48/48 | −7,801.5 [−7,824.2, −7,777.7] 48/48 |
| 768 | Decap | **−303.2** [−315.2, −292.0] 48/48 | −324.6 [−334.7, −314.4] 48/48 | −4,753.3 [−4,771.4, −4,735.5] 48/48 |
| 864 | Keypair | −7.2 [−17.8, +3.3] 25/48 | +42.1 [+30.8, +53.1] 6/48 | −6,288.7 [−6,298.4, −6,279.3] 48/48 |
| 864 | Encap | **−126.3** [−138.1, −114.6] 48/48 | −89.6 [−104.9, −73.9] 45/48 | −9,660.8 [−9,693.3, −9,631.9] 48/48 |
| 864 | Decap | **−391.4** [−400.5, −382.6] 48/48 | −328.7 [−342.8, −313.5] 48/48 | −6,908.0 [−6,925.4, −6,891.4] 48/48 |
| 1152 | Keypair | −178.9 [−392.8, +33.9] 28/48 | +116.6 [−128.0, +357.4] 23/48 | −7,802.5 [−8,071.1, −7,521.3] 48/48 |
| 1152 | Encap | **−147.6** [−162.1, −133.0] 48/48 | −83.4 [−106.4, −60.4] 39/48 | −12,074.3 [−12,121.3, −12,033.1] 48/48 |
| 1152 | Decap | **−396.1** [−408.5, −383.4] 48/48 | −419.0 [−436.1, −403.7] 48/48 | −7,472.1 [−7,510.3, −7,440.9] 48/48 |

### Decision (rule: Native default-selection pooled cand − base < 0 AND normal-placement ASLR-on paired 95% CI < 0)

| n | Op | Native cand − base | Paired normal | Paired reversed | Verdict |
|---|---|---|---|---|---|
| 768 | Keypair | −6.3 [−21.4, +8.8] | [+39.5, +61.3] | [+19.5, +49.7] | not a win: no keygen code changed; placement (flagged: both paired CIs above zero, +50 / +34) |
| 768 | Encap | −91.7 [−108.9, −72.7] | [−146.7, −76.8] | [−179.9, −158.6] | **robust research win** |
| 768 | Decap | −230.6 [−242.3, −218.3] | [−315.2, −292.0] | [−334.7, −314.4] | **robust research win** |
| 864 | Keypair | +19.7 [+3.9, +34.7] | [−17.8, +3.3] | [+30.8, +53.1] | not a win: no keygen code changed; placement (flagged: the Native CI and reversed paired CI lie above zero, +20 / +42) |
| 864 | Encap | −131.3 [−149.2, −113.2] | [−138.1, −114.6] | [−104.9, −73.9] | **robust research win** |
| 864 | Decap | −425.2 [−437.5, −413.6] | [−400.5, −382.6] | [−342.8, −313.5] | **robust research win** |
| 1152 | Keypair | −8.0 [−289.8, +271.1] | [−392.8, +33.9] | [−128.0, +357.4] | not a win: no keygen code changed; BaseInv retry mixture + placement |
| 1152 | Encap | −116.8 [−149.7, −86.1] | [−162.1, −133.0] | [−106.4, −60.4] | **robust research win** |
| 1152 | Decap | −376.0 [−393.8, −359.9] | [−408.5, −383.4] | [−436.1, −403.7] | **robust research win** |

Against Official the rule gives a robust research win for every (n, op), keypair included (the current best's gains).

Per op: **Inverse D (fused inverse)** — a Decap-only change; robust Decap wins on all parameters (component −139 / −252 /
−279, Decap KEM −138..−294 in the controls); **Shoup** — Encap and Decap; robust Encap wins on all parameters (Encap moves
only by Shoup) and part of the Decap win. Keypair is not claimed.

Reading:

- Native agrees with the same-ELF diagnostic and the normal paired runs within ~10–15% for Encap/Decap; the reversed
  placement shrinks the Encap gain (864 −90, 1152 −83) but keeps every Encap/Decap CI below zero.
- **Keypair placement effect (768, 864).** The keygen path is byte-identical source, but kem.o changes size. 864: the
  Native +19.7 and reversed paired +42.1 CIs sit above zero while the normal paired CI straddles zero; 768: Native −6.3
  straddles zero while both paired CIs sit above zero (+50.2 / +33.8). This is a code-placement effect of the same kind
  as the 768 HT encap reversed +24; it is reported, not claimed or hidden.
- **768 Decap Native (−231) is below its paired value (−303)**; same compiler (O3) for base and cand, so this is the
  usual Native-vs-fixed-ELF placement spread; every CI is below zero.

## 6. The NTRU+768 inverse (task 3)

The 768 current best's inverse is the HT inverse: a levels-6..2 block pass that fuses the radix-2 level 2, followed by the
**Official levels 1 (radix-3) and 0 verbatim**. crep5 and the sigma fold therefore apply exactly as on 864/1152, to those
verbatim levels (the level-1 radix-3 X+Y+Z / α twiddles and the level-0 split are the same code shape with the 768
offsets, `1152(%rdx)` instead of `1728(%rdx)`, σ mod q = −811); only the split (B) does not apply (the HT block pass
already is a single pass with fewer shuffles). `generate_invntt_crep.py --param 768` takes the pinned HT inverse as the
source of levels 6..2 (renaming its tables to `…_invcrep_…`). All gates pass (§3; its proof is the same basis argument,
against Official `poly_invntt_scale`, which the HT inverse equals bit for bit), and it is a component win in both link
orders (−139 / −153 vs HT inverse + crepmod3, 31/31) and adds −162 / −134 at Decap on top of Shoup (31/31). It is
therefore **in the 768 candidate** (`…-ht-invc-shoup-qual001`); Phase B (§5): Decap −230.6 Native, −303.2 paired normal, a robust research win. The Native run cannot separate the inverse from Shoup at Decap; that split rests on the same-ELF controls (§4).

## Reproduce

```sh
REPO=/home/nuc/src/ntru_plus-official-opt-864-1152
A=$REPO/ntruplus-ntt-Optimized/Additional_Implementation/avx2; T=$A/common/official_opt_lazy/tools; I=$A/common/official_opt_invshoup/tools
C=/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001; TAG=20260925is
# per parameter p (E = the experiment dir, B = the HT export, X = the new export):
#   768:  E=$A/NTRU+768/experiments/avx2_official_opt_freeze_001 B=avx2-officialopt-lazy-freeze-keccak-ht-qual001
#         X=avx2-officialopt-lazy-freeze-keccak-ht-invc-shoup-qual001
#   864:  E=$A/NTRU+864/experiments/avx2_official_opt_001 B=avx2-officialopt-lazy-codec-keccak-ht-qual001
#         X=avx2-officialopt-lazy-codec-keccak-ht-invd-shoup-qual001
#   1152: E=$A/NTRU+1152/experiments/avx2_official_opt_001 B=avx2-officialopt-lazy-freeze-keccak-ht-qual001
#         X=avx2-officialopt-lazy-freeze-keccak-ht-invd-shoup-qual001
(cd $E && make generate-invshoup)      # regenerate asm/src (writes; needs the pinned gcc for the Shoup .s)
(cd $E && make invshoup-record)        # Phase A -> results/invshoup-phase-a/
(cd $E && make invshoup-bench)
for o in normal reversed; do b=build/bench_invshoup_diag; [ $o = reversed ] && b=${b}_swapped
  (cd $E && python3 $T/phase_b_batch.py --result-dir results/invshoup-diag-$o-20260925 --metadata metadata.json -- \
    python3 $I/run_invshoup_diag.py --param $p --experiment . --launches 31 --binary $b --result-dir {RESULT}); done
(cd $E && make invshoup-qualification-check && make invshoup-flat-record)   # export committed; invshoup-qualification recreates it
python3 $T/install_qualification.py --param $p --campaign-root $C --export-root $E/qualification/$X
python3 $T/install_reversed_placement.py --param $p --campaign-root $C --baseline $B --candidate $X --skip-baseline
python3 $I/try_invshoup_flat.py --param $p --campaign-root $C --tree $X --tree $X-reversed \
  --output $E/results/invshoup-phase-b/flat-supercop-try.json
python3 $T/run_extended_native.py --param $p --experiment $E --campaign-root $C --tag $TAG --batches 9 --order rotate \
  --role official=avx2 --role base=$B --role cand=$X
# fixed O3GC builds (roles official/base/cand normal, base/cand reversed) and the three paired runs exactly as in
# ntruplus864-1152-ht.md#reproduce with fixed-is-<role>-<placement>-$TAG and pair names cand-vs-base / cand-vs-official, then
python3 $T/summarize_extended_multi.py --param $p --experiment $E --tag $TAG --order rotate --roles official,base,cand \
  --comparison cand:base --comparison cand:official --comparison base:official \
  --paired cand:base=cand-vs-base-$TAG --paired cand:official=cand-vs-official-$TAG
```

Curated evidence per experiment: `results/invshoup-phase-a/`, `results/invshoup-phase-b/`,
`results/invshoup-diag-{normal,reversed}-20260925/`, `results/native-ext-{official,base,cand}-b{1..9}-20260925is/`,
`results/fixed-is-*-20260925is/`, `results/paired-aslr-on-*-20260925is/`, `results/extended-multi-summary-20260925is.json`.
Raw launch output, `data`, `run.out`, `measure` ELFs and `host-hygiene.json` stay local (Git-ignored).

## Tool changes and regression proof

- New `common/official_opt_invshoup/` (own `invshoup.mk`, every variable/target prefixed `IS_`/`invshoup-`), included
  last by the three experiment Makefiles. `make -n -B` of `check phase-a record sanitize audit range-proof keccak-phase-a
  keccak-record keccak-bench ht-phase-a ht-record ht-bench ht-flat ht-flat-record ht-qualification-check generate-ht
  generate generate-keccak bench bench-keypair [ht-bench-keypair]` is byte-identical before and after for all three.
- Every existing generator `--check` ran inside `check-invshoup-generate` (via `check-ht-generate`) and passed; no
  committed file outside the new paths changed except the two install tools below and the three Makefiles.
- `symexec_ext.py` extends `symexec.py` by subclassing; `symexec.py`, `avx2emu.py`, `prove_ht.py`, `audit_ht_linked.py`
  and the HT/keccak exporters are imported unchanged (the hashed exporters are not edited).
- `install_qualification.py`: accepts the new kind `invshoup-qualification-source` (tuple extension only).
- `install_reversed_placement.py`: `basemul_shoup.s` → `zzz_basemul_shoup.s` when present. Proof: the old (HEAD) and new
  tool were run on fresh copies of all 11 existing qualification exports and the three `avx2` baselines; the 14 reversed
  trees (incl. `PLACEMENT.json`) are identical (`diff -r` empty).

## Deviations and notes

- **768 candidate includes the fused inverse** (task 3 outcome), so its export is `…-ht-invc-shoup-qual001` (not
  `…-ht-shoup-qual001`); the shoup-only variant stays a control, and `IS_QUAL_VARIANT=shoup` can still export it.
- **Optional 1152 variant F** (sigma fold + HT block split, needs the 4.6 KB HT table): not implemented (not cheap).
- **Keypair** is not claimed for any parameter (no keygen code change); 864's small positive keypair Native/reversed
  CIs are a placement effect and are flagged.
- The diagnostic's "keypair" region includes the KAT-DRBG reseed, so its absolute values (~60–95k) are not SUPERCOP
  keypair cycles; only deltas are used.
- 864 hygiene: two Native batches rerun once for a 0.53/0.54 pre-batch load (my own wait loops were polling during that
  run; they were removed for the later parameters).
- Stack spills of the gcc-compiled Shoup kernel are allowed and audited (§2); the data slots are not cleared.
- Test-only renames in the flat KEM test (Official `hash_f/g/h` renamed so both copies link), as for HT; the flat side
  is compiled without `-DSUPERCOP`, whose path is covered by `try`.

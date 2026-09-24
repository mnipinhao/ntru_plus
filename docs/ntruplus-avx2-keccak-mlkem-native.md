# NTRU+768 / 864 / 1152 Official AVX2: mlkem-native x1 C Keccak for every SHAKE256

Date 2026-09-23, branch `official-opt-lazy-864-1152` (from `335daed` = `origin/avx2-official-opt`, not pushed).
Phase A (code, correctness, audits) plus a same-ELF diagnostic were done on 2026-09-23. Phase B
(qualification exports, Native SUPERCOP and ASLR-on fixed-ELF paired timing) followed on 2026-09-24; see
[Phase B](#phase-b-native-supercop-2026-09-24). Result: a robust research win for every operation of all three
parameters, vs Official and vs the base candidate. `promotion: none`.

Motivation: Codex's component comparison `NTRU+768/experiments/avx2_keccak_compare_001` (in the
`ntru_plus-official-opt` worktree; read, not reused as evidence) found that mlkem-native's x1 *C*
Keccak (commit `b3ba7b32`) beats the pinned XKCP/CRYPTOGAMS `KeccakP-1600-AVX2.s` at the permutation
and at the three NTRU+768 SHAKE256 shapes. This change moves every SHAKE256 call of the KEM onto that
code, stacked on each parameter's current best Official-opt candidate.

| | NTRU+768 | NTRU+864 | NTRU+1152 |
|---|---|---|---|
| Experiment (`STATUS.yml` section `keccak_candidate:`) | `NTRU+768/experiments/avx2_official_opt_freeze_001` | `NTRU+864/experiments/avx2_official_opt_001` | `NTRU+1152/experiments/avx2_official_opt_001` |
| Base candidate (unchanged) | `avx2-officialopt-lazy-freeze-768-exp001` | `avx2-officialopt-lazy-codec-864-exp002` | `avx2-officialopt-lazy-freeze-1152-exp001` |
| New candidate | `avx2-officialopt-lazy-freeze-keccak-768-exp001` | `avx2-officialopt-lazy-codec-keccak-864-exp001` | `avx2-officialopt-lazy-freeze-keccak-1152-exp001` |
| Candidate KEM overlay | `src/kem_lazy_freeze2op_keccak.c` | `src/kem_lazy_codec_direct_keccak.c` | `src/kem_lazy_freeze2op_keccak.c` |
| Control | keccak-only `src/kem_keccak.c` (pinned Official `kem.c` + new Keccak) | same | same |

Experiment paths are under `ntruplus-ntt-Optimized/Additional_Implementation/avx2/`. The shared code
is `common/official_opt_keccak/` (`keccak.mk` is included last by each experiment `Makefile`).
Nothing under Codex's `NTRU+768/experiments/avx2_official_opt_001/` or in the `ntru_plus-official-opt`
worktree was written; no SUPERCOP tree was modified.

## Vendored code and license

`third_party/mlkem-native-fips202-b3ba7b32/` holds 11 files copied unchanged from
<https://github.com/pq-code-package/mlkem-native> at `b3ba7b32773e657dd37f6f87bce82528459ad8a4`
(clone verified with `git rev-parse HEAD`; clean tree):
`mlkem/src/fips202/{fips202.c,fips202.h,keccakf1600.c,keccakf1600.h}`,
`mlkem/src/{common.h,sys.h,cbmc.h,params.h,context.h,verify.h}` and `LICENSE`.
Its `README.md` records the URL, commit, the per-file SHA-256 and the config macros.
`tools/check_keccak_config_equivalence.py` re-verifies those files byte for byte against a clean checkout.

License: every vendored source file carries `SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT`
(copyright "The mlkem-native project authors"). Upstream `LICENSE` reproduces all three texts and
states that `mlkem/*` is available under the user's choice of them. The FIPS202 code derives from
the CC0 mupq code, the public-domain SUPERCOP `keccakc512/simple` and tweetfips202.

No x4 assembly or native backend is vendored. `keccakf1600.c` still contains mlkem-native's x4 *C*
fallback functions; they are unused and cannot be removed without editing the file.

Configuration, `common/official_opt_keccak/config/mlkem_native_config.h`, is picked up by
`common.h` as `"mlkem_native_config.h"`, with no `-D` flag:

- `MLK_CONFIG_PARAMETER_SET 768`: required by `params.h`. The FIPS202 code ignores it, so all three NTRU+
  parameters use it.
- `MLK_CONFIG_NAMESPACE_PREFIX ntruplus_mlkfips202`: all symbols become `ntruplus_mlkfips202_*`.
- `MLK_CONFIG_USE_NATIVE_BACKEND_FIPS202` is **not** defined. Codex's build defined it, but mlkem-native's
  x86_64 FIPS202 backend is x4-only, so the x1 permutation is the C `mlk_keccakf1600_permute_c`
  in both configurations. `keccak-config-equivalence.json` shows the x1 instruction streams
  (`shake256`, `absorb_once`, `xor_bytes`, `extract_bytes`, and the 470-instruction permutation body)
  are equal after removing padding. The only difference is that here `mlk_keccakf1600_permute`
  is `endbr64; jmp mlk_keccakf1600_permute_c`, because the body is shared with the unused x4 C fallback,
  while Codex's build inlines it.

## Adapter

The pinned Official `kem.c` and `symmetric.c` (identical for all three parameters, sha256 `368bb8f7…` and `49e7faa9…`)
reach SHAKE256 only through the one-shot `shake256(out, outlen, in, inlen)` of `fips202.h`. There are
8 call sites: 2 direct ones (keypair `genf`/`geng`, `32 -> N/4`) and 2 each of `hash_f`, `hash_g` and `hash_h`.
The Official incremental API (`shake256_init/absorb/finalize/squeeze`) is unused, and so is SHAKE128/SHA3.

- `src/fips202_mlkem.h` is a drop-in `fips202.h`. It claims the Official include guard `FIPS202_H`,
  includes mlkem-native's `fips202.h`, and defines `shake256` as `mlk_shake256`, which becomes
  `ntruplus_mlkfips202_shake256`.
- `src/symmetric_keccak.c` is the pinned Official `symmetric.c`, unmodified, compiled against that header.
  `keccak_names.h` renames its functions `hash_{f,g,h}` to `ntruplus{N}_keccak_hash_{f,g,h}` so that
  Official and candidate coexist in one ELF. Prefix bytes (0x00/0x01/0x02), the stack copy, the
  `secure_clear` of `hash_g`/`hash_h` (none in `hash_f`) and all lengths are therefore exactly the
  Official ones.
  mlk_shake256 forbids overlapping input and output. That holds because every wrapper hashes its stack
  copy (`hash_g(ct, ct)` in enc) and keypair hashes a separate `coins` buffer.
- The KEM overlays (`tools/generate_keccak_overlays.py`, `--check`) are 4-line preprocessor
  overlays: `util.h`, `fips202_mlkem.h`, `keccak_names.h`, then `#include` of the unchanged base source.
  The generator pins the sha256 of `kem.c`, `symmetric.c/.h`, `fips202.c/.h` and `util.h`. It asserts that the Official
  `fips202.h` guard and binding are as expected, and that the include chain has exactly 2 `shake256` calls and
  2/2/2 `hash_*` calls and no other SHAKE/SHA3/Keccak identifier.
- Include hygiene: mlkem-native headers are reachable only as `mlkem/src/...`, so its `params.h`
  cannot shadow NTRU+'s.
- `common/official_opt_lazy/tests/test_kem_lazy.c` gained an optional `CANDIDATE_SHAKE256` hook.
  It wraps the candidate's SHAKE symbol with the same forced-g injection. Existing builds are unchanged,
  and every existing gate (`make check freeze-check`, `make check codec-check direct-check`) was re-run and passes.

## Gates (all pass for 768, 864 and 1152)

Run with `make keccak-record MLK_ROOT=<clean checkout>` (= `keccak-phase-a` + config equivalence).
Evidence is in `<experiment>/results/keccak-phase-a/`.

| Gate | Result | Evidence |
|---|---|---|
| Generators | new overlays `--check`; base generators unchanged (`check-generate` + `check-freeze-generate` / `check-codec-generate check-codec-direct-generate`); `check-upstream` | `keccak-generation.json` |
| SHAKE256 differential (`tests/test_shake256_keccak.c`) | Official `fips202avx_shake256` vs candidate, byte-exact: every inlen 0..700 × 41 outlens (0, 1, rate ±1 multiples, N/4, 32+N/4, …, 600); every outlen 0..600 × 20 inlens (incl. 1153/1297/1729); inlen k·136+{−2..+2} up to 1770; 200 random up to 6000/1200 B; random misalignment, canaries on both sides, input unchanged: 43 626 cases | `closure-tests.log` |
| | x1 permutation: zero-state KAT (lane0 `F1258F7940E1DDE7`) + 4000 random states × 3 chained = 12 001 | |
| | NTRU+ shapes: 768 `32→192, 1153→32, 1153→192, 129→224`; 864 `32→216, 1297→32, 1297→216, 141→248`; 1152 `32→288, 1729→32, 1729→288, 177→320` × 3000 at the SHAKE level + Official vs candidate `hash_f/g/h`, in-place `hash_g`, domain bytes: 33 000 (76 626 SHAKE-level cases in total) | |
| | NIST CAVP SHAKE256 subset, 76/76 vectors through both implementations (`tests/vectors/shake256_cavp_subset.txt`; provenance header; `tools/extract_shake256_vectors.py --check` re-derives it from the zip, sha256 `debfebc3…`; also cross-checked with Python `hashlib.shake_256`) | |
| KEM (`test_kem_lazy.c`) | candidate and keccak-only vs Official: 100 deterministic vectors pk/sk/ct/ss byte-exact, invalid PK, flipped CT, noncanonical CT/SK, forced g retry (3 draws), forced f retry (+natural f/g counts; 1152: 85 natural retries, f=40 g=45) | `closure-tests.log` |
| ASan/UBSan/LSan | all 5 binaries, `detect_leaks=1`, `halt_on_error` | `closure-tests.log` |
| Mutation | 8/8 one-line mutants rejected (SHAKE domain 0x1F, pad merge 0x80, squeeze length, round constant, ρ offset, χ, `hash_g` domain byte, `hash_h` length); unmutated control passes | `keccak-mutation-check.json` |
| Linked audit | KEM closure (51 functions, address-keyed call graph of the linked ELF) from the candidate / keccak-only entries reaches no `KeccakP1600_*`, `KeccakF1600_*`, `fips202avx_*` or Official `hash_*`, and has no indirect call; Official role still reaches `KeccakP1600_Permute_24rounds`; KEM objects: relocations 2/2/2 to `ntruplus{N}_keccak_hash_*`, 2 to `ntruplus_mlkfips202_shake256`, 0 to Official | `keccak-linked-summary.json` |
| libc on the new path | mlk path: only `__stack_chk_fail` (distro `-fstack-protector-strong`; zeroize is an inlined memset + asm barrier). Wrappers add `memcpy` and `__explicit_bzero_chk`: these are the Official `symmetric.c`/`util.h` code kept verbatim | same |
| Stack (`-fstack-usage`, all frames `static`) | worst depth hash_f/hash_g/hash_h: 768 1784/1784/760 B, 864 1928/1928/776, 1152 2360/2360/808; mlk_shake256 576 (320 own + absorb 64 + permute_c 160 + returns). Official C part without its asm leaves: 1528/1528/504 (768) | same |
| Constant time | see below | `keccak-ct-summary.json` |
| Config/provenance | vendored == clean checkout; README sha256 table matches; x1 streams equal to the native-backend build (above) | `keccak-config-equivalence.json` |

### Constant-time review

mlkem-native's own claim at this commit (README "Security", `SOUNDNESS.md` A2): the C code is
CBMC-proved memory- and type-safe. Constant-time is formally proved only for its assembly, which is not used here.
For C it is tested with valgrind across compilers and flags, and value barriers are used against compiler-introduced leaks.

Our review of the compiled x1 path (release CFLAGS, GCC 15.2):

- **Static** (`tools/audit_keccak_ct.py`, objdump of the linked candidate ELF), identical for all three parameters:
  - There are 43 conditional branches over the 9 path functions. The 470-instruction `mlk_keccakf1600_permute_c` has exactly one, the round-loop counter, and no indexed memory access.
  - `absorb_once` has 4 branches (`mlen` vs rate, `mlen == 0`, and the last-byte test `mlen == r-1`, all on the public length).
  - `shake256` has 3 (the `outlen` loop, plus the stack-protector check) and one `cmovbe` (`len = min(outlen, r)`).
  - `xor_bytes`/`extract_bytes` have 16 each: the length, the offset, and the pointer-alignment peeling of the vectorised byte loop. Their indexed operands are `base + loop counter`.
  - The three wrappers have only the stack-protector check.
  - There are no variable-latency instructions (div/idiv/bsf/bsr/tzcnt/lzcnt/popcnt).
- **Dynamic** (`tests/ct_trace.c`): the same objects are linked into a `ptrace` single-stepper (`-no-pie -z now`, one untraced warm-up call).
  Each target runs on 12 secret inputs with fixed public lengths and pointers: all-zero, all-0xff, and 10 pseudo-random.
  The targets are SHAKE `32→N/4`, SHAKE `(1+POLYBYTES)→N/4`, `hash_f`, `hash_g`, `hash_h` and one permutation.
  For every executed instruction the tracer records rip and the effective address of its explicit memory operand.
  glibc memcpy/explicit_bzero record rip only.
  For every target all 12 traces are byte-identical: 768 `hash_g` 46 026 steps with 15 462 addresses checked, 1152 `hash_g` 68 828 / 23 176.
  A negative control (secret-indexed table load) does produce differing traces.

This is evidence for this compiler and these flags, not a proof. Other compilers or flags are not covered.
The SUPERCOP flat build below compiles with `-Os/-O2/-O` as well, but those builds were not traced.

## SUPERCOP-flat feasibility

`tools/export_keccak_flat.py` (`make keccak-flat FLAT_OUT=<scratch>`) builds one implementation
directory per parameter from the base qualification tree. For 768 and 1152 that is `qualification/avx2-officialopt-lazy-freeze-qual001`;
for 864 it is `qualification/avx2-officialopt-lazy-codec-qual002`. The steps:

- drop `fips202.c`, `fips202.h`, `KeccakP-1600-AVX2.s` and `KeccakP-1600-SnP.h`;
- install `fips202_mlkem.h` as `fips202.h`;
- copy the vendored files flat as `mlk_*.{c,h}`. The flat names avoid the `params.h`/`fips202.h` collisions. The only edits are `#include` lines, and every rewrite is recorded;
- add the local `mlkem_native_config.h` and `LICENSE.mlkem-native`.

`kem.c`, `symmetric.c` and all other base files keep their sha256.

The tool then emulates `do-part` in scratch. It generates `crypto_kem.h` and `crypto_kem_ntruplus{N}.h` from `MACROS`, `PROTOTYPES.c` and `api.h`.
Every `.c`/`.s` file is compiled with every `okc-amd64` line of the (read-only) campaign `supercop-campaign-lazy-864-1152-20260923-001`:
`gcc -march=native -mtune=native -O3|-Os|-O2|-O -fwrapv -fPIC -fPIE -gdwarf-4 -Wall`, with exactly `do-part`'s `-DSUPERCOP -DCRYPTO_NAMESPACE…` flags and include dirs (`constbranchindex`).
It links `try-small` and `try` with `knownrandombytes.o` and the campaign libs, runs them, and compares the checksums with the pinned `crypto_kem/ntruplus{N}/checksum{small,big}`.

Result (`<experiment>/results/keccak-supercop-flat-20260923/summary.json`): for all three parameters
and all four compiler lines, the flat candidate compiles standalone with **0 warnings** and no external `-D` flag,
and `try-small`/`try` reproduce the pinned checksums. The same holds for the unmodified base tree and the Official `avx2` tree.
The library's mlk globals are `ntruplus_mlkfips202_*`, with default visibility and not SUPERCOP-namespaced, just like Official's `KeccakP1600_*`.
Nothing was installed into a campaign.

## Same-ELF diagnostic (supercop-derived, not Native)

`common/official_opt_keccak/bench/bench_keccak_diag.c` (`make keccak-bench`) links these into one ELF per parameter:

- Official, base, base+keccak and keccak-only KEM translation units;
- Official, mlkem-native `-O3` and a second mlkem-native copy built at `-O2` (other namespace), for the hash wrappers and the x1 permutation.

The common O3GC recipe and cpucycles `default-perfevent` come from the campaign (read only).
The `_swapped` ELF links everything in reverse order.

Runs used `tools/run_keccak_diag.py` under the hygiene wrapper `phase_b_batch.py`: CPU 1, performance governor, turbo off, ASLR on, **31 fresh launches per link order**.
Each launch has 12 rotated blocks × 32 observations per variant, and keypair observations reseed the KAT DRBG (seed-matched retry composition).
All 6 batches were accepted on attempt 0, uncontaminated.
Cells below are the pooled StQ2 delta in cycles, with favourable launches out of 31 in brackets, normal / reversed.
Tables: `results/keccak-mlkem-native-20260923/diag-tables.md`; JSON:
`results/keccak-mlkem-native-20260923/diag-summary.json`; per experiment:
`results/keccak-diag-{normal,reversed}-20260923/{summary,metadata}.json`.

| Region | Delta | 768 normal | 768 reversed | 864 normal | 864 reversed | 1152 normal | 1152 reversed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| permute | mlkem_o3 − Official | −169 (31) | −154 (31) | −169 (31) | −152 (31) | −165 (31) | −163 (31) |
| hash_f | mlkem_o3 − Official | −1890 (31) | −1895 (31) | −2123 (31) | −2130 (31) | −2773 (31) | −2747 (31) |
| hash_g | mlkem_o3 − Official | −2125 (31) | −2115 (31) | −2301 (31) | −2397 (31) | −3253 (31) | −3227 (31) |
| hash_h | mlkem_o3 − Official | −369 (31) | −384 (31) | −583 (31) | −561 (31) | −766 (31) | −750 (31) |
| keypair | base+keccak − Official | −4463 (31) | −4493 (31) | −5320 (31) | −5428 (31) | −7398 (31) | −7497 (31) |
| keypair | base+keccak − base | −4263 (31) | −4241 (31) | −4407 (31) | −4560 (31) | −6896 (31) | −6883 (31) |
| keypair | keccak-only − Official | −4203 (31) | −4224 (31) | −4350 (31) | −4439 (31) | −7010 (31) | −6738 (31) |
| encap | base+keccak − Official | −7789 (31) | −7604 (31) | −9401 (31) | −9640 (31) | −11946 (31) | −11752 (31) |
| encap | base+keccak − base | −7529 (31) | −7338 (31) | −8551 (31) | −8689 (31) | −11588 (31) | −11558 (31) |
| encap | keccak-only − Official | −7564 (31) | −7376 (31) | −8418 (31) | −8712 (31) | −11635 (31) | −11418 (31) |
| decap | base+keccak − Official | −4268 (31) | −4265 (31) | −6108 (31) | −6372 (31) | −6838 (31) | −6906 (31) |
| decap | base+keccak − base | −4029 (31) | −4050 (31) | −4600 (31) | −4833 (31) | −6523 (31) | −6555 (31) |
| decap | keccak-only − Official | −4088 (31) | −4055 (31) | −4567 (31) | −4874 (31) | −6562 (31) | −6572 (31) |

Official pooled StQ2 (normal link order): permute 1336/1341/1334; hash_f 10935/12117/15712; hash_g 12140/13269/18115;
hash_h 2652/3838/4991; keypair 63817/66857/94350; encap 28247/32758/43046; decap 19460/23670/30582 (768/864/1152).
Relative to Official, base+keccak is (normal):

| | keypair | encap | decap |
|---|---:|---:|---:|
| 768 | −7.0 % | −27.6 % | −21.9 % |
| 864 | −8.0 % | −28.7 % | −25.8 % |
| 1152 | −7.8 % | −27.8 % | −22.4 % |

Every KEM delta is favourable in 31/31 launches in both link orders. Normal and reversed agree
within 5 %. The Keccak saving and the base candidate's saving add up:
`base+keccak − keccak-only ≈ base − Official`, for example 864 encap −983 vs −851.
The per-call cpucycles overhead (~190 cycles) is included equally in every variant. That is why the permutation
reads 1336 → 1167 here, against Codex's batched 1142 → 950.

**KEM effect larger than the isolated hash sum.** The in-KEM Keccak saving is about 1.7× the sum of the
isolated `hash_*` deltas: 768 encap −7529 vs −4384 (f+g+h); decap −4029 vs −2494 (g+h); 1152 encap −11 588 vs −6792.
A scratch probe (not committed) timed a 768 Official encap with the hash functions stubbed at 3111 cycles.
Official encap ≈ 3111 + its isolated hash costs, but candidate encap is ~1.6k below 3111 + the candidate's isolated hash costs.
So the mlkem-native hashes run faster inside the KEM than in the back-to-back per-call harness.
The cause is not established. Candidates are store-forwarding or 4K-aliasing effects of the tight loop, or predictor
state after each cpucycles read. The practical consequence is that component numbers understate the KEM effect in this harness.
Only Native SUPERCOP can settle the size of the effect.

### -O2 vs -O3 sensitivity (SUPERCOP picks the compiler per implementation)

| | 768 normal | 768 reversed | 864 normal | 864 reversed | 1152 normal | 1152 reversed |
|---|---:|---:|---:|---:|---:|---:|
| hash_g mlkem_o2 − mlkem_o3 | +1464 (0/31) | +1507 (0/31) | +1659 (0/31) | +1660 (0/31) | +2167 (0/31) | +2061 (0/31) |
| hash_g mlkem_o2 − Official | −662 (31) | −608 (31) | −642 (31) | −737 (31) | −1086 (31) | −1166 (31) |
| hash_f mlkem_o2 − mlkem_o3 | +1291 | +1326 | +1483 | +1476 | +1913 | +1828 |
| hash_h mlkem_o2 − mlkem_o3 | +339 | +339 | +366 | +352 | +443 | +416 |
| permute mlkem_o2 − mlkem_o3 | +13 | +1 | +13 | −15 | −8 | −4 |

The C permutation is insensitive to -O2 vs -O3. The whole -O2 penalty is in `keccakf1600_xor_bytes` and `extract_bytes`:
GCC 15 at `-O2` leaves them as byte loops (16/15 instructions, no vector code), whereas `-O3` vectorises them (121/109 instructions).
That is ~140-160 cycles per 136-byte block. At -O2 the candidate still beats Official on every hash (31/31 launches; 768 `hash_h` by only −30/−45), but it loses about two thirds of the hash saving.
This matters for Native: SUPERCOP picks the fastest `okc` line per implementation. If it picked `-O2`/`-Os`/`-O`,
most of the gain would disappear. Earlier 864 Phase-B records show SUPERCOP choosing `-O2` for some candidates.
A compiler-independent fix would need vectorised absorb/extract outside the vendored files; this change does not attempt it.

## Deviations and notes

- mlkem-native is built without `MLK_CONFIG_USE_NATIVE_BACKEND_FIPS202`, unlike Codex's comparison. The x1 code is equal apart from one tail jump (see above), and no x4 assembly is needed.
- `MLK_CONFIG_PARAMETER_SET 768` and the single prefix `ntruplus_mlkfips202` are used for all three NTRU+ parameters. The FIPS202 code does not depend on them. Linking two NTRU+ parameters' candidates into one binary would need distinct prefixes, a one-line config change.
- The mlk symbols have default visibility; they are namespaced but not hidden. Official `NTRUPLUS_INTERNAL` marks its own symbols hidden.
- The wrappers keep the Official `memcpy` + `explicit_bzero` (`secure_clear`) code, so the new hash path calls glibc `memcpy`/`__explicit_bzero_chk` exactly as Official does. The mlk part itself calls only `__stack_chk_fail`.
- mlk_shake256 is one-shot: absorb_once and squeeze_once, zeroizing its state. Official also clears its state. mlkem-native uses `memset` + an asm barrier; Official uses `explicit_bzero`.
- The KEM test reuses `test_kem_lazy.c`, so its log lines say "caller-lazy". The `CANDIDATE_SHAKE256` hook is the only change to it.
- The CAVP file is a 76-vector subset (ShortMsg 37, LongMsg 8, VariableOut 31), not the full CAVP set.

## Reproduction

```sh
cd ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_official_opt_freeze_001   # or the 864 / 1152 dirs
git clone https://github.com/pq-code-package/mlkem-native.git /tmp/mlkem-native
git -C /tmp/mlkem-native checkout b3ba7b32773e657dd37f6f87bce82528459ad8a4
make keccak-record MLK_ROOT=/tmp/mlkem-native       # all Phase-A gates -> results/keccak-phase-a/
make keccak-flat FLAT_OUT=/tmp/flat768              # SUPERCOP-flat compile + try (scratch)
make keccak-bench
python3 ../../../common/official_opt_lazy/tools/phase_b_batch.py --result-dir results/keccak-diag-normal-TAG \
  --metadata metadata.json -- python3 ../../../common/official_opt_keccak/tools/run_keccak_diag.py \
  --param 768 --experiment . --launches 31 --result-dir {RESULT}
# reversed link order: add --binary build/bench_keccak_diag_swapped (result dir keccak-diag-reversed-TAG)
python3 ../../../common/official_opt_keccak/tools/summarize_keccak_diag.py --tag TAG
# CAVP subset provenance: make keccak-vectors-check CAVP_ZIP=shakebytetestvectors.zip
```

## Phase B: Native SUPERCOP (2026-09-24)

Worktree `ntru_plus-official-opt-864-1152`, branch `official-opt-lazy-864-1152`, from `4d14314`
(= `origin/avx2-official-opt`). Not pushed. Everything ran on CPU 1 of the Core Ultra 7 155H, with ASLR on
(`randomize_va_space=2`) and normal placement only. The host was checked and left unchanged:
`performance` governor, `intel_pstate/no_turbo=1`. Every timing batch ran under `phase_b_batch.py` /
`hygiene_batch.py`. All timing ran strictly one batch after another, and nothing was built while timing ran.

### Qualification exports (measured)

`export_keccak_flat.py` has a new mode, `--qualification-root` (`make keccak-qualification`). It writes the
same flat tree that Phase A compiled into `qualification/<name>/`, plus a JSON manifest. It runs no compiler.
It refuses to overwrite and checks the following:

- the base export's manifest matches `bench/supercop.lock`, and the base tree matches that manifest (tree hash and every file hash);
- every vendored `third_party/mlkem-native-fips202-b3ba7b32` file matches the per-file SHA-256 table in its
  `README.md`, and every vendored source file carries `SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT`
  (upstream `LICENSE` ships as `LICENSE.mlkem-native`);
- `kem.c` and `symmetric.c` are still the base export's files;
- the export is file-for-file identical to the Phase-A flat tree in `results/keccak-supercop-flat-20260923/summary.json`.

The manifest (`kind: keccak-qualification-source`) records the tree hash, all 36 file hashes, the base
identity, and each vendored file with its upstream path, commit, source/flat hash and SPDX. It also records the
LICENSE hash, the adapter/config sources, all 16 `#include` rewrites and the exporter's own hash.
`install_qualification.py` now accepts this kind and also checks the exported file set. It installed the three
trees into `/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001`. The base exports already installed
there were re-hashed and match their committed manifests.

| n | Export (under the experiment's `qualification/`) | Tree SHA-256 | Base export (tree) |
|---|---|---|---|
| 768 | `avx2-officialopt-lazy-freeze-keccak-qual001` | `6209ebacb81ce313a43d305b960c6b5e94618ff6149abd326c39c15f98bb4fb6` | `avx2-officialopt-lazy-freeze-qual001` (`2d9fa350…`) |
| 864 | `avx2-officialopt-lazy-codec-keccak-qual001` | `0deb127b6f90e4e98bd3338abe1635f878a0e2e46ae4ef8667abbe2aa1e4da71` | `avx2-officialopt-lazy-codec-qual002` (`ece23c1a…`) |
| 1152 | `avx2-officialopt-lazy-freeze-keccak-qual001` | `e88c9c6d67606a4a414999a2992a9192c9049572a7c0ee328505412625f39dd0` | `avx2-officialopt-lazy-freeze-qual001` (`3e8068bb…`) |

**SUPERCOP try passes.** In every default-selection batch, `try` reported `ok` for all four compilers
(O3/Os/O2/O), with checksumsmall/checksumbig equal to the pinned `crypto_kem/ntruplus<N>/checksum*` (= Official).
The single compiler line of every fixed-O3/O2 batch passed too, and so did the O3GC fixed builds.
`summarize_extended_multi.py` now reads these `try` records and fails on any mismatch. SUPERCOP's namespace
report lists the 13 `ntruplus_mlkfips202_*` globals as outside `CRYPTO_NAMESPACE`. That is the same class as
the Official `KeccakP1600_*` symbols it replaces, and it is not a failure.

### Design (measured)

- **Native:** three roles: `official` (`avx2`), `base` (the installed current best export) and `keccak`
  (the new export). Each role had 27 fresh launches: 3 rounds with one 9-launch
  `run_supercop_benchmark.py --mode native-kem` batch per role per round. The role order rotated:
  official,base,keccak / keccak,official,base / base,keccak,official. `measure.c` was unmodified. The user
  decided that 27 launches are enough because the expected effect is thousands of cycles. Each role is pooled
  independently. CIs come from resampling launches within each role (2,000 resamples).
- **Three compiler settings, each a full 3 x 27 run per parameter:** SUPERCOP default selection (4-line
  `okc-amd64`); fixed `-O3` only; fixed `-O2` only. For the fixed runs, `run_extended_native.py --compiler-wrapper`
  passes `okc-native-gcc-{O3,O2}-only.sh` to each batch, and the batch swaps it in and restores it afterwards.
  After every batch the runner checked that the campaign `okc-amd64` was back to `82f1eea7…98b3`, and it
  was unchanged every time.
- **Paired:** O3GC fixed ELFs (`bench/supercop/okc-o3gc.sh`, one fresh build per role and parameter via
  `run_supercop_benchmark.py --fresh-launches 1`). `run_paired_aslr_on.py` ran 48 ABBA/BAAB blocks
  (192 fresh launches) with normal placement and ASLR on, for keccak vs Official and keccak vs base. The rebuilt
  864 Official (`9bf4b8b7…`), 864 base (`22276081…`) and 1152 Official (`fe8de722…`) ELFs are byte-identical
  to the earlier Phase-B builds.
- **Hygiene:** 96 batches ran (81 Native, 9 fixed-ELF builds, 6 paired). All were accepted on attempt 0 and
  none was contaminated. Pre-batch 1-minute load was 0.03-0.50. Default-selection batches took 12.7-16.5 s and
  fixed-compiler batches 4.6-5.8 s. Paired batches took 1.6-2.2 s, so only the before/after snapshots apply to them.

### Native, default SUPERCOP compiler selection

| n | Op | Official | Base | Keccak | Keccak − Official [95% CI] fav. | Keccak − Base [95% CI] fav. | Base − Official |
|---|---|---:|---:|---:|---:|---:|---:|
| 768 | Keypair | 21,594.0 | 21,379.4 | 16,842.9 | **−4,751.1** (−22.0%) [−4,765.3, −4,737.2] 27/27 | −4,536.4 (−21.2%) [−4,561.2, −4,512.9] 27/27 | −214.7 [−237.3, −190.5] 27/27 |
| 768 | Encap | 28,157.8 | 27,998.2 | 20,530.8 | **−7,627.0** (−27.1%) [−7,722.9, −7,573.3] 27/27 | −7,467.4 (−26.7%) [−7,536.8, −7,410.6] 27/27 | −159.6 [−258.9, −80.2] 25/27 |
| 768 | Decap | 19,465.9 | 19,147.0 | 15,043.3 | **−4,422.6** (−22.7%) [−4,455.8, −4,393.0] 27/27 | −4,103.7 (−21.4%) [−4,136.4, −4,074.9] 27/27 | −318.9 [−354.8, −280.5] 26/27 |
| 864 | Keypair | 23,745.9 | 22,896.2 | 17,972.8 | **−5,773.1** (−24.3%) [−5,805.0, −5,745.3] 27/27 | −4,923.4 (−21.5%) [−4,963.2, −4,877.1] 27/27 | −849.7 [−904.1, −804.1] 27/27 |
| 864 | Encap | 32,933.8 | 32,120.3 | 23,418.2 | **−9,515.6** (−28.9%) [−9,583.7, −9,455.6] 27/27 | −8,702.1 (−27.1%) [−8,744.7, −8,662.1] 27/27 | −813.5 [−881.9, −747.8] 27/27 |
| 864 | Decap | 23,686.4 | 22,350.5 | 17,463.8 | **−6,222.6** (−26.3%) [−6,262.0, −6,186.5] 27/27 | −4,886.7 (−21.9%) [−4,916.5, −4,855.6] 27/27 | −1,335.9 [−1,376.0, −1,298.8] 27/27 |
| 1152 | Keypair | 34,705.0 | 34,164.4 | 27,104.5 | **−7,600.5** (−21.9%) [−8,089.2, −7,098.9] 27/27 | −7,059.9 (−20.7%) [−7,563.8, −6,583.4] 27/27 | −540.7 [−1,097.0, +42.0] 18/27 |
| 1152 | Encap | 43,100.0 | 42,655.1 | 31,216.7 | **−11,883.3** (−27.6%) [−11,941.2, −11,839.3] 27/27 | −11,438.4 (−26.8%) [−11,518.4, −11,348.0] 27/27 | −444.9 [−548.2, −355.3] 25/27 |
| 1152 | Decap | 30,510.4 | 30,112.6 | 23,462.8 | **−7,047.6** (−23.1%) [−7,078.4, −7,007.2] 27/27 | −6,649.8 (−22.1%) [−6,707.6, −6,583.9] 27/27 | −397.8 [−463.6, −329.3] 26/27 |

### Native, fixed `-O3` only

| n | Op | Official | Base | Keccak | Keccak − Official [95% CI] fav. | Keccak − Base [95% CI] fav. | Base − Official |
|---|---|---:|---:|---:|---:|---:|---:|
| 768 | Keypair | 21,623.3 | 21,351.7 | 16,867.6 | **−4,755.7** (−22.0%) [−4,784.0, −4,729.8] 27/27 | −4,484.1 (−21.0%) [−4,525.6, −4,451.4] 27/27 | −271.6 [−302.8, −237.6] 27/27 |
| 768 | Encap | 28,269.6 | 28,059.6 | 20,523.9 | **−7,745.6** (−27.4%) [−7,772.0, −7,719.2] 27/27 | −7,535.6 (−26.9%) [−7,574.6, −7,499.1] 27/27 | −210.0 [−251.8, −167.1] 26/27 |
| 768 | Decap | 19,470.0 | 19,250.0 | 15,049.5 | **−4,420.5** (−22.7%) [−4,435.7, −4,403.6] 27/27 | −4,200.5 (−21.8%) [−4,229.6, −4,174.4] 27/27 | −220.0 [−244.6, −192.0] 26/27 |
| 864 | Keypair | 23,737.3 | 22,766.4 | 17,976.6 | **−5,760.7** (−24.3%) [−5,781.0, −5,740.2] 27/27 | −4,789.8 (−21.0%) [−4,831.5, −4,759.1] 27/27 | −970.9 [−1,002.2, −926.6] 27/27 |
| 864 | Encap | 32,908.3 | 32,138.5 | 23,404.3 | **−9,504.0** (−28.9%) [−9,538.8, −9,467.0] 27/27 | −8,734.2 (−27.2%) [−8,788.2, −8,697.6] 27/27 | −769.8 [−810.7, −718.3] 27/27 |
| 864 | Decap | 23,646.9 | 22,362.4 | 17,451.9 | **−6,195.0** (−26.2%) [−6,222.0, −6,166.6] 27/27 | −4,910.4 (−22.0%) [−4,933.0, −4,888.5] 27/27 | −1,284.5 [−1,309.7, −1,259.3] 27/27 |
| 1152 | Keypair | 34,691.9 | 33,733.8 | 27,468.4 | **−7,223.5** (−20.8%) [−7,792.0, −6,646.8] 27/27 | −6,265.4 (−18.6%) [−6,802.2, −5,796.5] 27/27 | −958.0 [−1,543.1, −330.5] 23/27 |
| 1152 | Encap | 43,113.0 | 42,736.4 | 31,266.1 | **−11,846.9** (−27.5%) [−11,936.6, −11,770.7] 27/27 | −11,470.3 (−26.8%) [−11,519.7, −11,396.1] 27/27 | −376.6 [−458.4, −341.5] 27/27 |
| 1152 | Decap | 30,542.1 | 30,200.5 | 23,463.9 | **−7,078.2** (−23.2%) [−7,096.6, −7,059.6] 27/27 | −6,736.6 (−22.3%) [−6,761.8, −6,715.0] 27/27 | −341.6 [−359.9, −321.3] 27/27 |

### Native, fixed `-O2` only

| n | Op | Official | Base | Keccak | Keccak − Official [95% CI] fav. | Keccak − Base [95% CI] fav. | Base − Official |
|---|---|---:|---:|---:|---:|---:|---:|
| 768 | Keypair | 21,599.6 | 21,377.1 | 18,363.1 | **−3,236.5** (−15.0%) [−3,267.8, −3,211.0] 27/27 | −3,014.0 (−14.1%) [−3,040.2, −2,990.4] 27/27 | −222.5 [−260.8, −187.3] 26/27 |
| 768 | Encap | 28,178.6 | 27,975.9 | 23,438.1 | **−4,740.5** (−16.8%) [−4,867.5, −4,673.6] 27/27 | −4,537.8 (−16.2%) [−4,580.3, −4,492.3] 27/27 | −202.7 [−327.0, −125.0] 25/27 |
| 768 | Decap | 19,461.3 | 19,167.2 | 16,697.3 | **−2,764.0** (−14.2%) [−2,789.2, −2,737.4] 27/27 | −2,469.9 (−12.9%) [−2,513.3, −2,437.2] 27/27 | −294.1 [−334.0, −242.4] 27/27 |
| 864 | Keypair | 23,788.1 | 22,909.0 | 19,771.9 | **−4,016.2** (−16.9%) [−4,052.7, −3,983.1] 27/27 | −3,137.1 (−13.7%) [−3,154.3, −3,119.2] 27/27 | −879.1 [−916.3, −845.2] 27/27 |
| 864 | Encap | 32,937.9 | 32,076.6 | 26,639.0 | **−6,298.8** (−19.1%) [−6,343.1, −6,255.5] 27/27 | −5,437.6 (−17.0%) [−5,462.7, −5,411.9] 27/27 | −861.3 [−910.3, −812.6] 27/27 |
| 864 | Decap | 23,756.0 | 22,287.7 | 19,227.9 | **−4,528.1** (−19.1%) [−4,570.2, −4,487.9] 27/27 | −3,059.8 (−13.7%) [−3,090.3, −3,032.9] 27/27 | −1,468.3 [−1,512.8, −1,420.6] 27/27 |
| 1152 | Keypair | 34,917.8 | 34,074.9 | 29,505.5 | **−5,412.3** (−15.5%) [−5,911.9, −4,924.3] 27/27 | −4,569.5 (−13.4%) [−5,113.6, −4,040.9] 27/27 | −842.9 [−1,338.3, −402.8] 23/27 |
| 1152 | Encap | 43,016.5 | 42,521.2 | 35,406.9 | **−7,609.6** (−17.7%) [−7,728.0, −7,507.6] 27/27 | −7,114.3 (−16.7%) [−7,255.3, −7,015.3] 27/27 | −495.3 [−632.3, −338.5] 25/27 |
| 1152 | Decap | 30,435.5 | 30,010.1 | 25,862.9 | **−4,572.6** (−15.0%) [−4,664.9, −4,494.0] 27/27 | −4,147.2 (−13.8%) [−4,173.3, −4,121.1] 27/27 | −425.4 [−519.7, −343.5] 27/27 |

### Compiler picks (default selection), batches 1-3

| n | Official | Base | Keccak |
|---|---|---|---|
| 768 | O2 O2 O2 | O2 O2 O2 | O3 O3 O3 |
| 864 | O3 O3 O3 | O2 O2 O3 | O3 O3 O3 |
| 1152 | O3 O3 O2 | O2 O3 O2 | O3 O3 O3 |

### Fixed-ELF paired, O3GC, ASLR on, normal placement, 48 blocks

| n | Op | Keccak vs Official: mean [95% CI] fav./48 | Keccak vs Base: mean [95% CI] fav./48 |
|---|---|---:|---:|
| 768 | Keypair | **−4,806.1** [−4,818.8, −4,795.2] 48/48 | −4,530.4 [−4,543.1, −4,518.0] 48/48 |
| 768 | Encap | **−7,649.9** [−7,698.5, −7,612.2] 48/48 | −7,523.8 [−7,560.1, −7,492.9] 48/48 |
| 768 | Decap | **−4,353.1** [−4,372.2, −4,335.3] 48/48 | −4,193.2 [−4,208.5, −4,177.7] 48/48 |
| 864 | Keypair | **−5,906.6** [−5,935.0, −5,884.2] 48/48 | −4,972.1 [−4,987.8, −4,957.0] 48/48 |
| 864 | Encap | **−9,406.5** [−9,436.7, −9,379.0] 48/48 | −8,556.0 [−8,580.8, −8,531.0] 48/48 |
| 864 | Decap | **−6,371.0** [−6,396.6, −6,346.9] 48/48 | −4,901.6 [−4,928.8, −4,878.4] 48/48 |
| 1152 | Keypair | **−7,489.7** [−7,779.9, −7,189.4] 48/48 | −6,985.1 [−7,258.0, −6,712.9] 48/48 |
| 1152 | Encap | **−11,725.6** [−11,768.1, −11,676.9] 48/48 | −11,259.6 [−11,297.8, −11,225.0] 48/48 |
| 1152 | Decap | **−6,960.4** [−6,990.0, −6,934.3] 48/48 | −6,564.3 [−6,586.8, −6,544.5] 48/48 |

### Anomaly check (keccak − base)

| n | Op | Native (default) | Same-ELF in-KEM (Phase A) | Isolated hash sum (Phase A) | Native / same-ELF | Native / isolated |
|---|---|---:|---:|---:|---:|---:|
| 768 | Keypair | −4,536.4 | −4,263.1 | n/a | 1.06 | n/a |
| 768 | Encap | −7,467.4 | −7,528.6 | −4,385.0 (hash_f+hash_g+hash_h) | 0.99 | 1.70 |
| 768 | Decap | −4,103.7 | −4,029.5 | −2,494.6 (hash_g+hash_h) | 1.02 | 1.65 |
| 864 | Keypair | −4,923.4 | −4,406.8 | n/a | 1.12 | n/a |
| 864 | Encap | −8,702.1 | −8,550.5 | −5,007.0 (hash_f+hash_g+hash_h) | 1.02 | 1.74 |
| 864 | Decap | −4,886.7 | −4,600.3 | −2,884.3 (hash_g+hash_h) | 1.06 | 1.69 |
| 1152 | Keypair | −7,059.9 | −6,896.2 | n/a | 1.02 | n/a |
| 1152 | Encap | −11,438.4 | −11,588.4 | −6,791.7 (hash_f+hash_g+hash_h) | 0.99 | 1.68 |
| 1152 | Decap | −6,649.8 | −6,523.0 | −4,019.0 (hash_g+hash_h) | 1.02 | 1.65 |

Values are pooled StQ2 cycles. "fav." is the number of candidate launches below the baseline's median launch.
CIs come from launch resampling. Per-batch deltas are in `STATUS.yml` and in the summaries. Every per-batch
Keccak − Official and Keccak − Base delta (3 per comparison and setting) is negative under all three compiler settings.

- **Compiler pick.** SUPERCOP picked `-O3` for the Keccak candidate in 9/9 batches. Official and base moved
  between `-O2` and `-O3`, as in earlier runs. The default-selection candidate ELFs are byte-identical to the
  fixed-O3 ones (768 `243d2fcd…`, 864 `c36b0349…`, 1152 `b645c5b3…`).
- **`-O2` sensitivity.** At fixed `-O2` the Keccak saving vs base drops to 59-73% of the fixed `-O3` saving
  (768 67/60/59%, 864 65/62/62%, 1152 73/62/62% for keypair/enc/dec). The cause is the byte-loop
  `xor_bytes`/`extract_bytes` described above. The saving stays 2.5-7 thousand cycles and every launch is
  favourable, so the candidate beats both Official and base under every compiler line tested.
- **1152 Keypair** has a wide CI, [−8,089, −7,099] for keccak − Official, because of the known BaseInv retry
  tail. The paired CI is also wider ([−7,780, −7,189]) but far below zero. The **base − Official** keypair CI for
  1152 crosses zero ([−1,097, +42], 18/27) at default selection; that does not bear on the Keccak verdict.

### Decision (rule: Native default-selection pooled delta vs Official < 0 AND normal-placement ASLR-on paired CI vs Official < 0)

| n | Keypair | Encap | Decap |
|---|---|---|---|
| 768 | **robust research win** | **robust research win** | **robust research win** |
| 864 | **robust research win** | **robust research win** | **robust research win** |
| 1152 | **robust research win** | **robust research win** | **robust research win** |

The same rule with the base candidate as the baseline also gives a robust research win for all 9 (n, op)
pairs. Under fixed `-O3` and fixed `-O2` every Native delta is also negative, vs Official and vs base, so the
result does not depend on SUPERCOP's compiler pick. `promotion: none`, and `clean/` was not touched. Details:
`STATUS.yml` `keccak_candidate.phase_b` and `results/keccak-phase-b-summary-20260924k.json` for each parameter.

### Phase-A anomaly: settled by Native

In Phase A, the in-KEM Keccak saving (same ELF) was about 1.7x the sum of the isolated `hash_*` deltas.
Native answers which figure is real: the Native keccak − base saving matches the **same-ELF in-KEM delta**
(ratio 0.99-1.06 for Encap/Decap). It is **not** the isolated hash sum (ratio 1.65-1.74). For 768 Encap,
Native gives −7,467 against the same-ELF −7,529 and the isolated −4,385. The per-call component harness
therefore understates the in-KEM benefit, and component numbers should not be used to predict KEM deltas for
this change. Keypair has no isolated counterpart; its Native saving is 1.02-1.12x the same-ELF value.

### Reproduce Phase B

```sh
REPO=/home/nuc/src/ntru_plus-official-opt-864-1152
A=$REPO/ntruplus-ntt-Optimized/Additional_Implementation/avx2
T=$A/common/official_opt_lazy/tools; W=$A/common/official_opt_lazy/compilers
C=/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001; TAG=20260924k
E768=$A/NTRU+768/experiments/avx2_official_opt_freeze_001; E864=$A/NTRU+864/experiments/avx2_official_opt_001
E1152=$A/NTRU+1152/experiments/avx2_official_opt_001
# exports (committed; recreate into a new dir with ... --qualification-root <dir>)
(cd $E768 && make keccak-qualification); (cd $E864 && make keccak-qualification); (cd $E1152 && make keccak-qualification)
python3 $T/install_qualification.py --param 768 --campaign-root $C --export-root $E768/qualification/avx2-officialopt-lazy-freeze-keccak-qual001
python3 $T/install_qualification.py --param 864 --campaign-root $C --export-root $E864/qualification/avx2-officialopt-lazy-codec-keccak-qual001
python3 $T/install_qualification.py --param 1152 --campaign-root $C --export-root $E1152/qualification/avx2-officialopt-lazy-freeze-keccak-qual001
# per parameter p (E, BASE, CAND as above; 864: BASE=avx2-officialopt-lazy-codec-qual002, CAND=avx2-officialopt-lazy-codec-keccak-qual001;
# 768/1152: BASE=avx2-officialopt-lazy-freeze-qual001, CAND=avx2-officialopt-lazy-freeze-keccak-qual001)
ROLES="--role official=avx2 --role base=$BASE --role keccak=$CAND"
python3 $T/run_extended_native.py --param $p --experiment $E --campaign-root $C --tag $TAG --batches 3 --order rotate $ROLES
for cc in O3 O2; do
  python3 $T/run_extended_native.py --param $p --experiment $E --campaign-root $C --tag $TAG$cc --batches 3 --order rotate $ROLES \
    --compiler-wrapper $W/okc-native-gcc-$cc-only.sh
done
for spec in official:avx2 base:$BASE keccak:$CAND; do
  python3 $T/phase_b_batch.py --result-dir $E/results/fixed-keccak-${spec%%:*}-normal-$TAG --metadata metadata.json -- \
    python3 $REPO/scripts/run_supercop_benchmark.py --campaign-root $C --parameter $p --implementation ${spec#*:} \
    --cpu 1 --mode native-kem --fresh-launches 1 --compiler-wrapper $REPO/bench/supercop/okc-o3gc.sh \
    --require-frequency-control --result-dir {RESULT}
done
for b in official base; do R=$E/results
  python3 $T/phase_b_batch.py --result-dir $R/paired-aslr-on-normal-keccak-vs-$b-$TAG --metadata manifest.json -- \
    python3 $T/run_paired_aslr_on.py --official $R/fixed-keccak-$b-normal-$TAG/measure \
    --candidate $R/fixed-keccak-keccak-normal-$TAG/measure --placement normal --cpu 1 --blocks 48 --compiler-recipe O3GC --output {RESULT}
  python3 $REPO/scripts/summarize_supercop_paired.py --campaign $R/paired-aslr-on-normal-keccak-vs-$b-$TAG --parameter $p
done
CMP="--comparison keccak:official --comparison keccak:base --comparison base:official"
python3 $T/summarize_extended_multi.py --param $p --experiment $E --tag $TAG --order rotate --roles official,base,keccak $CMP \
  --paired keccak:official=keccak-vs-official-$TAG --paired keccak:base=keccak-vs-base-$TAG
for cc in O3 O2; do python3 $T/summarize_extended_multi.py --param $p --experiment $E --tag $TAG$cc --order rotate --roles official,base,keccak $CMP; done
python3 $A/common/official_opt_keccak/tools/summarize_keccak_phase_b.py --param $p --experiment $E --tag $TAG
```

Curated evidence per experiment: `results/native-ext-{official,base,keccak}-b{1..3}-20260924k{,O3,O2}/`
(`metadata.json`, `stq-summary.json`, `supercop.lock`), `results/fixed-keccak-*-normal-20260924k/`,
`results/paired-aslr-on-normal-keccak-vs-{official,base}-20260924k/`,
`results/extended-multi-summary-20260924k{,O3,O2}.json`, `results/keccak-phase-b-summary-20260924k.json`.
Raw launch output, `data`, `run.out`, the `measure` ELFs and `host-hygiene.json` stay local (Git-ignored).

### Deviations

- 27 launches per role instead of the 81 used for earlier small-effect candidates. This was the user's
  decision. The CI half-widths are 0.3-7% of the Keccak deltas under default selection, and at most 12%
  (1152 Keypair, fixed `-O2`) in the fixed-compiler runs.
- No reversed-placement paired run (not requested). The Phase-A same-ELF diagnostic had both link orders agree within 5%.
- The fixed-ELF Official/base ELFs were rebuilt instead of reused. Where earlier builds exist they are byte-identical.
- One analysis-tool fix: `summarize_extended{,_multi}.py` read the batch number with `split("-b")`, which broke
  for a role named `base`. It is now parsed after the `native-ext-<role>-b` prefix. Summaries of earlier tags do not change.

## Next (not done)

- No production promotion and no `clean/` package. The next step toward production would be a clean package and
  a release-package Native re-confirmation.
- A compiler-independent vectorised absorb/extract for the byte-level `xor_bytes`/`extract_bytes` is **not needed
  for SUPERCOP**, which picked `-O3` for the candidate in every batch. It would recover the remaining ~30-40% for
  `-O2` builds. It would have to sit outside the vendored files, as a replacement TU, and would need its own gates.
- Distinct `MLK_CONFIG_NAMESPACE_PREFIX` per parameter if several NTRU+ parameters are ever linked into one binary.

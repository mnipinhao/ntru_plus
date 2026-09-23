# NTRU+768 / 864 / 1152 Official AVX2: mlkem-native x1 C Keccak for every SHAKE256

Date 2026-09-23, branch `official-opt-lazy-864-1152` (from `335daed` = `origin/avx2-official-opt`, not pushed).
This is Phase A (code, correctness, audits) plus a same-ELF diagnostic. No SUPERCOP campaign was
created and no Native timing was run.

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

## Next (not done)

- Phase B: export the flat trees as qualification trees and run Native SUPERCOP. Default compiler selection first,
  then fixed `-O3` and fixed `-O2` single-line runs (the `common/official_opt_lazy/compilers/` wrappers).
  Record which `okc` line SUPERCOP picks.
- If `-O2` or another non-O3 line is picked, consider a compiler-independent vectorised absorb/extract for the
  byte-level `xor_bytes`/`extract_bytes`. It would have to sit outside the vendored files, as a replacement TU, and would need its own gates.
- No production promotion.

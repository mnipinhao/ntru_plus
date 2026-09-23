# NTRU+864 / NTRU+1152 Official AVX2: caller-bounded lazy Forward (Phases A and B)

Branch `official-opt-lazy-864-1152`, forked from `avx2-official-opt` at
`e76ecdf`. This ports the NTRU+768 caller-lazy Forward
(`docs/ntruplus768-official-opt.md`, Rounds 4-6) to the two larger Official
parameter sets. **Phase A is only about correctness**; it made no timing,
SUPERCOP campaign or host-control change. **Phase B** (Native SUPERCOP
performance evidence, 2026-09-23) and its follow-up (fixed-compiler 864
Native, 1152 Keypair retry control) are at the end of this document, followed
by the extended Native / ASLR-on paired runs, which carry the current
decision rule (ASLR on only; normal placement primary). A second, 864-only
candidate (lazy Forward + layout-fused codec, Phase A and same-ELF diagnostic
only) has its own section near the end. No host control was changed in any
phase.

## Scope

| | NTRU+864 | NTRU+1152 |
|---|---|---|
| Experiment | `NTRU+864/experiments/avx2_official_opt_001` | `NTRU+1152/experiments/avx2_official_opt_001` |
| Upstream (SUPERCOP 20260831, imported once, never edited) | tree `13e0d983…7006` | tree `78daf6b9…5010` |
| Removed block | `ntt.s:365-383` (`#reduce2`), 6 regs/iter | `ntt.s:403-428` (`#reduce2`), 8 regs/iter |
| Removed per Forward | 54 each of `vpmulhrsw`/`vpmullw`/`vpsubw`, plus 1 `_16xv` load | 72 each, plus 1 `_16xv` load |
| Candidate symbol | `ntruplus864_officialopt_ntt_caller_lazy`, 1,329 B | `ntruplus1152_officialopt_ntt_caller_lazy`, 1,569 B |

Every other instruction of Official `poly_ntt` is kept in order. The
general-input `poly_ntt` stays linked and unchanged. The candidate KEM
(`src/kem_lazy.c`) is Official `kem.c`, which is byte-identical for 768, 864
and 1152, with its six `poly_ntt` calls redirected to the namespaced entry.
The entry is valid only for the Official caller domains (inputs in `[-3,4]`).
No general-input claim is made.

The shared, parameterised tooling is in
`ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/official_opt_lazy/`:
`tools/` (generator, linked audit), `tests/` (Forward and KEM differentials),
`range_proof/` (the Phase-0 reduction-audit emulator and ledger, ported to
read the experiment's upstream copy and the generated ASM), and `lazy.mk`.

## Gates (all pass for both parameters)

1. **Generator** (`make check-generate`). It pins the `ntt.s` and `kem.c`
   hashes and asserts that exactly one `#reduce2…#store` block exists, with
   the exact opcode counts. It also checks that each `vpsubw` closes an
   `x -= q·round(x·v/2^15)` on a register that is later stored, that the
   terminal loop runs 9 times, and that `%ymm1` is used nowhere else. The
   derivation is run twice and must be byte-identical. `--check` confirms
   that the committed ASM and KEM equal a fresh regeneration.
2. **Forward differential**. 27,295 cases for 864 and 33,055 for 1152, over
   five caller domains. The patterns are constants, alternating values, 4N
   impulse patterns, 1000 random inputs and 1000 extreme-only inputs.
   - Checks per case: lazy ≡ Official (mod q) in every lane; Official Barrett
     applied to the lazy output equals the Official output bit-exactly; the
     output lies within the per-domain proven bound; the canaries are intact.
   - Extra checks: the producer domains of cbd1, triple and sotp_encode, and
     crepmod3 on every int16 (output `[-2,2]`). The real
     `poly_tobytes`/`poly_frombytes` canonicalise every int16, so the lazy
     representation never reaches the wire.
3. **KEM**. 100 deterministic vectors, with pk/sk/ct/ss byte-exact against
   Official. Invalid PK, bit-flipped CT, noncanonical CT and noncanonical SK
   all behave identically.
   - Forced *g*-retry: `CBD1(g)=0`, 3 draws.
   - Forced *f*-retry: `TEST_F_RETRY`. The keys must equal an uninjected
     keypair whose first coin draw was discarded, which is stronger than the
     fixed draw count used for 768.
   - Natural retries: NTRU+1152 hit 40 natural *f*-inversion and 45 natural
     *g*-inversion retries within the 100 vectors, all byte-exact. This closes
     the "actual f-retry" gap that 768 left open, for 1152 only. NTRU+864 had
     no natural retry, so only the injected *f* path is covered for 864.
4. **Sanitizers**. ASan + UBSan (`-fno-sanitize-recover=all`) + LeakSanitizer
   passed on the Forward test, the KEM test and the KEM f-retry test.
   LeakSanitizer worked on this host, so it was **not** disabled (768 had to
   disable it). `DETECT_LEAKS=0` exists only for hosts where it breaks.
5. **Linked audit** (`results/phase-a/linked-symbol-summary.json`).
   - The symbol is unique, sized and 32-byte aligned. It has one `ret`, no
     stack reference, no call and no `vzeroupper`, and no `vpmulhrsw` or
     `_16xv` remains.
   - Compared row by row against the Official `poly_ntt` in the same ELF,
     every row is identical (branch targets included) except the removed
     block and the `_16xv` load.
   - Call relocations: the lazy KEM object calls the candidate 6 times and
     `poly_ntt` 0 times. The reference KEM calls `poly_ntt` 6 times.
6. **Range proof** (`make range-proof`, `results/phase-a/range-proof-summary.json`).
   - Validation: the emulator matches the machine on `poly_ntt`, the lazy
     entry, `poly_basemul` and `poly_baseinv_1`.
   - Method: a per-lane interval replay of the *generated* lazy ASM. It must
     equal, lane by lane, the Official replay with the terminal Barrett
     skipped. Zero signed-word failures occurred.
   - Lazy output bounds: envelope `[-17961,17957]`; keygen f
     `[-17193,17194]`, g `[-17193,17193]`; decap m′ `[-16382,16385]`;
     encap r/m and re-encryption `[-15580,15580]`.
   - Consumers: BaseInv has no overflow and its zero check is exact. BaseMul
     outputs stay within ±1865. `poly_add` stays within ±17404 (864) or
     ±17436 (1152), and `poly_sub` within `[-16385,19838]`. `tobytes` is
     canonical for every int16.
   - Any drift from the Phase-0 audit bounds is treated as a failure. A
     tampered-ASM negative test failed both `--check` and the range proof,
     as intended.

## Reproduce

```sh
cd ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+864/experiments/avx2_official_opt_001   # or NTRU+1152
make phase-a      # check-upstream, check-generate, Forward+KEM tests, sanitize, audit, range-proof
make record       # phase-a, then refresh results/phase-a/{linked-symbol,range-proof}-summary.json
```

Headers are read (read-only) from the pristine SUPERCOP 20260831 tree
(`SUPERCOP_PRISTINE`, default `/home/nuc/src/supercop-pristine-20260831`).
The deterministic RNG is the NIST KAT DRBG from
`third_party/NTRUplus-official-main`.

## Phase B: Native SUPERCOP performance

Phase B follows the NTRU+768 template (`docs/ntruplus768-official-opt.md`,
Rounds 5 and 6): a qualification export, a disposable SUPERCOP campaign,
Native KEM timing, fixed-ELF paired controls and the same-ELF complete-caller
diagnostic. Everything ran on CPU 1 of the Core Ultra 7 155H. The host was
checked and left unchanged: `performance` governor, `intel_pstate/no_turbo=1`,
SMT on (siblings 1-2), `randomize_va_space=2`. Phase B tooling is shared in
`common/official_opt_lazy/tools/`.

### Qualification export and campaign

`export_caller_lazy_qualification.py --param N` writes
`qualification/avx2-officialopt-caller-lazy-qual001/` with a sibling JSON
manifest. The export is the pinned Official tree plus `kem.c`
(= `src/kem_lazy.c`) and `ntt_caller_lazy.s` (the namespaced lazy Forward).
The manifest records all 26 source hashes. The exporter verifies the pinned
tree against `bench/supercop.lock` and refuses to overwrite. `diff -r` against
the upstream copy shows exactly those two differences.

| | NTRU+864 | NTRU+1152 |
|---|---|---|
| Export tree | `1d46cc7b…7e2e` | `4f571bc8…cff5` |
| Official tree (lock) | `13e0d983…7006` | `78daf6b9…5010` |

The campaign is `/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001`
(640 MB). `scripts/prepare_supercop.py` copied and verified it from
`supercop-pristine-20260831`, which was not modified.
`install_qualification.py` re-verified the export and the campaign's Official
`avx2`, then installed the export as
`crypto_kem/ntruplus{864,1152}/avx2-officialopt-caller-lazy-qual001`. Official
`avx2` is the baseline. `crypto_kem/measure.c` is unmodified (sha256
`7490844f…0174`, as for 768).

Deviation: a pristine copy has no host initialisation, and its
`do-part crypto_rng` cannot build `knownrandombytes` until a ChaCha20 stream
exists. The campaign was therefore initialised once, before any timing, with
`do-part init`, `do-part crypto_stream chacha20` and `do-part crypto_rng`
(all pinned to CPU 1).

### Host hygiene

Every timing batch ran under `phase_b_batch.py` → `hygiene_batch.py`. Before
a batch, the tool waited (bounded) until the 1-minute load average was at most
0.5, then recorded `uptime` and the top CPU consumers over a 3 s sample. The
same snapshot was taken after the batch. During the batch it sampled every
process every 5 s. A batch counts as contaminated if the pre-batch load is
above 0.5, if any process outside the batch holds more than 25% of a CPU for
two consecutive windows, or if a foreign benchmark-like process is seen. A
contaminated batch is quarantined in `results/_contaminated/` and re-run, up
to 2 times.

- **Result: all 16 batches were accepted on the first attempt; none was
  contaminated.**
- Pre-batch load was 0.22-0.50. The top consumers were the agent processes
  (`claude`, `codex`) and `gnome-shell`, each at or below 8% of one CPU.
- The post-batch load average includes the batch's own pinned process.
- The fixed-ELF paired batches (2.5-3.0 s) and same-ELF batches (0.8-0.9 s)
  are shorter than one 5 s in-batch window. For those, only the 3 s
  before/after snapshots apply.
- A compact record is embedded as `host_hygiene` in each `metadata.json` or
  `manifest.json`. The full per-sample record (`host-hygiene.json`) contains
  raw command lines, so it stays local and Git-ignored.

### Native SUPERCOP KEM (`supercop-native-kem`)

Each implementation was enabled alone (the others sticky). The timing used
normal SUPERCOP compiler selection and 9 fresh launches of the selected
`measure` ELF, giving 864 observations per operation. Values are pooled StQ2
cycles, and each implementation is pooled independently, so these are **not**
paired estimates.

| NTRU+864 | Official | Caller-lazy | Delta |
|---|---:|---:|---:|
| Keypair | 23,751.68 | 23,661.26 | −90.42 (−0.38%) |
| Encap | 32,891.92 | 32,832.47 | −59.45 (−0.18%) |
| Decap | 23,650.72 | 23,668.47 | **+17.75** (+0.08%) |

| NTRU+1152 | Official | Caller-lazy | Delta |
|---|---:|---:|---:|
| Keypair | 34,396.49 | 34,560.96 | **+164.47** (+0.48%) |
| Encap | 43,085.82 | 42,686.28 | −399.54 (−0.93%) |
| Decap | 30,535.55 | 29,956.09 | −579.45 (−1.90%) |

Compiler selection (GCC 15.2.0) is not the same for every build. It picked
`-O3` for Official 864, Official 1152 and caller-lazy 1152, but `-O2` for
caller-lazy 864. Raw `data`, `run.out`, fresh-launch output and the `measure`
ELFs stay local. The curated `stq-summary.json` and `metadata.json` (ELF and
source hashes, frequency policy, hygiene) are in
`results/native-lazy-qual-{official,candidate}-20260923/`.

### Fixed-ELF paired control (`fixed-elf-paired`)

Four fixed ELFs were built per parameter, all with the common O3GC wrapper
`bench/supercop/okc-o3gc.sh`: Official and candidate, each in normal and in
reversed placement (`install_reversed_placement.py`, which renames `ntt.s`,
`basemul.s`, `pack.s` and `ntt_caller_lazy.s`). `scripts/run_supercop_paired.py`
ran 16 ABBA/BAAB blocks, i.e. 64 fresh launches, per setting. ASLR was turned
off per process with `setarch -R`, never system-wide. The tables show the
paired mean delta (candidate − Official, cycles), the block-bootstrap 95% CI
(`summarize_supercop_paired.py`, 20,000 resamples) and the favourable blocks
out of 16.

NTRU+864:

| Setting | Keypair | Encap | Decap |
|---|---:|---:|---:|
| Normal, ASLR off | −220.06 [−268.63, −187.18] 16 | −260.88 [−406.75, −162.62] 16 | −214.24 [−311.60, −142.31] 16 |
| Normal, ASLR on | −194.71 [−241.94, −149.70] 16 | −220.89 [−290.99, −158.07] 15 | −187.18 [−217.91, −150.97] 15 |
| Reversed, ASLR off | −145.91 [−161.43, −133.03] 16 | −247.46 [−290.60, −198.34] 15 | −206.65 [−234.33, −176.07] 16 |
| Reversed, ASLR on | −128.46 [−154.89, −103.90] 16 | −238.41 [−327.06, −154.13] 15 | −202.69 [−246.51, −156.71] 15 |

All 12 NTRU+864 intervals lie below zero.

NTRU+1152:

| Setting | Keypair | Encap | Decap |
|---|---:|---:|---:|
| Normal, ASLR off | −504.69 [−1084.61, +82.23] 10 | −267.16 [−330.58, −196.95] 15 | −147.56 [−217.27, −58.49] 14 |
| Normal, ASLR on | −84.72 [−491.51, +322.97] 9 | −386.47 [−645.80, −222.69] 15 | −240.09 [−290.26, −191.68] 16 |
| Reversed, ASLR off | −522.38 [−1144.27, +51.70] 9 | −390.20 [−461.37, −320.43] 16 | −75.23 [−167.40, +49.36] 14 |
| Reversed, ASLR on | −746.23 [−1202.86, −304.29] 12 | −339.89 [−433.97, −221.54] 15 | −200.71 [−282.75, −99.09] 14 |

For NTRU+1152, 8 of 12 intervals lie below zero: all of Encap, three of
Decap and one of Keypair. The NTRU+1152 Keygen distribution is heavy-tailed
because it hits natural f/g BaseInv retries (40 and 45 per 100 keypairs in
Phase A).

ELF hashes, `nm`, section sizes and every launch record are in
`results/fixed-lazy-paired-20260923/manifest.json`. The per-ELF build records
are in `results/fixed-lazy-{official,candidate}-{normal,reversed}-20260923/`.

### Same-ELF complete-caller diagnostic

This diagnostic is not Native. It is the port of the 768 Round-5 bench:
`common/official_opt_lazy/bench/`, built with `make bench` (O3GC) and run by
`run_forward_caller_lazy_short.py`. It takes 9 fresh launches on CPU 1.
Values are pooled StQ2 differences, with favourable launches out of 9. Keygen
here includes the NIST KAT DRBG, so its absolute cycles are not comparable to
Native.

| Region | NTRU+864 | NTRU+1152 |
|---|---:|---:|
| `r` Forward | −92.93 (9/9) | −168.76 (9/9) |
| Keygen `f` Forward | −94.41 (9/9) | −171.48 (9/9) |
| Full Keygen | −170.58 (9/9) | −284.19 (7/9) |
| Full Encap | −106.57 (8/9) | −308.15 (9/9) |
| Full Decap | −223.29 (9/9) | −197.07 (9/9) |

### Decision

The rule is the one used for 768. An operation is a **robust research win**
only if its Native pooled delta is negative **and** all four paired 95% CIs
lie below zero. The decisions are also recorded in
`results/phase-b-summary-20260923.json` (`summarize_phase_b.py`) and in each
`STATUS.yml`.

| Op | NTRU+864 | NTRU+1152 |
|---|---|---|
| Keypair | **robust research win** | not robust: Native +164; 1/4 CIs below zero |
| Encap | **robust research win** | **robust research win** |
| Decap | not robust: Native +17.75, although 4/4 CIs are below zero | not robust: Native −579, but only 3/4 CIs below zero (reversed, ASLR off, crosses zero) |

How to read these results:

- The Forward saving itself is unambiguous in the same ELF: −93 cycles (864)
  and −169 cycles (1152) per Forward, 9/9 launches.
- At the KEM level, the O3GC fixed-ELF controls are consistently favourable.
  The Native pools are much smaller for 864, and for 864 Decap and 1152
  Keypair they are of the opposite sign.
- For 864, Native compiler selection gave the two implementations different
  optimisation levels (O3 against O2). The 864 Decap Native sign is therefore
  not attributable to the source change alone. It still fails the rule as
  written.
- None of this is a clean-production promotion. `promotion: none`, and
  `clean/` was not touched. A production package would need a separate review
  and a Native re-confirmation from its exact packaging. It should also get a
  larger Native sample (or a paired Native design) for 864 Decap and 1152
  Keypair/Decap.

### Reproduce Phase B

```sh
REPO=/home/nuc/src/ntru_plus-official-opt-864-1152
T=$REPO/ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/official_opt_lazy/tools
C=/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-NNN   # new, disposable
python3 $REPO/scripts/prepare_supercop.py --supercop-root /home/nuc/src/supercop-pristine-20260831 --campaign-root $C
(cd $C && taskset -c 1 ./do-part init; taskset -c 1 ./do-part crypto_stream chacha20; taskset -c 1 ./do-part crypto_rng)
for p in 864 1152; do
  E=$REPO/ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+$p/experiments/avx2_official_opt_001
  # (export already committed; to recreate: $T/export_caller_lazy_qualification.py --param $p --experiment $E --output-root <new dir>)
  python3 $T/install_qualification.py --param $p --campaign-root $C --export-root $E/qualification/avx2-officialopt-caller-lazy-qual001
  for pair in official:avx2 candidate:avx2-officialopt-caller-lazy-qual001; do
    python3 $T/phase_b_batch.py --result-dir $E/results/native-lazy-qual-${pair%%:*}-TAG --metadata metadata.json -- \
      python3 $REPO/scripts/run_supercop_benchmark.py --campaign-root $C --parameter $p --implementation ${pair#*:} \
      --cpu 1 --mode native-kem --fresh-launches 9 --require-frequency-control --result-dir {RESULT}
  done
done
# Fixed-ELF paired (per parameter p, experiment E, Q=avx2-officialopt-caller-lazy-qual001):
Q=avx2-officialopt-caller-lazy-qual001; R=$E/results
python3 $T/install_reversed_placement.py --param $p --campaign-root $C --candidate $Q
for spec in official:normal:avx2 candidate:normal:$Q official:reversed:avx2-reversed candidate:reversed:$Q-reversed; do
  role=${spec%%:*}; rest=${spec#*:}; place=${rest%%:*}; impl=${rest#*:}
  python3 $T/phase_b_batch.py --result-dir $R/fixed-lazy-$role-$place-TAG --metadata metadata.json -- \
    python3 $REPO/scripts/run_supercop_benchmark.py --campaign-root $C --parameter $p --implementation $impl \
    --cpu 1 --mode native-kem --fresh-launches 1 --compiler-wrapper $REPO/bench/supercop/okc-o3gc.sh \
    --require-frequency-control --result-dir {RESULT}
done
python3 $T/phase_b_batch.py --result-dir $R/fixed-lazy-paired-TAG --metadata manifest.json -- \
  python3 $REPO/scripts/run_supercop_paired.py \
  --official $R/fixed-lazy-official-normal-TAG/measure --candidate $R/fixed-lazy-candidate-normal-TAG/measure \
  --official-reversed $R/fixed-lazy-official-reversed-TAG/measure --candidate-reversed $R/fixed-lazy-candidate-reversed-TAG/measure \
  --cpu 1 --compiler-recipe O3GC --output {RESULT}
python3 $REPO/scripts/summarize_supercop_paired.py --campaign $R/fixed-lazy-paired-TAG --parameter $p
# Same-ELF: (cd $E && make check bench SUPERCOP_CAMPAIGN=$C) then
#   phase_b_batch.py --result-dir $E/results/officialopt-forward-caller-lazy-serious-TAG --metadata metadata.json -- \
#     python3 $T/run_forward_caller_lazy_short.py --param $p --experiment $E --launches 9 --skip-build --result-dir {RESULT}
# Summary and decision: python3 $T/summarize_phase_b.py --param $p --experiment $E --tag TAG
```

## Phase B follow-up (2026-09-23)

The follow-up targets the two open Phase B questions: 864 Native, where the
compilers differed, and the 1152 Keypair retry tail. It used the same host,
CPU 1, unchanged controls and campaign `-001`. Every timing batch ran under
`phase_b_batch.py`. **All 9 follow-up batches were accepted on attempt 0**:
pre-batch load was 0.12-0.48 and there were no foreign CPU users. Each
batch took 5.4-5.8 s, so the 5 s in-batch sampling covered it at most once;
the 3 s before/after snapshots apply as in Phase B.

Evidence labels used below:
- **measured**: new timing.
- **derived**: new analysis of timing that already exists.
- **estimated**: model or simulation.

### NTRU+864 Native with a fixed compiler (measured)

**How the compiler list was restricted.** SUPERCOP takes its C compiler list
from `bench/nucpromtlhcubinucai1ummsb209/bin/okc-amd64`, which `do-part init`
generated from `okcompilers/c`. That file has sha256 `82f1eea7…98b3`, mode 755,
and four lines after `#!/bin/sh`:

```
2: echo 'gcc -march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -gdwarf-4 -Wall'   <- Official 864 (Phase B)
3: echo 'gcc -march=native -mtune=native -Os -fwrapv -fPIC -fPIE -gdwarf-4 -Wall'
4: echo 'gcc -march=native -mtune=native -O2 -fwrapv -fPIC -fPIE -gdwarf-4 -Wall'   <- candidate 864 (Phase B)
5: echo 'gcc -march=native -mtune=native -O -fwrapv -fPIC -fPIE -gdwarf-4 -Wall'
```

Neither the campaign nor `okcompilers/c` was edited by hand. The restriction
used the existing `run_supercop_benchmark.py --compiler-wrapper` mechanism.
For the duration of one `do-part` it copies a single-entry list over
`okc-amd64`, and it restores the original bytes and mode in a `finally`. The
two lists are committed:
- `common/official_opt_lazy/compilers/okc-native-gcc-O3-only.sh` (line 2 only)
- `common/official_opt_lazy/compilers/okc-native-gcc-O2-only.sh` (line 4 only)

Their output was diffed against lines 1 and 3 of the original list's output
and matched. After every batch, `okc-amd64` was re-hashed and was still
`82f1eea7…98b3`. Each `metadata.json` records `compiler_policy: fixed-common`
and the wrapper path and sha256. `crypto_kem/measure.c` was unmodified
(`7490844f…0174`). Each implementation was enabled alone and got 9 fresh
launches.

**The builds are reproducible.** The fixed-O3 Official ELF (`f3cf0a37…`) is
byte-identical to Phase B's Official Native ELF. The fixed-O2 candidate ELF
(`b6654906…`) is byte-identical to Phase B's candidate Native ELF. The other
two ELFs are new: O3 candidate `b11aa429…` and O2 Official `7eadf7f3…`.

Primary runs (tag `20260923`, Official first) and a replicate (tag
`20260923r2`, candidate first). Each cell is candidate − Official for pooled
StQ1 / StQ2 / StQ3 (864 observations each). *fav* is the number of candidate
launches below the Official launch median, out of 9, followed by the 9×9
pairwise count of candidate launch < Official launch.

| Compiler | Op | Primary StQ1 / **StQ2** / StQ3 | fav | Replicate StQ1 / **StQ2** / StQ3 | fav |
|---|---|---|---|---|---|
| O3 only | Keypair | −234.2 / **−299.8** / −477.2 | 9/9, 81/81 | −224.4 / **−291.3** / −323.2 | 9/9, 81/81 |
| O3 only | Encap | +28.8 / **+85.4** / +148.1 | 2/9, 33/81 | −13.3 / **+5.9** / +55.4 | 7/9, 48/81 |
| O3 only | Decap | +43.3 / **−0.8** / −78.4 | 2/9, 27/81 | +42.5 / **+8.0** / −64.9 | 1/9, 29/81 |
| O2 only | Keypair | −80.1 / **−133.4** / −141.1 | 9/9, 81/81 | −98.8 / **−135.8** / +220.8 | 7/9, 65/81 |
| O2 only | Encap | −243.4 / **−218.9** / −243.3 | 9/9, 75/81 | −209.9 / **−143.4** / +263.1 | 7/9, 64/81 |
| O2 only | Decap | −101.8 / **−71.6** / −44.5 | 7/9, 63/81 | −70.7 / **−24.8** / −29.0 | 8/9, 65/81 |

Pooled StQ2 over both runs (derived; identical ELFs, 1,728 observations per
role, `native-fixedcc-summary-pooled.json`):

| Compiler | Keypair | Encap | Decap |
|---|---:|---:|---:|
| O3 only | −295.27 | +49.20 | +3.59 |
| O2 only | −138.32 | −185.20 | −48.06 |

Phase B's default-selection Native pairs the O2 candidate ELF with the O3
Official ELF. Those same two ELFs were re-measured twice here (derived from
the fixed-compiler runs):

| Op | Phase B | Primary | Replicate |
|---|---:|---:|---:|
| Keypair | −90.42 | −143.86 | −83.81 |
| Encap | −59.45 | +1.93 | −46.74 |
| Decap | +17.75 | −53.60 | −40.25 |

Phase B's Decap +17.75 did not reproduce with the same binaries. The
run-to-run spread of a 9-launch pooled delta is about ±70 cycles.

**Robust-research-win rule** (Native pooled StQ2 < 0 AND all 4 fixed-ELF
paired CIs < 0; the paired evidence is unchanged at 4/4 for all 864 ops):

| Op | Fixed O2 (candidate's Phase B compiler) | Fixed O3 (Official's Phase B compiler) |
|---|---|---|
| Keypair | **qualifies** (−133 / −136, both runs) | **qualifies** (−300 / −291, 9/9 launches) |
| Encap | **qualifies** (−219 / −143) | fails (+85 / +6) |
| Decap | **qualifies** (−72 / −25, 7/9 and 8/9) | not robust: −0.83 passes the sign test in the primary run only; the replicate is +7.96, the pool +3.59 and 1-2/9 launches are favourable. Read as zero |

Conclusion for 864 Decap: under a **controlled-compiler Native with the O2
entry**, Decap now meets the rule, in two independent runs. Under the O3 entry
it shows no Native gain. **This is a controlled-compiler Native. It is not
SUPERCOP's default compiler selection**, which picks O3 for Official and O2
for the candidate. With default selection, the three measurements of 864
Decap are +17.75, −53.60 and −40.25. Encap behaves the same way: it is a
clear win at O2 and zero at O3. The O3-built candidate loses the Encap/Decap
gain that the O3GC fixed-ELF controls show. Its text layout after the Forward
moves by 0x60-0x80 bytes, but the O2 build moves by the same amount. The
cause was not investigated.

Evidence: `NTRU+864/.../results/native-fixedcc-{O3,O2}-{official,candidate}-20260923{,r2}/`,
`native-fixedcc-summary-20260923{,r2}.json` and `native-fixedcc-summary-pooled.json`.

### NTRU+1152 Keypair: controlling the BaseInv retry tail

**Step 2a: call-index pairing is impossible (analysis).** `crypto_kem/measure`
is linked with `fastrandombytes`, not `knownrandombytes` (`do-part` line 420:
`measurelibs="$lib/$abi/fastrandombytes.o $libs"`). `fastrandombytes` keys its
ChaCha20 RNG once per process from `kernelrandombytes`. The i-th keypair call
therefore gets different coins in every fresh launch, for both
implementations. The zero-key `knownrandombytes` is linked only into the
try/checksum binaries. This was confirmed empirically: 274 Native and
fixed-ELF raw launch files contain **274 distinct** retry sequences.
Candidate_i − official_i is therefore not a matched pair, and no replay can
make it one.

The retry count is still observed exactly for every timed call. measure.c
logs `keypair_randomcalls` next to `keypair_cycles`, and both `kem.c` and
`src/kem_lazy.c` call `randombytes(coins, 32)` exactly once per *f* attempt
and once per *g* attempt. So retries = randomcalls − 2 and Forward calls =
randomcalls. No instrumented replay was needed.

**Why Native pooled StQ2 is composition-dominated (derived).** Each retry adds
about 5.9 k cycles. Official medians by stratum are 31.3 k (r=0), 37.2 k (r=1)
and 43.1 k (r=2). The share of keypairs with no retry is about 0.51, so StQ2's
37.5-62.5% window lies right on the r=0/r=1 boundary. In Phase B, the Official
pool had 52.2% r=0 keypairs and the candidate pool 49.65%, a difference of 22
of 864, about 1σ. The StQ2 window held 120 r=0 + 96 r=1 observations for
Official and 100 + 116 for the candidate. The pooled medians fell in different
clusters (33,063.5 against 36,490.5). That composition shift alone moves StQ2
by about +540 cycles and hides the real saving. The result is the Phase B
Native +164.47.

**Retry-stratified re-analysis of the existing raw data (derived, no new
timing).** Tool: `tools/analyze_keypair_retry_strata.py`, output
`keypair-retry-strata-20260923.json`.

Native (independent pools; CI from 2,000 launch resamples within each role):

| Retries | n (off / cand) | StQ2 Official | StQ2 candidate | Delta [95% CI] |
|---|---|---:|---:|---:|
| 0 | 451 / 429 | 31,460 | 31,084 | **−376.2** [−524.3, −211.4] |
| 1 | 254 / 269 | 37,456 | 36,917 | **−539.7** [−709.9, −373.4] |
| 2 | 102 / 105 | 43,372 | 42,691 | **−681.3** [−879.1, −481.6] |
| 3+ | 57 / 61 | 50,498 | 49,523 | −975.8 [−3266, +1965] |

Fixed-ELF paired (O3GC): the per-block median(candidate) − median(official)
within each stratum, meaned over 16 blocks, with the block-bootstrap 95% CI
and favourable blocks:

| Setting | r=0 | r=1 | r=2 |
|---|---:|---:|---:|
| Normal, ASLR off | −250.4 [−280.6, −219.4] 16 | −403.5 [−467.1, −342.9] 16 | −534.8 [−620.8, −443.0] 16 |
| Normal, ASLR on | −203.8 [−295.2, −61.7] 15 | −365.2 [−461.4, −212.2] 15 | −514.7 [−638.9, −338.6] 15 |
| Reversed, ASLR off | −319.5 [−339.5, −297.0] 16 | −482.6 [−505.3, −459.5] 16 | −625.4 [−658.2, −588.2] 16 |
| Reversed, ASLR on | −263.7 [−370.0, −109.7] 15 | −466.9 [−517.4, −414.9] 16 | −506.4 [−663.0, −281.1] 14 |

All 12 stratum-matched paired CIs for r = 0-2 lie below zero. The r=3+
stratum (2-4 observations per launch) is too sparse; its CIs are wide and
cross zero in 3 of 4 settings.

**Step 2b: seed-matched paired Keypair harness (measured; supercop-derived
diagnostic, not Native).** Harness `bench/bench_keypair_seedmatched.c`
(`make bench-keypair`), runner `tools/run_keypair_seedmatched.py`.
- **Build:** one ELF holds both KEMs through the namespaced
  `official_{ref,lazy}_keypair` entries, with the same O3GC recipe and objects
  as the same-ELF bench. A second ELF links the two KEM objects in the
  opposite order.
- **Coins:** each iteration derives one coin stream, SHAKE256(seed ‖ iter),
  outside the timed region. A local `randombytes()` serves it by memcpy.
- **Timing:** four keypairs per iteration, ABBA on even iterations and BAAB
  on odd ones, timed with SUPERCOP's `cpucycles` (default-perfevent).
- **Checks:** outside the timing, the harness traps unless all four calls made
  the same number of randombytes calls and produced identical pk/sk. No trap
  occurred.
- **Runs:** 12 fresh processes on CPU 1 (6 per ELF), 5,000 iterations each
  plus 32 warm-up, with distinct seeds `20260923000+k`.
- **Statistics:** per-iteration delta d = (lazy₁ + lazy₂ − off₁ − off₂)/2.
  CIs are two-stage bootstrap (processes, then iterations; 1,000 resamples).

| Subset | n | Median d [95% CI] | Mean d [95% CI] | d < 0 | Launches |
|---|---:|---:|---:|---:|---:|
| **All** | 60,000 | **−391.0** [−396.5, −384.5] | −419.5 [−444.2, −395.1] | 97.1% | 12/12 |
| Normal link order | 30,000 | −395.0 [−399.5, −390.0] | −432.8 [−471.8, −389.4] | 97.4% | 6/6 |
| Swapped link order | 30,000 | −387.0 [−394.5, −377.5] | −406.3 [−426.5, −383.0] | 96.9% | 6/6 |
| r=0 (2 Forwards) | 30,691 | −293.0 [−297.5, −289.0] | −292.1 [−317.4, −263.0] | 95.9% | 12/12 |
| r=1 (3) | 17,580 | −453.0 [−459.0, −444.5] | −457.1 [−486.2, −425.4] | 98.3% | 12/12 |
| r=2 (4) | 7,399 | −606.5 [−617.5, −593.0] | −607.0 [−670.0, −545.7] | 98.8% | 12/12 |
| r=3 (5) | 2,848 | −748.8 [−765.0, −732.0] | −730.3 [−882.7, −576.4] | 98.2% | 12/12 |
| r≥4 | 1,482 | −939.8 [−972.5, −910.0] | −1079.7 [−1269.1, −957.3] | 98.5% | 12/12 |

The mean retry count per keypair was 0.79. The saving is proportional to the
number of Forward calls. A fit on the stratum medians gives **−152 cycles per
Forward** with intercept +7; a fit at iteration level gives −163 per Forward
with intercept +36. This matches the same-ELF per-Forward price (−169/−171).
The retry-free cost is 2 Forwards, about −300 cycles; the expected cost per
keypair at the natural retry rate is about −390 to −420. The first timed call
of each quadruple is 29 cycles slower (median), and ABBA/BAAB cancels this.

**Pooled-StQ2 noise (estimated by resampling the harness observations).**
This compares two independent pools of Keypair observations, each 96 per
launch:

| Launches per role | SD of StQ2 delta | P(delta > 0) given the real saving |
|---:|---:|---:|
| 9 (Phase B design) | ≈ 545 | ≈ 0.27 |
| 36 | ≈ 255 | ≈ 0.09 |
| 81 | ≈ 166 | ≈ 0.01 |

**Conclusion for 1152 Keypair.** The saving is real. In the seed-matched
diagnostic it is about 390 cycles per keypair (median; mean 420), about 1.1%
of the Official 34.4 k StQ2. It is about 150-165 cycles per Forward and
scales with the retry count. Stratum by stratum, it is also visible in the
existing *Native* raw data (r=0 −376, r=1 −540, r=2 −681, all CIs < 0), and
all 12 stratum-matched fixed-ELF CIs (r = 0-2) are below zero.

It does **not** meet the Phase B robust-research-win rule as written. The
unstratified Native pooled delta is +164.47, and only 1 of 4 unstratified
paired CIs is below zero. With 9 launches per role that rule cannot resolve
this operation: composition noise, SD ≈ 545, is larger than the effect. The
evidence therefore belongs to a different class: *retry-stratified Native +
retry-stratified fixed-ELF paired + seed-matched paired diagnostic*. Under a
stratified version of the rule, which asks for Native per-stratum deltas < 0
and all paired per-stratum CIs < 0 for every well-populated stratum
(r = 0-2), 1152 Keypair qualifies. A pooled-Native confirmation would need
about 80 launches per role. That was not run.

### Decision after the follow-up

| Op | NTRU+864 | NTRU+1152 |
|---|---|---|
| Keypair | robust research win (unchanged; also under fixed O3 and fixed O2) | not robust under the Phase B rule. **Stratified-evidence win**: seed-matched −391 [−397, −385]; Native r=0-2 all < 0; paired 12/12 stratum CIs < 0 |
| Encap | robust research win (unchanged; fixed O2 qualifies, fixed O3 does not) | robust research win (unchanged) |
| Decap | not robust under default selection (+17.75, not reproduced: −53.6, −40.3). **Qualifies under controlled-compiler Native, O2 entry** (−72, −25). No gain under the O3 entry | not robust (unchanged; not re-examined) |

`promotion: none`, and `clean/` was not touched.

### Reproduce the follow-up

```sh
REPO=/home/nuc/src/ntru_plus-official-opt-864-1152
A=$REPO/ntruplus-ntt-Optimized/Additional_Implementation/avx2
T=$A/common/official_opt_lazy/tools; W=$A/common/official_opt_lazy/compilers
C=/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001
E=$A/NTRU+864/experiments/avx2_official_opt_001
for cc in O3 O2; do for pair in official:avx2 candidate:avx2-officialopt-caller-lazy-qual001; do
  python3 $T/phase_b_batch.py --result-dir $E/results/native-fixedcc-$cc-${pair%%:*}-TAG --metadata metadata.json -- \
    python3 $REPO/scripts/run_supercop_benchmark.py --campaign-root $C --parameter 864 --implementation ${pair#*:} \
    --cpu 1 --mode native-kem --fresh-launches 9 --compiler-wrapper $W/okc-native-gcc-$cc-only.sh \
    --require-frequency-control --result-dir {RESULT}
done; done   # replicate: same with TAGr2 and the pair order reversed
python3 $T/summarize_fixed_compiler_native.py --param 864 --experiment $E --tag TAG
python3 $T/summarize_fixed_compiler_native.py --param 864 --experiment $E --pool TAG TAGr2
E=$A/NTRU+1152/experiments/avx2_official_opt_001
python3 $T/analyze_keypair_retry_strata.py --experiment $E --tag 20260923    # Phase B raw
(cd $E && make check bench-keypair)
python3 $T/phase_b_batch.py --result-dir $E/results/keypair-seedmatched-TAG --metadata metadata.json -- \
  python3 $T/run_keypair_seedmatched.py --param 1152 --experiment $E --skip-build --result-dir {RESULT}
python3 $T/run_keypair_seedmatched.py --param 1152 --experiment $E --result-dir $E/results/keypair-seedmatched-TAG --summarize
```

## Extended Native and ASLR-on paired (2026-09-23)

### Methodology decision (applies from here on)

- **ASLR on only.** Production runs keep the kernel default
  (`randomize_va_space=2`). No ASLR-off setting was run and `setarch -R` was
  not used. The Phase B and follow-up ASLR-off rows above remain as history.
- **Normal placement + ASLR on is the primary evidence.** This follows the
  reference practice: SUPERCOP compiles and links the implementation
  directory normally, times many fresh processes and reports StQ; mlkem-native
  times in a single process (50 warm-ups, 300 iterations per test, 500 tests,
  median) with no placement or ASLR control. Neither controls placement.
- **Reversed placement + ASLR on is a secondary robustness check only.** As in
  `bench/mlkem-batch.md`, the favourable placement is never used as the
  headline.
- **Updated decision rule.** An operation is a **robust research win** iff
  (i) the extended Native pooled StQ2 delta (default SUPERCOP compiler
  selection) is negative, and (ii) the fixed-ELF paired 95% CI with normal
  placement and ASLR on lies below zero. The reversed ASLR-on result is
  reported alongside and is flagged, not failed, if it disagrees. This
  replaces the Phase B rule (Native < 0 and all four paired CIs < 0).

### Design (measured)

- **Native:** Official `avx2` against `avx2-officialopt-caller-lazy-qual001`
  in campaign `-001`, unmodified `crypto_kem/measure.c` (`7490844f…0174`),
  default compiler selection (no wrapper; `okc-amd64` still `82f1eea7…98b3`).
  81 fresh launches per implementation, as 9 rounds of one 9-launch batch
  per implementation. Round k ran Official then candidate for odd k and
  candidate then Official for even k (A,B,B,A,A,B,…). Every batch is a full
  `run_supercop_benchmark.py --mode native-kem` call, so SUPERCOP rebuilt and
  re-selected the compiler in each batch. Pooled StQ over 7,776 observations
  per role and operation. The 95% CI of the pooled delta is from resampling
  launches within each role (2,000 resamples). These are independent pools,
  not paired estimates.
- **Paired:** the Phase B O3GC fixed ELFs, unchanged (hashes re-checked
  against their `metadata.json`). `run_paired_aslr_on.py` is
  `scripts/run_supercop_paired.py` restricted to one placement, ASLR on and 48
  ABBA/BAAB blocks (192 fresh launches). It was run once per placement.
  Summary by the unchanged `scripts/summarize_supercop_paired.py`: per-block
  mean of StQ2(candidate) − StQ2(Official), block-bootstrap 95% CI (20,000
  resamples), favourable blocks.
- **Hygiene:** all 39 batches (36 Native, 3 paired) were accepted on attempt
  0; none was contaminated or re-run. Pre-batch load was 0.31-0.50, with no
  sustained foreign CPU user. Native batches took 15.9-16.6 s. Paired
  batches took 1.9-2.4 s, shorter than one 5 s window, so only the
  before/after snapshots apply.

### SUPERCOP compiler selection per batch (measured)

SUPERCOP picks the fastest compiler at build time, and the pick was **not
stable** from batch to batch. Each compiler always produced the same ELF.

| Batch | 1152 Official | 1152 candidate | 864 Official | 864 candidate |
|---:|---|---|---|---|
| 1 | O3 | O3 | O3 | O2 |
| 2 | O3 | O3 | O3 | **O3** |
| 3 | **O2** | O3 | O3 | O2 |
| 4 | O3 | **O2** | O3 | O2 |
| 5 | O3 | O3 | O3 | O2 |
| 6 | O3 | O3 | O3 | O2 |
| 7 | O3 | O3 | O3 | O2 |
| 8 | **O2** | O3 | O3 | **O3** |
| 9 | O3 | O3 | O3 | O2 |

ELFs: 1152 Official O3 `16cab433…` (= Phase B), O2 `bbd7b998…`; candidate O3
`0cfa12ab…` (= Phase B), O2 `45c87edb…`. 864 Official O3 `f3cf0a37…`
(= Phase B); candidate O2 `b6654906…` (= Phase B), O3 `b11aa429…` (= the
follow-up fixed-O3 ELF). Phase B saw O3/O3 for 1152 and O3/O2 for 864; that
was the majority pick here as well (6/9 and 7/9 batches).

### NTRU+1152 extended Native (measured)

Candidate − Official, pooled over 81 launches per role:

| Op | StQ1 | **StQ2** [95% CI] | StQ3 | StQ2 % | Cand. launches < Off. median |
|---|---:|---:|---:|---:|---:|
| Keypair | −396.3 | **−470.6** [−784.5, −167.8] | −467.2 | −1.36% | 54/81 |
| Encap | −648.9 | **−486.6** [−552.4, −412.6] | −443.9 | −1.13% | 74/81 |
| Decap | −499.7 | **−570.7** [−600.2, −531.5] | −434.6 | −1.87% | 81/81 |

Absolute pooled StQ2 (Official → candidate): Keypair 34,643.5 → 34,172.8;
Encap 43,098.8 → 42,612.2; Decap 30,530.0 → 29,959.3.

Per-batch StQ2 deltas (9 launches per side each):

| Op | b1 | b2 | b3 | b4 | b5 | b6 | b7 | b8 | b9 | mean | SD | neg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Keypair | −538 | −468 | +23 | +35 | −586 | −422 | −464 | −745 | −1012 | −464 | 333 | 7/9 |
| Encap | −631 | −684 | −472 | −406 | −690 | −523 | −362 | −221 | −255 | −472 | 176 | 9/9 |
| Decap | −624 | −624 | −418 | −495 | −606 | −622 | −656 | −242 | −514 | −534 | 135 | 9/9 |

**Keypair retry composition** (retries = `keypair_randomcalls` − 2, per timed
call):

| Retries | Official n (share) | Candidate n (share) |
|---|---:|---:|
| 0 | 3,996 (51.4%) | 4,010 (51.6%) |
| 1 | 2,302 (29.6%) | 2,266 (29.1%) |
| 2 | 957 (12.3%) | 938 (12.1%) |
| 3+ | 521 (6.7%) | 562 (7.2%) |
| mean retries | 0.781 | 0.786 |

The r=0 counts differ by 14 (binomial SD of the difference ≈ 62), against 22
of 864 in Phase B. The StQ2 window holds 1,020 r=0 + 924 r=1 observations
(Official) and 1,014 + 930 (candidate), so both pooled StQ2 values now sit in
the same place on the r=0/r=1 boundary. Per-batch r=0 shares range over
0.49-0.53 (Official) and 0.48-0.53 (candidate).

Retry-stratified Native deltas (derived from these runs; CI by resampling
launches within each role, 2,000 resamples):

| Retries | n (off / cand) | StQ2 delta [95% CI] | Median delta [95% CI] |
|---|---|---:|---:|
| 0 | 3,996 / 4,010 | **−396.0** [−427.1, −364.0] | −395.0 [−427.0, −366.5] |
| 1 | 2,302 / 2,266 | **−549.6** [−586.4, −514.0] | −549.5 [−586.0, −514.0] |
| 2 | 957 / 938 | **−692.1** [−748.5, −635.1] | −682.0 [−748.5, −632.0] |
| 3+ | 521 / 562 | −866.3 [−1556.0, −162.0] | −955.5 [−1694.0, −214.0] |

All four strata, including 3+, now have CIs below zero. The step per retry
(about −150 cycles) matches the seed-matched diagnostic (−152 per Forward).

**Against the simulation (estimated, follow-up).** The follow-up predicted an
SD of the pooled Keypair StQ2 delta of ≈ 545 at 9 launches per role and
≈ 166 at 81 (the request quoted ≈ 180), with P(delta > 0) ≈ 0.01 at 81. Here
the SD of the nine 9-launch batch deltas is 333, and the launch-resampling
SD of the 81-launch pooled delta is 159 (333/√9 = 111 from the batch
spread). The 81-launch result, −470.6, is within about 0.5 SD of the seed-matched
−391/−420 expectation, and 2 of 9 single batches are still positive, as the
9-launch noise predicts.

Batches grouped by the measured ELF pair (derived): O3/O3 (6 batches) −588.6 /
−514.5 / −615.9; Official O2 vs candidate O3 (2 batches) −361.1 / −363.5 /
−330.5; Official O3 vs candidate O2 (1 batch) +34.7 / −406.5 / −495.2
(Keypair / Encap / Decap). These subsets are small and are not decision inputs.

### NTRU+1152 fixed-ELF paired, ASLR on (measured)

Mean delta [block-bootstrap 95% CI], favourable blocks out of 48:

| Setting | Keypair | Encap | Decap |
|---|---:|---:|---:|
| **Normal, ASLR on (primary)** | **−474.14** [−748.32, −202.48] 33/48 | **−312.90** [−400.37, −229.39] 45/48 | **−199.03** [−248.77, −149.36] 44/48 |
| Reversed, ASLR on (secondary) | −664.58 [−999.53, −325.69] 35/48 | −318.59 [−400.73, −225.75] 44/48 | −267.13 [−301.45, −234.29] 46/48 |

All six intervals lie below zero. Keypair retry-stratified (derived, per-block
median delta, mean over blocks with ≥ 3 observations per side):

| Setting | r=0 | r=1 | r=2 | r=3+ |
|---|---:|---:|---:|---:|
| Normal, ASLR on | −235.7 [−279.3, −194.4] 46/48 | −386.7 [−440.1, −336.0] 48/48 | −561.4 [−605.7, −518.9] 48/48 | −817.9 [−1489.6, −160.0] 33/48 |
| Reversed, ASLR on | −311.9 [−356.8, −268.2] 47/48 | −457.6 [−511.7, −410.9] 47/48 | −623.6 [−687.9, −551.8] 46/48 | −1676.4 [−2428.3, −958.9] 39/48 |

### NTRU+864 extended Native (measured)

| Op | StQ1 | **StQ2** [95% CI] | StQ3 | StQ2 % | Cand. launches < Off. median |
|---|---:|---:|---:|---:|---:|
| Keypair | −88.1 | **−103.0** [−127.8, −78.3] | −122.4 | −0.43% | 75/81 |
| Encap | −132.0 | **−92.7** [−149.3, −42.9] | −184.9 | −0.28% | 63/81 |
| Decap | −70.0 | **−24.0** [−55.9, +4.0] | −81.8 | −0.10% | 49/81 |

Absolute pooled StQ2 (Official → candidate): Keypair 23,751.7 → 23,648.7;
Encap 32,957.7 → 32,865.0; Decap 23,676.1 → 23,652.1.

| Op | b1 | b2 | b3 | b4 | b5 | b6 | b7 | b8 | b9 | mean | SD | neg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Keypair | −130 | −250 | −63 | −77 | −117 | −48 | −64 | −204 | −80 | −115 | 70 | 9/9 |
| Encap | −155 | −142 | +68 | −220 | −217 | −137 | +48 | −89 | −52 | −99 | 104 | 7/9 |
| Decap | −92 | +16 | −35 | −16 | −18 | −58 | −149 | +45 | −53 | −40 | 58 | 7/9 |

No natural retries occurred for 864 (all 7,776 keypairs per side had r=0).
Grouped by measured ELF pair (derived): Official O3 vs candidate O2
(7 batches) −82.4 / −89.2 / −57.4; O3 vs candidate O3 (batches 2 and 8)
−225.7 / −107.6 / **+29.6** (Keypair / Encap / Decap). The two positive
Decap batches are exactly the two where SUPERCOP picked O3 for the
candidate. This repeats the follow-up finding that the O3-built 864
candidate shows no Native Decap gain. The Decap pool is negative, but its
launch-resampling CI reaches +4.0 and only 49/81 launches are favourable.

### NTRU+864 fixed-ELF paired, normal placement, ASLR on (measured)

| Setting | Keypair | Encap | Decap |
|---|---:|---:|---:|
| **Normal, ASLR on (primary), 48 blocks** | **−209.63** [−227.42, −191.25] 47/48 | **−176.15** [−230.95, −110.44] 43/48 | **−222.30** [−249.88, −194.96] 46/48 |
| Reversed, ASLR on (secondary; Phase B, 16 blocks) | −128.46 [−154.89, −103.90] 16/16 | −238.41 [−327.06, −154.13] 15/16 | −202.69 [−246.51, −156.71] 15/16 |

The reversed row is the existing Phase B ASLR-on result; reversed placement
was not re-run at 48 blocks for 864.

### Decision under the updated rule

| Op | NTRU+864 | NTRU+1152 |
|---|---|---|
| Keypair | **robust research win**: Native −103.0; normal CI [−227, −191]; reversed agrees | **robust research win**: Native −470.6; normal CI [−748, −202]; reversed agrees |
| Encap | **robust research win**: Native −92.7; normal CI [−231, −110]; reversed agrees | **robust research win**: Native −486.6; normal CI [−400, −229]; reversed agrees |
| Decap | **robust research win (marginal Native)**: Native −24.0, but its CI [−55.9, +4.0] crosses zero, the pool is 49/81 favourable, and the O3-built candidate batches are positive; normal CI [−250, −195]; reversed agrees | **robust research win**: Native −570.7 (81/81 launches); normal CI [−249, −149]; reversed agrees |

No reversed-placement flag was raised: all reversed ASLR-on CIs lie below
zero. 864 Decap meets the rule as written; its Native margin depends on
SUPERCOP picking O2 for the candidate, which it did in 7 of 9 builds. The
change from the Phase B decisions (864 Decap, 1152 Keypair and Decap not
robust) comes from two things. The Native samples are 9 times larger. The
rule no longer asks for ASLR-off or reversed-placement CIs; the one CI that
had crossed zero (1152 Decap) was reversed + ASLR off. `promotion: none`,
and `clean/` was not touched.

Evidence: `results/native-ext-{official,candidate}-b{1..9}-20260923x/`,
`results/paired-aslr-on-{normal,reversed}-20260923x/` (864: normal only) and
`results/extended-summary-20260923x.json` for each parameter.

### Reproduce the extended runs

```sh
REPO=/home/nuc/src/ntru_plus-official-opt-864-1152
A=$REPO/ntruplus-ntt-Optimized/Additional_Implementation/avx2; T=$A/common/official_opt_lazy/tools
C=/home/nuc/src/supercop-campaign-lazy-864-1152-20260923-001
TAG=20260923x
for p in 1152 864; do   # strictly sequential; nothing else pinned to CPU 1
  E=$A/NTRU+$p/experiments/avx2_official_opt_001; R=$E/results
  python3 $T/run_extended_native.py --param $p --experiment $E --campaign-root $C --tag $TAG   # 9 rounds x 2 batches, ABBA/BAAB
  for place in normal reversed; do   # 864 ran normal only
    python3 $T/phase_b_batch.py --result-dir $R/paired-aslr-on-$place-$TAG --metadata manifest.json -- \
      python3 $T/run_paired_aslr_on.py --official $R/fixed-lazy-official-$place-20260923/measure \
      --candidate $R/fixed-lazy-candidate-$place-20260923/measure --placement $place --cpu 1 --blocks 48 \
      --compiler-recipe O3GC --output {RESULT}
    python3 $REPO/scripts/summarize_supercop_paired.py --campaign $R/paired-aslr-on-$place-$TAG --parameter $p
  done
  python3 $T/summarize_extended.py --param $p --experiment $E --tag $TAG
done
```

## NTRU+864 layout-fused codec (Option A, 2026-09-23)

A second NTRU+864 candidate, `avx2-officialopt-lazy-codec-864-exp001`, stacks
a layout-fused `poly_tobytes`/`poly_frombytes` on the caller-lazy Forward
above. **This is Phase A plus a same-ELF diagnostic. There was no SUPERCOP
campaign, Native was not measured, and no host control was changed.** The
lazy-only candidate is unchanged and still builds and passes `make check`. The
new rules live in the experiment's `codec.mk`, which only the NTRU+864
Makefile includes, so `lazy.mk` and NTRU+1152 are untouched.

| File (in `NTRU+864/experiments/avx2_official_opt_001/`) | Role |
|---|---|
| `tools/generate_codec_fused.py` | generator (with `--check`), derived from `upstream/supercop-avx2/pack.s` |
| `asm/ntruplus864_officialopt_codec_fused.s` | generated kernels `ntruplus864_officialopt_{tobytes,frombytes}_fused` |
| `src/kem_lazy_codec.c` | candidate KEM: preprocessor overlay of `src/kem_lazy.c` that binds `poly_tobytes`/`poly_frombytes` to the fused kernels |
| `src/kem_codec.c` | control (codec only): the same overlay on the unmodified Official `kem.c` |
| `tests/test_codec_fused.c` | codec differential |
| `tools/audit_codec_fused.py` | linked-ELF audit |
| `bench/bench_codec_fused.c`, `tools/run_codec_fused_diag.py`, `tools/run_codec_keypair_seedmatched.py` | diagnostics |

### What Official does

`poly_tobytes` calls `poly_ntt_pack`, which freezes each coefficient to `[0,q)`
and converts the internal 6-way layout (per 96-coefficient block, register `r`
lane `l` holds coefficient `6l+r`) to natural order. It writes the result to a
1728-byte stack `tmp`. `poly_tobytes_raw` then reloads it and does a 4-way SoA
transpose, 12-bit packing and byte arrangement: 13 blocks of 64 coefficients
plus a 32-coefficient xmm tail. `poly_frombytes` does the reverse. The
reversed path also writes `r` twice, since `poly_ntt_unpack` works in place.

The two 128-bit-lane permutation stages that meet at the natural-order image
compose into a single one. In pack's pre-permute registers
`p_k = [H_k | H_{k+6}]` (with `H_i` = coefficients `8i..8i+7`), the input
tobytes needs is `t_i = [G_i | G_{i+4}]`, and each `t_i` is one `vperm2i128`
(or one `vinserti128`) of two `p_k` halves. The 96- and 64-coefficient blocks
realign every 192 coefficients.

### Design

* **Arithmetic is unchanged.** The kernels keep Official's per-lane freeze
  (`vpmulhrsw v, vpmullw q, vpsubw; vpsraw 15, vpand q, vpaddw`), 12-bit
  pack/unpack and the q-1 canonical check. Every in-lane shuffle keeps the same
  immediate.
* **Cross-lane data movement:**
  - The pack and tobytes permutes are composed. So are the frombytes and
    unpack permutes. That gives 12 instead of 24 `vperm2i128` per 192
    coefficients.
  - The byte-side permutes are folded into memory access. tobytes stores the
    six 16-byte halves that `pack.s:66-72` would permute
    (`vmovdqu xmm` / `vextracti128 m128`). frombytes builds `pack.s:154-156`'s
    half pairs from 16-byte loads and `vinserti128 m128`.
* **Blocking:** four 192-coefficient super-iterations (2 layout blocks = 3
  codec blocks), then a final 96 coefficients (one codec block and the
  32-coefficient tail). The tobytes tail runs the ymm body on the pack
  registers whose upper lanes hold the tail coefficients, then stores only
  those upper lanes. The frombytes tail is Official's xmm tail.
* **Canonical check:** `vpmaxuw` accumulates across all blocks, followed by a
  single `vpcmpgtw q-1` / `vpmovmskb` at the end. `max > q-1` holds exactly
  when some coefficient is above q-1, so the return value is identical.
* **Stack:** none. Official's `poly_tobytes` has a 1760-byte frame, including
  the 1728-byte tmp.
* **Contract:** Official's pointer contract (32-byte aligned poly, unaligned
  bytes). The byte array and the poly must not overlap. That holds at every
  KEM call site. Official tobytes would tolerate overlap through its stack
  copy.
* **Scheduling is required.** The generator list-schedules each straight-line
  block on its data-dependence graph: critical path first, with register
  pressure capped at the free registers. Registers are then allocated by
  linear scan.

  The first, unscheduled fusion was *slower* than Official. In a scratch
  `perf stat` tight loop on CPU 1, tobytes took ~570 cycles against ~495. The
  cause: Official tobytes is port-bound (p0/p1/p5 about 90% busy), while the
  fused version, although it issues fewer uops, was latency/scheduler-bound at
  about 75%. Removing the memory round trip also removed the decoupling
  between the long pack chain and the tobytes chain. After scheduling (plus
  the split stores and half loads), the same loop measured tobytes ~483 vs
  ~491 cycles and frombytes ~382 vs ~463.

Dynamic instructions per call (linked ELF, `results/codec-phase-a/codec-linked-summary.json`;
Official counts are the `pack.s` kernels only, without its C wrappers):

| per call | tobytes Official | fused | frombytes Official | fused |
|---|---:|---:|---:|---:|
| total | 1613 | 1375 | 1432 | 1170 |
| cross-lane permutes (p5) | 145 | 52 | 145 | 54 |
| `vinserti128` from memory (load + p015) | 0 | 0 | 0 | 39 |
| loads / stores | 112 / 96 | 56 / 81 | 97 / 110 | 43 / 54 |
| vector ALU other than permutes | unchanged | | 168 alu → 143 (one final compare instead of 13+1) | |

Per 96 coefficients, tobytes needs 10.3 fewer cross-lane permutes and 26.4
fewer instructions in total; frombytes needs 10.1 and 29.1 fewer. The 1728-byte
store and reload is gone in both directions, and frombytes also drops the
second 1728-byte write of `r`.

### Gates (all pass)

1. **Codec differential** (`build/test_codec_fused`). The fused kernels are
   checked against Official `poly_tobytes`/`poly_frombytes` in the same ELF,
   plus an independent scalar wire model.
   - **tobytes, 287,072 polys:**
     - every int16 value in every position (65,536 constant polys plus a
       65,536-poly Latin sweep);
     - 36,000 polys drawn from the lazy-Forward caller envelopes (random and
       extreme-only);
     - 120,000 random int16 polys.
   - **frombytes, 3,763,050 inputs, 662,739 of them rejected by Official:**
     - 100,000 random valid encodings;
     - boundary patterns;
     - every 12-bit value 0..4095 at each of the 864 positions, over a valid
       background, plus all-equal patterns;
     - 100,000 random byte strings.
   - Output poly **and** return value must be equal.
   - Every call also checks 256-byte canaries, input immutability and 32
     byte-array misalignments, and the run includes 20,000 fused round trips.
   - Seven hand mutations were all caught. `vpsraw 15→14` is an equivalent
     mutant, since post-Barrett `|x| < 2^14`.
2. **KEM** (`test_kem_lazy_codec[_fretry]`, `test_kem_codec[_fretry]`; the
   common `test_kem_lazy.c` is unchanged). For both lazy+codec and codec-only:
   - 100 deterministic vectors, pk/sk/ct/ss byte-exact vs Official;
   - invalid PK, bit-flipped CT, noncanonical CT and noncanonical SK all
     matched;
   - forced g-retry and f-retry injection pass.
3. **Sanitizers.** ASan, UBSan (`-fno-sanitize-recover=all`) and LSan
   (`detect_leaks=1`) on all five binaries.
4. **Linked audit** (`build/test_kem_lazy_codec`):
   - both symbols are 32-byte aligned (2,587 B and 2,283 B);
   - no stack reference, no call, no `vzeroupper` (Official `pack.s` and its
     wrappers also have none);
   - all six Official codec functions coexist in the ELF;
   - the candidate KEM has 7 tobytes and 4 frombytes relocations to the fused
     symbols and 6 to the lazy Forward, and none to `poly_tobytes`,
     `poly_frombytes` or `poly_ntt`.

Evidence: `results/codec-phase-a/closure-tests.log`, `results/codec-phase-a/codec-linked-summary.json`.

### Same-ELF diagnostic (`supercop-derived`, not Native)

One ELF holds four KEM translation units (Official, lazy, codec, lazy+codec)
plus both codec implementations. Build flags are the common O3GC recipe.
cpucycles comes from the disposable campaign (read only). Runs were pinned to
CPU 1 with ASLR on, 15 fresh launches, and 256 observations per variant per
launch. Blocks rotate the variant order. The tables show the pooled StQ2
delta, with launch-level favourable counts in brackets. The reversed column is
the same sources linked in reverse object order. All three batches were clean
on attempt 0.

| region | Official StQ2 | fused − Official, normal | reversed |
|---|---:|---:|---:|
| tobytes | 697.6 | −16.1 (15/15) | −15.4 (15/15) |
| frombytes | 666.3 | −82.0 (15/15) | −81.7 (15/15) |

| KEM delta | Encap normal | reversed | Decap normal | reversed |
|---|---:|---:|---:|---:|
| lazy+codec − Official | −465.2 (15/15) | −303.1 (15/15) | −406.5 (15/15) | −361.9 (15/15) |
| lazy+codec − lazy (codec on top of lazy) | −222.4 (15/15) | −171.2 (15/15) | −245.1 (15/15) | −218.3 (15/15) |
| codec − Official | −153.2 (15/15) | −140.5 (14/15) | −269.5 (15/15) | −278.9 (15/15) |
| lazy − Official | −242.8 (15/15) | −131.9 (14/15) | −161.4 (15/15) | −143.6 (15/15) |

**Keypair is not resolved by this bench.** The region costs ~66k cycles here,
because the KAT AES DRBG runs inside it. Results:
- lazy+codec − Official: −146.4 (normal), −160.9 (reversed), 15/15;
- lazy+codec − lazy: +8.6 (7/15) and −0.3 (9/15);
- codec − Official: +5.4 (8/15) and +12.8 (6/15).

A scratch ELF whose tobytes has the same speed as Official still showed a
keypair offset of about +100, so per-ELF keypair offsets are larger than the
effect being measured. The unchanged shared seed-matched harness
(`bench_keypair_seedmatched.c`: byte-identical SHAKE coins, ABBA/BAAB, pk/sk
equality traps) resolves it. With 9 launches × 1000 iterations per pairing,
d = B − A:

| pairing | median d | mean d [95% two-stage bootstrap CI] | launches favourable |
|---|---:|---:|---:|
| lazy+codec vs Official | −177.0 | −153.4 [−176.3, −123.3] | 9/9 |
| lazy+codec vs lazy | −11.5 | −19.6 [−46.6, +5.2] | 9/9 |
| codec-only vs Official | −32.5 | −35.7 [−72.7, +0.4] | 8/9 |

From the component deltas, codec-only should move Encap by about −115 (2
tobytes + 1 frombytes), Decap by about −279 (2 + 3) and Keypair by about −48 (3
tobytes). Observed: Encap −153/−141, Decap −270/−279, and Keypair −33 in the
seed-matched run. Evidence: `results/codec-fused-diag-20260923/`,
`results/codec-fused-diag-swapped-20260923/` and
`results/codec-keypair-seedmatched-20260923/`. Each has `summary.json` and
`metadata.json` with source hashes, `elf_text_sha256` and the host-hygiene
record. The whole-ELF sha256 changes on every rebuild because `.strtab` holds
gcc's temporary object names, so `.text` is the stable identity.

### Better designs (described here; both implemented in exp002, see the next section)

* **2-op canonicalisation.** Replace `vpsraw/vpand/vpaddw` with
  `t = x + q; x = vpminuw(x, t)`: one op less per register, and one less p01
  shift. In the scratch tight loop this took tobytes from ~483 to ~463 cycles.
  It changes the reduction sequence, so it needs its own identity and
  exhaustive int16 record before use. The existing all-int16-per-position test
  would be that record.
* **Direct 12-bit packing (Option B/C).** Official's `tobytes_raw` spends 48
  instructions per 64 coefficients on the SoA transpose, packing and byte
  re-interleave. From natural order, one `vpmaddwd` with (1, 4096) forms
  24-bit pair values, one `vpshufb` compacts each lane to 12 bytes, and the
  lanes are stored as overlapping 16-byte halves (or put together with one
  `vpermd`). That is 2–3 vector ops per 16 coefficients instead of 12. The last
  group needs a narrower store so nothing lands beyond byte 1296. frombytes has
  the mirror image (`vpshufb` expand, shift/mask). Going straight from the
  6-way layout (Option B proper) packs 9 bytes per lane and would need
  byte-granular cross-lane moves. The natural-order route keeps pack's in-lane
  stages and looks simpler.

### Reproduce

```sh
E=ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+864/experiments/avx2_official_opt_001
T=ntruplus-ntt-Optimized/Additional_Implementation/avx2/common/official_opt_lazy/tools
cd $E
make codec-phase-a            # generator checks, codec + KEM differentials, sanitizers, linked audit
make codec-record             # copies the audit into results/codec-phase-a/
make check                    # lazy-only candidate, unchanged
make codec-bench codec-bench-keypair
python3 ../../../common/official_opt_lazy/tools/phase_b_batch.py --result-dir results/codec-fused-diag-TAG \
  --metadata metadata.json -- python3 tools/run_codec_fused_diag.py --experiment . --launches 15 --skip-build --result-dir {RESULT}
python3 ../../../common/official_opt_lazy/tools/phase_b_batch.py --result-dir results/codec-fused-diag-swapped-TAG \
  --metadata metadata.json -- python3 tools/run_codec_fused_diag.py --experiment . --launches 15 --skip-build \
  --binary build/bench_codec_fused_swapped --result-dir {RESULT}
python3 ../../../common/official_opt_lazy/tools/phase_b_batch.py --result-dir results/codec-keypair-seedmatched-TAG \
  --metadata metadata.json -- python3 tools/run_codec_keypair_seedmatched.py --experiment . --skip-build --result-dir {RESULT}
```

## NTRU+864 direct 12-bit codec (exp002, 2026-09-23)

A third NTRU+864 candidate, `avx2-officialopt-lazy-codec-864-exp002`, puts a
new codec on the caller-lazy Forward. It implements both "better designs" from
the Option A section: the 2-op freeze and direct 12-bit packing. **This is
Phase A plus a same-ELF diagnostic. There was no SUPERCOP campaign, Native was
not measured, and no host control was changed.** exp001 and the lazy-only
candidate are unchanged, and `make check codec-check` still passes. The new
rules live in `codec_direct.mk`, which the NTRU+864 Makefile includes after
`codec.mk`.

| File (in `NTRU+864/experiments/avx2_official_opt_001/`) | Role |
|---|---|
| `tools/prove_freeze_2op.py`, `tests/test_freeze_2op.c` | exhaustive 2-op freeze record (Python model + real instructions) |
| `tools/generate_codec_direct.py` | generator (with `--check`); reuses the exp001 scheduler |
| `asm/ntruplus864_officialopt_codec_direct.s` | generated `ntruplus864_officialopt_{tobytes,frombytes}_direct` |
| `asm/ntruplus864_officialopt_codec_fused_min.s` | generated control `ntruplus864_officialopt_tobytes_fused_min` (exp001 + 2-op freeze only) |
| `src/kem_lazy_codec_direct.c`, `src/kem_codec_direct.c` | candidate KEM overlay of `kem_lazy.c`; direct-codec-only control on Official `kem.c` |
| `tests/test_codec_direct.c`, `tests/test_codec_fused_min.c` | the unchanged exp001 differential, bound to the new kernels by overlay |
| `tools/audit_codec_direct.py`, `tools/mutate_codec_direct.py` | linked-ELF audit; mutation check |
| `bench/bench_codec_direct.c`, `tools/run_codec_direct_diag.py`, `tools/run_codec_direct_keypair_seedmatched.py` | diagnostics |

### Idea 2: 2-op canonicalisation (proved)

Official freezes each coefficient with a Barrett step (`vpmulhrsw _16xv`,
`vpmullw _16xq`, `vpsubw`) and then adds q to negative results (`vpsraw 15`,
`vpand q`, `vpaddw`). The last three instructions become
`y = vpaddw(b, q); out = vpminuw(b, y)`. This is correct exactly when every
Barrett output b lies in (−q, q):
- for b ≥ 0, unsigned b < b+q < 2q;
- for b < 0, unsigned b ≥ 2^16 − q + 1, which is larger than b+q ∈ (0, q).

`prove_freeze_2op.py` reads q and `V = BARRETT_V(q)` = 9 from the pinned
`params.h` and `consts.c`. It then checks every freeze site in `pack.s`
instruction by instruction, on the registers loaded from `_16xv` and
`_16xq`. Over all 65,536 int16 inputs, with bit-exact word semantics, it
finds:
- the Barrett output lies in **[−3291, 3291]**;
- the 2-op and 3-op results are equal bit for bit;
- both equal x mod q.

The C twin runs the same 65,536 inputs through the real instructions with the
linked constants. Result: `results/codec-direct-phase-a/freeze-2op-proof.json`.

**Portability:** NTRU+768 and NTRU+1152 `poly_tobytes` (pristine
`pack.s:20-70`, read-only) use the same freeze: the same 3-op sequence, 8
sites per iteration, q = 3457, V = 9. The same record passes for both, so the
change ports as-is. It was not applied there.

In isolation (the `fused_min` control, i.e. exp001 with only this change),
tobytes drops from 1375 to 1321 instructions per call. That is 6 per 96
coefficients, all of them p01 shifts. The same-ELF saving is 14–16 cycles
(15/15 launches, both link orders).

### Idea 1: direct packing, straight from the 6-way layout

In the internal layout, register `R_r`, word `l` (0..15) holds wire
coefficient `6l + r`. Wire pair `(6l+2s, 6l+2s+1)` is therefore
`(R_2s[l], R_2s+1[l])`, which is in the same lane of two registers. Per
96-coefficient block, tobytes does:

1. freeze (Barrett + 2-op) on the six registers;
2. `vpunpck{l,h}wd(R_2s, R_2s+1)` and `vpmaddwd` by (1, 4096). Each dword now
   holds the 24-bit wire value `c_even + 4096·c_odd`. `D_s^lo` holds pairs
   `3l+s` for l = 0..3 | 8..11, and `D_s^hi` for l = 4..7 | 12..15;
3. a 5-op in-lane dword interleave per triple:
   `X = unpckldq(D1,D2)`, `Y = unpckhdq(D0,D1)`,
   `O0 = unpcklqdq(D0,X)`, `O1 = blendd(Y,X,0xCC)`, `O2 = unpckhqdq(Y,D2)`.
   Every 128-bit lane then holds exactly one 12-byte wire group (4 consecutive
   pairs, out of order);
4. one `vpshufb` per register orders the pairs and drops each dword's fourth
   byte;
5. each lane goes out as a 16-byte store at `12·group`
   (`vmovdqu xmm` / `vextracti128 m128`).

There is **no cross-lane permute and no transpose to natural order**. Each
16-byte store spills 4 zero bytes into the next group, which that group's
store then overwrites. The generator therefore adds an ordering chain to the
exp001 list scheduler so that stores stay in ascending address order. The last
group (bytes 1284..1295) uses `vextracti128` + `vmovq` + `vpextrd`, so nothing
is written past byte 1295.

frombytes is the mirror image:
1. 16-byte loads at `12·group` (`vmovdqu xmm` + `vinserti128 m128`);
2. a `vpshufb` expand to `[b0 b1 b2 0]` dwords, placing the pairs in the same
   `O_k` positions;
3. the inverse 5-op interleave
   (`Z = unpckldq(O1,O2)`, `W = unpckhdq(O0,O1)`, `D0 = unpcklqdq(O0,Z)`,
   `D1 = blendd(W,Z,0xCC)`, `D2 = unpckhqdq(W,O2)`);
4. `vpand 0xfff` / `vpsrld 12`;
5. `vpackusdw(lo, hi)`, which restores the 6-way word order exactly. Values
   are ≤ 4095, so nothing saturates.

The last group is loaded from byte 1280 with a mask whose lane 1 is shifted
by 4, so nothing is read past byte 1295. The canonical check is exp001's:
`vpmaxuw` into one accumulator, then a single `vpcmpgtw q-1` / `vpmovmskb` at
the end. Blocking is 4 × 192 coefficients plus a final 96, with no stack,
calls or `vzeroupper`. The pointer and no-overlap contract is exp001's.
Official pack.s is untouched, and the new constants are local `.rodata`
labels.

**6-way direct vs "natural order first".** The task also proposed transposing
to natural order first (pack's in-lane stages) and then packing with
`vpmaddwd`/`vpshufb`. Per 96 coefficients, that route costs pack's 30
pair16/pair32/pairq ops plus 6 `vpmaddwd` and 6 `vpshufb`: 42 ops after the
freeze. Going straight from the 6-way layout costs 6 unpack + 6 `vpmaddwd` +
10 interleave + 6 `vpshufb`: 28 ops. The worry for the 6-way route was
compacting 9-byte records. That disappears, because the dword interleave can
leave the pairs out of order and the final `vpshufb` reorders them for free.
The first estimate for that interleave (2 `vpshufd` + 6 `vpblendd`) was also
improved to 5 unpack/blend ops, and frombytes inverts it in 5. The 6-way
route was the only one built.

**Scheduling effort.** The exp001 scheduler (critical path first, register
pressure capped, linear-scan allocation) was used unchanged apart from the
store chain. Pinning the `vpshufb` masks in registers was tried. It does not
fit in 16 ymm registers: the allocator runs out in both kernels. The masks
therefore stay RIP-relative memory operands, which cost 6.3 loads per 96
coefficients on the three load ports. In a scratch `rdtscp` tight loop on
CPU 1 (TSC ticks, exploratory only), tobytes took 298 against 720 (exp001),
692 (`fused_min`) and 727 (Official). frombytes took 288 against 573 and 674.

Dynamic instructions (linked ELF, `results/codec-direct-phase-a/codec-direct-linked-summary.json`;
Official = `pack.s` kernels only). First per call, then per 96 coefficients:

| tobytes | Official | exp001 | fused_min | exp002 |
|---|---:|---:|---:|---:|
| total per call | 1613 | 1375 | 1321 | **707** |
| total per 96 coefficients | 179.2 | 152.8 | 146.8 | **78.6** |
| p01 (multiply + shift) | 508 | 508 | 454 | 162 |
| p015 (add/logic/min/blendd) | 370 | 370 | 370 | 180 |
| in-lane shuffle (p15 on Golden/Redwood Cove, p5 on Skylake) | 290 | 290 | 290 | 180 |
| cross-lane permute (p5) | 145 | 52 | 52 | 1 |
| loads / stores | 112 / 96 | 56 / 81 | 56 / 81 | 57 / 109 |

| frombytes | Official | exp001 | exp002 |
|---|---:|---:|---:|
| total per call | 1432 | 1170 | **547** |
| total per 96 coefficients | 159.1 | 130.0 | **60.8** |
| p01 (shift) | 346 | 346 | 54 |
| p015 (and/max/blendd) | 348 | 323 | 129 |
| in-lane shuffle | 290 | 290 | 180 |
| cross-lane permute (p5) | 145 | 54 | 0 |
| loads / `vinserti128 m128` / stores | 97 / 0 / 110 | 43 / 39 / 54 | 55 / 54 / 54 |

Per 96 coefficients, exp002 tobytes spends 30 ops on the freeze, 12 on
unpack + `vpmaddwd`, 10 on interleave, 6 on `vpshufb`, plus 6 loads and 12
stores. exp002 frombytes spends 12 loads, 6 `vpshufb`, 10 interleave, 18
split/pack, 6 `vpmaxuw` and 6 stores. The port classes are a coarse model,
not a measurement.

### Gates (all pass)

1. **Codec differential.** `build/test_codec_direct` is the unchanged exp001
   test (`tests/test_codec_fused.c`), bound to the direct kernels.
   - Cases: 287,072 tobytes polys and 3,763,050 frombytes inputs (662,739 of
     them rejected by Official), as in exp001.
   - Every call checks canaries, input immutability and 32 byte-array
     misalignments. Output poly **and** return value must equal Official and
     the scalar wire model.
   - `build/test_codec_fused_min` passes the same test.
   - `tools/mutate_codec_direct.py` applied 20 hand mutations to the direct
     asm. They cover the freeze, the madd constant, every mask family including
     lane-1-only and last-group, blend immediates, load/store offsets, store
     order, the last-group stores, the low12 mask, the shift count, the
     canonical check and the loop bound. 19 were caught. `vpackusdw →
     vpackssdw` is an equivalent mutant, since the values are ≤ 4095.
2. **KEM.** `test_kem_lazy_codec_direct[_fretry]` and
   `test_kem_codec_direct[_fretry]` use the common `test_kem_lazy.c`
   unchanged.
   - 100 deterministic vectors, pk/sk/ct/ss byte-exact vs Official;
   - invalid PK, bit-flipped CT, noncanonical CT and noncanonical SK all
     matched;
   - forced g-retry and f-retry injection pass.
3. **Sanitizers.** ASan, UBSan (`-fno-sanitize-recover=all`) and LSan on all
   seven binaries (including the freeze test and `fused_min`).
4. **Linked audit** (`build/test_kem_lazy_codec_direct`):
   - the symbols are 32-byte aligned (1,354 B and 1,117 B);
   - no stack reference, no call, no `vzeroupper`, no text relocations;
   - the candidate KEM has 7 tobytes and 4 frombytes relocations to the direct
     symbols and 6 to the lazy Forward, and none to Official or exp001 codec
     symbols or to `poly_ntt`.

Evidence is in `results/codec-direct-phase-a/`: `closure-tests.log`, which
also holds the mutation run and the `make check codec-check` regression,
`codec-direct-linked-summary.json`, `freeze-2op-proof.json` and
`mutation-check.json`.

### Same-ELF diagnostic (`supercop-derived`, not Native)

One ELF holds:
- the Official, lazy, exp001 and exp002 KEM translation units;
- the Official, exp001, `fused_min` and exp002 codec kernels.

The setup matches the exp001 diagnostic: CPU 1, ASLR on, 15 fresh launches,
common O3GC recipe, cpucycles from the disposable campaign. Each launch uses
12 rotated blocks × 32 = 384 observations per variant. Cells show the pooled
StQ2 delta, with favourable launches in brackets. The reversed column uses the
same objects and asm linked in reverse order. All batches were clean on
attempt 0.

| region | Official StQ2 | exp002 − Official, normal | reversed | exp002 − exp001, normal | reversed |
|---|---:|---:|---:|---:|---:|
| tobytes | 701.3 | −265.3 (15/15) | −273.1 (15/15) | −251.8 (15/15) | −256.9 (15/15) |
| frombytes | 672.4 | −276.6 (15/15) | −265.1 (15/15) | −192.6 (15/15) | −180.5 (15/15) |
| Encap | 32921 | −986.9 (15/15) | −1003.1 (15/15) | −666.9 (15/15) | −617.3 (15/15) |
| Decap | 23826 | −1573.6 (15/15) | −1507.3 (15/15) | −1074.9 (15/15) | −1082.5 (15/15) |

Same batches, other pairs:
- exp001 − Official: tobytes −13.5/−16.2, frombytes −84.0/−84.6, Encap
  −320.0/−385.8, Decap −498.7/−424.8;
- `fused_min` − exp001 (the 2-op freeze alone): −14.4/−16.4, 15/15;
- exp002 − lazy: Encap −834.8/−874.1, Decap −1379.9/−1359.8, all 15/15.

Keypair in the same ELF gives exp002 − exp001 = −725.9/−704.3 (15/15). The
KAT DRBG is inside that region, so the seed-matched harness is the reference
(unchanged `bench_keypair_seedmatched.c`, 9 launches × 1000 iterations per
pairing, d = B − A):

| pairing | median d | mean d [95% two-stage bootstrap CI] | launches favourable |
|---|---:|---:|---:|
| exp002 vs Official | −915.0 | −941.3 [−987.9, −903.9] | 9/9 |
| exp002 vs exp001 | −711.0 | −718.6 [−758.4, −681.6] | 9/9 |
| exp002 vs lazy | −736.5 | −741.1 [−775.0, −712.5] | 9/9 |

The component deltas explain the caller deltas. Averaged over both link
orders, exp002 − exp001 is about −254 per tobytes and −187 per frombytes. That
predicts:
- Keypair ≈ −762 (3 tobytes); observed −711 seed-matched;
- Encap ≈ −695 (2 tobytes + 1 frombytes); observed −667/−617;
- Decap ≈ −1069 (2 + 3); observed −1075/−1083.

Evidence: `results/codec-direct-diag-20260923/`,
`results/codec-direct-diag-swapped-20260923/` and
`results/codec-direct-keypair-seedmatched-20260923/`. Each has `summary.json`
and `metadata.json` with source hashes, `elf_text_sha256` and the hygiene
record.

### Reproduce

```sh
E=ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+864/experiments/avx2_official_opt_001
T=../../../common/official_opt_lazy/tools
cd $E
make direct-phase-a        # generator checks, freeze proof (864 + pristine 768/1152), codec + KEM differentials, sanitizers, audit
make direct-record         # copies proof and audit into results/codec-direct-phase-a/
python3 tools/mutate_codec_direct.py --experiment . --output results/codec-direct-phase-a/mutation-check.json
make check codec-check     # lazy-only and exp001, unchanged
make direct-bench direct-bench-keypair
python3 $T/phase_b_batch.py --result-dir results/codec-direct-diag-TAG --metadata metadata.json -- \
  python3 tools/run_codec_direct_diag.py --experiment . --launches 15 --skip-build --result-dir {RESULT}
python3 $T/phase_b_batch.py --result-dir results/codec-direct-diag-swapped-TAG --metadata metadata.json -- \
  python3 tools/run_codec_direct_diag.py --experiment . --launches 15 --skip-build \
  --binary build/bench_codec_direct_swapped --result-dir {RESULT}
python3 $T/phase_b_batch.py --result-dir results/codec-direct-keypair-seedmatched-TAG --metadata metadata.json -- \
  python3 tools/run_codec_direct_keypair_seedmatched.py --experiment . --skip-build --result-dir {RESULT}
```

## Still not done

- No `clean/` change and no promotion.
- No natural *f*-retry for 864; only the injection covers it.
- No Native re-confirmation from a release package.
- The 81-launch pooled Native runs are done for both parameters (see
  "Extended Native and ASLR-on paired"). There is still no explanation for
  why the O3-built 864 candidate loses its Decap gain in Native.
- 864 reversed placement was not re-run at 48 blocks with ASLR on; the
  secondary check uses the Phase B 16-block run.
- NTRU+864 lazy+codec candidates (exp001, exp002): no qualification export,
  no SUPERCOP campaign and no Native measurement yet. Only Phase A and the
  same-ELF diagnostic exist.
- The 2-op freeze is proved for NTRU+768/1152 `poly_tobytes` but not applied
  there. The direct 12-bit codec is not ported: 768/1152 have their own
  codec layout, which was not analysed.

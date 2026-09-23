# NTRU+864 / NTRU+1152 Official AVX2: caller-bounded lazy Forward (Phases A and B)

Branch `official-opt-lazy-864-1152`, forked from `avx2-official-opt` at
`e76ecdf`. This ports the NTRU+768 caller-lazy Forward
(`docs/ntruplus768-official-opt.md`, Rounds 4-6) to the two larger Official
parameter sets. **Phase A is only about correctness**; it made no timing,
SUPERCOP campaign or host-control change. **Phase B** (Native SUPERCOP
performance evidence, 2026-09-23) is at the end of this document. No host
control was changed in either phase.

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

## Still not done

- No `clean/` change and no promotion.
- No natural *f*-retry for 864; only the injection covers it.
- No Native re-confirmation from a release package.

# NTRU+768 Forward redesign: Encap-first architecture gate

Date: 2026-09-21  
Branch: `avx2-gt-ntt-864-1152`  
Official baseline: SUPERCOP 20260831, `crypto_kem/ntruplus768/avx2`  
Current GT baseline: `avx2-gt32-clean`

Frozen provenance:

```text
Official AVX2 tree SHA-256: 8db00172e705b67e231b63708295781d65681fef2c7422d717fe91ab48d576e7
GT clean source-manifest SHA-256: 55b27d94e490384baca7df09e3ccc4e9ba1fb221555fad8767f6400a3a31b468
normal Official ELF SHA-256: edcd87e8e2552e1fd9e0cd118a8048a9369ade3ad25989458a2efdd6107b159f
normal GT ELF SHA-256:       5657dbb8983c9fcf421b4487ca48f0f54b2c1493403ccbc16af5fb03635cb470
reversed Official ELF SHA-256: d8a08a0a1836bb9fe2a06cef1deb1ac6778bb33a7e43039ad38ba05921f1674c
reversed GT ELF SHA-256:       a8a27121040f1d8e1bbca1d39efdbc4f78bb2cc93a35c7343b7c2efc5c92d680
```

The source-manifest digest is the SHA-256 of the sorted `sha256sum` records
for every regular file below `clean/avx2-gt32-clean`; it does not claim to be
the hash of a tar archive.

## Outcome

The original A/B/C gate overclaimed its negative evidence. Its fixed frontend
allocation did not rule out partial D16/D8 execution; the R1-U/inverse proof
was not the Encap consumer; and expensive GT-to-Official bridges did not test
an Official-like direct consumer. Those historical results are retained below
with corrected scope. B/C remain open, not globally rejected.

The follow-up closes the actual clean Encap range contract and constructs two
same-DAG, namespaced A wavefronts. See the new closure section below. Clean
production remains unchanged; local wins are not Native/promotion evidence.

The reproducible decision artifact is:

```text
generated/tile4_forward_redesign_gate.json
```

Regenerate it with:

```sh
cd ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+768/experiments/avx2_gt32_tile4_official_001
python3 tools/generate_forward_redesign_gate.py
```

## Frozen performance coordinate

The original gate used the following historical Native coordinate. Do not
mix these observations with the new 2026-09-21 campaign at the end of this
report, or treat different campaign deltas as additive:

| operation | Official StQ2 | current GT StQ2 | GT - Official |
|---|---:|---:|---:|
| keypair | 21585.12 | 21259.69 | -325.43 |
| enc | 28279.75 | 28309.01 | +29.26 |
| dec | 19451.19 | 19256.62 | -194.57 |

For Encap, fixed-ELF results remain placement-sensitive and close to parity.
Therefore a local Forward win is not promoted without a complete Encap-island
and Native win.

## Consumer contracts

The design search does not treat Forward as a single-output primitive.

```text
r: coefficient polynomial
   -> arithmetic M state retained for h*r
   -> exact Q24/hash input bytes

m: coefficient polynomial
   -> transformed M addend
   -> h*r + m
   -> exact ciphertext bytes

h: validated public-key Q24 bytes
   -> M leaves with the same quartic/root/lambda lane identity as r and m
```

All layouts in this report use Montgomery exponent `e=0`; the external wire
format and terminal quartic factors are frozen.

## Current GT register flow

### Frontend: coefficient to materialized GT packets

```text
register ownership before
  six input YMM columns for one of eight frontend iterations

instructions/dependencies
  raw -722 top split
  branch twist by fixed Montgomery constants
  two DFT3 groups
  DFT3_WIDE_STORE writes one vector into each of six terminal tiles

ownership after
  six produced vectors are in scratch, not live registers

mathematics
  CRT/Good coordinate n=(64*n3+33*n32) mod 96
  two branch transforms, then the length-3 axis

layout/scale/range
  group-major AoS, e=0; six tiles accumulate one vector per iteration

next consumer
  a complete terminal tile needs eight vectors, but D16 can start after its
  first pair and D8 after its four-vector dependency cohort is ready
```

The eight iterations therefore create `8 × 6 = 48` YMM values.  The current
boundary writes and later reloads all 48 vectors (1536 bytes each direction).

One representative YMM is:

```text
128-bit low half                          128-bit high half
[q0.c0..c3 | q1.c0..c3]                  [q2.c0..c3 | q3.c0..c3]
 two quartic groups                       two quartic groups
```

The exact `q0/q1` identities depend on the generated GT mapping; the important
ownership fact is that all four quartic coefficients of a leaf remain together.

### Terminal: NTT32 and M landing

```text
register ownership before
  eight YMM values for one terminal tile

instructions/dependencies
  D16 raw add/sub, then D8/D4 Montgomery butterflies
  D2/D1 half/qword routing
  terminal transpose to four coefficient planes

ownership after
  c0, c1, c2, c3 planes in the private M layout

mathematics
  five radix-2 layers complete the length-32 axis

layout/scale/range
  AoS -> coefficient-plane M; e remains 0

next consumer
  lane-wise quartic BaseMul/Add, Q24 hash/ciphertext serializers
```

This explains both sides of the current design: materialization costs 48
stores plus 48 reloads, but it also releases all frontend registers and gives
the out-of-order engine two separately schedulable regions.

## Family A: GT3-first frontend/NTT32 joint scheduling

The original gate summarized historical fixed schedules; it did not construct
new single-/double-cohort instruction-level allocations.

Each frontend iteration produces one vector for each of six terminal tiles.
The previous 16/16-YMM allocation cannot simply retain additional values, but
that is a scoped statement about that allocation. Reordering the same DAG and
renaming registers can free space without changing arithmetic. Partial radix
execution does not need a complete eight-vector tile.

Existing machine evidence:

- F14 changes dependencies only and saves roughly 5.8--7.3 TSC cycles per
  Forward, but its whole-Encap effect is below launch/image variance.
- W2 preloads the next packet and saves roughly 1--2 cycles; it removes no
  instruction or boundary and is explicitly not repeated.
- N5 cross-tile preload is about a one-cycle effect with code growth.

Historical decision superseded: A has now been reopened with concrete SSA
allocation and partial D16/D8 consumption, not W2 next-packet preloading.

## Family B: NTT32-first/interleaved GT

The new question was whether the previous N32-first repair was only required
because its proof used the wider `[-3,4]` domain.  The gate recomputes every
fixed-factor signed Montgomery interval for actual Encap `r/m in [-1,1]`.

| quantity | branch 0 | branch 1 |
|---|---:|---:|
| raw top interval | [-723, 723] | [-724, 724] |
| DFT3 output bounds | 13256/13262/13196 | 13442/13296/13415 |
| worst Forward intermediate | 13262 | 13442 |

Forward is signed-i16 safe under that interval model. The following historical
R1-U/inverse composition fails its conservative proof, but is NOT Encap:

```text
R1-U maximum                    14485
inverse IDFT3 internal          28686
inverse radix-2 stage bounds    54386, 56410, 59098, 61881, 65102
```

The later inverse intervals exceed i16; this is neither a reachable overflow
witness nor a refutation of zero-row0-repair Encap. Encap uses the general B3
R-squared finalizer and serializers, with no inverse.

Decision: B deferred, not rejected by this evidence. The existing 168-chain conjugated implementation
with row0 centering remains the range-safe N32-first machine object; its prior
complete-chain result was approximately parity and placement-sensitive.

## Family C: Official-like/hybrid landing

Two exact bridges were audited instead of comparing abstract layouts.

GT terminal to Official native landing requires, per Forward:

```text
256 vperm2i128
256 vpshufb
208 vpor
 48 stores
-----------
720 routing/store instructions
```

The selected private terminal uses 144 shuffles, so this bridge adds 576 route
instructions.  Each Official target vector mixes five or six source-half
routes; the cost cannot be hidden by renaming stores.

For a different final Encap P layout, the best exact candidate saves 48
Forward instructions and 41 Q24 routes but pays 96 M-to-P routes, a net `+7`
instructions.  It removes no materialized pass, multiply chain, or reduction.

Decision: C deferred. Instruction counts above do not establish cycle loss.
A viable hybrid must compute a consumer result
directly from the Official late-stage registers; GT-to-Official or M-to-P
bridges are not evidence for such a design.

## Layered decision

| layer | result |
|---|---|
| Forward | compare new A prototypes against the frozen current GT, not stale Official wrapper measurements |
| r dual output | materialized M plus exact hash-input bytes; no serializer fusion |
| complete Encap polynomial island | new A1/A2 results below |
| Native KEM | separate campaign required; never inferred by summing local deltas |

No clean source, pristine SUPERCOP tree, or package source was modified.

## What can still change the result

The next useful work must add a mechanism absent from A/B/C as currently
specified:

1. An instruction-level frontend/radix schedule exploiting partial readiness,
   not merely preloading or requiring all eight vectors before any work.
2. A joint N32-first **actual Encap** B3/add/serializer range contract;
   inverse safety is a separate caller question.
3. An Official late-stage arithmetic/serializer consumer written directly on
   Official register ownership, with no GT/M bridge.

These are separate hypotheses; neither a different arithmetic DAG nor a new
physical ABI is required for A. No universal GT/AVX2 conclusion follows.

## Encap range closure and partial D16/D8 wavefront (2026-09-21)

The new proof follows `encap.c`: CBD1/SOTP inputs in `[-1,1]`, decoded valid h
in `[0,3456]`, e=0 M states, general B3 with R-squared finalizer, add m, pack.
There is no inverse in this contract. No reduction was added.

| boundary | conservative maximum absolute value |
|---|---:|
| D16 | 9844 |
| D8 | 11478 |
| D4 | 12674 |
| D2 | 14398 |
| D1 / Forward output | 15605 |
| asymmetric h*r, after R-squared finalizer | 1856 |
| h*r + m | 17461 |

Frontend enumeration covers the exact independent small-coefficient sets;
later operations use conservative per-tile/per-Q intervals. These are not
reachable endpoint witnesses. The old 10788 Forward metadata assumed a
centered core entry that the reachable frontend does not supply. It was not
a proof of the full caller. Conversely, the pack function names do not impose
hardware limits: the reachable v=9 reducer correctly canonicalizes all 65536
signed-i16 inputs. Both mathematical enumeration and the real pack ASM were
checked. Intentional VPMULLW wrap is distinguished from unintended signed
add/sub overflow.

### Constructive scheduling, not a register-count impossibility argument

The generator expands the reachable clean macros into SSA and allocates actual
AVX2 operations. It searches all six single tiles and fifteen two-tile pairs,
three packet orders (including `0,4,2,6,1,5,3,7`), and two list-scheduling
policies: 126 cases. A cohort is one `(branch,k3)` output tile. Named boundary
values may use their existing scratch slots; multiply temporaries may not spill.

D16 pair `(0,4)` can execute as soon as those two values exist. D8 waits for
the corresponding four-value cohort. The frozen D4/D2/D1 suffix consumes the
result when ready. Merely storing all D8 outputs would relocate, not remove,
the boundary; this is why the suffix must also accept live D8 results.

| realization | selected tiles | explicit extra boundary stores/reloads | total data loads/stores | net vs control |
|---|---|---:|---:|---:|
| current materialized control | — | — | 96 / 96 | — |
| A1 single cohort | tile 0 | 0 / 0 | 88 / 88 | -8 / -8 |
| A2 double cohort | tiles 0,1 | 7 / 7 | 87 / 87 | -9 / -9 |

Both selected schedules use packet order 0..7. The dependency-friendly
alternative was searched, not assumed superior. The two-tile schedule removes
16 nominal frontend pairs but pays seven explicit pairs back: its net credit
is nine, not sixteen. Peak YMM is 16, stack scratch/spill zero. This search is
bounded and does not prove a global optimum or impossibility of larger wins.

The implementation also changes register scheduling, coalesces register moves,
unrolls remaining tile work, and removes the internal frontend/core call and
vzeroupper boundary. Hence measured credit is the whole realization, not a
causal estimate of the deleted memory instructions alone. Constants are copied
from the frozen source tables; footprint is recorded, not optimized here.

### Correctness and linked checks

Both prototypes pass 11,543 Forward cases: 1536 +/- impulses, four boundary
patterns, and 10,003 inputs generated by actual CBD1/SOTP routines. Raw outputs
match current GT. An independent polynomial evaluation at every quartic root
checks impulses and 64 random inputs, rather than trusting the physical map
alone. Tests cover output=input, output=scratch, disjoint immutable input,
canaries, 100 asymmetric B3 cases, exact wire encoding and retained-r state.

Linked audits check 32-byte entry alignment, actual data loads/stores, ordered
source/machine register-flow equality, backwards machine liveness, no calls,
branches, stack frame or stack vector traffic, and one outer vzeroupper.
ASan/UBSan pass; LSan alone is disabled because the sandbox forbids its ptrace
operation. The C harness uses no heap allocation. ASM memory accesses remain
covered by canaries and differential checks, not compiler instrumentation.

### Same-ELF pricing against current GT

`results/encap-range-wavefront-20260921-serious/summary.json` records 9 fresh
processes, 96 observations per mode/variant/process, common O3GC architecture
flags, normal placement / ASLR-on, CPU 1 performance/turbo-off, pinned SUPERCOP
`default-perfevent` cpucycles backend, and stabilized quartiles. This is
**supercop-derived-poly**, not Native SUPERCOP KEM. One immutable input bank
per operand, common output/scratch residency, untimed preflight and warmups;
no mode dispatch in the timed operation. SHAKE is not part of these islands.

| boundary | A1 StQ2 delta | favorable launches | A2 StQ2 delta | favorable launches |
|---|---:|---:|---:|---:|
| 1x r Forward | -7.39 | 9/9 | -8.03 | 9/9 |
| 1x m Forward | -7.67 | 9/9 | -7.46 | 9/9 |
| 2x Forward | -14.55 | 9/9 | -16.25 | 9/9 |
| r state + exact hash-input bytes | -10.45 | 9/9 | -8.87 | 9/9 |
| full polynomial island including PK decode and ciphertext | -17.15 | 9/9 | -2.63 | 7/9 |

A1 is eligible for a new Encap-only Native experiment. A2 stays research-only:
one additional saved pair does not produce a stronger complete-island result.
Neither result authorizes clean promotion. Short RDTSCP observations are
preserved separately and must not be mixed with cpucycles/StQ numbers.

### Native re-entry: A1 does not retain the island win

Installed only A1 as `avx2-gt32-encap-wavefront1-exp-sc20260831` into a fresh
disposable SUPERCOP copy. Only the two Encap Forward calls change. The complete
candidate passes 100 deterministic KAT vectors byte-exact and 32 valid/tampered
API trials plus invalid-PK rejection/zeroization, input immutability and canaries.

All three Native measurements use unmodified `crypto_kem/measure.c`, normal
SUPERCOP compiler selection and nine fresh processes. Official selected GCC
15.2 O2, both GT implementations selected GCC 15.2 O3, with the native SUPERCOP
architecture/PIC/PIE flags. These are serial Native results, not paired causal
estimates. Artifacts: repository `results/encap-wavefront-native-20260921/`.

| operation, Native StQ2 | Official | current GT | A1 wavefront | A1 minus current |
|---|---:|---:|---:|---:|
| Keygen | 21600.63 | 21248.06 | 21183.87 | -64.19 |
| Encap | 28085.76 | 28176.59 | 28390.81 | **+214.23** |
| Decap | 19437.83 | 19190.22 | 19123.38 | -66.84 |

A1 Encap is also **+305.05 cycles vs Official**. Therefore it stays in the
experiment; no clean promotion and no winner-only four-setting confirmation.
Unchanged Keygen/Decap source does not earn an arithmetic credit from the
different image's observed numbers. The result rejects this realization as a
Native improvement, not Good–Thomas or partial wavefront in general.

Whole Native image footprint changed from `.text=64919/.rodata=60520` bytes to
`.text=74775/.rodata=85320`. The candidate is straight-line and copies frozen
constant sections, including unused constants; those bytes are **not** a hot
working-set measurement. Candidate A1 alone is 9848 text bytes, compared with
3917+1056 bytes for the two compact current Forward functions (retained for
other callers). Footprint/placement are plausible contributors, not proven
causes of the +214 cycles. No third ASM prototype was added to chase this result.

Post-timing validation repeated the differential with scratch/output poisoned
before every candidate invocation to rule out dependence on a prior control's
materialized state. It passes with ASan/UBSan and the same linked structural
checks. This is recorded in `results/encap-range-wavefront-20260921-poisoned-recheck/`.
The original serious-campaign harness is preserved as
`test_encap_wavefront.measured.c` inside that serious result directory; its
SHA-256 exactly matches the measurement metadata, before the later poisoning
test enhancement. Measurement ELFs and raw observations were not replaced.

### Reproduce

From the 768 experiment directory:

```sh
make encap-range-wavefront-generate
python3 tools/run_encap_wavefront.py --tag <new-check-tag>
python3 tools/run_encap_wavefront.py --short --tag <new-short-tag>
python3 tools/run_encap_wavefront.py --serious --supercop-root <pinned-root> --tag <new-serious-tag>
```

Runners refuse to overwrite results. The serious result records input cutpoints,
bank/warmup policy, compiler/flags, source/ELF hashes, selected cpucycles identity,
host state, disassembly, sanitizer logs and raw observations. The top-level
`prepare_supercop.py`, experiment `install_encap_wavefront.py`, `run_flat_kat.py`,
`run_api_semantics.py`, and `run_supercop_benchmark.py --mode native-kem` reproduce
Native integration in a **new** campaign; the installer requires the qualifying
serious-island summary. The Native summary has its own non-overwriting
`tools/summarize_encap_wavefront_native.py <campaign-results>` command.

Current disposition: range contract closed; two real wavefronts validated;
A1 small island win did not survive Native Encap; A2 lacked consistent island
direction. Production and pristine/frozen sources remain unchanged.

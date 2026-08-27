# NTRU+864 / 1152 AVX2 polynomial-optimization workflow

This document is the branch source of truth for the NTRU+864 and NTRU+1152
AVX2 polynomial work. The project optimizes the complete polynomial subsystem,
but no experimental result becomes production merely because one kernel wins.

## Scope and fixed boundaries

- Target: x86-64 AVX2; the primary qualification host is the Intel Core Ultra
  7 155H available in this workspace.
- Order: establish the shared `2 x 9 x 16` transform model, qualify NTRU+1152,
  then reuse the framework for NTRU+864's cubic terminal arithmetic.
- Contracts: keep KEM-reachable small-input multiplication separate from
  general centered mod-q multiplication (`[-1728,1728]`).
- Public API: `crypto_kem_keypair`, `crypto_kem_enc`, and `crypto_kem_dec` do
  not change. Polynomial benchmark symbols remain internal.
- Frozen baseline: `ntruplus-KpqC-Final/` is read-only and is not the primary
  performance source.

## Branch and commit sequence

Work on `experiment/avx2-ntruplus864-1152-polymul-001`, based on commit
`20c7116`. Keep benchmark infrastructure, shared algebra, parameter work, and
promotion in reviewable commits:

1. SUPERCOP lock, workflow, and benchmark framework.
2. Shared GT9x16 oracle and generator.
3. NTRU+1152 baseline and optimization.
4. NTRU+864 baseline and optimization.
5. Qualified production cleanup.
6. Frozen package export and release evidence.

## Directory policy

| Path | Role | Rule |
| --- | --- | --- |
| `ntruplus-KpqC-Final/` | Frozen correctness baseline | Never edit |
| `bench/supercop.lock` | Performance-source identity | Explicit refresh only |
| `.../avx2/common/gt9x16/` | Shared model/generator | No production dependency |
| `NTRU+*/experiments/` | Candidates and local evidence | All research starts here |
| `NTRU+*/clean/` | Qualified flat production source | Promotion only |
| `bench/` | Cross-implementation validation | Keep implementation-neutral |

Each parameter experiment contains `upstream/supercop-avx2/` (an untouched
import), `ref/`, `src/`, `asm/`, `generated/`, `tests/`, `bench/`, `tools/`,
and `results/`. `STATUS.yml` records the active candidate, completed gates,
rejections, and next step.

## SUPERCOP baseline lifecycle

`scripts/refresh_supercop_lock.py` discovers the newest official release,
downloads it, hashes the archive, verifies the two AVX2 implementations, and
rewrites the lock. Normal tests never refresh implicitly.

`scripts/prepare_supercop.py` verifies an existing pristine tree against the
lock or extracts the pinned archive into a new directory. A campaign copy is
created separately. Candidate installation, sticky-bit implementation
selection, compiler forcing, and custom `measure.c` replacement are allowed
only in the campaign copy.

`scripts/import_supercop_ntruplus.py` copies the pinned
`crypto_kem/ntruplus{864,1152}/avx2` directories into experiment `upstream/`
locations and records `UPSTREAM.json`. It refuses to overwrite an import.

## Optimization and symbol flow

Candidate symbols use a parameter and experiment namespace, for example
`ntruplus1152_exp_gt9x16_forward_small`. They must not collide with Official
`poly_ntt`, `poly_basemul`, `poly_invntt_scale`, or KEM API symbols while
being compared in local same-image harnesses.

The complete coefficient-domain multiplication contract is:

```text
coefficient a,b -> forward(a), forward(b) -> BaseMul -> inverse
                -> centered canonical output
```

`poly_mul_small` uses the KEM input envelope and may use proved lazy
reductions. `poly_mul_general` accepts arbitrary centered mod-q coefficients.
KEM integration preserves private NTT layouts across callers rather than
forcing every path through the complete wrapper. The shared contract is the
semantic `(branch,p,q,terminal-coefficient)` owner, terminal factor, scale,
range, and physical P/Q identities. YMM packing, retained split state,
materialization, and consumer epilogues may be caller-private.

Development proceeds through primitive differential tests, caller-complete
keygen/encapsulation/decapsulation polynomial islands, a namespaced candidate
KEM, and finally a flat SUPERCOP implementation. A generic `2F+B+I` island is
still a useful polynomial-multiplication gate, but it is not the universal KEM
integration milestone. Isolated wins do not skip these steps.

### Risk-tiered prototype workflow

ASM prototypes are cheaper to authorize than serious pricing or production.
Classify the change before deciding how much pre-ASM evidence to build:

| change class | examples | minimum pre-ASM path |
| --- | --- | --- |
| High risk | decomposition, representation/ABI, Q-order/ownership, scale or Montgomery domain | map -> exact schedule -> namespaced ASM |
| Medium risk | reduction placement, twist/twiddle absorption with unchanged output contract | small identity/range proof -> rough machine budget -> namespaced ASM |
| Low risk | same-DAG scheduling, register reuse, instruction selection, constant caching | namespaced ASM directly |

The medium-risk gate requires a proved or tightly scoped identity, an unchanged
input/output contract, a safe range argument, real structural credit, and no
evident routing, temporary, or spill debt. It does not require a complete
generated instruction schedule. The low-risk gate requires an independent
differential oracle but no separate map checkpoint.

Scale absorption proofs follow the complete linear DAG, including identity
branches and every add/sub merge. Rekeying only multiplication edges does not
establish a common output gauge when an untwiddled path reaches the same merge.
Require a full modular basis differential (or an equivalent linear proof) and
range replay before treating an existing twiddle or constant as a free scale
absorption site.

After authorization, the linked object is the source of truth for instruction,
constant-operand, spill, alignment, and footprint ledgers. If it contradicts a
symbolic estimate, preserve and correct the estimate; do not discard the
machine result. A short diagnostic benchmark may reject a low-risk prototype,
but cannot promote it.

Before serious pricing, every surviving candidate still closes the full
differential, range, ABI, constant-time, sanitizer, linked alignment/spill, and
same-ELF gates. Native SUPERCOP and production promotion requirements are not
weakened by this faster prototype workflow.

### GT pipeline checkpoint order

GT work treats forward, terminal arithmetic, and inverse as one physical-layout
design. After the scalar/permutation hypothesis is validated, proceed in this
order:

1. Compare linked GT compiler output against pinned Official `ntt.s`,
   `basemul.s`, `baseinv.s`, and `invntt.s`. Record calls, frames, vector stack
   traffic, `vzeroupper`, scalar loops, and materialization boundaries.
2. Generate a terminal-layout contract spanning forward output, BaseMul/BaseInv
   operands, and inverse input. Evaluate at least three layouts before selecting
   the next prototype ABI.
3. Implement shear, distance-8, and distances 4/2/1 as one leaf-ish explicit
   AVX2 NTT16 block. Do not call row helpers or canonicalize between layers.
4. Adapt Official's AVX2 radix-3 Montgomery schedule into one straight-line
   two-layer NTT9 baseline. It is a baseline; the next research step examines a
   fused radix-9 schedule and delayed/precombined reductions.
5. Build caller-native islands: Encap through MulAdd and serialization, Keygen
   through BaseInv and its tail, and Decap through BaseMul/BMScale and inverse.
   Qualify complete caller boundaries before any production claim.

For the 1152 experiment, Checkpoint C records both a faithful structural C0
and a split-representation C1 in `CHECKPOINT-C.md`. C0 is selected; C1 remains
as a correctness-validated performance rejection. The C0 register-only macro
is the required input boundary for step 4. No isolated island result changes
the SUPERCOP promotion gates.

Checkpoint C2 must precede NTT9 integration: pair terminal coefficients and
measure whether fuller Montgomery-lane utilization survives operand packing
and row reconstruction. If only an isolated stage wins while the complete
NTT16 pair regresses, pause radix-3 work and reassess the physical AVX2
orientation. The 1152 C2 result follows this rejection branch.

Before abandoning terminal pairing, test Official-style persistent S/D routing
through 128→64→32→16-bit granularities with only one final terminal-major
reconstruction. A winning row-pair result must next survive complete nine-row
skewed-shear integration; NTT9 remains paused until that gate passes.

The 1152 C4 gate passes when natural-input nine-row pair processing retains a
directional win with zero intermediate materialization and persistent S/D
output. After that result, reopen NTT9 only in a form that consumes persistent
S/D directly; a coefficient-major boundary does not qualify.

Official AVX2 leaves YMM registers caller-clobbered and returns without
`vzeroupper`. The candidate should remove unnecessary internal function
boundaries, not insert cleanup instructions. `vzeroupper` is considered only
for a measured outer AVX-to-legacy-SSE transition.

### Assembly alignment contract

Handwritten AVX2 source uses explicit power-of-two alignment. Function entries
and YMM constant tables default to `.p2align 5` (32 bytes). Constants live in
an aligned read-only section. Bare `.align` is forbidden because its meaning is
toolchain-dependent. A 64-byte entry (`.p2align 6`) or an aligned internal hot
target is a code-placement experiment: retain it only with recorded padding,
code size, symbol addresses, and paired evidence. Do not insert padding into a
straight-line fall-through path merely to make the source look aligned.

Code/constant alignment does not strengthen the public pointer ABI. Before
using `vmovdqa` or any other alignment-requiring memory operand on caller data,
prove the allocation and every byte offset for all native KEM invocations.
Otherwise use unaligned loads/stores. If a candidate creates vector stack
storage, separately prove stack alignment, ABI/unwind correctness, and that the
storage is not an avoidable spill.

The static audit records object/ELF section alignment, entry and hot-symbol
addresses modulo 32 and 64, constant-table alignment, padding, and code size.
Repeat that audit after flattening the candidate into a disposable SUPERCOP
implementation because link placement may change. Alignment variants remain
subject to reversed-link-order and ASLR-on/off fixed-ELF controls; a favorable
address is not an arithmetic credit.

Two timing views are retained. `full-real` includes all adapters, transposes,
and scatters that still execute. Component timings locate hotspots but never
exclude a real conversion from end-to-end comparison. A conversion reaches zero
cost only when adjacent producer/consumer schedules actually absorb it.

## Validation gates

Run gates in this order and stop at the first failure:

1. Generator reproducibility and generated-artifact hashes.
2. Scalar transform oracle versus schoolbook multiplication modulo
   `x^n-x^(n/2)+1`.
3. Forward, BaseMul, inverse, round-trip, and BaseInv differential tests.
4. Full small/general multiplication differentials.
5. Zero, impulse, monomial, alternating-bound, random, alias, and canary tests.
6. ASan/UBSan, strict warnings, assembly ABI/stack/spill/alignment audit.
7. Range, scale, constant-branch, and constant-index checks.
8. KAT byte-for-byte comparison.
9. Directional benchmark.
10. Native SUPERCOP, SUPERCOP-derived polynomial, and paired fixed-ELF runs.

## Benchmark layers

### Repository correctness

Repository tests provide fast differential, sanitizer, KAT, and audit gates.
Repository cycle results are diagnostic and cannot promote production.

### Native SUPERCOP KEM

Install Official and candidate as separate directories below
`crypto_kem/ntruplus{864,1152}/`. Run SUPERCOP `do-part` with one enabled
implementation at a time and the unmodified `crypto_kem/measure.c`. Preserve
`keypair_cycles`, `enc_cycles`, `dec_cycles`, the selected compiler, machine
data, run log, and SUPERCOP data file. Label these results
`supercop-native-kem`.

For this pinned 20260627 release, native `crypto_kem/measure.c` uses 32
successive timings and SUPERCOP builds it with `LOOPS=3`, producing 96 raw
observations per operation and process. Serious campaigns replay the exact
SUPERCOP-built measure ELF in 9 fresh pinned processes and pool 864
observations per operation. Report StQ1/StQ2/StQ3 using the release's
`include/stq.h` algorithm; StQ2 is the headline, not a repository median.

### SUPERCOP-derived polynomial

Native KEM measure does not expose polynomial primitives. A disposable
campaign may substitute `bench/supercop/poly_measure.c`, which uses SUPERCOP's
`cpucycles`, allocation, compiler-selection, and build machinery. It measures
small/general forward, BaseMul, inverse, BaseInv, and complete small/general
multiplication. Label the output `supercop-derived-poly`; it is not a public
native SUPERCOP result.

The derived measure mirrors the native timing geometry: 32 successive
`cpucycles()` deltas with the SUPERCOP-supplied `LOOPS=3`. It must not add a
sink or bookkeeping operation inside the measured interval. Serious derived
campaigns use the same 9-fresh-process and stabilized-quartile policy as native
KEM measurement.

### Host controls and provenance

Short SUPERCOP runs may record an uncontrolled host for debugging, but are not
formal evidence. Serious native and derived runs fail before compilation unless
the selected CPU uses the performance governor and turbo/boost is disabled.
Pin one known physical P-core and record its SMT siblings, core type when the
kernel exposes it, base/min/max frequencies, CPU model, and kernel. Never
silently write sysfs controls from a benchmark script.

Every fresh process must report one stable SUPERCOP identity: implementation,
compiler recipe, CPUID, `cpucycles_implementation`, and
`cpucycles_persecond`. Preserve the raw process outputs, the exact measure ELF
and SHA-256, pooled stabilized-quartile summary, SUPERCOP data file, run log,
lock file, and source hashes.

### Fixed-ELF paired replay

Save the SUPERCOP-built Official and candidate measure ELFs and record SHA-256,
compiler flags, section sizes and alignment, symbol addresses modulo 32/64,
release identity, and source tree hashes. Run 16 balanced blocks and 64
launches:

```text
odd:  Official Candidate Candidate Official
even: Candidate Official Official Candidate
```

Pin one physical P-core. Run PIE/ASLR-on and controlled `setarch -R` campaigns,
plus reversed link order or an equivalent placement control. Analyze paired
deltas from each launch's StQ2 and bootstrap confidence intervals. PMU counters explain results but
do not replace paired timing.

### Compiler policy

Report both normal SUPERCOP compiler selection and a common O3GC recipe
(`-O3`, function/data sections, linker section GC, and SUPERCOP architecture
flags). Native SUPERCOP must not regress; the common-compiler paired result
must show that the implementation rather than compiler choice caused the win.

## Experiment commands

Each parameter experiment exposes:

```text
make check
make sanitize
make audit
make supercop-check
make supercop-install-candidate
make supercop-kem-short
make supercop-kem-serious
make supercop-poly-short
make supercop-poly-serious
make supercop-paired-serious
make supercop-promotion-report
```

The main knobs are `SUPERCOP_ROOT`, `SUPERCOP_CAMPAIGN_ROOT`, `BENCH_CPU`,
`SUPERCOP_IMPLEMENTATION`, `RESULT_TAG`, `SUPERCOP_FRESH_LAUNCHES_SHORT`, and
`SUPERCOP_FRESH_LAUNCHES_SERIOUS`. Scripts derive repository paths
and never embed a user's home directory.

Omit `SUPERCOP_COMPILER_WRAPPER` for native SUPERCOP selection. Set it to
`bench/supercop/okc-o3gc.sh` for the common O3GC comparison; the runner backs
up and restores the campaign's `okc-amd64` selector and records its hash.

## Promotion and clean production

Promotion requires all correctness/security gates, a successful SUPERCOP
try/compile/measure, no unexplained native KEM regression, a full caller-path
win under the common compiler, placement agreement, an ASLR-off paired 95%
bootstrap interval below zero, and no reversed direction in ASLR-on runs.

Keygen, encapsulation, and decapsulation may use different source-resolved
winners. A failed candidate remains in the experiment. Qualified source is
cleaned into `NTRU+{864,1152}/clean/avx2-fastest-clean/` with no selector,
dead variant, experiment include, workspace symlink, or build-time generator.
Install a qualified tree as `avx2-fastest-clean` with
`scripts/install_supercop_clean.py`; the installer refuses nested or unqualified
clean trees and never overwrites an existing implementation.

## Release packaging

The development tree is not the release package. A non-overwriting exporter
creates `ntruplus-AVX2-Final/` in the KpqC layout, taking unchanged material
from the frozen package and AVX2 sources from qualified clean directories. It
dereferences allowed links, rejects workspace dependencies, excludes research
and raw results, generates manifests/checksums, and independently rebuilds and
runs all KATs before a tarball or release tag is created.

Release documentation records the SUPERCOP URL/version/archive hash, upstream
tree hashes, implementation names, native KEM results, derived polynomial
results, paired evidence, CPU, and compiler.

After both clean trees contain reviewed `SOURCE-MANIFEST.json` files, export
without overwriting an existing package:

```sh
python3 scripts/export_ntruplus_avx2_final.py \
  --destination /path/to/ntruplus-AVX2-Final \
  --qualification-report /path/to/promotion.json
```

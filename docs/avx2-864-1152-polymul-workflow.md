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
KEM integration should preserve private NTT layouts across callers rather than
forcing every path through the complete wrapper.

Development proceeds through primitive differential tests, a complete
`2F+B+I` island, a keygen/encap/decap polynomial island, a namespaced candidate
KEM, and finally a flat SUPERCOP implementation. Isolated wins do not skip
these steps.

## Validation gates

Run gates in this order and stop at the first failure:

1. Generator reproducibility and generated-artifact hashes.
2. Scalar transform oracle versus schoolbook multiplication modulo
   `x^n-x^(n/2)+1`.
3. Forward, BaseMul, inverse, round-trip, and BaseInv differential tests.
4. Full small/general multiplication differentials.
5. Zero, impulse, monomial, alternating-bound, random, alias, and canary tests.
6. ASan/UBSan, strict warnings, assembly ABI/stack/spill audit.
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

### SUPERCOP-derived polynomial

Native KEM measure does not expose polynomial primitives. A disposable
campaign may substitute `bench/supercop/poly_measure.c`, which uses SUPERCOP's
`cpucycles`, allocation, compiler-selection, and build machinery. It measures
small/general forward, BaseMul, inverse, BaseInv, and complete small/general
multiplication. Label the output `supercop-derived-poly`; it is not a public
native SUPERCOP result.

### Fixed-ELF paired replay

Save the SUPERCOP-built Official and candidate measure ELFs and record SHA-256,
compiler flags, section sizes, symbol addresses, release identity, and source
tree hashes. Run 16 balanced blocks and 64 launches:

```text
odd:  Official Candidate Candidate Official
even: Candidate Official Official Candidate
```

Pin one physical P-core. Run PIE/ASLR-on and controlled `setarch -R` campaigns,
plus reversed link order or an equivalent placement control. Analyze paired
deltas and bootstrap confidence intervals. PMU counters explain results but
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
`SUPERCOP_IMPLEMENTATION`, and `RESULT_TAG`. Scripts derive repository paths
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

# GT768 AArch64 scalar Keccak-f[1600] experiment

Experiment ID: `gt768-keccak-x1-scalar-20260911-e40`

Baseline: `aarch64-production` at
`f14cc9b84ebfd69c460efbcb2a0da887d4b90677`.

Candidate branch: `codex/gt768-keccak-x1-scalar-20260911-e40`.

The public `shake256()` and `hash_f/g/h()` interfaces and implementations are
unchanged.  The candidate replaces only the internal Keccak-f[1600]
permutation with the supplied mlkem-native scalar AArch64 x1 assembly kernel.

The supplied source matches mlkem-native revision
`0924122d0e92b2d682fab5d5e5e2593ec84c8a1f` byte-for-byte except for its final
newline.  The upstream source SHA-256 is
`62134e210376a567c53d460ebeb7feee648eac1d77d8ea2d587f5d89c7ccfeef`.
Upstream associates this routine with a HOL-Light proof artifact.  This report
does not claim that the locally namespaced/section-adapted copy was separately
formally verified.

## Gates

- Mac AArch64 KEM round trip: pass (100 iterations).
- Mac AArch64 ABI sentinel: pass.
- Mac canonical and small-input differential tests: pass.
- Mac zeroization audit: pass.
- KAT response SHA-256: `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8` (exact match).
- Pi 5 package/KAT/ABI gate: pass.
- Pi 5 paired benchmark: pass; no throttling (`0x0`).

## Pi 5 component benchmark

Host: `pi@100.99.191.9`, Linux 6.18.33+rpt-rpi-2712, GCC 14.2.0,
core 3.  Each variant used 62 samples, 2,000 operations/sample and 100
warmups/run in both execution orders.

| Component | GT portable C | Scalar asm | Saved | Improvement |
|---|---:|---:|---:|---:|
| SHAKE coins (`32 -> 192`) | 2,722 | 2,216 | 506 | 18.59% |
| `hash_f` | 11,907 | 9,671 | 2,236 | 18.78% |
| `hash_g` | 13,194 | 10,710 | 2,484 | 18.83% |
| `hash_h` | 2,772 | 2,261 | 511 | 18.43% |

The four paths imply approximately 248--256 cycles saved per Keccak-f[1600]
call.  Their sums predict the full-KEM changes to within 15 cycles.

## Pi 5 full KEM benchmark

This is the same SUPERCOP-style harness and link contract used for the GT
production package: 62 samples/variant, 2,000 operations/sample, 100 warmups,
core 3 and both execution orders.

The reused harness's machine-readable labels are historical: `Official`
means the GT production portable-C baseline here, and `GT-Polynomial` means
the otherwise-identical scalar-assembly candidate.

| Operation | GT portable C | Scalar asm | Saved | Improvement |
|---|---:|---:|---:|---:|
| Keygen | 36,348 | 33,095 | 3,253 | 8.95% |
| Encap | 37,212 | 31,993 | 5,219 | 14.03% |
| Decap | 32,082 | 29,079 | 3,003 | 9.36% |

The KEM call graph predicts 3,248/5,231/2,995 saved cycles from the component
measurements, confirming that the full result comes from the permutation
replacement.  PMU medians show instruction reductions of about 16,833,
27,181 and 15,537 per Keygen/Encap/Decap.  Loads fall by approximately
63%/72%/67%, consistent with retaining the 25 state lanes in registers instead
of the compiler-generated C permutation's round-time materialization.

Linked `KeccakF1600_StatePermute` is 1,600 bytes in the baseline.  The new
assembly body is 1,152 bytes, and total linked text changes from 81,377 to
81,057 bytes (320 bytes smaller).

After replacing the temporary `#if 0` with the explicit AArch64 backend
selection, the Pi package/test/KAT gate was rerun.  The pre-cleanup and final
linked `.text` SHA-256 values are both
`432570cc3cae7038de633121f287a580646f52b1d40c22337026aa948f1ea0ee`;
the cleanup therefore does not change the measured AArch64 executable.

Initial decision after measurement: **keep-experimental, promotion
recommended**, pending explicit promotion approval.  That approval and the
additional promotion preflight are recorded below.

## Exact-commit rerun

Commit `ec26b4a7cb28ee31483fc0e01314bd6287bd098e` was subsequently rebuilt
from fresh SUPERCOP leaves and rerun on the same Pi 5.  The full package
`make check` passed, including 100 KEM round trips, ABI, 9,216 canonical
boundary cases, 4,096 small-input cases, zeroization checks, and byte-identical
KAT request/response files.

| Operation | GT portable C | Scalar asm | Saved | Improvement |
|---|---:|---:|---:|---:|
| Keygen | 36,346 | 33,092 | 3,254 | 8.95% |
| Encap | 37,329 | 31,982 | 5,347 | 14.32% |
| Decap | 32,088 | 29,078 | 3,010 | 9.38% |

The run used 62 samples/variant, 2,000 operations/sample, 100 warmups and
both execution orders.  The host remained at `throttled=0x0`; temperature was
59.3--65.3 C.  Linked text remained 81,377 bytes for the portable-C baseline
and 81,057 bytes for the assembly candidate.

## Promotion preflight

- Apple Clang 21 built the full package and passed KAT, KEM, ABI, canonical,
  small-input and zeroization gates.
- GCC 14.2 built the full package with `-march=armv8-a` and passed the same
  gates, including byte-identical KAT output.
- Apple Clang cross-assembled `keccakf1600.S` for the generic
  `aarch64-linux-gnu`/`armv8-a` target.
- Source and linked-opcode audits found no Armv8.2 SHA3 instructions
  (`eor3`, `rax1`, `xar`, or `bcax`).
- The private symbol is `ntruplus_keccak_f1600_x1_aarch64`; it does not imply
  a SHA3-extension requirement and avoids the generic upstream namespace.

The promotion decision is **accepted**.  The previous production champion is
`f14cc9b84ebfd69c460efbcb2a0da887d4b90677`.  The final promotion-ready code
revision is recorded in `iteration.yml` after this preflight commit.

Raw binaries, samples, disassembly, and PMU logs are ephemeral and belong in
the gitignored `.build/` directory locally and under the matching experiment
directory on the Pi 5.

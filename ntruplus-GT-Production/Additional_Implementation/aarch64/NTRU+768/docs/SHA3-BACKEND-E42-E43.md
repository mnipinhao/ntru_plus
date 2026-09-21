# NTRU+768 SHA3 backend experiments E42/E43

Date: 2026-09-15

## Revisions and policy

- Champion before E42: `aarch64-production` at
  `3b889be0999ededf602a93c1f811504988dda766`.
- E42 experiment ID/branch: `gt768-ce-keccak-v84a-20260915-e42` /
  `codex/gt768-ce-keccak-v84a-20260915-e42`.
- E42 candidate commit: `58790554` (`aarch64: add SHA3-gated Keccak x1 backend`).
- E43 experiment ID/branch: `gt768-fused-shake-v84a-20260915-e43` /
  `codex/gt768-fused-shake-v84a-20260915-e43`.
- E43 candidate commit: `b5036b82` (`aarch64: fuse SHA3 hash-g sponge`).
- Decision: E42 and E43 are accepted on the experiment chain, but remain off
  `aarch64-production` pending an explicit promotion request.

The compile-time selector is `__ARM_FEATURE_SHA3`. SHA3 builds use the
namespaced v8.4-A x1 and fixed `hash_g` backends. Other AArch64 builds retain
the existing scalar implementations. No runtime dispatch is added.

The v8.4-A round body comes from `pq-code-package/mlkem-native` revision
`438f0da19dc3d5299bb2e318d1067f9a298f1bcf`; generated upstream source SHA-256
is `8f7841f3c130549ccc64af236e8b8d6f811cba1cdafd83a8b12424476973d3da`.
The fused NTRU+ integration has not itself been formally verified.

## Correctness evidence

- M2 Pro SHA3 build: package `make check` passed, including 100 KEM round
  trips, ABI, 9,216 canonical-boundary cases, 4,096 small-NTT cases,
  zeroization audit, and byte-exact KAT.
- Forced scalar fallback (`-U__ARM_FEATURE_SHA3`): KEM, ABI, and byte-exact KAT
  passed on the M2 Pro.
- E43 targeted `hash_g`: 4,096 non-alias plus 4,096 `out == input` random
  differential cases passed against the portable C Keccak oracle.
- Pi 5/Cortex-A76 fallback: full package `make check` passed; linked symbols
  contain only the scalar x1 and scalar fused `hash_g`; throttling was `0x0`.
- KAT response SHA-256:
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

## M2 Pro performance

Host: Apple M2 Pro `Mac14,9`, macOS 26.4.1, Apple clang 21.0.0.
Both SHA3 feature sysctls are enabled. Measurements use `mach_absolute_time`,
rotated execution order, deterministic KEM inputs, warmups, and p50 in ns/op.

E42 versus the scalar production hash backend (median of three run p50s):

| Operation | Scalar production | E42 x1 v8.4-A | Change |
| --- | ---: | ---: | ---: |
| Keygen | 10,510 | 8,128 | -22.7% |
| Encap | 9,473 | 7,537 | -20.4% |
| Decap | 8,140 | 7,742 | -4.9% |

E43 isolates the fixed `hash_g` seam. Five-run median p50:

| `hash_g` | E42 scalar fused | E43 v8.4-A fused | Change |
| --- | ---: | ---: | ---: |
| ns/op | 3,442 | 1,540 | -55.3% |

Relative to E42, E43 complete-KEM median-of-three p50 is:

| Operation | E42 | E43 | Change |
| --- | ---: | ---: | ---: |
| Keygen | 8,604 | 8,412 | -2.2% |
| Encap | 7,584 | 5,840 | -23.0% |
| Decap | 7,783 | 6,021 | -22.6% |

The small Keygen delta is treated as noise/control because Keygen does not call
`hash_g`. Compared with the scalar production measurements above, the complete
E43 chain improves Keygen by about 20.0%, Encap by 38.4%, and Decap by 26.0%
on this SHA3-capable host. These are M2-specific latency results, not Pi 5
claims; Pi 5 intentionally retains the scalar path.

## Static effect

- E42 adds the 428-byte standalone v8.4-A permutation body.
- E43 keeps 25 lanes live across all ten fixed `hash_g` permutations and
  removes intermediate state store/reload boundaries.
- The E43 linked test binary adds 920 bytes of Mach-O `__text` over E42.
- The E43 v8.4-A object contains 1,540 bytes of text for standalone, shared
  live-state round body, and fused `hash_g` together.
- The candidate has no hidden spill: the live state occupies `v0-v24`, with
  `v25-v31` used by the round/absorb frontend; AAPCS64 `d8-d15` are preserved
  in an 80-byte aligned frame and the live vector state is cleared on return.

Ephemeral objects, binaries, raw samples, and differential harnesses remain in
the gitignored worktree experiment directories and are not committed.

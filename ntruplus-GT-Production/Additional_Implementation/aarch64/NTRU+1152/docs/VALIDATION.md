# NTRU+1152 AArch64 — what `make check` verifies

Every gate below runs from one `make check`, and each one fails the build rather
than printing a warning.

| gate | what it establishes |
|---|---|
| `check-release` | the tree contains sources and nothing else: no build products, no result files, and no reference to a path outside it. Also pins the expected KAT hash |
| `manifest-check` | every shipped file matches `SOURCE-MANIFEST.sha256` |
| `zeroization-source-check` | the clears are present in source — the barrier in `secure_clear.h`, the C call sites, the 2,304-byte inverse scratch wipe, and all thirty-two SIMD register wipes, enumerated rather than sampled |
| `check-inplace` | `packed_i9`'s nine data loads all retire before its first store, which is the precondition that lets `inverse_ntt.S` overlay the rebase buffer on the scratch |
| `test_kem` | 64 round trips plus tampered-ciphertext rejection |
| `test_canonical` | 13,824 boundary cases of the canonical decoder |
| `test_abi` | AAPCS64 sentinels on every public entry point |
| `test_baseinv_fail` | all 288 non-invertible leaves reject and clear, aliased and not |
| `test_zeroization` | the audited clears observe zero bytes afterwards |
| `kat-check` | the generated KAT is byte-identical to `kat/expected/` |
| `export-check` | the SUPERCOP leaf regenerates deterministically |

## Two gates that exist because something was missed

`zeroization-source-check` was added after a rewrite of `inverse_ntt.S` silently
dropped the thirty-two SIMD register wipes and nothing caught it for eight
gates: the runtime audit hook only fires inside the C clear primitive and cannot
see stores emitted by assembly, and the ABI sentinels check that callee-saved
registers are *preserved*, which is a different property from volatile ones
being *erased*. It pins the register wipes individually for that reason.

`check-inplace` guards a property of the current SLOTHY schedule, not of the
algorithm. A future scheduling pass is free to interleave the loads and stores,
and the result would be silent corruption; this fails the build instead.

## Scratch ownership

No assembly leaf in this tree allocates working memory the C caller cannot
reach. `ntt.S` and `inverse_ntt.S` take their scratch as an argument, so the
transform's intermediates live in a buffer `api_glue.c` declares and can clear —
the arrangement mlkem-native's kernels use. `ntt.S`'s buffer is cleared in C;
`inverse_ntt.S` clears its own, being the last thing to touch it.

## Cleanup policy

This package follows the same Official-aligned policy NTRU+768 adopted, rather
than the former P0-B full-frame policy.

- Secret **data** with a lifetime is still cleared in C: keys, inverses, coins,
  messages, hash buffers and the polynomials derived from them, through
  `secure_clear`, which is a plain clear plus a compiler barrier on every
  non-Windows platform.
- Assembly **working frames are not wiped.** The leaves take their scratch from
  the caller rather than allocating it, so nothing they touch is unreachable
  from C, but the buffer itself is not erased.
- **Volatile SIMD registers are still erased** at the inverse boundary. That is
  a deliberate exception: it costs one cycle, and unlike a stack frame, register
  state is not overwritten by whatever runs next.

The frame wipes were measured before being retired. At the wipe's own boundary
the scratch does survive the call -- probing the stack immediately after
`poly_invntt_ternary` finds the full 1,152-halfword scratch intact without it,
and 31 halfwords with it. But by the time decapsulation returns, the transform,
basemul, two hashes and the serializer that follow have overwritten the same
region either way: 64 halfwords of recognisable residue, with the wipe and
without. The window in which the wipe changes anything is the few thousand
cycles between the inverse returning and the next write to that stack.

Removing them costs nothing in coverage that survives the call and returns
about 540 cycles on NTRU+864 and 320 on NTRU+1152 decapsulation.

There is no promise to erase handwritten spill frames. This is not a proof
about compiler copies, caches, swap, or microarchitectural remanence.

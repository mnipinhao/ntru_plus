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

# NTRU+1152 AArch64 — what `make check` verifies

Every gate below runs from one `make check`, and each one fails the build rather
than printing a warning.

| gate | what it establishes |
|---|---|
| `check-release` | the tree contains sources and nothing else: no build products, no result files, and no reference to a path outside it. Also pins the expected KAT hash |
| `manifest-check` | every shipped file matches `SOURCE-MANIFEST.sha256` |
| `zeroization-source-check` | the clears are present in source — the barrier in `secure_clear.h`, the C call sites including the decapsulation `io` union that holds the inverse scratch, the declassify sites, the absence of a baseinv failure branch, and all thirty-two SIMD register wipes, enumerated rather than sampled |
| `test_kem` | 64 round trips plus tampered-ciphertext rejection |
| `test_canonical` | 13,824 boundary cases of the canonical decoder |
| `test_abi` | AAPCS64 sentinels on every public entry point |
| `test_baseinv_fail` | all 288 non-invertible leaves reject and clear, aliased and not |
| `test_zeroization` | the audited clears observe zero bytes afterwards |
| `kat-check` | the generated KAT is byte-identical to `kat/expected/` |
| `export-check` | the SUPERCOP leaf regenerates deterministically |

## A gate that exists because something was missed

`zeroization-source-check` was added after a rewrite of `inverse_ntt.S` silently
dropped the thirty-two SIMD register wipes and nothing caught it for eight
gates: the runtime audit hook only fires inside the C clear primitive and cannot
see stores emitted by assembly, and the ABI sentinels check that callee-saved
registers are *preserved*, which is a different property from volatile ones
being *erased*. It pins the register wipes individually for that reason.

A second gate, `check-inplace`, guarded the in-place overlay of the rebase
buffer on the scratch.  It was retired with the rebase itself (P126):
`packed_i9` now reads `basemul_rinv`'s output and writes the scratch, which do
not overlap.

## Batch inversion's fqmul (P128, 2026-09-23)

`baseinv`'s prefix, inversion and recovery chains are serial, so they are
latency-bound.  Their `fqmul` now takes the Montgomery quotient from the low
half of the product (`mul`), as Official's does, instead of `uzp1` of the
widened product: one permute fewer on every step of a ~40-step chain.
`baseinv` on M2 550 -> 517 ns (Official 532); A76 +44 cycles a call.  Key
generation: **M2 -90 ns (-1.44%)**, A76 +195 cycles (+0.36%), which lands under
the roadmap's rule 2.

## Rebase folded into basemul_rinv (P126, 2026-09-23)

`basemul_rinv` now writes the inverse's (component, half) lane basis itself,
so the separate `p65_rebase` pass (432 `trn`, a load/store pass) and the
`check-inplace` gate are gone.  One iteration takes the two halves of one
(j, tg); the Montgomery narrowing `uzp2` becomes a `trn2` of two components,
and `zip.4s`/`zip.2d` finish the transpose.  The kernel is generated in
`dev/ntruplus1152_clean` and scheduled for the A76 in `dev/ntruplus1152_opt`.

Decapsulation, min of blocks: M2 -18.5 ns (-0.37%); A76 unchanged (+-50
cycles).  The inverse itself is 283 A76 cycles and 30-42 ns faster; the
basemul pays most of it back on the A76, whose dispatch splits permutes evenly
over both vector pipes even when V0 is saturated by multiplies (16 `smull` +
16 `zip` take 23 cycles, not 16).  KAT, TIMECOP (`-O`..`-Os`) and the P125
range proof are unchanged.

## Constant time and range proof (P124-P125, 2026-09-23)

- **SUPERCOP TIMECOP passes** (20260831, valgrind 3.24.0 with `libc6-dbg`,
  Pi 5, `TIMECOP=256`) at `-O`, `-O2`, `-O3` and `-Os`, with SUPERCOP's own
  checksum `2275d102...`.  Before this change the leaf failed on the
  secret-key decode status in Decaps and on BaseInv's failure branch.
  Official's 1152 leaf fails too, on `poly_fqinv_batch`.
- Both status bits are declassified, as Official does.  BaseInv keeps its early
  exit, after declassifying: 29% of 1152's f and g candidates are
  non-invertible (27% for g), and a branch-free failure path cost keygen 1.1%
  on A76.  864, whose candidates practically never fail, is branch-free.
- The inverse's 2,304-byte scratch is part of `kem.c`'s `io` union, overlaid on
  `buf1`/`buf3` and cleared with them on exit, at no extra cost.
- **Range proof of the linked inverse** (interval interpreter over the
  executable's disassembly, `experiments/gt-p125-864-1152-range-proof`): for
  every input with |x| <= 2458 (the canonical product bound) no intermediate
  leaves int16 (peak 22,122 in `packed_i9`), the output is in {-1,0,1}, and
  the largest input to `crepmod3`'s single q-correction is 5,178.  That
  correction is exact up to 5,185, so the margin is 7; the proof holds up to
  |x| <= 2,501, which covers the inherited 2,497 contract.  No never-written
  scratch is read.

## Scratch ownership

No assembly leaf in this tree allocates working memory the C caller cannot
reach. `ntt.S` and `inverse_ntt.S` take their scratch as an argument, so the
transform's intermediates live in a buffer `api_glue.c` declares and can clear —
the arrangement mlkem-native's kernels use.  Neither leaf clears its buffer;
decapsulation's inverse scratch is part of `kem.c`'s cleared `io` union.

## Cleanup policy

This package follows the same Official-aligned policy NTRU+768 adopted, rather
than the former P0-B full-frame policy.

- Secret **data** with a lifetime is still cleared in C: keys, inverses, coins,
  messages, hash buffers and the polynomials derived from them, through
  `secure_clear`, which is a plain clear plus a compiler barrier on every
  non-Windows platform.
- Assembly **working frames are not wiped.** The leaves take their scratch from
  the caller rather than allocating it, so nothing they touch is unreachable
  from C, but the buffer itself is not erased.  The one exception costs
  nothing: decapsulation's inverse takes its scratch from `kem.c`'s `io` union,
  which overlays `buf1` and `buf3` (first written after the inverse) and is
  cleared with them on exit.
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

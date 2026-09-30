# NTRU+864 for AArch64: implementation notes

The KEM flow is Official's (`kem.c`). Key generation samples f and g, maps them
to the transform domain and inverts them there; encapsulation and decapsulation
use transform-domain products, and decapsulation inverts the transform with the
ternary reduction fused in. This page records the contracts between the
kernels, the bounds they rely on, what `make check` verifies, and the
constant-time and cleanup policy.

## Representations

Polynomials are `int16_t[864]` in R_q = Z_q[X]/(X^864 - X^432 + 1), q = 3457.
Transform-domain coefficients are in the Good-Thomas (GT) order, not wire
order. Montgomery scales are written R^k with R = 2^16: an "R0" value carries
no factor, an "R^-1" value one factor R^-1.

| Kernel | Input | Output |
|---|---|---|
| `poly_ntt` (Forward) | every coefficient in [-3, 4] | transform domain, R0, not reduced |
| `poly_baseinv` | Forward output, abs <= 28,765 | the inverse of every leaf, R0, abs <= 2,550 (not centered); returns 1 and clears the output if a leaf is not invertible |
| `poly_basemul`, `poly_basemul_add` | transform domain, R0 | R0, in [-3023, 3023] |
| `poly_basemul_rinv` | decoded bytes, in [0, 4095] | R^-1, abs <= 2,497; decapsulation's first product only |
| `poly_invntt_ternary` | the output of `poly_basemul_rinv` | coefficient domain, in {-1, 0, 1} |
| `poly_frombytes` | 1,296 bytes | the decoded coefficients; returns 1 if any is `>= q` |

The Forward kernel's first split multiplies without reduction, so it requires
every input coefficient in [-3, 4]. The KEM's inputs (f, g, r, the encoded
message and the recovered m) all satisfy this; it is not a general polynomial
transform.

## Decapsulation inverse

`poly_invntt_ternary` (`inverse.S`, `inverse9.S`, `inverse16_paired.S`,
`inverse_tail_direct.S`, `inverse_route.S`, `inverse*_tables.h`) inverts the
transform and reduces to {-1, 0, 1} in one pass. It consumes the R^-1 output of
the first product directly; the R^-1 factor is folded into its final
constants.

- **Ternary reduction.** The map from a raw coefficient to {-1, 0, 1} uses a
  single correction by q, which is exact for abs <= 5,185 because q = 1
  (mod 3); the first failure is at +-5,186 (exhaustive check over `int16_t`).
- **Cooley-Tukey 16-point stages.** Decimation in time absorbs the bit
  reversal into the coordinate order, so no permutation pass is needed, and it
  stays inside `int16_t` at the stage input bound 3,456, where a Gentleman-Sande
  sum path would reach 55,296.
- **FEAT_RDM.** The final merge uses `sqrdmlah` when the compiler targets
  FEAT_RDM (`__ARM_FEATURE_QRDMX`) and `sqrdmulh` plus `add` otherwise, so
  Armv8.0 cores (Cortex-A53, Cortex-A72) run it too. The SUPERCOP leaf always
  carries the Armv8.0 form.
- **Range.** An interval analysis of the linked executable's disassembly, with
  the exact error of every constant pair, shows that for every input with
  abs <= 2,497 no intermediate value leaves `int16_t` (peak 22,473), the output
  is in {-1, 0, 1}, and every input to the ternary map has abs <= 4,482, inside
  the 5,185 above. The analysis holds up to abs <= 3,640. The analysis tool is
  not part of this package.
- **Scratch.** 1,792 bytes, owned by the caller: `kem.c` overlays it on buffers
  that decapsulation clears before it returns.

## Batch inversion

`poly_baseinv` (`inverse.S` with `baseinv_num.S`, `baseinv_prefix.S`,
`baseinv_inverse.S`, `baseinv_recover.S` and `baseinv_finish.S`) inverts the 288
leaves Z_q[X]/(X^3 - zeta) of the transform domain with one field inversion:
numerators and norms per leaf, prefix products, one inversion, the recovery of
each inverse, and the final scaling. It reads the Forward output directly,
without conversion to Official's layout, and the Montgomery scales of its steps
cancel up to one global correction. A leaf is not invertible exactly when its
norm is zero. The function then zeroes its output on the same path and returns
1; key generation declassifies that bit and draws a new sample, as Official
does.

## Serialization

`pack.c` serializes a transform-domain polynomial, with the tables in
`pack6.h`. The coefficients are in GT order, so the serializer both packs
12-bit values and applies the fixed GT-to-wire permutation. One twelve-byte
block's eight coefficients sit at two lanes of eight vectors, so no transpose
delivers a block. The unit is the **run** instead: six consecutive wire
coefficients in the same lane of six vectors, 72 bits, nine bytes.

- 18 groups of six vectors (`pack6_vec`). Lane j of a group is one run for
  every j, so a group yields eight runs, and the 144 runs tile the 1,296-byte
  output exactly (`pack6_off`).
- Per group: six loads, the reduction below, `fold6` (six coefficients into
  five halfwords, seven instructions), and an 8x8 halfword transpose that puts
  each run in its own vector.
- A run is nine live bytes of a sixteen-byte vector. Where possible it takes one
  16-byte store and lets the seven extra bytes land in a neighbouring run that
  is written later and overwrites them: kind 1 stores at the run's offset, kind
  2 stores ending at the run's last byte (`ext` by 9 first), and kind 0 uses an
  8-byte and a 1-byte store. 113 runs take one store (72 kind 1, 41 kind 2) and
  31 take two: 175 stores in place of 288.
- The group order, the lane order within each group and the kind of every run
  (`pack6_order`, `pack6_lane`, `pack6_store`) were generated by a script that
  also simulated every byte write and checked that each of the 1,296 bytes is
  last written by the run it belongs to and that no store leaves the buffer.
  The script is not part of this package. The loops are fully unrolled over
  these constant tables, so every store is fixed at compile time and there is no
  data-dependent branch.

| Entry | Input | Reduction per vector | KEM callers |
|---|---|---|---|
| `poly_tobytes` | any `int16_t` | Barrett (rounding multiply-high by 9, multiply-subtract by q, landing in (-q, q)), then `add q` and an unsigned minimum | f in key generation; r in encapsulation, through `hash_g_fr0`; the re-encryption in decapsulation |
| `poly_tobytes_small` | every coefficient in (-q, q) | `add q` and an unsigned minimum | h and f * g^-1 in key generation; c in encapsulation; the second product in decapsulation |

- The unsigned minimum is exact on (-q, q): a non-negative value is below q and
  is its own minimum, while a negative value wraps to at least 2^16 - 3456 and
  its sum with q lands in (0, q).
- The small entry's inputs are the outputs of `poly_basemul` and
  `poly_basemul_add`, whose final reduction (signed 32-bit `sqrdmulh` by
  621,199, multiply-subtract by 3,457, narrow) lands in [-3023, 3023] for every
  32-bit accumulator (exact enumeration of the quotient intervals). Forward
  outputs have counterexamples and must use the full entry.
- `poly_frombytes` (`unpack.c`) is the exact inverse: one 16-byte load per run,
  one `tbl` expanding it to six halfwords, an 8x8 halfword transpose, and one
  `and` or `ushr` per vector. It returns 1 if any coefficient is `>= q`.
- Input and output must be disjoint; loads and stores use public pointers and
  constant offsets, and no coefficient reaches a general-purpose register, a
  branch or an address. Neither direction allocates scratch.

## Hashing

SHAKE256 is the public-domain sponge in `fips202.c` over mlkem-native's
Keccak-f[1600] permutations: `keccakf1600.S` (scalar), `keccakf1600_v84a.S`
(FEAT_SHA3, used when the compiler targets it) and `keccakf1600_x2_v84a.S` (two
states at once, FEAT_SHA3). NTRU+768 and NTRU+1152 carry the same three files.

- `shake256_prefixed` absorbs a domain byte and a message without building
  their concatenation; `hash_f`, `hash_g` and `hash_h` use it.
- Key generation expands the seeds of f and g with `shake256_x2`, which
  permutes both states at once with FEAT_SHA3 and makes two single-state calls
  otherwise. It draws the next seed before trying f, so `randombytes` sees the
  same calls in the same order as with Official.
- `hash_g_fr0` serializes r with the full entry into a local buffer and hashes
  it with the prefixed sponge, so r's bytes never pass through the ciphertext
  buffer.
- SUPERCOP builds (`-DSUPERCOP`) always use the scalar permutation, the only one
  the exported leaf carries.

## Validation

`make check` runs:

| Target | Checks |
|---|---|
| `manifest-check` | the tree holds only release files (`scripts/check_release.py`) and every file matches `SOURCE-MANIFEST.sha256` |
| `test` | 64 key pairs, encapsulations and decapsulations, each followed by a tampered ciphertext (`test_kem`); callee-saved registers across the KEM functions, the kernels and the Keccak permutations (`test_abi`); rejection with a cleared output for a non-invertible leaf at each of the 288 positions, with and without aliasing (`test_baseinv_fail`) |
| `canonical` | a coefficient q, q + 1 or 4095 at each of the 864 positions of pk, ct and both halves of sk is rejected with cleared outputs (`test_canonical`, 10,368 cases) |
| `zeroization` | the clear sites in the sources (`scripts/check_zeroization.py`) and, at run time, that the clears leave zeros (`test_zeroization`) |
| `kat-check` | the generated KAT equals `kat/expected/`, Official's vectors |
| `export-check` | the SUPERCOP export is deterministic |
| `keccak-v84a` | the FEAT_SHA3 permutation equals the scalar one on 100,003 states (skipped without FEAT_SHA3) |
| `shake-prefixed` | `shake256_prefixed` equals `shake256` over the built concatenation |

## Constant time

- SUPERCOP's TIMECOP (`TIMECOP=256`) passes for the exported leaf at `-O`,
  `-O2`, `-O3` and `-Os`.
- The only values declassified are the two that Official releases by design:
  whether a secret key decodes canonically (decapsulation) and whether a key
  generation sample is invertible (key generation retries).
- Branches and memory addresses depend only on public data; tables are indexed
  by public constants.

## Cleanup policy

- Secret data with a lifetime is cleared in C with `secure_clear` (a plain
  clear and a compiler barrier; `SecureZeroMemory` on Windows): keys, inverses,
  coins, messages, hash buffers and the polynomials derived from them. The
  generic SHAKE API also wipes its state and buffers.
- Kernel working buffers are not wiped. The Forward transform and the batch
  inversion take their scratch from wrappers in `api_glue.c`, so no kernel
  allocates memory that C cannot reach, but that scratch is not erased.
  Decapsulation's inverse takes its scratch from `kem.c`, which overlays it on
  buffers that are first written after the inverse and cleared on exit.
- The inverse erases the SIMD registers (v0-v31) before it returns: register
  state, unlike a stack frame, is not overwritten by the code that runs next.
- There is no promise about stack frames, compiler spill slots, caches, swap or
  microarchitectural state.

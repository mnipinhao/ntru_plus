# NTRU+864 for x86-64 AVX2 (avx2-opt): implementation notes

## 1. Scope

This package is Official NTRU+ AVX2 with the changes listed below, derived from
SUPERCOP 20260831's `crypto_kem/ntruplus864/avx2` leaf. **Official**, the
baseline of every figure, is defined in [`../../README.md`](../../README.md),
section Official. The external behaviour is Official's: pk, sk, ct, ss and the
decapsulation rejection are byte-identical, and `kat/expected/` holds
Official's KAT (main's `KAT/NTRU+864/PQCkemKAT_2624.rsp`, sha256
`0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`).

Against Official, the package:

- binds each KEM call directly to its kernel (section 2) and replaces the
  kernels of sections 3 to 6;
- replaces the Keccak backend (section 7);
- adds one `vzeroupper` at each entry point's exit (section 9);
- names files and functions by what they do and prefixes every global symbol
  except the three NIST entry points (section 9);
- drops the code the entry points never reach and the twiddle-table entries no
  kernel reads, which moves some table offsets (section 12).

The symbolic executions, interval replays and exhaustive checks cited below
were run with tools that are not part of this package; the tests in `test/`
and the KAT check are.

## 2. KEM data flow

The flow is Official `kem.c`. Each call binds directly to its function:

| Call site | Official | this package |
|---|---|---|
| Forward NTT: keygen f, g; Encap r, m; Decap f', re-encryption r (6 calls) | `poly_ntt` | `poly_ntt` (lazy, section 3) |
| BaseInv of f, g | `poly_baseinv` | `poly_baseinv` (output x R, section 4) |
| keygen products `h = g*finv`, `f*ginv` | `poly_basemul` | `poly_basemul_montgomery` (x R^-1, cancels that R) |
| Encap `c = h*r`; Decap `(c - f')*hinv` | `poly_basemul` | `poly_basemul_shoup` (section 4) |
| Decap `m = c*f` | `poly_basemul_scale` | unchanged |
| Decap `poly_invntt_scale(&m); poly_crepmod3(&m);` | two calls | `poly_invntt_crepmod3(&m)` (section 5) |
| `poly_tobytes` / `poly_frombytes` | `pack.s` | section 6 |
| SHAKE256 (`hash_f/g/h`, keygen seed expansion) | XKCP AVX2 Keccak | mlkem-native x1 Keccak (docs/KECCAK.md) |

The Shoup call puts its canonical operand last: `poly_basemul_shoup(&c, &r, &h)`
and `poly_basemul_shoup(&f, &c, &hinv)`.

## 3. Forward NTT (`ntt.s`)

`poly_ntt` computes Official `poly_ntt`'s output up to the terminal Barrett
reduction. Official's arithmetic is kept instruction for instruction. Two
changes affect only data movement and scheduling:

- level 0 and the first radix-3 level run fused in one pass;
- levels 3..6 run as one pass per block of coefficients (the block pass), which
  exchanges data through a network of `vpunpck` stages and one `vperm2i128`
  stage, with its own twiddle tables in `ntt.s`.

The output is bit-identical to Official `poly_ntt` without its final `#reduce2`
block, for every int16 input (symbolic execution). It equals Official's output
modulo q. It is **not reduced**, so the function is valid only for the KEM's
caller domains. For each caller, the output range was proved by per-lane
interval replay of the assembly:

| caller | proven output range |
|---|---|
| keygen f | [-17193, 17194] |
| keygen g | [-17193, 17193] |
| Encap r, m and Decap re-encryption r | [-15580, 15580] |
| Decap f' = poly_ntt(crepmod3 output) | [-16382, 16385] |

Every consumer stays in int16. BaseInv and the BaseMul variants accept these
envelopes (section 4), `poly_sub(c, f')` stays within the Decap Shoup envelope,
and `poly_tobytes` is canonical for every int16 input.

## 4. Base multiplication and inversion

**`poly_baseinv` (`baseinv.c`, `baseinv_1.s`).** This is Official's hierarchical
batch inversion (Kim-Cho-Park, ePrint 2026/1191) with one constant changed: the
fqinv input scale is R^2 instead of R^3. The output is therefore Official's inverse
times R (mod q), with the same bounds. Non-invertibility returns 1 and zeroes r,
exactly as Official does.

**`poly_basemul_montgomery` (`basemul_montgomery.s`).** This is Official
`poly_basemul` without its R^2 pass: every output is the Montgomery core
`a*b*R^-1`. In key generation, its `finv`/`ginv` operand carries the extra R, so
`h` and the secret-key polynomial equal Official's. It is used only there.

**`poly_basemul_shoup` (`basemul_shoup.s`).** It computes r = a*b in each base
`Z_q[x]/(x^3 - zeta)`, in Official `poly_basemul`'s output scale, without an
R^2 pass:

- b must be canonical ([0, q)); a must lie in the proven envelope; r must not
  overlap a or b.
- The b companion is `b'' = mulhu(16b, 38825)`.
- Every term is `lo16(a*b) - lo16(q*mulhrs(a, b''))`, accumulated lazily with
  one `vpmullw` by q per output.

Proofs:

- symbolic identity with the reference formula;
- exhaustive per-term bounds over the whole caller envelope;
- triangle bounds for every output;
- equality with Official modulo q on the unit basis and on 4000 random
  caller-domain inputs.

| | a envelope | output |
|---|---|---|
| Encap `c = r*h` | [-15580, 15580] | [-10032, 10032]; `poly_add(c, m)` [-25612, 25612] |
| Decap `(c - f')*hinv` | [-16385, 19838] | [-10329, 11400] |

`basemul_shoup.s` is gcc output, committed as assembly, of an intrinsics C
source that is not part of this package: gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0
with `-O3 -mavx2 -mtune=alderlake -fschedule-insns -fsched-pressure
-fno-asynchronous-unwind-tables -fcf-protection=none -fno-stack-protector -S`.
The `.file` and `.ident` lines were then dropped, the entry's `.p2align 4`
raised to `.p2align 5`, the symbols renamed to the package names, the table's
label made `.L`-local, `.globl` spelled `.global`, and the GNU-stack note put
under `.ifndef no_gnu_stack`. No build compiles that C.

The function's frame is `push %rbp; mov %rsp,%rbp; and $-32,%rsp`, and it
spills to fixed `%rsp` offsets `-64(%rsp)`, `-32(%rsp)`:

- `-64(%rsp)` holds a public constant; `-32(%rsp)` holds a secret-derived partial quotient sum;
- all displacements are constant, no memory operand uses an index register,
  and the only conditional branch is the loop back-edge;
- it ends with one `vzeroupper`, then `leave` and `ret`.

## 5. Inverse NTT + crepmod3 (`invntt_crepmod3.s`)

`poly_invntt_crepmod3(r)` equals Official `poly_crepmod3(poly_invntt_scale(r))`
on the Decap domain, where r = `poly_basemul_scale(c, f)` for canonical c and f.
It changes Official's levels 1 and 0; the earlier levels keep Official's
arithmetic (bit-identical, restructured as below):

- **σ fold.** The final `Ns*R^-1` scale (σ mod q = -1693) is folded into the
  level-1 twiddles, and the level-1 `X+Y+Z` Barrett becomes a Montgomery
  multiply by Ns.
- **8-op level 0.** Level 0 is `t = mont(A-B, z0); A+B-t; t+t`.
- **5-op crepmod3 in level 0.** The centered mod-3 map is fused into level 0,
  before the stores. It is exact on [-16388, 16391] (exhaustive).
- **Levels 6..3.** Official's block loop is split before level 4 into two memory passes, (L6, L5) and (L4, L3); the arithmetic is unchanged and the split is bit-identical for every input.

The proof combines two steps:

- **Linear map.** An interval replay on the Decap domain ([-5231, 5730], pre-crep range
  [-6123, 6123]) shows every multiply is a Montgomery- or Barrett-by-constant idiom.
  Both programs are therefore Z_q-linear maps.
- **Unit basis.** Equality on all 864 unit vectors then gives equality mod q.

It is **not** a general-input inverse NTT. `poly_basemul_scale`, which produces
its input, is kept unchanged for that reason.

Official's `poly_crepmod3` is main's `crepmod3.s`, while the proof above was run
against the SUPERCOP leaf's. The two agree on every input in [-5185, 5185], and
both equal the centered mod-3 map on [-q+1, q-1] (exhaustive over all int16
inputs). Official's `poly_invntt_scale` ends in Montgomery products, whose
outputs lie in [-q+1, q-1], so the equality holds for either version.

## 6. Serialization (`pack.s`)

`pack.s` replaces Official's `poly_ntt_pack`/`poly_tobytes_raw` and
`poly_frombytes_raw`/`poly_ntt_unpack` pairs with a direct 12-bit codec. It
packs straight from the 6-way NTT storage order with `vpunpck`, `vpmaddwd(1, 4096)`,
an in-lane interleave and `vpshufb`, and uses no cross-lane permutes. The
canonical freeze is Official's Barrett plus the 2-op `vpaddw q; vpminuw`,
exhaustively proven over every int16. The bytes and the return value equal
Official's. The byte array and the polynomial must not overlap; a guard-page
test shows no access outside either.

`poly_frombytes` returns 1 if a coefficient is >= q and still writes r. The
result is derived with `vpmovmskb` and `setne`, without a branch. Every tobytes
variant is canonical for every int16 input, so no lazy representative reaches
the wire.

## 7. SHAKE256

SHAKE256 is mlkem-native's portable x1 C `mlk_shake256` (commit
`b3ba7b32773e657dd37f6f87bce82528459ad8a4`), vendored as `fips202.c`, `fips202.h`, `keccakf1600.c` and
`keccakf1600.h`, with `mlkem_native_config.h` in place of mlkem-native's own
headers; it replaces Official's XKCP AVX2 Keccak. `hash_f/g/h` are Official's `symmetric.c` with each `shake256`
call renamed `mlk_shake256`, as are key generation's two calls in `kem.c`.
[KECCAK.md](KECCAK.md) covers provenance, configuration, the removed code and
the license.

## 8. Cleanup (zeroization) policy

The package follows Official NTRU+ AVX2's policy, as the AArch64 packages do
(`aarch64/NTRU+768/docs/IMPLEMENTATION.md`, section 10;
`aarch64/NTRU+864/docs/IMPLEMENTATION.md` and
`aarch64/NTRU+1152/docs/IMPLEMENTATION.md`, section Cleanup policy):

- **Clears.** `secure_clear` (explicit_bzero) runs on every path over:
  - kem.c's secret stack buffers and polynomials (22 sites): keygen `h`,
    `coins`, `buf`, `f`, `finv`, `g`, `ginv`; Encap `msg`, `buf`, `r`, `m`,
    `coins` and the invalid-pk `ss`; Decap `msg`, `buf1..3`, `c`, `f`, `hinv`,
    `m` and the failure `ss`;
  - the batch-inversion scratch (`pc`, `R`, `den`);
  - the prefixed inputs of `hash_g`/`hash_h`.
- **mlkem-native state.** `mlk_shake256` zeroizes its Keccak state.
- **Not cleared.** `hash_f` hashes the public key and clears nothing, as in Official.
- **Not wiped.** Assembly spill slots and caller-saved registers are not wiped.
  This matches compiler spills in the C code. The only kernel that spills is
  `poly_basemul_shoup` (section 4: `-64(%rsp)` holds a public constant; `-32(%rsp)` holds a secret-derived partial quotient sum). This policy does not
  require clearing those slots, and the package does not.

`make zeroization-source-check` pins the clear sites and the Shoup frame.
`make zeroization` audits the cleared bytes at run time through a test-only hook,
on key generation, encapsulation and decapsulation and on three failure paths:
encapsulation with a non-canonical pk, decapsulation with a non-canonical ct,
and decapsulation of a tampered canonical ct. Neither is a proof about compiler
copies, caches or swap.

## 9. ABI boundary

- **Names.** The public API is the AArch64 packages' `api.h`, byte for byte:
  `crypto_kem_keypair`, `crypto_kem_enc` and `crypto_kem_dec` keep their NIST
  names, so one binary holds one parameter set. Every other global symbol is
  `ntruplus864_avx2opt_<name>`. The C declarations of the internal symbols carry the
  attributes of the internal header `abi.h`: `NTRUPLUS_INTERNAL` (hidden
  visibility on ELF) and `NTRUPLUS_SYSV` (the SysV convention for the assembly
  kernels, needed only on MinGW, untested). Under SUPERCOP, `crypto_kem.h`
  namespaces the entry points.
- **System V AMD64.** Only rbx, rbp, r12-r15 and rsp are callee-saved; the
  kernels use none of them, and `poly_basemul_shoup` saves rbp.
- **Stack alignment.** Nothing assumes more than the ABI's 16-byte stack
  alignment. gcc realigns the stack for the 32-byte-aligned `poly` locals, and so
  does the Shoup frame. `make abi` calls every function at rsp = 0 and
  rsp = 16 mod 32.
- **Upper YMM state.** Official's assembly kernels, and this package's, return
  with the upper YMM halves in use. That is harmless between AVX kernels, but SSE
  code that runs later in a caller can pay a transition penalty or a false
  dependency. So each public entry point executes one `vzeroupper` just before it
  returns.
  - `make abi` checks XINUSE[2] = 0 after each entry point.
  - The kernels do not change for it.

  Neither SUPERCOP nor mlkem-native requires this: mlkem-native's AVX2 assembly
  has no `vzeroupper` and relies on compiled C around it. Measured on the Core
  Ultra 7 155H against a control whose three `vzeroupper` are 3-byte NOPs, so
  that function addresses are identical (fixed binaries, ASLR on, 48 paired
  blocks), the instruction costs keypair +9.9 [-3.3, +23.6], enc +9.2
  [-5.9, +24.5], dec +10.9 [-4.8, +27.8] cycles, and every 95% interval
  contains 0. `crypto_kem_dec` keeps its size, because gcc's loop-alignment
  padding absorbs the 3 bytes.
- **CET (Control-flow Enforcement Technology).** The package is not CET-marked. Its
  assembly objects carry no `.note.gnu.property` and its kernels have no `endbr64`,
  as in the official implementation. SUPERCOP adds nothing either: its compiler
  lines set no `-fcf-protection`, and almost none of its assembly is marked.
  The linker enables CET for a program only when every object is marked. A
  program that links this package therefore runs without shadow stack and
  indirect-branch tracking, even when its C code, including this package's C
  files, is built with `-fcf-protection` (GCC's default on Ubuntu).
  mlkem-native marks its own assembly, but only its C Keccak is used here.

## 10. Build contract

This is the one full statement of the build flags; the README and the Makefile
refer to it.

- **Toolchain.** Tested with GCC 15.2.0 (Ubuntu) on x86-64 Linux. Clang, other
  gcc versions and the MinGW path of `abi.h` are untested.
- **`-mavx2 -mbmi -mbmi2`.** The assembly needs only AVX2 (no BMI, POPCNT or AES
  instruction). mlkem-native's C Keccak permutation, however, compiles to `andn`
  (BMI1) and `rorx` (BMI2) when they are enabled; without them it compiles to
  `not`+`and` and `rol`/`ror` with extra moves. Every AVX2 CPU of Intel (Haswell
  and later) and AMD (Excavator, Zen) also has BMI1 and BMI2 (all x86-64-v3 CPUs
  have them), and `-march=x86-64-v3` measured the same as `-mbmi -mbmi2`. No
  `-march` is set, so the objects run on any of these CPUs. The Makefile adds
  the flags with `override`, so a command-line `CFLAGS` cannot drop them.
- **How much BMI1/BMI2 matter.** Built with `-O3 -mavx2` alone, this set loses
  40% / 50% / 46% (keypair / enc / dec) of the gain it has over SUPERCOP's own
  `avx2` leaf with `-O3 -mavx2 -mbmi -mbmi2` (medians of 11 fresh processes per
  build, both implementations built with the same flags). The leaf's Keccak is
  XKCP assembly, which these flags do not change.
- **`-O3`.** At `-O2`, GCC 15 leaves mlkem-native's `xor_bytes`/`extract_bytes`
  byte loops scalar, and the KEM keeps only 62-74% of its `-O3` gain over
  SUPERCOP's `avx2` leaf (SUPERCOP Native, one fixed compiler line per build).
  The leaf itself is compiler-insensitive.

**`-mtune=native`.** In one session (81 launches per implementation and build,
builds interleaved round by round), the Makefile build took 2.4% / 3.0% / 2.4%
more cycles than SUPERCOP's default `-march=native` build (keypair / enc /
dec), and adding `-mtune=native` to the Makefile flags recovered 101%
[98%, 104%] / 98% [94%, 102%] / 101% [97%, 104%] of that. gcc resolves
`-mtune=native` to `-mtune=alderlake` on this host and keeps `-march=x86-64`.

- **Instruction set.** Compiled with `-mtune=native`, every file of the package
  uses only x86-64, AVX, AVX2, BMI1 and BMI2 (plus Ubuntu gcc's `endbr64`
  hints, which are NOPs without CET, and the `xgetbv` in the test-only
  `test/abi_sentinel.S`), checked by an objdump mnemonic-to-ISA map and by
  re-assembling with gas restricted to that set.
- **Generated code.** It differs in instruction choice and in some inlining
  decisions: generic tuning clears and copies small buffers with
  `rep stos`/`rep movs` (4 / 3 in the KEM objects: the Keccak state,
  `hash_f`/`hash_g` and `crypto_kem_*` buffers), alderlake tuning with 32-byte
  AVX stores (0 / 0).
- **`-march=native`.** The KEM objects use no further extension on this host
  (only the NIST KAT harness's `kat/rng.c` gains one `movbe`), but on another
  build machine gcc may use others.

## 11. Constant-time review

**SUPERCOP TIMECOP passes** at `-O`, `-O2`, `-O3` and `-Os` (`TIMECOP=256`).

- **Run.** SUPERCOP 20260831's unmodified `do-part` built the leaf that
  `scripts/export_supercop.py` exports with each of SUPERCOP's gcc lines
  (`-march=native -mtune=native -fwrapv -fPIC -fPIE`) and ran `try-timecop`
  under valgrind 3.26.0 memcheck (`--track-origins=yes --error-exitcode=99`).
- **Secrets.** TIMECOP marks every `randombytes` output and the secret key
  undefined, and the public key and ciphertext defined. In 256 loops of key
  generation, encapsulation and decapsulation, no conditional jump and no memory
  address depended on undefined data.
- **Declassified by design.** The only values made public are whether a discarded
  key-generation sample was invertible and whether the secret key decodes
  canonically (`ntruplus_declassify`, SUPERCOP's `crypto_declassify` under
  `-DSUPERCOP`).
- **Negative control.** NTRU+768 with `ntruplus_declassify` made a no-op fails
  TIMECOP at every level (NTRU+768 has the same declassification sites);
  memcheck then reports exactly these two branches: BaseInv's invertibility
  check (`fqinv_batch`, key generation) and the secret-key decode check of
  `crypto_kem_dec`.
- **Control.** Official and SUPERCOP's own `avx2` leaf, run the same way, pass
  too.

In addition, two checks run on the release-flag build, over every
function of the package:

- **Static review.** Every conditional branch, cmov/setcc, variable-latency
  instruction and indexed memory operand is listed.
  - Assembly: every conditional branch is a loop back-edge whose flags come from
    a GPR `cmp`/`add`/`sub` on a pointer or counter. No memory operand uses an
    index register, and there is no division, bit scan or popcount. The only
    setcc is `poly_frombytes`'s return value.
  - C: branches are on loop counters and public lengths (mlkem-native sponge);
    on the public pk/ct canonicality checks; on two values declassified by
    design (`ntruplus_declassify`: whether a discarded key-generation sample was
    invertible, and whether sk decodes canonically); and on the stack protector.
    `verify` uses cryptoint's branch-free `cmov` idiom.
- **Dynamic trace.** Single-step traces of `crypto_kem_keypair`, `crypto_kem_enc`
  (fixed and varying pk) and `crypto_kem_dec` (valid ciphertexts, varying keys,
  and valid mixed with tampered ciphertexts) record every executed instruction's
  rip and memory address. They are byte-identical across trials that differ only
  in secret data, and a secret-indexed negative control differs.

This is evidence for the compiled code on one toolchain, not a proof.

## 12. Code and data not carried over

The linked-call audit shows 0 calls from the three entry points to these, so
they are not in this package:

- Official `ntt.s` (`poly_ntt`), `invntt.s` (`poly_invntt_scale`),
  `crepmod3.s` (`poly_crepmod3`), `basemul.s:poly_basemul`, the Official
  `poly_baseinv` and its statics in `poly.c`, and the unreferenced `consts.c`
  vectors;
- Official `pack.s` (`poly_ntt_pack`, `poly_ntt_unpack`, `poly_tobytes_raw`, `poly_frombytes_raw`) and the `poly.c` wrappers `poly_tobytes`/`poly_frombytes` (replaced by the direct codec in `pack.s`);
- the mlkem-native functions this KEM never calls (SHAKE128, SHA3-256/512 and
  the x4 Keccak functions; docs/KECCAK.md).

**Twiddle tables.** `consts.c` keeps only the entries of Official's `zetas` and
`zetas_inv` that a kernel reads. A symbolic run of every kernel that reads them
records each load: no kernel reads any other entry, the k-th load of the old and
the new layout reads the same values, and every word the kernel writes is
bit-identical for every input.

- **`zetas`**: 336 of Official's 1232 entries (1,792 bytes fewer):
  - [0, 288) = Official `zetas[944..1231]`, read by poly_basemul_montgomery, poly_basemul_scale and poly_baseinv_1: per loop iteration (96 coefficients) 32 entries, 16 x zeta*qinv then 16 x zeta.
  - [288, 336) = Official `zetas[20..67]`, read by poly_ntt level 2: per iteration four broadcast dwords, a*qinv, a, a^2*qinv and a^2, each twice.
- **`zetas_inv`**: 1204 of Official's 1224 entries (40 bytes fewer):
  - [0, 1200) = Official `zetas_inv[0..1199]`, read by poly_invntt_crepmod3 levels 6..2, in Official's layout.
  - [1200, 1204) = Official `zetas_inv[1216..1219]`, read by poly_invntt_crepmod3 level 0: two broadcast dwords, (z-z^5)^-1*qinv twice, then (z-z^5)^-1 twice.

The instructions that index them, rebased:

- `poly_basemul_montgomery`, `poly_basemul_scale`: Official's `add $1888, %rcx` is gone (their twiddles now start the table);
- `poly_baseinv_1`: Official's `add $1888, %r9` is gone (likewise);
- `poly_ntt` level 2: `add $32, %rdx` becomes `add $568, %rdx`, so that `8(%rdx)` is `zetas[288]`, the first level-2 twiddle;
- `poly_invntt_crepmod3` level 0: `1728(%rdx)`/`1732(%rdx)` become `1696(%rdx)`/`1700(%rdx)`, because its constants now follow entry 1199 directly (the 16 entries between them were the level-1 twiddles that the σ fold replaced).

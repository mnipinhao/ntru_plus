# P120 — GT 768 against Official with the hash layer held equal, and TIMECOP

## 1. Hash layer equalised

Three builds per machine, same flags (`-O3 -fomit-frame-pointer`; clang on M2,
gcc on the Pi 5):

- **A**: Official 768 as SUPERCOP ships it, C Keccak (`official/`, copied from
  `supercop-20260831/crypto_kem/ntruplus768/aarch64`);
- **B**: GT P118 as is (asm Keccak, prefixed sponge, fused `hash_g`);
- **C**: GT P118 with Official's `fips202.c` + `symmetric.c`, unchanged, in
  place of its own (`offhash/`).  No GT hash code is left: C contains only
  Official's C `KeccakF1600_StatePermute`.

`check_same.c`: A, B and C print the **same digest** of pk/sk/ct/ss over 200
seeded keypair/enc/dec rounds plus a tampered-ciphertext decaps each.  They are
the same KEM bit for bit.  Permutation counts are identical: 13 / 21 / 12 per
keygen / enc / dec.

`bench_min.c`: deterministic randombytes (the tree's `/dev/urandom` read would
otherwise dominate), min of 400 blocks x 100, three runs.

**A76 (Pi 5, core 3, PMU cycles, `throttled=0x0`), the clean result:**

| cycles | A Official | B GT | C GT + Official hash | B vs A | **C vs A (no hash optimisation)** |
|---|---:|---:|---:|---:|---:|
| keygen | 38,599 | 31,649 | 36,432 | −18.0% | **−5.6%** |
| encaps | 38,749 | 29,654 | 37,271 | −23.5% | **−3.8%** |
| decaps | 33,459 | 27,233 | 31,576 | −18.6% | **−5.6%** |

Share of GT's margin, A76:

| | total | arithmetic (A − C) | hash layer (C − B) |
|---|---:|---:|---:|
| keygen | 6,950 | 2,167 (31%) | 4,783 (69%) |
| encaps | 9,095 | 1,478 (16%) | 7,617 (84%) |
| decaps | 6,226 | 1,883 (30%) | 4,343 (70%) |

**M2 (ns):** A 4,507 / 5,225 / 3,860; B 3,822 / 4,133 / 3,110.  C keygen is
4,519 (+0.3% against A) and C decaps 3,773 (−2.3%).

C encaps is unreliable on M2:

- fixed-pk loop: +4.6% against A;
- encaps-only blocks: +25%;
- interleaved with keygen/decaps: +56%.

A's encaps is stable in all three setups, and so are A76's.  C is B's
arithmetic plus A's hash code, each stable on its own.  So this is an
M2-specific interaction between the two, not code behaviour; it was not traced
further.  The M2 "no hash" figures for C are therefore likely pessimistic for
GT, and the A76 table is the one to quote.

## 2. TIMECOP

SUPERCOP 20260831 runs TIMECOP (valgrind memcheck, secrets marked undefined by
`randombytes_callback`) when `TIMECOP` is set and the leaf declares
`goal-constbranch` + `goal-constindex`.  Setup on the Pi had no sudo, so
everything is user-space (`~/vg` on the Pi):

- the `valgrind` and matching `libc6-dbg` (2.41-12+rpt1+deb13u2, from the
  Raspberry Pi archive pool) `.deb`s, unpacked with `dpkg -x`;
- an unstripped copy of `ld-linux-aarch64.so.1` made with `eu-unstrip`, since
  valgrind requires `strlen` in ld.so and the system loader is stripped;
- `~/vg/bin/valgrind`, a wrapper that passes valgrind's options unchanged and
  runs the program through that loader;
- the TIMECOP `cpucycles` (`CPUCYCLESTIMECOP=1 ./do`) and valgrind headers
  installed into the P119 staging;
- `../gt768-p119-supercop/timecop.sh` drives it; `TIMECOP=1`, all four `-O`
  levels of gcc 14.2.

| leaf | result | findings (distinct sites) |
|---|---|---|
| Official (goal files restored) | **fail** | `poly_fqinv_batch` (`poly.c:122-123`): keygen's invertibility branch, taken before Official's declassify |
| GT P118, no annotations | **fail** | `gt_keygen_baseinv_hier_k8` (asm `cbz` on invertibility); `crypto_kem_dec_internal` (`kem.c:339`, decode-fail branch) |
| GT + `crypto_declassify` | **fail** | `gt_keygen_baseinv_hier_k8` only |
| **GT + declassify + branch-free inversion** | **pass, all four -O levels** | none |

The fix, in the NTRU+768 tree, not yet committed:

- `util.h`: `ntruplus_declassify` macro, Official's (`crypto_declassify` under
  `SUPERCOP`, a no-op otherwise);
- `kem.c`: declassify the decaps decode result before `if (fail)`;
- `keygen.c`: declassify the inversion result before `if (result)`;
- `base.S`: `gt_keygen_baseinv_hier_k8` no longer branches.  The tree always
  completes (a zero total product inverts to zero) and returns `cmp`/`cset` on
  the `uminv` of the total product, kept in x20 (saved and restored).

Checks on the fix:

- Without `SUPERCOP`, `kem.o` and `keygen.o` are machine-code identical to
  before.
- The keygen base inversion returns the same values and outputs as the committed
  tree over 20,000 inputs, including non-invertible ones.
- `make check` passes on M2 and Pi, KAT unchanged.
- SUPERCOP timing in the TIMECOP run: keypair 31,696-31,706, enc
  29,441-29,452, dec 27,296-27,310.  P119 gave 31,646 / 29,443 / 27,315.

`TIMECOP=1` is SUPERCOP's minimum loop count.  Branch and index coverage does
not depend on it, but only one random input set per operation was checked.

### Confirmed with the system valgrind

After `apt install valgrind libc6-dbg` on the Pi (libc6 and libc6-dbg both
2.41-12+rpt1+deb13u4, valgrind 3.24.0; the user-space wrapper was moved
aside), `timecop_system.sh` re-ran TIMECOP on the promotion tree
(`promote/gt768-e4-inverse`, b0009e5d):

| leaf | TIMECOP=1 | TIMECOP=16 | TIMECOP=256 |
|---|---|---|---|
| GT, promotion tree | pass x4 | pass x4 | pass x4 |
| Official (goal files restored) | fail: `poly_fqinv_batch` (poly.c:122-123) | | |
| GT P118, no annotations | fail: `gt_keygen_baseinv_hier_k8`, `kem.c:339` | | |

"x4" means `-O`, `-O2`, `-O3` and `-Os`.  This is the same verdict as the
user-space setup, now without the loader workaround.

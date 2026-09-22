# P112 — what SUPERCOP ships is not what upstream's GitHub builds

Prompted by the question of whether SUPERCOP's Official ought to have the SHA3
path.  It should, in the sense that upstream's repository builds it by default.
It does not, in the sense that the copy inside SUPERCOP has been stripped of it.

## Upstream GitHub: SHA3 is the default

`github.com/ntruplus/ntruplus`, `main`, pushed **2026-08-14** -- two weeks before
the SUPERCOP-20260831 tarball.  `Additional_Implementation/aarch64/NTRU+768/Makefile`:

    HAS_SHAKE256_ASM := 1
    ifeq ($(HAS_SHAKE256_ASM), 1)
        SOURCES += CE/fips202.c CE/f1600.S
        CFLAGS  += -march=armv8.2-a+sha3 -DSUPPORTS_SHAKE256_ASM

`CE/f1600.S` carries 64 `eor3`/`bcax`/`rax1`/`xar`.  NTRU+864 and NTRU+1152 hold
`CE`, `Makefile`, `symmetric.c` and `symmetric.h` as **symlinks** (git mode
120000) to 768's, so one Keccak serves all three -- upstream's own version of
what P110 did by copying the file.

A plain `make` in upstream's tree therefore produces the SHA3 build.

## SUPERCOP: the SHA3 path is absent

`~/supercop-20260831/crypto_kem/ntruplus864/aarch64/`:

* no `f1600.S`, and nothing anywhere matching `eor3`
* `fips202.c` is a **third** file, matching neither `CE/fips202.c` (684 lines
  differ) nor `NO_CE/fips202.c` (331 differ), with a C `KeccakF1600_StatePermute`
* `SUPPORTS_SHAKE256_ASM` appears in `symmetric.c` and `kem.c` and **is never
  defined**; in `symmetric.c` both arms of the `#ifdef` include the same header.
  A dead hook.
* `architectures` contains exactly `aarch64`

The last line is the reason.  SUPERCOP builds an implementation for a named
architecture with no FEAT_SHA3 gate, so `-march=armv8.2-a+sha3` would fail to
assemble on any plain ARMv8 target -- which is precisely what `CE/f1600.S` does
on the Pi 5.  The submission drops the path rather than not build.

## What this corrects

The roadmap called "Official + CE" a **strict baseline constructed** because
"upstream does" have a SHA3 path.  That understates it: **Official + CE is
upstream's default build.**  The SUPERCOP column is the stripped variant, not
the canonical one.  So on M2 the Official + CE table is the honest headline and
the SUPERCOP table flatters us by a backend upstream ships and SUPERCOP declined
to carry.

## An asymmetry this turned up on the A76 side

On the Pi 5 neither side can use FEAT_SHA3, and the roadmap records the A76
table as fair on that ground.  It is fair about *SHA3*.  It is not symmetric
about *assembly*:

| | A76 Keccak |
|---|---|
| GT | `keccakf1600.S`, 230 hand-written instructions, selected by `#if !defined(__ARM_FEATURE_SHA3)` |
| Official | `fips202.c`, 621 lines of portable C -- identical in SUPERCOP and in upstream's `NO_CE` |

Upstream wrote no non-SHA3 assembly Keccak, so on a machine without FEAT_SHA3
its only option is C.  GT's selection is compile-time, not runtime:
`fips202.c:361`, `#if defined(__ARM_FEATURE_SHA3)`.

This is a legitimate implementation-against-implementation result -- we wrote a
backend they did not.  It is not a Good-Thomas result, and the A76 margins of
-14% to -24% contain an unmeasured amount of it.  The same question the M2
baselines have been asked, unasked on the A76 side until now.

**Not yet quantified.**  The measurement is one build: Official on the Pi 5 with
GT's `keccakf1600.S` substituted for its `KeccakF1600_StatePermute`.

# Plantard Usage Audit in `ntruplus-KpqC-Final`

Date: 2026-03-02

## Scope
Checked these directories:
- `Optimized_Implementation`
- `Additional_Implementation`

## Main Conclusion
1. Your correction is valid for the AArch64 `ntt.s` sequence:
   - `mul` + `sqrdmulh` + `mls` is best classified as a Barrett-style reciprocal modular multiply primitive in NEON lanes.
   - It is not an explicit Plantard API call.
2. In this repository, explicit Plantard routines are in `Optimized_Implementation/*/ntt.c` (C code).
3. `Additional_Implementation` (AArch64 + AVX2) uses assembly/intrinsics modular arithmetic patterns (`fqmul_*`, mulhi/mullo/sub, reciprocal reduction), and does not define `plantard_*` functions.

## Evidence

### 1. Repository architecture split
`ntruplus-ntt-Optimized/README.md` states:
- `Optimized_Implementation`: high-performance C (`README.md:10-12`)
- `Additional_Implementation`: hand-tuned assembly for AVX2 and ARMv8-A NEON (`README.md:14-18`)

So in this tree, `Optimized_Implementation` is not an assembly folder.

### 2. AArch64 Additional: Barrett-style NEON pattern
In `ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/ntt.s`:
- Twiddle multiply kernel:
  - `mul ...` (`ntt.s:25`)
  - `sqrdmulh ...` (`ntt.s:32`)
  - `mls ... v0.h[0]` (`ntt.s:39`)
- Reduction kernel:
  - `sqdmulh ... v0.h[1]` (`ntt.s:253`)
  - `srshr ... #11` (`ntt.s:258`)
  - `mls ... v0.h[0]` (`ntt.s:263`)
- Constant table repeatedly starts with `0x0d81, 0x4bd4` (`ntt.s:1011`, then repeated blocks), matching modulus/reciprocal-style packed constants.

The same `sqdmulh + srshr + mls` reduction structure is also present in:
- `.../aarch64/NTRU+864/asm/ntt.s` (example: `409-415`)
- `.../aarch64/NTRU+1152/asm/ntt.s` (example: `411-419`)

### 3. Additional C/intrinsics layer does not expose Plantard API
AArch64:
- `.../aarch64/NTRU+768/poly.c` defines `fqmul_neon` (`poly.c:8`) and uses it in base inversion flow (`poly_baseinv`: `poly.c:113-129`).

AVX2:
- `.../avx2/NTRU+768/poly.c` defines `fqmul_avx2` (`poly.c:7`) with `mullo/mulhi/sub` structure (`poly.c:11-14`).
- Base inversion entry point: `poly_baseinv` (`poly.c:170-185`).
- Constants include `QINV`, `_16xqinv`, `_16xq`, `_16xRinv`, `_16xRinvqinv` (`consts.c:5`, `:35`, `:32`, `:40`, `:41`).

AVX2 asm also uses the same reduction style:
- `.../avx2/NTRU+768/asm/baseinv.s`: loads `_16xqinv` and `_16xq` (`baseinv.s:3-4`), then repeated `vpmullw/vpmulhw/vpsubw` blocks.

### 4. Explicit Plantard usage is in Optimized C files
- `.../Optimized_Implementation/NTRU+768/ntt.c`:
  - `plantard_reduce` (`ntt.c:56`)
  - `plantard_reduce_acc` (`ntt.c:77`)
  - `plantard_mul` (`ntt.c:99`)
- Same structure exists in:
  - `.../NTRU+864/ntt.c` (`plantard_*` starts around `67`, `88`, `110`)
  - `.../NTRU+1152/ntt.c` (`plantard_*` starts around `67`, `88`, `110`)

Call density (from grep count):
- `NTRU+768/ntt.c`: `plantard_mul` 66 calls
- `NTRU+864/ntt.c`: `plantard_mul` 70 calls
- `NTRU+1152/ntt.c`: `plantard_mul` 72 calls

## Base Inversion Context (TCHES statement)
The statement about smaller speed-up in base inversion is consistent with this code structure:
- base inversion includes many variable-variable multiplications and dependency-heavy chains.
- constant-only multiplication shortcuts are less dominant in this stage than in twiddle-heavy NTT layers.

In this repo specifically:
- Optimized C base inversion still calls `plantard_*` helpers (`Optimized_Implementation/NTRU+768/ntt.c:553+`),
- while Additional assembly/intrinsics base inversion uses the same reciprocal reduction machinery used elsewhere (`fqmul_*` / mulhi-mullo-sub patterns).

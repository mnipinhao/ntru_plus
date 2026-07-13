# Explanation of `ntt.s` (AArch64, NTRU+768)

Correction note (2026-03-02): in this file, the NEON sequence
`mul + sqrdmulh + mls` is better described as a Barrett-style
reciprocal modular multiply primitive, not an explicit Plantard API call.

Target file: `ntruplus-KpqC-Final/Additional_Implementation/aarch64/NTRU+768/asm/ntt.s`

## 1. What this assembly file implements

This file contains two exported routines:

- `poly_ntt` / `_poly_ntt` (forward NTT)
- `poly_invntt` / `_poly_invntt` (inverse NTT)

For `NTRU+768`, we have:

- `NTRUPLUS_N = 768`
- `NTRUPLUS_Q = 3457`
- 16-bit coefficients (`int16_t`)
- total polynomial size = `768 * 2 = 1536` bytes

The code is fully vectorized with AArch64 NEON:

- each `q` register (`v?.8h`) holds 8 coefficients
- most arithmetic is done in 16-bit lanes with lazy reduction

Calling convention in this file:

- `x0` (`dst`) = output polynomial pointer
- `x1` (`src`) = input polynomial pointer
- `x2` (`zetas_ptr`) = pointer to twiddle/constant table
- `x8` (`counter`) = loop counter

## 2. Constant tables: `zetas` and `zetas_inv`

At the end of the file:

- `zetas:` (used by forward NTT)
- `zetas_inv:` (used by inverse NTT)

They are loaded in 64-byte chunks:

```asm
ld1 {v0.8h - v3.8h}, [zetas_ptr], #64
```

Each chunk packs:

- modulus/reduction constants (`q` and reciprocal-like constants)
- per-stage twiddle constants already arranged for NEON multiply + reduction patterns

That packing removes scalar address arithmetic in hot loops.

## 3. Core arithmetic idioms used everywhere

## 3.1 Twiddle multiplication (Barrett-style NEON pattern)

Typical sequence:

```asm
mul      vT.8h,   vA.8h,  vZ.h[idx0]
sqrdmulh vTmp.8h, vA.8h,  vZ.h[idx1]
mls      vT.8h,   vTmp.8h, vQ.h[0]
```

Interpretation:

- `mul` computes the low-lane product term
- `sqrdmulh` computes a high/rounded reciprocal product term
- `mls` subtracts the estimated `k*q` term (`q` is in `v0.h[0]`)

This is a reciprocal-based Barrett-style modular multiplication pattern
in NEON lanes.

## 3.2 Fast lane-wise reduction

Typical sequence:

```asm
sqdmulh vTmp.8h, vX.8h, v0.h[1]
srshr   vTmp.8h, vTmp.8h, #11
mls     vX.8h,   vTmp.8h, v0.h[0]
```

Interpretation:

- estimate quotient using fixed-point reciprocal
- round-shift
- subtract estimated `quotient * q`

This is a fast bounded reduction to keep values in range between butterfly stages.

## 4. `poly_ntt` structure (forward transform)

## 4.1 Setup

At the top:

- `adr zetas_ptr, zetas`
- preload first zeta block
- `counter = 128`

## 4.2 Loop `_looptop_012` (lines ~16-231): levels 0, 1, 2

This loop processes strided data with offsets like `#k*128`.

- reads 12 vectors (`q4..q15`) from 12 coefficient groups
- performs stage-0 to stage-2 butterflies
- stores back to `dst` with same strided pattern
- increments `src`/`dst` by `#16` bytes per iteration
- `counter` goes `128 -> 0` by `#16` (8 iterations)

So this loop covers the whole 1536-byte polynomial in a strided layout.

Notable details:

- level 1 contains 3-point butterfly-style math (`t1/t2/t3`) matching the C formulation that uses `omega`
- several `mul + sqrdmulh + mls` groups realize twiddle multiplies

## 4.3 Loop `_looptop_3456` (lines ~238-459): levels 3, 4, 5, 6

Before entering:

- `src` and `dst` are adjusted back by `#128`
- `counter = 1536`

Per iteration:

- load a new zeta chunk (`v0..v3`)
- load 8 vectors from contiguous `dst`
- do level 3/4/5/6 butterflies
- do `trn1/trn2` shuffles (64-bit, then 32-bit, then 16-bit) to transpose/reorder lanes between stages
- reduce
- store 8 vectors (`st1 {v4-v7}`, `st1 {v8-v11}`), post-incrementing `dst` by 128 bytes

`counter -= 128` gives 12 iterations (12 * 128 = 1536 bytes).

## 5. `poly_invntt` structure (inverse transform)

## 5.1 Setup

- `adr zetas_ptr, zetas_inv`
- `counter = 1536`

## 5.2 Loop `_looptop_6543` (lines ~482-651): inverse levels 6, 5, 4, 3

Per 128-byte block:

- load 8 vectors from `src`
- perform inverse butterflies (difference terms first, then multiply by inverse twiddles)
- same `trn1/trn2` lane-reordering structure as forward path
- reduce/store to `dst`

Again: 12 iterations.

## 5.3 Loop `_looptop_210` (lines ~659-999): inverse levels 2, 1, 0

After first inverse loop:

- `sub dst, dst, #1536` rewinds output pointer to start
- load next zeta chunk
- `counter = 128`

Then strided processing similar to forward early stages:

- loads/stores with offsets `#k*128`
- level-2, level-1, level-0 inverse butterfly algebra
- includes extra multiply constants from `v3.h[...]` in level-0 section (the part corresponding to final normalization/scaling in the C inverse flow)

8 iterations (`128 / 16`).

## 6. Practical way to read this file

If you want to map assembly to reference logic quickly:

1. Split by labels: `_looptop_012`, `_looptop_3456`, `_looptop_6543`, `_looptop_210`.
2. Inside each loop, follow comment markers: `#level`, `#mul`, `#update`, `#reduce`, `#store`.
3. Treat each `v?.8h` register as 8 independent coefficients.
4. Recognize `mul + sqrdmulh + mls` as a Barrett-style modular multiplication primitive.
5. Recognize `sqdmulh + srshr + mls` as the reduction primitive.

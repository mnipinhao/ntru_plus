# M5U-CF4 — complete FR-ISO2 polynomial-multiplication closure

## Question

Can the current experimental pieces execute one real

`2 × Forward -> FR-ISO2 BaseMul -> Inverse`

polynomial multiplication without an 864-coefficient FR-ISO2/FR-0 conversion
pass, and is that exact composition still a plausible Cortex-A76 winner?

This directory is an Experiment-only integration gate.  It does not change the
Production implementation or the SUPERCOP package.

## Linked operation DAG

1. `gt864_forward_poly_ntt_friso2` is called independently for operands `a`
   and `b`.  It is CF0's correctness-proved direct FR-ISO2 Forward and writes
   the existing 864-halfword FR tile once.
2. `gt864_friso2_basemul_direct` multiplies each three-component leaf modulo
   `Y^3-9` for top branch 0 or `Y^3-3` for top branch 1.  Its output is R0.
3. `gt864_friso2_inverse_ntt9_neon` reads that FR-ISO2 buffer directly and
   writes the existing 896-halfword P8-plus-tail boundary.
4. `gt864_fr0_inverse_finish_neon` consumes P8-plus-tail and writes 864 natural
   coefficients.

There is no call to `gt864_friso2_denormalize` in the candidate path.  That
function is linked only as a test oracle for direct-Inverse differential cases.

## Exact direct-Inverse factor flow

For component `j` at `(top,row,column)`, FR-ISO2 stores

`Fiso[j] = tau(top,row,column)^j * Ffr0[j]`,

where

`tau = delta(top,column) * gamma^row`, `gamma = theta^32`,

`delta(0,c)=theta^(2c)`, and `delta(1,c)=27*theta^(2c)`.

The inverse consumer therefore performs:

1. Load nine row vectors for eight adjacent columns.  Register-like object
   `rows.v[r]` contains the same component and top branch for row `r`; its eight
   lanes are columns `8*block ... 8*block+7`.
2. For components 1 and 2 and rows 1 through 8, apply one Algorithm-10
   `mul/sqrdmulh/mls` fixed multiplication by `gamma^(-j*r)`.  This removes the row-dependent
   factor.  Component 0 and row 0 are unchanged.
3. Run the frozen oriented inverse NTT9.  Because `delta(top,column)^j` is
   common to all nine rows of a lane, it commutes through this linear transform.
4. Use a component-specific inverse-twist table containing the old
   `inv9*lambda^(-s)` multiplied by `delta(top,column)^(-j)`.  This cancels the
   remaining column factor with no separate multiplication and no extra twist
   load.
5. Transpose rows 0 through 7 into P8 column vectors and scatter row 8 into the
   existing packed tail.  The second inverse pass is unchanged.

The fused correction adds exactly 64 fixed multiplications: two top branches,
two column blocks, two scaled components, and eight nonzero rows.  It adds no
coefficient boundary.  The current intrinsics implementation is deliberately a
correctness/reference realization: local compiler output has a 0x220-byte
frame and is not a performance or no-spill claim.

## Reproduction

Run `make check` on AArch64.  It generates both table families, proves factor
identity/Montgomery scale and the complete interval schedule, then runs direct
Inverse differential cases and full quotient-ring products against schoolbook.

The cost ledger intentionally stops the gate before a new Pi 5 run: previously
measured CF0 Forward penalties already exceed the measured BaseMul saving by
463.162 cycles before the new Inverse work is added.

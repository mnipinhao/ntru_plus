# 141 — RAW-H / NORMALIZED-R ASYMMETRIC B3 FACTORIZATION

This is a generator/static-proof gate.  It does not modify production code and
does not use instruction count as a cycle verdict.  Its purpose is to establish
whether a new executable candidate actually deletes an operation class before
writing assembly.

## What “raw h” means in the current implementation

`ntruplus768_unpack_m_avx2` extracts unsigned 12-bit coefficients, accumulates
the maximum for the public-key canonicality check, transposes each four-vector
group into private M/SoA, and stores it.  It performs **no modular reduction and
no centering**.  Valid stored values are already the raw canonical residues
`0..3456`.

The current general B3 consumes this raw `h_M` directly together with transformed
`r_M`.  Therefore “absorb raw-to-normalized h conversion” is not a new saving:
there is no such conversion on the current path.

## Cuts tested

The 4x16 physical transpose has three four-instruction routing layers.  There
are twelve groups in NTRU+768.  The generator checks four legal cuts:

- `RAW_PACKET`: decoder stops before the transpose; B3 pays all three layers.
- `P1_WORD`: decoder pays one layer; B3 pays two.
- `P2_DWORD`: decoder pays two layers; B3 pays one.
- `M_SOA`: current path; decoder pays all three and B3 pays none.

For every cut, the complete decode-to-B3 path is 12 groups × 12 routes = 144
dynamic routing instructions.  This is a conservation result for the existing
transpose+B3 factorization, not a claim that every imaginable B3 tensor must pay
144 routes.

## Answers to the five gate questions

1. **How far can raw decoded h be retained?** Through any of the four cuts,
   including all the way to B3 entry.  The current implementation already keeps
   the raw residue values through the full M presentation.
2. **Can canonicality accumulation still complete?** Yes.  It is computed on
   extracted 12-bit values before the transpose.  Permuting those values cannot
   change the maximum or the predicate `value >= q`.
3. **Can B3 constants absorb raw→normalized conversion?** Congruence-wise yes,
   but vacuously: current B3 already accepts raw residues and no conversion is
   executed.  Constants cannot absorb the remaining cross-lane permutation;
   lane-wise diagonal multiplication is not a permutation network.
4. **Is a reduction or 48-route layer actually deleted?** No.  No reduction is
   present to delete, and every cut totals 144 routes over the twelve groups.
5. **Peak register / spill result?** All cut placements can stay within the 16
   architectural YMM registers and need no spill, but this does not create a
   performance candidate because the dynamic operation class is unchanged.

## Decision

`STATIC_NO_OPERATION_CLASS_DELETION` for this factorization.  Do not write an
ASM candidate that merely moves transpose layers from unpack to B3.

This does **not** close asymmetric B3 tensors in general.  Reopen only with a
factorization that consumes a pre-transpose packet presentation without
recreating the missing routing layer, or that deletes a separate Montgomery /
reduction class.

Run:

```sh
python3 generate.py
```

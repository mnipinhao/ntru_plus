# GT basemul_add32 prototype status

This note records the isolated prototype contract only.  No production wiring
is changed.

The safe add32 direction is the R^-1 accumulator/finalizer path, not a fully
raw quartic dot product.  The existing GT quartic basemul inner reductions
produce `raw_rminus1_i = product_i * R^-1 mod q` in 16-bit bounded normal
residue form.  The current symbolic finalizer accepts either one such residue
or a bounded signed-16 sum of such residues.  It then accumulates the final add
in 32-bit lanes as:

```text
prefinal_i = c_i * R + raw_rminus1_i * R^2
out_i      = Mont(prefinal_i)
```

For NTRU+768, `q = 3457`, `R = -147`, and `R^2 = 867`.  With centered `c` and
one product, `abs(prefinal) <= 1728*147 + 3456*867 = 3250368`; with two raw
products accumulated before finalization in signed 16-bit lanes,
`abs(prefinal) <= 6246720`.  Both are well below signed 32-bit range and below
the Montgomery reducer precondition `q * 2^15 = 113278976`.

The Montgomery factor cancels exactly:

```text
Mont(c*R + raw_rminus1*R^2)
  = (c*R + (product*R^-1)*R^2) * R^-1
  = c + product  (mod q)
```

So the output is normal `R^0` public polynomial representation, matching
`poly_basemul_add` and suitable for `poly_tobytes` after its usual bounded
negative normalization.

Prototype artifacts:

- `asm/slothy/microkernels/base_gt_add32_rminus1_finalize.sym.S`
- `asm/slothy/microkernels/base_gt_add32_rminus1_finalize.contract.yml`
- `asm/slothy/microkernels/base_gt_add32_rminus1_finalize_optimize.py`

Before benchmarking, run Slothy externally, inspect and assemble the generated
output, add an isolated harness/wrapper, and differential-test against the
existing add32 reference and stock `poly_basemul_add`.

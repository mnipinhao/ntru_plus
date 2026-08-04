# GT layout, component, and scale invariants

`tools/generate_gt_rewrite.py` is the single source of truth.  It reconstructs
the 192 Official quartic leaves rather than copying their table, then asserts
that every generated exponent is exactly equal to Official Figure 22's
`index[192]`.

The input CRT coordinate is
`n = 64*n3 + 33*n32 (mod 96)` and the output frequency coordinate is
`k = 32*k3 + 3*k32 (mod 96)`.  Branch 0 uses `F=2`, `F^96=phi^-1`, and
`F^-n`; branch 1 uses `F=22`, `F^96=phi`, and `F^-n`.  The generated forward
and inverse maps are asserted bijective and mutually inverse, and every
generated `F^-n` is asserted multiplicatively inverse to its `F^n`
postweight.

The private ABI is fixed as:

```text
batch = ((branch*3+k3)*2+block32)
Q     = 16*block32+lane
word  = 64*batch+16*degree+lane
```

All GT public-entry kernels use normal centered scale.  Consequently
`gt_poly_basemul_scale` equals normal GT basemul: normalization is already
part of the paired GT inverse.  Serialization alone applies the generated
GT-to-Official component map and `[centered] -> [0,q)` conversion.  GT layout
never crosses a wire or non-GT caller boundary.

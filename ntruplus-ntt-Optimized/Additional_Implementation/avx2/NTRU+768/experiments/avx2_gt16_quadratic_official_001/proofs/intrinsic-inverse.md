# Benchmark-only paired vertical inverse

The executable I0 path consumes the quadratic terminal result directly and
implements the complete inverse boundary:

```text
quadratic-native
  -> scale-2 quadratic-to-quartic merge
  -> lazy Cooley-Tukey inverse vertical NTT16
  -> inverse DFT3 and combined (1/48)*F^n postweight
  -> standard R2 branch merge
  -> special R2 top merge and scale removal
  -> coefficient-order stores
```

The QBM reducer returns `R^-1` output and the merge deliberately retains a
factor two.  I0 therefore enters the inverse with uniform scale `2*R^-1`.
Both standard-R2 `1/2` operations are deferred, making the two top residues
carry `4*R^-1`; the final special-R2 constants include `R/4` and remove the
scale.  The inverse DFT3 `1/3` is folded into the per-lane `F^n` postweight.

I1 fuses quadratic merge arithmetic into the first inverse load.  Across eight
alternating process samples it is slower than I0 by 3.252% at stage 1, 2.027%
through inverse NTT16, and 0.782% through the complete inverse.  I0 is selected:
sequential merge constants and
scratch traversal are cheaper than I1's bit-reversed direct constant access,
and I0 is 306 linked bytes plus the shared 133-byte merge while I1 is 490
bytes.

The first conservative implementation centered twice after every NTT16
butterfly.  After stage 1 all inputs are centered, so subsequent add/sub nodes
use a generated, position-specific CT trace.  Length 4 needs no correction and
is bounded by `[-3458,3458]`; length 8 performs the sole intermediate
correction and is bounded by `[-3455,3455]`; length 16 needs no correction and
is bounded by `[-6910,6910]`.  Identity CT twiddles remain lazy instead of
performing redundant Montgomery multiplication.  The following DFT3 reaches
at most `[-20730,20730]`, still inside signed int16.

The standalone inverse-NTT16 diagnostic retains `/16`.  The complete inverse
instead folds `/16`, inverse-DFT3 `/3`, and `F^n` into one `(1/48)*F^n`
postweight.  Postweight is bounded by `[-2108,2108]`, the largest special-R2
difference is 8397, and final raw outputs are within `[-3570,3570]`; one final
correction is sufficient.  These changes lower complete I0 from 1887.748 to
1126.226 TSC ticks.  Directly fusing DFT3 output into R2 raises register
pressure and regresses to 1239.515, so the 48-vector boundary is retained.

One thousand random full-range cases and six boundary patterns compare the
inverse NTT16 against a scalar DFT16 and the complete inverse against an
independent scalar DFT3/postweight/R2 implementation.  Exact centered output,
`out==in`, ASan, and UBSan pass.

The direct cycle gate still fails, but by much less.  In the same binary the
frozen GT32 fused inverse has median 911.862 TSC ticks; quadratic GT16 I0 is
23.508% slower.  Its 214.364-tick inverse deficit exceeds the measured 48.840
tick terminal gain, leaving a known terminal-plus-inverse regression of
165.524 ticks before either forward is counted.  This result does not close
`2F+B+I`, because no executable Round 4C forward exists.  Assembly remains
unauthorized, but the forward break-even is now 82.762 ticks per forward rather
than the earlier 246.800.

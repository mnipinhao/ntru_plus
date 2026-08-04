# Benchmark-only paired vertical inverse

The executable I0 path consumes the quadratic terminal result directly and
implements the complete inverse boundary:

```text
quadratic-native
  -> scale-2 quadratic-to-quartic merge
  -> inverse vertical NTT16 / 16
  -> inverse DFT3 / 3 and F^n postweight
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
alternating process samples it is slower than I0 by 1.668% at stage 1 and
1.125% through inverse NTT16.  I0 is selected: sequential merge constants and
scratch traversal are cheaper than I1's bit-reversed direct constant access,
and I0 is 306 linked bytes plus the shared 133-byte merge while I1 is 490
bytes.

The first conservative implementation centered twice after every NTT16
butterfly.  After stage 1 all inputs are centered, so subsequent add/sub nodes
are bounded by `[-3456,3456]`; one signed correction is sufficient.  Retaining
two corrections only at the wider merge/first-stage boundary lowers complete
I0 from 1887.748 to 1456.139 TSC ticks without changing any representative.

One thousand random full-range cases and six boundary patterns compare the
inverse NTT16 against a scalar DFT16 and the complete inverse against an
independent scalar DFT3/postweight/R2 implementation.  Exact centered output,
`out==in`, ASan, and UBSan pass.

The direct cycle gate fails.  In the same binary the frozen GT32 fused inverse
has median 913.699 TSC ticks; quadratic GT16 I0 is 59.368% slower.  Its 542.440
tick inverse deficit exceeds the measured 48.840 tick terminal gain, leaving a
known terminal-plus-inverse regression of 493.600 ticks before either forward
is counted.  This result does not close `2F+B+I`, because no executable Round
4C forward exists, but it forbids assembly authorization and makes a forward
prototype justify at least this deficit before the chain gate can reopen.

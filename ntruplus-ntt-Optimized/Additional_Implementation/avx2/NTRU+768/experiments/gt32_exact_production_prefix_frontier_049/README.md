# GT32-EXACT-PRODUCTION-PREFIX-FRONTIER-049

This gate measures cumulative Official-versus-GT Encap cost from the real
production entry to five coarse semantic checkpoints:

- A: Decode, hashes, and CBD(r) complete.
- B: Forward/pack of r-hat and `hash_g` complete.
- C: SOTP(m) and Forward(m) complete.
- D: general BaseMul and add(m) complete.
- E: complete production Encap.

The inputs are the frozen exact-production ELF files from experiment 043, the
image on which the full-Encap reversal motivating this gate was observed.
Variants A-D are made only by replacing complete instructions immediately
after a checkpoint with an equal-size jump to that implementation's existing
normal cleanup path. E is the original ELF byte for byte. There is no compile,
link, symbol movement, stack-frame change, or call-target change before a
checkpoint.

This is a cumulative frontier. Differences between adjacent checkpoints are
not reported as isolated component costs: they also include history,
interaction, and delivery effects accumulated by the exact production caller.

## Decision rule

- A localized large change in the cumulative GT-minus-Official curve justifies
  inspection of that coarse region.
- A distributed or unstable curve closes additive component attribution; it
  does not justify subtracting isolated-kernel timings.

See `RESULTS.md` after the balanced SUPERcop-style run.

`build-045-control/` and the correspondingly named result files record an
initial non-target-image control. They are not used for the 049 decision: that
045 image had a different full-Encap delivery outcome and therefore could not
answer the reversal question.

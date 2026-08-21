# GT32-LOAD-TO-COMPUTE-COMPOSITE-042

Same-ELF 2x2 factorial full-Encap gate:

- A: production Decode and production B3.
- D: resident Decode mask0123 and production B3.
- B: production Decode and qinv-preload B3.
- DB: both load-to-compute changes.

Candidate target symbols are padded to exactly the control symbol sizes.
All four profiles execute one fixed-address common Encap caller and differ only
in two function pointers. This adds equal indirect-call overhead to every
profile, but removes the four-caller address confound. Normal and reversed
binaries invert only the Decode/B3 target order. Serializers, Forward kernels,
hashes, and protocol glue are shared.

`make benchmark` runs the final 48-launch gate and writes the raw launch data,
summary, MAD, and deterministic bootstrap intervals to
`generated/benchmark.json`.
GT Clean production is not modified.

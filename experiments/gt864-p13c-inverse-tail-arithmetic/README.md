# P13-C — tail Inverse16 composite terminal map

This promoted experiment isolates the one-call, six-useful-lane tail kernel after the
P13-B main-kernel promotion.  The lane ABI is not the main-kernel ABI: lanes
0–2 hold the three degree-3 components for top0, lanes 3–5 hold them for top1,
and lanes 6–7 are zero padding.  The candidate must preserve all 96 natural
stores, the P8 raw consumer bound, the public wrapper, and the scratch boundary.

The fixed hypothesis and gate state are in `iteration.yml`; the complete result
is in `RESULTS.md`.  Exact proof, Slothy, native correctness, and paired Pi 5
timing all pass, and the tested payload is now production.

# P33 — two-bank inverse16 terminal sharing

P33 is an isolated replacement experiment for the six production `lazy_i16`
calls.  For each component, half zero is transformed to its sixteen
preterminal vectors and materialized in its already-consumed 256-byte scratch
block.  Half one is transformed and remains live in registers.  A reusable
pair helper then loads four composite terminal constants once per column and
uses them for both halves.

The external FR0/natural-order contract, tail transform, raw-to-ternary pass,
1792-byte scratch size and wipe policy are unchanged.  Production is not
modified unless no-spill Slothy allocation, exact correctness, ABI checks and
paired Pi 5 full-path measurements all pass the promotion gate.

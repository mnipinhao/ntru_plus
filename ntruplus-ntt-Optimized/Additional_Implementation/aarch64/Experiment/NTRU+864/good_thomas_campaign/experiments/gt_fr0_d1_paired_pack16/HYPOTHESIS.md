# D1-P3B9 paired-pack16 hypothesis

Observation: P3B6 packs each completed eight-coefficient output independently,
paying one `TBL` and two stores for twelve bytes.  Two adjacent outputs contain
eight coefficient pairs and can form three eight-byte streams directly.

Primary bottleneck category: packing permutation and stores.

Hypothesis: pair packing with even/odd deinterleave, narrow/shift/insert, and a
single `ST3` can beat two independent pack8 operations on Cortex-A76 despite
its structured-store cost.

Exact proposed change: first benchmark a complete 864-coefficient ordered
serialization boundary using either 108 independent pack8 operations or 54
paired pack16 operations.  Both include the same full signed-int16
normalization.  Separately machine-model how P3B6 obtains adjacent output
pairs; do not modify the complete FR0 route in this gate.

Expected static effect: per pair, replace two six-operation `TBL` pack networks
and four stores with a twelve-instruction `ST3` network.  Expected cycle effect:
positive only if removing `TBL` and stores exceeds the cost of `ST3`.

Expected register-pressure effect: the isolated primitive is small.  Complete
integration cannot hold adjacent outputs until both complete: the exact current
schedule must spill the first member of every pair to public fixed-address
scratch, or a new route schedule is required.

Correctness/range impact: none.  Both candidates canonicalize every signed
int16 coefficient and emit the same four three-byte coefficient pairs.

Falsifying measurement: any byte mismatch, out-of-bounds write, unexpected
spill in the isolated core, paired packing no faster than pack8, or integration
scratch cost larger than the primitive saving.

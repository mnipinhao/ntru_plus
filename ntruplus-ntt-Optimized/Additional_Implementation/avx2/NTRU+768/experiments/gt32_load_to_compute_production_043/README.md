# GT32-LOAD-TO-COMPUTE-PRODUCTION-043

Exact-image production adjudication of the two locally qualified 041 changes:

- resident Decode `0123` mask;
- B3 `qinv` preload.

The candidate is copied from the frozen GT Clean SUPERcop export and replaces
only `pack.s` and `basemul.s` with the generated, equal-symbol-size 041 bodies.
There is no padding sweep or layout selection.  The implementation uses the
ordinary deterministic SUPERcop compiler/link order.

This experiment deliberately separates two claims:

1. 042 already showed that the mechanism is not placement-robust.
2. 043 asks whether the predefined exact production image is nevertheless a
   reproducible implementation-level winner, which is the question SUPERcop
   normally answers.

The formal gate rebuilds Official, GT Clean A, and GT Clean DB using the same
captured SUPERcop compiler profile, verifies the candidate KAT, records binary
hashes/section sizes/symbol addresses, and runs a balanced three-way campaign.

## Final decision

The predefined production image is **not promoted as the new Encap baseline**.
The serious 256-block campaign found:

- Keypair DB versus Clean: neutral, paired CI `[-16.30, +7.73]` cycles.
- Encap DB versus Clean: inconclusive, paired median `-12.95` cycles but CI
  `[-29.10, +4.17]` crosses zero.
- Decap DB versus Clean: a real exact-image win, paired median `-43.36` cycles
  and CI `[-50.15, -31.68]`.

The candidate therefore demonstrates a Decap delivery win in this exact image,
but it fails the predeclared Encap promotion requirement.  The 042 Normal result
must not be carried over: the clean export places both modified bodies at the
original production slots, while 042 Normal placed candidate copies in later
duplicate slots.

Against Official in the same serious campaign, DB wins Keypair and Decap but
still loses Encap.  See `RESULTS.md` for the complete figures and methodology.

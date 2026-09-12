# P19 — promote P18 ToBytes to GT864 production

P19 links the exact P18 full and small assembly artifacts into the production
NTRU+864 package.  The supported public KEM-facing entries remain
`gt864_fr0_tobytes_full` and `gt864_fr0_tobytes_small`; their C adapter now
calls complete P18 assembly functions instead of the P9/P16 inner-plus-wrapper
pair.

The committed pre-promotion production tree is the benchmark baseline.  The
candidate is copied from the working production directory, including its
manifest.  Validation covers exact bytes, input immutability and output
canaries, AAPCS `d8-d15`, SIMD cleanup, package KEM/KAT, malformed ciphertext,
linked objects, and paired boundary/full-KEM PMU on Pi 5.

Input/output overlap is not a production ToBytes contract, so P19 does not
invent an in-place alias guarantee.  The relevant memory gate is disjoint
buffers with exact output extent and immutable input.

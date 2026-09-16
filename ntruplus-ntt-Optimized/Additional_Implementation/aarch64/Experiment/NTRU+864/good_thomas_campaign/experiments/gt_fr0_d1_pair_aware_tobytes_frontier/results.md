# D1-P3B13 evidence

Status: **the direct pair-wait integration is rejected before assembly.**

The replay uses the exact P3B6 composed map.  Under the P3B6 input order,
keeping adjacent output q-vectors until both are complete has a peak frontier
of 34 vectors and active-area 1284.  A stronger pair-aware heuristic witness
reduces these to 28 and 1036.

The 28-vector result is useful but insufficient for the declared gate.  Only
four architectural vector registers remain, while the live source plus exact
normalization and `pack16` path need a conservative minimum of four work
registers at the completion boundary.  This exactly saturates `v0-v31`; it is
not a proof that every clever allocation is impossible, but it leaves no
required lowering/allocation margin.  P3B10 already showed that adding a coefficient scratch boundary
regresses P3B6 by 5.725 cycles despite retiring 121 fewer instructions.

The search supplies a witness, not a lower-bound certificate.  Therefore this
decision rejects only the straightforward pair-wait/no-scratch architecture;
it does not reject structured route9/packing co-design.

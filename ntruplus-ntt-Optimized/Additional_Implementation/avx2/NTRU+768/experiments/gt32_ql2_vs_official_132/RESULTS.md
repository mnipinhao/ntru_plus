# Results

Experiment 132 directly compared the qualified QL2 image with Official using
an explicit NTRU+768 SUPERCOP harness.  The harness fixes the 768 byte sizes
(`pk=1152`, `sk=2336`, `ct=1152`, `ss=32`) rather than depending on whichever
SUPERCOP implementation most recently occupied `work/compile`.

Experiment 104 was rebuilt and its geometry audit passed before this run:

- 82 pre-existing symbols retained identical address, size, and bytes;
- the Encap caller slot remained 611 bytes;
- E0V and QL2 tails remained deterministic RX-only sections;
- no RWX segment was present.

The existing experiment-104 correctness evidence was also rerun before this
campaign: 1000 deterministic cases, 768 noncanonical cases, immutable inputs,
KAT, ASan, and UBSan passed.

## Formal results

All deltas are `QL2 - Official`; negative is faster.

| ASLR | operation | Official Q2 | QL2 Q2 | delta | paired bootstrap 95% CI | favorable blocks |
|---|---:|---:|---:|---:|---:|---:|
| on | Keypair | 21497.10 | 21239.54 | **-257.56** | [-290.05,-227.64] | 16/16 |
| on | Encap | 28165.66 | 28252.92 | **+87.26** | [+42.21,+164.88] | 3/16 |
| on | Decap | 19301.34 | 19260.67 | **-40.67** | [-58.74,-6.39] | 12/16 |
| off | Keypair | 21441.78 | 21229.51 | **-212.27** | [-221.27,-196.31] | 16/16 |
| off | Encap | 28071.32 | 28253.31 | **+181.99** | [+134.94,+218.35] | 0/16 |
| off | Decap | 19272.44 | 19268.33 | -4.11 | [-23.94,+8.90] | 10/16 |

The ASLR-on campaign is the primary SUPERCOP-style result.  It says QL2 has
not yet crossed Official: Encap remains slower by about 87 cycles (0.31%).
ASLR-off independently agrees on the sign and shows a larger 182-cycle debt.

## Interpretation

QL2 remains a proven Encap architecture improvement.  Experiments 103 and 104
showed approximately 97 cycles in the convergence island, 120 cycles in a
controlled caller, and 71--97 cycles in geometry-preserving production A/B
runs.  Experiment 132 answers a different question: after applying that win,
is the complete QL2 implementation faster than Official?  The answer is no in
this image, although the remaining gap is only 0.31% in the primary run.

Keypair is still clearly faster than Official.  Decap is faster in the
ASLR-on primary run and statistically neutral with ASLR disabled.  Neither is
QL2 algorithmic credit because QL2 changes only Encap; they describe the full
candidate image relative to Official.

An initial infrastructure run was isolated under
`results-invalid-object-order/`.  That run sorted the QL2 objects
alphabetically and therefore destroyed experiment 104's link-order contract.
It must not be used for performance claims.  The final `results/` campaign
restores the exact experiment-104 implementation object order.

## Decision

QL2 is retained as the Encap research champion, but it is not promoted over
the `b2a4bea` production baseline yet.  The remaining target is an
approximately 90--180 cycle Encap-only debt versus Official.  Further work
must preserve Keypair/Decap geometry and should delete a real operation class;
another small placement sweep is not justified by this result.

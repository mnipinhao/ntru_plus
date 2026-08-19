# GT32-QWORD-FORWARD-ASM-016

This experiment implements the qword-semantic Forward selected by 013 without
modifying GT Clean.  It deletes `GT_BLEND3`, relabels the frontend twist rows,
stores DFT3 rows in packet order, and regenerates the five DIF NTT32 stages so
that the terminal is the unchanged private-M ABI.

## Executable correction to 013

The first executable differential exposed a coordinate error in the original
013 generator: the frontend phase entering a DIF NTT32 is indexed by input
column `q`, not by the bit-reversed terminal `physical_Q -> column_j` mapping.
After correcting that coordinate and the row-table pointer transition, the
candidate passes:

```text
1000 random coefficient inputs in [-3,4]
candidate Forward == production Forward (mod q)
candidate out == in alias == out-of-place candidate
```

Regenerating 013 with the correct coordinate changes its conservative terminal
bound from `14188` to `14358`.  Both 014 and 015 were regenerated.  The 014
symmetric inverse hard stop remains, while the actual Encap and post-inverse
Decap callsites still have zero-extra-instruction range closure.

## KEM differential

The same ELF contains production and candidate Encap/Decap callers.  Only the
two Forward symbols are redirected in the candidate caller.  One thousand
deterministic trials cover byte-exact Encap, valid Decap, and malformed
ciphertexts.  Return codes, ciphertexts, and shared secrets all match.

## Fixed-core benchmark

The benchmark uses one fixed ELF, `setarch x86_64 -R`, CPU 18, alternating
AB/BA order, 20 paired samples per launch, 64 calls per sample, and eight
process launches.  The launch-median paired deltas in TSC are:

```text
Forward:  +9, +4, +23, -7, +7, +8, -7, -7
Encap:   -29,-20, -26,  0,-20, -9,-43,-50
Decap:   +22, -5, +25,+61,+11,+35,-14,+28
```

Across launches:

```text
Forward median delta:  +5.5 TSC; candidate wins 3/8 launches
Encap median delta:    -23.0 TSC; candidate wins 7/8, one tie
Decap median delta:    +23.5 TSC; candidate wins 2/8 launches
```

The candidate removes 32 dynamic instructions per Forward in the static model,
but replaces cheap `vpblendd` routing with 16 additional Montgomery chains.
The measured standalone Forward does not improve on this AVX2 target.  The
small Encap-only improvement is therefore a caller/code-delivery interaction,
not evidence that the replacement Forward is intrinsically faster.  Decap,
which also executes two candidate Forwards, regresses at the launch median.

The candidate code is also larger: frontend plus core are 5637 bytes versus
4973 bytes for the selected production pair.  This is another reason not to
promote a marginal caller-only effect.

## Decision

```text
semantic correctness:            pass
KEM caller range closure:         pass
standalone Forward performance:   fail
Encap delivery:                   small/conditional
Decap delivery:                   fail
production promotion:             no
GT Clean modified:                no
```

The useful result is architectural: 014 does not block the real KEM callsites,
but the qword route-elimination trade itself is not faster on this CPU.

Run `make check` for differential tests and one local benchmark launch.  Use
`setarch x86_64 -R taskset -c 18 build/bench_qword_kem` for the controlled
launch configuration above.

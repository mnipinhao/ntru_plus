# GT32 QBM cross-factor packing gate 023

022 only rejected one packet under an instruction-count model.  This gate
isolates the stronger density question without claiming a cycle-level stop.

## Ordinary i32 output coordinates

`vpmaddwd` has eight independent dword destinations.  A quadratic product has
two independent pre-REDC i32 coordinates.  Therefore one instruction can
carry at most four complete factors when each coordinate occupies one dword.
Permuting or interleaving adjacent factors changes labels, not this capacity:
eight factors require sixteen dword results.

## Could one dword encode both residues?

After canonical reduction, `c0 + q*c1` fits in 24 bits because
`q^2-1 = 11,950,848`.  But producing it directly before REDC requires the
integer bilinear matrix

```text
[[1, q],
 [q, root]].
```

For the current lazy bound 3456, an i16 linear form valid over the complete
input cube can have coefficient L1 norm at most `floor(32767/3456)=9`.  A
two-product dot of such forms can generate a matrix entry of magnitude at
most `2*9*9=162`, not the required 3457.  The direct forms
`e0+q*e1` and `root*e1+q*e0` also exceed signed i16 by orders of magnitude.

Packing two residues after REDC is possible but too late: both output dots
and both reducers have already executed, so it cannot solve the atomic
first-result liveness problem.

## Decision

The apparent 8-to-4 density drop is structural under the current full-range
linear-i16 preparation and pre-REDC i32-coordinate contract.  This remains a
conditional packing stop, not a complete performance stop.  Nonlinear or
narrower producer encoding and whole-pipeline delayed reduction remain open.

The next required evidence is the missing cycle gate: matched-geometry ASM
for the selected eight-factor/two-madd QBM versus the four-factor atomic
expanded packet.  Static 22-versus-26 accounting must not substitute for that
benchmark.

## Reproduction

```sh
make check
```

# Checkpoint G1C1: adjusted inverse-head oracle

G1C1 closes the first adjusted inverse layer without adding assembly or cycle
claims. The candidate must reverse the GT factorization, not copy the textual
stage order of Official `invntt.s`. Its first layer is therefore the inverse of
the adjusted NTT16 distance-1 butterfly.

For each row-specific forward twiddle `z`, the persistent pair already contains
the two physical distance-1 outputs:

```text
S = a + z*b
D = a - z*b
```

The adjusted inverse head consumes those vectors directly:

```text
A2 = S + D
B2 = z^-1 * (S - D)
```

Thus `A2=2a` and `B2=2b`. There is no division by two, standalone
reconstruction, or Montgomery-exponent change.

## Generated closure

`generated/g1c-adjusted-inverse-head.json` records 576 scalar butterflies and
covers all 1,152 input and output cells exactly once. Every butterfly retains:

- branch, physical GT row, mathematical `p`, and terminal coefficient;
- paired physical lanes and mathematical `q` values;
- the two corresponding Official component positions and factor roots;
- forward and inverse twiddles;
- persistent-pair input and inverse-head output positions.

The 72 inverse twiddles satisfy both `z*z^-1=1 mod q` and the local matrix
identity `I1(z)F1(z)=2I`. Generated Montgomery and `qinv` tables are available
as both a C header and an assembly include.

## Scale and range

| Path | input scale / R exponent | output scale / R exponent | sum/difference | twisted difference |
| --- | --- | --- | ---: | ---: |
| BMScale | 16 / R^-1 | 32 / R^-1 | [-27648,27648] | [-2441,2441] |
| BaseInv | 1/4 / R0 | 1/2 / R0 | [-6912,6912] | [-1899,1899] |

Every recorded intermediate fits signed 16-bit arithmetic and no extra
reduction is required at this layer. The test performs 720,576 independent
round-trip algebra checks in addition to component coverage and constant
checks.

## Authorization boundary

The standalone adjusted inverse distance-1 ASM is now authorized. The linked
G1C-M C2 tail+head is not yet authorized: its next checkpoint must define how
live BMScale result registers emit persistent-pair data without a converter,
then differential-test the linked tail+head and audit its register pressure and
materialized seam. Cycles remain null until that linked prototype exists.


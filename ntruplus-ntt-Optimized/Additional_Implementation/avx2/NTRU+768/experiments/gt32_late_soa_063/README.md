# GT32-LATE-SOA-063

Architecture-critical composition gate for one fixed `(branch,k3)` NTT32
island.  The common input is the current TILE4 state after Forward S3; the
common output is current TILE4/AoS after inverse stages I0 and I1.

This does **not** modify GT Clean or any KEM caller.

## Why this gate exists

Older gates measured the two relevant mechanisms separately:

- Forward S5 can directly form the private coefficient-plane BM layout.
- BM plane redeposit can absorb inverse I0 and feed I1 without a complete AoS
  materialization.

The old complete chain still inserted `SoA product -> AoS transpose -> inverse`.
This experiment closes that composition gap.

## Paths

- `C0`: AoS S4/S5, materialized TILE4 BM, standalone inverse I0/I1.
- `C1`: AoS S4/S5, BM output redeposit fused with inverse I0/I1.
- `L0`: S4/S5 directly form private SoA, SoA BM consumes it, and BM output
  redeposit is fused with inverse I0/I1.

Thus `C1-C0` attributes the output/inverse seam, `L0-C1` attributes the
input-side Late-SoA seam, and `L0-C0` is the architecture result.

## Commands

```sh
make test
make audit
make bench-short
make pmu
```

The benchmark is a short same-ELF paired directional gate, not a production or
KEM promotion benchmark.

## Result

All 1,336 correctness cases passed exactly at the common post-I1 endpoint.
There are no stack references or spills in the measured leaves.

Median of eight launches, candidate minus `C0`:

| region | `C1` TSC | `L0` TSC | `L0` core cycles | `L0` instructions |
|---|---:|---:|---:|---:|
| 2x suffix | 0.0 | +8.0 | +19.33 | +41.60 |
| BM through I1 | -1.0 | -25.0 | -42.53 | -87.84 |
| complete | -0.5 | **-10.0** | **-18.27** | **-43.56** |

The output/inverse seam alone (`C1`) is approximately neutral in the complete
island.  `L0` wins because its more expensive terminal plane formation is more
than repaid when both BM input transposes disappear.  This is the first direct
measurement of the complete Late-SoA composition; it is not inferred by adding
two older isolated gates.

Decision: **architecture-critical pass / pause before integration**.  Per the
gate contract, no DFT3 producer landing, six-tile backend, or KEM integration is
implemented here.

# GT32-LATE-SOA-064

Six-tile arithmetic closure for the Late-SoA mechanism proven by experiment
063.  It compares complete `2F+B+I` NTT32 arithmetic from two already-formed
TILE4 frontend states to the common inverse-core output.

No DFT3, frontend, inverse tail, `crepmod3`, or KEM caller is changed.

## Profiles

- `C0`: selected TILE4 Forward, materialized selected B3, selected inverse.
- `C1`: selected TILE4 Forward, AoS B3 redeposit fused through inverse I1,
  followed by the common remaining inverse.
- `L0`: Late-SoA Forward terminal, SoA-native B3 fused through inverse I1,
  followed by the same remaining inverse.

The only new arithmetic leaf is a six-tile loop around the already-validated
063 SoA B3-to-I1 block.  All other symbols are reused from the existing TILE4
experiment.

## Reproduce

```sh
make test
make audit
make bench-short
make pmu
```

## Result

All 1,776 correctness cases pass exactly for both the post-I1 checkpoint and
the complete inverse-core output.  The new six-tile bridge is a compact loop
with zero stack references and zero spills.

Median of eight launches, candidate minus `C0`:

| region | `C1` TSC | `L0` TSC | `L0` core cycles | `L0` instructions |
|---|---:|---:|---:|---:|
| 2x Forward | +0.5 | +66.5 | +93.52 | +240.63 |
| B3 through inverse I1 | +29.5 | -118.5 | -182.00 | -523.22 |
| remaining inverse | 0.0 | 0.0 | -1.71 | -0.44 |
| complete `2F+B+I` | +2.0 | **-68.0** | **-130.48** | **-153.55** |

`L0` is negative in all eight launches.  The complete-region PMU also reports
approximately `+2.19` loads, `+0.05` stores, `-5.01` branches, `-25.96` IDQ
not-delivered uops, and no meaningful L1D-pending change.  Therefore the win is
not a claim that the complete chain moves less data: it is a cheaper executable
terminal/BM/inverse-entry DAG with lower instruction and frontend-delivery cost.

The isolated rows are attribution, not additive component timing.  In
particular, `C1` is slower in the isolated B3/I1 region but nearly neutral in
the complete chain.  The complete `-68 TSC` measurement is the architecture
decision.

Decision: **REPRESENTATIVE_ISLAND_PASS**.  The next eligible gate is a full
GT32 arithmetic-chain integration, but it is intentionally not implemented by
064.

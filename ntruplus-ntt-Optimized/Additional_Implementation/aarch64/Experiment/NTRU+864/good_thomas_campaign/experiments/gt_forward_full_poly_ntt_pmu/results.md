# M5P results

The frozen Pi 5 PMU campaign completed on Cortex-A76 r4p1, Linux
6.18.33+rpt-rpi-2712, GCC 14.2.0, pinned to core 3.  It used one binary, 61
samples per order, 20,000 calls per sample, 100 warm-ups per variant, and three
complete `Official -> GT -> GT -> Official` repetitions.

| Repetition | Official cycles p10/p50/p90 | GT cycles p10/p50/p90 | GT change |
| --- | --- | --- | --- |
| 1 | 4395.85 / 4395.96 / 4396.15 | 4694.74 / 4695.22 / 4695.63 | +6.81% |
| 2 | 4395.80 / 4395.97 / 4396.20 | 4695.83 / 4696.41 / 4696.93 | +6.83% |
| 3 | 4395.84 / 4396.01 / 4396.18 | 4694.83 / 4695.13 / 4695.54 | +6.80% |

Across all 366 samples per implementation:

- Official: 4395.98 p50 cycles, 4035.00 instructions, IPC 0.9179, cycle IQR
  0.19.
- GT: 4695.42 p50 cycles, 4832.00 instructions, IPC 1.0291, cycle IQR 1.04.
- Paired `GT - Official`: +299.43 p50 cycles, IQR 1.02 cycles.
- GT executes about 797 more retired instructions per call.  Its higher IPC
  recovers part, but not all, of that instruction-count cost.

Every one of the six timed processes first passed 64 disjoint and 64 exact
in-place comparisons with input preservation and output sentinels: 384 cases
of each alias mode total.  All results matched modulo q through the frozen M5O
ABI map.  Temperature rose from 56.0 C to 62.6 C; every environment check was
`throttled=0x0`.

Local/remote source identities used by the formal run:

- Official NTT: `2ffb45951c3156eb41aabc1f5032b558dabd16d4dd7162a8a32a4142509e3489`
- top split: `8ccc5cbd18bb8445f20b219ff675e93d826340c28ea2c8811953ff7096df02e0`
- M5N pass 2: `259c7d4dfbdb0f5b2038511f81ade9b92663c2612570bb042a1463464a83db60`
- M5O wrapper: `be9fb246c8c792481d7452c5900a5001f4b824b5c5d07dc40eed91533e4211e9`
- benchmark harness: `3d1a0423714581af953848a77d54fec227c7cf386bfb3dc731a2868174972b6c`
- formal runner revision: `f0760a26fe05be15da22826c0863d9fdbab63f47bcc2e5b1f02d23ba96f0f407`

Remote object text sizes were 8,016 bytes for the Official `ntt.s` object
(which also contains inverse code/tables) and 5,268 bytes across the three GT
objects.  These whole-object figures are source-closure/I-cache context, not a
like-for-like live Forward byte count.

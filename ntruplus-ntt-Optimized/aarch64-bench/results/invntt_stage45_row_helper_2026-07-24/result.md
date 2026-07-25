# InvNTT Stage45 Row-Helper Result

Date: 2026-07-24

Machine: Raspberry Pi 5, Cortex-A76, core 3 pinned, Linux `perf_event_open`.
Both KEM variants use the current GT production source closure and portable
`NO_CE` SHAKE.

## Direct InvNTT

Configuration:

```text
NTESTS=61
NITERATIONS=20000
NWARMUP=300
NINPUTS=64
```

| Event | Production p50 | Helper p50 | Paired p50 delta | Wins |
|---|---:|---:|---:|---:|
| cycles | 3581.894 | 3580.377 | -1.520 | 61/61 |
| instructions | 4816.001 | 4822.001 | +6.000 | 0/61 |

Cycle paired-delta distribution:

```text
p10=-1.881, p50=-1.520, p90=-1.028 cycles
```

## Same-Binary Full KEM

Configuration:

```text
NTESTS=61
NITERATIONS=2000
NWARMUP=100
NINPUTS=32
order=AB/BA
```

| Scope | Production cycles | Helper cycles | Paired cycle delta | Instruction delta |
|---|---:|---:|---:|---:|
| keypair | 37888.700 | 37886.785 | -2.626 | 0 |
| encapsulation | 37975.538 | 37971.943 | -3.605 | 0 |
| decapsulation | 32991.325 | 33002.902 | +11.750 | +6 |

Only decapsulation calls the changed InvNTT. Its cycle delta distribution was:

```text
p10=+9.266, p50=+11.750, p90=+13.943 cycles
candidate wins=0/61
```

Correctness:

```text
prepare inputs=32, mismatches=0, capture_error=0
paired checks=366, mismatches=0
```

## Isolated Full-Decap Binaries

This check removes the main limitation of the same-binary harness: each
executable contains only its selected InvNTT. Both `poly_invntt` symbols start
at `0xbf90`, so function address modulo 32 and modulo 64 are both equal:

```text
addr_mod32=16
addr_mod64=16
```

Binary text:

```text
production=74857 bytes
helper=72233 bytes
delta=-2624 bytes
```

Eight balanced A/B pair medians:

```text
production: 32814, 32815, 32825, 32836, 32839, 32839, 32827, 32860
helper:     32846, 32817, 32838, 32844, 32853, 32818, 32840, 32846
paired deltas: +32, +2, +13, +8, +14, -21, +13, -14 cycles
paired median delta: approximately +10.5 cycles
helper wins: 2/8
```

## Decision

Reject as a speed optimization, but accept as a production code-size tradeoff.
It saves about 2.6 KB while the current full decapsulation path regresses by
roughly 10-12 cycles, about 0.03%. The production documentation must not claim
that the helper itself accelerates InvNTT or decapsulation.

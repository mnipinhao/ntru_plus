# Results

## Hard-gate result

All four two-block regions pass.

| Case | Instructions | Public loads | RA wall time | N1 proxy cycles | Boundary copies/spills/stores |
| --- | ---: | ---: | ---: | ---: | ---: |
| `t0c1` | 308 | 68 | 23.168698 s | 77 | 0 |
| `t0c2` | 308 | 68 | 23.950665 s | 77 | 0 |
| `t1c1` | 276 | 36 | 18.093823 s | 69 | 0 |
| `t1c2` | 276 | 36 | 18.209409 s | 69 | 0 |

Every RA run is `OPTIMAL` with self-check `OK`; every schedule reports
`split_heuristic_full:OK!`.  The emitted regions assemble for AArch64.  The
audit proves eighteen distinct live-outs and proves that no block-0 output
register is overwritten after block 1 starts.

## Boundary cost

CF2's two isolated schedule proxies sum to 76 cycles for top 0 and 68 for top
1.  The composed regions report 77 and 69 respectively.  The exact boundary
therefore adds one N1-proxy cycle and zero instructions.  This is evidence that
the 18-value live boundary is feasible, not a Cortex-A76 performance claim.

The full-Forward arithmetic/load estimate is unchanged from CF2: `+280`
instructions relative to M5R-D before address setup, only eight instructions
below rejected CF0 after its four address setups.  A target speedup remains
unproven.

## Generic parser limitation

The required generic log parser was run.  It falsely classifies the literal
configuration message `Setting timeout of 1800 seconds` as a timeout and also
interprets the RA functional objective as a cycle result.  The complete logs
contain `OPTIMAL` and self-check `OK`; the checked-in audit validates those
terminal markers, the returned assembly, boundary liveness, and assembler
acceptance directly.

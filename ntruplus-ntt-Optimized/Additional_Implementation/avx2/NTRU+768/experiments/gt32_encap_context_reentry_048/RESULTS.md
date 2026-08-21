# GT32 Encap Context Re-entry 048 Results

## Correctness and method

- Official and GT consume the same count-0 canonical KAT public key and the
  same deterministic 96-byte coins.
- R2 output digest matches: `0bbaba5c59497d54`.
- R3 output digest matches: `f146801723341fbf`.
- CPU affinity is fixed to core 1.
- Each process collects 2,048 samples per target/context with rotated ordering.
- HOT executes the identical target eight times immediately before timing.
- REAL executes the actual semantic Encap prefix, excludes it from timing, and
  then times the identical target.
- Two independent 64-block Official/GT AB/BA runs were completed.

No prefix-duration subtraction is used.

## Independent runs

### Run 1

| Target | GT−Official HOT | GT−Official REAL | Differential context penalty |
|---|---:|---:|---:|
| R2 | -12 | -10 | +2, CI [+2,+2] |
| R3 | -12 | +2 | +14, CI [+14,+14] |

### Run 2

| Target | GT−Official HOT | GT−Official REAL | Differential context penalty |
|---|---:|---:|---:|
| R2 | -12 | -12 | 0, CI [0,0] |
| R3 | -14 | -8 | +6, CI [+6,+8] |

## Pooled 128-block diagnostic

| Target | GT−Official HOT | GT−Official REAL | Differential context penalty | 95% CI |
|---|---:|---:|---:|---:|
| R2 | **-12.0** | **-11.5** | **+1.5** | [0,+2] |
| R3 | **-14.0** | **-2.0** | **+10.0** | [+8,+12] |

All 128 R3 blocks report a positive differential context penalty. The effect is
therefore real: the hash/SOTP/R2 history makes the subsequent GT R3 relatively
more expensive, almost eliminating its small controlled-hot advantage.

## Interpretation

The proposed context-composition mechanism is partially correct, but its
measured magnitude is insufficient:

```text
direct R2 context erosion     about  1–2 cycles
direct R3 context erosion     about 10 cycles
combined scale                about 11–12 cycles
full Encap unexplained scale  about 170–250 cycles
```

The experiment also corrects the historical planning baseline: in this current
minimal matched-target harness, HOT R2/R3 are each only about 12–14 cycles
faster than Official, not the older isolated-region estimates of 37–44 cycles.
Those older numbers came from different harness/image/region shapes and cannot
be inserted into a current full-caller sum.

## Limitation

048 reproduces the actual prefix instruction sequence and times the same target
under two histories, but it is a dedicated harness rather than instrumentation
inside the exact production SUPERcop ELF. It therefore proves a small direct
re-entry effect; it does not prove that all remaining cycles reside outside R2
or R3, nor does it fully reproduce production image geometry.

## Decision

Do not optimize based on a presumed +200-cycle GT kernel re-entry penalty. The
direct penalty exists but is too small. Production remains unchanged. A further
attribution step is justified only if it instruments fixed regions inside the
exact production image; otherwise the remaining gap should be treated as a
whole-caller non-compositional result rather than a sum of isolated debts.

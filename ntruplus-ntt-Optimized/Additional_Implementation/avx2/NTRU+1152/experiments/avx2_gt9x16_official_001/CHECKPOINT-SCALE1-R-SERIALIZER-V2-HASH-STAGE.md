# Serializer V2 direct hash-stage pass elimination

## Architecture

The cumulative path formerly performed:

```text
wire state -> Serializer V2 -> 1728-byte temporary
temporary  -> hash_g memcpy -> 1729-byte domain-separated stage -> SHAKE
```

The candidate performs:

```text
wire state -> Serializer V2 -> stage[1..1728]
stage[0] = 0x01
unchanged SHAKE
```

This preserves the materialized Forward boundary but removes one complete
1728-byte reload plus one complete 1728-byte staging copy. It does not change
the hash, SOTP, Forward, wire representation, or Serializer V2 arithmetic.

## Correctness

One thousand real CBD1 Forward states pass exact `hash_g` output differential.
Input immutability and ASan/UBSan pass. The candidate retains an aligned local
1729-byte stage because the unchanged SHAKE API consumes a contiguous input.

## SUPERCOP-derived serious result

CPU 1, performance governor, turbo disabled, common O3GC recipe, balanced
same-ELF order, nine fresh processes, 1728 pooled observations per variant.

| boundary | control StQ2 | candidate StQ2 | delta | direction |
|---|---:|---:|---:|---:|
| P0 serializer + hash input staging, no SHAKE | 749.7569 | 692.1644 | -57.5926 | 9/9 |
| P1 serializer + complete `hash_g` | 18572.6435 | 18505.8356 | -66.8079 | 9/9 |

P0 proves that the removed 3456 bytes of copy traffic is real machine credit.
P1 shows that the credit survives the unchanged SHAKE consumer, although the
large SHAKE body makes its absolute estimator noisier.

## Full representation-boundary conclusion

The remaining `wire state -> serializer` boundary contains 72 vector reloads.
A side product substantially smaller than the 1152 residues cannot replace
those reloads: exact serialization depends on every residue. Removing this
boundary therefore requires one of:

1. producer/serializer fusion;
2. a different persistent r ABI jointly consumed by MA2 and serialization;
3. direct absorption of packed terminal output into Keccak state.

The already measured full-terminal dual-output fusion lost about 421 cycles.
Serializer V2 recovers only about 47 isolated cycles, so repeating that same
fusion with a better pack schedule is not currently justified. The remaining
credible architecture gate is an r-specific shared-ABI/D1-orientation search,
where serializer-native stride-8 formation must be absorbed rather than moved
from the serializer into Forward or MA2.

## Decision

Direct hash-stage output is selected for the next caller candidate. First
price it through SOTP using the unchanged caller; if the approximately
57--67-cycle credit survives, integrate it into a new Native candidate. Do
not reopen full Forward-terminal serialization without new evidence that its
formation can be absorbed into D1 output orientation.

# GT32 QBM atomic hand-ASM gate 024

This experiment supplies the cycle evidence deliberately left open by 022
and 023.  It does not modify GT Clean or any production symbol.

## Compared kernels

Both symbols use 768-byte matched cages, have no stack references or spills,
and are emitted in normal and reversed order.

`qbm_selected_control_asm` implements the selected eight-factor/two-output
QBM-PREWEIGHT packet.  `qbm_atomic_expanded_asm` implements the strongest
four-factor atomic packet found under the same input and REDC32 contract:

```text
A duplication with two vpshufb masks
B weighted/swap construction
two vpunpck*dq routes
two vpmaddwd output dots
two REDC32 chains
one vpackssdw
```

The actual assembly improves the earlier 26-instruction estimate: the final
pack naturally restores factor order, so no final interleave shuffle is
needed.  The atomic loop is therefore 25 vector/data instructions rather than
26.  It is nevertheless three static instructions longer than control per
iteration.  Across 48 iterations this predicts 144 extra retired
instructions per call.

## Correctness

Normal and reversed binaries pass 1,000 random trials, boundary vectors, and
alias differential tests against the existing intrinsic oracle.  Output is
word-exact.

## Cycle result

Four launches per placement, 40 paired samples per launch, 2,000 calls per
sample, pinned to the first available CPU:

| Placement | Atomic - control median TSC | Negative launches | Sample wins |
|---|---:|---:|---:|
| Normal | +38.874 | 0/4 | 6/160 |
| Reversed | +34.501 | 0/4 | 0/160 |

Positive is slower.  Symbol order does not change the conclusion.

## PMU attribution

Process-scoped counters use one million calls per run and five repeats per
mode/placement.  Values below are median atomic-minus-control per call:

| Placement | Core cycles | Instructions | Retired uop slots | Port 5/11 uops |
|---|---:|---:|---:|---:|
| Normal | +56.01 | +143.82 | +191.98 | +128.35 |
| Reversed | +58.54 | +139.84 | +187.87 | +127.32 |

The measured instruction delta matches the exact 3 x 48 static prediction.
The extra routes are not hidden behind REDC32 latency; they materially raise
retired work and pressure on the shuffle-capable port group.

## Decision

The current-input/current-reduction four-factor atomic expanded packet is a
cycle-level hard stop.  This is deliberately narrower than saying that every
atomic or dual-output design is impossible.

Reopen only if producer-native preparation, a narrower/nonlinear input
contract, or a QBM-to-inverse delayed-reduction ABI removes a complete packet
construction or reduction boundary.  Merely rescheduling this packet is not
supported by the measured headroom.

## Reproduction

```sh
make check
make bench
make pmu
```

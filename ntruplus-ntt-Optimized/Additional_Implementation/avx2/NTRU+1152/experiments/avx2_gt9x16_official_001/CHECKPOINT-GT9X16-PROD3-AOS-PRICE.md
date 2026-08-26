# GT9X16-PROD3-AOS-PRICE

## Scope

This checkpoint prices only the complete forward-producer boundary:

```text
Control:   coefficient input -> unchanged top split
           -> four G0/P2-B pair paths -> exact 2,304-byte MA2 ABI

Candidate: coefficient input -> unchanged top split
           -> persistent-AoS PROD3 FULL -> exact same MA2 ABI
```

MA2 arithmetic, resident `h`, serialization, and KEM code are not executed.
Both paths use the same input residency and stop at a raw bit-exact boundary.

## Linked PRICE object

The benchmark builds a candidate-only copy of the FULL assembly. The old
standalone branch-0 and old FULL symbols are compile-time excluded from that
archive member. The saved benchmark ELF passes a strict retention gate:

- candidate symbol size: 16,569 bytes;
- old standalone branch-0 retained: no;
- old FULL symbol retained: no;
- entry alignment: 32 bytes;
- saved ELF type: PIE (`ET_DYN`).

The linked movement delta remains exactly the FULL audit result: 144 fewer
data loads, 72 fewer data stores, and 360 fewer routing instructions, with
unchanged Montgomery-chain and Barrett-vector counts. The candidate still
pays 78 more constant-memory operands and 8,826 more symbol text bytes.

## Placement and ASLR policy

Two fixed-common O3GC SUPERCOP ELFs were built from separate implementation
directories. Only flat archive source order differs:

```text
normal:   control ASM @ 0x4460, candidate ASM @ 0x62a0
reversed: candidate ASM @ 0x4460, control ASM @ 0x85c0
```

Both ELFs have identical 41,239-byte `.text` and 17,472-byte `.rodata`
sections. A nine-process ASLR-on selection phase chose the lower absolute 2x
candidate StQ2, not the largest paired delta:

| placement | candidate 2x StQ2 | control 2x StQ2 |
| --- | ---: | ---: |
| normal | 2945.1667 | 3380.7801 |
| reversed | **2942.6806** | 3376.3889 |

Reversed placement was locked before the serious replay. The headline is
reversed placement with ASLR enabled because unmodified SUPERCOP executes a
PIE under the host ASLR policy; SUPERCOP does not invoke `setarch -R`.
ASLR-off and alternate-placement runs are diagnostic controls, not equal
promotion gates.

## Serious result

Each setting uses nine fresh processes. Every label has 96 observations per
process and first/second balanced ordering. The headline result is:

| 2x producer | pooled StQ2 |
| --- | ---: |
| G0/P2-B control | 3377.8935 |
| persistent-AoS candidate | **2946.5231** |

The candidate wins 9/9 launches. Its per-launch median candidate-minus-control
delta is **-429.1250 cycles**, with a deterministic paired-launch bootstrap
95% interval of **[-432.1458, -425.1875]**. The pooled StQ2 ratio is 0.8723,
or approximately 12.8% lower than the control.

The one-forward attribution result is 1588.1921 versus 1809.7755 pooled StQ2,
also in the candidate direction.

## Controls

| setting | 2x candidate StQ2 | 2x control StQ2 | paired median delta | direction |
| --- | ---: | ---: | ---: | --- |
| reversed, ASLR on (headline) | 2946.5231 | 3377.8935 | -429.1250 | 9/9 |
| reversed, ASLR off | 2943.8750 | 3376.1597 | -430.8750 | 9/9 |
| normal, ASLR on | 2947.1829 | 3378.8750 | -430.8750 | 9/9 |
| normal, ASLR off | 2945.6667 | 3380.8194 | -434.3333 | 9/9 |

ASLR-on produced nine distinct runtime address tuples in each placement;
ASLR-off produced one. All four bootstrap intervals remain entirely below
zero. Placement changes absolute time by only a few cycles and never changes
the conclusion.

The run recorded CPU 1 with the host in `performance` governor and Intel turbo
disabled. Frequency state is metadata rather than a hidden runner mutation;
the benchmark scripts did not change the host policy.

## Decision

Persistent AoS is selected over the G0/P2-B realization at the exact MA2
boundary. This is the first complete producer result where its large unrolled
code footprint and additional constant operands are directly priced and still
win against the smaller dynamic-pair implementation.

This remains a SUPERCOP-derived boundary result, not a native SUPERCOP KEM
number and not a production promotion. The next authorized checkpoint is one
consumer-shaped island only:

```text
two coefficient inputs
-> unchanged top split
-> G0/P2-B control or selected persistent-AoS producer
-> identical resident-h projection
-> identical MA2 arithmetic / inv4 / serializer
-> ciphertext
```

Only if that credit survives the unchanged consumer should native
encapsulation KAT and SUPERCOP `enc_cycles` be reopened.

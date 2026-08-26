# GT9X16-PROD3-AOS-CONSUMER

## Scope

This checkpoint changes exactly the two GT producer implementations inside
the complete MA2 ciphertext island:

```text
Control:
  top split(r/m) -> G0/P2-B(r/m) -> exact MA2 planes
  -> resident h -> native MA2 -> inv4 -> serializer -> ciphertext

Candidate:
  top split(r/m) -> PROD3 persistent AoS(r/m) -> exact MA2 planes
  -> same resident h -> same native MA2 -> same inv4 -> same serializer
  -> ciphertext
```

No MA2 schedule, resident-`h` projection, twist, serializer, producer code
organization, reduction, or top-split arithmetic is changed.

## Correctness

A repository test executes 257 zero, alternating, and random-small r/m cases.
It compares both 2,304-byte producer outputs raw and both 1,728-byte
ciphertexts byte-for-byte. Input immutability and ASan/UBSan pass.

The linked SUPERCOP ELF independently enforces the direct-transfer graph.
Control contains two top splits, eight P2-B pair calls, and one native MA2
tail. Candidate contains two top splits, two PROD3 FULL calls, and the exact
same native MA2 tail. No old standalone branch-0 or old FULL symbol is
retained.

## Placement selection

Independent nine-process ASLR-on selection uses the minimum absolute candidate
StQ2:

| placement | candidate StQ2 | control StQ2 |
| --- | ---: | ---: |
| normal | **4762.1204** | 5189.9213 |
| reversed | 4763.2523 | 5188.3588 |

Normal is selected. The two ELFs have identical 101,847-byte `.text` and
19,616-byte `.rodata`; only archive placement differs. The selected ELF has:

- native MA2: 27,791 text bytes;
- P2-B control: 7,743 text bytes;
- PROD3 candidate: 16,569 text bytes;
- all relevant entries aligned to 32 bytes.

## Serious result

The headline is an independent nine-process normal-placement ASLR-on replay,
matching SUPERCOP's PIE/host-ASLR behavior. Each label contributes 96
observations per process with balanced first/second order.

| complete ciphertext island | pooled StQ2 |
| --- | ---: |
| G0/P2-B + unchanged MA2 | 5192.9537 |
| PROD3 AoS + unchanged MA2 | **4765.0602** |

The pooled difference is -427.8935 cycles. The candidate wins 9/9 launches;
the per-launch median delta is **-432.0000 cycles**, with paired-launch
bootstrap 95% interval **[-436.1875, -421.9583]**.

## Controls

| setting | candidate StQ2 | control StQ2 | paired median delta | direction |
| --- | ---: | ---: | ---: | --- |
| normal, ASLR on (headline) | 4765.0602 | 5192.9537 | -432.0000 | 9/9 |
| normal, ASLR off | 4760.5394 | 5189.2245 | -429.0625 | 9/9 |
| reversed, ASLR on | 4764.4907 | 5191.0694 | -427.6667 | 9/9 |
| reversed, ASLR off | 4762.4120 | 5189.2014 | -426.6250 | 9/9 |

Every bootstrap interval is entirely below zero. ASLR-on produces nine unique
runtime-address tuples per placement and ASLR-off one. Placement and ASLR do
not change the conclusion.

## Credit survival

The preceding producer-only headline had a -429.1250-cycle paired median.
The complete consumer island has -432.0000 cycles. These are independent
campaigns and are not subtracted as one formal estimator, but their agreement
shows that essentially all persistent-AoS producer credit survives the
producer-to-MA2 boundary. The large combined frontend footprint does not
create a visible regression in this warm caller-shaped island.

## Decision

Persistent AoS is the selected GT9x16 producer baseline; G0/P2-B remains the
historical/control producer. Compact/shared-helper PROD3 and permutation
micro-optimization stay deferred.

This is still a SUPERCOP-derived ciphertext-island result, not native KEM
evidence. Its stable approximately 430-cycle credit reauthorizes the next
sequence without changing anything else:

```text
complete encapsulation KAT
-> native SUPERCOP enc_cycles
-> fixed-common paired ELF
-> selected-placement confirmation and attribution
```

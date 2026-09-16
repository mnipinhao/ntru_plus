# G0 range and scale proof

## Header

- Ring: `Z_3457[x]/(x^864-x^432+1)`
- Forward input: signed int16 representatives in `[-3456,3456]`
- Transform-domain layout: FR-0 SoA, 288 leaves x 3 components
- Transform-domain scale: R0
- BaseMul zeta scale: R1
- M5C and M5E output scale: R0
- Narrow arithmetic: signed 16-bit Neon lanes
- BaseMul accumulators: signed 32-bit widened lanes
- Secret-dependent control/addressing: none introduced

## Current chain

| Stage | Operation | Input bound | Largest intermediate | Output bound | Type |
| --- | --- | ---: | ---: | ---: | --- |
| NTT16 | constant-specific Algorithm-10 radix-2 | `3456` | `9342` | `9342` | int16 |
| NTT9 twist | Algorithm-10 public constants | `9342` | `2197` | `2197` | int16 |
| level-1 B3 | one-product radix-3 | column-specific | `13563` | column-specific | int16 |
| eta correction | Algorithm-10 | level-1 output | `1863` | `1863` | int16 |
| level-2 B3 | one-product radix-3 | column-specific | `25569` | `[-25569,25566]` | int16 |
| M5C products | up to three widened variable products | `25569` | `1961321283` | R-1 temporaries | int32 |
| M5C BaseMul | zeta and RSQ reductions | FR-0 R0 | same int32 maximum | `2148` | int16 R0 |
| M5C BaseMulAdd | fused R0 addend | FR-0 R0 | same int32 maximum | `2205` | int16 R0 |
| M5E inverse NTT9 | one/two radix-3 layers | `2205` | `15981` | fixed-product bounded | int16 |
| M5E inverse NTT16 | four lazy radix-2 layers | fixed-product `3444` | `17220` | final `6888` | int16 R0 |

Every one-product difference is at most `12604`; its Algorithm-10 result is at
most `1893`.  All 288 physical leaves are carried separately into BaseMul, so
the proof does not silently replace a lane-dependent zeta with one favorable
constant.  A symmetric `[-25569,25569]` M5C consumer contract is also safe.

The M5E fixed-multiply theorem is rerun over all 65,536 signed-halfword inputs
for 270 distinct constants: 17,694,720 products, zero congruence failure, and
maximum output magnitude 3444.

## Boundary changes relative to the archived chain

| Contract | Historical | G0 authoritative |
| --- | ---: | ---: |
| NTT16 producer | `8874` | `9342` |
| FR-0 BaseMul operand | `24438` | `25569` |
| BaseMul output | `2114` | `2148` |
| BaseMulAdd / Inverse input | `2168` | `2205` |
| M5E maximum lazy halfword | `17220` | `17220` |

The last value is unchanged because M5E's four inverse16 layers are dominated
by the universal `3444` Algorithm-10 output bound, not by the 37-coefficient
increase at its input.

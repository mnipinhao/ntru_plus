# P42 — CMLT+MLS ToBytes canonicalization

P42 is complete and is **not promoted**. Production remains the P24 Full and
Small ToBytes kernels.

## Historical audit

P15/P16 used `CMLT`, but their correction was still `CMLT + AND + ADD`.  The
exact `CMLT + MLS` lowering had not been isolated on the current P24 global
routing DAG.  P42 is therefore the first same-boundary test of the proposed
two-instruction form.

## Identity and static effect

For negative signed halfwords `CMLT` produces `-1`, otherwise `0`. Therefore
`MLS x,mask,q` computes `x-mask*q`, exactly `x+q` for negative x and x
otherwise. Exhaustive comparison over all 65,536 signed-int16 values passed.
The frozen P23/P24 route oracle also passed all 516 exact lane-map/byte cases.

The complete public call handles 108 routed vectors, so the change retires
exactly 108 fewer instructions in both modes. Loads, stores, branches, route,
pack, scratch and ABI are unchanged.

## Slothy pipeline signal

Fixed-allocation three-output scheduling used `/Users/chenpinhao/slothy`, with
renaming and spills disabled.  Despite fewer instructions, the Cortex-A76
model regressed:

| Mode | P24 instructions/top | P42 | P24 model cycles/top | P42 |
|---|---:|---:|---:|---:|
| Full | 1041 | 987 | 1495 | 1562 |
| Small | 933 | 879 | 1010 | 1071 |

This is the expected risk: `SSHR/AND/ADD` uses non-multiply SIMD resources,
whereas the second P42 instruction is an `MLS`. Full already places it after
the Barrett `SQRDMULH+MLS`; Small also loses the ability to distribute the
three correction operations across distinct execution resources.

## Pi 5 decision

The selected tree was `/home/pi/supercop-20260831`; the host remained
unthrottled. All component, KAT, malformed-ciphertext and exact/tampered KEM
gates passed.

| Mode | P24 cycles | P42 cycles | Delta | Instructions delta | IPC P24 -> P42 |
|---|---:|---:|---:|---:|---:|
| Full | 1393.617 | 1401.055 | **+7.438** | -108 | 1.5558 -> 1.4704 |
| Small | 985.117 | 999.891 | **+14.774** | -108 | 1.9776 -> 1.8404 |

Complete Keygen/Encaps/Decaps also regress by `+26.625/+18.525/+25.825`
paired-median cycles, while retiring `324/216/216` fewer instructions. This is
a clean pipeline counterexample: fewer instructions are slower because the
new instruction class is placed on the limiting resource.

P42 is rejected. The prior precedence-aware route-cache borrowing proposal is
retained and renumbered P43.

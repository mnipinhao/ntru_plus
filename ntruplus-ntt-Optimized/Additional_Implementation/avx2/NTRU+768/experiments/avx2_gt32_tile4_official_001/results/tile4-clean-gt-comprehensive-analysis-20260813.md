# Clean GT comprehensive analysis (2026-08-13)

## Executive conclusion

The fixed-ELF, multi-launch SUPERcop result is decisive but small:

| Operation | CleanGT - Official | Relative | 95% bootstrap CI | Decision |
|---|---:|---:|---:|---|
| Keypair | -33.76 core cycles | -0.157% | [-80.83, -13.42] | CleanGT wins narrowly |
| Encap | +113.92 core cycles | +0.406% | [+40.04, +154.83] | CleanGT loses |
| Decap | +28.24 core cycles | +0.146% | [+16.65, +50.33] | CleanGT loses |

These are hardware core cycles from SUPERcop's `default-perfevent` backend,
not TSC estimates.  Both ABBA/BAAB order families have the same sign and all
three intervals exclude zero.  The complete CleanGT backend therefore does not
beat Official Main.  Official remains the full-backend default.

The architectural result is nevertheless positive: GT32 has a substantially
faster Forward NTT, arithmetic-parity quartic BaseMul, and successful GT-native
Q24 wire boundaries.  Its gains are consumed by the BaseMul/inverse composite,
serialization and representation boundaries, extra loads, critical-path/IPC
cost, and the much larger specialized code/data image.

## Evidence hierarchy

1. The fixed-ELF 64-launch SUPERcop comparison above is the production decision.
2. Same-binary phase PMU measurements identify mechanisms and stable debts.
3. Normal/reversed, operation-minimal and historical custom-TSC measurements
   are diagnostic.  They demonstrate delivery sensitivity but are not additive
   accounting for the final fixed ELF.

## Kernel-level picture

### Forward NTT

- Official Forward: about 452.801 TSC in the frozen kernel comparison.
- selected N5/TILE4 Forward: about 383.430 TSC.
- local advantage: about 69.4 TSC, or 15.3%, per Forward.
- In the Encap caller, two GT Forwards save about 120 TSC and approximately
  190--244 region-scoped core cycles.

This is the strongest and most repeatable GT32 mechanism.  Identity-lazy,
fixed-factor reduction, radix-4 and terminal-only scheduling variants did not
produce another meaningful gain, so the local arithmetic DAG is frozen.

### BaseMul

- Official native arithmetic: about 265.972 TSC.
- GT B3 quartic arithmetic: about 265.380 TSC; effectively parity.
- Complete B3 with its layout/output work: about 397.302 TSC.
- The isolated representation tax is therefore about 131 TSC, not an
  arithmetic multiplication deficit.

Typed M-layout Encap makes the general B3 edge slightly faster than Official
(about 11 TSC; 29--49 core cycles in the corresponding phase).  However, the
synthetic `BM+inverse` chain remains roughly 16% slower than Official.  The
large Forward win only reduces the complete synthetic `2F+B+I` result to an
approximately 5--7 cycle GT advantage.

### Inverse

I1 and T9 are strong local kernels, but their full interface with B3 remains
more expensive than Official's native composite.  Radix-4, identity-lane
specialization, permutation-native repair, T10, SoA inverse, and BM-to-I1
fusion did not shorten the executable critical path enough.  Fewer retired
instructions often failed to become fewer cycles.

### Q24 GT-native codec

Q24 is a real success.  It fuses 12-bit serialization/deserialization with the
GT leaf mapping and TILE4/private-SoA deposit.  GT-unpack, recovered-r GT-pack,
lazy10788 GT-pack and the Encap high-range H1 pack removed large earlier
boundary debts.

Q24 is not free.  It contributes specialized code, masks/tables and load-side
work.  The raw linked-family upper bound is large, and the complete CleanGT ELF
has about 66,327 bytes of `.text` and 56,776 bytes of `.rodata`, versus 42,007
and 5,384 bytes for Official.  These figures explain why frontend/cache/code
placement effects can be comparable with gains measured in tens of cycles.

## Full-operation attribution

### Keypair: small formal win, no large headroom demonstrated

The final fixed image wins by 33.76 core cycles (0.157%).  P-J1 specialization
is the correct Keypair architecture: local BaseInv-to-BM and P-suffix gates
showed genuine reductions in Forward/consumer work.  The final margin is small
because later BaseInv/BM/pack/hash delivery returns much of that saving.

Earlier PMU runs also showed that GT Keypair can retire roughly 2.4--2.5K fewer
instructions and 0.4K fewer stores while issuing roughly 0.9K more loads.  That
is the characteristic GT trade: less arithmetic/control work, but more table,
layout and specialized-boundary delivery.

The J1-AoS/R1-U alternative was not competitive: native BaseInv alone was
roughly 540 cycles slower and the consumer region remained hundreds of cycles
slower.  M-unified Keypair reached parity but did not beat the specialized P
path robustly.  Thus P for Keypair and M for Encap/Decap is currently better
than a universal ABI.

A hybrid image using GT Keypair and Official Encap/Decap is directionally
attractive, but the 34-cycle margin is too small to infer from separate ELF
results.  It requires its own fixed hybrid-image serious benchmark.

### Encap: Forward win is consumed by boundary and caller delivery

Stable phase-level TSC evidence from the qualified H1 image was:

| Phase | GT - Official | Reading |
|---|---:|---|
| E1 decode/CBD/SOTP | about +12 TSC | small input/producer debt |
| E2 two Forwards | about -120 TSC | largest GT win |
| E3 general B3 | about -11 TSC | parity/small GT win |
| E4a add(m) | about 0 | parity |
| E4b serialize r-hat | +22 to +26 TSC | real high-range reduction debt |
| E4c ciphertext H1 pack | +21 to +26 TSC | residual boundary debt |
| E5 hash/glue | about +16 TSC | small caller debt in that image |

The fixed formal whole operation nevertheless loses 113.92 core cycles.  This
is not contradicted by the phase table: the table is from a different linked
image and is diagnostic, while the final fixed ELF is the production result.
Fresh cumulative-prefix PMU shows that CleanGT retires fewer instructions from
early in the caller, but ends with roughly 0.75--0.78K more loads and a
217--276-cycle final delivery transition.  Compact reusable GT boundaries work;
large source-first/fused bodies do not close at the caller boundary.

The follow-up in-process retired-load attribution closes this debt at exactly
763 loads in both placements: Decode +106, the two Forward calls +358, the two
Q24 serializers +191, and BaseMul/add +104. Hashes, CBD/SOTP, copies and clears
account for only four extra loads. The executed GT ASM kernels have no
stack-pointer memory references, so this is a source/constant/table/scratch
load profile, not register spilling.

The r-hat serializer cannot use a centered/sign-only shortcut: real producer
trials reached magnitude 12,884.  Its canonical reduction chain cannot simply
be removed.  Therefore no single remaining Encap debt is known to recover the
formal 114-cycle gap without a new mechanism.

### Decap: near parity, but C1/C2 remain intrinsically less efficient

The formal fixed image loses 28.24 core cycles (0.146%).  Earlier phase PMU
identified the stable structure:

| Phase | Normal / reversed core-cycle delta | Reading |
|---|---:|---|
| C1 Decode/GT-unpack | +51 / +49 | stable GT boundary loss |
| C2 first BM+inverse+crep | +57 / +66 | stable critical-path/composition loss |
| C3 Forward/sub/general-BM/recovered-r pack | -97 / -16 | GT win, magnitude placement-sensitive |
| C4 hash/SOTP/hash | +24 / -157 | runtime/placement-sensitive shared code |
| C5 reencryption/verify | -6 / +12 | parity |
| C6 select/cleanup | +30 / -17 | small and sensitive |

CleanGT can retire about 1.5K fewer instructions yet consume more core cycles.
Thus the issue is not instruction count alone: load pressure, dependency depth,
frontend delivery and lost overlap matter more than the static reduction.

Attempts to eliminate materialization confirmed this.  Q24-to-B3 streaming
removed about 6 KiB of traffic and at least 146 instructions, but its 13.7 KiB
fused symbol was about 64--66 TSC slower.  BM-to-I1 fusion, T10, dual-terminal
output, pack-and-verify and direct T9-to-N5 variants also failed.  Materialized
boundaries can improve reuse and give the out-of-order core a cleaner scheduling
window.  The SOTP sidecar is locally qualified at about -46 TSC but its full
integration is not delivery-stable, so it remains dormant.

## Why Official remains difficult to beat

Official is not merely a collection of individually fast kernels.  It has a
compact end-to-end representation in which NTT, BaseMul, inverse and pack
already connect with little layout debt.  GT32 changes the cost distribution:

1. Good--Thomas/TILE4 makes Forward substantially cheaper.
2. Quartic BaseMul arithmetic reaches parity, but its preferred plane layout
   and inverse consumer create routing/output cost.
3. Typed P/M/Q24 contracts recover much of that cost, but require more symbols,
   constants, tables and loads.
4. Saved instructions are often off the critical path or overlap in Official;
   added shuffles, loads and dependent reductions are more cycle-visible.
5. Aggressive fusion reduces byte traffic but often creates a larger symbol,
   longer dependency graph and worse frontend scheduling.
6. Hash/RNG/KEM control code is shared and limits the fraction of an operation
   that polynomial optimization can improve.

The prior Decap accounting put the polynomial/layout slice near 2,731 TSC, or
about 22.7% of a roughly 12K-TSC caller.  A 10% full-Decap target would require
about a 44% reduction of that entire slice if hash/protocol work stays frozen.
The demonstrated local margins are far smaller, so a 10% whole-KEM advantage
is not realistic within the current decomposition and AVX2 contracts.

## Closed design spaces

- New quartic BaseMul formulas, Karatsuba/pair layouts and multi-accumulator
  variants: operand formation, range checkpoints, routing and registers consume
  the multiplication-count saving.
- Forward/inverse radix-4 and identity specialization: shuffle/repair cost is
  greater than the removed multiplication work.
- Barrett/Plantard fixed-factor replacement: no shorter AVX2 multiply DAG than
  the current Montgomery primitive.
- Universal P/M/SoA ABI: exhaustive searches found that specialization is
  cheaper than forcing all callers through one representation.
- T16-to-T32 overlap: the minimum live set is at least 17 YMM registers; AVX2
  has 16.
- Pure materialization removal and mega-fusion: repeatedly loses executable
  scheduling quality and code reuse.
- Scale/twisting relocation without deleting a complete reduction chain:
  moves work rather than removes it.

N5/B3/I1 local arithmetic should reopen only if a complete multiply,
reduction, shuffle or materialization chain disappears; the output/range
contract changes; the transform decomposition changes; or the target ISA/CPU
changes.

### Encap load-quality closure

Fresh region-scoped PMU closes the apparent `+763 retired loads` debt.  The
loads are warm-L1, with effectively zero L1/L2 misses and no material
store-forward, address-alias, or store-buffer blocking.  Two bounded probes
then tested the largest apparently removable groups:

- B3 finalizer + add(m) removes about 131 instructions, 49 loads and 49 stores,
  but its direct core-cycle result changes sign across placement/event runs.
- Register-resident Q24 pair/pack constants remove exactly 94 retired loads per
  serializer, yet serialize-r-hat becomes about 3.6--4.2 core cycles slower and
  ciphertext serialization is about 0.4 cycle slower.

Thus memory-source AVX2 operands and warm-L1 materialization cannot be valued
at one cycle per retired load.  Neither probe is production-eligible.  Full
details are in `results/tile4-encap-load-followup-20260813.md`.

## Practical choices

1. Keep Official Main as the default complete backend.
2. Preserve CleanGT as an opt-in research backend and regression oracle.
3. If production wants one final bounded experiment, build a fixed hybrid ELF
   with GT Keypair and Official Encap/Decap, then repeat the same 64-launch
   SUPERcop serious method.  Do not infer the result by combining separate
   binaries.
4. Do not pursue additional 2--20-cycle local variants.  A new GT32 direction
   should have a mechanism capable of recovering at least hundreds of caller
   cycles: a changed decomposition, a genuinely consumer-native producer that
   deletes an entire arithmetic layer, or a wider ISA/register domain.
5. Revalidate on each target microarchitecture.  The current conclusion is
   specific to this AVX2 CPU and its frontend/load/port behavior.

## Bottom line

CleanGT is not a failed arithmetic design.  It proves that GT32 can make the
Forward NTT much faster and can integrate exact GT-native wire codecs.  But in
the complete KEM, Official's compact representation and delivery efficiency
consume nearly all of that gain.  The final measurable outcome is therefore
one tiny Keypair win and two tiny Encap/Decap losses, not a broadly faster
backend.

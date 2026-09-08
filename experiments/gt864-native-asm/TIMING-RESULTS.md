# GT864 native timing — 2026-09-08

Decision: keep-experimental, positive timing gate. Production was not edited.
This compares **current GT production**, not a new SUPERCOP Official run.

## Complete KEM

Pi5 Cortex-A76 CPU3, GCC 14.2.0, identical -O3 -march=armv8-a+simd policy.
Six independent paired processes, alternating AB/BA, 41 samples each.
Numbers are medians of six process medians, cycles/call. Every process first
checks valid/tampered and malformed ciphertext behavior and exact pk/sk/ct.

| Boundary | Production | Scheduled native | Change |
|---|---:|---:|---:|
| Keygen | 54149.500 | 52237.250 | -3.531% |
| Encaps | 46045.900 | 46065.500 | +0.043%, effectively neutral |
| Decaps | 44422.950 | 43573.775 | -1.912% |

Independent same-wrapper allocation-versus-scheduling pairs isolate Slothy:

| Boundary | Allocated, source order | Scheduled | Change |
|---|---:|---:|---:|
| Keygen | 52738.000 | 52224.375 | -513.625 cycles |
| Encaps | 46104.325 | 46098.350 | -5.975 cycles, neutral |
| Decaps | 43860.375 | 43594.175 | -266.200 cycles |

Do not subtract values from different paired experiments as exact attribution.
All six process deltas favor scheduled Keygen and Decaps. Dynamic instruction
and branch counts are identical between allocation and scheduling. Thus the
measured improvement is scheduling economics, not deleted work.

## Components

| Component | Production | Scheduled | Change |
|---|---:|---:|---:|
| BaseInv success | 8760.266 | 7796.594 | -11.00% |
| BaseInv failure | 6899.625 | 5173.000 | -25.02% |
| BaseMul (scale-specific) | 2156.797 | 1750.828 | -18.82% |
| Inverse (scale-specific) | 7660.000 | 7226.985 | -5.65% |
| **BaseMul → Inverse** | **9798.906** | **8970.828** | **-8.45%** |

BaseMul/Inverse individual rows use different R0/R^-1 boundary contracts;
only their combined row is representation-equivalent end to end. BaseInv
success uses cubic leaves (1,0,0), failure all-zero: useful repeatable synthetic
boundaries, not an average over the KEM retry distribution. Complete KEM above
is the actual caller result. Component tests include public save/restore and
new scratch wipe costs. Production and native erasure policies differ; the
allocation/scheduling comparison preserves the identical new policy.

Pure scheduling saves approximately 255 cycles for BaseInv success, 107 for
BaseMul, 169 for Inverse, and 269 for their combined boundary. In the production
comparison, combined dynamic instructions increase 12898 → 13685 while cycles
drop: instruction count alone would misrank this candidate.

## Correctness and object evidence

- Allocated and scheduled cores pass native Mac AND Pi5 tests: BaseInv 808
  cases, all 288 injected zero leaves, 256 Inverse inputs, 256 BaseMul chains,
  independent cubic identities, range, exact alias, canaries, AAPCS, scratch wipe.
- Fresh production build passes 64 KEM round trips and tamper rejection.
- All three library comparisons pass 32 valid/tampered and 32 malformed cases;
  pk/sk/ct differences are zero. No official KAT regeneration this round.
- Ten scheduled cores assemble for ELF, no core stack accesses/spills/hidden
  calls. Instruction counts match allocation. Wrappers deliberately use stack.
- Shared-library text sizes: prod 102112 bytes, alloc/opt 116677 bytes. Candidate
  libraries retain exported old routines plus new routines; this is not the
  isolated hot-path I-cache footprint. Scheduling does not increase size.
- Local Slothy entry /Users/chenpinhao/slothy, existing venv at
  /Users/chenpinhao/slothy_and_ra/.venv/bin/python, cortex_a76. Fixed allocation,
  small timing windows, allow_spills=false, allow_renaming=false.
- Optional Unicorn/LLVM execution selftest unavailable; native tests substitute
  for execution checking. Final Slothy selfchecks pass.
- Generic parse-slothy-log reports fail on intermediate INFEASIBLE attempts and
  reports the minimum *window* cycle as if complete. Do not use that summary as
  whole-kernel latency. The final outputs/selfchecks and Pi5 evidence are primary.
- Whole-region post-window estimation internally clears timeout; future driver
  runs disable that optional estimate. This completed run retained the estimates.

Governor was ondemand, sampled frequency before/after 2.4GHz, temperature
61.15 →61.70 C. Governor was not changed, and frequency was not continuously
logged; paired PMU cycles and consistent six-process deltas support this result.

## Reproduction and files

Remote isolated workspace:
`/home/pi/ntruplus-experiments/gt864-native-timing-20260908.X8u5QV`

`pi-build.py` creates fresh production and both candidate libraries;
`pi-run.py` performs correctness and paired measurement. `summarize-timing.py`
reports medians and per-process deltas. No remote old object was linked.

`timing-results.json`: cycles/instructions/branches, IPC, per-process deltas.
`timing-environment.json`: host/compiler, binary SHA256, sampled conditions.
`candidate.opt.S` in each region: scheduled assembly; `slothy-timing.log`: solver.
Raw logs are in gitignored `build/pi-evidence/`, with a copy on the Pi.

ToBytes was excluded: its new routing still needs native execution and a
separate performance gate. No production promotion or commit was performed.

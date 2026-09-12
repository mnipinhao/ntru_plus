# P19 results — P18 ToBytes production promotion

## Decision

P19 passes every promotion gate.  Production now links the exact P18 Full and
Small ToBytes instruction artifacts through `gt864_p18_tobytes_full_asm` and
`gt864_p18_tobytes_small_asm`.  `gt864_tobytes.c` keeps the established
KEM-facing FR0 entries and calls those functions directly.  The legacy P9
public wrapper objects are no longer linked.

## Source and linkage

- Pre-promotion baseline revision:
  `34d62285580cbd36e907cf0a593f8a57432f0310`.
- Full assembly SHA-256:
  `634fe9ee2e982405e86d87980703080dae0c51821d7b79e16905676eb128d83e`.
- Small assembly SHA-256:
  `f32af0ec4e173481018856d62a24999fb59818f4d2d1b26a9b4fa541443c1254`.
- The candidate library and `gt864_tobytes.o` expose/reference both P18
  functions and contain neither P9 public wrapper symbol.
- Target objects contain 1,204/1,096 instructions for Full/Small and no Q
  register stack access.

The P18 source omits optional ELF `.type/.size` metadata, so the direct ABI
test linker emits a warning.  Symbol resolution, execution and every gate pass;
adding metadata is retained as packaging-only cleanup and must not be mixed
with a new performance claim.

## Correctness and memory/ABI gates

- Production manifest: pass.
- Local and Pi 5 exact oracle: 513 Full + 513 Small cases and guarded edges.
- Package test: 64 valid/tampered KEM cases per baseline/candidate.
- KAT SHA-256:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Malformed transcript SHA-256:
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
- Test-only assembly probe confirms `d8-d15` preservation, zeroed volatile
  SIMD state and zero high halves for `v8-v15`.
- Input remains immutable and 16-byte output canaries around the exact
  1,296-byte destination survive.

Input/output overlap is not part of the production ToBytes ABI.  P19 therefore
tests the actual disjoint-buffer contract rather than claiming in-place alias
support.

## Same-boundary Pi 5 PMU

| Mode | P16 production | P19 production | Delta cycles | Delta instructions |
| --- | ---: | ---: | ---: | ---: |
| Full | 1441.016 | 1409.695 | -31.321 | -461 |
| Small | 1175.555 | 1031.516 | -144.039 | -479 |

## Full-KEM Pi 5 PMU

| Operation | P16 production | P19 production | Paired delta | Delta instructions | Observations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Keygen | 43596.875 | 43275.375 | -331.875 | -1419 | 252 |
| Encaps | 45276.675 | 45069.825 | -209.425 | -940 | 252 |
| Decaps | 40313.975 | 40125.875 | -194.550 | -940 | 252 |

Measurements use Cortex-A76 CPU 3, GCC 14.2, balanced process order and the
isolated directory
`/home/pi/supercop-20260831/bench/pinhao/gt864-p19-20260912`.  The Pi reports
`throttled=0x0` before and after boundary and full-KEM measurements.

## Maintained queue

1. P20: refresh the complete GT versus selected SUPERCOP 20260831 profiler.
2. Select the next optimization from the fresh positive cycle gaps.
3. Separately add ELF function metadata; it is not an arithmetic or timing
   experiment.

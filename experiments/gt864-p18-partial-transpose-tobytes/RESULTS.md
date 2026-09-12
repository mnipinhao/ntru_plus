# P18 results — class-local partial-transpose ToBytes

## Outcome

P18 passes its exact-map, local correctness, static instruction, Slothy,
Pi 5 same-boundary, and full-KEM gates.  It is a promotion candidate but has
not changed production.

## What changed

For each top half, the 54 wire-order outputs are grouped into fifteen
eight-source neighborhoods.  After two or four fixed cyclic source rotations,
each wanted vector is a selected column of an 8x8 matrix.  P18 constructs only
the required 2, 4, or 6 columns using `EXT`, `TRN1`, and `TRN2`, then immediately
normalizes, packs, and stores the result.  It never builds nine complete routed
rows, uses no coefficient scratch, and retains only the existing per-output
packing `TBL`.

## Correctness and ABI

- Exact composed coordinate map SHA-256:
  `087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270`.
- Local exact-byte oracle: 513 full cases, 513 small cases, two guarded-edge
  cases; final Slothy output reassembled and rechecked.
- Public wrapper: preserves `d8-d15`, processes both top halves, erases all
  `v0-v31`, restores the frame, and returns without coefficient scratch.
- Pi 5: both 64-case package KEM tests, KAT SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`,
  513-case boundary oracle/canaries, and malformed transcript SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`
  pass.
- Target objects contain no vector stack access (spill).

## Static and Slothy evidence

| Mode | Production dynamic instructions | P18 | Delta | Slothy model cycles |
| --- | ---: | ---: | ---: | ---: |
| full | 2809 | 2348 | -461 | 992 |
| small | 2607 | 2128 | -479 | 712 |

Slothy used `/Users/chenpinhao/slothy`, the Cortex-A76 target, fifteen
class-local scheduling windows per mode, fixed physical registers, renaming
disabled, and spills disabled.  The instruction multiset is preserved.  Since
the parser does not accept `STUR D/W`, scheduling uses same-address and
same-width `STR D/W` surrogates; the emitted assembly restores the real `STUR`
before AArch64 assembly and correctness testing.

## Raspberry Pi 5 same-boundary PMU

| Mode | Production cycles | P18 cycles | Cycle delta | Instruction delta | Read delta | Write delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| full | 1441.008 | 1409.641 | -31.368 | -461 | +10.000 | -7.993 |
| small | 1173.750 | 1024.633 | -149.117 | -479 | +10.000 | -7.969 |

The full path is still shuffle-throughput limited: removing 461 dynamic
instructions produces only 31.368 cycles.  The small path converts the new DAG
into a substantially larger cycle win.

## Frozen full-KEM integration

| Operation | Production cycles | P18 cycles | Paired delta | Instruction delta | Observations |
| --- | ---: | ---: | ---: | ---: | ---: |
| Keygen | 43601.250 | 43267.750 | -334.125 | -1419 | 252 |
| Encaps | 45273.025 | 45065.850 | -194.400 | -940 | 252 |
| Decaps | 40313.425 | 40129.375 | -182.825 | -940 | 252 |

The exact instruction deltas identify the KEM call sites without guesswork:
Keygen executes one full and two small ToBytes calls, while Encaps and Decaps
each execute one full and one small call.

Measurements ran on Cortex-A76 CPU 3 under the `ondemand` governor in
`/home/pi/supercop-20260831/bench/pinhao/gt864-p18-20260912`.  The Pi reported
`throttled=0x0` before and after.

## Decision and maintained queue

P18 passes the promotion gate.  Production remains unchanged until P19.

1. P19: promote both kernels, rebuild from the committed production tree, and
   repeat KAT, malformed/rejection, alias/cleanup, object, and paired KEM gates.
2. Refresh GT versus selected SUPERCOP component profiling after promotion.
3. Only then choose the next bottleneck.  If ToBytes is reopened, focus on the
   full-mode shuffle critical path rather than further instruction count alone.

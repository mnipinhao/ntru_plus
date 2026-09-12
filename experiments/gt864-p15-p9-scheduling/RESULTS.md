# P15 result — P9 scheduling is full-only beneficial

P15 preserved the production P9 ToBytes DAG, physical register assignment,
instruction multiset and memory boundary.  Slothy reordered bounded output
completion, normalization and pack windows for Cortex-A76.  The predeclared
promotion rule required both full and small public boundaries to improve.

## Static and correctness gates

- Slothy root: `/Users/chenpinhao/slothy`.
- Full: 9 windows and 1,224 scheduled instructions.
- Small: 8 windows and 1,136 scheduled instructions.
- Register renaming and spill insertion were disabled.
- Every window preserves its exact instruction multiset and every physical
  destination is an explicit live-out.
- The existing three D-register ABI restore operations in the scheduled tail
  remain exactly preserved; no coefficient-Q stack access exists.
- Target objects retain 1,378 instructions/top for full and 1,277/top for
  small, exactly matching GCC 14.2 P9.
- Both target packages pass 64-case KEM tests and the exact KAT.
- Full and small each pass 513 differential vectors including edge inputs and
  output canaries.

## Pi 5 same-boundary PMU

All values are medians over two reversed-order runs, 37 paired samples per
run, pinned to Cortex-A76 CPU 3.  Neither run throttled.

| Mode | P9 cycles | P15 cycles | Delta | Instructions delta | Branch delta | Read delta |
|---|---:|---:|---:|---:|---:|---:|
| full | 1518.188 | 1441.633 | -76.555 | 0 | 0 | 0 |
| small | 1174.282 | 1175.868 | +1.586 | 0 | 0 | 0 |

The full result demonstrates a real scheduling gain with identical work.  The
small result is effectively neutral but fails the strict negative-cycle gate.

## Decision

Reject combined P15 and leave production unchanged.  Full-KEM integration was
intentionally skipped because one required mode failed its same-boundary
falsifier.

Do not discard the full schedule.  The next independent gate is P16: replace
only full ToBytes with the P15 schedule, retain production P9 small unchanged,
and run complete KEM correctness plus paired Keygen/Encaps/Decaps.  This keeps
the original P15 decision honest while testing the independently useful result.

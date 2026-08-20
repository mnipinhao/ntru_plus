# Checkpoint C4: nine-row persistent pair pipeline

C4 extends the selected C3 representation across all nine GT rows and two
terminal coefficients. It stores final persistent `S/D` rows directly; there
is no coefficient-major reconstruction and no intermediate YMM materialization.

## Implementations

- `from_z_sequential`: consumes two skewed-Z coefficient arrays and finishes
  one row before starting the next.
- `from_z_pipelined`: carries previous-high in `ymm15` and advances two rows
  together across stages 4/2/1 to expose independent Montgomery chains.
- `with_shear`: builds nine pair-packed low halves with the 27-blend shear,
  then produces each paired high half as a rolling value and consumes it
  immediately. No 288-byte skew array exists.

Persistent output is `state[row][S_or_D][lane]`; lanes 0..7 belong to terminal
coefficient 0 and lanes 8..15 to coefficient 1. This layout is intended to be
consumed directly by NTT9.

## Liveness contract

| Phase | Long-lived data | Temporary budget | Designed peak YMM |
| --- | --- | --- | ---: |
| from-Z sequential | previous high + one S/D row | A/B + two Montgomery temps | 11 |
| from-Z two-row pipeline | previous high + two S/D rows | shared A/B + temps | 13 |
| natural paired-low shear | nine paired-low rows | one shear temporary | 10 |
| natural rolling row | remaining paired-low rows + active S/D | high producer + four arithmetic temps | 15 |

All audited functions have no calls, frame, stack references, spills, or
`vzeroupper`. Each complete pair uses 36 vector Montgomery chains.

## Result

Nine pinned launches, 201 samples each, Intel Core Ultra 7 155H CPU 1, GCC
15.2 `-O3 -mavx2`:

| Nine-row two-terminal kernel | Median cycles |
| --- | ---: |
| C0 natural-input two islands | 179.941 |
| C4 from-Z sequential | 97.730 |
| C4 from-Z two-row pipeline | 95.277 |
| C4 natural input, zero materialization | 147.811 |

The two-row schedule improves from-Z by 2.5%. Natural C4 is 17.9% faster than
C0 pair while halving Montgomery chains from 72 to 36. It retains a meaningful
part of C3's row-level benefit and passes the gate to reopen NTT9 work.

The remaining tax is explicit: natural C4 performs 162 input loads because the
high-half rolling producer gathers eight source rows for each coefficient and
GT row. It still wins, but this producer—not persistent NTT16 arithmetic—is the
next local optimization target.

Checkpoint D is reopened under a new boundary: vector NTT9 must consume the
persistent `S/D` layout directly. Reconstructing terminal-major rows first
would invalidate the C3/C4 result. Evidence:
`results/c4-intel155h-20260820-001/c4-diagnostic.json`. Repository-local only;
not SUPERCOP promotion evidence.

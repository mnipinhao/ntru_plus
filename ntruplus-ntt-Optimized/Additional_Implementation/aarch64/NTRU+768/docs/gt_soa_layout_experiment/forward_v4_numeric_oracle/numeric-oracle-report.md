# Gate 14 Forward v4 Numeric Oracle

Status: `complete_numeric_oracle_no_asm_candidate`

This gate parses the actual NTRU+768 Forward NTT32 table and checks
whether the Gate 13 full-absorption candidate has a numeric equivalent
under row/plane relabeling or per-lane twiddle scaling without final
lane mixing.  It does not generate `.S`, `.opt.s`, Slothy input, or
benchmark binaries.

## Source Facts

- `NTRUPLUS_N`: `768`
- `NTRUPLUS_Q`: `3457`
- `gt96_omega32_powers` entries: `32`
- matrix verification: `pass` over `11` cases

## Numeric Equivalence Check

- distinct proportional NTT32 row pairs: `0`
- all rowpack blocks have lane-preserving match: `False`

| block | target k32 rows | lane-preserving match |
| ---: | --- | --- |
| 0 | `[0, 1, 2, 3, 4, 5, 6, 7]` | `False` |
| 1 | `[8, 9, 10, 11, 12, 13, 14, 15]` | `False` |
| 2 | `[16, 17, 18, 19, 20, 21, 22, 23]` | `False` |
| 3 | `[24, 25, 26, 27, 28, 29, 30, 31]` | `False` |

## Decision

Each rowpack target vector contains eight distinct NTT32 output matrix rows for one branch/lane plane.  Under a lane-preserving no-transpose model, a plain vector store can only expose one NTT32 output row across lanes, even with per-lane diagonal scaling. The actual NTT32 rows from the current table are not proportional within any rowpack k32 block, so no numeric equivalence was found.

Forward v4 ASM remains blocked.  Continuing this direction now
requires a broader mathematical decomposition, not another layout
or scheduling attempt.

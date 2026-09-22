# P107 — the inverse tail normalises six values a vector, not three

P106 localised P29's remaining Cortex-A76 cost to the tail: +180 cycles over the
old one, all of it the ternary reduction it performs itself.  `generate.py`
showed why.

## Three of eight lanes

The generator called a six-instruction `normalization()` once per `(t, side)`:

```python
for t, state in enumerate(p28.REGS):          # 16
    for side in ("low", "high"):              # 2
        ...
        normalization(lines, value, f"tail_{t}_{side}")
```

**32 calls, 192 instructions, for 96 values.**  `j = 8` gives one `(t, side)`
only its three components, so each vector was three-eighths full.

| | instructions per value |
|---|---:|
| `crepmod3` | **0.75** (6 per 8) |
| P29's tail | **2.00** (6 per 3) |

## One MOV

The three values sit in lanes 0..2 and leave through `umov x9, V.d[0]`, so the
high side's three fit in lanes 4..6 with a single `mov V<low>.d[1],
V<high>.d[0]`, and one normalisation then covers six.  The store path does not
change at all: `.d[0]` for the low side, `.d[1]` for the high.

| | P29 | P107 |
|---|---:|---:|
| symbolic instructions | 849 | **737** |
| allocated instructions | 850 | **738** |
| normalisation `CMGT` | 64 | **32** |
| `SQRDMULH` / `MLS` | 88 / 88 | **72 / 72** |

Regenerated from the symbolic source and re-scheduled by Slothy in **sixteen**
windows rather than thirty-two, one per `t` (56 seconds).  No spills, no
symbolic registers left.

## Measured

| | A76 | M2 |
|---|---:|---:|
| P29 tail | 502 cyc | 139 cyc |
| **P107 tail** | **430** | **119** |

Byte-identical over 5,000 random inputs across all 1,024 halfwords, with exactly
96 positions written, verified on both machines.

Decapsulation: **A76 14,242 -> 14,211 ns, M2 4,048 -> 4,041.**  Both machines,
so it lands under rule 1, not the amended rule 2.  `49a229be`.

## Where the inverse stands

| 864 decapsulation | pre-P29 | P29 | + route (P106) | + tail (P107) |
|---|---:|---:|---:|---:|
| M2 Pro | 4,093 | 4,055 | 4,045 | **4,041 (-1.27%)** |
| Cortex-A76 | 14,149 | 14,266 | 14,248 | **14,211 (+0.44%)** |

P29's A76 cost is down from +117 ns to +62, and its M2 gain up from -38 to -52.
Per component on A76: paired main **-34**, route **+95** (was +148), tail
**+108** (was +180).

The tail's remaining +108 is no longer normalisation density -- at 738
instructions against the old tail's 592 for the same 96 values, what is left is
that the old tail did not normalise at all, and the route's remaining +95 is the
`ST3` premium A76 charges over plain stores (80 cycles measured).

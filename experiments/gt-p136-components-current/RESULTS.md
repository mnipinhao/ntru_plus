# P136: GT against SUPERCOP's Official, component by component, on the current trees

`comp_ke.c` (P128's key generation / encapsulation components) and
`comp_dec.c` (P127's decapsulation components, generalised to 1152), built
from each tree's Makefile (`build.sh`), against SUPERCOP 20260831's Official
with its symbols renamed `o_*`.  Weights are kem.c's calls per operation
(1152's f/g steps x the measured retry rate).  `m2_run1.txt`, `m2_run2.txt`,
`a76_run1.txt`.

**P128's tool was wrong for two rows.**  It timed Official's in-place
`poly_ntt` and `poly_triple` after a `memcpy` of the input, charging Official
a copy its kem.c does not make: key generation and encapsulation call both
in place; the only copy is decapsulation's `f = m;` before one of its two
transforms.  The rows now follow kem.c (the decapsulation pair carries the one
copy).  With that, M2's in-place forward NTT is GT +12-13 ns a call, as P100
and P105 measured directly.

| GT - Official, arithmetic | keygen | encaps | decaps |
|---|---:|---:|---:|
| 864, M2 (ns) | -39 | -39 | -40 |
| 864, A76 (cycles) | -2,806 | -2,255 | -2,506 |
| 1152, M2 (ns) | -113 | -8.5 | -25 |
| 1152, A76 (cycles) | -2,804 | -1,536 | -2,502 |

(P128 had 864 M2 -94 / -60 and 1152 M2 -179 / -64 for keygen / encaps.)

Deficits left at the time: 1152 `frombytes` (+15 ns / +124 cycles a call,
x3 in decapsulation -- landed as P137), 864's inverse -> ternary (+52 ns on
M2, structural, P127), the M2 forward NTT (+12-13 ns a call, no lever,
P100/P105), 1152's first product (+14 ns / +142 cycles, P126's transpose),
1152 baseinv on the A76 (+86 cycles a call, P128's rule-2 trade).  GT leads
in basemul on both machines and in the serializers, most on the A76.

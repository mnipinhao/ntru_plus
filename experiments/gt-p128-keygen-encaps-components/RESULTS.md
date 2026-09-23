# P128 — key generation and encapsulation, component by component; 1152 baseinv's fqmul

Option B after P127: look beyond decapsulation.  `comp2.c` times every
arithmetic component of key generation and encapsulation, GT against
Official (SUPERCOP 20260831, symbols renamed o_*, Official's `poly.c` compiled
with `rename.h`), weighted by calls per operation.  1152's f/g steps are
weighted by the measured retry rate (1.42 / 1.38 attempts, P124).
Serializers follow `kem.c`: key generation writes f in full and pk, hinv with
`tobytes_small`; encapsulation writes ct with `tobytes_small`.

## Result: GT is ahead almost everywhere

| | M2 keygen | M2 encaps | A76 keygen | A76 encaps |
|---|---:|---:|---:|---:|
| 864 arithmetic, GT - Official | -94 ns | -60 ns | -2,783 cyc | -2,172 cyc |
| 1152 arithmetic, GT - Official | -179 ns | -64 ns | -3,476 cyc | -1,778 cyc |

Deficits left: **1152 baseinv on M2** (+20 ns a call, +57 ns a key
generation; A76 level), 1152 `frombytes` (+19 ns M2 / +128 A76, closed as
structural in the roadmap: the unpack transpose), and 864 `cbd1`/`frombytes`
(+3 ns each).

## 1152 baseinv

The two Slothy kernels (numerator, finish) help on M2 as well: the C
fallbacks are +23 and +44 ns.  The gap is the C middle -- prefix products, one
inversion, recovery -- three serial chains of ~40 dependent `fqmul`, so
latency-bound.  Official's `fqmul` takes the Montgomery quotient from
`mul.8h(x, y)`; GT's took it from `uzp1` of the widened product, one more
permute on every step's critical path.  Switching:

| | M2 baseinv | A76 baseinv | M2 keygen | A76 keygen |
|---|---:|---:|---:|---:|
| before | 550 ns | 5,298 cyc | 6,236 ns | 54,358 cyc |
| after | **517 ns** | 5,342 cyc | **6,146 ns (-1.44%)** | 54,556 cyc (+0.36%) |
| Official | 532 ns | 5,280 cyc | | |

Keygen means over six interleaved M2 rounds and three A76 rounds, both builds
same session.  Lands under rule 2.  KAT, M2 + Linux `make check`, TIMECOP
(`-O`..`-Os`) pass.  864's batch-inversion kernels already use the `mul`
quotient (21 fqmul, 43 `mul` in `baseinv_inverse.S`).

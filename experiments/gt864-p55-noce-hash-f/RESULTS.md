# P55 results

P55 passed every release and performance gate on `pi@100.99.191.9` under
`/home/pi/supercop-20260831`:

- 4096 random `hash_f` differential cases and 4096 exact input/output alias
  cases.
- Baseline and candidate package KEM, ABI, canonical-rejection and runtime
  zeroization tests.
- Unchanged KAT response SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Unchanged malformed-ciphertext transcript SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
- No `EOR3`, `RAX1`, `XAR`, or `BCAX`; the new 393-instruction function has
  18 live-state zero moves and nine stack-wipe pairs.
- The P53 `hash_g` section is byte-identical between baseline and candidate.
- Two measurement orders completed with `throttled=0x0`.

| boundary | baseline cycles | P55 cycles | paired delta | instruction delta | branch delta |
|---|---:|---:|---:|---:|---:|
| hash_f | 13277.969 | 9176.250 | -4102.938 | -16056 | -19 |
| Keygen | 43193.500 | 39082.875 | -4117.000 | -16058 | -19.5 |
| Encaps | 40707.850 | 36612.875 | -4095.400 | -16056 | -19 |
| Decaps control | 35416.800 | 35417.675 | +2.575 | 0 | 0 |

The fixed hash accounts for essentially the complete Keygen and Encaps
improvement. Decaps retires exactly the same instructions and branches; its
2.575-cycle movement is noise. P55 is therefore promoted for the NO_CE
production build.

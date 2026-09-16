# P53 results

All gates passed on `pi@100.99.191.9` under
`/home/pi/supercop-20260831`:

- 4096 random differential and exact input/output alias cases.
- Two 64-case KEM tests and unchanged KAT SHA-256
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Unchanged malformed-ciphertext transcript SHA-256
  `2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67`.
- No `EOR3`, `RAX1`, `XAR`, or `BCAX`; nine stack-wipe pairs and complete
  live-state retirement are present in the linked object.
- No Pi throttling.

| boundary | baseline cycles | P53 cycles | paired delta | instruction delta |
|---|---:|---:|---:|---:|
| hash_g | 14455.360 | 10096.532 | -4358.235 | -17379 |
| Encaps | 44884.500 | 40630.500 | -4252.225 | -17194 |
| Decaps | 39757.500 | 35438.850 | -4312.950 | -17379 |
| Keygen control | 43086.625 | 43099.875 | +7.750 | 0 |

The Keygen control changes no retired instruction or branch and its small
cycle movement is treated as noise. P53 is promoted for the NO_CE production
build. A future Armv8.4 SHA3 backend remains a separate feature-policy gate.

# P108 — the nine numbers, both machines, rebuilt in one session

Official is SUPERCOP's `crypto_kem/ntruplus{768,864,1152}/aarch64`, fetched from
the Pi 5.  Every binary in a table built in the same session with the same
compiler, each GT tree carrying **its own Makefile `CFLAGS`** (768
`-O3 -fomit-frame-pointer`, 864 `-O3`, 1152 `-O3 -std=c11 -D_DEFAULT_SOURCE`
plus its three `-DNTRUPLUS1152_ASM_*`, which select the assembly baseinv and
basemul_rinv -- omitting them silently benchmarks the C fallbacks).  RNG
reseeded before every timed batch; min of 401 x 300 under the clock gate;
median of three sessions.  All three sets pass their full gate suite at these
revisions.

## Cortex-A76, Raspberry Pi 5, no FEAT_SHA3 on either side

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 768 | Official | 16,025 | 16,068 | 13,942 |
| | **GT** | **13,135** | **12,263** | **11,551** |
| | | **-18.0%** | **-23.7%** | **-17.1%** |
| 864 | Official | 18,391 | 19,189 | 16,943 |
| | **GT** | **15,200** | **14,802** | **14,208** |
| | | **-17.4%** | **-22.9%** | **-16.1%** |
| 1152 | Official | 28,106 | 24,577 | 21,820 |
| | **GT** | **23,990** | **19,344** | **18,129** |
| | | **-14.6%** | **-21.3%** | **-16.9%** |

## M2 Pro, against Official + CryptoExtension

The strict baseline: the submission ships no SHA3 path, but upstream does, so
crediting GT with a Keccak backend Official could have is not a result.  The
measurement copy of `CE/f1600.S` carries the AAPCS64 save/restore upstream omits.

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 768 | Official + CE | 4,159 | 4,751 | 3,702 |
| | **GT** | **3,795** | **4,081** | **3,138** |
| | | **-8.8%** | **-14.1%** | **-15.2%** |
| 864 | Official + CE | 4,545 | 5,254 | 4,146 |
| | **GT** | **4,147** | **4,682** | **3,866** |
| | | **-8.8%** | **-10.9%** | **-6.8%** |
| 1152 | Official + CE | 7,115 | 6,952 | 5,487 |
| | **GT** | **6,519** | **6,130** | **4,986** |
| | | **-8.4%** | **-11.8%** | **-9.1%** |

## M2 Pro, against Official exactly as SUPERCOP has it

Portable Keccak, which is what the submission contains:

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 768 | Official | 4,479 | 5,152 | 3,863 |
| | **GT** | **3,795** | **4,081** | **3,138** |
| | | **-15.3%** | **-20.8%** | **-18.8%** |
| 864 | Official | 4,909 | 5,987 | 4,598 |
| | **GT** | **4,147** | **4,682** | **3,866** |
| | | **-15.5%** | **-21.8%** | **-15.9%** |
| 1152 | Official | 7,675 | 7,839 | 6,023 |
| | **GT** | **6,519** | **6,130** | **4,986** |
| | | **-15.1%** | **-21.8%** | **-17.2%** |

The gap between the last two tables is the Keccak backend.  Both are true;
which to quote depends on whether the comparison is to the submission or to
what the submission could be.

## What moved since the first run of this table

`gt-p110-keccak-swap` gave 864 and 1152 the permutation 768 already had, which
roughly doubled all six of their M2 margins; the three inverse landings
(`ed4d870c`, `b9a3c7f5`, `49a229be`) and 1152's compare swap (`ecb6d5e1`)
account for the rest.  Cortex-A76 is unchanged throughout: it has no FEAT_SHA3,
and the store-path work is neutral to slightly negative there by construction
of the amended promotion rule.


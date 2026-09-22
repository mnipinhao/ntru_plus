# P108 — the nine numbers, both machines, rebuilt in one session

Official is SUPERCOP's `crypto_kem/ntruplus{768,864,1152}/aarch64`, fetched
from the Pi 5.  Every binary in a table was built in the same session with the
same compiler, each GT tree carrying **its own Makefile `CFLAGS`** (768
`-O3 -fomit-frame-pointer`, 864 `-O3`, 1152 `-O3 -std=c11 -D_DEFAULT_SOURCE`
plus its three `-DNTRUPLUS1152_ASM_*`, which select the assembly baseinv and
basemul_rinv -- omitting them silently benchmarks the C fallbacks).  The
harness reseeds the RNG before every timed batch, carries a clock witness and
gates on it; min of 401 batches of 300.

## Cortex-A76, Raspberry Pi 5, no FEAT_SHA3 on either side

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 768 | Official | 16,025 | 16,066 | 13,950 |
| | **GT** | **13,149** | **12,260** | **11,554** |
| | | **-17.9%** | **-23.7%** | **-17.2%** |
| 864 | Official | 18,384 | 19,191 | 16,926 |
| | **GT** | **15,205** | **14,811** | **14,201** |
| | | **-17.3%** | **-22.8%** | **-16.1%** |
| 1152 | Official | 28,100 | 24,578 | 21,813 |
| | **GT** | **23,990** | **19,339** | **18,128** |
| | | **-14.6%** | **-21.3%** | **-16.9%** |

## M2 Pro, against Official + CryptoExtension

The honest baseline here: the submission ships no SHA3 path, but upstream does,
so crediting GT with a Keccak backend Official could have is not a result.  The
measurement copy of `CE/f1600.S` carries the AAPCS64 save/restore upstream omits;
without it the timer's own accumulators come back corrupted.

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 768 | Official + CE | 4,156 | 4,754 | 3,703 |
| | **GT** | **3,789** | **4,079** | **3,138** |
| | | **-8.8%** | **-14.2%** | **-15.3%** |
| 864 | Official + CE | 4,547 | 5,253 | 4,150 |
| | **GT** | **4,340** | **4,981** | **4,045** |
| | | **-4.6%** | **-5.2%** | **-2.5%** |
| 1152 | Official + CE | 7,114 | 6,954 | 5,489 |
| | **GT** | **6,797** | **6,535** | **5,230** |
| | | **-4.5%** | **-6.0%** | **-4.7%** |

## M2 Pro, against Official exactly as SUPERCOP has it

What the submission actually contains -- portable Keccak, no CE:

| set | | key generation | encapsulation | decapsulation |
|---|---|---:|---:|---:|
| 768 | Official | 4,482 | 5,153 | 3,864 |
| | **GT** | **3,789** | **4,079** | **3,138** |
| | | **-15.5%** | **-20.8%** | **-18.8%** |
| 864 | Official | 4,908 | 5,987 | 4,600 |
| | **GT** | **4,340** | **4,981** | **4,045** |
| | | **-11.6%** | **-16.8%** | **-12.1%** |
| 1152 | Official | 7,679 | 7,839 | 6,027 |
| | **GT** | **6,797** | **6,535** | **5,230** |
| | | **-11.5%** | **-16.6%** | **-13.2%** |

The gap between the last two tables is the Keccak backend, and it is most of
what a naive M2 comparison would report: at 864 decapsulation, -12.1% against
the shipped Official and -2.5% against Official + CE.


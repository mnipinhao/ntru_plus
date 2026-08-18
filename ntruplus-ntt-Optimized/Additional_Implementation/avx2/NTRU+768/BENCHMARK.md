# Benchmark record

## Fresh formal comparison

The finalized `avx2-clean-typed-v1` directory was compiled alongside Official
Main with GCC 15.2.0 and SUPERcop O3GC flags. The fixed benchmark ELFs were:

| Implementation | ELF SHA-256 | `.text` | `.rodata` |
|---|---|---:|---:|
| Official `avx2` | `c7c1d482a0357fba85d14060196dccd08a616bbf1404ae5a72b24e86df91b217` | 42,007 B | 5,384 B |
| Clean typed | `a3e095ed2800ae5a91fd8d17cd0d93a2c673a1741d75fccd6317c0bfbbb83069` | 64,343 B | 56,808 B |

Each mode used 16 balanced blocks and 64 fresh launches on CPU 1. Odd blocks
were Official/GT/GT/Official and even blocks reversed the order. Each launch
contributed 96 native observations per KEM operation. Negative delta means the
clean implementation is faster.

### Production-like PIE with ASLR enabled

| Operation | Official cycles | Clean cycles | Clean - Official | Relative | Favorable blocks | Bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Keypair | 21,456.65 | 21,173.91 | **-270.17** | **-1.259%** | 16/16 | [-303.06, -234.73] |
| Encap | 28,033.98 | 28,240.95 | **+207.92** | **+0.742%** | 2/16 | [+167.00, +244.48] |
| Decap | 19,344.52 | 19,144.79 | **-209.63** | **-1.084%** | 16/16 | [-215.85, -193.56] |

Encap contained one +1066-cycle paired-block outlier; its confidence interval
nevertheless remains entirely above zero.

### Same PIE ELFs with ASLR disabled by `setarch -R`

| Operation | Official cycles | Clean cycles | Clean - Official | Relative | Favorable blocks | Bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Keypair | 21,509.71 | 21,171.57 | **-331.91** | **-1.543%** | 16/16 | [-357.13, -309.17] |
| Encap | 28,032.45 | 28,127.58 | **+110.00** | **+0.392%** | 1/16 | [+64.20, +131.77] |
| Decap | 19,308.30 | 19,094.16 | **-222.43** | **-1.152%** | 16/16 | [-247.75, -198.94] |

The production decision is unchanged: the clean backend wins Keypair and
Decap, but it is not a strict replacement because Official still wins Encap.
Disabling ASLR narrows Encap's delivery variance without changing direction.

Raw launches, fixed ELFs, environment records, and analyzed JSON are under
`experiments/avx2_gt32_tile4_official_001/results/clean-typed-v1-formal-20260818/`.

## Clean-folder validation

The independently installed `avx2-clean-typed` snapshot passed the canonical
100-vector NTRU+768 KAT byte-for-byte on 2026-08-18:

```text
PQCkemKAT_2336.req  36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa
PQCkemKAT_2336.rsp  22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

The clean implementation also compiles as independent C/assembly translation
units and relocatably links with only the expected SUPERcop/libc imports:
`randombytes`, `crypto_declassify`, stack checking, and secure clear.

## Required formal method

- SUPERcop implementation directories in one fixed benchmark ELF.
- One pinned physical core.
- Turbo/frequency/runtime state recorded.
- ASLR disabled for the controlled measurement process with `setarch -R`.
- Palindromic Official/GT block order to limit drift.
- Keypair, Encap, and Decap measured from the same binary image.
- Report core cycles as the microarchitecture primary metric and TSC as
  latency corroboration.
- Run KAT, valid differential tests, and malformed/canonicality tests first.

Do not compare isolated numbers from different ELFs or infer a production win
from linker padding.

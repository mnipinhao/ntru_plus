# GT Clean table-GC fixed-ELF SUPERcop gate

Date: 2026-08-18

The production GT Clean source was exported independently as:

```text
crypto_kem/ntruplus768/avx2-gt32-clean-tablegc
```

Both implementations were freshly compiled by SUPERcop with GCC 15.2.0 and:

```text
-march=native -mtune=native -O3 -fwrapv -fPIC -fPIE
-ffunction-sections -fdata-sections -Wl,--gc-sections
```

The resulting `measure` ELFs were copied once and then held fixed for every
launch.

| Implementation | ELF SHA-256 | `.text` | `.rodata` | ELF file |
|---|---|---:|---:|---:|
| Official `avx2` | `c7c1d482a0357fba85d14060196dccd08a616bbf1404ae5a72b24e86df91b217` | 42,007 B | 5,384 B | 355,304 B |
| GT table-GC | `2f2bf04b64bb023a2b2d6f44faaa3d1123991e3e96b9d87ce8cf4bfcfc458d88` | 64,343 B | 21,576 B | 335,800 B |

Compared with the preceding Clean typed GT ELF, GT `.text` is unchanged at
64,343 B while `.rodata` falls from 56,808 B to 21,576 B.  The 35,232-byte
difference is exactly the set of split GT table sections discarded by the
linker.

The independently exported implementation passed the 100-vector canonical KAT
byte-for-byte.  Request and response hashes are in `kat-export/sha256.txt`.

## Method

- CPU 1, `default-perfevent/PERF_COUNT_HW_CPU_CYCLES`.
- 16 balanced paired blocks per mode, 64 fresh process launches.
- Odd blocks: Official/GT/GT/Official.
- Even blocks: GT/Official/Official/GT.
- 96 native observations per operation per launch.
- Launch-level stabilized Q2, then paired block deltas.
- Negative delta means GT is faster.
- The same fixed ELFs were tested with ASLR disabled and enabled.

## ASLR disabled

| Operation | Official | GT | GT - Official | Relative | Favorable blocks | 95% CI | MAD |
|---|---:|---:|---:|---:|---:|---:|---:|
| Keypair | 21,488.54 | 21,147.17 | **-345.11** | **-1.606%** | 16/16 | [-359.38, -321.38] | 18.74 |
| Encap | 28,023.93 | 28,134.36 | **+102.18** | **+0.365%** | 1/16 | [+61.06, +126.55] | 34.79 |
| Decap | 19,321.55 | 19,092.99 | **-219.19** | **-1.134%** | 16/16 | [-252.77, -203.67] | 26.33 |

## ASLR enabled

| Operation | Official | GT | GT - Official | Relative | Favorable blocks | 95% CI | MAD |
|---|---:|---:|---:|---:|---:|---:|---:|
| Keypair | 21,473.77 | 21,168.20 | **-304.15** | **-1.416%** | 15/16 | [-334.10, -258.88] | 38.79 |
| Encap | 28,033.49 | 28,213.42 | **+150.65** | **+0.537%** | 4/16 | [+26.07, +217.33] | 73.34 |
| Decap | 19,356.39 | 19,125.98 | **-228.81** | **-1.182%** | 16/16 | [-244.50, -168.55] | 35.45 |

## Delivery conclusion

The smaller image does not establish a general delivery-stability improvement.
Against the preceding Clean typed fixed-ELF gate:

- ASLR-off Keypair MAD improves from 25.30 to 18.74 cycles.
- ASLR-off Encap MAD worsens from 26.20 to 34.79; Decap is effectively flat
  at 25.11 versus 26.33.
- With ASLR enabled, the median deltas become more favorable for all three
  operations, but block MAD increases for all three.

Thus table GC is retained as production image hygiene and removes dormant
tables from placement decisions, but it is not a complete fix for launch-level
delivery variance.  The backend decision is unchanged: GT wins Keypair and
Decap, GT loses Encap, and Official remains the default complete backend.

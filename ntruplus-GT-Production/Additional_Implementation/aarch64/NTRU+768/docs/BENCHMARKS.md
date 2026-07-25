# GT-Optimized Benchmarks

GT-Optimized denotes the optimized Good-Thomas AArch64 Neon implementation.

All reported cycle counts must be measured on the same Raspberry Pi 5
Cortex-A76 setup, with identical SHAKE selection and benchmark method.

The clean release was measured against KPQC final with both implementations
using portable `NO_CE` SHAKE:

| Operation | KPQC final | GT-Optimized | Reduction |
|---|---:|---:|---:|
| Key generation | 40,134 | 36,852 | 8.18% |
| Encapsulation | 39,311 | 37,832 | 3.76% |
| Decapsulation | 35,179 | 32,741 | 6.93% |

Measurement setup:

- Raspberry Pi 5 Cortex-A76, pinned to core 3.
- Linux `6.18.33+rpt-rpi-2712`, Debian GCC 14.2.0.
- Linux `perf_event_open` hardware CPU-cycle counter.
- Two balanced 31-sample invocations per variant, 2,000 operations per
  sample, and 100 warmups.
- Separate KPQC and GT binaries, run in `KPQC/GT` then `GT/KPQC` order.
- Identical deterministic `randombytes` harness for both implementations.
- GCC `-O3 -fomit-frame-pointer`.
- `-ffunction-sections -fdata-sections -Wl,--gc-sections`.
- Every binary validates its fixture before timing and validates the final
  measured output after timing.

The p10/p50/p90 distributions were:

| Operation | Implementation | p10 | p50 | p90 |
|---|---|---:|---:|---:|
| Key generation | KPQC final | 40,111 | 40,134 | 40,142 |
| Key generation | GT-Optimized | 36,823 | 36,852 | 36,880 |
| Encapsulation | KPQC final | 39,308 | 39,311 | 39,317 |
| Encapsulation | GT-Optimized | 37,827 | 37,832 | 37,836 |
| Decapsulation | KPQC final | 35,157 | 35,179 | 35,198 |
| Decapsulation | GT-Optimized | 32,737 | 32,741 | 32,745 |

The archived run is included in
[`../../benchmark/results/pi5-reference-20260725/`](../../benchmark/results/pi5-reference-20260725/).
It contains the raw stdout for every invocation, the generated Markdown and
JSON summaries, and the build log. The recorded source-tree hashes are:

```text
GT-Optimized  de6c4b0b46707ebc0c07c40773292c821a2913960e2c2b09f0e46b3c610c7224
KPQC final    d08759f2faca6ecea9990b43a4c1cfda1bde67ece7dcb2d26fe7da5951e96381
```

## Where GT Wins

The following rows use the actual production KEM contracts rather than the
slower generic compatibility entry points. They were measured with 31 samples,
5,000 calls per sample, and 100 warmups. Combined rows overlap their component
rows and must not be added to other rows.

| KEM context | Measured contract | KPQC final | GT-Optimized | Reduction |
|---|---|---:|---:|---:|
| Key generation | sample NTT for `f` | 3,642 | 2,857 | 21.55% |
| Key generation | sample NTT for `g` | 3,639 | 2,867 | 21.21% |
| Key generation | base inversion + following multiplication | 6,693 | 5,708 | 14.72% |
| Encapsulation | NTT for `r` | 3,441 | 2,593 | 24.64% |
| Encapsulation | NTT for `m` | 3,441 | 2,592 | 24.67% |
| Encapsulation | multiply-add + ciphertext packing | 3,030 | 2,893 | 4.52% |
| Encapsulation | SOTP encode | 322 | 315 | 2.17% |
| Decapsulation | first multiplication + paired inverse NTT | 6,593 | 5,461 | 17.17% |
| Decapsulation | NTT for `m1` | 3,441 | 2,593 | 24.64% |
| Decapsulation | NTT for `r1` | 3,441 | 2,593 | 24.64% |
| Decapsulation | coefficient reduction modulo 3 | 400 | 384 | 4.00% |
| Decapsulation | verify product to canonical bytes | 3,426 | 3,394 | 0.93% |

The largest repeatable kernel-level gain is the forward NTT, at about 21-25%
in its KEM contexts. Key generation also benefits from treating hierarchical
base inversion and the following pointwise multiplication as one internal
representation contract. Decapsulation benefits from the paired `R^-1`
multiplication/inverse contract. Serialization remains an overhead that offsets
part of these kernel gains, which is why the full-KEM reductions are smaller.

## Code Size

Using the same 100-round KEM test harness and the same section-GC flags:

| Implementation | `.text` bytes | Total allocated bytes |
|---|---:|---:|
| KPQC final | 19,757 | 20,453 |
| GT-Optimized | 71,649 | 72,353 |

GT-Optimized is therefore about 3.63 times the KPQC `.text`
size. This is the main cost of retaining a large scheduled Good-Thomas NTT plus
keygen, encapsulation, and decapsulation-specific endpoints. Section GC is
already enabled; this number does not include rejected experiment families.
The compact generic serializer and shared-core key-generation serializer reduce
the GT linked `.text` by 6,400 bytes (7.93%) relative to the preceding
production build. Sharing the three identical inverse-NTT Stage45 row bodies
through one internal helper removes another 2,624 linked `.text` bytes.

## Correctness

- 100 full KEM round trips: pass.
- Required AAPCS64 sentinel mask: `0x00000`.
- Deterministic canonical KAT: byte-for-byte equal to KPQC final.
- Flattened release versus the include-fragment baseline: `.text`, `.rodata`,
  and `.data` sections are byte-for-byte identical.
- `PQCkemKAT_2336.rsp` SHA-256:
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

Run:

```sh
make test
make kat
make kat-check
make size
```

The repository benchmark harness may be used for the paired KPQC comparison,
but the release build itself intentionally contains no benchmark profile
selector.

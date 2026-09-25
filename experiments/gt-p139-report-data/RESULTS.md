# P139: the data a report needs that was missing

GT at main fb31b61d.  Official is SUPERCOP 20260831's leaf and, where marked,
GitHub main 3991b2a's `NO_CE` build (the same leaf with main's `crepmod3.s`,
P138).  Pi 5 (Cortex-A76) numbers are gcc 14.2; M2 Pro numbers Apple clang.
`throttled=0x50000` at every reading (sticky bits from before, current bits clear).

## 1. SUPERCOP 20260831 on the Pi 5, all three sets (`supercop_run.py`)

Unmodified `do-part`, six rotated rounds per set, three leaves per set.  Each
SUPERCOP data line is a median and 32 deviations; `supercop_run.py` keeps
every sample.  Key generation also as the **mean of all 576 samples**: with
retried candidates its distribution is multimodal, and 1152's round medians
swing between 49,466 and 58,265 (GT) or 61,573 and 70,305 (Official).

| cycles (median of rounds) | keypair | enc | dec | keypair, mean of samples |
|---|---:|---:|---:|---:|
| 768 Official (SUPERCOP leaf) | 38,419.5 | 38,590.5 | 33,586.5 | 38,961 |
| 768 Official (GitHub main) | 38,416.5 | 38,582.5 | 33,741.5 | 39,037 |
| **768 GT** | **31,621.5** | **29,277.5** | **27,322.0** | **32,300** |
| 864 Official (SUPERCOP leaf) | 44,045.5 | 46,086.5 | 40,791.5 | 44,645 |
| 864 Official (GitHub main) | 44,027.0 | 46,082.0 | 40,961.5 | 44,654 |
| **864 GT** | **36,290.5** | **34,962.0** | **33,184.0** | **37,039** |
| 1152 Official (SUPERCOP leaf) | (63,021) | 59,019.0 | 52,525.5 | 68,569 |
| 1152 Official (GitHub main) | (66,550.5) | 59,006.5 | 52,808.0 | 69,028 |
| **1152 GT** | **(55,127.5)** | **45,902.0** | **43,018.5** | **59,982** |

| GT vs Official | keygen (mean) | enc | dec |
|---|---:|---:|---:|
| 768, SUPERCOP leaf / GitHub main | -17.1% / -17.3% | -24.1% / -24.1% | -18.7% / -19.0% |
| 864 | -17.0% / -17.1% | -24.1% / -24.1% | -18.7% / -19.0% |
| 1152 | -12.5% / -13.1% | -22.2% / -22.2% | -18.1% / -18.5% |

1152's key generation by median would read -12.5% against one Official leaf
and -17.2% against the other; the means agree within 0.6 points, which is the
sampling noise of 576 samples.  Its expected lead (-12.5 to -13.1%) is smaller
than a fixed-seed harness shows (P138: -15.0%), because a fixed seed times one
particular retry count.

## 2. Code size, executed footprint, cold start (Pi 5, `build_extra.sh`, `run_extra.sh`)

- **Linked KEM text**: a program calling the three entry points, gc-sections,
  minus the same program against empty entry points (`size_main.c`).
- **Executed per operation**: distinct instruction addresses callgrind sees
  inside the entry point (`footprint.c`, `footprint.py`), x 4 bytes; libc's
  memcpy/memset counted apart (0.2-1.5 KB, similar on both sides).  lackey's
  `--trace-mem` spins on this Pi and was abandoned.
- **Cold**: P122's method -- before every operation read 32 MiB and execute
  96 KiB of distinct nops, RNG reseeded so every run sees the same inputs;
  medians of 61 per process, 12 alternating GT/Official process pairs, core 3
  (`cold.c`, `icache_thrash.S`).

| | linked text | executed: keygen / encaps / decaps | cold: keygen / encaps / decaps (cycles) |
|---|---:|---|---|
| 768 GT | 87,546 B | 45.3 / 22.4 / 25.0 KB | 47,956 / 44,103 / 43,179 |
| 768 Official | 19,174 B | 12.1 / 7.5 / 9.3 KB | 46,415 / 47,130 / 45,129 |
| 864 GT | 48,409 B | 28.3 / 21.7 / 32.7 KB | 51,342 / 48,918 / 55,158 |
| 864 Official | 22,806 B | 12.2 / 8.5 / 10.7 KB | 52,381 / 55,400 / 56,167 |
| 1152 GT | 48,509 B | 30.4 / 23.1 / 29.0 KB | 74,706 / 58,892 / 64,038 |
| 1152 Official | 20,854 B | 12.1 / 8.0 / 10.5 KB | 79,746 / 67,344 / 67,275 |

Cold, GT against Official: 768 **+3.3%** / -6.4% / -4.3% (GT faster in 1 / 12
/ 11 of 12 pairs), 864 -2.0% / -11.7% / -1.8% (10 / 12 / 8), 1152 -6.3% /
-12.6% / -4.8% (12 / 12 / 12).  Warm, every operation fits the 64 KB L1I, so
size costs nothing in steady state (P122); fully cold, most of the lead goes,
and 768's key generation -- the largest footprint -- falls behind.

P122 recorded 768's executed footprint as 25.1 / 24.6 / 25.3 KB with a method
not kept on record; the callgrind count here is exact and puts key generation
at 45.3 KB.

## 3. NTRU+768 component table (`comp768.c`, `build768.sh`)

P136's method for 768, by phase, because GT fuses steps (see the file head);
inputs from a real key pair and ciphertext, invertible baseinv inputs on both
sides.  Four GT entry points (`poly_cbd1`, `poly_sotp_encode`,
`poly_sotp_decode`, `poly_triple`) clobber d8-d15 (their `test_abi` mask is
non-zero; kem.c reaches them through `kem_api.S`), so they are called through
an AAPCS64 wrapper (`abi_wrap.S`) -- without it the harness's own timing
variables were corrupted.

| GT - Official | M2 (ns) | A76 (cycles) |
|---|---:|---:|
| keygen: cbd1 x2 | +6 | -14 |
| keygen: triple + forward NTT x2 | +5 | -404 |
| keygen: baseinv x2 | +3 | -151 |
| keygen: basemul x2 | -53 | -989 |
| keygen: tobytes x3 | **+50** | -642 |
| **keygen** | **+12** | **-2,204** |
| encaps: frombytes | +1 | -1 |
| encaps: forward NTT x2 | -60 | -1,613 |
| encaps: tobytes (r transcript) | **+48** | +211 |
| encaps: basemul_add + tobytes (ct) | **+54** | -247 |
| encaps: cbd1, sotp_encode | +3 | -14 |
| **encaps** | **+45** | **-1,665** |
| decaps: decode ct, f, hinv + first product | +17 | -32 |
| decaps: inverse -> ternary | -45 | -623 |
| decaps: forward NTT x2 (Official's copy included) | -32 | -870 |
| decaps: basemul | -14 | -263 |
| decaps: sub, tobytes x2, sotp_decode, cbd1 | +3 | -17 |
| **decaps** | **-71** | **-1,806** |

- A76: the sums (-918 / -694 / -753 ns) match P138's whole-KEM split of the
  arithmetic (-900 / -684 / -788 ns).
- M2: key generation and decapsulation match the split within 17 ns;
  encapsulation does not (+45 here, -16 in the KEM).  Hot-loop component
  timing leaves ~60 ns of GT's in-KEM encapsulation lead unexplained; the
  whole-KEM figure is the one to quote.  In place or not makes no difference
  to `poly_basemul_add_encap` (194 vs 197 ns; Official 168).
- 768's M2 deficits are the codec (`tobytes_keygen_cq`, P104's +53 ns;
  `tobytes_encap_loose`, which absorbs the reduction the small NTT skips;
  `tobytes_encap`) and `poly_basemul_add_encap` (+27 ns).  On the A76 all of
  them but the r-transcript tobytes are GT wins.

## 4. GT against Official with its two sponge fixes (from P138 part 3)

`upstream_fix/` in P138: `CE/fips202.c` absorbs the tail by lanes and
`load64` is one load; SUPERCOP's (= `NO_CE`'s) `fips202.c` gets the `load64`
fix.  Same sessions as the unfixed Official, output-checked:

| GT vs Official | as shipped | with the two fixes |
|---|---|---|
| M2, default (CE) build, 768 | -8.8 / -15.7 / -16.0% | -3.8 / -7.5 / -7.9% |
| M2, CE, 864 | -9.6 / -11.7 / -9.4% | -4.6 / -7.4 / -6.8% |
| M2, CE, 1152 | -9.5 / -12.1 / -10.3% | -5.4 / -6.7 / -6.4% |
| A76, `NO_CE`, 768 | -17.9 / -24.1 / -18.6% | -15.4 / -20.2 / -16.1% |
| A76, `NO_CE`, 864 | -18.0 / -24.0 / -18.7% | -15.6 / -20.5 / -16.6% |
| A76, `NO_CE`, 1152 | -15.0 / -22.2 / -18.3% | -13.0 / -18.5 / -16.0% |

(keygen / encaps / decaps; P138 harness, ns.)  The fixed M2 column still
contains GT's faster permutation (~11 ns a call over upstream's `CE/f1600.S`).

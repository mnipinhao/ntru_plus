# P17 — Why NTRU+864 beat the official before its hash work and NTRU+1152 does not

Branch `neon-1152`, parent `a3ad7ff8`.  Pi 5 core 3, GCC 14.2.0, perf_event PMU,
41 samples per point in both implementation orders (164 per figure).
`correctness=pass`, `cross_implementation_wire_differences=0`,
`instrumentation_equivalence=pass`.

The question: NTRU+864's GT lane was **already ahead of the selected official**
before its hash campaign (gates P53/P55).  NTRU+1152's is not.  This gate
establishes whether that is a property of the parameter set or of unfinished
work, and names what is missing.

## 1. The two standings, measured

864 at **P52**, the checkpoint immediately before the hash campaign
(`experiments/gt864-p52-official-profile/`):

| operation | official | GT | delta |
|---|---:|---:|---:|
| Keygen | 44,310 | 43,128 | **-2.67%** |
| Encaps | 46,440 | 44,914 | **-3.29%** |
| Decaps | 40,756 | 38,769 | **-4.88%** |

1152 now, re-measured for this gate (P12/P13 in place; the earlier P11 figures
predate them and P12/P13 were never entered in the ledger):

| operation | official | GT | delta |
|---|---:|---:|---:|
| Keygen | 64,065 | 67,670 | +5.6% |
| Encaps | 59,598 | 61,711 | +3.5% |
| Decaps | 52,537 | 60,799 | +15.7% |
| **total** | **176,200** | **190,181** | **+7.9%** |

## 2. Same categories, side by side

Both profiles aggregated with one mapping, per-operation medians summed over
keygen + encaps + decaps.  Attribution covers 91-92% of each total on both
sides, so the deltas are comparable (864's coverage is ~100%; its harness
instruments more call sites).

| category | 864 off | 864 GT | delta | 1152 off | 1152 GT | delta |
|---|---:|---:|---:|---:|---:|---:|
| hash | 69,959 | 70,856 | +897 | 84,789 | 86,642 | +1,852 |
| forward | 22,556 | 20,373 | **-2,183** | 28,884 | 26,277 | **-2,607** |
| inverse | 4,603 | 4,760 | +157 | 6,295 | 7,419 | +1,125 |
| basemul | 11,944 | 10,449 | **-1,495** | 16,134 | 15,963 | -171 |
| baseinv | 8,349 | 8,337 | -12 | 10,592 | 12,992 | +2,399 |
| **serialize** | 10,934 | 8,700 | **-2,234** | 10,066 | 20,975 | **+10,909** |
| sample | 4,430 | 4,062 | -368 | 3,895 | 4,460 | +565 |
| **SUM** | 132,775 | 127,537 | **-5,238** | 160,657 | 174,729 | **+14,072** |

**864 won pre-hash because its serializer was a win, not a loss.**  At -2,234 it
was 864's second largest single advantage, behind only the forward NTT.  1152's
is +10,909, the sign reversed, and it alone exceeds the whole 1152 deficit.

Note what the official side is doing: official serialize is **10,934 at 864 and
10,066 at 1152** — essentially the same work.  The official implementation is not
harder to beat at 1152.  The difference is entirely on the GT side: 8,700 against
20,975.

## 3. There is no structural penalty from the parameter set

Transferring 864's pre-hash *ratio* in each category onto 1152's official
baseline:

| category | 864 GT/off | 1152 GT/off | 1152 GT now | at 864's ratio | to find |
|---|---:|---:|---:|---:|---:|
| hash | 1.013 | 1.022 | 86,642 | 85,876 | +766 |
| forward | 0.903 | **0.910** | 26,277 | 26,089 | +188 |
| inverse | 1.034 | 1.179 | 7,419 | 6,510 | +909 |
| basemul | 0.875 | 0.989 | 15,963 | 14,115 | +1,848 |
| baseinv | 0.999 | 1.227 | 12,992 | 10,577 | +2,415 |
| serialize | 0.796 | 2.084 | 20,975 | 8,009 | **+12,966** |
| sample | 0.917 | 1.145 | 4,460 | 3,571 | +889 |
| SUM | 0.961 | 1.088 | 174,728 | 154,747 | **+19,981** |

```
864 at P52          -5,238 cycles   -3.95%
1152 now           +14,073 cycles   +8.76%
1152 at 864 ratios  -5,908 cycles   -3.68%
```

**At 864's pre-hash ratios, 1152 would stand at -3.68% — the same place 864
stood at -3.95%.**  Nothing about degree-4 leaves, 8 banks or the larger ring
costs anything structural.  The forward NTT proves it directly: 0.903 at 864
against **0.910 at 1152**, the same transform performing the same way at both
parameters, and P16 showed it is at 93% of the hardware floor.

Where the 19,981 sits:

| | cycles | share |
|---|---:|---:|
| serialize | +12,966 | **64.9%** |
| baseinv | +2,415 | 12.1% |
| basemul | +1,848 | 9.3% |
| inverse | +909 | 4.6% |
| sample | +889 | 4.4% |
| hash | +766 | 3.8% |
| forward | +188 | 0.9% |

## 4. The mechanism: 864 never materialises natural order

This is the concrete difference, and it is visible in the source.

**864.**  `pack.c` is twelve lines of wrapper; all three entry points call
straight into assembly.  `pack_full_top`, which serializes half a polynomial,
has this instruction mix:

| | count |
|---|---:|
| `trn1` / `trn2` | 100 / 100 |
| `uzp1` / `uzp2` | 54 / 54 |
| `tbl` / `ext` | 54 / 24 |
| `sqrdmulh` / `mls` / `mla` | 54 / 54 / 54 |
| `ushr` / `shl` / `orr` | 108 / 54 / 54 |
| `stur` | 108 |
| `ldr` | 62 |

The Good-Thomas to natural permutation is performed **in registers** with
`trn`/`uzp`/`tbl`/`ext`, fused with the Barrett reduction and the 12-bit packing,
and the wire bytes go out as plain full-vector `stur`.  There is no intermediate
array and no second pass over memory.  `pack_full.S` + `pack_small.S` +
`pack_compare.S` are 7,751 lines with 37 Slothy windows each — this cost roughly
twenty gates (p9, p14, p16, p18, p19, p23, p24, p29-p34, p38, p41, p44-p47).

**1152.**  `gt1152-p12-codec-neon/pack.c` declares `uint16_t nat[1152]` in all
three entry points.  Every call runs two passes: `gt_to_natural()` scatters
through the permutation into that scratch, then `pack_natural()` reads it back
and packs.  P14 measured the pieces against a 156-cycle contiguous-copy floor:

| | cycles |
|---|---:|
| contiguous copy (floor) | 156 |
| 12-bit pack only | 461 |
| permute GT -> natural | 941 |
| permute natural -> GT | 1,418 |

Per call, measured this gate: `poly_frombytes` 2,185 against the official's 509;
`poly_tobytes_small` 1,817 and `poly_tobytes` 2,368 against the official's 1,147.
The permutation pass *is* the deficit.

**P12 was the right first move and is one generation behind.**  It took serialize
from +30,750 to +10,909 by replacing a scalar gather with lane-indexed LD4/ST4.
What it did not do is remove the natural-order array.

## 5. P15's rejection does not close the fused route

P15 tried fusing and measured 12,129 cycles *worse*, but it fused within the
lane-indexed store family: `vst3_lane_u8` / `vld3_lane_u8`, which turns 8
halfword lane stores into 16 byte lane stores per group.  **864 uses no
lane-indexed store at all.**  Its permutation is `trn`/`uzp`/`tbl`/`ext` between
whole registers followed by full-vector `stur`.  That approach has not been tried
at 1152, and the degree-4 leaf should suit it better than degree-3 did — four
contiguous int16 is exactly one lane of a four-way structure, which is why 864
needs 54 `tbl` and 24 `ext` to fix up its three-coefficient leaves.

This does not make it free: 864 reached -2,234 with 7,751 lines of scheduled
assembly, and no estimate here says 1152 gets there more cheaply than 864 did.

## 6. Conclusions

1. **864's pre-hash lead was real and modest**: -3.95%, with the hash campaign
   later taking it to -11% / -21% / -13%.  The lead did not come from the
   transform alone; it came from *every* category being a win or neutral, the
   serializer most of all.
2. **1152 has no structural disadvantage.**  At 864's pre-hash ratios it would
   stand at -3.68%.  The forward NTT already matches 864's ratio (0.910 vs
   0.903) and is at 93% of the hardware floor (P16).
3. **65% of the shortfall is one component**, and its cause is named: 1152
   materialises natural order and 864 does not.
4. **The hash is not the reason.**  1152's hash ratio (1.022) is close to 864's
   pre-hash ratio (1.013); the entire hash category accounts for 766 of the
   19,981.  M2-1 is a large absolute win on top of parity, exactly as it was for
   864 — it is not what separates the two campaigns.

## Reproduce

```sh
cd experiments/gt1152-p11-profile
sh build.sh                    # on the Pi
taskset -c 3 ./profile_harness 0 > run-fwd.csv
taskset -c 3 ./profile_harness 1 > run-rev.csv
```

# P142: margins against GitHub main after P140

GT at main ec3ddf45 (with P140's two-state Keccak for key generation's seeds).
Official is `github.com/ntruplus/ntruplus` main 3991b2a throughout: its default
build (`CE/fips202.c` + `CE/f1600.S`) on M2, its `NO_CE` build (SUPERCOP's
leaf with main's `crepmod3.s`) on both machines, and main's CE sponge calling
GT's permutation for the permutation-equal comparison (on the A76 with
`NTRUPLUS_FORCE_SHA3` defined only to pass the sponge's `#error`, its f1600
routed to GT's scalar permutation).  `gt<s>_offhash` is GT's arithmetic and
KEM flow with that same sponge; `glue.c` gives it `hash_g_fr0` and
`shake256_x2` (as two Official `shake256` calls).  Every build output-checked
(same pk / ct / ss digest within a set, both machines); `nm` confirms GT links
the x2 routine on M2 and the offhash builds do not.  P129 harness, three
round-robin sessions per machine (`build.sh`, `run_sessions.sh`,
`tables.py`); `throttled=0x50000` throughout (sticky bits from earlier).

## M2 Pro (ns)

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| 768 GT | 3,490 | 4,038 | 3,106 |
| vs main default (CE) | **-16.3%** | **-15.6%** | **-16.1%** |
| vs main NO_CE | -22.3% | -22.0% | -19.5% |
| vs main sponge + GT permutation | -13.3% | -11.2% | -13.0% |
| 864 GT | 3,803 | 4,638 | 3,753 |
| vs main default (CE) | **-16.6%** | **-12.0%** | **-9.4%** |
| vs main NO_CE | -22.5% | -22.6% | -18.3% |
| vs main sponge + GT permutation | -13.5% | -7.1% | -6.0% |
| 1152 GT | 5,955 | 6,116 | 4,921 |
| vs main default (CE) | **-16.4%** | **-12.0%** | **-10.1%** |
| vs main NO_CE | -22.4% | -22.0% | -18.1% |
| vs main sponge + GT permutation | -13.5% | -7.2% | -6.4% |

## Cortex-A76 (ns)

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| 768 GT | 13,121 | 12,196 | 11,353 |
| vs main NO_CE | **-18.1%** | **-24.0%** | **-19.1%** |
| vs main sponge + GT permutation | -10.6% | -13.6% | -12.4% |
| 864 GT | 15,080 | 14,572 | 13,775 |
| vs main NO_CE | **-18.0%** | **-24.0%** | **-19.1%** |
| vs main sponge + GT permutation | -11.0% | -13.1% | -11.6% |
| 1152 GT | 23,902 | 19,134 | 17,825 |
| vs main NO_CE | **-14.9%** | **-22.2%** | **-18.7%** |
| vs main sponge + GT permutation | -7.7% | -10.8% | -11.1% |

## The permutation-equal lead, split

GT's hash layer (its sponge, and now the two-state Keccak) against the rest
(arithmetic and KEM glue):

| | M2: hash layer / rest (ns) | share | A76: hash layer / rest (ns) | share |
|---|---|---:|---|---:|
| 768 keygen / encaps / decaps | -548 / +14, -543 / +33, -377 / -88 | 103 / 106 / 81% | -651 / -905, -1,233 / -680, -744 / -864 | 42 / 64 / 46% |
| 864 | -564 / -31, -322 / -35, -185 / -55 | 95 / 90 / 77% | -706 / -1,151, -1,168 / -1,020, -654 / -1,145 | 38 / 53 / 36% |
| 1152 | -797 / -133, -455 / -20, -295 / -41 | 86 / 96 / 88% | -995 / -1,010, -1,593 / -715, -896 / -1,319 | 50 / 69 / 40% |

Against P138: M2 key generation moved from about -9% to -16% against main's
default build (P140); everything else is within half a point.  On M2 the
permutation-equal lead is almost all hash layer; on the A76 the arithmetic is
roughly half, -680 to -1,319 ns an operation.

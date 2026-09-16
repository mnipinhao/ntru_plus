# Results

Status: **cost decomposition passed; no new assembly candidate was promoted.**

## Exact static decomposition

Relative to the 569-instruction M5R-D bank, each CF5-B scaled bank retains the
same coefficient loads/stores, transposes, additions, and subtractions.  The
complete 280-instruction Forward delta is exactly:

- 64 extra Algorithm-10 multiplications = 192 `mul/sqrdmulh/mls`
  instructions;
- 88 extra public constant `ldr` instructions.

The per-bank split is:

| case | instructions | extra mulmods | extra loads | total delta | N1 proxy delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| t0c1 | 654 | 16 | 37 | +85 | +21 cycles |
| t0c2 | 654 | 16 | 37 | +85 | +21 cycles |
| t1c1 | 624 | 16 | 7 | +55 | +13 cycles |
| t1c2 | 624 | 16 | 7 | +55 | +13 cycles |

## Isolated Cortex-A76 PMU

Each generated function uses the exact returned instruction order and output
stores.  For every case, 64 inputs times 144 outputs matched the corresponding
complete M5R-D or CF5-B Pass-2 bit-for-bit before timing.  Three repetitions,
both `BCN` and `NCB` orders, 61 samples/order and 40,000 calls/sample ran on Pi
5 core 3 with `throttled=0x0`.

| case | baseline cycles | candidate cycles | paired delta | instruction delta | baseline IPC | candidate IPC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| t0c1 | 595.518 | 684.035 | +88.517 | +85 | 1.0243 | 1.0160 |
| t0c2 | 595.517 | 681.034 | +85.517 | +85 | 1.0243 | 1.0205 |
| t1c1 | 595.516 | 686.233 | +90.699 | +55 | 1.0243 | 0.9691 |
| t1c2 | 595.514 | 685.845 | +90.303 | +55 | 1.0243 | 0.9696 |

The four isolated deltas sum to **355.036 cycles**.  The prior complete-Forward
delta is 351.936 cycles, leaving only -3.100 cycles residual, or 0.88%.  The
isolated model therefore explains the full regression.

## Bottleneck classification

The table-load-only hypothesis is rejected.  Top0 performs 30 more additional
loads per bank than top1, yet top1 is slightly slower.  The common feature is
16 extra mulmods per bank.  Top1 additionally loses about 5.5% IPC, exposing a
dependency/schedule problem that the Neoverse-N1 proxy did not predict for the
Cortex-A76.

This does not prove a per-instruction cycle attribution: loads overlap with
arithmetic, and the mulmods and dependency graph are correlated.  It does prove
that `ldr` encoding/table compaction alone cannot recover the required 184.839
cycles.  The next candidate must change the FR-ISO2 arithmetic DAG and address
the top1 critical path, then demonstrate a complete-Forward delta no greater
than 167.097 cycles relative to M5R-D.

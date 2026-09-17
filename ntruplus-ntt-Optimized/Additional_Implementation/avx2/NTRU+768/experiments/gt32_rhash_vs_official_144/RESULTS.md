# Experiment 144 results

The promoted QL2 + direct-r-hash GT image was compared with the frozen
Official AVX2 implementation using a private NTRU+768 SUPERcop harness. Each
mode used 16 paired blocks and alternating Official/GT launch order.

All paired deltas are GT minus Official; negative is faster.

| ASLR | Operation | Official Q2 | GT Q2 | aggregate delta | paired mean | paired 95% CI | favorable blocks |
|---|---|---:|---:|---:|---:|---:|---:|
| on | Keypair | 21486.74 | 21245.81 | -240.93 | **-242.93** | **[-270.92,-214.82]** | 16/16 |
| on | Encap | 28201.50 | 28197.30 | -4.20 | +5.02 | [-62.94,+73.44] | 7/16 |
| on | Decap | 19300.21 | 19270.57 | -29.64 | **-28.98** | **[-49.54,-6.89]** | 14/16 |
| off | Keypair | 21451.51 | 21234.95 | -216.56 | **-219.02** | **[-231.25,-206.18]** | 16/16 |
| off | Encap | 28063.81 | 28203.37 | +139.56 | **+127.45** | **[+100.11,+154.14]** | 0/16 |
| off | Decap | 19269.30 | 19264.59 | -4.71 | -8.14 | [-19.88,+3.65] | 10/16 |

## Decision

`DIRECT_R_HASH_PRODUCTION_PROMOTED_OFFICIAL_ENCAP_NOT_CLOSED`

Experiment 143 proves that direct-r-hash is a real production optimization:
it improves Encap while Keypair and Decap remain neutral in the matched
production A/B. It is therefore retained in GT Clean.

Against Official, Keypair remains clearly faster. Decap is faster with ASLR
enabled and neutral with ASLR disabled. Encap is statistically tied in the
primary ASLR-on campaign but remains about 127 paired core cycles slower with
ASLR disabled. Therefore this promotion nearly closes, but does not robustly
reverse, the remaining Official Encap gap.

The result closes the `r` serializer copy debt. Future Encap work must target
a different operation class; it must not count these removed copy loads and
stores again.

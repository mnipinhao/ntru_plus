# GT production I-cache and link-order result

Pi 5 Cortex-A76, core 3, portable `NO_CE`, 61 samples x
2000 calls. Internal cycles/instructions are medians. External perf
events are process-level means divided by measured calls; use them for
same-mode relative diagnosis, not as isolated kernel counts.

| Mode | Variant | Cycles | Instructions | CPI | Text | Cycles vs L0 | Text vs L0 | L1I misses/call | Front stalls/call | Backend stalls/call |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| kem_keygen | L0_current | 37713 | 86067 | 0.4382 | 95341 | +0 | +0 | 0.99 | 8.84 | 12361.45 |
| kem_keygen | L1_gc | 37711 | 86069 | 0.4381 | 81273 | -2 | -14068 | 0.95 | 4.65 | 12351.51 |
| kem_keygen | L2_mode_hot | 37720 | 86067 | 0.4383 | 95309 | +7 | -32 | 0.96 | 9.18 | 12338.33 |
| kem_keygen | L3_mode_hot_gc | 37719 | 86069 | 0.4382 | 81241 | +6 | -14100 | 0.97 | 11.15 | 12370.77 |
| kem_enc | L0_current | 37604 | 106175 | 0.3542 | 95325 | +0 | +0 | 0.85 | 5.35 | 7867.67 |
| kem_enc | L1_gc | 37590 | 106173 | 0.3540 | 81257 | -14 | -14068 | 0.77 | 4.59 | 7860.77 |
| kem_enc | L2_mode_hot | 37604 | 106175 | 0.3542 | 95325 | +0 | +0 | 0.82 | 4.39 | 7908.61 |
| kem_enc | L3_mode_hot_gc | 37582 | 106173 | 0.3540 | 81257 | -22 | -14068 | 0.89 | 5.44 | 7874.73 |
| kem_dec | L0_current | 32850 | 76465 | 0.4296 | 95325 | +0 | +0 | 10.09 | 8.65 | 10583.47 |
| kem_dec | L1_gc | 32825 | 76465 | 0.4293 | 81257 | -25 | -14068 | 3.79 | 4.36 | 10668.48 |
| kem_dec | L2_mode_hot | 32853 | 76465 | 0.4296 | 95325 | +3 | +0 | 10.01 | 4.33 | 10585.84 |
| kem_dec | L3_mode_hot_gc | 32885 | 76465 | 0.4301 | 81257 | +35 | -14068 | 3.78 | 4.27 | 10610.96 |

Cycle winners:

```json
{
  "kem_keygen": "L1_gc",
  "kem_enc": "L3_mode_hot_gc",
  "kem_dec": "L1_gc"
}
```

Promotion rule: a link-order/GC candidate must not regress any full-KEM mode.
Alignment padding was intentionally excluded because the previous blanket
32-byte alignment experiment regressed encapsulation.

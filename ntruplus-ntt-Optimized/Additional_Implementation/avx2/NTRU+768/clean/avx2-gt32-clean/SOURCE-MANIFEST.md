# Source provenance

This directory was exported from:

```text
experiments/avx2_gt32_tile4_official_001
```

using the Gc/H0 selected call graph. The initial source selection was made by
`tools/install_supercop_fastest_clean.sh`; this directory then performed only
production cleanup:

- experimental selectors were resolved;
- unused assembly function emissions were pruned;
- files and selected symbols were renamed;
- the three NTT assembly translation units were kept separate;
- documentation and a non-overwriting SUPERcop installer were added.

Selected source families were:

| Clean file | Selected source role |
|---|---|
| `ntt.s` | TILE4 wide raw frontend |
| `ntt_m.s` | all-BM-SoA M terminal Forward |
| `ntt_p.s` | BaseInv-safe P/L3 terminal Forward |
| `basemul.s` | M B3 scale/general and finalizer-free F0-by-J1 product |
| `baseinv.c`, `batch_inverse.s` | P/J1 BaseInv and hand-written batch tree |
| `invntt.s` | selected global inverse core and isolated T9 tail |
| `pack.s` | selected Q24 M/P codec and native Decap equality |

`SHA256SUMS` contains relative checksums of the finished clean snapshot.

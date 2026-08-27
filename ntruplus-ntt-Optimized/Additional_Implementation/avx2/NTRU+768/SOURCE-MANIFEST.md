# Source provenance

This implementation was selected from:

```text
experiments/avx2_gt32_tile4_official_001
```

using the Gc/H0 selected call graph. The initial source selection was made by
`tools/install_supercop_fastest_clean.sh`, first staged under
`clean/avx2-gt32-clean`, and then promoted to this NTRU+768 source root.  The
production cleanup performed the following:

- experimental selectors were resolved;
- unused assembly function emissions were pruned;
- independently aligned assembly constant tables were placed in collectable
  `.rodata.gtclean.*` sections;
- the local qualification build enabled function/data sections and linker
  garbage collection;
- files and selected symbols were renamed;
- the three NTT assembly translation units were kept separate;
- documentation and a non-overwriting SUPERcop installer were added.

Official sources and local test/KAT harnesses are resolved from the frozen
`third_party/NTRUplus-official-main` tree; no second Official implementation is
kept in this directory.

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

The promoted E0V integration adds `encap-slot-pad.s`, `e0v-tail.ld`, and the
production-owned `qualified/` builder/auditor. These files preserve the
executable geometry qualified by experiments 087, 091, 092, and 093; they are
not optional benchmark padding.

Experiment 094 subsequently removed the dead fifth Encap polynomial slot. The
qualified geometry reference remains the promoted E0V caller before this
frame-only change, so the audit isolates the 6592-byte current frame from the
8128-byte E0V control.

`SHA256SUMS` contains relative checksums of the finished clean snapshot.

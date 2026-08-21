# GT32 DELIVERY ROBUSTNESS / CAUSAL MAP 040

## Decision

040 closes the current code-delivery attribution line with two corrections:

1. Code address is a real performance input for both Official and GT32.  It is
   not a GT32-only failure mode.
2. No single tested GT32 hot cluster explains the earlier 100--200 cycle
   whole-image swings.  The remaining sensitivity is compositional across hot
   regions, not a localized fragile inverse tail or Q24 body.

Therefore this experiment does **not** select a magic offset and does **not**
change the production GT Clean implementation.  A fixed-slot production linker
architecture (`041`) is not justified by a concentrated culprit from this gate.

The established equal-size cage methodology remains required for measuring
small intrinsic changes.

## Scope

No arithmetic or executed instruction sequence was changed.  The experiment
only relocates selected functions inside fixed-size cages.

The source production tree remains untouched.  All generated implementations,
fixed SUPERcop executables, tools, and results live below this directory.

## 040A: broad deterministic relocation

Official and GT Clean were each built at five deterministic broad shifts:

```text
0x000, 0x200, 0x400, 0x600, 0x800
```

The benchmark used CPU 1, native SUPERcop measure executables, balanced layout
order, and both normal PIE/ASLR and `setarch -R` controls.

Cycle range across the five layouts:

| ASLR | implementation | Keypair | Encap | Decap |
|---|---:|---:|---:|---:|
| on | Official | 148.25 | 248.00 | 219.75 |
| on | GT Clean | 72.75 | 130.00 | 162.25 |
| off | Official | 149.75 | 257.00 | 229.00 |
| off | GT Clean | 68.25 | 317.75 | 233.75 |

This rejects the former working assumption that compact Official loops are
intrinsically layout-stable while GT32 alone is fragile.  GT Encap is the most
sensitive cell in the ASLR-off sweep, but Official Encap and Decap also move by
more than 200 cycles.

The broad sweep is a sensitivity measurement, not an offset ranking.  No
winning broad offset is promotion-eligible.

## 040B: fixed-cage hot-cluster localization

Each cluster member receives its own 0x800-byte cage.  Moving a cluster to
`+0x400` or `+0x800` leaves all tracked unrelated hot-symbol addresses exactly
unchanged.  Address audit confirmed exact target movement and zero collateral
movement within each family.

The final gate uses 48 balanced blocks with ASLR disabled.  The primary result
is the same-block paired median and deterministic bootstrap 95% interval.

### Stable signals at +0x400

| Cluster | Operation | paired median cycles | 95% bootstrap CI |
|---|---:|---:|---:|
| B3-scale + inverse core | Decap | -18.00 | [-41.00, -7.50] |
| frontend + N5 (build A) | Encap | -27.75 | [-52.75, -16.00] |
| frontend + N5 (build A) | Decap | -15.75 | [-26.00, -0.50] |
| frontend + N5 (byte-identical build B) | Encap | -23.50 | [-38.00, -7.50] |
| frontend + N5 (byte-identical build B) | Decap | -17.75 | [-25.50, -4.75] |
| general B3 + centered Q24 | Decap | -23.50 | [-34.00, -17.25] |
| general B3 + lazy Q24 | Encap | -37.50 | [-66.00, -12.00] |
| general B3 + lazy Q24 | Decap | -36.25 | [-51.50, -15.50] |

The duplicated frontend/N5 family has identical `.text`, addresses, and sizes,
and reproduces the direction.  This is the cleanest localized address effect.

However, the cluster effects are only roughly 15--38 cycles.  Decode-only,
inverse-tail-only, and Q24-only moves do not produce stable large effects.  The
`+0x800` results also do not consistently preserve the `+0x400` benefit.

Consequently no cluster accounts for the former 100--200 cycle swings on its
own.  The larger swings require multiple address relationships to change
together.

## PMU control

A balanced whole-process `perf stat` control collected:

```text
cpu_core/cycles/
cpu_core/instructions/
cpu_core/idq.dsb_uops/
cpu_core/idq.mite_uops/
```

This control is intentionally recorded as inconclusive.  The two executables
in each pair have the same executed instruction sequence, yet whole-process
retired-instruction deltas varied by tens or hundreds of thousands.  The
SUPERcop process lifecycle and run-level disturbance swamp a 20--40 cycle hot
region signal.  These counters cannot identify DSB/MITE as the mechanism.

Any future PMU investigation must use a region-scoped repeated caller harness,
not `perf stat` around the complete SUPERcop measure process.

## Final interpretation

```text
intrinsic optimization measurement:
    solved well enough by equal-size fixed-address cages

production layout robustness:
    quantified, but not eliminated

single fragile GT cluster:
    not found

Official uniquely stable:
    rejected

magic alignment/padding search:
    prohibited

041 fixed hot-slot architecture:
    not opened by this evidence
```

The delivery micro-tuning family should now stop.  Future performance work
should return to deletion of real producer/consumer work.  Any such candidate
must first be adjudicated in a fixed-size cage and only then integrated into a
whole image.

## Reproduction

```sh
./tools/materialize_sweep.py
./tools/build_sweep.sh
./tools/run_curve.py

./tools/materialize_clusters.py
./tools/build_sweep.sh
./tools/run_cluster_curve.py
./tools/analyze_cluster_pairs.py
```

`tools/run_frontend_pmu.py` reproduces the negative whole-process PMU control;
it is not a promotion benchmark.

## Artifacts

- `results/layout_sensitivity_curve.json`: broad Official/GT curves.
- `results/cluster_sensitivity_curve.json`: 48-block cluster samples and
  symbol addresses.
- `results/cluster_paired_summary.json`: paired medians and bootstrap intervals.
- `results/frontend_pmu_pairs.json`: inconclusive whole-process PMU control.
- `generated/cluster_manifest.json`: fixed-cage cluster definitions.


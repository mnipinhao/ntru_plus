# GT production mainline contract

Updated: 2026-07-27

This document fixes the configuration and validation policy used when the
AArch64 GT production line is integrated into the repository mainline.

## Selected default

The mainline build selects:

```text
GT_PRODUCTION_DEFAULT_VARIANT=gt_production_q31
GT_PRODUCTION_KEYGEN_LAYOUT=cq
GT_PRODUCTION_DECAP_VERIFY_PROFILE=pipeline
GT_PRODUCTION_USE_SECTION_GC=1
```

The resulting KEM uses the Direct-CQ keygen endpoint, Q31 encapsulation
endpoint, paired rminus1 pointwise/inverse contract, and compact pipelined
decapsulation verification backend. This is the same implementation profile
flattened into `ntruplus-GT-Production`.

The historical `mixed` and `legacy` keygen layouts remain explicit
compatibility and benchmark inputs. They are not alternative defaults:

```text
GT_PRODUCTION_KEYGEN_LAYOUT=mixed
GT_PRODUCTION_KEYGEN_LAYOUT=legacy
```

## Public and internal ABI

Public KEM and required polynomial entrypoints obey AAPCS64 and are covered by
the ABI sentinel. Some closed-world support leaves use `d8-d15` as internal
scratch and are not supported as independently callable library symbols.

Changing compiler family, compiler version, optimization flags, or source
closure requires rebuilding the complete KEM and rerunning the ABI sentinel,
KEM round-trip, and byte-for-byte KAT. Passing only an assembly or kernel
micro-test is not a release gate.

## Repository artifact policy

Mainline tracks:

- production and test source;
- canonical KAT vectors;
- source and release manifests;
- benchmark runners;
- curated benchmark summaries.

Mainline does not track:

- generated release zip files;
- benchmark binaries;
- raw benchmark stdout and build logs;
- local upstream comparison checkouts.

Release archives and raw benchmark evidence are generated from a selected
commit and published as external release or CI artifacts.

## Required gates

Before moving the mainline pointer or publishing a release:

```text
optimized workspace:
  check-production-layout
  production symbol closure
  KEM differential and KAT

standalone release:
  make check
  make size
  make symbols

performance host:
  GT versus KPQC full-KEM benchmark under one fixed compiler/hash policy
```

The standalone release `make check` includes source-manifest validation, 100
KEM round trips, the public ABI sentinel, and canonical KAT comparison.

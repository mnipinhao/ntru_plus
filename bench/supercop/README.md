# SUPERCOP benchmark policy

Formal performance comes from the release pinned in `../supercop.lock` and a
disposable campaign tree. Native KEM runs keep SUPERCOP's
`crypto_kem/measure.c` unchanged. Derived polynomial runs temporarily install
`poly_measure.c` in the campaign and are always labelled
`supercop-derived-poly`.

Both measures use 32 successive `cpucycles()` deltas. SUPERCOP compiles the
measure with `LOOPS=3`, so each fresh process emits 96 observations per
operation. A serious run launches the exact SUPERCOP-built measure ELF 9 times,
pools 864 observations, and reports StQ1/StQ2/StQ3 using the pinned release's
stabilized-quartile definition. StQ2 is the headline.

Short runs use three fresh processes and record frequency state without
claiming formal status. Serious runs require the performance governor and
disabled turbo/boost. The runner never writes sysfs.

Typical commands from a parameter experiment are:

```sh
make supercop-kem-short SUPERCOP_CAMPAIGN_ROOT=/path/to/campaign
make supercop-kem-serious SUPERCOP_CAMPAIGN_ROOT=/path/to/campaign
make supercop-poly-short SUPERCOP_CAMPAIGN_ROOT=/path/to/campaign
make supercop-poly-serious SUPERCOP_CAMPAIGN_ROOT=/path/to/campaign
```

Each result retains `run.out`, SUPERCOP `data`, `metadata.json`, the exact
`measure` ELF, `fresh-launches/*.out`, `stq-summary.json`, and the lock file.
Repository-local paired timings remain useful diagnostics but are not
SUPERCOP headlines.

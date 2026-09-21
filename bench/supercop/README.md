# SUPERCOP benchmark policy

Formal performance comes from the release pinned in `../supercop.lock` and a
disposable campaign tree. Native KEM runs keep SUPERCOP's
`crypto_kem/measure.c` unchanged. Derived polynomial runs temporarily install
`poly_measure.c` in the campaign and are always labelled
`supercop-derived-poly`. Inverse-tail kernel comparisons temporarily install
`itail_measure.c` and are labelled `supercop-derived-itail`.

All measures use 32 successive `cpucycles()` deltas. SUPERCOP compiles the
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
make supercop-itail-short SUPERCOP_CAMPAIGN_ROOT=/path/to/campaign
make supercop-itail-serious SUPERCOP_CAMPAIGN_ROOT=/path/to/campaign
make supercop-itail-d0-short SUPERCOP_CAMPAIGN_ROOT=/path/to/campaign
make supercop-itail-d0-serious SUPERCOP_CAMPAIGN_ROOT=/path/to/campaign
make supercop-itail-d0-m2-short SUPERCOP_CAMPAIGN_ROOT=/path/to/campaign
make supercop-itail-d0-m2-serious SUPERCOP_CAMPAIGN_ROOT=/path/to/campaign
```

The inverse-tail measure balances code placement in every loop by running
B0-first/B1-second and B1-first/B0-second. Its report contains pooled StQ
values plus a paired StQ2 delta for every fresh launch.
The D0 measure applies the same balanced ordering to the materialized and
register-live D8-to-inverse9 schedules and is labelled
`supercop-derived-itail-d0`.
The three-way M0/M1/M2 late-layer attribution is labeled
`supercop-derived-itail-d0-m2`; it is also a primitive diagnostic, not a native
SUPERCOP public result.

The NTRU+1152 PROD3 hash-fanout measure is labelled
`supercop-derived-gt9x16-prod3-hash-fanout`.  It runs O0/O1/C0/C1 in a
four-position Latin square within one ELF.  Its headline is the per-launch
median excess tax `(C1-C0)-(O1-O0)`, not the raw `C1-O1` difference.  Placement
selection uses the fastest absolute C1 ASLR-on result; normal/reversed and
ASLR on/off serious replays remain diagnostic controls.

Each result retains `run.out`, SUPERCOP `data`, `metadata.json`, the exact
`measure` ELF, `fresh-launches/*.out`, `stq-summary.json`, and the lock file.
Repository-local paired timings remain useful diagnostics but are not
SUPERCOP headlines.

The unified 768/864/1152 campaign additionally uses the
`derived-component-768`, `derived-component-864-d3`, and
`derived-component-1152-current` modes.  Hash, SOTP, add/sub, and polynomial
entries in `poly_measure.c` are caller building blocks; they remain
`supercop-derived-component` evidence and must not be summed to predict the
Native KEM totals.

Forward attribution distinguishes `native_inplace` from `preserve_input`.
The latter includes a real polynomial copy before the implementation's native
in-place transform.  Reports must state which ownership contract is being
answered; a preserve-input wrapper is not the Official production kernel.
`forward_general_*_unqualified` is diagnostic only until the implementation's
general-input range and differential contract is proved.

PMU mode selection is parsed once before the 4096-operation loop.  The matched
baseline uses the same switch and loop geometry with a compiler memory barrier.
Any negative baseline-subtracted event invalidates that component's PMU record.
The 4096-bank Forward PMU working set prevents repeated in-place transformation
of already-transformed data; its cycle count diagnoses residency and is not a
component timing headline.

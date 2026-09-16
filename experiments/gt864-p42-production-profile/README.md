# Post-P42 GT864 production versus selected Official profiler

This is a measurement-only checkpoint for exact GT production revision
`34d2c758` against the user-selected
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64` implementation.

The GT tree is extracted with `git archive`; unrelated working-tree changes do
not enter the binaries. The inherited reviewed profiler runs fresh GT package
checks and KAT, cross-implementation exact/tampered checks, clean paired PMU,
call-site cycle profiling, and retired-instruction/branch event profiling.

The selected Official snapshot uses SHAKE256 and has not been independently
verified as the latest upstream revision.

The first attempted archive at `151ed540` was correctly rejected before build
because the P42 roadmap update had not refreshed `SOURCE-MANIFEST.sha256`.
Commit `34d2c758` repairs only that manifest entry; executable sources are
unchanged.

Run with:

```sh
python3 run_pi5.py
```

The campaign passed. See [RESULTS.md](RESULTS.md) and the machine-readable
`results.json`, `event-results.json`, `environment.json` and `SUMMARY.json`.

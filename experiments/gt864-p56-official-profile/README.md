# P56 — selected-Official profiler checkpoint

P56 is a measurement-only comparison of exact committed P55 production
(`9941d3bc`) against the user-selected SUPERCOP 20260831 implementation at:

```text
/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64
```

The selected source uses SHAKE256 and is pinned by the hashes in
`bench/aarch64/gt-production/OFFICIAL-BASELINE.json`. It has not independently
been verified as the latest upstream revision.

The campaign runs six balanced processes on Pi 5 core 3. Each implementation
gets 252 clean observations per KEM operation and 126 observations per
instrumented component. Clean full-KEM PMU values are authoritative;
instrumented component values are diagnostic and do not have to sum exactly to
the clean totals.

Run with:

```sh
python3 experiments/gt864-p56-official-profile/run_pi5.py
```

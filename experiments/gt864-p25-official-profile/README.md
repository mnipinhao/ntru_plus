# P25 — post-P24 selected-Official profiler checkpoint

P25 is a measurement-only gate.  It compares exact P24 GT864 production commit
`d76a8289` with the user-selected SUPERCOP 20260831 AArch64 implementation at
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`.

The GT package is extracted with `git archive`; benchmark-time working-tree
changes cannot enter the target.  The runner reuses the reviewed P12/P20 clean
full-KEM, call-site cycle, retired-instruction and branch profiler.  It runs
fresh package/KAT checks, cross-implementation exact/tampered transcripts and
instrumentation-equivalence checks before accepting PMU data.

```sh
python3 run_pi5.py
```

Result: passed.  P24 production beats the selected Official implementation in
all three complete KEM operations.  The largest remaining positive matched
boundary is Decaps Inverse-to-ternary; aggregate ToBytes remains second.  See
[RESULTS.md](RESULTS.md).

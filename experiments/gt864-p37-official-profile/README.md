# P37 — post-P35 selected-Official profiler checkpoint

P37 is a measurement-only gate. It compares exact P35 GT864 production commit
`88fb877e` with the user-selected SUPERCOP 20260831 AArch64 implementation at
`/home/pi/supercop-20260831/crypto_kem/ntruplus864/aarch64`.

The GT package is extracted with `git archive`; benchmark-time working-tree
changes cannot enter the target. The runner reuses the reviewed P12/P25 clean
full-KEM, call-site cycle, retired-instruction and branch profiler. It runs
fresh package/KAT checks, cross-implementation exact/tampered transcripts and
instrumentation-equivalence checks before accepting PMU data.

```sh
python3 run_pi5.py
```

Result: passed. P35 production beats the selected Official implementation in
all three complete KEM operations. The remaining positive matched boundaries
are Full ToBytes and Decaps Inverse-to-ternary; after separating Full from the
already-winning Small serializer, Full ToBytes is the larger opportunity. See
[RESULTS.md](RESULTS.md).

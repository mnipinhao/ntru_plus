# P20 — post-P19 selected-Official profiler checkpoint

P20 is a measurement-only gate. It compares the P19 GT864 production package
with the user-selected SUPERCOP 20260831 AArch64 implementation and refreshes
the clean full-KEM, 22-group call-site, and instruction/branch profiles.

The runner reuses the reviewed P12 profiler and changes only the injected GT
production source/revision and experiment identity. Generated binaries and raw
logs remain in the ignored local `build/` directory and the isolated Pi 5 run
directory.

Result: passed. P19 production beats the selected Official implementation in
all three complete KEM operations. The largest remaining positive same-boundary
gap is Decaps Inverse-to-ternary, followed closely by aggregate ToBytes. See
`RESULTS.md` for provenance, measurements, and the P21 decision.

```sh
python3 run_pi5.py
```

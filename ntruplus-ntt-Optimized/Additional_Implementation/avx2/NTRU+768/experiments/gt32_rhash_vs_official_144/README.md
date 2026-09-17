# 144 — promoted direct-r-hash GT versus Official

This gate compares the geometry-qualified production GT image after Experiment
143 against the frozen NTRU+768 Official AVX2 implementation.  It uses the
native SUPERcop measurement harness, CPU 1, 16 paired blocks, alternating
Official/GT launch order, and reports ASLR-on plus ASLR-off corroboration.

```sh
make benchmark
```

# GT32 QL2 production qualification 139

This gate benchmarks the promoted production source tree directly against
frozen Official Main. It uses SUPERcop's native `crypto_kem/measure.c`, the
prepared host libraries, CPU 1 pinning, ABBA/BAAB ordering, sixteen fresh-
process blocks per ASLR mode, and the stabilized-quartile estimator.

The production build keeps the E0V helper and appends the three QL2 kernels in
the deterministic page-aligned RX tail. No experiment-generated object is
linked into the GT benchmark executable.

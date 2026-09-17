# GT32-QL2-VS-OFFICIAL-132

This gate compares the qualified, geometry-preserving QL2 Encap candidate
from experiment 104 directly with the NTRU+768 Official AVX2 implementation.

It does not modify the production GT Clean source tree.  The QL2 binary keeps
the `b2a4bea` production image anchored and appends the deterministic private
QL2 RX cluster used by experiment 104.

The benchmark follows the SUPERCOP measurement model:

- the native SUPERCOP `measure.c` harness and stabilized-quartile estimator;
- CPU 1 affinity;
- 16 paired blocks in alternating O/Q/Q/O and Q/O/O/Q order;
- ASLR enabled for the primary result;
- ASLR disabled only as a corroborating geometry view.

Run:

```sh
make benchmark
```

The immutable architecture under test is:

```text
Forward(m) -> QL2
B3(h,r)    -> QL2
QL2(product,m) -> final-Q reduction -> WIRE12
```

The comparison reports all three KEM operations because only Encap is
intentionally changed; Keypair and Decap therefore expose shared-image
collateral.


# SUPERCOP benchmark lane

This lane packages NTRU+ implementations for measurement by SUPERCOP itself.
It deliberately does not emulate SUPERCOP's cycle counter or statistics.

After `make -C bench supercop-package ...`, run from the SUPERCOP checkout:

```sh
./do-part init
./do-part crypto_kem ntruplus864
```

Use `ntruplus1152` for NTRU+1152. Compare Production and Experiment on the
same machine, CPU policy, compiler configuration, and SUPERCOP revision. Keep
the first quartile, median, third quartile, and raw SUPERCOP data path with the
promotion record.

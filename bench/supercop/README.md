# SUPERCOP benchmark lane

This lane packages NTRU+ implementations for measurement by SUPERCOP itself.
It deliberately does not emulate SUPERCOP's cycle counter or statistics.

After `make -C bench supercop-package ...`, run from the SUPERCOP checkout:

```sh
./do-part init
./do-part crypto_stream chacha20
./do-part crypto_rng
./do-part crypto_kem ntruplus864repo
```

On macOS, SUPERCOP 20260627 also needs its `cpuid/do` byte formatting made
portable to BSD `od`; the campaign result records the exact patch. The
packager prepends SUPERCOP's generated `crypto_kem.h` to the packaged `kem.c`
so SUPERCOP can namespace the implementation without changing Production. It
also installs a checked-in scheme checksum when one is available; this makes
SUPERCOP reject outputs that disagree with the KEM byte contract instead of
accepting them as `unknown`.

Use a separate scheme name whenever the repo KEM byte contract differs from a
built-in SUPERCOP primitive. Compare Production and Experiment on the
same machine, CPU policy, compiler configuration, and SUPERCOP revision. Keep
the first quartile, median, third quartile, and raw SUPERCOP data path with the
promotion record.

Summarize the three SUPERCOP measurement batches with the stabilized-quartile
definition used by SUPERCOP's `stq.h`:

```sh
python3 bench/supercop/summarize.py \
  /path/to/supercop/bench/HOST/data --scheme ntruplus864repo
```

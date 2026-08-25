# NTRU+864/1152 Neon lanes

The existing implementation directories are the Production source of truth:

- `NTRU+864/`
- `NTRU+1152/`

The two Production builds share only `common/kem.c`. This neutral copy breaks
the old dependency on mutable NTRU+768 GT `kem.c`; parameter-specific Neon
polynomial and assembly sources remain inside each Production directory.

All unproven work belongs below the matching Experiment directory:

- `Experiment/NTRU+864/<candidate>/`
- `Experiment/NTRU+1152/<candidate>/`

Production builds run `check-production-boundary` before compiling. The check
rejects source references or symlinks from Production into `Experiment/`.
Experiment is never globbed or linked by `stock.mk`.

## Candidate lifecycle

1. Start a self-contained candidate under `Experiment/<PARAM>/<candidate>/`.
2. Record its parent Production revision and changed kernel contract.
3. Pass the candidate's test and KAT comparison against Production.
4. Benchmark both implementations through SUPERCOP on the same AArch64 host.
5. Promote only the measured winner by copying the reviewed source change into
   the Production directory. Never make Production point at Experiment.
6. Record the exact host, compiler, SUPERCOP revision, quartiles, and KAT result.

An experiment that loses or has inconclusive data remains in Experiment. It
must not change Production defaults.

## SUPERCOP packaging

Use the repository helper to install a self-contained implementation in an
existing SUPERCOP checkout:

```sh
make -C bench supercop-package \
  IMPL=../ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+864 \
  SUPERCOP_ROOT=/path/to/supercop \
  SUPERCOP_SCHEME=ntruplus864 \
  SUPERCOP_IMPL=neon-production
```

Package an Experiment candidate with a different implementation name, then
run SUPERCOP's own `do-part` flow. SUPERCOP remains responsible for the cycle
counter, repeated measurements, and quartile reporting; this repository does
not substitute a look-alike timing loop.

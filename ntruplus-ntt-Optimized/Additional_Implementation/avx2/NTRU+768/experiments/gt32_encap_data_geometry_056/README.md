# GT32-ENCAP-DATA-GEOMETRY-056

This experiment tests one narrow explanation for the exact-production Encap
debt observed by experiment 055:

> Does the physical placement of the five 1536-byte polynomial roles inside
> the existing Clean-GT stack frame cause a material part of the CBD,
> producer, or B3 cost?

The production Clean-GT source is not modified.  All profiles execute the same
`geometry_056_encap` symbol in the same ELF with the same 8128-byte stack frame,
arithmetic, calls, and memory-traffic volume.  A runtime profile changes only
which fixed 1536-byte slot is bound to each logical role.

| Profile | h | r | m | c | work | Purpose |
|---|---:|---:|---:|---:|---:|---|
| P0 | 0 | 1 | 2 | 3 | 4 | Current Clean-GT order |
| P1 | 0 | 1 | 2 | 4 | 3 | Exchange the two frontend/final-result slots |
| P2 | 1 | 2 | 3 | 4 | 0 | Rotate every role by one 1536-byte slot |

The three causal regions are:

- `CBD`: `poly_cbd1` only;
- `rprod`: `poly_cbd1 -> frontend -> N5`;
- `B3`: the real general-B3 call after production-shaped setup.

The full Encap path is also measured, but it is an attribution control rather
than an exact production promotion gate: selecting the mapping at runtime adds
common pointer-binding code which is absent from production.

## Reproduction

```sh
tools/build.sh
build/test_056
tools/run.py \
  --binary build/bench_056 \
  --launches 48 --cpu 1 \
  --output results/geometry-48.json
sudo -n true  # only if the local perf policy requires it
tools/run_pmu.py \
  --binary build/pmu_056 \
  --blocks 18 --cpu 1 \
  --output results/pmu-balanced-18.json
```

`run.py` pins every launch to CPU 1 and rotates all six profile orders.
`run_pmu.py` uses mirrored, balanced orders so each profile appears twice per
block and every profile occupies early and late process positions equally.

## Scope

This gate can reject or support *slot permutation inside the existing frame*.
It cannot reject structural lifetime changes which remove a polynomial, delete
a materialization, or shrink the frame.  Those change the working-set size and
instruction stream rather than merely relocating identical objects.

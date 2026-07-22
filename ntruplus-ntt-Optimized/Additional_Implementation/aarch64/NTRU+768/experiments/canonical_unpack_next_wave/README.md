# Canonical unpack next wave

This directory owns default-off scheduling experiments for one complete
canonical `poly_frombytes` chunk:

```text
96 canonical input bytes
  -> 64 unpacked 12-bit coefficients
  -> canonical-to-GT 8x8 transpose
  -> 16 fixed GT quartic-block stores
```

`U0` is a mechanical extraction of the current production chunk.  `U1` keeps
the same arithmetic, mask, permutation, direct store offsets, and ABI contract,
but presents the complete load/unpack/transpose/scatter DAG to Slothy.  It does
not alter production.

## Generate and optimize

```sh
python3 extract_unpack_chunk.py
python3 generate_unpack_chunk_candidate.py
SLOTHY_PATH=$HOME/slothy $HOME/slothy/venv/bin/python \
  optimize_unpack_chunk.py --timeout 1800
python3 generate_unpack_wrappers.py
python3 generate_full_unpack_candidate.py
```

## Correctness

```sh
make -B test_gt_canonical_unpack_chunk_candidate
make -B test_gt_canonical_unpack_full_candidate
```

The tests compare against `poly_frombytes_gt_canonical`, check untouched output
and guard bytes, and verify `x19-x28` plus the AAPCS64-required low halves
`d8-d15`.

## Pi 5 PMU, deferred while the host is offline

```sh
cd ../../../../../aarch64-bench
make -B bench_gt_canonical_unpack_chunk_pmu
make -B bench_gt_canonical_unpack_full_pmu
```

No speed claim or production promotion is allowed from the N1 solver estimate.

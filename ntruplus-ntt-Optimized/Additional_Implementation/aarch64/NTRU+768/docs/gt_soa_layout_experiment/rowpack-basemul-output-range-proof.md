# Rowpack Basemul Output Range Proof

Scope: decide whether an InvNTT32 row kernel variant can safely omit
row-input Barrett normalization when it consumes rowpack SoA basemul output.

## Result

The current raw `basemul` / `basemul_add` output convention is not enough to
remove row-input normalization.  It only inherits the `montgomery_reduce`
postcondition:

```text
raw basemul lane in [-3456, 3456]
```

The row kernel without entry normalization needs canonical centered
representatives:

```text
canonical row input lane in [-1728, 1728]
```

The opt-in convention that proves no row-boundary normalization is needed is:

```text
rowpack basemul canonical output:
  every stored basemul/basemul_add lane is barrett_reduce(raw_lane)
```

Under that convention, the stored output is in `[-1728, 1728]`, and Barrett is
idempotent on the stored range.  A no-input-normalization row kernel may consume
that convention directly.  This does not make normalization free; it moves the
cost from the row-kernel boundary into the basemul/add output convention.

## Proof

Facts from `ntt.c`:

- `montgomery_reduce(a)` returns a value in `[-q+1, q-1]`.
- For NTRU+768, `q = 3457`, so raw Montgomery output is in
  `[-3456, 3456]`.
- `barrett_reduce(x)` maps every `x` in `[-3456, 3456]` to
  `[-1728, 1728]`.
- `barrett_reduce(x) = x` for every `x` in `[-1728, 1728]`.

Therefore, if basemul/add stores `barrett_reduce(raw_lane)`, every row input
lane is already canonical and a row-kernel entry Barrett pass is redundant.

The current raw convention fails the canonical precondition.  The analyzer has
a deterministic counterexample:

```text
zeta = -1130
a = [-124, 1662, -319, 1203]
b = [2270, -546, -697, -478]
c = [0, 0, 0, 0]

basemul raw r[1]     = -1737
basemul_add raw r[1] = -1737
barrett_reduce(-1737) = 1720
```

So the raw convention can produce a lane outside `[-1728, 1728]`, even though
it is still congruent modulo `q`.

## Executable Gate

Run:

```sh
make analyze_gt_rowpack_basemul_output_ranges
make test_gt_rowpack_soa_invntt32_fullpath_canonical
```

This checks:

- Barrett is idempotent on `[-1728, 1728]`.
- Barrett maps the full Montgomery output interval `[-3456, 3456]` into
  `[-1728, 1728]`.
- The raw basemul and basemul-add counterexample above still reproduces.
- The canonical rowpack basemul/add convention feeds the no-entry-normalization
  InvNTT32 row kernel through product and product-add full-path roundtrips.

The canonical full-path gate uses
`kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.opt.S` by default.  This
variant keeps the same ABI symbol as the fused-normalization row kernel, but
removes the 12 entry-Barrett instructions and requires every rowpack
basemul/add output lane to be canonical before the row kernel is called.

Local `bench_gt_basemul_soa` sanity on this machine shows the cost of the
canonical output convention:

| target | median `cntvct` ticks/call |
| --- | ---: |
| `gt_basemul_rowpack_soa_ld1_intrinsic` | 5.219 |
| `gt_basemul_rowpack_soa_canonical_ld1_intrinsic` | 5.594 |
| `gt_basemuladd_rowpack_soa_ld1_intrinsic` | 5.016 |
| `gt_basemuladd_rowpack_soa_canonical_ld1_intrinsic` | 5.625 |

The no-entry row kernel scheduled Slothy output is 150 instructions with an
expected-cycle estimate of 37.  The fused-normalization scheduled output is 162
instructions with an expected-cycle estimate of 40.  These numbers are local
model signals, not a Pi5 benchmark.

## Integration Consequence

The current Slothy rowpack row kernel keeps fused row-input Barrett
normalization, so it is safe with current raw basemul/add output.  A future
no-entry-normalization row-kernel variant must be paired with the canonical
rowpack basemul/add output convention, and the convention must be part of the
public transformed-domain ABI.  The executable full-path gate now proves that
the canonical ABI is algebraically sound; the remaining question is whether the
basemul/add canonicalization cost is paid back by removing normalization from
the row kernel in the production pipeline.

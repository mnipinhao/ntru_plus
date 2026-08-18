# Wave31 InvNTT Branch Fold

This experiment corrects the inverse-tail boundary. It does not replace the
transform algebra and does not fold Basemul into InvNTT.  Starting from the
two branch vectors after inverse DFT3, it combines:

```text
global untwist -> branch merge -> normalization -> canonical branch halves
```

into one fixed 2x2 linear map per lane.

The existing algebraic endpoint first computes both untwists, then applies a
normalization product to the branch sum and a correction product to the branch
difference.  If `u0,u1` are the two untwist factors, `n` is normalization and
`k` is the merged branch-correction factor, the folded factors are:

```text
fL0 = u0 * (n-k) / R    fL1 = u1 * (n+k) / R
fH0 = u0 * (2k)  / R    fH1 = u1 * (-2k) / R

L = Mont(x0,fL0) + Mont(x1,fL1)
H = Mont(x0,fH0) + Mont(x1,fH1)
```

The factors are packed as `[branch0 | branch1]` YMM tables.  Two independent
YMM Montgomery chains produce the low and high canonical halves; each result
then needs one high-half extract and one add.  This is the intended Branch
Fold.  It leaves the inverse-32 and inverse DFT3 arithmetic unchanged.

The static tail count falls by 22 vector instructions per four-vector group,
or 264 instructions over all 12 groups.  For the original `[0,q]` research
boundary, the exact raw folded bounds are 3599 for normal input and 3605 for
the R^-1 input path.  The fused native producer has a wider contract; over the
complete signed-int16 input domain, the corresponding proved bounds are 5091
and 5053. One positive and one negative constant-time correction are still
sufficient to select a canonical result.  This is large enough to justify a
default-off ASM prototype but is not a Production or measured-performance
result.

Run `python3 analyze_branch_fold.py` to regenerate `branch_fold.json`.
The script exhaustively checks every `[0,q]` input for each unary Montgomery
composition, then checks deterministic branch pairs and exact centered
outputs after an exact canonical reduction.

One caveat is explicit: a single existing `center10` checkpoint does not
choose a unique representative for every congruent result.  The old and
folded tails can therefore differ by exactly `q` after that approximate
checkpoint even though their canonical results are identical. An ASM
prototype must either accept the existing lazy-output contract or append an
exact conditional correction when canonical representatives are required.
The static counts below are kept separate from the measured Intel PMU results.

## Implemented endpoints

All three symbols contain the same native three-child inverse-32 and DFT3
body. Only their postprocess differs:

```text
wave31_invntt_native_rminus1_algebraic_avx2
wave31_invntt_native_rminus1_branch_fold_lazy_avx2
wave31_invntt_native_rminus1_branch_fold_exact_avx2
```

The lazy endpoint returns a congruent result bounded by 5053. The exact
endpoint applies `abs -> compare -> signed-q correction` and returns the
unique centered representative in `[-1728,1728]`.

## Measured Intel PMU result

Same binary, CPU 3, balanced order, 200,000 calls and seven repetitions:

| Endpoint | cycles | IQR | instructions | IPC |
|---|---:|---:|---:|---:|
| R^-1 algebraic control | 1342.09 | 8.04 | 3821.94 | 2.848 |
| Branch Fold lazy | 1132.68 | 9.31 | 3398.94 | 3.001 |
| Branch Fold exact | 1238.45 | 6.89 | 3638.94 | 2.938 |
| materialized Official DAG | 865.10 | 9.20 | 2865.94 | 3.313 |

Relative to the same-body algebraic control, lazy saves 209.41 cycles and 423
instructions; exact saves 103.64 cycles and 183 instructions. Branch Fold is
therefore a real cycle win, not only a static-model win. It does not close the
remaining inverse gap to Official: lazy is still 267.58 cycles slower and
exact is 373.35 cycles slower in this isolated test.

The full Dec pairwise screens use the same R^-1 Basemul on both sides. They
show a 296.26-cycle median gain for lazy and a 132.48-cycle gain for exact.
Their IQR is much wider than the isolated screen, so these Dec numbers are
supporting evidence rather than the primary attribution.

Both full-KEM variants pass valid-input byte-for-byte Dec and 128 malformed
ciphertext cases. The existing Wave24 full KEM correctness suite also remains
green. No Production dispatch was changed.

## Reproduction

```sh
python3 analyze_branch_fold.py
make correctness linkage full-kem-correctness
python3 ../wave20_gt_contract_optimization/scripts/run_pmu.py \
  --binary build/wave31_same_binary --output results/isolated_pmu.json \
  --core 3 --iterations 200000 --repetitions 7 --warmups 100 \
  --operations inverse-materialized inverse-algebraic \
  inverse-fold-lazy inverse-fold-exact
```

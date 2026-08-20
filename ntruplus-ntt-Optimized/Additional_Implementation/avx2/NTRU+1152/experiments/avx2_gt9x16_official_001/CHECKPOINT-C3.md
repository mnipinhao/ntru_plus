# Checkpoint C3: Official-style persistent routing

C3 isolates the missing half of C2: keep pair-packed sum/difference state
across all four NTT16 layers instead of reconstructing coefficient-major rows
after every butterfly. It covers one GT row and two terminal coefficients;
shear, cross-row scheduling, NTT9, and BaseMul are deliberately outside this
microkernel.

The representation evolves exactly once per granularity:

```text
stage8 S/D
  -> stage4 vpunpckl/hqdq
  -> stage2 shift32 + vpblendd
  -> stage1 shift16 + vpblendw
  -> one coefficient-major reconstruction
```

The C2 comparison performs the same four pair-packed Montgomery chains but
reconstructs and re-compresses at each layer. Both variants use two input loads
and two output stores and are bit-exact with the verified C0 transform over
10,003 full-i16/boundary/random row pairs.

## Result

Nine pinned fresh launches, 201 samples per launch, CPU 1 on Intel Core Ultra
7 155H, GCC 15.2 `-O3 -mavx2`:

| One two-terminal row | C2 | C3 |
| --- | ---: | ---: |
| cycles | 72.619 | 50.413 |
| routing instructions | 44 | 18 |
| total instructions | 89 | 59 |
| `.text` bytes | 441 | 279 |
| Montgomery vector chains | 4 | 4 |
| loads / stores | 2 / 2 | 2 / 2 |

C3 is 30.6% faster and removes every `vpermq`, `vpshufd`, and `vpshufb` from
the row-pair body. Both leaves have zero calls, frame, stack references,
spills, and `vzeroupper`.

This reverses the interpretation of C2: terminal pairing is not rejected;
per-layer canonical reconstruction is rejected. C3 is selected for the next
experiment, which must integrate nine rows with skewed shear while retaining
persistent S/D state. Checkpoint D remains paused until that complete NTT16
pair path wins. Evidence is in
`results/c3-intel155h-20260820-001/c3-diagnostic.json` and remains local
diagnostic—not SUPERCOP promotion evidence.

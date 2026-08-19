# GT32 QBM wide-consumer gate 025

This experiment tests whether QBM i32 accumulators can skip the immediate
REDC32 boundary and directly enter the actual inverse consumer.  It does not
modify GT Clean and emits no assembly unless a complete arithmetic chain is
deleted.

## The actual first consumer

The first consumer is not an inverse-NTT twiddle.  It is the quadratic-to-
quartic `merge2` operation:

```text
sum  = plus + minus
high = Mont(plus - minus, merge_weight_mont)
      ↓
inverse size-2 identity butterfly
```

Consequently a generic `i32 -> inverse twiddle` fusion would skip a required
CRT merge and is not the real edge.

## Delaying REDC without changing merge2

The sum/difference transform is invertible and retains the same number of
independent output residues.  Forming it in i32 therefore still requires two
full REDC32 chains per original QBM vector, followed by the same weighted-
difference Montgomery chain.  This moves the reducers and expands the live
representation; it deletes no operation class.

## Direct `vpmulld` fusion

Before reduction the proved difference bounds are:

```text
c0: 23,887,872
c1: 47,775,744
```

The centered merge weights reach absolute value 1,726.  Products can reach
41,230,467,072 and 82,460,934,144, so a dense eight-lane `vpmulld` is not an
exact signed-i32 implementation.  Only 44/768 c0 lanes and 28/768 c1 lanes
are safe; mixed exceptional handling cannot provide a reusable full-vector
kernel.

`vpmuldq` is arithmetically legal but halves lane density and AVX2 has no
dense packed 64-bit modular reducer.  It does not delete the reduction class.

## Legal signed-word fused reducer

Writing a signed dword as

```text
x = low_s + 2^16 * (high_s + carry(low_s < 0))
```

gives an exact fused identity:

```text
REDC(low_s*w + high_s*(wR) + carry*(wR))
    == w*x*R^-1 (mod q).
```

The complete range remains signed-i32 safe (conservative absolute bound
57,814,157), and its REDC output remains signed-i16 safe (conservative bound
2,611).  The generator checks 3,842,880 boundary/random-weight cases.

However, the best known dense AVX2 sequence is ten instructions:

```text
2 shifts to derive the low-word carry
vpmaddwd word decomposition
vpand + vpaddd carry correction
5-instruction REDC32
```

Current `REDC32` followed by the merge Montgomery multiply is nine
instructions.  The legal fusion is one instruction longer and does not
shorten the dependency chain, before accounting for wide merge routing.

## Decision

Direct wide-consumer reduction under the current merge contract is a static
stop.  No ASM is emitted because all three direct variants either delete no
operation class, overflow, or are already longer than the current chain.

This does not close producer-native co-design.  Reopen when a producer can
directly form weighted sum/difference dots and thereby delete `merge2` or one
complete reducer, or when a narrowed/nonlinear representation or wider ISA
changes the arithmetic primitives.

## Reproduction

```sh
make check
```

# GT864 raw-Inverse-to-ternary consumer gate

Status: planned hard gate; no implementation or performance claim yet.

## Scope

This is a Decaps-only consumer gate. In the production NTRU+864 KEM call graph,
Inverse is used only by Decaps. The candidate may therefore specialize the
Inverse-output consumer for the ternary-message path; it does not need to
preserve a generic polynomial-multiplication consumer contract.

The current path is:

```text
GT raw Inverse output, natural-order R0, |x| <= 6912
  -> center864, output in [-1728,1728]
  -> poly_crepmod3, output in {-1,0,1}
```

The candidate path is:

```text
GT raw Inverse output, natural-order R0, |x| <= 6912
  -> gt864_crepmod3_raw, output in {-1,0,1}
```

`gt864_crepmod3_raw` must compute the exact centered residue modulo 3 without
materializing the centered-mod-q intermediate. Since q = 3457 = 1 (mod 3), if
`k` is the unique value in {-2,-1,0,1,2} for which
`x - k*q` lies in [-1728,1728], the candidate may reduce `x - k` modulo 3.

The exact quotient regions are:

| Raw input x | k |
| --- | ---: |
| [-6912,-5186] | -2 |
| [-5185,-1729] | -1 |
| [-1728,1728] | 0 |
| [1729,5185] | 1 |
| [5186,6912] | 2 |

The previously rejected P3-B producer-side centering is not this candidate.
P3-B serialized full mod-q centering into the Inverse terminal scatter. This
gate retains a batched full-vector consumer unless a new Inverse output ABI is
separately proven and measured.

## Hard gates

1. Reconfirm that every production Inverse output lane is bounded by
   `[-6912,6912]` for all reachable Decaps producers.
2. Exhaustively verify the threshold boundaries, especially
   `+/-1728/1729` and `+/-5185/5186`.
3. Author a four-vector common DAG.
4. Allocate and schedule without spill.
5. Compare exactly against `center864 -> poly_crepmod3`.
6. Pass exact in-place/alias testing.
7. Pass malformed-ciphertext testing and the complete KAT.
8. On Pi 5, compare the complete `Inverse + conversion` boundary.
9. Make the final decision from Decaps cycles, not the standalone consumer.

## Required contract evidence

- Input layout: natural coefficient order.
- Input representation: signed int16, R0.
- Input range: closed reachable bound, provisionally `|x| <= 6912`.
- Output layout: natural coefficient order.
- Output representation and range: signed int16 in `{-1,0,1}`.
- Control flow and addresses: secret-independent.
- Memory: in-place operation, one consumer read and one consumer write per
  coefficient; no coefficient scratch and no added memory pass.
- Oracle: byte-exact equality with the current
  `center864 -> poly_crepmod3` path.

# Checkpoint G1C-M3 full-path repair-placement proof

The requested D4-tail fusion is not safe under the declared BMScale contract.
This is a proof failure, not a benchmark regression: with independent raw
BMScale lanes in `[-13824,13824]`, D1 is safe, but a D2 large-plus-large edge
has the exact interval `[-55296,55296]`. A D4 repair executes too late to
protect that operation.

The earlier M3C2-P result remains valid only conditionally: if valid signed-i16
D4 operands have already been produced, reducing both D8 inputs is sufficient.
It does not establish that the lazy path can safely reach D4.

As a constructive control, the oracle also proves that applying
Montgomery-by-identity to the D1 large/sum stream closes the signed-i16 range
through D2, D4, and D8 for every row. The identity constant is `R mod q`, so
`Mont(x,R)=x (mod q)` and the stream's Montgomery exponent is preserved.

Consequently no D4-tail assembly or C0/C1/C2 timing was produced: timing a
path whose `vpaddw` can wrap before its repair would produce an invalid result.
The next valid checkpoint is a fused D1-large repair, followed by the original
three-way accounting. It is deliberately not a D4-tail fusion.

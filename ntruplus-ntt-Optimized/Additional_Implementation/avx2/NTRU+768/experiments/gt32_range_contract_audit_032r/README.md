# GT32-RANGE-CONTRACT-AUDIT-032R

032 found an executable value of 12882, disproving the historical
`Forward<=10788` / `highrange12699` naming as a current mathematical contract.
The regenerated current-executable proof bounds Encap `B3+m_hat` by 20296.

This audit verifies the exact selected Q24 reduction sequence exhaustively for
every scalar value in `[-20296,20296]`, then runs the production assembly packer
for each value and checks all 768 serialized coefficient slots.

The exact reducer is:

```text
t = vpmulhrsw(x, 9)
y = x - t*3457
z = y + (y < 0 ? 3457 : 0)
```

Result:

- 40,593 scalar-domain cases pass;
- 40,593 x 768 executable packet/slot cases pass;
- centered reducer output is `[-2739,2739]`;
- canonical output is exactly `[0,3456]` and equals `x mod 3457`;
- the same reducer also passes all 65,536 signed-int16 inputs, producing
  centered output `[-3291,3291]`.

Therefore the historical function names may remain as ABI names, but must not
be used as current range invariants. The proven Encap input contract is now
`|x|<=20296`; the reducer itself is valid on the full signed-word domain.

GT Clean is not modified.

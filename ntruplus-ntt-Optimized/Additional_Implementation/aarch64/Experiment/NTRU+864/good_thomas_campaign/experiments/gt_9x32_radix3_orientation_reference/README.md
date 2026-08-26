# NTRU+864 oriented radix-3 NTT9 reference

## Bounded question

Can the paper's cyclic orientation of one first-layer `B3` and one second-layer
output group replace the direct nine-point Horner stage in the frozen NTRU+864
9-by-32 Good-Thomas reference without changing its public GT representation?

The experiment applies only the dense 9-point idea. NTRU Prime-specific zero
patterns, 10-point sparse transforms, length-16 TMVP base cases, auxiliary CRT,
and `uzp1` narrowing are outside this experiment because NTRU+864 does not share
their prerequisites.

## Candidate data flow

For each 32-point column and cubic branch, the frozen Stage32 produces `T[s]`.
The candidate makes the column twist explicit:

```text
f[s] = T[s] * lambda^s
F[row] = sum_s f[s] * eta^(row*s)
```

It then evaluates the NTT9 as six `B3` butterflies. The oriented form keeps four
inter-level multiplications but uses only `eta` and `eta^-1`, rather than three
distinct constants `eta`, `eta^2`, and `eta^4`.

The output is written back to the frozen canonical row-major GT layout. This
first reference therefore proves the internal orientation identity; it does not
yet carry a non-canonical `(P,D)` representation through BaseMul and InvNTT.

## Run

```sh
make check
```

No benchmark or Production claim is authorized by this experiment.

# NTRU Prime AVX2 pipeline transfer audit (129)

This experiment studies the NTRU Prime truncation AVX2 implementation as a
**whole dataflow contract**, then checks whether a direct mechanism remains
unexplored in the current NTRU+768 GT Clean implementation.  It does not copy
assembly, modify production, or claim cycles from static instruction counts.

Primary source files inspected on 2026-09-15:

- [`radix_3x2.S`](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation/blob/main/avx2/avx2/radix_3x2.S)
- [`__avx2.c`](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation/blob/main/avx2/avx2/__avx2.c)
- [`basemul.S`](https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation/blob/main/avx2/avx2/basemul.S)

Run the local contract audit with:

```sh
make check
```

The generated machine-readable result is
[`generated/transfer_matrix.json`](generated/transfer_matrix.json).

## What the reference actually does

The useful unit is not `radix_3x2.S` alone.  `_mulcore` constructs this path:

```text
src1: Rader17 -> radix-3x2 + pre-twist -> twist+transpose -> leaf batches
src2: Rader17 -> radix-3x2 + pre-twist -> twist+transpose -> leaf batches
                                                     |
                                  cyclic/negacyclic FFT16 BaseMul
                                                     |
result: inverse transpose+twist -> inverse radix-3x2 -> inverse Rader17
                                                     |
                           final ring fold + FINAL_SCALE_Rmod
```

There are three concrete implementation ideas:

1. The GT permutation is encoded in the six load/store offsets of
   `radix_3x2.S`; it is not paid as a separate permutation pass.
2. `twist_transpose_pre/post` makes the leaf multiplication layout once at the
   entrance to the multiplication island and undoes it once at the exit.
3. `_mulcore` owns two inputs, multiplication and inverse together, so a
   single coefficient endpoint can absorb the accumulated scale and ring fold.

## Direct comparison with NTRU+768

| NTRU Prime mechanism | Current NTRU+768 equivalent | Result |
|---|---|---|
| GT offsets hidden in memory addressing | `FRONTEND_WIDE_ITER_BODY` and `DFT3_WIDE_STORE` directly deposit six GT branches | already absorbed |
| radix-3x2 fused with twist | top split, twist/Montgomery work, DFT3 and deposit share the selected wide frontend pass | already absorbed |
| one transpose into leaf-lane batches | TILE4 is kept through NTT32, then M/P coefficient planes are chosen for real consumers | already absorbed and more caller-specific |
| leaf-native multiplication | M-native general/scale B3 and P-native BaseInv/F0xJ1 product | already absorbed |
| inverse transpose/post-twist | M-native inverse plus the Late-SoA 063--067 seam | already tested |
| one final scale/fold | typed `e=0`, `e=-1`, J1 and SP1 endpoints | no single common KEM endpoint |
| two Forward + BaseMul + inverse workspace | no exact standard KEM caller match | graph mismatch |

The apparent similarity is therefore real, but most of it describes the
architecture GT Clean already converged to:

```text
transform-friendly TILE4
        -> caller-specific M or P
        -> native BaseMul/BaseInv/inverse/Q24 consumer
```

This is stricter than copying the reference transpose.  M and P are typed by
consumer, leaf order and Montgomery exponent; they are not a universal
"transposed NTT" buffer.

## Why the shared `_mulcore` cannot be copied into a KEM caller

The reference earns its strongest contract because it owns a complete
coefficient-to-coefficient multiplication.  NTRU+768's real callers differ:

- **Encap** has two Forward transforms, but `r` must be serialized and hashed
  before `m` exists, and the endpoint is `B3 + m -> Q24`, not inverse NTT.
- **Decap first product** has `scale B3 -> inverse`, but both operands arrive
  from serialized-key/ciphertext decode already in M; there are not two
  Forward producers to fold into a shared pre-transpose.
- **Keygen** sends Forward results into BaseInv, two products and serialized
  P outputs; there is no common inverse/coefficient endpoint.

Consequently, creating a new generic `2F+B+I` private workspace would
benchmark a graph that the standard KEM does not execute.

## Prior experiments that already adjudicate the tempting ports

- 030 and 061--067 cover persistent/progressive coefficient-plane placement
  and the B3-to-inverse seam.
- 082--083 cover the immediate dual terminal for Encap `r`: retain M for B3
  while also creating the wire/hash representation.
- 084--105 cover Encap caller topology, virtual sum, persistent B3-input
  presentation and QL2 convergence layouts.
- 072--078 and 026--029 cover moving normalization/scale across product and
  inverse/serializer boundaries.

The NTRU Prime source validates the *reason* those were the right experiment
units; it does not reopen them.

## Decision

```text
reference architecture:       applicable and already substantially absorbed
new direct transfer:          none
new assembly/benchmark gate:  not justified
production modified:          no
```

This is not a claim that no future NTRU+768 redesign can use the reference.
Reopen only with a new consumer seam that deletes a complete materialization
or reduction beyond M/P/E0V/QL2, a genuinely different leaf factorization, or
an actual coefficient-to-coefficient polymul API selected as the measured
target.  Merely moving the GT permutation, transpose, twist, or final scale to
another existing boundary would repeat a measured search class.

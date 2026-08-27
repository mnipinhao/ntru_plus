# ENCAP MA2 ciphertext egress H4-M3 ASM

## Outcome

H4-M3 produced two real, namespaced AVX2 machine objects:

- `ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1`;
- `ntruplus1152_exp001_encap_h4_m3`.

The caller-wide scale-1 gauge and the live H3 terminal are correct.  The first
M2 packed-egress lowering used the wrong coefficient namespace, so no
benchmark is authorized yet.  The subsequent M2B exact search shows that the
abstract M2 same-lane wire-pair model itself was valid.

## Scale-1 producer

The producer keeps persistent-AoS, Natural-Q, T0-beta, all routing, all
reductions, and the output ABI frozen.  It replaces each row alpha by the M0
caller-wide scale-1 factor.  Row zero now also needs a Montgomery chain.

Linked delta per forward versus the scale-4 T0-beta producer:

| instruction | delta |
| --- | ---: |
| `vpmullw` | +8 |
| `vpmulhw` | +16 |
| `vpsubw` | +8 |
| routing / loads / stores | 0 |

This is exactly eight added Montgomery chains.  The symbol is 32-byte aligned,
has no call, branch, frame, spill, or `vzeroupper`, and is 15,489 text bytes.

The semantic test checks every output cell using:

```text
canonical(scale4) == canonical(4 * scale1)
```

over zero, structured boundary, and 1003 random-small caller inputs.

## Live terminal and intentional scratch

`ntruplus1152_exp001_encap_h4_m3` retains the H3 decode/validate/MA2 DAG.  Each
of the 72 former raw scale-4 stores is replaced by:

```text
three-instruction Barrett
sign canonicalization
aligned canonical-i16 scratch store
```

There is no terminal `inv4`.  The 2304-byte scratch contains exact canonical
Natural-Q scale-1 MA2 planes and is the only intentional materialization.
All 72 scratch vectors compare bit-exactly with the independently executed H3
scale-1 raw result after scalar canonicalization.

The ABI is:

```c
int ntruplus1152_exp001_encap_h4_m3(
    uint8_t ct[1728], const uint8_t pk[1728],
    const int16_t r_scale1[1152], const int16_t m_scale1[1152],
    int16_t scratch[1152]);
```

All 54 PK loads complete before the first ciphertext store.  Exact `pk == ct`
and both tested 16-byte partial-overlap directions therefore pass.

## First M3 lowering failure

The failed helper treated adjacent Official physical coefficient IDs as a
serializer pair.  The exact map gives this namespace counterexample:

```text
MA2 vector 20 lane 15 -> Official coefficient 0
MA2 vector 21 lane 15 -> Official coefficient 16
MA2 vector 20 lane 14 -> Official coefficient 1
```

But ciphertext pairing is keyed by serialized wire coefficient.  Wire pair 0
is physical coefficients 0 and 16, so:

```text
vpunpckwd(vector20, vector21)
```

forms the correct wire pair `(wire 0, wire 1)`.  The incorrect first helper
instead paired adjacent lanes within vector 20 because it sorted by physical
IDs 0/1.  The first nonzero ASM differential exposed this at ciphertext byte
1.  Canonical scratch remained exact, isolating the error to that lowering.

The generated 1502-instruction M2 ledger remains a conditional symbolic
estimate.  Its `72 vpunpckwd + 72 vpmaddwd` primitive is ownership-valid only
when the operands are selected by wire ID.  It must not be benchmarked until
that exact lowering exists and passes the byte differential.

## Exact-ownership correctness control

To finish the machine correctness gate without hiding the error, H4-M3 uses
the proven Natural-Q H1 coefficient reconstruction and pack after the H4
terminal.  Its `inv4` and sign-canonicalization instructions are removed,
because the H4 terminal already produced canonical scale-1 values.

The resulting linked H4 leaf has:

| item | linked value |
| --- | ---: |
| instructions | 5189 |
| text | 32,996 B |
| rodata | 5,408 B |
| terminal Barrett vectors | 72 |
| canonical scratch stores | 72 |
| exact-ownership scratch loads | 288 |
| ciphertext stores | 54 |
| terminal `inv4` | 0 |

This is a correctness control, not the intended H4 packed-egress winner.

## Correctness and ABI gates

Passed:

- scale-1 producer semantic differential;
- exact 72-vector canonical scratch differential;
- exact 1728-byte comparison against Official
  `poly_ntt -> poly_basemul -> poly_add -> poly_tobytes`;
- zero, structured boundary, and 1003 random valid inputs;
- Official decoder acceptance on structured and 1003 random byte strings;
- `pk == ct` and both tested partial overlaps;
- input immutability and scratch/output canaries;
- 32-byte entry/constant alignment;
- call-free, branch-free, frame-free, spill-free, `vzeroupper`-free objects.

## Decision

The M0 caller-wide scale gauge and H3 terminal realization are closed.  The
M2 packed-egress machine lowering is reopened.  No serious benchmark and no
native KEM integration is authorized from this checkpoint.

H4-M2B rebuilds terminal-to-wire ownership from the exact direct map and
separates physical and wire coefficient namespaces.  The H1-based H4-M3
object remains the correctness control for the next exact schedule, not a
promotion candidate.

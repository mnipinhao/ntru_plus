# ENCAP-H-DECODE-NATURAL-Q-MAP

## Question

Can the public-key decoder materialize the frozen Natural-Q MA2-native `h`
ABI directly, while preserving the exact NTRU+ wire-format and rejection
semantics?

This is a representation/decoder-contract map.  It adds no ASM and makes no
performance claim.

## Caller graph

Official encapsulation has one successful-value consumer of `h`:

```text
pk bytes
-> poly_frombytes(&h,pk)
-> canonicality branch
-> poly_basemul(c,h,r)
```

The cumulative GT caller also has exactly one successful-value consumer:

```text
pk bytes
-> Official poly_frombytes(&h,pk)
-> canonicality branch
-> Natural-Q h formation inside scale-4 MA2
```

There is no second hash, serializer, or recovery consumer of the decoded `h`.
The error branch consumes only the decoder return value.  A caller-private
Natural-Q decoder is therefore semantically possible without reproducing the
earlier `r` dual-consumer problem.

## Exact ownership

`generated/encap-h-decode-natural-q-map.json` records all 1152 paths:

```text
PK byte/bit fragments
-> serialized 12-bit coefficient
-> Official physical cell/vector/lane
-> (branch,p,q,terminal coefficient)
-> Natural-Q vector/lane
```

The map composes the probed Official `physical_to_serialized` permutation with
the frozen `ntruplus1152_exp001_qnat_h_source` permutation.  Both maps are
bijections.

The decisive geometry result is:

```text
Official decode blocks:       9
coefficients per block:       128
live decoded source vectors:  8
Natural-Q output vectors:     72
block-local output vectors:   72 / 72
cross-block output vectors:   0 / 72
```

Every group of eight Natural-Q vectors can be formed from the eight decoded
vectors already produced by one 192-byte `poly_frombytes` iteration.  No
cross-block register retention or scratch array is required.

## Extensional decoder proof

The independent byte-level model decodes the same contiguous 12-bit public-key
stream through two paths:

```text
Official bytes -> Official physical h -> frozen Natural-Q permutation
Official bytes -> direct Natural-Q h
```

It checks:

- all 4096 possible 12-bit values;
- values 3456, 3457, 3458, and 4095 at every one of 1152 positions;
- 1152 multiple-invalid cases;
- 1003 deterministic random 1728-byte strings.

For every case, both paths accept exactly when every decoded coefficient is
less than 3457.  For accepted inputs, the 1152-cell Natural-Q outputs are raw
exact.  The wire bytes, accepted set, error return, and mathematical `h` are
unchanged.

## Movement accounting

The current post-decode edge is:

```text
Official decoder:
    54 PK vector loads
    72 Official-layout stores

Natural-Q formation inside MA2:
    144 h vector loads
    360 routes
    0 intermediate stores
```

A conservative direct-decoder realization is:

```text
Direct decoder:
    same 54 PK vector loads
    <=360 Natural-Q formation routes on live decoded vectors
    72 Natural-Q stores

Preprojected-h MA2:
    72 native h vector loads
    0 h-formation routes
```

Therefore the MAP-level guaranteed delta is:

```text
vector loads:   -72
vector stores:    0
routes:           0
scratch:          0
```

This corrects the optimistic interpretation that the complete 360-route
projection necessarily disappears.  The conservative candidate relocates
those routes from MA2 into the decoder and permanently removes 72 duplicated
loads.  Some formation routes may later fuse with the existing 216-route
Official unpack network, but that is an ASM/linked-object result, not a MAP
claim.

The 2304-byte `h` materialization remains necessary because public-key decode
occurs before hashing, `r`, and `m` production; keeping eight decoder vectors
live until MA2 is not a realistic caller contract.  The optimization changes
the materialized ABI, not the existence of the resident `h` buffer.

## Authorization

The map authorizes one paired namespaced machine prototype:

```text
ntruplus1152_exp001_poly_frombytes_h_natural_q
+
ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4_preprojected_h
```

The decoder processes one 192-byte block, preserves the Official validation
accumulator, forms eight Natural-Q vectors from its eight live decoded vectors,
and stores directly to the existing aligned 2304-byte `h` buffer.  The MA2
entry changes only its `h` input ABI and loads one preprojected vector per
plane; its arithmetic, scale, reductions, `r/m` ABI, and output ABI stay
frozen.

Before pricing, the prototype must pass invalid-input accept/reject
differential, raw Natural-Q output differential, linked call/frame/spill/
alignment/constant-time audit, and prove no scratch or Official-layout
intermediate.  Benchmark and native KEM integration are not yet authorized.

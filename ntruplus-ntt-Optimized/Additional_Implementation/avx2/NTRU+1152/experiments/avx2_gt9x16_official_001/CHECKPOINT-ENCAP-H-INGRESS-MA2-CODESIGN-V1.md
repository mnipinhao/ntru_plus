# ENCAP-H-INGRESS-MA2-CODESIGN-V1

This checkpoint keeps the direct Natural-Q decoder as an H1 machine control,
but changes the research target to PK-byte ingress co-designed with MA2.  It is
not a benchmark or a KEM-promotion result.

## H1 control closure

The namespaced assembly symbols are:

```text
ntruplus1152_exp001_poly_frombytes_h_natural_q
ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4_preprojected_h
```

The decoder performs nine unrolled 192-byte Official-equivalent decode and
validation waves.  Each wave forms its eight exact Natural-Q vectors from the
eight live decoded vectors and stores them directly; it never materializes a
full Official-layout polynomial.  Exhaustive 12-bit values, all four boundary
values at all 1152 positions, 1003 random byte strings, input immutability,
canaries, and raw Natural-Q output all pass.  The preprojected-h consumer is
raw bit-exact with the frozen scale-4 MA2.

The linked H1 decoder has 54 PK loads, 72 Natural-Q stores, and the expected
360 formation routes.  Relative to frozen MA2, the preprojected consumer
removes 72 h loads and 360 routes while retaining exactly the same Montgomery
and add/sub arithmetic.  Both leaves are 32-byte aligned, call/frame/spill
free, and contain no `vzeroupper`.  H1 retains a 2304-byte h object and is a
control, not the desired architecture.

## Caller reorder legality

For the actual cumulative caller, h has one successful-value consumer: MA2.
`hash_f`, r sampling, the r forward/hash fanout, SOTP, and the m forward use PK
bytes but not decoded h.  `crypto_kem_enc` consumes randomness before entering
the deterministic encapsulation body, so moving validation later does not
change randomness consumption.

To preserve even the current incidental `pk`/`ct` overlap behavior, a late
decoder must not use `ct` as the r-serialization/hash scratch before consuming
all PK bytes.  The plan redirects that identical r serialization into storage
reusing the dead 2304-byte h frame slot.  Final ciphertext is written only
after all nine PK blocks are consumed.  An invalid public key may cause more
work, but the work depends only on public input; the externally visible result
remains zero ciphertext, zero shared secret, and return value 1.

## Exact block cut

Every decode block supplies two complete quartic MA2 tiles:

```text
192 PK bytes -> 128 decoded coefficients -> 8 decoded YMM vectors
             -> 2 complete (branch,p) MA2 tiles
```

There are nine such cuts and no cross-block h value.  Both tiles reuse all
eight decoded source vectors, which is the main register-allocation constraint.

The naive schedule needs at least 18 YMM registers: eight decoded sources,
four formed h vectors, four r vectors, and two temporaries.  It is rejected.
An output-accumulator wavefront has a zero-slack upper bound of 16: eight
decoded sources, four output accumulators, one formed h, one r operand, and two
routing/Montgomery temporaries.  This is feasible on paper but is not yet a
machine schedule; it requires an exact register allocation and linked
zero-spill proof.

## Architecture decision

The remaining architectures are:

| ID | h presentation | resident h | status |
| --- | --- | ---: | --- |
| H0 | Official layout plus projection | 2304 B | current control |
| H1 | exact Natural-Q | 2304 B | implemented machine control |
| H2 | decoder-native persistent H-ABI | 2304 B | fallback search |
| H3 | live decode-to-MA2 wavefront | 0 B | preferred target |

Natural-Q remains frozen for r/m, but h may use decoder-native vector, lane,
half, block orientation, and scale if MA2 absorbs them while preserving exact
semantic owner and external bytes.  Constant-table reindex alone is not
sufficient when h and r lane owners differ.

The next checkpoint is one exact 192-byte/two-tile H3 schedule.  It must prove
validation accumulation, the overlap-safe scratch plan, 16-YMM allocation,
zero spill, unchanged MA2 arithmetic/output, and an explicit half-resident
128-byte fallback.  No performance measurement or native KEM run is authorized
yet.

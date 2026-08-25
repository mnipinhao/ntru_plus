# Checkpoint F0-MA-MAP

## Outcome

This checkpoint closes the exact semantic map from the selected paper-adjusted
F0 forward representation to the pinned NTRU+1152 encapsulation consumer.  It
does not select an arithmetic circuit, authorize assembly, or make a
performance claim.

The pinned SUPERCOP caller corrects an earlier path assumption.  Encapsulation
is:

```text
poly_frombytes(h, pk)
F0(r)
F0(m)
poly_basemul(c, h, r)
poly_add(c, c, m)
poly_tobytes(ct, c)
```

There is no inverse transform in this caller.  `h` is the resident public-key
operand, while only `r` and `m` are fresh forward-transform producers.  The
BMScale-to-inverse work from G1C belongs to decapsulation and remains a
separate consumer path.

## Exact component map

The common semantic coordinate is
`(branch, p, q, terminal_coefficient)`.  YMM packing, persistent stream
orientation, local coefficient-plane formation, and the serialization layout
are caller-private physical choices.

The paper-adjusted F0 physical-P order is:

```text
0, 3, 6, 1, 4, 7, 8, 2, 5
```

The earlier pipeline-layout oracle used:

```text
0, 3, 6, 1, 4, 7, 2, 5, 8
```

Consequently physical rows 6, 7, and 8 must be joined to Official by semantic
`(branch,p,q,j)`, never by raw row index.  The generated map proves complete
bijections among all 1,152 semantic owners, F0 i16 positions, and Official i16
positions.  It records all 72 F0 vectors, every lane's exact F0 range, its
quartic factor, and its Official position without changing the current
bit-reversed NTT16 lane order.

## Scale and caller boundary

`h` is resident at transform scale 1 and Montgomery exponent 0.  F0 produces
`r` and `m` at transform scale 4 and Montgomery exponent 0.  Therefore both
`h*r` and `h*r+m` are at scale 4.  Ciphertext serialization expects scale 1,
so the inverse-four factor `2593 mod 3457` must be absorbed by the candidate
finalizer or a scale-aware serializer.  A standalone normalization pass is
not an acceptable production design.

## Symbolic candidates

Four exact circuits remain alive for scheduling analysis:

| ID | Physical boundary | Quartic circuit | Base-field bilinear rank |
| --- | --- | --- | ---: |
| MA0 | Explicit F0-to-Official adapters | Existing weighted schoolbook control | 16 |
| MA1 | Direct persistent F0 storage | Weighted schoolbook | 16 |
| MA2 | Local 16-leaf coefficient planes | Weighted schoolbook | 16 |
| MA3 | Local 16-leaf coefficient planes | Even/odd three-quadratic Karatsuba | 9 |

MA3's exact weighted output was checked against schoolbook for all 288 lane
factors with 16 deterministic random cases each, or 4,608 checks.  Rank alone
cannot select it: its extra additions, lambda schedule, resident-`h`
projection, range repairs, register pressure, and serializer debt are not yet
priced.  Static elimination of MA0--MA3 is therefore forbidden.

## Next gate

`F0-MA-SCHED` must derive, for two or three retained candidates:

1. the exact resident-`h` projection schedule;
2. the exact output-to-ciphertext-serializer schedule, including inverse-four;
3. signed-i16 ranges at every pre-operation point; and
4. a linked peak-YMM/register-spill plan.

Only after those proofs may a narrow assembly island be built.  Its primary
benchmark boundary is the complete caller segment:

```text
F0(r) + F0(m) + resident h -> MulAdd -> ciphertext serialization
```

A BaseMul-only timing cannot select the production candidate.  Formal
promotion still requires the pinned SUPERCOP native KEM and fixed-ELF paired
gates described by the branch workflow.

## Reproducible artifacts

- `generated/f0-ma-consumer-map.json`
- `generated/f0-ma-symbolic-synthesis.json`
- `tools/generate_f0_ma_map.py`
- `tests/test_f0_ma_consumer_map.py`
- `tests/test_f0_ma_symbolic_synthesis.py`

# GT32 Encap M-prime layout generator (070)

This default-off gate asks whether an Encap-specific leaf order can retain the
current M coefficient-plane representation while making all twelve Q24 packet
groups instances of one uniform loop body.

It is a generator-only experiment. It does not modify GT Clean and it does not
contain an executable candidate.

## Fixed contract

The search preserves:

- four coefficient planes and sixteen independent quartic leaves per block;
- the current six-tile, two-q4-block M storage size;
- the current B3 arithmetic, scale, range and Montgomery convention;
- the exact 48-packet canonical Q24 byte stream.

It may change only the order of the twelve M blocks, the sixteen leaf lanes
inside each block, corresponding `lambda`/`lambda_qinv` table indexing, and
the Forward terminal store destinations/deposit masks. B3 is accepted only
when its change is a table relabel. Forward routing is charged to M-prime; it
is not hidden at the Q24 edge.

## Search

The uniform serializer family is:

```text
four M coefficient planes
  -> current 4x16 transpose network
  -> one common permutation of the four transpose outputs
  -> one common vpermq choice per output packet
  -> four packets
```

This is `24^5 = 191,102,976` possible templates. The generator evaluates all
twelve production templates as seeds plus 512 deterministic random starts by
coordinate descent. Static cost selects candidates only; it is not a cycle
result or a universal AVX2 lower bound.

The current Forward terminal's `FR_PACKED_TO_PLANES` network is modeled
symbolically. For every M-prime block, the gate checks whether changing the
four existing `vpshufb` masks can absorb its leaf permutation. Non-absorbed
routes are classified against one- and two-operation one-source AVX2 families.

## Result

The search found a mathematically valid M-prime layout:

- Q24 can use one uniform four-packet body in a twelve-iteration loop;
- B3 arithmetic is unchanged and needs only relabeled lambda tables;
- block order can be emitted by changing tile store destinations;
- all block, lane and lambda-source maps are bijections.

It did **not** find the required zero-extra producer trajectory:

```text
12 M-prime blocks
  4  absorb into current Forward deposit masks
  8  require block-dependent lane routing
```

For the best searched template, the model totals 24 extra operations per
degree plane across the blocks, or 96 vector routing operations per Forward.
Encap has two such Forward polynomials, so it would add about 192 modeled
vector routing operations before receiving the uniform-Q24 benefit.

```text
uniform-Q24 M-prime representation:        EXISTS
B3 table-relabel-only compatibility:       PASS
current shared Forward zero-extra landing: FAIL in searched family
```

Therefore no ASM is written. This is not a rejection merely because an
instruction estimate increased. It fails the gate's architecture premise:
the consumer layout must be available through table/store relabel rather than
through a new block-dependent producer network.

## Scope and reopening

This does not prove every AVX2 uniform serializer impossible. The `24^5`
family was searched heuristically, and route class 3 means only "outside the
modeled two-operation one-source family."

Reopen only if a jointly redesigned S4/S5 Forward terminal can form the eight
block-dependent lane orders inside movement already required by the transform.
Another Q24 template sweep, common global lane relabel, or standalone
post-Forward permutation does not change the identified producer cost.

## Reproduce

```sh
make check
```

Generated evidence:

- `generated/search.json`: search definition, best template, route classes,
  store schedule and decision;
- `generated/mprime_lanes.csv`: exact M-prime-to-current-M lane and lambda
  relabel map.

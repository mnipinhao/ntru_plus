# GT32 TM/Q24 economics gate

Experiment: `GT32-TM-Q24-ECONOMICS-003`

This is an isolated generator-only continuation of
`GT32-PERSISTENT-TWIDDLE-MAJOR-002`. It does not modify GT Clean or emit an
assembly symbol.

## Question

002 proves that persistent TM passes the Forward/B3 static closure but cannot
make Q24 zero-debt. This gate asks the correct relaxed question:

```text
How much incremental Q24 routing debt is required,
and can two Forward savings (-216 instructions) pay for it?
```

`D` and `E` below are incremental costs relative to the current Q24 decode and
encode paths, not the total serializer cost.

## Result 1: exact post-Q24 adapter economics

The generator performs a breadth-first exact search over paired
`vpunpck{l,h}{wd,dq,qdq}` and `vperm2i128` operations. Per degree, the first
exact `M -> M_TM` route appears at five paired operations, or 10 instructions.
The inverse route has the same minimum.

```text
10 instructions/degree
x 4 degrees/tile
x 6 tiles/polynomial
= 240 instructions/polynomial
```

Therefore:

```text
D = 240
E = 240
D + E = 480
Encap net = -216 + 480 = +264 instructions
```

This constructive adapter is a static loss. It also consists entirely of
shuffle instructions, including 48 cross-128 operations per direction.

## Result 2: relaxed direct packet route

The direct route search is deliberately optimistic:

- packet execution order is arbitrary;
- all 24 qword permutations are treated as free;
- decode and encode need not share an adapter;
- uniform eight-register networks are searched through six layers, or
  48 instructions/tile.

No route is found. The 48 Forward terminal orders are not tested as unrelated
cases: the generator proves they form one exact symmetry orbit:

```text
3! permutations of three unpacked lane bits
x 2^3 XOR orientations
= 48 orders
```

The network search already exhausts the matching unit/bit orders and
reverse/swap orientations, so one representative covers the orbit.

Uniform layers cost eight instructions. Since no route exists through 48, the
next possible cost is at least 56/tile. Relative to current Q24's 24/tile:

```text
increment >= (56 - 24) x 6 = 192 per direction
D + E >= 384
Encap net >= -216 + 384 = +168
```

Thus the complete uniform layered direct-packet family is also a static loss.

## Result 3: split-128 terminal

Pure split stores/loads do not close the route. Every destination 128-bit half
depends on both source registers and both source halves. Destination addresses
alone therefore cannot absorb the M_TM group bit.

This does not rule out a nonuniform network that combines split memory
operations with additional shuffles. It rules out split-128 as a free repair.

## Decision

```text
Persistent TM N32/B3:       qualified by 002
Q24 zero-debt:              stopped by 002
current-Q24 plus adapter:   static loss (+264 net)
uniform direct packet:      static loss (>= +168 net)
pure split-128:             insufficient
assembly:                   stop for tested relaxed families
```

This is still not the statement “TM failed.” It is:

> Persistent TM has real Forward headroom, but neither the exact adapter nor
> the complete uniform packet family can amortize Q24 in standard Encap.

Reopen for a nonuniform packet atom with `D+E < 216`, a caller with more than
two amortized Forward credits, a non-Q24 internal island, or a different ISA.

## Reproduce

```sh
make check
```

The generated JSON includes exact paths, state counts, symmetry proof, split
half dependencies, cost vectors, source hashes, and explicit non-conclusions.


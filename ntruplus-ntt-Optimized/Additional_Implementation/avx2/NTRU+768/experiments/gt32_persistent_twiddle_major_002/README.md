# GT32 persistent twiddle-major gate

Experiment: `GT32-PERSISTENT-TWIDDLE-MAJOR-002`

This is an isolated generator-only experiment. It does not modify GT Clean,
its selected symbols, build files, tables, or production selector.

## Question

The earlier `GT32-TWIDDLE-MAJOR-SIMD-001` gate rejected a post-hoc route:

```text
current layout -> twiddle-major -> current layout
```

This gate tests the different persistent architecture:

```text
current S1--S3
-> S4-native (do not repair the old layout)
-> one 24-unpack L4N-to-{Lp,Hp} network
-> compact-vector S5
-> M_TM
-> consumers remain in M_TM
```

`M_TM` remains coefficient-plane SoA. It changes only the leaf order and uses
the S5 sum/difference branch as the two 16-leaf groups.

## Exact positive results

### S4-native

Removing the two trailing `vperm2i128` repairs from each S4 pair changes S4
from 40 to 32 instructions per tile, or **-48 instructions per Forward**.

### L4N to L/H planes

The exhaustive bounded search finds an exact 24-instruction network:

```text
8 x vpunpck{l,h}wd
8 x vpunpck{l,h}dq
8 x vpunpck{l,h}qdq
```

It needs 8 live data registers plus one rotating temporary: **peak 9 YMM**.
The selected common leaf-lane order is bit-reversal on four bits:

```text
0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15
```

### Compact S5 tables

The generator derives one 16-word QINV vector and one 16-word factor vector
from the selected production tables. The vectors are degree-independent, so
the same pair is reused for all four coefficient planes. S5 keeps four
Montgomery vector chains per tile and the existing range/scale contract.

### B3 and add

M_TM remains four consecutive degree planes per 16-leaf group. B3 therefore
needs no runtime repair: only the lambda and lambda-QINV lanes are relabelled.
Lane-wise polynomial addition is unchanged.

### Inverse topology candidate

An exact reverse 24-instruction network exists with the same instruction
multiset as the current progressive inverse entry: eight word, eight dword,
and eight qword unpacks. This is a conditional closure result, not an emitted
inverse kernel: the permutation must replace/interleave with the existing
inverse entry, not become a standalone 24-instruction repair pass.

## Static Forward ledger

Per tile:

| Item | Current | Persistent M_TM |
|---|---:|---:|
| S4 | 40 | 32 |
| L4N to L/H | 0 | 24 |
| Compact constant loads | included | 2 |
| S5 arithmetic | 36 | 24 |
| Plane redeposit | 24 | 0 |
| Stores | 8 | 8 |
| **Total** | **108** | **90** |

The static ceiling is therefore **-18 instructions/tile**, or
**-108 instructions/Forward**, before consumer costs.

## Q24 hard stop

Q24 is the consumer that prevents promotion.

The current four-packet route cannot be relabelled because each serialized
packet crosses the new M_TM group bit. The generator then exhausts all 2,304
three-layer 24-unpack networks for an eight-packet tile. It repeats that test
for all 48 leaf orders admitted by the Forward 24-instruction network:

```text
48 terminal leaf orders x 2,304 Q24 networks = 110,592 networks
```

None produces the two M_TM groups at the current 24-instruction transpose
budget using the modeled AVX2 operations and packet-local qword placements.
Consequently, Q24 would require route repair or a wider/new packet mechanism.
The experiment forbids a global M_TM-to-M repair, so no assembly is emitted.

This is a bounded physical-network result. It does not claim that no larger
AVX2 network could encode M_TM; it says that such a network loses the required
zero-debt Q24 consumer closure.

## Decision

```text
S4-native:       qualified static
24-inst L/H:     qualified static
compact S5:      qualified static
B3/add:          closed by table relabel / unchanged lanes
inverse:         conditional progressive-topology candidate
Q24:             no zero-debt route in the bounded search
assembly:        hard stop
```

Reopen only if Q24 gains a new packet mechanism that consumes/emits M_TM
without more runtime routing than current M, or if a caller can remain M_TM
without crossing a Q24 boundary.

## Reproduce

From this directory:

```sh
make check
```

The generated JSON contains source hashes, exact symbolic register flow,
networks, compact tables, leaf mapping, consumer proofs, and the static ledger.


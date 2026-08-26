# GT9X16-PROD3-ENCAP-R-HASH-FANOUT-ATTRIBUTION

## Question

The real encapsulation caller consumes sampled `r` twice.  MA2 needs a
transform state, while `hash_g` needs the exact 1,728-byte serialization of
Official's NTT state.  This checkpoint separates transform-producer cost from
the incremental cost of that second consumer.

Four variants share one SUPERCOP-derived measure ELF:

```text
O0: coefficient r -> Official NTT state
O1: coefficient r -> Official NTT state + exact hash bytes
C0: coefficient r -> PROD3 exact MA2-native planes
C1: coefficient r -> PROD3 exact MA2-native planes
                  -> current recovery -> exact hash bytes
```

The primary estimator is:

```text
Official fanout cost   FO = O1 - O0
Candidate fanout cost  FC = C1 - C0
Excess fanout tax          = FC - FO
```

`C1-O1` is retained as the complete dual-output comparison, while `C0-O0`
separately prices the producer implementations.

## Correctness and structure

The four wrappers preserve the existing arithmetic exactly.  PROD3, top
split, scale, plane order, the recovery bridge, and Official `poly_tobytes`
are unchanged.  The differential passes:

- zero and alternating inputs;
- all 2,304 signed impulses;
- 1,003 random small-polynomial inputs;
- raw equality of O0 and O1 Official states;
- raw equality of C0 and C1 MA2 planes;
- byte equality of O1 and C1's complete 1,728-byte hash input;
- coefficient-input immutability;
- ASan and UBSan.

The linked-ELF audit proves these direct-transfer graphs:

| variant | direct transfers |
| --- | --- |
| O0 | `poly_ntt` |
| O1 | `poly_ntt`, `poly_tobytes` |
| C0 | `top_split_small`, `prod3_aos_full_price` |
| C1 | `top_split_small`, `prod3_aos_full_price`, `prod3_hash_bytes` |

Every variant occupies each of four timing positions once per loop.  This
Latin-square schedule gives 384 balanced observations per variant per fresh
process.  Input residency and allocation policy are identical.

## Serious result

The benchmark uses pinned SUPERCOP 20260627 timing, allocation, compiler, and
machine machinery with the fixed O3GC recipe.  Independent nine-process
ASLR-on selection chooses normal placement by absolute C1 StQ2 (2422.7593
versus 2423.0995).  The headline is a separate nine-process normal-placement
ASLR-on replay on CPU 1 of the Intel Core Ultra 7 155H, performance governor,
turbo disabled.

| variant | pooled StQ2 |
| --- | ---: |
| O0: Official producer | 1406.4132 |
| O1: Official dual output | 1711.9861 |
| C0: PROD3 MA2 producer | 1588.0961 |
| C1: PROD3 dual output | 2423.1250 |

The headline per-launch medians are:

| attribution | cycles |
| --- | ---: |
| Official hash fanout, O1-O0 | +305.8021 |
| candidate hash fanout, C1-C0 | +835.3333 |
| PROD3 producer versus Official, C0-O0 | +181.8750 |
| **excess hash-fanout tax** | **+529.5313** |
| complete dual output, C1-O1 | +712.8333 |

The excess-tax direction is positive in 9/9 launches, with bootstrap 95%
interval `[+525.8021,+533.7500]`.  Complete dual output is slower in 9/9 with
interval `[+705.1563,+714.4792]`.  The producer-only delta is also positive in
9/9 with interval `[+179.2604,+183.6771]`.

## Placement and ASLR controls

| setting | producer delta | excess fanout tax | complete dual-output delta |
| --- | ---: | ---: | ---: |
| normal, ASLR on | +181.8750 | +529.5313 | +712.8333 |
| normal, ASLR off | +181.6979 | +527.1354 | +710.3646 |
| reversed, ASLR on | +183.2083 | +528.3958 | +710.4271 |
| reversed, ASLR off | +181.2188 | +526.8333 | +707.4479 |

Every delta above is the median of nine fresh processes.  All producer,
fanout, and complete-dual-output confidence intervals remain strictly above
zero, so the attribution does not depend on placement or ASLR.

## Interpretation

The current recovery path imposes a real approximately 530-cycle tax beyond
the approximately 306 cycles Official pays to serialize its already-native
state.  This validates multi-consumer fanout as a significant optimization
target.  It explains a material part, but not all, of the previous native
`+1498.7` and fixed-common `+1.9--2.1k` encapsulation regressions.  Those
campaigns have different boundaries and must not be subtracted as a formal
cycle ledger.

This checkpoint also corrects an overly broad reading of the earlier island
result.  PROD3 is approximately 432 cycles faster than the historical G0/P2-B
producer pair, but in this direct one-operand comparison Official O0 remains
approximately 182 cycles faster than PROD3 C0.  Persistent AoS is the selected
GT9x16 realization; it is not yet the fastest complete NTRU+1152 forward
producer against Official.

## Decision

A direct serializer now has a measured local ceiling: eliminate as much as
possible of the approximately 530-cycle excess tax by producing the exact hash
bytes directly from scale-4 MA2 planes.  It is worth mapping, but cannot by
itself establish production competitiveness.  Even a hypothetical fanout
matching Official would leave the measured producer delta and other
outside-island caller debt.

The next checkpoint is map/proof only:

```text
GT9X16-PROD3-MA2-HASH-DIRECT-MAP

MA2 planes, scale 4
-> exact coefficient/byte ownership oracle
-> localized inv4 and representative normalization
-> exact 12-bit serialized byte map
```

No direct serializer assembly is authorized until that map proves exact
ownership, byte-boundary handling, range, alias, and a defensible movement
ledger.  PROD3 arithmetic, MA2, twist, top split, and plane ABI remain frozen.

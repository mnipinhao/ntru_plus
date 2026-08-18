# Quartic AoS Basemul schedules

| schedule | vector work | result |
| --- | --- | --- |
| direct schoolbook | 16 products, 12 zeta folds, 16 coefficient selections | implemented, no scalar lane extraction or scratch |
| expanded formula | same product count, potentially fewer masks | needs independent schedule proof |
| Karatsuba-like | fewer products, more reshuffle/live state | rejected for this layout |

The direct schedule uses 48×29 Montgomery chains, 1,536 `vpshufb`, and 768 masked accumulations. It needs no `vperm2i128`, unpack/interleave, scalar insertion, or scratch, but is a likely Basemul tax relative to GT SoA.

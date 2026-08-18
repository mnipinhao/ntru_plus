# Y1 Yang-style signed range ledger

All values remain at mathematical scale R^0. Bounds are conservative absolute signed
bounds; the signed-16 margin is `32767-bound`.

| Boundary | Bound | Margin | Producer | Next consumer | Correction |
| --- | ---: | ---: | --- | --- | --- |
| input | 3456 | 29311 | native state | L0 add/sub | none |
| L0 | 6912 | 25855 | lazy add/sub | L1 Montgomery | redundant |
| L1 | 9005 | 23762 | Montgomery + lazy add/sub | L2 Montgomery | redundant |
| L2 | 11209 | 21558 | Montgomery + lazy add/sub | semantic store | Barrett + canonical add-q |
| L3 | 13529 | 19238 | Montgomery + lazy add/sub | L4 Montgomery | redundant |
| L4 | 15972 | 16795 | Montgomery + lazy add/sub | pre-DFT3 state | Barrett + canonical add-q |

For an input bound B, the signed Montgomery result is conservatively bounded by
`ceil(3456*B/65536)+1729`. This gives 2094, 2204, 2321 and 2443 at the successive
multiplication boundaries. No 16-bit addition or Montgomery operand approaches overflow.

The first implementation used a single add/sub correction at L4. Random case 0 exposed
`-909` versus canonical `2548`; they are congruent modulo 3457. This confirmed that the
proved multi-q range required signed Barrett, not another single-q correction.

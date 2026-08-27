# 098A results — E0V RX-tail entry phase

## Decision

`SEARCHED_NO_PROMOTION`.

Moving only the E0V helper entry by 32-byte increments produced apparent
winners in the directional and first formal campaigns, but the selected phase
did not reproduce in an independent 32-block confirmation.  Production stays
at page offset zero and source baseline `b2a4bea`.

## Static and correctness gates

- All 16 phases from `0x000` through `0x1e0` were generated exactly.
- The helper remained 4914 bytes and came from one common object.  Its final
  RIP-relative displacements changed as required by relocation.
- 82 pre-existing hot symbols retained identical address, size, and bytes.
- The Encap caller retained entry address `0x3cd0`, size 590, and its qualified
  611-byte reservation; only its helper call displacement changed.
- `.rodata` remained identical across all images.
- All 16 phases passed 1000 deterministic byte-exact Encapsulations, 768
  noncanonical-public-key cases, and input-immutability checks.

## Four-block directional sweep

The best Encap medians versus phase zero were:

| Helper offset | Median cycles | 95% bootstrap CI | Negative blocks |
|---:|---:|---:|---:|
| +320 | -27.00 | [-34.50, +7.50] | 3/4 |
| +448 | -22.00 | [-66.00, +2.00] | 3/4 |
| +480 | -14.75 | [-62.50, +49.00] | 2/4 |
| +128 | -11.00 | [-34.50, +53.50] | 3/4 |

The sweep was used only to select finalists.

## Sixteen-block formal gate

No finalist produced an Encap confidence interval below zero:

| Helper offset | Encap median | 95% bootstrap CI | Negative blocks |
|---:|---:|---:|---:|
| +320 | +4.50 | [-30.75, +16.25] | 6/16 |
| +448 | -6.00 | [-31.50, +5.50] | 10/16 |
| +480 | -9.50 | [-18.00, +9.50] | 10/16 |
| +128 | -0.38 | [-26.75, +21.75] | 9/16 |

Phase +448 did show a post-attribution equal-weight
`Keypair + Encap + Decap` median of -43.13 cycles with CI
[-95.75, -9.50].  Because this implementation-level signal could be useful
even without Encap-local attribution, it received an independent confirmation
rather than being discarded.

## Independent 32-block confirmation: +448 versus zero

| Metric | Median cycles | 95% bootstrap CI | Negative blocks |
|---|---:|---:|---:|
| Keypair | -5.63 | [-13.50, +20.00] | 18/32 |
| Encap | -5.13 | [-17.25, +1.00] | 20/32 |
| Decap | -7.63 | [-18.25, +7.63] | 20/32 |
| Equal-weight total | -9.25 | [-83.00, +6.25] | 19/32 |

The qualification signal did not reproduce.  Selecting +448 would therefore
fit one favorable launch population rather than establish a faster exact
implementation under the declared host-default-ASLR SUPERCOP protocol.

## Closure

The E0V helper 32-byte entry-phase search is closed for the current image and
benchmark target.  Geometry remains an implementation variable, but neither
four-slot ordering (097) nor isolated E0V entry phase (098A) yielded stable
credit.  If code placement research continues, the next hypothesis must alter
relative placement of a larger producer/consumer pair, such as B3 and Q24,
rather than scanning more offsets of this helper alone.

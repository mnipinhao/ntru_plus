# GT9X16-PROD3-MA2-HASH-H1-PRICE

## Question and frozen boundary

This checkpoint prices only the representation edge from one already
materialized scale-four MA2 plane state to the exact 1,728 bytes consumed by
`hash_g`.

- H0 control: MA2 planes -> generic F0 -> Official physical order -> inv4 ->
  pinned `poly_tobytes`.
- H1 candidate: the direct straight-line
  `ntruplus1152_exp001_prod3_ma2_hash_h1` leaf.
- Both paths receive the same 2,304-byte input and produce bit-identical bytes.
- PROD3, MA2 arithmetic, hashing, SOTP, and the KEM caller are not executed.

The installed-source measure performs an untimed H0/H1 byte-exact preflight
before emitting timing observations. The linked call-graph audit verifies that
the two aligned wrappers transfer only to the intended H0 bridge and H1 leaf.

## Method

The benchmark is SUPERCOP-derived, not a native KEM result. It uses the pinned
SUPERCOP 20260627 snapshot, fixed-common O3GC compiler wrapper, SUPERCOP
`cpucycles`, allocation, build, compiler, and machine machinery, CPU 1, the
performance governor, and disabled turbo.

Each variant occupies all four positions in a balanced same-ELF schedule. The
selection campaign uses nine fresh ASLR-on processes for each normal/reversed
archive placement and selects the smallest absolute H1 StQ2. The serious
campaign then runs nine fresh processes for each placement with ASLR on and
off. Every label has 96 observations per launch. The headline estimator is
the median of the nine per-launch `H1 - H0` StQ2 deltas.

## Results

Independent selection chose reversed placement: H1 selection StQ2 was
767.4340 cycles versus 769.3391 for normal placement.

| setting | pooled H0 StQ2 | pooled H1 StQ2 | median H1-H0 | bootstrap 95% CI | direction |
| --- | ---: | ---: | ---: | ---: | ---: |
| reversed, ASLR on (headline) | 1083.1238 | 768.3310 | -314.6458 | [-317.9583, -311.9271] | 9/9 H1 faster |
| reversed, ASLR off | 1084.6597 | 769.0324 | -315.3750 | [-316.8542, -314.8542] | 9/9 H1 faster |
| normal, ASLR on | 1086.1794 | 767.1771 | -319.2396 | [-320.9688, -315.7917] | 9/9 H1 faster |
| normal, ASLR off | 1085.6273 | 768.0150 | -318.0938 | [-319.7604, -314.5625] | 9/9 H1 faster |

At the selected headline placement, direct H1 removes about 29.1% of the
current recovery time. The result is insensitive to both tested placement and
ASLR controls.

## Interpretation and decision

H1 is selected as the hash-serialization implementation for the PROD3
research caller. This validates direct consumer-native serialization as a
machine optimization, not merely as a static movement reduction.

The roughly 315-cycle edge credit is smaller than the earlier 529.5313-cycle
excess hash-fanout tax and far smaller than the 1498.6991-cycle native
encapsulation deficit. Those values come from distinct campaigns and are not
formally additive, but their scale rules out a production-performance claim
from this edge result alone.

The next checkpoint may only replace the old recovery bridge with H1 in the
otherwise frozen PROD3 encapsulation caller, rerun byte-exact KAT, and measure
native SUPERCOP `enc_cycles` plus fixed-ELF attribution. H2 remains withdrawn;
PROD3, MA2, twist, top split, serializer semantics, and caller allocation must
not change in that integration.

## Evidence

- `results/gt9x16-prod3-hash-h1-price-intel155h-20260826-001/supercop-gt9x16-prod3-hash-h1-price/summary.json`
- selection and serious measure ELFs, raw SUPERCOP data, compiler selection,
  fresh-launch outputs, runtime addresses, metadata, and pinned lock under the
  same result directory
- `bench/supercop/gt9x16_prod3_hash_h1_price_measure.c`
- `scripts/run_gt9x16_prod3_hash_h1_price.py`

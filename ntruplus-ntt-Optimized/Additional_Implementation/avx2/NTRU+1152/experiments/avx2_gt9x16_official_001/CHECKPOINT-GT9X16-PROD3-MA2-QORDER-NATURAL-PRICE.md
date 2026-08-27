# GT9X16-PROD3-MA2-QORDER-NATURAL-PRICE

## Frozen comparison

This checkpoint performs the final machine arbitration between current-Q and
C1-natural-Q. Both same-ELF paths execute the complete caller-shaped island:

- two coefficient-domain top splits and PROD3 producers for `r` and `m`;
- one resident-`h` projection;
- identical lane-wise MA2 arithmetic, with only offline lambda reindexing;
- H1 serialization for the ciphertext polynomial and the `r` hash input.

The untimed preflight requires both paths to produce identical ciphertext
polynomial bytes and identical 1,728-byte hash input. The comparison changes
only the shared internal Q-order ABI.

## Method

This is a SUPERCOP-derived caller-island benchmark, not a native KEM result.
It uses pinned SUPERCOP 20260627, SUPERCOP `cpucycles`, allocation/build and
machine machinery, the fixed-common O3GC wrapper, CPU 1, the performance
governor, and disabled turbo. Each label has 96 observations per fresh process.

Normal and reversed archive placements were each built once and retained as
fixed ELFs. Every ELF was replayed in nine fresh processes with ASLR enabled
and nine with ASLR disabled. Balanced same-ELF ordering covers current-first,
natural-second, natural-first, and current-second. No placement was selected as
a headline; all four settings are co-equal ABI evidence.

## Results

| placement | ASLR | current pooled StQ2 | natural pooled StQ2 | median natural-current | bootstrap 95% CI | launches |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| normal | on | 5318.7870 | 5166.4074 | -160.0000 | [-165.5000, -144.1042] | 8/9 natural faster |
| normal | off | 5321.0463 | 5157.9699 | -166.2917 | [-173.7708, -156.1875] | 9/9 |
| reversed | on | 5321.6435 | 5156.2593 | -163.8333 | [-173.0208, -159.2500] | 9/9 |
| reversed | off | 5319.4884 | 5154.5440 | -165.0625 | [-170.2083, -155.9583] | 9/9 |

Natural-Q wins by about 160--166 cycles, approximately 3.0--3.1%, in every
placement/ASLR setting. All four bootstrap confidence intervals lie entirely
below zero. One of 36 fresh launches was an ASLR-on outlier in the normal ELF;
the setting-level median, confidence interval, and the other three controls all
retain the same direction.

The linked static attribution remains `-192` routing instructions, `+16` data
loads, and `-176` total instructions for natural-Q. The arithmetic and store
counts are identical. The result therefore confirms that redefining the shared
internal ABI around the producer's natural presentation is a caller-wide
machine win.

## Decision

C1-natural-Q is permanently frozen as the Q-order for the PROD3 Encap research
baseline. Current-Q remains only as a historical/control implementation. Do
not reopen XOR orders, bit permutations, or another Q-order search unless a
consumer's arithmetic architecture is itself redesigned.

This checkpoint does not authorize native KEM measurement or production
promotion. The next checkpoint is T0 absorption mapping and exact Montgomery
chain-count proof. It must demonstrate a real reduction in chain count before
ASM or performance work is authorized.

## Evidence

- `results/gt9x16-prod3-qorder-price-intel155h-20260827-001/summary.json`
- fixed normal/reversed measure ELFs, compiler metadata, SUPERCOP data, raw
  fresh-launch outputs, runtime addresses, and pinned lock below that directory
- `bench/supercop/gt9x16_prod3_qorder_price_measure.c`
- `scripts/prepare_gt9x16_prod3_qorder_placements.py`
- `scripts/run_gt9x16_prod3_qorder_price.py`

# ENCAP-MA2-CT-EGRESS-H4-M3B-PRICE

## Outcome

The machine-probed exact H4-M3B egress is a small, stable win over the
qualified H4-M3 Natural-Q H1 fallback at the complete caller-shaped boundary:

```text
valid 1728-byte PK + resident scale-1 r/m -> exact 1728-byte ciphertext
```

The predeclared normal-placement, ASLR-on serious headline is:

```text
H4-M3 control StQ2:     2134.8542 cycles
H4-M3B candidate StQ2:  2107.3773 cycles
launch-median delta:     -27.6042 cycles
bootstrap 95% CI:       [-29.2708, -25.6875]
direction:               9 / 9 launches faster
```

This is `supercop-derived-encap-h4-m3b-price`, not a native SUPERCOP KEM
result.

## Exact comparison

Control:

```text
H3 decode / producer / MA2
-> canonical scratch
-> Natural-Q H1 exact fallback
-> ciphertext
```

Candidate:

```text
same H3 decode / producer / MA2
-> same canonical scratch
-> machine-probed exact pair32 / packed24 egress
-> ciphertext
```

Untimed preflight requires the rejection result, all 2,304 canonical scratch
bytes, and all 1,728 ciphertext bytes to match exactly.  No KEM wrapper,
hashing, or unrelated arithmetic is included.

## Serious fixed-ELF evidence

The campaign uses pinned SUPERCOP 20260627 `cpucycles()`, fixed common O3GC,
CPU 2, performance governor, disabled turbo, balanced first/second execution,
and 9 fresh processes per setting.  Every label contributes 96 observations
per launch; each combined control or candidate result has 1,728 observations.

| Setting | Control StQ2 | Candidate StQ2 | Launch-median delta | 95% CI | Direction |
| --- | ---: | ---: | ---: | ---: | ---: |
| normal, ASLR on | 2134.8542 | 2107.3773 | -27.6042 | [-29.2708, -25.6875] | 9/9 |
| normal, ASLR off | 2135.3912 | 2108.6667 | -26.8125 | [-27.5000, -24.4167] | 9/9 |
| reversed, ASLR on | 2135.4514 | 2109.8426 | -25.8958 | [-27.3125, -24.5417] | 9/9 |
| reversed, ASLR off | 2134.8611 | 2108.9606 | -26.0833 | [-28.4167, -23.4167] | 9/9 |

All 36 serious fresh launches agree in direction.  ASLR-on runs observed nine
distinct runtime-address tuples; ASLR-off runs observed exactly one.

## Machine attribution

Relative to the H4-M3 control, M3B changes the complete symbol as follows:

```text
instructions: 5189 -> 5075  (-114)
.text:        32996 -> 31348 (-1648 bytes)
.rodata:       5408 ->  5728 (+320 bytes)
```

The measured gain is therefore real but deliberately characterized as a small
egress credit.  It does not justify a native-KEM claim by itself and does not
erase the remaining caller debt.

## Reproduction

The non-overwriting campaign installer creates separate normal and reversed
implementations.  The runner preserves both fixed ELFs, hashes, raw outputs,
addresses, machine state, and pinned lock data.

```sh
make prepare-encap-h4-m3b-price \
  SUPERCOP_CAMPAIGN_ROOT=<disposable-campaign>

make supercop-encap-h4-m3b-price \
  SUPERCOP_CAMPAIGN_ROOT=<disposable-campaign> \
  SUPERCOP_COMPILER_WRAPPER=<repo>/bench/supercop/okc-o3gc.sh \
  BENCH_CPU=2 \
  H4_M3B_PRICE_LAUNCHES=9
```

The retained serious report is
`results/encap-h4-m3b-price-intel155h-20260828-001/summary.json`.

## Decision

Select H4-M3B as the research baseline for exact ciphertext egress.  Preserve
H4-M3 as the exact H1 fallback and attribution control.  Do not run native KEM
or claim production promotion from this isolated `-27.6` cycle result alone.

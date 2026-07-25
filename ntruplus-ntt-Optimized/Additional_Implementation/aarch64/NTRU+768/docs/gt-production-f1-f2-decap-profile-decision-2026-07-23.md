# GT Production F1/F2 Decapsulation Profile Decision

Date: 2026-07-23

## Decision

Use compact F1 as the default GT production decapsulation verification
backend. Keep fully unrolled F2 as the opt-in `speed` profile:

```text
default:
  GT_PRODUCTION_DECAP_VERIFY_PROFILE=compact

maximum decapsulation speed:
  GT_PRODUCTION_DECAP_VERIFY_PROFILE=speed
```

Both profiles implement the same private contract:

```text
GT block-major c-m2 + canonical hinv bytes
  -> QSoA pointwise product
  -> canonical verification bytes
```

They do not replace generic `poly_basemul`.

## Correctness and ABI gates

Raspberry Pi 5, Cortex-A76:

```text
F1 full KEM: count = 0
F2 full KEM: count = 0
F1 decap backend: mismatches = 0, ABI mask = 0x0
F2 decap backend: mismatches = 0, ABI mask = 0x0
transform semantic mismatches = 0
transform ABI mask = 0x0
production inverse mismatches = 0
production inverse ABI mask = 0x0
production symbol closure = pass
```

The transform audit reports representative differences for the independently
normalized inverse, but all differences are zero modulo q and remain inside
the required centered range. This is existing representative behavior, not an
F1/F2 difference.

## Same-binary paired PMU

Settings:

```text
core = 3
NTESTS = 61
NITERATIONS = 2000
NINPUTS = 32
balanced F1/F2 call order
valid and malformed ciphertext differential checks
```

| Profile | Full decap cycles | Instructions | CPI |
|---|---:|---:|---:|
| F1 compact | 33,076 | 76,484 | 0.432 |
| F2 speed | 32,964 | 76,434 | 0.431 |

Paired `F1 - F2`:

```text
p10 = +103 cycles
p50 = +112 cycles
p90 = +117 cycles
F1 wins = 0 / 61
```

F2 is consistently about 112 cycles, or 0.34%, faster when both backends are
linked into the same binary.

## Unique replacement binaries

Balanced order was F2, F1, F1, F2.

Full decapsulation medians:

```text
F2: 32903, 32871 cycles
F1: 32971, 32976 cycles
```

The averaged gap is about 87 cycles, or 0.26%, in favor of F2.

The profile does not execute during keygen or encapsulation. Unique-binary
measurements showed only code-placement noise:

```text
keygen:
  F2 = 37728, 37704
  F1 = 37698, 37686

encapsulation:
  F2 = 37574, 37575
  F1 = 37581, 37656
```

No systematic non-decap regression is attributed to F1.

## Code size

Minimal full-KEM correctness binary:

| Profile | `.text` bytes |
|---|---:|
| F1 compact | 95,027 |
| F2 speed | 104,115 |

F1 saves 9,088 bytes of `.text`. The unique aarch64-bench replacement
binaries show the same 9,088-byte delta.

## Rationale

F2 remains the fastest decapsulation backend, but its approximately 0.3%
full-decap gain costs about 9 KB of text. F1 is therefore the better general
production balance. The explicit speed profile preserves F2 for deployments
where code size and instruction-cache footprint are secondary.

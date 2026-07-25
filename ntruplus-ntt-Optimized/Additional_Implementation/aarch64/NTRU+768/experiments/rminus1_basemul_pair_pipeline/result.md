# R-minus-one basemul pair pipeline result

## Decision

Promote the Slothy two-iteration schedule as the production rminus1 basemul
implementation. It preserves the arithmetic/layout contract and also preserves
the AAPCS64 low `d8-d15` lanes, which the previous leaf did not.

## Correctness and ABI

Raspberry Pi 5:

```text
1003 cases x 768 coefficients
U2 mismatches: 0
Slothy mismatches: 0
sentinel-output mismatches: 0
x19-x28 / d8-d15 ABI mask: 0x0
full KEM count: 0
production symbol closure: pass
KAT SHA256:
22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8
```

The first direct test also exposed that the old production leaf clobbered
callee-saved `d8-d15`. PMU therefore compares the candidate with an ABI-safe
save/call/restore wrapper around the old arithmetic.

## Direct PMU

Pi 5 Cortex-A76, core 3, 61 samples x 20,000 calls:

| Variant | Cycles | Instructions | Paired delta | Wins |
|---|---:|---:|---:|---:|
| old production, ABI-safe wrapper | 2020.02 | 1920 | 0 | baseline |
| U2 source order | 2010.01 | 1894 | -10 | 61/61 |
| Slothy pair | 1912.01 | 1894 | -108 | 61/61 |

The candidate improves the ABI-safe kernel by 5.35%. N1's annotated
`38 cycles/pair` is not an A76 prediction because the current model does not
represent A76's single V0 multiply resource accurately.

## Full KEM

Unique replacement binaries, portable `NO_CE`, 61 samples x 2,000 calls:

| Scope | Old production | Pair candidate | Result |
|---|---:|---:|---:|
| decapsulation, A then B | 32945 | 32864 | -81 |
| decapsulation, B then A | 32964 | 32849 | -115 |
| keygen | 37696/37720 | 37704/37695 | placement noise |
| encapsulation | 37599/37576 | 37610/37601 | placement noise |

Full decapsulation retired instructions changed from 76,479 to 76,465.
Binary `.text` increased from 95,005 to 95,325 bytes, a 320-byte cost.

## Frozen production artifact

The production source is:

```text
asm/gt/basemul/poly_basemul_rminus1.n1.opt.S
SHA256 cde190dc57fbc4fff5428237e2b40ccddf82ea4cc3a445f4541d4db7ebc34546
```

It is selected by `GT_PRODUCTION_BASE_SOURCES`; no source override is required.
Both mixed BPQ/CQ and direct-CQ KEM closures pass `count=0` and symbol closure.
The production inverse ABI test and transform semantic audit also pass.

# AVX2-GT-D4-AOS-OFFICIAL-API — domain-boundary ledger

## Required distinct reference types

Reference code and tests will use separate types even though the eventual
shadow-KEM ABI stores every transform-domain value in `poly`:

```c
typedef struct { int16_t coeff[768]; } d4aos_coeff_ref;
typedef struct { int16_t lane[768]; } d4aos_ntt_ref;
typedef struct { int16_t lane[768]; } official_ntt_ref;
typedef struct { uint8_t byte[1152]; } wire12_ref;
```

`d4aos_ntt_ref` is not layout-compatible with `official_ntt_ref` by declaration.
Only mapper functions can cross this boundary.

## d=4 AoS hypothesis (not yet proved)

The target internal layout is branch-paired quartic AoS.  For physical YMM lane
index `0..15`, the proposed identity is:

```text
lane(b, u, c) = 8*b + 4*u + c
b = paired branch, u = quartic component within a 128-bit half, c = 0..3
```

This is an implementation hypothesis, not a licence to reuse existing GT SoA
tables.  Before code, a generator must prove logical-to-physical and inverse
maps, Good--Thomas indices, branch identities, Forward/inverse roots, quartic
zeta order, R/R^-1 scale, normalisation, and natural-output mapping.

## Allowed and forbidden crossings

| Crossing | Status | Rule |
| --- | --- | --- |
| `COEFF ↔ D4AOS-NTT` | required | d4 Forward/Inverse maps, proved by round trips |
| `OFFICIAL-NTT → D4AOS-NTT` | required later | named mapper only; account separately in Dec endpoint |
| `D4AOS-NTT → OFFICIAL-NTT` | required later | named mapper only; permitted for non-production BaseInv bridge |
| `D4AOS-NTT ↔ WIRE12` | required later | reference via Official mapper first, then direct checked codec |
| Official NTT value consumed as d4AoS | forbidden | no untagged `poly` handoff |
| d4AoS value consumed by Official baseinv/pack | forbidden | no implicit layout reuse |
| d2 representation | forbidden | outside this campaign |

## AVX2 contract for the first inverse candidate

The first assembly candidate may begin only after the mapping generator passes.
It must consume verified d4AoS input, retain one DFT3 row per compact AoS YMM,
retain all three row outputs in three YMMs, avoid whole-array DFT3 rewrite and
SoA conversion, use at most 16 YMM registers, and not spill to stack.  Its
range checkpoints initially match the selected proof rather than copying a
current GT SoA lazy schedule.

## Required generated evidence before Stage 3

- machine-readable map and inverse-map tables;
- symbolic root and zeta-order proof;
- scale/normalisation constants and reduction proof;
- tagged lane tests for every logical position;
- shared schoolbook oracle for `X^768 - X^384 + 1`;
- ASan/UBSan test plan, canaries, and alias cases.

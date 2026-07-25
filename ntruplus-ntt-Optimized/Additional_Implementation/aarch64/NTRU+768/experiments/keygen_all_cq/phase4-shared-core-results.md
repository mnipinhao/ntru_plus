# Phase 4: Shared Generic/Direct-CQ NTT Core

Date: 2026-07-23

Status: correctness and ABI pass; code-size gate pass; keep as the selected
default-off all-CQ implementation base. Production default is unchanged.

## Candidate shape

The previous direct-CQ binary linked two complete forward NTT bodies:

```text
generic poly_ntt:
  Phase123 -> generic Stage12/Stage345 stores

direct-CQ endpoint:
  Phase123 -> direct-CQ Stage12/Stage345 stores
```

The shared-core candidate keeps one common Phase123 body and branches at the
first row Stage12 boundary:

```text
public entry selector
  -> shared prologue and Phase123
  -> generic row suffix OR direct-CQ row suffix
  -> shared epilogue and one copy of the NTT tables
```

The selector is determined only by the called public symbol. Arithmetic,
reduction, and both endpoint layout contracts are unchanged.

## Correctness and ABI

Pi 5 results:

```text
generic differential cases  1000, mismatches 0
CQ differential cases       1000, mismatches 0
generic in-place             pass
CQ in-place                  pass
generic ABI mask             0x0
CQ ABI mask                  0x0
full KEM count               0
```

The ABI sentinel checks `x19-x28` and the required low `d8-d15` halves. The
AArch64 feature checker and secret-independence checker report zero warnings.

## Endpoint PMU

Pi 5 Cortex-A76, core 3 pinned, grouped Linux perf events, 61 samples x 20000
calls. Standalone and shared candidates were rebuilt and measured in the same
session.

| Endpoint | Cycles | Instructions | CPI |
|---|---:|---:|---:|
| standalone production generic | 2594.82 | 3701 | 0.7011 |
| shared-core generic | 2591.23 | 3707 | 0.6990 |
| standalone direct-CQ | 2659.68 | 3722 | 0.7146 |
| shared-core direct-CQ | 2664.89 | 3726 | 0.7152 |

The exact dispatch overhead is six retired instructions on the generic entry
and four on the CQ entry. The generic cycle difference is noise/alignment
sensitive. The CQ path costs 5.21 median cycles in this run.

## Full-KEM replacement PMU

Portable `NO_CE` SHAKE, core 3 pinned, 61 samples x 2000 calls. These are
separate replacement binaries, so single-digit cycle differences between the
two all-CQ builds must not be treated as paired evidence.

| Operation | Production | Separate direct-CQ | Shared direct-CQ |
|---|---:|---:|---:|
| keygen cycles | 37706 | 36743 | 36736 |
| encapsulation cycles | 37613 | 37586 | 37590 |
| decapsulation cycles | 32908 | 32933 | 32903 |
| keygen instructions | 86067 | 81565 | 81573 |
| encapsulation instructions | 106175 | 106173 | 106185 |
| decapsulation instructions | 76429 | 76429 | 76441 |

The instruction deltas match the entry contract: keygen calls the CQ endpoint
twice (`+8` instructions), while encapsulation and decapsulation each execute
two generic forward NTTs (`+12` instructions). Shared-core keygen remains about
970 cycles, or 2.57%, below the current production keygen in this run.

## Linked text size

All three binaries below use `-ffunction-sections -fdata-sections` and
`--gc-sections`.

| Binary | `.text` bytes | Delta vs production | Delta vs separate CQ |
|---|---:|---:|---:|
| production | 89865 | 0 | -11392 |
| all-CQ, separate generic/direct-CQ bodies | 101257 | +11392 | 0 |
| all-CQ, shared generic/direct-CQ core | 92825 | +2960 | -8432 |

The two separate NTT symbols contain 29,636 bytes of function body. The shared
dual-endpoint body is 24,416 bytes, saving 5,220 bytes. Keeping one rather than
two copies of the NTT tables accounts for the remaining 3,212-byte reduction.

Symbol placement in this build:

| Symbol | Address | mod 32 | mod 64 | Size |
|---|---:|---:|---:|---:|
| production `poly_ntt` | `0x77c0` | 0 | 0 | 14776 |
| separate generic `poly_ntt` | `0x77a0` | 0 | 32 | 14776 |
| separate direct-CQ | `0x12600` | 0 | 0 | 14860 |
| shared `poly_ntt` | `0xdfa0` | 0 | 32 | 24416 |
| shared direct-CQ entry | `0xdfa8` | 8 | 40 | shared body |

## Decision

The shared-core gate succeeds:

- correctness and ABI contracts pass;
- direct-CQ keygen benefit survives;
- 8,432 bytes of the duplicate implementation are removed;
- the remaining all-CQ binary cost is 2,960 bytes over identical-GC
  production;
- runtime overhead is four to six instructions per NTT entry.

Keep this as the serious all-CQ experiment base. Promotion still requires a
deliberate production API/source-closure decision; this gate does not change
the default backend.

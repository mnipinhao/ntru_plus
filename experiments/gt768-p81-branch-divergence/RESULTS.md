# P81 — the two NTRU+768 trees, compared substantively

`neon-1152` and `aarch64-production` carry different NTRU+768 trees.  Today's
SUPERCOP run measured the one on this branch at −1.60% against the official
where the recorded figure is −20.70%, which looked like a regression.  It is
not: **this branch's NTRU+768 is an older generation**, and the recorded figure
belongs to `aarch64-production`.

## Measured, same host, same harness

A76, `taskset -c 2`, `PERF_COUNT_HW_CPU_CYCLES`, median of 65 x 60, three runs
agreeing within 0.8%.

| | keygen | encaps | decaps | total |
|---|---:|---:|---:|---:|
| `neon-1152` | 36,660 | 38,030 | 32,810 | 107,516 |
| `aarch64-production` | 31,607 | 29,370 | 27,715 | **88,692** |
| | −5,053 | −8,660 | −5,095 | **−18,824 (−17.5%)** |

Every operation is behind, not just the hashed ones.

## Where the divergence is

Merge base `d28c2137`.  Since then:

- **`aarch64-production`: 24 commits touching NTRU+768**
- **`neon-1152`: 3, all of them mine from today** (P74's clear technique, P80's
  caller-owned scratch, and a SUPERCOP export script).  The other two commits
  that touch a 768 path are repository housekeeping — a baseline archive and the
  removal of the obsolete KpqC tree.  `ntruplus-ntt-Optimized`'s NTRU+768 is
  identical on both branches, and there are no 768 experiments here.

So this branch has **no NTRU+768 optimizations of its own**.  What it has is the
state the branch forked from, plus three changes I made today against it.

## What only `aarch64-production` has

Performance:

| commit | |
|---|---|
| `58790554` | SHA3-gated Keccak x1 backend |
| `b5036b82` | fused SHA3 hash-g sponge |
| `e8dd7faa` | absorb hash prefixes without building them |
| `fce5c064` | drop the fused sponges for the portable one |
| `0bdc5798` | packed16 encap reduction |
| `dcfce09e` | D1 and Encap-small |
| `b6b78543` | compact lazy Encap NTT |
| `b2f9ee83` | checked unpack direct output mapping |
| `aad4167d` | eliminate zero Decap top-split quotients |

Structure: `739e0472` flattened the package paths, so the **flat layout is the
newer one** and this branch's `asm/`, `asm/internal/`, `internal/`, `NO_CE/`
split is what preceded it.  `14daa263` added the SUPERCOP leaf export.

## The Keccak backend is the visible half

`aarch64-production`'s `fips202.c` routes unconditionally to assembly —
`ntruplus_keccak_f1600_x1_v84a_aarch64` under `__ARM_FEATURE_SHA3`, else
`ntruplus_keccak_f1600_x1_aarch64`.  This branch's `NO_CE/fips202.c` calls a
static C `KeccakF1600_StatePermute` and the tree ships no Keccak assembly at
all.

| | `neon-1152` | `aarch64-production` | |
|---|---:|---:|---:|
| `hash_f` | 12,394 | 8,596 | −31% |
| `hash_g` | 13,692 | 9,557 | −30% |
| `hash_h` | 2,889 | 2,025 | −30% |

It cannot be isolated further by excluding the assembly, because that
`fips202.c` has no C fallback at the routing point — the link fails. Attributing
the remaining gap between the hash work and the encap/decap kernel commits above
would need call counting, which this gate did not do.

## Two things I got wrong on the way here

The export script I wrote for this branch's NTRU+768 (`52a3200c`) **duplicates
one that already exists on `aarch64-production`** (`14daa263`), and arrives at
the same design — a generated `namespace.h` prefix plus an `adapter.c` bridging
SUPERCOP's namespaced C names onto the assembly-defined entry points.  I should
have looked at the other branch before deriving it.

I also described the flat layout as the older one.  It is the newer one.

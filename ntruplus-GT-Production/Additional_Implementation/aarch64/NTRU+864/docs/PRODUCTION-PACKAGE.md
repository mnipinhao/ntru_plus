# NTRU+864 AArch64 production package contract

This package adopts the NTRU+768 production workflow, release gates, and
export contract. It does **not** inherit NTRU+768's transform decomposition,
twiddles, physical layout, Montgomery scale, range bounds, or schedules.

## Authoritative layers

- Public API: `api.h`, `params.h`, `poly.h`, `kem.c`.
- Representation contracts: the `gt864_*_api.h`, layout/table headers, and
  the range ledger referenced by `OPTIMIZATION-ROADMAP.md`.
- Accepted arithmetic: only objects named by `KEM_OBJECTS` in `Makefile`.
- Hash backend: generic `NO_CE/fips202.*` plus the Pi-5-compatible scalar
  fixed-size `hash_g_fixed.c`/`keccakf1600.S`. The latter does not require the
  Armv8.4 SHA3 extension.
- Correctness: `test/`, `kat/`, and external experiment records.
- Benchmark artifacts: repository `experiments/` or external `bench/`, never
  the exported SUPERCOP leaf.

The default `make` target directly links `test_kem`. `libgt864.so` is retained
only as the `shared` compatibility target used by paired profiler harnesses; it
is not the production linkage contract.

## P54 cleanup ledger

The first linked-symbol audit after P53 found that the integration-era shared
object still exports legacy/oracle/campaign endpoints such as `p3b12_*`, tail
architecture controls, legacy ToBytes cores, and generic stock transforms.
Those symbols do not imply that KEM callers use them, but they show why the
shared object cannot define the release source closure.

The package is therefore being cleaned in this order:

1. Freeze direct KEM/KAT `KEM_OBJECTS` and record each caller relocation.
2. Separate production-owned endpoints from test/reference endpoints.
3. Consolidate accepted transform, base, pack, and support source ownership.
4. Move differential oracles to `test/reference/`.
5. Move raw PMU/evidence logs out of the package.
6. Add ABI, canonical/malformed, zeroization, and exact checked-in KAT gates.
7. Add a deterministic SUPERCOP exporter driven by the Makefile closure.
8. Regenerate-and-compare the SUPERCOP leaf; never edit that leaf manually.

Until steps 2–8 pass, P54 remains active and this directory must not be called
as clean/self-contained as the NTRU+768 production package.

## Promotion gate order

Source selection → kernel proof → full KEM → ABI/alias → canonical/rejection →
zeroization → exact KAT → release hygiene → deterministic SUPERCOP export →
same-host performance → isolated Git commit.

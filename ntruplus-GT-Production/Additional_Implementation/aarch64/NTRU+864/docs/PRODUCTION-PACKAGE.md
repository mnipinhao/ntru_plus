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
  fixed-size `hash_f`/`hash_g` entries in `hash_g_fixed.c`/`keccakf1600.S`.
  Neither fixed entry requires the Armv8.4 SHA3 extension.
- Correctness: `test/`, `kat/`, and external experiment records.
- Benchmark artifacts: repository `experiments/` or external `bench/`, never
  the exported SUPERCOP leaf.

The default `make` target directly links `test_kem`. `libgt864.so` is retained
only as the `shared` compatibility target used by paired profiler harnesses; it
is not the production linkage contract.

## P54 closure

P54 completed the direct-link audit after P53. The accepted closure now
contains one tail layout, one checked decoder, the selected serializers, and
the selected Forward/BaseInv/BaseMul/Inverse kernels. Legacy stock transforms,
campaign candidates, differential oracles and raw PMU evidence are outside the
production package.

`make check` runs release hygiene and manifest checks, direct KEM tests, an
AAPCS64 sentinel over public and selected internal endpoints, all-position
noncanonical rejection, runtime/source zeroization checks, exact checked-in
KAT comparison, and deterministic export regeneration. The flattened export
also builds and passes the direct KEM test on Pi 5.

P55 extends that closed hash backend with an independent fixed-size `hash_f`
entry for SHAKE256(`0x00 || input[1296]`) to 32 bytes. It preserves the P53
`hash_g` section byte-for-byte and removes the generic 1297-byte transcript
only from Keygen and Encaps; Decaps is an exact retired-instruction control.

## Promotion gate order

Source selection → kernel proof → full KEM → ABI/alias → canonical/rejection →
zeroization → exact KAT → release hygiene → deterministic SUPERCOP export →
same-host performance → isolated Git commit.

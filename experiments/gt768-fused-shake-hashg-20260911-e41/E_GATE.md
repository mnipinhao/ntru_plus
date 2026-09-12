# E: production-shaped SUPERCOP export and integration gate

Experiment ID: `gt768-fused-shake-hashg-20260911-e41`.

Baseline production revision:
`a64e7035cb13410554af1c67870d4132a30037b4`.
D measured code revision:
`317a52f400fd84ee9b41d313548cc0dcbe81ba52`.

## Hypothesis gate

- Observation: the first D Official-layout export contained
  `ntruplus_hash_g_fused_aarch64`, but the package generator retained
  Official `symmetric.c`. Therefore `hash_g` continued to call generic
  `shake256` and the fused entry was not a linked caller dependency.
- Hypothesis: exporting the D `symmetric.c` and its matching `fips202.h`
  declaration will make the existing public `hash_g` wrapper call the fused
  implementation without changing the public SHAKE or symmetric APIs.
- Exact proposed change: move only `symmetric.c` and `fips202.h` from the
  generator's Official-copy set to its GT-copy set. Official CBD/SOTP,
  centered-mod3, utility, public API/parameters and `symmetric.h` remain
  unchanged.
- Expected static effect: one direct `hash_g -> ntruplus_hash_g_fixed`
  caller edge and one `ntruplus_hash_g_fixed ->
  ntruplus_hash_g_fused_aarch64` edge; the fused symbol becomes reachable.
  Hash-f/hash-h arithmetic and generic SHAKE remain unchanged.
- Expected performance effect: recover the fixed-wrapper and register-resident
  savings measured in C/D. The first non-D export measured 31967 Encap and
  29133 Decap cycles, close to the prior scalar-x1 leaf; a true D export should
  be materially lower.
- Expected register-pressure effect: none outside the already-validated fused
  entry. Its 25-lane GPR state and 144-byte frame contract are unchanged.
- Correctness/range impact: no polynomial, SHAKE, byte-stream, overlap,
  cleanup, public ABI or output contract changes.
- Falsifier: reject if the linked caller edges are absent, the fused symbol is
  dead-stripped, any package/KAT/failure/overlap/ABI/cleanup check fails, or
  paired Pi measurements do not improve reproducibly.

## First export control

The initial generated leaf was deterministic and passed Official-versus-leaf
KAT and public failure checks, but it did not exercise D. Pi 5 medians were
33101/31967/29133 cycles for Keygen/Encap/Decap, matching the earlier scalar-x1
package scale. This run is retained as a negative integration control rather
than reported as D performance.

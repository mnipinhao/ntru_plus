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

## Final integrated result

Integration revision:
`09d4b501423e0d48441ad078b2a846c05e834baa`.

The generator now takes `symmetric.c` and the matching `fips202.h` from the
GT package. It still takes Official `symmetric.h`, preserving its hidden-symbol
declarations and the Official public/header shell. The GT source guards its
six local size macros so the Official header and implementation compose
without redefinition warnings. The cleanup has no code-generation effect:
the pre-cleanup and final linked `.text` are both 74124 bytes with SHA256
`a11a80552293b12df78185a7c685130ca375c21bdee3e4395a153fce1c482398`.

Linked AArch64 disassembly proves the exact active path:

```text
hash_g (4 bytes)
    b ntruplus_hash_g_fixed
ntruplus_hash_g_fixed (12 bytes)
    load round-constant address
    b ntruplus_hash_g_fused_aarch64
ntruplus_hash_g_fused_aarch64 (1644 bytes)
```

The standalone `ntruplus_keccak_f1600_x1_aarch64` remains 1152 bytes for
generic SHAKE. The fused body is reachable rather than merely present.

### Correctness and packaging

- Mac and Pi package `make check` pass at the integration revision: 55-file
  release/manifest check, 100 KEM round trips, ABI including `hash_g_fixed`,
  9216 canonical cases, 4096 small-input cases, support tests, source/runtime
  cleanup checks and byte-identical KAT.
- KAT response SHA256 is
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.
- The final exported leaf is deterministically reproduced by the generator.
- Both Official and D exported leaves pass valid Keygen/Encap/Decap workloads,
  malformed-ciphertext failure and noncanonical-public-key failure checks.
  Operation sinks agree.
- Final export build logs contain no integration redefinition warning.

### Pi 5 SUPERCOP-style result

Official is exactly
`/home/pi/supercop-20260831/crypto_kem/ntruplus768/aarch64`, tree hash
`6529e33b01163decbdb441a6b6b905a6ad66807c0f9da9ec924969847785cc03`.
The D export tree hash is
`23cb63e0f6145535fbcc4801197617b264af7498ce0f649e1360192f8a5c58fe`.

Host: Pi 5 Cortex-A76, Linux 6.18.33+rpt-rpi-2712, GCC 14.2.0, core 3.
Each variant used 62 samples, 2000 operations/sample, 100 warmups and both
execution orders.

| Operation | Official p50 | D export p50 | Saved | Improvement |
|---|---:|---:|---:|---:|
| Keygen | 38535 | 33115 | 5420 | 14.07% |
| Encap | 38687 | 30445 | 8242 | 21.30% |
| Decap | 33489 | 27604 | 5885 | 17.57% |

Paired-sample saved-cycle medians are 5422.5/8243/5884.5. Their p10/p90
ranges are 5333--5505, 8226--8253 and 5866--5903 respectively.
Boundary environment checks were 58.2--62.6 C and `throttled=0x0`.

Three 100000-operation PMU runs per variant show the same direction. Relative
to Official, D reduces median instructions by about 13912/27396/18595,
`ld_spec` by 5780/10480/6357, `st_spec` by 3510/5880/3579 and backend-stall
cycles by 2414/3217/1874 for Keygen/Encap/Decap. Load/store events are
speculative, not retired-memory counts.

Full workload `.text` is 21617 bytes for Official and 82889 for D: +61272
bytes (+283.44%). Relative to the 81209-byte scalar-x1 negative control,
activating fixed/fused hash-g adds 1680 bytes.

## Reproduction and decision

Remote generated leaf:
`/home/pi/gt768-fused-shake-hashg-20260911-e41/.build/supercop-export-gate-v3/D-SUPERCOP/crypto_kem/ntruplus768/aarch64`.
Raw results:
`/home/pi/gt768-fused-shake-hashg-20260911-e41/.build/supercop-export-gate-v3/results`.
Local ephemeral mirror: `.build/pi-supercop-export-gate-v3`.

Generate with `ntruplus-GT-Production/scripts/generate_supercop_ntruplus768.py`
using the Official path above, then run the existing E34 `run_gate.py` with
the e33 SUPERCOP benchmark inputs. Exact paths, flags and results are retained
in `E-summary.json` and the raw summary/logs.

Decision: **accept as promotion-ready experimental champion**. The first
control falsified the original export mapping; the corrected mapping passes
all gates and recovers D's measured effect. No production merge or push was
performed in this gate.

## Promotion

After explicit user approval, branch `gt768-fused-shake-hashg-20260911-e41`
was merged into `aarch64-production`. The production code merge revision is
`525b6a5f815e2f45d260aab54429585bf500871a`; previous champion revision was
`a64e7035cb13410554af1c67870d4132a30037b4`. The tracked SUPERCOP leaf hash is
the measured v3 hash above. A post-merge Mac package `make check` passed.
Nothing was pushed as part of promotion.

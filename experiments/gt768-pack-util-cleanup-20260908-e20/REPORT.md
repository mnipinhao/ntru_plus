# e20: pack windows, checked mapping, support contracts and cleanup

Experiment ID: `gt768-pack-util-cleanup-20260908-e20`.
Branch: `codex/gt768-pack-util-cleanup-20260908-e20`.
Previous/current production champion: `ce617c87a39412958cddea17f10809fd2e0b3a3f`.
Candidate source: `561b6aa50dc0e237c3c884ec7174a208baf869e5`.
Decision: keep experimental pending promotion review; production is unchanged.

Official means the fixed Pi snapshot `/home/pi/supercop-20260627/crypto_kem/ntruplus768/aarch64`, not a newly fetched upstream main. Snapshot leaf hashes are retained in e19. This experiment compares the candidate with G5 under the same package contract; it does not rerun Official timing.

## 1. Loose reducer and consumer window

P0 uses reciprocal 9, SQRDMULH and MLS. Exhaustive signed-16 arithmetic gives residual [-3291,3291], with canonical correction producing the same bytes. P1 schedules eight independent quotient chains into the compact consumer, duplicating only a small reduction frontend, not twelve complete packing cores. Neither uses Slothy: these are bounded handwritten arithmetic/scheduling controls.

Four alternating Pi core-3 PMU rounds, 200,000 measured operations and 1,000 warmups:

| Variant | cycles/op | instructions/op | backend stalls/op |
| --- | ---: | ---: | ---: |
| Original loose pack | 970.13 | 1678.40 | 463.63 |
| P0 | 976.15 | 1581.92 | 517.15 |
| P1 reducer + consumer | 1015.32 | 1593.98 | 556.68 |

These totals include harness/setup/warmup overhead, not pure bare-kernel latency. All differential tests passed, including all signed-16 inputs. Both candidates are rejected: fewer instructions did not improve cycles. Candidate source retains the original loose reducer. Generated alternatives live only under ignored `.build`; `pack_candidates.py` regenerates them from the champion commit.

## 2. Checked unpack direct mapping

U removes the final eight TRN.2D instructions per chunk. The stores already select individual D halves, so they can select the equivalent halves of pre-TRN registers directly. Decode, global-max check, arithmetic, output order, 96 UMOV and 192 D stores remain unchanged. There is no new layout contract and no spill. Symbolic mapping covers all twelve chunks; arbitrary-byte differential covers 4096 cases. Register allocation peaks at 18, including six reserved registers.

This deletes 96 dynamic TRN per polynomial. Checked unpack falls from 549.21 to 512.98 cycles (36.24 cycles, 6.60%). Instructions fall from 1233.40 to 1136.92, while load/store counts are unchanged; backend stalls fall from 220.34 to 196.30. U is integrated in the candidate, but its full-KEM gain is small/noisy (see below).

## 3. crepmod3 semantic discrepancy

The old direct centered-mod3 helper and Official q-centering then mod3 are not equivalent outside [-1728,1728]. Tracing the real inverse-to-mod3 boundary gives:

| Input class | cases | helper calls | observed range | differing lanes | final rc/ss differences |
| --- | ---: | ---: | --- | ---: | ---: |
| Valid ciphertext | 4096 | 4096 | [-360,342] | 0 | 0 |
| One-bit mutation | 4096 | 3923 | [-1954,1962] | 37485 | 0 |
| Random canonical ciphertext | 4096 | 4096 | [-1936,1946] | 39177 | 0 |

Noncanonical early rejection explains the missing mutation helper calls. All malformed inputs in this sample were rejected. Thus the discrepancy is reachable on real malformed Decap intermediates, but this does not demonstrate a valid-ciphertext failure or exploit. The observed valid range is not a universal mathematical bound.

The candidate restores Official centering semantics over [-3456,3456], preserving GT's two-pointer ABI. The implementation uses caller-saved vectors and passes the public ABI gate. The new support oracle exhaustively covers this interval, both in-place and out-of-place. KAT remains bit-exact.

## 4. Names and clear helper

- Active ABI-safe `poly_sub_decap` becomes `poly_sub` in `add.S`; callers are updated and the duplicate older subtraction implementation removed. Renaming does not change subtraction semantics. GT's existing two-pointer `poly_triple` is preserved in this file.
- `support.S` is replaced by the focused `crepmod3.S`; `decap_add.S` is removed.
- `secure_clear.h` becomes `util.h`, and `gt_secure_clear` becomes `secure_clear`. The audit callback follows the name; the opt-in audit macro remains available.
- Portable clear implementations and coverage are preserved, rather than blindly copying Official's header. The Linux explicit_bzero declaration, optional Annex K/volatile fallback and Windows path remain explicit. The resulting `fips202.c` is byte-identical to the pinned Official copy.

Baseline/final clear calls and bytes are identical: Keygen 20/13352, Encap 16/6410, valid and invalid Decap 9/10930, noncanonical Decap 2/8608, invalid-PK Encap 2/128.

## 5. Residual code

Removed uncalled `gt_decap_reference_poly_ntt` and its private forward constants, `gt_decap_poly_triple`, `gt_decap_poly_basemul_scale`, `gt_decap_poly_basemul_add`, and `gt_decap_poly_baseinv_1`. Shared active tables remain.

Legacy QSoA decode/encode and verification are moved to `test/legacy`, explicitly linked by regression/ABI tests but excluded from the production source closure and exported leaf. Nine retired symbols are absent from the exported final executable. Public basemul/inverse, exact small-input NTT oracle and generic loose endpoints are retained. The inactive SHAKE assembly include branch is removed.

KAT executable text decreases from 125375 to 117543 bytes: -7832 bytes. This is linked executable text, including harness/tables, not a measurement of hot instruction-cache footprint. Unpack alone accounts for exactly 384 bytes.

## Full package gate and timing

Mac and Pi checks pass: KEM, required public ABI, canonical/failure paths, 4096 small-NTT differential cases, support oracle, zeroization and exact KAT. Legacy custom-ABI test exceptions remain explicitly inventoried, not silently reclassified as public ABI successes. Required public ABI failures are zero. KAT req/rsp SHA-256: `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

Four alternating SUPERCOP rounds; median of round medians:

| Leaf | Keygen | Encap | Decap |
| --- | ---: | ---: | ---: |
| G5 baseline | 36352.5 | 37152 | 32501 |
| Unpack-only | 36335.5 | 37140 | 32493.5 |
| Final candidate | 36377.5 | 37128 | 32513.5 |

Final deltas are +25 / -24 / +12.5 cycles. These small full-KEM changes do not establish a stable speedup; one final Encap round was slower than baseline. Keep the clear single-component unpack result separate from promotion claims. The support fix and cleanup are independently reviewable.

Pi: `pi@100.99.191.9`, Cortex-A76 core 3, Linux 6.18.33+rpt-rpi-2712, GCC 14.2.0. SUPERCOP flags: `-march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -gdwarf-4 -Wall`. Recorded throttling is always 0x0; maximum recorded temperature 68.6 C.

## Reproducibility and artifact policy

Local experiment directory is beside this report. Remote root is `/home/pi/gt768-pack-util-cleanup-20260908-e20`; package is `NTRU+768` underneath it. Remote scripts run as `python3 trace.py`, `python3 run_pack.py`, `python3 final_gate.py`, then `python3 seal.py` after syncing final sources. `final_gate.py` uses the existing `/home/pi/gt768-four-gates-20260907-e09/common.py` SUPERCOP driver. Exact commands, build options and source references are in these scripts. Local package gate: `make check` in `ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768`.

`cleanup_patch.py` emits a patch against a fresh champion checkout; do not replay it against the already modified candidate. Source changes are retained by candidate commit, not duplicate source snapshots. `mapping-proof.json`, `pack-results.json`, `mod3-trace.txt`, `final-summary.json`, `final-runs-summary.json` and `sealed.json` retain decisions/results/identity. Objects, executables, generated candidates, raw PMU logs and SUPERCOP workspaces remain under ignored `.build`. `sealed.json` confirms the final source exports byte-identically to the measured final leaf.

Next decision: review the semantic fix/cleanup and unpack change for promotion independently of speed claims. Do not promote P0/P1 or infer an Official speedup from this gate.

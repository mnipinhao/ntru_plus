# G5 GT Production vs Official — 2026-09-08

Experiment ID: `gt768-g5-official-profile-20260908-e19`.
Decision: benchmark/profile audit complete; no optimization or source promotion in this run.

## Compared sources

- GT: `aarch64-production`, `ce617c87a39412958cddea17f10809fd2e0b3a3f`.
  Maintained G5 source commit: `b6b7854347417d012e229f8e23f8b795d0959d63`.
- Official: `pi@100.99.191.9:/home/pi/supercop-20260627/crypto_kem/ntruplus768/aarch64`.
  SUPERCOP snapshot, radix-3/radix-2, not Good-Thomas and not an asserted upstream Git main commit.
- All 19 Official file hashes match the earlier e10 snapshot. Benchmark leaf omits its two goal markers.
- Local production package hashes match the package copied to Pi. `identity.json` and
  `file-audit.json` retain exact identities; exporter provenance is in `.build/gt-production.export.json`.
- This is a measurement-only record, stored outside the production package. The production branch
  remains at the revision above. No candidate branch was needed because no kernel candidate was created.

## Full SUPERCOP benchmark

Pi5 Cortex-A76, core3, Linux 6.18.33+rpt-rpi-2712, GCC 14.2.0.
The real `run-ntruplus768-aarch64.sh` runs in an isolated SUPERCOP tree.
Four rounds alternate implementation order. Each run is the median of three SUPERCOP cycle rows;
the table is the median of the four run medians. Both leaves use:
`-march=native -mtune=native -O3 -fwrapv -fPIC -fPIE -gdwarf-4 -Wall`.

| Operation | GT G5 cycles | Official cycles | Cycles saved | Improvement |
|---|---:|---:|---:|---:|
| Keygen | 36390.5 | 38445 | 2054.5 | 5.34% |
| Encap | 37162.5 | 38600 | 1437.5 | 3.72% |
| Decap | 32487 | 33552.5 | 1065.5 | 3.18% |

| Operation | GT run-median range | Official run-median range |
|---|---:|---:|
| Keygen | 36377–36405 | 38430–38488 |
| Encap | 37155–37184 | 38588–38619 |
| Decap | 32474–32500 | 33539–33557 |

GT wins every operation in every round. These ranges are not confidence intervals.
All recorded benchmark pre/post throttle values are 0x0; maximum recorded benchmark
temperature is 69.2 C. Full rows, metadata and remote raw-result paths are in
`benchmark-summary.json`. These gains are the entire GT-versus-Official difference,
not gains attributable solely to G5. The older G5 gate isolated approximately 140 Encap cycles.

## Correctness and measurement scope

Fresh production `make check` passed on Pi: release/manifest, KEM, required ABI,
canonical/failure tests, small-input tests, zeroization audit and expected KAT.
Both profiler object closures separately passed exact KAT req/rsp and matching workload sinks.
KAT response SHA256: `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.
Production sources retain the Official-aligned clearing policy. This is not a no-clear build.
The two implementations have different scratch objects, so equal policy does not imply equal
byte counts for all operations. This run does not claim a new constant-time proof.

Profiler uses unchanged kernels and a deterministic RNG workload through public KEM APIs.
Keygen retains retries, Encap uses a fixed valid PK and changing coins, Decap a fixed valid CT/SK.
This is hot-path profiling; invalid-input/cold-cache costs are not represented.
PMU totals use three 100000-operation runs; counter groups avoid multiplexing.
Encap/Decap self samples use cycles:u period 100003; Keygen uses cpu-clock:u 997Hz,
three 500000-operation runs, following e11's finding of cycle-period attribution bias.
All 18 accepted sample runs have zero lost samples. Component percentages are equally weighted
across repetitions. Keygen percentages are on-CPU time, not exact hardware-cycle partitions.
Whole-program PMU totals include initialization/loop/sink overhead and therefore are a different
protocol from the SUPERCOP numbers above.

## Profiler component shares

Each percentage is relative to that implementation's own total; rows are not independent kernel timings.

| Keygen component | GT | Official |
|---|---:|---:|
| Hash/SHAKE | 47.09% | 44.65% |
| Base inversion | 18.96% | 18.46% |
| Forward NTT | 14.78% | 14.67% |
| Base multiplication | 9.83% | 11.56% |
| Packing | 4.32% | 5.86% |

| Encap component | GT | Official |
|---|---:|---:|
| Hash/SHAKE | 73.81% | 71.25% |
| Two Forward NTTs | 10.93% | 14.90% |
| Basemul-add | 5.51% | 5.85% |
| Two packs combined | 4.49% | 3.79% |
| Checked PK unpack | 1.30% | 0.67% |

Using the separate PMU totals only as an approximate scale, Encap Forward accounts for
4070 vs 5764 cycles; basemul-add 2052 vs 2265; pack 1671 vs 1466; checked unpack 486 vs 260.
Thus Forward is the largest advantage, while serialization/decode consume part of that saving.
These estimates do not establish exact latency or a causal instruction-level decomposition.
Hash is approximately 27477 vs 27561 cycles; its higher GT share is mainly the smaller total.

| Decap component | GT | Official |
|---|---:|---:|
| Hash/SHAKE | 48.48% | 46.14% |
| Forward NTT | 16.51% | 17.38% |
| Inverse NTT | 10.87% | 10.88% |
| Fused checked decode + first product | 6.64% | separate below |
| Base multiplication | 6.10% (verification only) | 11.89% (both products) |
| Checked unpack | 0.95% (remaining hinv decode) | 2.78% |
| Packing | 4.62% | 4.47% |

GT decode+products aggregate to 13.69%, Official 14.67%; comparing only the basemul row
would incorrectly omit GT's fused first product. Full components, repeat ranges, source/entry
attribution and sample counts are in `profile-summary.json`.

## Unsampled PMU

| Version/operation | cycles/op | instructions/op | ld_spec/op | st_spec/op | stall_backend/op |
|---|---:|---:|---:|---:|---:|
| GT Keygen | 36373 | 83252 | 10716 | 6507 | 11230 |
| Official Keygen | 38430 | 80332 | 9733 | 6220 | 13221 |
| GT Encap | 37228 | 106776 | 15252 | 9226 | 6905 |
| Official Encap | 38682 | 103953 | 14556 | 8627 | 8845 |
| GT Decap | 32433 | 71994 | 9279 | 5787 | 10453 |
| Official Decap | 33461 | 72245 | 9142 | 5524 | 11131 |

`ld_spec`/`st_spec` are speculative events, not retired memory-op counts.
GT Encap executes more instructions but has fewer backend-stall events and higher IPC
(about 2.87 versus 2.69). This is consistent with better dependency scheduling, not proof
that one particular schedule change caused the whole difference.
Profiler executable `size text`: GT 105537, Official 23193 bytes. This includes linked
helpers/tables and harness; it is not the hot instruction working set. GT remains much larger.

## Source file mapping and actual changes

Paths below are relative to the current flattened production NTRU+768 package, not the old asm/internal tree.

| Official file | GT file(s) | What differs |
|---|---|---|
| kem.c | kem.c, kem_api.S | Public ABI wrapper and operation-specific private calls; Encap m/output alias, Decap scratch union and fused decode/product. Wire format and KAT remain the same. |
| ntt.s | ntt.S | GT 3×32 Good-Thomas Forward paths with Encap block-major, Keygen CQ and Decap consumer-specific output. Encap selects G5 small-lazy twice. Decap inverse remains the previously audited Official-derived arithmetic/table family, not a newly optimized GT inverse. |
| base.s | base.S, keygen.c | Encap Q31 basemul-add; Decap D1 direct final reduction; packed decode/first-product fusion; CQ Keygen prepare/tree/fqinv/finish pipeline. |
| poly.c | keygen.c, base.S | Official NEON batch-inversion orchestration corresponds to GT CQ helpers/assembly. Both already use batch inversion. |
| pack.s | pack.S | Separate Encap reduced/loose pack, checked block-major PK decode, Keygen CQ pack, Decap decode/pack. All serialize the same canonical bytes. |
| cbd.s | cbd.S | Adapted symbols/ABI and assembly packaging; sampling/SOTP behavior preserves KAT. This run does not claim a new CBD speedup. |
| add.s | support.S, decap_add.S | Generic support and Decap-specific subtraction; GT private pointer/layout contracts differ. |
| crepmod3.s | support.S | Centered-mod3 support consolidated with GT ABI. |
| fips202.c | fips202.c | Exactly identical after replacing util.h with secure_clear.h and secure_clear with gt_secure_clear. No new SHAKE arithmetic. |
| fips202.h | fips202.h | Byte-identical. |
| symmetric.c/h | symmetric.c/h | Hash constants/header organization and clear-helper adaptation; same hash sizes and domain separation. Inactive CE include is not enabled by this build. |
| util.h | secure_clear.h | Same Linux explicit_bzero policy; GT adds portable fallback/declaration and optional audit hook. Hook is not enabled in timed builds. |
| api.h | api.h, kem_api.S | Same public KEM signatures/sizes; visibility/ABI organization differs. |
| params.h | params.h | Same N=768, q=3457 and byte sizes; GT header omits Official NTRUPLUS_D=4 macro. Quartic basecase is still used. |
| poly.h | poly.h, ntt.h, ntt_internal.h, keygen.h, decap_verify.h, layout.h | GT makes operation-specific layout/scaling/range/alias contracts explicit. Same function name is not sufficient to interchange internal buffers. |
| architectures | scripts/export_supercop.py | Exporter emits aarch64 marker and private namespace, Linux-preprocessed assembly and public adapter. |
| goal-constbranch / goal-constindex | no copied goal markers | SUPERCOP packaging metadata; not arithmetic files. No new constbranch/constindex proof is asserted. |

GT additional support includes `keygen_lambda.c`, `basemul_lambda.c`, `decap_verify.c`,
standalone `randombytes.c/h`, `Makefile`, `test/`, `kat/`, `scripts/`, documentation and manifest.
The standalone randombytes implementation is excluded from the SUPERCOP export; each benchmark
uses its harness RNG. `file-audit.json` enumerates all Official file mappings and SHA256 values.

G5 specifically changes the two Encap calls to `poly_ntt_encap_small_lazy`:
input [-2,2], output [-21050,21050], same block-major layout/mod-q scaling and exact alias.
The original raw-bit-exact small endpoint remains available. G5 does not change Keygen or Decap arithmetic.

## Reproduction and artifacts

Remote root: `/home/pi/gt768-g5-official-profile-20260908-e19`.
`run_gate.py` reuses the pinned e09 SUPERCOP driver and e11 profiler mechanics, with the
current maintained exporter and updated symbol classification. Copy the exact package into
`NTRU+768` under a fresh root, then run `python3 -u run_gate.py` followed by `python3 summarize.py`.
The script requires fresh output leaf directories. `run_profile.py` is the inherited harness;
invoke it through `run_gate.py` so the new paths and revision are applied.

Persistent: this report, identities/hashes, benchmark/profile summaries, scripts and workload.
Ephemeral: `.build/` contains local sample text, maps, logs and Official audit copy; remote
`.build/` also contains binaries, perf data and isolated SUPERCOP outputs. Production source
is identified by commit, not another persistent source copy. No push was performed.

# NTRU+768 / NTRU+1152 Official AVX2: 2-op freeze in `poly_tobytes` on top of the lazy Forward

Date 2026-09-23, branch `official-opt-lazy-864-1152` (from `369d82a` = `origin/avx2-official-opt`, not pushed).
This covers Phase A (code and correctness) and a same-ELF diagnostic. No SUPERCOP campaign and no
Native timing were run.

| | NTRU+768 | NTRU+1152 |
|---|---|---|
| Experiment | `NTRU+768/experiments/avx2_official_opt_freeze_001` (new) | `NTRU+1152/experiments/avx2_official_opt_001` (`freeze2op:` section of STATUS.yml) |
| Candidate | `avx2-officialopt-lazy-freeze-768-exp001` | `avx2-officialopt-lazy-freeze-1152-exp001` |
| Control | freeze-only (Official Forward + new tobytes) | same |
| Lazy Forward | common generator, instruction stream equal to the 768 qual001 candidate | existing lazy-only candidate (unchanged) |

All of these directories are under `ntruplus-ntt-Optimized/Additional_Implementation/avx2/`.
The shared tooling is in `common/official_opt_lazy/`: `freeze2op.mk`, plus the tools and tests named below.

## The change

In Official `poly_tobytes` (the pristine `pack.s:1-144` for both 768 and 1152), each loop iteration freezes 8 registers.
Each freeze is a Barrett step `vpmulhrsw _16xv; vpmullw _16xq; vpsubw` followed by a 3-op add of q:
`vpsraw $15; vpand q; vpaddw`. The candidate replaces every 3-op add with

    vpaddw _16xq, X, T      # T = b + q
    vpminuw T, X, X         # X = min_u(b, b + q)

The registers and grouping stay the same: 4 `vpaddw` then 4 `vpminuw` where Official has 4/4/4 lines.
The saving is 8 instructions per iteration: 48 per call on 768 (6 iterations) and 72 on 1152 (9 iterations).
`kem.c` calls `poly_tobytes` 7 times (keypair 3, enc 2, dec 2). No other pinned source calls it.

This is correct iff the Barrett output b lies in (-q, q).
`tools/prove_freeze_2op.py` checks this over all 65536 int16 inputs with bit-exact word semantics. It is the shared copy of the NTRU+864 tool.
Its C twin `tests/test_freeze_2op.c` runs the real instructions against the linked constants.
Result for both parameters: q=3457, V=9, 8 sites, b in [-3291, 3291], 2-op == 3-op bit for bit, output == x mod q.
The proof holds for every int16 input, so it also covers the lazy-Forward outputs that feed `poly_tobytes` directly (enc `ct <- r_hat`, dec `buf1 <- f_hat`).

## Implementation

- `tools/generate_tobytes_freeze2op.py --param {768,1152}` reads the pinned `pack.s` and `kem.c` (sha256 pinned). It writes:
  - `asm/ntruplus{N}_officialopt_tobytes_freeze2op.s` (`.p2align 5`, `.type`, `.size`, namespaced loop label);
  - the overlay `src/kem_lazy_freeze2op.c` (`#define poly_tobytes ...` + `#include "kem_lazy.c"`);
  - the overlay `src/kem_freeze2op.c` (same rebinding on the Official `kem.c`).

  Before replacing anything, the generator asserts:
  - exactly 8 sites, each the exact 3-op sequence on the `_16xq` register;
  - each site's register comes from a complete Barrett step and is untouched in between;
  - each site's temporary is dead afterwards;
  - the loop bound is 2N, the stride 256, and the trip count 6 or 9.

  It then checks that the line diff is exactly 24 removed lines and 16 added lines, with every other line equal and in order, and that generation is deterministic. `--check` verifies the committed files.
- 768 lazy Forward: `generate_forward_caller_lazy.py` now also takes `--param 768`. It gained 768 hash pins, a per-parameter trip count (6) and a per-parameter label set (768 has no `_looptop_j_2`).
  The 864 and 1152 outputs are unchanged (`--check` passes; lazy-only `make phase-a` re-run for both).
  To support 768, `audit_forward_caller_lazy.py`, `range_proof/prove_forward_lazy.py`, `tests/test_forward_caller_lazy.c` and `scripts/check_supercop_experiment.py` gained 768 entries.
  The 768 lazy bounds (`EXPECTED_LAZY[768]`) come from this tool. Its keygen/encap/decap maxima (15252 / 15251 / 13636 / 14449) and `c - f_hat` maximum 17905 equal the independent Codex round-4 lane proof in `NTRU+768/experiments/avx2_official_opt_001/STATUS.yml`.
- 768 upstream was imported fresh with `scripts/import_supercop_ntruplus.py --destination`. Its tree hash `8db00172...` matches `bench/supercop.lock`, and its content is identical to Codex's import.
  Nothing under `NTRU+768/experiments/avx2_official_opt_001/` was written; that directory was only read.

## Gates (all pass, both parameters)

| Gate | Result | Evidence (per experiment) |
|---|---|---|
| 1 generator `--check`, structural diff, proof | pass (see above) | `results/freeze2op-phase-a/freeze2op-generation.json`, `freeze-2op-proof.json` |
| 2 tobytes differential vs Official | 242608 polys byte-exact | `results/freeze2op-phase-a/closure-tests.log` |
| 2b mutation check | 5/5 one-line mutants rejected, unmutated passes | `freeze2op-mutation-check.json` |
| 3 KEM candidate and control vs Official | 100 vectors byte-exact; invalid/noncanonical cases matched; retries covered | `closure-tests.log` |
| 4 ASan + UBSan + LSan | pass for all 6 freeze binaries (and the 768 lazy ones) | `closure-tests.log` |
| 5 linked audit | pass | `freeze2op-linked-summary.json` |
| 6 (768 only) lazy stream == qual001 | pass | `lazy-stream-equality.json` |

Details for the table rows:

- **Gate 2 coverage.** The differential covers:
  - every int16 value at every position (`a[i] = base + K*i`, all 65536 bases, K = 0, 1, 40503);
  - 20000 random polys and 2000 edge-set polys;
  - the lazy-Forward envelopes and 4000 real lazy-Forward outputs;
  - canaries, input immutability and wire misalignments 0..31;
  - guard pages (PROT_NONE before and after both the wire array and the poly, adapted from `NTRU+864/.../tests/test_codec_guard.c`).

  Each case also checks that the `frombytes` round trip returns x mod q.
- **Gate 3 retries.** The KEM test uses a forced g retry and an f-retry injection. NTRU+1152 also saw its natural f/g retries in the 100 vectors (40 / 45). NTRU+768 saw none in the 100 vectors, so the injection is its only retry coverage.
- **Gate 5 audit contents.** In the linked ELF:
  - the symbol is 32-byte aligned; 619 bytes; 114 rows against Official's 122;
  - the row diff is exactly −8 `vpsraw`, −8 `vpand`, −8 `vpaddw`, +8 `vpaddw q`, +8 `vpminuw`;
  - no stack use, no calls, no vzeroupper;
  - candidate KEM: 7 references to the new symbol, **0 to `poly_tobytes`**, 6 to the lazy Forward, 0 to `poly_ntt`;
  - freeze-only control: 7 / 0, and 6 to `poly_ntt`;
  - lazy-only KEM unchanged: 7 to `poly_tobytes`.
- **Gate 6 detail.** The normalised text matches: 295 instructions, with labels renamed to `L<k>` and the entry to `FUNC`. The assembled `.text` bytes match (1633 bytes, sha256 `0a2f5746…`), and so do the 5 relocations. The reference is `NTRU+768/.../avx2_official_opt_001/asm/ntruplus768_officialopt_ntt_caller_lazy.s` (sha256 `efb8a1e1…`, equal to qual001 `ntt_caller_lazy.s`), read only. A one-register mutation is rejected.

The 768 lazy gates were also run: differential (25375 cases), KEM, sanitizers, audit, and range proof.
Their evidence is in `results/phase-a/`.

## Same-ELF diagnostic (`supercop-derived`, not Native)

Setup:
- `common/official_opt_lazy/bench/bench_freeze2op.c`, O3GC recipe;
- cpucycles from the disposable campaign `supercop-campaign-lazy-864-1152-20260923-001`, read only;
- CPU 1, ASLR on, 31 fresh launches per link order, 384 observations per variant per launch;
- every batch run under `phase_b_batch.py`; all 6 batches were clean on attempt 0.

Deltas are pooled StQ2 (cycles), followed by the number of favourable launches out of 31.

### Component tobytes (freeze2op − Official)

| | normal | reversed |
|---|---|---|
| 768 (Official 427) | −16.9 (31/31) | −18.0 (31/31) |
| 1152 (Official 531) | −22.9 (31/31) | −24.2 (31/31) |

### KEM: lazy+freeze2op − lazy-only (the freeze2op increment)

| | 768 normal | 768 reversed | 1152 normal | 1152 reversed |
|---|---|---|---|---|
| keypair | −63.3 (29) | −33.8 (27) | −197.8 (21) | −54.4 (22) |
| encap | −53.5 (29) | −20.7 (25) | **+52.3 (2)** | −193.1 (31) |
| decap | −26.2 (30) | −46.6 (31) | −90.3 (31) | −99.5 (31) |

### KEM vs Official (lazy-only / lazy+freeze2op / freeze-only)

| | 768 normal | 768 reversed | 1152 normal | 1152 reversed |
|---|---|---|---|---|
| keypair | −204 / −268 / −41 | −209 / −243 / −31 | −363 / −561 / −165 | −365 / −419 / +22 |
| encap | −184 / −237 / −48 | −107 / −127 / +10 | −419 / −366 / −121 | −232 / −425 / −57 |
| decap | −221 / −247 / −38 | −214 / −261 / −55 | −339 / −429 / −139 | −190 / −290 / +46 |

### Seed-matched paired Keypair, lazy+freeze2op (B) − lazy (A)

Setup:
- shared harness `bench_keypair_seedmatched.c`;
- identical coins, ABBA/BAAB order;
- 15 launches × 2000 iterations per ELF.

| | normal link | swapped link | pooled (30 launches) |
|---|---|---|---|
| 768 | median −46.5, mean −46.7 [−61.3, −32.3], 15/15 | −58.0, −57.8 [−71.6, −44.0], 15/15 | −52.5, −52.3 [−62.7, −42.4], 30/30 |
| 1152 | −41.0, −44.2 [−61.2, −25.6], 15/15 | −129.5, −141.5 [−166.2, −119.0], 15/15 | −84.5, −92.8 [−115.2, −70.9], 30/30 |

### Reading

- The component saving is real and robust: about 17–18 cycles per call on 768 and 23–24 on 1152, favourable in 31/31 launches in both link orders.
  The count predicts 48 or 72 instructions fewer per call (about 0.35 cycles per removed instruction).
- **768 whole-op effect.** All six increments are negative, and the seed-matched Keypair −52 [−63, −42] matches the expected 3 × 17 ≈ −51.
  The absolute size (20–60 cycles on 20k–64k-cycle ops, ≤ 0.2 %) is at the level that link placement moves: encap lazy-only − Official is −184 in normal order but −107 in reversed.
- **1152 whole-op effect.** Placement dominates. Encap is +52 (2/31) in normal order but −193 (31/31) in reversed.
  The seed-matched Keypair is −41 normal versus −130 swapped (expected about 3 × 23 ≈ −69), and the freeze-only control changes sign between orders.
  Only decap is consistently negative (−90 / −100, 31/31 both orders).
- Verdict: correctness is complete, and the component win is real. The end-to-end effect is small and within placement noise for 1152 encap, so it is not established.
  Settling it needs Native SUPERCOP launches (not run by instruction). No promotion.

## Reproduce

```
A=ntruplus-ntt-Optimized/Additional_Implementation/avx2
T=../../../common/official_opt_lazy/tools
# Phase A (per experiment E = $A/NTRU+768/experiments/avx2_official_opt_freeze_001 or
#                            $A/NTRU+1152/experiments/avx2_official_opt_001)
(cd $E && make phase-a && make freeze-phase-a)      # lazy gates + freeze gates (incl. freeze-mutate, 768: lazy-stream-equal)
(cd $E && make freeze-record)                       # copies curated evidence to results/freeze2op-phase-a/
# Diagnostic (p = 768 or 1152), from $E after `make freeze-bench freeze-bench-keypair`:
python3 $T/phase_b_batch.py --result-dir results/freeze2op-diag-normal-TAG --metadata metadata.json -- \
  python3 $T/run_freeze2op_diag.py --param $p --experiment . --launches 31 --result-dir {RESULT}
python3 $T/phase_b_batch.py --result-dir results/freeze2op-diag-reversed-TAG --metadata metadata.json -- \
  python3 $T/run_freeze2op_diag.py --param $p --experiment . --launches 31 --binary build/bench_freeze2op_swapped --result-dir {RESULT}
python3 $T/phase_b_batch.py --result-dir results/freeze2op-keypair-seedmatched-TAG --metadata metadata.json -- \
  python3 $T/run_freeze2op_keypair_seedmatched.py --param $p --experiment . --launches-per-elf 15 --iterations 2000 --result-dir {RESULT}
```

Deviations and notes:
- The shared KEM test prints its "caller-lazy KEM byte differential" banner for the freeze binaries too. The binary name tells you which object was tested.
- The freeze2op proof JSON records absolute source paths, as the NTRU+864 version does.
- NTRU+768 observed no natural keygen retries in the 100 vectors, so the injected f and g retries are its only retry coverage.

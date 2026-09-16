# Fixed-scale physical gate — 2026-09-09

Status: investigate. Production is unchanged. Pi5 full-path timing is outstanding.
Update 2026-09-10: Pi5 correctness and paired PMU completed; see
BENCHMARK-20260910.md. The connection-blocker notes below are historical.
Two SSH attempts to pi@100.99.191.9 timed out on port 22, including a bounded
10-second connection check. No upload or Pi5 measurement completed this turn.

## Slothy

Existing-region replacements: numerator and finish. Canonical checkout
/Users/chenpinhao/slothy, revision c9fea6c179454536c92eaa50f90e0f9d8f8152dd.
It has no local venv; the existing associated environment is
/Users/chenpinhao/slothy_and_ra/.venv/bin/python, with PYTHONPATH pointing to
the canonical checkout. The driver asserts the imported architecture path.
User's earlier local-execution authorization applies.

Functional RA without reorder, then fixed-RA bounded-window Cortex-A76 scheduling;
30-second solve bounds, no spills. No software pipelining or whole-function
solver estimate. All generated sources/logs are in baseinv_num/ and baseinv_finish/.

The first static checker found missing register-contract comments. They were
added, static checks passed, and both Slothy runs were repeated on the corrected
sources. Final symbolic checks have no errors; finish has three cmgt classification
warnings, manually reviewed as the unchanged centered-output correction.

The generic parse-slothy-log.py reports fail because it matches normal search
infeasible/timeout strings, and reports 0 from functional RA as a best cycle.
Neither is a meaningful whole-kernel timing result. Both actual runs exited
successfully, produced allocation and scheduled artifacts, and end in
split_heuristic_full:OK!. Do not use the parser's 0 or sum window cycle estimates
as a performance claim. This ambiguity remains a promotion limitation.

## Physical result

| Region | Instructions excluding ret | Q loads | Q stores | Spill |
|---|---:|---:|---:|---|
| numerator | 114 | 4 | 4 | no |
| finish | 57 | 4 | 3 | no |

No internal calls, stack accesses or unresolved symbolic registers in emitted
code. These counts preserve the model's 432-instruction saving per BaseInv.
Whole-operation public wrapper and scratch clearing are unchanged.

Constants and internal ranges differ from the baseline as documented by proof.json;
external input/output, memory and ABI contracts are preserved. No promotion or
approval of broader contract changes is inferred. The baseline-contract.yml
records the old arithmetic; the candidate/kernel contracts record the new one.

## Native correctness

The isolated package in build/package imports only the two generated cores and
refreshes its source manifest. It does not modify production.

Mac assembly execution passed:
- 64 valid/tampered KEM cases.
- 100 KAT cases, unchanged hash
  0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c.
- BaseInv 808 cases (517 success /291 failure), every zero-leaf position,
  exact alias, canaries, AAPCS preservation and scratch wipe.

These tests are actual allocated/scheduled assembly tests, not just symbolic
models. They do not replace Pi5 GCC/rejection and full-path benchmark gates.

## Reproduction

    PYTHONPATH=/Users/chenpinhao/slothy /Users/chenpinhao/slothy_and_ra/.venv/bin/python experiments/gt864-native-asm/baseinv-fixed-scale/optimize.py baseinv_num
    PYTHONPATH=/Users/chenpinhao/slothy /Users/chenpinhao/slothy_and_ra/.venv/bin/python experiments/gt864-native-asm/baseinv-fixed-scale/optimize.py baseinv_finish
    python3 experiments/gt864-native-asm/baseinv-fixed-scale/prepare-package.py
    python3 experiments/gt864-native-asm/verify-production-mac.py experiments/gt864-native-asm/baseinv-fixed-scale/build/package /tmp/gt864-fixed-physical-mac
    python3 experiments/gt864-native-asm/verify-integrated-components.py /tmp/gt864-fixed-physical-mac

Next: upload the isolated package to Pi5, freeze the cleanup-aligned baseline,
run pi-integrated.py --checked and pi-profile.py, then complete BaseInv stage
measurement. Retain the specified SUPERCOP 20260831/aarch64 comparator.

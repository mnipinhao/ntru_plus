# E26 — Production source readability cleanup

Baseline: aarch64-production 3f35aae91d3ca277dbf87167b13856d447ca7f78.
Action: requested production cleanup; no arithmetic, layout, ABI or clear-policy change.

## Changes

- Remove duplicate initial section selection in ntt.S / base.S.
- Keep the single poly_sub prototype in poly.h; decap_verify.h already includes it.
- Replace obsolete BEGIN/END original-file wording with explicit section markers.
- Replace old whole-source hashes / Wave 8 headlines with current contract descriptions.
- Correct generic inverse commentary: it is not the active Decap inverse.
- Explicitly mark old same-address aliases and boundary markers as compatibility symbols.
  Retain them: their external consumers cannot be ruled out by an in-repository search.
  Darwin underscore symbols and all executable labels remain unchanged.
- Update source manifest. Preserve range, table-generation and scheduling-contract comments.

## Why retain the generic / exact routines?

| Entry | Actual purpose |
|---|---|
| poly_ntt_loose | Generic loose transform; test_ntt_small.c compares small variants against it. Shares assembly core with Keygen CQ. |
| poly_ntt_encap_small | Input restricted to [-2,2]; raw bytes must match generic output, including aliasing. Used in small differential and ABI tests. |
| poly_ntt_encap_small_lazy | Actual Encap path; need not match raw representatives, but must match modulo 3457, satisfy [-21050,21050], and pack identically. |
| poly_basemul / poly_invntt | Retained raw-factor/block-major interface pair, exercised by ABI sentinel. ABI checks are NOT a mathematical product/round-trip oracle. |

Keygen uses its CQ entries. Decap uses poly_basemul_decap and poly_invntt_decap_scale
(and the fused checked decode/first multiplication). The ordinary KEM does not
execute all retained generic variants. Retaining source for tests does not imply
it must remain in every production binary: a future test-only/section split can
be considered, but requires tracing shared bodies/tables and preserving tests.
This cleanup does not perform that split or claim runtime savings.

## Validation

- Mac and Pi: complete make check passed (manifest, KEM, ABI, canonical,
  small-input, support, zeroization, expected KAT req/rsp).
- Every top-level C / assembly object rebuilt before/after with
  cc -O3 -fomit-frame-pointer: whole-object bytes identical on each host.
  This also preserves symbols, tables, relocations and executable bytes.
- Debug line metadata deliberately omitted from equality comparison because
  comments move source line numbers.
- Results/hashes: results.json. Reproducer: verify_objects.py OLD NEW OUTPUT_DIR.
- No fresh cycle benchmark: machine-code-equivalent cleanup, not a speedup.
- Raw builds: /tmp/gt768-source-readability-cleanup-20260908-e26 on Mac;
  /home/pi/gt768-source-readability-cleanup-20260908-e26/.build on Pi.
- Historical provenance remains recoverable from Git.

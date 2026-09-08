# E27 — Generic pair moved to test/reference

Baseline: aarch64-production 52117af3733f842e70e2cea322268320bfb97ff0.
Scope: requested package split, no arithmetic/Forward NTT/clear-policy change.

## Implementation

- Move the complete generic basemul section from base.S to test/reference/basemul.S.
- Move the complete generic inverse section, macros and private tables from
  ntt.S to test/reference/invntt.S. No duplicate source remains.
- Keep gt_rowbitrev_lambda in basemul_lambda.c: production Encap basemul-add uses it.
- Add REFERENCE_ASM only to the existing ABI test link. No tests removed.
- Move generic declarations from poly.h into test/reference/poly_reference.h,
  included by test/test_abi.c.
- Update release checker, source manifest and implementation documentation.
- Export rejects any test source in KEM_SOURCES and rejects generic pair
  symbols in the compiled definition set. Reference headers are outside
  the exported top-level header set.

## Validation

Mac and Pi complete make check: PASS (manifest/release, KEM, ABI, canonical,
small-input differential, support, zeroization, KAT).
Expected rsp SHA-256:
22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8.

Pi ELF inspection with verify_linux.py:

- Every nonempty allocated PROGBITS section retained in base.S / ntt.S is
  byte-identical to baseline, including embedded tables.
- Retained relocation offsets/types/symbol names/addends are identical;
  incidental ELF symbol-table indices are excluded.
- Moved .text.module_base_body: 704 bytes, reference bytes and relocations identical.
- Moved .text.module_invntt_body: 13,712 bytes, reference bytes and relocations identical.
- Total excluded from production objects: 14,416 bytes of these sections.
- Export all C/assembly objects compile. Generic basemul/inverse and inverse
  aliases absent, gt_rowbitrev_lambda present.
- Exported objects link with the package KAT harness, without section GC;
  expected req and rsp both match exactly.

No fresh benchmark or cycle claim. Link addresses may move despite identical
section contents. Builds with section GC already excluded these unused sections,
so 14,416 bytes is not a guaranteed additional saving in every final executable.
Mac correctness is tested natively; the per-section binary/relocation comparison
is specifically Linux ELF.

Artifacts:
- results.json: persistent section hashes and export result.
- verify_linux.py: reproducer, assumes the fixed E26 baseline staging on Pi.
- Mac raw build: /tmp/gt768-test-reference-split-20260908-e27/mac.
- Pi raw build/export: /home/pi/gt768-test-reference-split-20260908-e27/.build.
- Baseline staging: /home/pi/gt768-source-readability-cleanup-20260908-e26/.build/NTRU+768.

Decision: package split gates pass. Test-only generic API is intentionally no
longer exported by the production leaf; external users requiring that old
generic interface must explicitly link test/reference. The three KEM API
entries and their contracts are unchanged. No push performed.

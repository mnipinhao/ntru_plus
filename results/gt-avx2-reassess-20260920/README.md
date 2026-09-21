# GT/AVX2 reassessment evidence

Authoritative outputs:

- `reassessment-summary.json`: machine-readable decision record.
- `serious/*`: corrected 9-fresh-process O3GC component campaigns.
- `gate-a/pmu2-*`: PMU v2 records with matched mode-dispatch baseline and
  equal 4096-bank Forward residency.

The other `gate-a/*-v2`, `*-v3`, and `pmu-*` directories are retained as the
audit trail that exposed the ownership/residency mismatch.  They are
superseded and must not be used as headlines.  Native KEM results remain in
`../ntruplus-avx2-768-864-1152-20260920/`; this reassessment did not rerun or
rewrite them.

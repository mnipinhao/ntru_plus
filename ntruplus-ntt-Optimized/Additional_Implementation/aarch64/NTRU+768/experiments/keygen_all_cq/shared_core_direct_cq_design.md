# Shared-Core Direct-CQ Design

Date: 2026-07-23

Status: default-off candidate; differential, ABI, full-KEM correctness, PMU,
and code-size gates pass. Production default remains unchanged.

## Real source boundary

The active forward NTT is not organized as all Stage12 followed by all
Stage345. It executes:

```text
shared prologue + Phase123 for all rows
  -> row0 Stage12 + Stage345
  -> row1 Stage12 + Stage345
  -> row2 Stage12 + Stage345
  -> shared epilogue
```

Therefore the safe shared boundary is immediately before row0 Stage12. The
generic and CQ suffixes each retain their exact arithmetic, reduction, and
store contracts.

## Internal dispatch contract

```text
poly_ntt:
  w2 = 0
  branch shared body

gt_experiment_poly_ntt_to_cq:
  w2 = 1
  fall through shared body

shared body:
  allocate existing 1696-byte frame
  save public selector at [sp, #8]
  run exact production Phase123
  load selector and branch to generic or CQ row suffix
```

`[sp, #8]` is unused by the production source. `[sp, #0]` remains the existing
Slothy GPR spill slot. The selector is public and fixed by the called symbol;
it is not derived from polynomial data.

## Static instruction model

| Region | Instructions |
|---|---:|
| shared prefix including prologue | 1303 |
| generic row suffix | 2382 |
| CQ row suffix | 2403 |
| shared epilogue | 9 |
| dispatch overhead | 7 |
| two separate full bodies | 7409 |
| generated dual body | 6104 |
| estimated instructions removed | 1305 |

The object also includes the NTT tables only once instead of once per complete
function body. Actual linked text size remains the deciding measurement.

## Measured outcome

The full measurements and build conditions are recorded in
`phase4-shared-core-results.md`. In summary, the shared object removes 8,432
bytes of linked text relative to the separate generic plus direct-CQ bodies.
Its CQ entry retires four extra instructions and costs about five cycles per
forward NTT in the endpoint harness. The generic entry retires six extra
instructions; no stable cycle regression was visible in the full-KEM runs.

## Hard invariants

- Generic suffix is copied exactly from production.
- CQ suffix is copied exactly from the audited direct-CQ candidate.
- Shared prefix and epilogue must be byte-identical between both sources.
- No `bl`, new scratch handoff, arithmetic change, reduction change, or
  secret-dependent branch is introduced.
- Production default does not link this object.

# Results

## Decision

Active polynomial cardinality by itself is not a demonstrated Encap
optimization on this target.

Profile B is the decisive comparison: it leaves one complete 1536-byte slot
untouched while retaining the same reserved frame and common hot-body address.
Its small directional median does not survive launch-level confidence testing,
and L1D pending cycles do not decrease.  Therefore the data-working-set premise
does not meet the proposed 20--50 core-cycle continuation threshold.

Profile C also fails to provide a stable full-caller win.  Removing the frame
storage changes the wrapper address/shape and reintroduces executable-delivery
interaction; its measurements cannot be treated as a pure stack-size credit.

## Correctness

- 1000 deterministic valid Encap cases matched production Clean GT byte for
  byte for A, B, and C.
- All 768 serialized public-key positions were separately set to `q=3457`.
  Return value, ciphertext clearing, and shared-secret clearing matched
  production for every profile.

## Static controls

- A/B share `working_set_057_reserved` and `encap_body`.
- B never passes the fifth `c` slot to the hot body.
- C uses the same `encap_body` and the same selected arithmetic symbols.
- Source scratch changes from `5 * 1536` to `4 * 1536` bytes.
- Disassembly places the deepest A/B and C polynomial objects at frame-pointer
  offsets `-0x1e70` and `-0x1870`: an exact `0x600 = 1536` byte difference.

The common noinline hot body intentionally adds the same helper boundary to all
profiles.  It makes A/B causal; this experiment is not a production export.

## 48-launch paired full-Encap gate

CPU 1, six balanced orders, 96 observations per profile per launch:

| Comparison | Meaning | Median delta | 95% bootstrap CI | Favorable launches |
|---|---|---:|---:|---:|
| B - A | Active 5 -> 4, frame fixed | -8.38 core cycles | [-68.58, +30.46] | 26/48 |
| C - A | Active 5 -> 4 and frame released | -0.38 | [-108.63, +27.17] | 24/48 |
| C - B | Additional frame release | -25.96 | [-58.79, +6.54] | 30/48 |

None passes.  The wide launch distribution is another reason not to promote
the old 031 result from a favorable median alone.

## Balanced PMU gate

Eighteen mirrored blocks, 20,000 calls per process:

| Comparison | Event | Median delta/call | 95% bootstrap CI |
|---|---|---:|---:|
| B - A | core cycles | -37.76 | [-331.89, +128.72] |
| | instructions | +3.59 | [-9.65, +143.54] |
| | IDQ uops not delivered | -34.38 | [-185.40, +38.27] |
| | L1D pending cycles | **+0.088** | [-0.157, +0.285] |
| C - A | core cycles | +69.12 | [-111.19, +205.45] |
| | L1D pending cycles | -0.024 | [-0.126, +0.178] |
| C - B | core cycles | +137.81 | [+11.14, +246.84] |
| | L1D pending cycles | -0.016 | [-0.171, +0.286] |

The PMU core-cycle estimates are noisy and C includes a different wrapper, so
the C-B positive result is delivery evidence rather than a reusable intrinsic
cost.  The mechanism-level fact is simpler: B does not reduce L1D pending
cycles and does not establish a latency win.

## Consequences

Close these directions:

- rearranging or merely reducing the number of simultaneously named polynomial
  objects while executing the same complete load/store work;
- promoting 031 on the basis of its old 13/16 favorable-launch result;
- interpreting the 055 L1D-pending excess as a directly recoverable active-frame
  cardinality cost.

Still open only with a new premise:

- delete an actual full-polynomial store/reload or operation class;
- prove a specific load instruction owns B3 or Decode stalls;
- reduce traffic, not only alias two storage lifetimes;
- obtain a consumer contract which removes a materialization.

Thus the 055 data-side pressure remains an observed production characteristic,
but neither 056 slot placement nor 057 active cardinality turns it into an
actionable 20--50 cycle optimization.

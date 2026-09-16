# D1-P3B9 results

Status: **paired-pack primitive passes; complete P3B6 integration pending.**

Both ordered boundaries canonicalize all 864 signed-int16 coefficients and
emit exactly 1296 bytes.  Local 256-case and Pi 128-case differential tests
include index tags, `INT16_MIN`, `INT16_MAX`, and random values.

## Cortex-A76 PMU

| ordered boundary | cycles | instructions | branches |
| --- | ---: | ---: | ---: |
| independent pack8 | 1197.671 | 1651.050 | 3.010 |
| paired pack16/ST3 | **1023.371** | **1335.050** | 3.010 |
| paired - independent | **-174.300** | **-316.000** | 0 |

The result is stable across all three paired repetitions and the Pi reports
`throttled=0x0`.

GCC emits 108 `TBL` and no `ST3` for pack8, versus zero `TBL` and 54 `ST3` for
pack16.  The pack16 object combines many adjacent inputs into `LDP`.  Neither
object has a coefficient spill; all stack references are normal GPR or
callee-saved SIMD ABI preservation.

## Integration constraint

Under P3B6's exact peak-16 input order, none of the 27 adjacent output pairs in
one top complete on the same input step.  The first member of every pair must
therefore be retained until its partner completes.  Keeping all such values in
registers reaches twenty pending complete vectors and is impossible beside the
partial-output frontier.

A bounded integration may store the first completed member to one fixed
16-byte slot per pair and reload it when the partner completes.  This requires:

- 27 partner stores and 27 partner loads per top;
- 108 extra memory instructions per complete two-top call;
- 432 bytes of reusable fixed-address scratch;
- no change to the 1296-byte external output or FR0 input contract.

The isolated 174.300-cycle saving is larger than this static memory overhead,
but the costs are not additive.  The next hard gate must implement this exact
scratch-integrated P3B6 route and measure the complete ToBytes boundary.  No
production or full-KEM promotion follows from the primitive result alone.

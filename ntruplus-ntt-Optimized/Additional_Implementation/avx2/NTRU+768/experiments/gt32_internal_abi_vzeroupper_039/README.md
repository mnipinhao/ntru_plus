# GT32-INTERNAL-ABI-VZEROUPPER-039

039 tests whether selected internal AVX2-to-AVX2 edges pay unnecessary
`vzeroupper` work.  It begins after 038 showed that loop compaction is not an
intrinsic speed mechanism for the tested GT bodies.

Production GT Clean is not modified.

## Causal method

The gate does not rebuild a shorter symbol and does not move any address.  It
builds one non-PIE control ELF, copies it byte-for-byte, and patches exactly
four bytes at one selected leaf epilogue:

```text
control:    c5 f8 77 c3    vzeroupper; ret
candidate:  c3 0f 1f 00    ret; unreachable three-byte NOP
```

The ELF length, symbol size, consumer address, constants, caller, and every
other byte are identical.  A same-return-address control replaces
`vzeroupper` with one three-byte NOP (`0f 1f 00 c3`) for the two initially
interesting edges.

Each result below is the median delta over 12 paired fresh launches, with
alternating control/candidate order and fixed CPU affinity.  Negative means
the no-`vzeroupper` candidate is faster.  Each program internally takes the
median of 31 TSC samples and 15 region-scoped PMU samples.  Retired
instructions provide a mechanism check, not a performance gate.

## Caller audit

Disassembly of the production-shaped C callers confirms that the compiler does
not insert another `vzeroupper` between the tested assembly calls.  It does
insert cleanup before SHAKE/libc boundaries; those generic/public boundaries
are deliberately outside 039.

## Fixed-address results

| Edge | TSC delta | Core-cycle delta | Retired instructions | Negative core launches |
|---|---:|---:|---:|---:|
| frontend -> NTT-M | -0.175 | -0.416 | -1 | 8/12 |
| frontend -> NTT-P | +1.914 | -2.281 | -1 | 8/12 |
| NTT-M -> Q24 pack | +2.985 | +2.831 | -1 | 4/12 |
| NTT-M -> B3 | -7.534 | -2.137 | -1 | 7/12 |
| B3 scale -> inverse core | -6.675 | -3.176 | -1 | 10/12 |
| B3 general -> add | -0.719 | +0.414 | -1 | 3/12 |
| inverse core -> inverse tail | -0.588 | -1.277 | -1 | 8/12 |
| inverse tail -> crepmod3 | -0.575 | +5.847 | -1 | 4/12 |

The exact `-1` retired-instruction result for every early-return candidate
confirms that the binary patch removes precisely the intended dynamic work.
It does not translate into a stable multi-cycle benefit.

The apparent inverse-core signal in the first run was not retained after PMU
sampling was strengthened: it reduced to about 1.3 core cycles and only 8/12
negative launches.  The same-return-address NOP control is neutral
(`+0.126` core cycles, 6/12 negative), so there is no hidden large AVX
transition penalty at this edge.

NTT-M -> Q24 is explicitly not a removal candidate.  Both the early-return
candidate and the same-return-address NOP control fail to show a stable win.

## Correctness

Every individually patched selected leaf passed the existing complete GT Clean
test binary.  The patch changes no arithmetic, memory access, output, or
control-flow decision before the function return.

## Decision

No edge meets a useful private-ABI continuation threshold.  Even the best
core-cycle median is only about three cycles, while TSC/core signs and
launch-level signs are not consistently corroborated.  Stacking such edges
would create a new internal calling convention without evidence that the gain
survives a caller.

Therefore:

- do not create a blanket no-`vzeroupper` ABI;
- do not change public or generic-C/SHAKE boundaries;
- do not run a whole-KEM promotion benchmark for 039;
- close hot-loop/frontend-shape/internal-ABI micro-tuning unless a future
  consumer supplies a materially different transition contract.

The next research unit must delete actual producer/boundary work, beginning
with bounded `SOTP -> frontend landing` and `CBD -> frontend landing` audits.
This is not contradicted by 038/039: those gates changed how the same work was
delivered, whereas producer-native landing may remove a full materialization.

## Artifacts

- `bench_internal_edges.c`: local producer/consumer regions.
- `tools/patch_leaf_epilogue.py`: exact four-byte ELF patcher.
- `tools/run_gate.py`: fixed-address build and paired multi-launch runner.
- `results/internal_edges.json`: complete launch records and geometry checks.
- `CURRENT-CLEAN-AUDIT.md`: fresh GT Clean/Official final-ELF compiler-boundary
  audit and the production policy derived from it.

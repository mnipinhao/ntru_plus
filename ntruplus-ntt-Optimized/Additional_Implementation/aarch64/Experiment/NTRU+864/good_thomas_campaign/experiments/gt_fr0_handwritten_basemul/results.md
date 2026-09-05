# B1-0 results

The exact active FR0 intrinsics source was compiled on Raspberry Pi 5 with
GCC 14.2.0 and `-O3 -std=c11 -Wall -Wextra -Werror -march=armv8-a+simd`.
The source SHA-256 is
`45afee29adaeddd7df691d2ea12aa614cc41db78f2b8fe632085c2b5fc983f4b`.
All 47 exact/canonical/alias test cases pass.

Three repetitions, two opposite orders and 61 samples per order on Cortex-A76
core 3 give:

| Boundary | cycles p50 | retired instructions | kernel instructions | IPC |
| --- | ---: | ---: | ---: | ---: |
| 36-group BaseMul | 2674.222 | 2832.001 | 2820 | 1.0590 |
| 36-group BaseMulAdd | 2831.180 | 3275.001 | 3263 | 1.1568 |

The compiler uses no stack/spill and avoids callee-saved `v8-v15`. The exact
BaseMul loop is 78 instructions/group including loop control:

```text
8 smull       8 smull2
14 smlal     14 smlal2
8 mul         8 uzp1       8 uzp2
3 ldr         2 ldp
1 stp         1 stur
1 add         1 cmp        1 b.ne
```

Thus the widening multiplier family is 44 instructions/group. BaseMulAdd is
90 instructions/group, with 50 widening-multiplier instructions, ten vector
loads and three vector stores. These are the authoritative GCC ledgers; the
earlier Clang archive estimate is not used for H1/H2.

Parallel static feasibility gates reject two broad arithmetic shortcuts:

- B1-K0: 230/288 leaves exceed signed int16 for the best pair sum/difference;
  worst-case magnitude is 51135. A global six-product int16 Karatsuba path is
  therefore invalid under the closed G0 intervals.
- B1-D0: deleting the initial cross reductions while keeping scale-aligned
  int32 direct accumulators is unsafe for 288/288 leaves; the worst bound is
  2,210,643,558,585. This does not reject local reduction elimination or an
  independently costed int64 representation.

K1 closes the remaining tile-local Karatsuba question. The 58 K0-safe leaves
form zero complete eight-lane groups; the best group contains only four safe
lanes. Public whole-vector switching therefore cannot use this shortcut.

## B1-D1 direct final R0 Barrett

The local D1 static proof covers the complete BaseMul and BaseMulAdd final
accumulator union `[-1961116731,1961346849]`. With reciprocal 621199, exact
SQRDMULH transition enumeration proves:

```text
qhat = floor((x * 621199 + 2^30) / 2^31)
r    = x - qhat * 3457
r in [-2911,2911]
```

`qhat*3457` and `r` stay in signed int32, `r` is congruent to `x` modulo 3457,
and narrowing is safe. The new 2911 input bound re-closes the existing inverse
at the same maximum halfword magnitude 17220; it does not satisfy the old 2205
consumer contract, so the contract must change explicitly.

The D1 intrinsics object uses six `sqrdmulh.4s`, six `mls.4s`, and three
narrowing `uzp1` instructions per group. GCC emits no call, stack access,
spill, or `v8-v15` use. Its loop sizes are 57 instructions/group for BaseMul
and 69 for BaseMulAdd, versus 78 and 90 in B1-0.

Three paired Pi 5 repetitions give:

| Boundary | B1-0 cycles | D1 cycles | delta | kernel instruction delta |
| --- | ---: | ---: | ---: | ---: |
| 36-group BaseMul | 2674.688 | 2150.755 | -523.933 (-19.59%) | -755 |
| 36-group BaseMulAdd | 2830.974 | 2154.314 | -676.660 (-23.90%) | -758 |

All 71 boundary/random comparisons are equal modulo q, all five alias paths
pass, and every repetition favors D1 with throttling `0x0`. D1 therefore
passes as an isolated arithmetic candidate, independently of H1/H2 scheduling.
The separate D1-C1 experiment now confirms complete polynomial multiplication
and 547.594-cycle full-boundary penetration, promoting D1 to the experimental
arithmetic baseline. It is still not a Production result.

B1-0 remains the comparison oracle and D1 is the active experimental
arithmetic baseline. The old 78-instruction H1/H2 path is deferred. If
scheduling reopens, it becomes D1-H1, D1-H2-U and D1-H2-P over the
57-instruction DAG. D1-C2b has now closed the real-Encapsulation serialization
consumer; the next integration gate is production-shaped D1-P1.

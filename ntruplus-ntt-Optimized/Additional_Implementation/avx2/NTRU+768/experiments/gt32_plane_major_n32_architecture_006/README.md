# GT32 plane-major N32 architecture gate

Experiment: `GT32-PLANE-MAJOR-N32-ARCHITECTURE-006`

This experiment restarts the physical-basis question before S1. It does not
modify GT Clean and does not use Q24 cost to reject a transform-domain basis.

## Coverage correction

The proposed reverse-Inverse progressive Forward is not new. The older
`GT32-GLOBAL-PHYSICAL-LAYOUT-001` searched all 5,040 assignments of the seven
semantic bits between every radix-2 stage, emitted exact Forward/inverse
assembly, and serious-qualified the resulting private `2F+B+I` primitive.

What remains genuinely open is narrower but still architectural:

- persistent full-plane N16 Stockham/Pease stages;
- a fused stage transition whose output is the next stage's input, instead of
  charging every lane-local stage the old fixed 16-shuffle pair-packed shape;
- twiddle load/reuse and its register cost;
- a hybrid-native BaseMul rather than forcing the endpoint to current M;
- plane-major `N32 = 2 x 4 x 4` radix-4.

## Exact basis inventory

The generator verifies 128-word bijections for three starting coordinates:

| basis | cross-YMM stages | lane-local stages | B3 plane loads native |
| --- | ---: | ---: | --- |
| current-like | 3 | 2 | no |
| hybrid one-plane-bit | 2 | 3 | no |
| full plane-major | 1 | 4 | yes |

This records the real trade: full plane-major maximizes B3 locality and
twiddle reuse but must justify four in-YMM stages with executable circuits.

## Twiddle oracle

The dormant `.Lgp_forward_s2_*` through `.Lgp_forward_s5_*` tables contain
four vectors per qinv/factor table but only two unique vectors. Across S2--S5:

```text
current-equivalent vector operands   32 / tile
unique plane-major register loads    16 / tile
potential constant-load reduction    16 / tile
```

This is a constant-delivery opportunity, not yet a cycle claim. The register
allocation must include data, q, factors, qinv and Montgomery temporaries.

## Decision

Do not emit another whole Forward yet. The next executable gate is an exact
plane-major N16 lane-stage library covering q3..q0, with stage output retained
as the next stage's physical input. It must compare persistent plane-major,
the already-qualified progressive circuit, and the current pair-packed local
control under the same matrix, range and register contract.

Q24 remains deferred until this transform-domain architecture is executable.

## Reproduce

```sh
make check
```

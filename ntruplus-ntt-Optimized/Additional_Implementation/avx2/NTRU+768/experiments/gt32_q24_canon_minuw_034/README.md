# GT32-Q24-CANON-MINUW-034

This experiment asks whether the already-proven Q24 remainder interval can
replace the three-instruction signed-to-canonical tail with unsigned minimum.
It does not modify GT Clean.

Control, per 16-word packet after the approximate reducer:

```asm
vpsraw $15, r, t
vpand  q, t, t
vpaddw t, r, r
```

Candidate:

```asm
vpaddw  q, r, t
vpminuw t, r, r
```

For `r in [-3291,3291]`, negative `r` has a large unsigned encoding while
`r+q` lies in `[166,3456]`; nonnegative `r` is no larger than `r+q`.
Therefore unsigned minimum yields the unique representative in `[0,q)`.

The candidate is mechanically derived from production `pack.s`, built in a
separate object, and symbol-prefixed. Control and candidate retain the same
5120-byte cage. Normal/reversed binaries change only their object order.

Run:

```sh
make check
make benchmark
```

The benchmark uses SUPERcop's `default-perfevent` cycle backend, pins each
fresh process to one CPU, alternates AB/BA order, and reports launch-level
paired medians for one and two Q24 calls.

## Result

Correctness passed over all 65,536 signed-int16 scalar values in every one of
the 768 serialized slots, plus 10,000 heterogeneous random polynomials and
1,000 deterministic full-Encap differential trials.

Static audit:

| item | control | candidate |
|---|---:|---:|
| hot instructions / Q24 | 1001 | 953 |
| symbol cage | 5120 B | 5120 B |

The strongest isolation uses two non-PIE ELFs with the Q24 symbol at the exact
same virtual address (`0x401760`), identical `.text`/`.rodata` sizes, and equal
100,064-byte ELF size. Across 48 interleaved fresh launches:

| region | candidate - control core cycles | wins | bootstrap 95% CI |
|---|---:|---:|---:|
| one Q24 | -20.646 | 48/48 | [-21.250, -19.542] |
| two Q24 | -38.562 | 48/48 | [-39.750, -37.250] |

The same-ELF normal/reversed cage test also passed in every launch:

| region | normal | reversed | wins |
|---|---:|---:|---:|
| one Q24 | -26.500 | -16.292 | 48/48, 48/48 |
| two Q24 | -45.958 | -37.083 | 48/48, 48/48 |

Full Encap remains launch-noisy: normal was -14.583 core cycles with 30/48
favorable launches and a CI crossing zero; reversed was -72.292 with 36/48
and a negative CI. Region-dominant PMU resolves the intrinsic work change:
`-95.998` retired instructions and `-65.645` core cycles per Encap, with loads
and stores unchanged. This exactly matches two Q24 calls deleting 48
instructions each.

## Decision

The unsigned-min canonicalizer is mathematically and locally performance
qualified, and it is the Q24 hot-body shape that the subsequent 033B section
ordering experiment should use. GT Clean remains untouched: whole-caller
delivery does not meet the prior >=90% favorable-launch promotion rule, so
production promotion requires a clean in-place export/KAT and formal caller
benchmark rather than interpreting the noisy duplicate-caller harness.

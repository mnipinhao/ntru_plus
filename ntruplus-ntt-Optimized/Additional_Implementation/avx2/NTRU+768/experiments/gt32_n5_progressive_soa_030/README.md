# GT32-N5-PROGRESSIVE-SOA-030

This experiment audits the proposed NTRU-Prime-inspired progressive-SoA
research line against the gates already present in the GT32 archive.  It does
not modify GT Clean and emits no assembly.

## Result

The broad Stage4/Stage5 idea is not an uncovered architecture.  The earlier
`GT32-GLOBAL-PHYSICAL-LAYOUT-001` search allowed a physical-layout transition
before, between, and after every NTT32 stage.  Its selected executable path
progressively exchanges Q axes with coefficient axes, lands directly in M,
and passed the 100k polynomial-chain gate.  Experiments 007 and 008 separately
tested persistent plane-major radix-2 and radix-4 schedules.

The genuine coverage gap was narrower: the old transpose gate found exact
12-instruction networks but did not prove 12 minimal over its advertised
structured physical-state family.

For one four-YMM/16-leaf block, the exact semantic selector states are:

```text
packed = (c0,c1,q1,v0,q0,v1)
M      = (q1,v1,q0,v0,c0,c1)
```

The generator searches all `6! = 720` affine assignments.  Edges are exact
full-four-YMM AVX2 bit-axis circuits: lane permutations, low/high word/dword/
qword unpacks, 128-bit-half selection, and free whole-register renaming.  The
shortest packed-to-M route costs exactly 12 instructions.  No route below 12
exists in this family.

This is deliberately **not** called a universal AVX2 lower bound.  A
non-affine circuit may split and recombine fragments with blends and leave the
720-state space.  Such a candidate reopens P0 only if it supplies an exact
sub-12 circuit; instruction-count speculation alone is insufficient.

## Coverage decision

| Proposed gate | Existing evidence | Decision |
|---|---|---|
| P0 packed to M | transpose-redeposit + this 720-state search | affine family closed at 12 |
| P1 Stage5 + M | global physical layout | already implemented and measured |
| P2 Stage4+5 progressive M | global physical + experiments 007/008 | already covered |
| P3 partial M to B3 add | transpose-redeposit phase D | 18-YMM/spill or repayment stop |
| P4 frontend + early NTT32 | specialized M frontend seam | deferred under current producer |

The important distinction is that production `ntt_m.s` still uses the
qualified compact 12-op terminal.  The global progressive implementation is a
qualified private polynomial primitive, not the selected whole-KEM backend;
its KEM delivery results were not stable enough to replace the specialized
production paths.  Re-running the same Stage4/Stage5 layout search under a new
name would therefore add no evidence.

## Reproduce

```sh
make check
```

Machine-readable evidence is in
`generated/progressive_soa_gate.json`.

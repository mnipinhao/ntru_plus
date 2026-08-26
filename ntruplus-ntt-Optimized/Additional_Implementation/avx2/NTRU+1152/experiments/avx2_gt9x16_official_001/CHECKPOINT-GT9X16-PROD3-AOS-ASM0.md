# GT9X16-PROD3-AOS-ASM0

This checkpoint realizes only the new machine-risk boundary selected by
`GT9X16-PROD3-AOS-SCHED`:

```text
one physical-p=0 D4-output AoS tile
-> D2
-> D1
-> live hierarchical transpose
-> four AoS-physical-q coefficient planes
```

It does not implement NTT9, twist, D8, D4, a complete branch, a complete
producer, or a KEM caller. It contains no benchmark.

## Routing-account reconciliation

The previous MAP and SCHED headlines used different scopes:

| ledger | formation | adjusted NTT16 internal | P2-B | total |
| --- | ---: | ---: | ---: | ---: |
| MAP known boundary count | 576 | excluded/open | 72 | 648 |
| linked G0/P2-B control | 576 | 288 | 72 | 936 |
| persistent-AoS exact MA2 | 0 | 432 to AoS planes | 144 packed-lane routes | 576 |

Branch0 later found that this tile stopped one representation short of the
frozen MA2 packed-lane ABI. Exact MA2 output needs another eight routes per
tile, so the corrected full-forward comparison is `936 - 576 = 360`. The
linked audit still refuses a changed `648 + 288 = 936` control identity.

## Tile ABI

The input is 64 signed 16-bit representatives in D4-output AoS order:

```text
[q0.j0, q0.j1, q0.j2, q0.j3, ... q15.j3]
```

The output is the AoS physical-q plane order:

```text
[j0.physical_q0..q15, ..., j3.physical_q0..q15]
```

The arithmetic is the frozen physical-row-zero adjusted D2 and D1 Montgomery
butterfly DAG. It introduces no reduction, scale conversion, Q permutation,
or representative normalization. Input and output pointers do not gain an
alignment requirement; the leaf uses `vmovdqu` for caller data.

## Linked realization

The assembled leaf is 297 bytes and has the following exact dynamic ledger:

| class | count |
| --- | ---: |
| D4-state loads | 4 |
| D2 `vperm2i128` | 4 |
| D1 qword unpacks | 4 |
| transpose word unpacks | 4 |
| transpose dword unpacks | 4 |
| transpose qword unpacks | 4 |
| final `vpermq` | 4 |
| MA2-plane stores | 4 |
| routing total | 24 |
| Montgomery chains | 4 |

There is no `vpshufb`, call, stack frame, stack reference, vector spill, or
`vzeroupper`. The fixed-register instruction flow peaks at nine live YMM
registers, leaving seven architectural registers free. This closes the
symbolic schedule's register-pressure concern for this tile.

The public leaf entry and all nine YMM constant vectors use `.p2align 5`.
The linked object reports 32-byte `.text` and `.rodata` alignment and entry
address modulo 32 equal to zero. No bare `.align` is present.

## Correctness gates

The independent scalar oracle evaluates D2 then D1 in semantic q order and
transposes only at the final comparison boundary. The ASM output is raw
bit-exact, not merely congruent modulo q, for:

- zero and every positive/negative input-lane impulse;
- alternating D4 range bounds;
- 10,003 random tiles in `[-16691,16691]`;
- unaligned-but-`int16_t`-aligned input and output pointers;
- in-place aliasing, input immutability, and output canaries.

Because raw representatives match, the frozen per-row range proof remains the
applicable proof; no repair or reduction was inserted.

## Decision

The C1 arithmetic tile is machine-feasible: its 24-route AoS-plane network
lowers to a clean, aligned, zero-spill AVX2 leaf. Branch0 supersedes the old
claim that these four vectors already were the exact MA2 packed-lane ABI.

The next review checkpoint is a one-branch realization:

```text
top-split branch -> AoS NTT9 -> D8/D4 -> nine C1 tiles -> MA2 planes
```

That step remains unimplemented and unbenchmarked. Twist stays at T0 and the
current frozen MA2 Q order remains unchanged.

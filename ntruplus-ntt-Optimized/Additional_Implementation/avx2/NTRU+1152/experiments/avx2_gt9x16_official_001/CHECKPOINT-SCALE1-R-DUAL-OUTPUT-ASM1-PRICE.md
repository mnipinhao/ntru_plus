# Scale-1 r dual-output ASM1 and fanout pricing

## Result

The exact live-terminal dual-output implementation is correct and removes
the intended 72 serializer reloads.  It is nevertheless substantially slower
at the complete scale-1 `r` fanout boundary and is rejected for caller and
Native integration.

This closes the first direct dual-output realization; it does not reject the
semantic two-consumer contract or a future schedule that can preserve
producer/serializer overlap.

## Contract

Both paths start with the same coefficient-domain, CBD1-compatible `r` and
finish with all three of:

1. the same retained 1152-cell wire-monotone scale-1 transform state;
2. the same `hash_g` output; and
3. the same SOTP polynomial.

The control runs the frozen Forward, materializes the retained state, then
reloads 72 vectors in the standalone exact-wire serializer.  The candidate
keeps the same 72 state stores for the later MA2 consumer but feeds each
serializer tile directly from the four live terminal YMM registers.

## Correctness and machine audit

- 1003 fixed/random trials passed.
- Retained transform state is raw bit-exact.
- Exact 1728-byte serialized `r` is byte-exact.
- Installed SUPERCOP preflight additionally passes `hash_g` and SOTP output
  equality.
- Input immutability, state/byte canaries, ASan, and UBSan pass.
- The linked candidate removes exactly 72 `vmovdqa` reloads and one separate
  `ret`; arithmetic and routing mnemonic counts are unchanged.
- Combined `.text` is 564 bytes smaller and `.rodata` is unchanged.
- The candidate remains call-free, branch-free, frame-free, spill-free, and
  `vzeroupper`-free.

The first diagnostic installation was rejected before timing.  Its source
implementation contained an older Forward template with the same
materialized output but a different terminal-register assignment.  The
installer now pins and records the exact branch-template hash used by the
live-register map.  The corrected non-overwriting implementation is:

```text
crypto_kem/ntruplus1152/avx2-gt9x16-wire-dual-r-exp012-sc20260831
```

## SUPERCOP-derived serious pricing

Pinned SUPERCOP 20260831, fixed common GCC 15.2 `-O3`, CPU 1, performance
governor, turbo disabled, balanced same-ELF order, nine fresh processes, and
1728 pooled observations per variant:

| path | StQ1 | StQ2 | StQ3 |
|---|---:|---:|---:|
| separate Forward + serializer control | 19871.1319 | 20067.0787 | 20130.1759 |
| live-terminal dual-output candidate | 20276.8819 | 20488.6481 | 20568.1505 |
| candidate - control | +405.7500 | **+421.5694** | +437.9745 |

Every fresh-process StQ2 delta is positive:

```text
+443.604, +295.438, +283.250, +465.250, +434.062,
+434.458, +378.042, +514.062, +415.500 cycles
```

This is a SUPERCOP-derived caller-shaped result, not Native SUPERCOP KEM
output.

## Interpretation and decision

The eliminated reloads were inexpensive hot-L1 operations that also provided
an intentional producer/consumer scheduling boundary.  Moving the full
serializer into every Forward terminal tile lengthens the dependent terminal
path and removes the out-of-order decoupling of the two passes.  The linked
instruction ledger is therefore insufficient to predict cycles: fewer
instructions and less `.text` still lose by about 422 cycles at the actual
fanout boundary.

- Reject this live-terminal dual-output realization.
- Do not change the cumulative Native KEM candidate and do not run Native KEM
  for this rejected leaf.
- Keep the scale-1 two-consumer contract as an oracle.
- The next dual-output attempt, if reopened, must preserve a materialized or
  buffered scheduling boundary, or use a much smaller terminal side product;
  simply consuming every terminal quartet immediately is closed.


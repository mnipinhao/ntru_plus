# A1 — tail architecture shootout

This default-off experiment compares three exact NTRU+864 tail NTT16
architectures before any new Slothy scheduling:

- T0 current: column-major `[t][six banks,0,0]`, sixteen lane loads per bank,
  six packed one-bank NTT16 transforms.
- T1 bank-major: `[bank][t0..t15]`, two contiguous vector loads per bank, six
  otherwise-identical packed one-bank NTT16 transforms.
- T2 six-bank SIMD: column-major input, sixteen vector loads total, one scalar
  NTT16 DAG whose vector lanes carry the six banks, then two 8x8 halfword
  transposes back to bank-major output.

The current packed one-bank implementation already uses its eight lanes for
eight butterflies. Consequently T2 executes 48 Algorithm-10 products (16
twists plus 32 butterfly products), rather than T0/T1's 36 (six banks times
two packed twists plus four packed stages). T2 is therefore an empirical
latency/ILP/routing hypothesis, not an assumed sixfold arithmetic reduction.

`make check` generates unscheduled assembly and verifies T0/T1 exact equality
and T0/T2 coefficientwise equality modulo q on tagged and randomized inputs.
Production is unchanged. Slothy is intentionally deferred until the
architecture and full-boundary measurements are complete.

Pi 5 Cortex-A76 paired PMU results select T1.  The complete Forward p50 is
4231.714 cycles for T0, 4165.076 for T1, and 4206.830 for T2.  T2 wins only
when its routing is prepared outside the measured one-bank/six-bank boundary;
after the transpose is charged to complete Forward, T1 wins by 41.754 cycles.
See `results.md` and `DECISION.md`.  No Slothy run or Production change was
made.

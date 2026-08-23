# Results

## Correctness

- 256 valid deterministic-Encap cases;
- 69 mutated or malformed ciphertext cases;
- post-I1 words exact;
- crepmod3 coefficients exact;
- recovered message and recovered-r bytes exact;
- complete valid/invalid Decap status and shared secret byte-exact;
- NIST KAT control/candidate response byte-exact:
  - 948,402 bytes;
  - SHA-256 `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

## Primary full-caller TSC gate

Candidate minus current GT Clean control, 16 launches per placement:

| Placement | post-I1 | B3→crepmod3 | full Decap | full wins | full 95% CI |
|---|---:|---:|---:|---:|---:|
| Normal | +6.306 | -23.592 | **-9.895** | 14/16 | [-18.131, -6.126] |
| Reversed | +5.837 | -22.110 | **-11.360** | 12/16 | [-24.320, -1.743] |

The seam therefore passes the predeclared affected-caller TSC rule in both
placements.  The gain is much smaller than 065 because Decap enters at M and
contains only the B3→inverse seam, not the complete 2F+B+I graph.

## Region PMU attribution

The diagnostic ELF gives the following core-cycle deltas:

| Frontier | Normal | Reversed |
|---|---:|---:|
| B3→post-I1 | +8.08 | +8.70 |
| B3→crepmod3 | **-41.94** | **-35.71** |
| Decode→crepmod3 | **-36.12** | **-35.77** |
| Recover-r ready | **-38.02** | **-33.49** |
| Recovered-message trace | +23.73 | +86.03 |
| Full Decap | -25.21 | +13.44 |

At B3→post-I1 the candidate retires about 78 fewer instructions, 16 fewer
loads, and 15 fewer stores, but is about 8 core cycles slower.  After the
common inverse tail and crepmod3 it retires about 133 more instructions and 36
more loads/stores, yet becomes 36–42 core cycles faster.  The win is therefore
an executable-DAG/critical-path effect, not an instruction-count result.

The first integration reversal occurs after recovered-r, at the Hash/SOTP
trace checkpoint, even though those operations are byte-identical and common.
This is recorded as code-delivery interaction, not as Hash arithmetic debt.

A separate 17-pair full-only PMU validation was inconclusive for core cycles:

| Placement | median core-cycle delta | negative pairs | 95% CI |
|---|---:|---:|---:|
| Normal | +6.08 | 8/17 | [-49.17, +80.35] |
| Reversed | -76.52 | 11/17 | [-267.31, +39.89] |

Both intervals cross zero.  Consequently 066 is caller-qualified by its lean
same-ELF paired TSC gate, but it is not yet a production export or a claim of
placement-independent core-cycle improvement.

## Decision

```text
GT32-LATE-SOA-066: AFFECTED_CALLER_PASS
GT Clean production: unchanged
Next caller: not started
```

065 remains `FULL_ARITHMETIC_CHAIN_PASS`.  No conclusion from 066 weakens the
063–065 arithmetic results.

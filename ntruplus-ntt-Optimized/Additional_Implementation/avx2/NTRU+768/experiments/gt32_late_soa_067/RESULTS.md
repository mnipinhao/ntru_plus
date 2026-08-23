# Results

## Correctness and construction audit

- 256 valid production-shaped Decap cases pass exactly.
- 69 invalid or malformed ciphertext cases have exact status and shared secret.
- Control and candidate KAT responses are both 948,402 bytes with SHA-256
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.
- Both compiled Decap callers are 808 bytes.  Their pre-relocation machine
  bytes are identical; after normalizing the two allowed call targets, their
  text relocation lists are identical.
- Both decision binaries are PIE.  All section sizes, hashes, and selected
  symbol offsets are captured in `results/static.json`.

The experiment therefore changes no caller C code, frame, cleanup, Hash,
validation, or failure behavior beyond the previously qualified seam.

## Primary full-Decap gate

Candidate minus current GT Clean control, 32 launches per placement:

| Placement | median delta TSC | favorable launches | bootstrap 95% CI |
|---|---:|---:|---:|
| Normal | **+57.715** | 0/32 | [+53.014, +66.817] |
| Reversed | **+11.086** | 10/32 | [+0.229, +19.966] |

Both production-shaped placements are significantly slower.  The result
fails both the primary CI requirement and the `28/32` near-all-launch target.
This is not a marginal or sign-ambiguous promotion result.

## PMU corroboration

Full Decap, 17 paired processes per placement:

| Placement | core cycles | instructions | loads | stores | IDQ not delivered |
|---|---:|---:|---:|---:|---:|
| Normal | **+145.83** | +132.00 | +36.00 | +36.00 | **+708.74** |
| Reversed | -10.92 (CI crosses 0) | +132.00 | +36.00 | +36.00 | -285.73 |

Normal has a large, statistically positive core-cycle and frontend-delivery
regression.  Reversed improves IDQ delivery but has inconclusive core cycles
and still loses paired TSC.  Thus no placement-independent execution mechanism
supports promotion.  The fixed +132 instructions and +36 loads/stores are the
same structural trade already seen in 066; 066 could hide them through a
better executable DAG, while the production geometry cannot do so reliably.

## Evidence ladder

| Gate | Normal | Reversed | meaning |
|---|---:|---:|---|
| 065 full polynomial chain | -66.25 TSC | -67.43 TSC | arithmetic pass |
| 066 lean full Decap | -9.895 TSC | -11.360 TSC | affected-caller pass |
| 067 production-shaped Decap | **+57.715 TSC** | **+11.086 TSC** | promotion rejected |

Differences between rows are evidence transitions across different executable
contexts, not additive component costs.

## Decision

```text
GT32-LATE-SOA-067: PRODUCTION_PROMOTION_REJECTED
Late-SoA x current GT Clean Decap production image: CLOSED_FOR_SCOPE
GT32-LATE-SOA-065: FULL_ARITHMETIC_CHAIN_PASS retained
GT32-LATE-SOA-066: AFFECTED_CALLER_PASS retained
GT Clean production: unchanged
```

No Late-SoA arithmetic, alignment, padding, constant-placement, or scheduling
search is reopened.  A future retry requires an independently justified
production-image change that creates a genuinely new delivery context.

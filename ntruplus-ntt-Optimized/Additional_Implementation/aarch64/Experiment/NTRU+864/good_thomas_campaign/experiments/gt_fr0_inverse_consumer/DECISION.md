# Decision

M5D passes. Retain FR-0 and the P8+tail boundary for the inverse path.

The exact inverse order is inverse NTT9 first, then inverse NTT16. Inverse NTT9
already receives rows as registers and columns as lanes; after its inverse
twist, the existing 8x8 transpose reconstructs P8. The second pass packs alpha
and beta in vector halves, performs one shared inverse NTT16 schedule, and
recombines directly to natural low/high coefficients. No separate 2x432 buffer
is algebraically or layout-wise required.

The next permitted experiment is handwritten inverse memory/store realization.
It must preserve this map and scale, prove stacklessness or account for spills,
and price the component-strided stores. M5D does not authorize Production
linkage or claim a cycle improvement.

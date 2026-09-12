# P21 result — current-production Inverse-to-ternary decomposition

P21 is a measurement-only decomposition of production revision
`c24cf55296b150712159ce1c3f3a8cad03f3551b`. It follows P20's finding that GT
`Inverse_to_ternary` remains 284.200 cycles slower than selected Official
`Inverse + Crepmod3` at the matched Decaps call-site boundary.

## Binding and correctness

- Source bundle: 120 files, content-addressed before upload.
- Production library SHA-256:
  `39fda20ffdb9d3cf3f5f8ec6684a908b224232c33bbf6ee1f48db0a7e1ace063`,
  identical to P20's profiled GT library.
- Fresh manifest check, 64 KEM round trips/tampered rejections, and 100-case
  KAT pass.
- KAT SHA-256:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- Diagnostic controls only delete terminal `UMOV/STRH`: exactly 256
  instructions from each main-I16 call and 192 from the tail call. Arithmetic,
  loads, tables, and production objects are unchanged.
- Pi 5 stayed unthrottled (`0x0`); temperature was 57.1 to 62.0 C.

## Pi 5 stage decomposition

Numbers are medians after subtracting the empty harness. There are six balanced
processes and 43 samples per process per boundary, hence 258 observations per
boundary; each PMU sample executes 64 operations on Cortex-A76 CPU 3.

| Boundary | Cycles | Share of complete | Instructions | IPC | Reads | Writes |
|---|---:|---:|---:|---:|---:|---:|
| inverse9 ×12 | 1,682.047 | 34.38% | 2,381 | 1.416 | 344.000 | 296.985 |
| main I16 ×6 | **2,117.531** | **43.27%** | 4,070 | 1.922 | 520.000 | 770.000 |
| tail I16 | 341.313 | 6.98% | 611 | 1.790 | 88.000 | 95.985 |
| raw-to-ternary | 430.164 | 8.79% | 951 | 2.211 | 109.016 | 107.969 |
| wrapper/routing/wipe residual | 322.172 | 6.58% | 323 | — | -16.000 | 127.077 |
| complete Inverse-to-ternary | **4,893.227** | 100% | 8,336 | 1.704 | 1,045.016 | 1,398.016 |

The residual is diagnostic and non-additive: it includes wrapper setup,
address/control work, tail initialization, scratch wipe, ABI save/restore, and
differences between isolated-call and complete-call cache context. Its negative
read residual is direct evidence that it must not be interpreted as an
independent hardware stage.

The complete isolated median is 11.523 cycles below P20's KEM call-site median
of 4,904.750 cycles. That 0.235% difference is small enough for stage selection,
but P20 remains the authoritative Official comparison.

## Scatter diagnostic

| Diagnostic deletion | Cycle ceiling | Retired instruction delta | Write delta |
|---|---:|---:|---:|
| all main-I16 terminal scatters | 157.125 | 1,534 measured / 1,536 static | 768.000 |
| all tail-I16 terminal scatters | 17.891 | 195 measured / 192 static | 96.016 |
| aggregate | **175.016** | — | — |

This is an optimistic ceiling, not a candidate: all 864 coefficients still
have to reach the consumer. It confirms the earlier P7-B0 result that removing
scalar stores alone cannot recover the complete inverse gap.

More importantly, main I16 without any terminal scatter still costs
1,960.406 cycles and 2,536 instructions, with IPC 1.294. It remains larger than
the complete inverse9 aggregate. The bottleneck has therefore genuinely moved
after P7-C1's one-product inverse9 promotion.

## Decision

P21 selects:

> **P22 — main-I16 arithmetic/dependency DAG audit and candidate search.**

P22 must reconstruct the six-call current P13-B main-I16 kernel at the exact
fixed ABI and split its 422.7 no-store instructions per call into load/table,
four CT layers, reductions, composite terminal map, and dependency depth. A
candidate must delete arithmetic/reduction work or materially shorten the
critical path, remain int16/range correct, preserve the current output
coordinates and memory boundary, allocate without spill, and beat the current
2,117.531-cycle six-call boundary on Pi 5. A store-only rewrite cannot pass.

The maintained order after P22 is ToBytes smaller-route/pack DAG, then monitored
BaseInv/Rinv retired-work gaps. Production is unchanged by P21.

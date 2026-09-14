# P26 result — the Inverse deficit is materialization, not reduction

P26 aligns the complete semantic boundary selected by P25.  Production remains
exact revision `d76a8289a8652e156665aff78bee6946183b2923`; selected Official
remains tree SHA-256
`40a284439eb5fe8dfef77f1a995ebc8dd16182835048d64e959fbcb6e3df0b59`.
The Official snapshot has not been independently verified as latest upstream.

## Exact reconciliation

Every fixed loop and GT helper invocation is expanded by `audit.py`:

| Boundary | Dynamic source instructions | Profiler shell | P25 measured |
|---|---:|---:|---:|
| Official Inverse + Crepmod3 | 4,583 | +22 | 4,605 |
| GT fused Inverse-to-ternary | 8,324 | +21 | 8,345 |
| GT minus Official | +3,741 | -1 | **+3,740** |

The one-instruction profiler-shell difference explains the source/PMU delta
exactly; no residual instruction count is left unattributed.

GT's source total decomposes as:

| GT stage | Dynamic instructions |
|---|---:|
| inverse9 ×12 | 2,220 |
| main I16 ×6 | 4,008 |
| tail I16 | 604 |
| raw-to-ternary | 954 |
| wrapper, addressing, calls, initialization and wipe | 538 |
| Total | **8,324** |

## Instruction-class delta

| Class | GT minus Official |
|---|---:|
| `mul` | -23 |
| `sqrdmulh` | -64 |
| `mls` | -64 |
| All modular-multiply instructions | **-151** |
| Lane extraction (`UMOV`) | **+864** |
| Loads | **+788** |
| Stores | **+1,159** |
| Vector copies (`ORR`) | +224 |
| Vector routing | +92 |
| Vector integer work | +269 |
| Scalar setup/address/control | +438 |
| Control transfers | +58 |

GT therefore already performs fewer `mul/sqrdmulh/mls` instructions than
Official.  Removing another reduction is not the explanation for the measured
gap.

The load difference is equally specific:

| Load source | Official | GT |
|---|---:|---:|
| Coefficient/intermediate | 171 | 328 |
| Constant tables | 81 | **706** |
| Callee restore | 4 | 10 |
| Total | **256** | **1,044** |

GT's 706 constant loads consist of 216 inverse9 twist loads, 42 I16 stage
loads, and **448 composite-terminal loads**.  The latter are the same 64-Q
table reloaded by six main calls and the tail call.

## Why scalar materialization cannot simply be deleted

The six main I16 calls and tail emit 864 coefficients with exactly 864 `UMOV`
and 864 `STRH` instructions.  P21 already measured the optimistic benefit of
deleting every one of those stores/extractions as only 175.016 cycles, below
P25's 280.675-cycle matched deficit.  Output delivery remains mandatory.

P11 replaced these scalar pairs with D stores followed by a joint ternary
route, deleting up to 1,292 instructions, but every A0–A4 candidate was slower.
P22's copy-free I16 improved the isolated main boundary yet regressed complete
Inverse and Decaps.  Neither experiment is reopened.

The structural reason is the current call basis.  Each `lazy_i16` call holds a
single degree-3 component and one four-row half, while natural coordinates are

```text
natural_index = 27*k + 3*row + component
```

A single current call therefore cannot form consecutive natural eight-lane
output vectors.  Natural full-vector stores require either multiple components
to be live together or an earlier change to the lane/bank basis.  Writing the
current records and routing afterward is precisely the rejected P11 shape.

## P27 selection

P27 is a machine-only consumer-oriented I16 lane-basis search before any new
assembly.  It must alter the inverse9→I16 physical basis so the terminal
arithmetic directly produces vectors consumable by raw-to-ternary; it may not
append a post-store route.

Hard gates:

1. exact CRT coordinate, root, R0 scale and range ledger;
2. exact natural ternary output for all 864 coefficients;
3. no additional coefficient memory pass or larger scratch;
4. no lane `ST3`, no 864-`UMOV`/`STRH` terminal ABI, and no P11 D-record route;
5. final stores at full-vector granularity, with at most 108 coefficient-vector
   stores before public cleanup;
6. peak at most 32 vector registers and no spill;
7. static candidate must remove real materialization/routing work, not merely
   encode two existing loads as one `LDP`;
8. only a surviving exact DAG proceeds to Slothy and Pi 5.

Constant-load sharing, especially the 448 composite loads, is recorded as a
secondary opportunity.  It should be co-designed with the new lane basis only
if it does not add a memory boundary.

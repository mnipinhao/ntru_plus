# NTT-domain representation contract

This checkpoint does not select a production ABI. It normalizes mathematical
component identity, physical position, Montgomery scale, range, terminal
factor, and consumer boundary so the complete forward/arithmetic/inverse path
can select one.

The machine-readable sources of truth are:

- `generated/ntt-domain-lifecycle-audit.json`;
- `generated/gt9x16-pipeline-layout.json`;
- `generated/gt9x16-representation-cost-matrix.json`.

## Component identity

Every terminal scalar is identified by `(b,p,q,j)`: top branch, NTT9
frequency, NTT16 frequency, and degree-4 terminal coefficient. Physical rows
and lanes are deliberately private orders:

```text
p = P[r], P = [0,3,6,1,4,7,2,5,8]
q = Q[l], Q = [0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15]
```

No consumer may assume `r=p` or `l=q`. Each `(b,r,l)` maps to
`X^4-factor`, its Montgomery factor/qinv pair, all four terminal coefficients,
and Official positions. Replacing R3R3 with another NTT9 schedule changes
`P[]` and generated constants, not BaseMul/BaseInv semantics.

`transform_scale` is a separate contract dimension from the Montgomery
`scale_r_exponent`. The current generic R3R3 producer has transform scale one;
the F-R3 paper producer has transform scale four. R2 changes the private row
map to `P = [0,3,6,1,4,7,8,2,5]`; generated consumers follow `p=P[r]` and do
not restore the standard order at runtime. See `CHECKPOINT-F-R3.md` and
`generated/gt9x16-scaled-r3r3-oracle.json`.

## Arithmetic-domain contracts

| Boundary | Scale | Conservative range | Status |
| --- | ---: | ---: | --- |
| KEM-small forward output | `R^0` | `[-3107,3107]` | proved from small-input stage bound plus Official final reduction |
| resident BaseMul/BaseInv value | `R^0` | `[-3456,3456]` | Montgomery-output contract |
| regular BaseMul output | `R^0` | `[-3456,3456]` | includes the in-kernel R² post-pass |
| BaseInv output | `R^0` | `[-3456,3456]` | after denominator batch inversion/application |
| scaled BaseMul inverse feed | `R^-1` | `[-13824,13824]` | conservative; deliberately omits R² post-pass |

The table's scale column is the Montgomery-domain exponent. For R1/R2, the
additional arithmetic transform scale is four at forward output, 16 after two
forward operands enter BaseMul, and `1/4` after BaseInv. This scalar ledger is
proved modulo q; executable range bounds remain an F-R3B gate.

The provisional D-B forward must retain an equivalent final reduction before
BaseMul/BaseInv. General centered-input forward remains unqualified. Official
`poly_invntt_scale` consumes the `R^-1` scaled-BaseMul result; a diagnostic
`F+BaseInv+I` path needs either R0-specific inverse normalization constants or
a fused BaseInv output scale. It must not silently reuse the R^-1 contract.

## Official lifecycle

Official keeps 18 contiguous 128-byte terminal-major blocks. Each block is
four adjacent YMM vectors, one per `j`, with 16 independent factors in lanes.

- Forward stores two terminal blocks per 256-byte radix-2 block.
- Regular BaseMul consumes two operands in that shape and performs an R²
  post-pass without changing layout.
- Scaled BaseMul keeps the same layout but omits the post-pass for inverse.
- BaseInv phase 1 consumes four vectors and emits four vectors plus one
  denominator vector per terminal block; `den[18]` is batch-inverted and phase
  2 multiplies it back.
- Inverse loads eight vectors per 256-byte block directly. There is no
  standalone permutation on any Official edge.

All five audited assembly leaves are call-free, frame-free, stack-reference-
free, contain no `vzeroupper`, and use all 16 YMM registers. BaseInv's C wrapper
still owns the separate 18-YMM denominator array; that is arithmetic state,
not a layout pass.

## Candidate closure ABIs

### A. Terminal-major

```text
T[branch][physical_p_row][terminal_j][physical_q_lane]
```

Forward, BaseMul/BaseInv loads and stores, and an independent adjusted inverse
NTT16 need no boundary routing. The open cost is that it may give up the
terminal-pair Montgomery-chain sharing suggested by C4.

### B. Persistent pair S/D

```text
P[branch][physical_p_row][terminal_pair][S_or_D][packed_lane]
```

For terminal pair `k`, lower lanes hold `j=2k`, upper lanes `j=2k+1`; S/D
selects even/odd physical q lanes. A paired forward and paired inverse can
potentially keep this form without reconstruction. The current explicit AVX2
unpack schedule uses eight routing instructions per operand/row. Including
two BaseMul inputs and persistent output gives 24 per row, 432 over 18 rows.
BaseInv uses one input and one output pack: 16 per row, 288 total.

### C. Terminal-to-inverse-pair hybrid

Forward and arithmetic inputs use A; BaseMul/BaseInv store directly as B for a
paired inverse. Only the arithmetic store side routes: eight per row, 144 over
the full transform. This is a boundary policy, not a standalone conversion.

The counts for B/C are explicit-schedule estimates, not proved lower bounds or
cycle predictions. A, B, and C remain alive until native implementations are
measured as `2F+BaseMul_scale+I` and scale-correct `F+BaseInv+I` paths.

## Closure rule

No candidate may insert a full-array transpose, gather, scatter, or cosmetic
natural-order pass. Load-side unpack and store-side repack are allowed only
inside the real producer/consumer arithmetic kernel and stay in full-path
timing.

## G0 consumer-edge refinement

Checkpoint G0 does not replace this contract with one universal ABI. It treats
the A/B/C controls as views in a larger `R=(P,Q,B,g,s,O)` space and permits
different source-resolved layouts for encapsulation, scaled-multiply/inverse,
and BaseInv/inverse paths. The authoritative generated inventory is
`generated/g0-representation-views.json`; its consumer graph is
`generated/g0-consumer-graph.json`.

The G1 shortlist is F1 terminal-major, F3 consumer-fused terminal basis, F4
encapsulation terminal streams, and F5 inverse-feed hybrid. F0 D1 persistent
S/D remains the measured control. F2 `p,-p` is deferred because the current R2
row order makes three of four nonzero pairs nonadjacent and no cheap factor
identity has been proved. A universal natural-order boundary is rejected
because it requires a standalone full-array pass.

G1A materializes these policies as five edge oracles in
`generated/g1-edge-oracles.json`. F1 prices the forward producer tail; F5
separately prices BMScale/BaseInv stores against inverse heads. They are not a
pipeline selection. `generated/g1-edge-debt-matrix.json` now records G1B's
measured F1-B1 producer debt of 58.5 cycles and B0 clean upper bound of 60.5
cycles. Consumer credit and net delta remain null. G1C0 confirms that Official
BMScale and inverse already share a zero-conversion terminal-major boundary;
no C1 store-order credit is available. The adjusted inverse head remains a
generated-oracle gate, so F1 and F5 are still independent and no complete-path
layout is selected.

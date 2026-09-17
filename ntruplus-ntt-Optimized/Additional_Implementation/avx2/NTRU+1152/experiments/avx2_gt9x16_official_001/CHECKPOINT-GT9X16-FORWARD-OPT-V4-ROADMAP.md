# GT9X16 Forward OPT-V4 roadmap

## Objective

The current NTRU+1152 scale-1 wire-monotone Forward is a qualified research
baseline, not a finished kernel.  At the latest same-O3 SUPERCOP-derived
coefficient-input boundary it is statistically near Official parity:

```text
Official                 1486.9861 cycles
current GT               1484.1690 cycles
GT - Official              -2.8171 cycles (7/9 launches negative)
```

The next Forward program must seek structural credit large enough to survive
the complete caller.  It must not promote a candidate from instruction count,
an isolated prepared-layout benchmark, or a repository-local timer.

The frozen control for every step is:

```text
coefficient-domain small polynomial
  -> existing top split
  -> persistent-AoS NTT9-first Forward
  -> scale-1 wire-monotone output ABI
```

Unless a phase explicitly reopens a contract, leaf identity, scale,
Montgomery exponent, signed-i16 safety, wire ownership, and all consumers stay
unchanged.

## Baseline ledger

```text
linked instructions                 2875
Montgomery chains                    296
Barrett vectors                       40
routing vectors                      488
initial/final data loads/stores    72/72
NTT9/NTT16 boundary loads/stores   72/72
.text                              15449 bytes
.rodata                            12192 bytes
call/frame/spill/branch/vzeroupper     0
```

## Phase 1: NTT9-to-NTT16 wavefront

### 1A. W1 machine control

Realize the already-proved one-row schedule as a namespaced ASM candidate.
It retains one selected row per branch across four q-blocks and must show:

```text
intermediate stores                 -8
intermediate reloads                -8
extra constant operands              0
recomputed arithmetic                0
spill/frame                           0
```

W1 is not expected to be the final architecture.  It is the machine control
that prices whether this L1 boundary is beneficial to remove at all.

Gate order:

1. exact/canonical Forward differential and range replay;
2. linked store/reload, constant-load, spill and alignment audit;
3. installed KAT;
4. Native SUPERCOP `enc_cycles` with normal compiler selection;
5. common-O3 same-ELF component replay only for attribution.

Stop if Native direction is non-negative or compiler selection makes the
effect unresolved.  Do not infer a multi-row win from static traffic alone.

### 1B. W2 two-row feasibility and pricing

Two rows require six retained vectors at the fourth q-block.  Together with
nine NTT9 values, three cached constants and one R3 temporary, the naive peak
is 19 YMM.  The exact W2 gate enumerates the bounded same-DAG trade between:

- materializing selected-row vectors, which gives back store/reload debt; and
- using memory-form `q`/`kappa` constants, which consumes load-port bandwidth.

Only a Pareto W2 variant may reach ASM.  It must beat W1 at a complete
coefficient-input Forward boundary before larger row counts are considered.
Full two-row retention is not authorized merely because it fits after moving
all constants to memory.

### 1C. W4/W9 extension

Proceed only if W2 produces a stable Native or fixed-common caller credit.
Search row counts incrementally.  At every size report boundary traffic,
constant-memory operands, recomputation, peak live YMM, `.text`, and code
placement.  Full zero-materialization is a possible endpoint, not a premise.

## Phase 2: NTT9 arithmetic and alpha co-design

Reopen the 152-chain NTT9-side budget:

```text
scale-1 alpha normalization           72
radix-3 kappa                          48
rho/zeta interstage                    32
```

Candidate families are scaled CT/GS radix-3 orientations, alpha absorption
into an existing multiply, output-gauge transfer into NTT16, and a fused
radix-9 realization.  This phase is high risk: it must prove the complete
linear basis, Montgomery exponent, output scale, root identity, and exact
pre-operation signed-i16 intervals before serious timing.

Advance only candidates that remove multiplication chains without replacing
them with comparable routing, reduction, or constant-traffic debt.

## Phase 3: D2/D1 and terminal transpose co-design

Optimize the complete 488-route late network rather than only the visible 56
`vpshufb` instructions:

```text
D2 vperm2i128                         72
D1 qword unpack                       72
16/32/64-bit terminal transpose      288
wire-specific vpshufb                 56
```

Allowed freedoms include equivalent butterfly output swaps, sign/twiddle
orientation, unpack operand order, CT/GS selection, and store renaming.  The
wire ABI remains exact.  Search output is an executable def/use schedule, not
only a semantic permutation count.

## Phase 4: retained Barrett repair co-design

The current mask 79 is the unique minimum under independent interval replay
for the frozen paper-R2 DAG, so direct 40-to-smaller deletion is closed.
Reopen it only after Phase 2 or through a localized correlation/fusion proof.
Each surviving candidate may go directly to namespaced ASM after a small
identity/range proof because the external contract is unchanged.

## Phase 5: scheduling and footprint closure

Compare the current 15.4-KiB straight-line leaf against narrowly scoped
realizations:

- two-row arithmetic interleave where liveness fits;
- branch-local compact/table-driven code;
- selective constant caching and memory-form constants.

Smaller `.text` is not a win.  Keep variants only when Native SUPERCOP agrees
and fixed-ELF normal/reversed placement plus ASLR controls do not reverse the
direction.

## Caller integration and promotion

Forward work proceeds beside, not instead of, the larger dual-output and tail
debts.  After a Forward candidate wins its intended boundary:

```text
winning Forward
  -> exact r dual-output/hash fanout
  -> PK decode/MA2/ciphertext tail
  -> full KAT and invalid-PK behavior
  -> Native SUPERCOP keypair/enc/dec
  -> common-compiler fixed-ELF placement controls
```

No Forward variant enters `clean/` unless the complete changed caller wins
and Native SUPERCOP does not regress.

## Current execution cursor

```text
Phase 1A W1 schedule/ASM/gates    complete
Phase 1A W1 Native pricing       rejected: +184.03 enc cycles vs control
Phase 1B W2 bounded feasibility  complete; no ASM after failed W1 control
Phase 2 NTT9/alpha co-design     next
```

The same-DAG wavefront family is closed.  It may be reopened only by a
materially different NTT9 microkernel or arithmetic DAG, not by paying the W2
constant-load trade after W1's Native regression.

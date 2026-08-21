# GT9x16 forward experiment: current diagnostic checkpoint

These are repository-local diagnostics, not SUPERCOP results and not promotion
evidence. They measure one fixed branch/terminal-coefficient 9×16 slice with
hot L1 data on CPU 1 of an Intel Core Ultra 7 155H. Each reported value is the
median of nine fresh launches; each launch uses 201 batches of 2,000 calls.

Source: `results/shear-intel155h-20260820-005/shear-diagnostic.json`.

| Brief layer | Current implementation | Median cycles/call | Status |
| --- | --- | ---: | --- |
| A | existing top split + existing transform | — | pending full caller harness |
| B | scalar materialized `Y` permutation only | 69.037 | diagnostic component |
| C | 27 blends + 9 materialization operations | 13.754 | differential passed |
| D | 27 blends + fused distance-8 | 35.826 | both branch tables passed |
| E | D + distances 4/2/1, with a memory boundary and nine row calls | 300.090 / 300.355 | correctness-first baseline |
| F | E + reference NTT9 | — | pending |

The E result is deliberately not optimized: stage-8 is materialized before
nine calls to the row kernel, and the row kernel constructs routing/twiddle
vectors from source-derived tables. It provides a measurable correctness
island, not a predicted final cost.

## Static compiler audit

Compiler: GCC 15.2, `-O3 -mavx2 -fno-inline` plus strict warnings.

| Function | Instructions | `.text` bytes | YMM allocation | Vector loads/stores | Vector stack spills |
| --- | ---: | ---: | ---: | ---: | ---: |
| 27-blend `Z` | 58 | 288 | 10 | 9 / 9 | 0 |
| materialized `Y` | 69 | 342 | 10 | 9 / 9 | 0 |
| shear + distance-8 | 162 | 796 | 12 | 9 / 9 | 0 |
| one-row distances 4/2/1 | 120 | 510 | 6 | 1 / 1 | 0 |

No audited function contains a conditional branch, division/modulo,
gather/scatter, or vector stack reference. The materialized version uses nine
`vblendps` half selections instead of literal `vperm2i128`; this is a compiler
choice with the same row result.

No conclusion about 9×16 versus the official transform is justified until A
and F exist and full-forward differential tests pass.

## Full-forward paired checkpoint

After A and F passed full-forward differential tests, the pinned Official AVX2
`poly_ntt` and the correctness-first GT path were linked into the same ELF and
measured with the same aligned small-input buffer, compiler flags, CPU pinning,
and hot-L1 residency. Input reset is outside the timed region. Sixteen blocks
per launch use `O-C-C-O` / `C-O-O-C`; each slot is the median of 96 transform
observations, across nine fresh launches.

Source: `results/transform-intel155h-20260820-001/transform-paired.json`.

| Transform | Median cycles |
| --- | ---: |
| pinned Official AVX2 forward | 750.0 |
| GT correctness-first full forward | 6965.5 |
| paired GT − Official | +6214.5 |

The paired-delta bootstrap 95% interval is `[+6213.0,+6220.75]` cycles. This
repository-local result is not SUPERCOP evidence, has no ASLR/link-placement
controls, and cannot promote production. It establishes that the current
correctness layout is about 9.29× slower end-to-end; it does not isolate the
future fused radix-8 or vector NTT9 potential.

GCC's static stack report is 5,696 bytes for the current full-forward wrapper
(two complete 1152-coefficient temporaries plus row islands), 608 bytes for
the scalar NTT9, 56 bytes for the adapter, and 8 bytes for top split. These are
correctness-baseline costs and explicit optimization targets, not a production
stack contract.

## Checkpoint C NTT16 island

Nine fresh pinned launches use 201 hot-L1 batches each. Leaf variants include
nine input loads and nine output stores; body replay places loads/stores outside
128 consecutive register-body iterations.

Source: `results/ntt16-intel155h-20260820-002/ntt16-diagnostic.json`.

| Variant | Median cycles/island | Interpretation |
| --- | ---: | --- |
| retained C reference | 289.533 | prior ~300-cycle baseline |
| C0 realistic leaf | 105.076 | selected structural port |
| C0 arithmetic body | 101.647 | diagnostic lower boundary |
| C1 split-representation leaf | 196.453 | rejected: duplicate arithmetic |

C0 removes about 64% of the reference cost. C1 is about 87% slower than C0:
eliminating two intermediate routing blends costs 36 additional vector
Montgomery multiplies. This is local diagnostic evidence only; the next gate
is register-to-register C0→NTT9 integration and a full-forward paired run.

## Checkpoint C2 terminal-pair packing

Source: `results/c2-intel155h-20260820-001/c2-diagnostic.json`.

| Two-island variant | Median cycles |
| --- | ---: |
| distance-8 C0, 18 chains | 38.539 |
| distance-8 C2, 9 pair-packed chains | 37.186 |
| full NTT16 C0, 72 chains | 181.199 |
| full NTT16 C2, 36 pair-packed chains | 266.010 |

The isolated distance-8 gain is only 3.5%; the full pair-packed transform is
46.8% slower. C2 is rejected and NTT9 work is paused pending a physical-layout
reassessment. See `CHECKPOINT-C2.md` for routing and memory-boundary counts.

## Checkpoint C3 persistent S/D routing

Source: `results/c3-intel155h-20260820-001/c3-diagnostic.json`.

| One two-terminal row-pair | Median cycles | Routing instructions |
| --- | ---: | ---: |
| C2 reconstruct/repack each layer | 72.619 | 44 |
| C3 Official-style persistent S/D | 50.413 | 18 |

C3 wins by 30.6% with the same four Montgomery chains and identical two-load,
two-store boundary. It selects persistent routing for the next nine-row/shear
integration experiment; it does not yet authorize NTT9 work.

## Checkpoint C4 nine-row persistent pair

Source: `results/c4-intel155h-20260820-001/c4-diagnostic.json`.

| Variant | Median cycles / nine-row pair |
| --- | ---: |
| C0 natural two islands | 179.941 |
| C4 from-Z sequential | 97.730 |
| C4 from-Z two-row pipeline | 95.277 |
| C4 natural, zero intermediate materialization | 147.811 |

Natural C4 wins by 17.9%, retains 36 Montgomery chains, and writes persistent
S/D without final reconstruction. This passes the local gate to start a vector
NTT9 that directly consumes this layout.

## Checkpoint D Official-stage paired baseline

Source: `results/official-stages-intel155h-20260821-001/official-stage-paired.json`.
The stage functions are mechanically extracted from pinned Official `ntt.s`;
their sequential composition passes 10,003 bit-exact comparisons with the
original function. Input reset is outside timing.

| Partition / implementation | Median cycles | Candidate - Official |
| --- | ---: | ---: |
| Official T0 | 70 | — |
| Official T3x3 | 252 | — |
| D-A persistent NTT9, four pairs | 321 | +69 |
| Official T2x4 | 474 | — |
| C4 from-Z, four pairs | 422 | -52 |
| C4 natural, four pairs | 630 | +156 |
| Official full forward | 754 | — |

The `630 - 422 = 208` cycle gap isolates the natural GT producer tax and is
consistent with the earlier 210.136-cycle estimate.
D-B remains the selected transform order because its exact basis oracle absorbs
the shear phase into p-dependent NTT16 twiddles. Checkpoint E leaves its
terminal ABI deliberately undecided.

## Checkpoint E benchmark policy

Forward remains a reported component metric, but it no longer selects the
NTT-domain ABI. After provisional A/B/C kernels exist, the primary paired
diagnostics are complete arithmetic paths:

```text
2F + BaseMul_scale + scale-correct adjusted inverse
F + BaseInv + scale-correct adjusted inverse
```

Every candidate includes forward stores, BaseMul/BaseInv load-side unpack,
arithmetic store-side repack, inverse loads, and normalization. Input reset is
outside timing; Official/candidate use the same compiler recipe, pinning,
residency, and symmetric block order. No isolated routing or forward win can
select or promote a representation. Formal promotion still requires native
SUPERCOP KEM and fixed-ELF evidence after the complete caller path exists.

## Checkpoint F-R3A benchmark status

F-R3A has no executable R1/R2 kernel and therefore reports no cycles. The
generated 18-to-10 chain count and three-to-two distinct-twiddle count are
algebraic diagnostics only. F-R3B must compare R0/R1/R2 in one ELF with the
same persistent-S/D input/output, compiler flags, pinning, residency, balanced
order, and observation count; adapters may not be omitted from a full-real
view.

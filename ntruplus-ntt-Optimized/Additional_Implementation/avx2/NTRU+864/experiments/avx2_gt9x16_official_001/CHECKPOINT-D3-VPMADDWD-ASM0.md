# D3 VPMADDWD ASM0 machine pricing

## Fair machine cutpoint

Static instruction count was not used to reject this candidate. Two real,
namespaced ASM functions were built with the same ABI:

```text
input:  two packed T3 operands + one 16-lane zeta table
output: three coefficient planes accepted by the existing inverse entry
```

The baseline performs `P(A)`, `P(B)`, then the pinned positive-zeta official
cubic arithmetic. The candidate consumes both packed operands directly with
the joint pair routing, exact MR32, packed diagonal products, and exact final
coefficient planes. This corrects the earlier one-P analytical accounting:
the machine benchmark charges two P networks because both benchmark inputs
start packed.

## Correctness and linked audit

The candidate passes 10,003 tile cases including endpoints, zeros, and
deterministic random canonical-by-signed-i16 inputs. Both ASM paths match the
scalar cubic oracle modulo q. Input immutability, 32-byte alignment, and
canaries pass.

| Linked property | Baseline | Candidate |
| --- | ---: | ---: |
| instructions | 115 | 131 |
| `.text` bytes | 624 | 837 |
| `vpmaddwd` | 0 | 12 |
| `vpsrad` / `vpsubd` | 0 / 0 | 6 / 6 |
| `vpackssdw` / `vpermq` | 0 / 0 | 3 / 3 |
| `vpshufb` | 18 | 33 |
| stack frame / vector spill / call | 0 | 0 |
| function alignment | 32 B | 32 B |

The 12 `vpmaddwd` instructions are six data dot products and six `t*q`
corrections. The final return boundary has one `vzeroupper` in both paths.

## Paired result

Method:

```text
PIE, ASLR enabled
CPU 1
9 fresh launches
16 paired blocks per launch
96 observations per slot
64 tile calls per observation
odd:  Baseline Candidate Candidate Baseline
even: Candidate Baseline Baseline Candidate
```

| Placement | Baseline | Candidate | Candidate - baseline | Direction |
| --- | ---: | ---: | ---: | --- |
| normal | 29 cycles | 33 cycles | **+4** | candidate slower 9/9 |
| reversed | 29 cycles | 33 cycles | **+4** | candidate slower 9/9 |

This is repository-local machine arbitration, not a Native SUPERCOP result
and not production evidence. It does, however, answer the scoped question:
the higher static count did **not** translate proportionally to cycles, but
the tested direct-packed realization still failed to produce a cycle win.

## Decision

Do not integrate this D3 realization into full BaseMul or KEM. Preserve the
exact MR32 primitive and routing oracle for a future candidate with a better
consumer geometry, but close this particular three-pair-sum realization.

Reproduce with:

```sh
make d3-asm0-check
make d3-asm0-price BENCH_CPU=1
```

Evidence:

```text
generated/d3-vpmaddwd-asm0-audit.json
results/d3-vpmaddwd-asm0-intel155h-20260910-001/tile-paired.json
```

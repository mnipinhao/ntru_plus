# GT32-LATE-SOA-065

Full GT32 polynomial-arithmetic-chain closure for the Late-SoA mechanism
qualified by experiments 063 and 064.  The measured public boundary is:

```text
two coefficient-order small polynomials
  -> current raw N5 frontend / top split / twist / DFT3
  -> 2F + quartic B3 + complete NTT32 inverse
  -> current inverse DFT3 / untwist / top merge / normalization
  -> coefficient-order polynomial result
```

No `crepmod3`, serialization, hash, or KEM caller is included.  GT Clean and
all production selectors remain unchanged.

## Profiles

- `C0`: current TILE4 Forward twice, materialized B3, current complete inverse.
- `C1`: current TILE4 Forward twice, AoS B3 redeposit fused through inverse I1,
  then the current remaining inverse and coefficient-output tail.
- `L0`: Late-SoA Forward terminal twice, SoA-native B3 fused through inverse
  I1, then the exact same remaining inverse and coefficient-output tail.

All profiles use the same `gt32_tile4_frontend_wide_raw_asm` and
`gt32_tile4_inverse_tail_t9_isolated_private_asm` symbols.  The three C
wrappers are each 137 bytes and have the same 7-call shape.  The experiment
adds no arithmetic or reduction mutation beyond the 064 bridge.

## Contract closure

| boundary | contract used by 065 |
|---|---|
| input | coefficient order, `e=0`, each coefficient in `[-3,4]` |
| frontend -> Forward | selected TILE4 raw-frontend contract, unchanged |
| Forward S3 -> Late-SoA suffix | exact 063/064 seam; same ring, scale, and logical leaves |
| Late-SoA inverse recovery -> remaining inverse | current TILE4 post-I1 contract |
| inverse core -> T9 tail | current AoS `e=-1` contract |
| output | coefficient order, `e=0`, exact modulo-q result |

The observed output bound (`1816`) is test evidence only and does not widen a
production range contract.  No extra reduction was inserted.  The full wrapper
allows `out == a` and `out == b`; scratch must remain aligned and disjoint.

## Reproduce

```sh
make test
make audit
make bench-short
make pmu
```

`bench_normal` and `bench_reversed` keep the three wrapper addresses fixed but
reverse the hot ASM object order.  Each launch alternates paired execution
order.  This is an architecture gate, not a KEM promotion benchmark.

## Correctness and static result

- 1,776 end-to-end cases pass exactly (`768` impulses, `8` structured, `1000`
  random `[-3,4]` cases).
- Each of `out == a` and `out == b` passes 136 cases.
- The existing 064 Late bridge has zero stack references and zero spills.
- Each full-chain wrapper is 137 bytes.  It performs five ABI register saves
  and restores, equally for all three profiles, but allocates no local frame.
- Scratch remains five 1536-byte polynomial slots (`7680` bytes) for every
  profile.

## Benchmark result

Median of eight launches per placement, candidate minus `C0`:

| placement | profile | 064 arithmetic subregion TSC | full chain TSC | integration closure |
|---|---|---:|---:|---:|
| Normal | `C1` | -2.06 | +2.83 | +4.88 |
| Normal | `L0` | **-72.26** | **-66.25** | +6.01 |
| Reversed | `C1` | -2.19 | -2.01 | +0.18 |
| Reversed | `L0` | **-73.07** | **-67.43** | +5.64 |

`L0` is negative in all 8/8 launches in both placements.  The common frontend
and tail isolated controls are approximately neutral in paired TSC.

Region PMU medians:

| placement | region | core cycles | instructions | loads | stores | branches |
|---|---|---:|---:|---:|---:|---:|
| Normal | arithmetic | -114.86 | -153.94 | +2.11 | +0.03 | -5.01 |
| Normal | full chain | **-114.17** | **-159.23** | +1.19 | -0.20 | -6.04 |
| Reversed | arithmetic | -121.15 | -165.25 | -0.16 | -0.51 | -5.11 |
| Reversed | full chain | **-117.64** | **-155.75** | +1.94 | -0.02 | -6.02 |

The PMU integration closure is only `+0.69` core cycles in Normal and `+3.50`
in Reversed.  Retired loads/stores remain effectively unchanged.  The result
therefore preserves 064's mechanism: Late-SoA is a cheaper executable
Forward-terminal/B3/inverse-entry DAG, not a memory-traffic reduction claim.

## Decision

**FULL_ARITHMETIC_CHAIN_PASS.**  The 064 gain survives both the true current
frontend and the true current coefficient-output inverse tail.  The next
eligible experiment is a caller-level gate, but 065 intentionally stops before
`crepmod3` or any KEM integration.

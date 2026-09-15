# Experiment 127 results

## Formal total

The exact same binaries were already qualified by native SUPERCOP in
Experiment 099:

| operation | Official StQ2 | GT Clean StQ2 | GT - Official |
| --- | ---: | ---: | ---: |
| Encap | 28,106.01 | 28,358.48 | **+252.47** |

GT is 0.898% slower.  The paired-block median was `+266.19`, with bootstrap
95% CI `[+218.08,+318.38]`.

## Direct Encap leaf intervals

128 balanced launches, `cpu_core/cycles/u`, period 50,000,
`any_call,any_ret`.  Values are medians of per-launch leaf-body medians.

| semantic component | Official | GT | GT - Official |
| --- | ---: | ---: | ---: |
| Decode public key | 170.00 | 203.50 | **+33.50** |
| CBD(r) | 120.00 | 144.00 | **+24.00** |
| r producer (NTT vs frontend+NTT) | 726.25 | 676.00 | **-50.25** |
| serialize r-hat | 212.00 | 257.75 | **+45.75** |
| SOTP(m) | 125.75 | 138.00 | **+12.25** |
| m producer (NTT vs frontend+NTT) | 724.00 | 678.50 | **-45.50** |
| general BaseMul | 525.00 | 511.00 | **-14.00** |
| add(m) + ciphertext serializer | 260.00 | 276.00 | **+16.00** |
| descriptive mapped-leaf total | 2,863.00 | 2,884.75 | **+21.75** |

The E0V baseline has no standalone GT `poly_add`: its virtual sum is included
in the final two-source serializer, so the comparison groups Official add and
pack together.

The current GT BaseMul is no longer a debt in this image.  Relative to the
older 055 profile (`+35.25`), it now measures about `-14`, while both Forward
producer paths remain winners.  The clearest mapped debts are Decode, CBD,
the r-hat serializer, SOTP, and the final serializer.

The `+21.75` mapped total must not be subtracted from `+252.47` and named as a
`+230.72` caller, frontend, or Hash component.  Hash/SHAKE is nested and is
intentionally excluded; LBR coverage, overlap, sampling skid, and omitted
intervals make the leaf medians descriptive rather than an additive full-path
reconstruction.

## PMU sampling attribution

Encap-visible LBR-chain samples:

| event | Official | GT | interpretation |
| --- | ---: | ---: | --- |
| cycles | 3,011 | 2,767 | visibility/sample count, not total cycles |
| IDQ uops not delivered | 2,421 | 2,190 | no broad GT frontend excess in this run |
| L1D pending cycles | 13 | **83** | strong GT-side data/load-pressure signal |

The main Keccak permutation occupies essentially the same share of visible
cycle samples: 83.36% Official and 83.23% GT.  This does not prove equal Hash
cycles, but it gives no profiler evidence that the unchanged Hash arithmetic
owns the GT gap.

GT's 83 visible L1D-pending samples concentrate in:

| GT symbol | samples | share of GT pending samples |
| --- | ---: | ---: |
| `ntruplus768_ntt_frontend_avx2` | 27 | 32.5% |
| `ntruplus768_unpack_m_body_avx2` | 20 | 24.1% |
| `ntruplus768_ntt_m_avx2` | 14 | 16.9% |
| `ntruplus768_basemul_general_m_avx2` | 9 | 10.8% |

The absolute pending-sample count is small, so it is a direction and PC map,
not a cycle budget.  Still, it independently supports a distributed
data-dependency explanation centered on Decode and the GT producer path.

## Engineering conclusion

`perf` can identify where GT Encap spends cycles and where PMU pressure lands,
but it does not reveal a single component worth the complete 252-cycle gap.
The present production map is:

- proven winners: both GT producer paths and current general B3;
- largest actionable leaf debt: r-hat serializer (`+45.75`);
- other medium debts: Decode (`+33.5`), CBD (`+24`), SOTP (`+12.25`), and
  final virtual-sum serializer (`+16`);
- strongest microarchitectural clue: extra GT L1D-pending pressure in
  frontend/Decode/NTT/B3;
- unexplained full-operation residual: compositional and non-additive, not a
  valid standalone component cost.

Future optimization should use the PC-level pending-load map to justify a
specific work-deletion or dependency change.  It should not reopen Hash or
rewrite B3 arithmetic based only on the full Encap delta.

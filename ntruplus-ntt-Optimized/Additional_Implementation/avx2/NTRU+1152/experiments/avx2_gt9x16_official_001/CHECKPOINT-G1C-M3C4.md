# Checkpoint G1C-M3C4: executable repaired full inverse16

All variants use the same proved Montgomery-by-identity repair on the D1
large/sum stream. `Mont(x,R mod q)=x mod q`, so the repair preserves scale and
the exact full-path proof bounds every later pre-Montgomery operation by
17,377.

The executable decomposition is:

```text
C0: raw BMScale boundary -> repaired D1 -> materialized D2/D4/D8
C1: live BMScale->repaired D1 -> materialized D2/D4/D8
C2: live BMScale->repaired D1 boundary -> persistent D2/D4/D8
```

C2 deliberately retains one post-D1 store/load boundary. A more aggressive
depth-first fusion into each BMScale result was priced at about 1,248 cycles
and rejected because it serializes the producer with a long inverse dependency
chain. The selected C2 instead loads physical-adjacent terminal vectors in
pairs, keeps D2/D4/D8 live, and writes only the final state.

Across 1,003 producer-real cases, C0/C1/C2 are bit-exact against the independent
scalar BMScale, repaired-D1, D2, D4, and D8 oracle. Input immutability, output
canary, strict build, ASan/UBSan, range/scale proof, and static ABI/constant-time
gates pass. The internal KEM leaf requires pairwise non-aliasing output and
operands; the current decapsulation caller satisfies that contract.

Static boundary traffic is:

| path | output loads | output stores |
| --- | ---: | ---: |
| C0 | 288 | 360 |
| C1 | 216 | 288 |
| C2 | 72 | 144 |

C2 removes 288 boundary memory instructions relative to C1. All leaves are
call/frame/stack/branch/`vzeroupper`-free and peak at 16 YMM registers.

Nine fresh CPU-1 launches, one ELF, 16 balanced six-slot blocks, and 96
observations per slot give:

| path | median cycles |
| --- | ---: |
| C0 | 1136 |
| C1 | 1108 |
| C2 | 1099 |

The paired medians are C1-C0 `-28`, C2-C1 `-9.5`, and C2-C0 `-37.5`; every
delta has the same winning direction in 9/9 launches. This is repository-local
diagnostic evidence, not SUPERCOP or production qualification.

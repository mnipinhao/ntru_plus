# Results

## Correctness and ABI controls

- 1000 generated M inputs: `pack(r_M) -> hash_g` and
  `gt142_hash_g_from_m(r_M)` are byte-exact at the 192-byte hash output.
- 1000 deterministic Encapsulations: ciphertext, shared secret, and return
  status are byte-exact.
- One explicit noncanonical public key: rejection output/status are exact.
- The helper is `noinline`.  Both full callers reserve the same 6592-byte
  frame (`0x19c0` after the shared page probe); the 1153-byte hash input is a
  callee-local object in both variants.
- The production Forward_M, r_M materialization, B3, QL2 path, and serializer
  assembly are unchanged.

## SUPERcop-style paired launches

CPU 1, ASLR on, 16 fresh launches per backend, alternating order:

| Backend | Region | Median candidate-control | 95% bootstrap CI | Favorable |
|---|---|---:|---:|---:|
| `default-perfevent` | pack+hash | **-58.94 core cycles** | [-87.56, -50.80] | 16/16 |
| `default-perfevent` | full Encap | -66.63 core cycles | [-125.50, +6.88] | 10/16 |
| RDTSCP | pack+hash | **-121.28 TSC** | [-351.92, -99.56] | 16/16 |
| RDTSCP | full Encap | **-230.75 TSC** | [-429.00, -105.00] | 15/16 |

The local mechanism is unambiguous.  Full Encap is directionally favorable,
and RDTSCP qualifies, but the primary `default-perfevent` CI narrowly crosses
zero.  This experiment therefore does not directly modify production.

## PMU corroboration

Median fixed-process totals were divided by 200,000 pack+hash calls and 20,000
full Encap calls:

| Region | core cycles | instructions | retired loads | retired stores |
|---|---:|---:|---:|---:|
| pack+hash candidate-control | **-66.50** | -142.59 | **-41.15** | **-38.07** |
| full Encap candidate-control | **-91.75** | -293.86 | **-37.04** | **-34.43** |

The memory deltas match the intended mechanism: the libc `memcpy` of 1152
bytes is gone.  Counts are smaller than a naive 72-load/72-store AVX copy
because the actual libc copy implementation and retired-memory accounting do
not map one-to-one to logical 32-byte chunks.

## Decision

```yaml
GT32-R-PACK-HASH-DIRECT-142:
  correctness: PASS
  local_operation_class_deletion: PASS
  local_cycles: PASS
  full_encap_rdtscp: PASS
  full_encap_default_perfevent: DIRECTIONAL_CI_CROSSES_ZERO
  production_modified: false
  decision: MECHANISM_QUALIFIED_PROMOTION_DEFERRED
```

The next gate, if selected, should be geometry-preserving production
integration: keep the production Encap slot and all shared hot symbols fixed,
place the noinline helper in a deterministic RX tail, and rerun all three KEM
operations.  It should not change serializer arithmetic or inline the helper.

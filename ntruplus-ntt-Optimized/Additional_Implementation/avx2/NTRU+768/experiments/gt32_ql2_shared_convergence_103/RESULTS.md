# Results

## Correctness and static contract

The following are byte-exact:

- 768 impulses and four structured boundary patterns;
- 1000 random centered polynomial pairs;
- `Forward_QL2 == M_to_QL2(Forward_M)`;
- `B3_QL2 == M_to_QL2(B3_M)`;
- `QL2_add_Q24 == M_add_Q24`;
- 1000 deterministic full Encapsulations, covering real SOTP-produced `m`;
- noncanonical public-key rejection.

All three leaves have zero stack references and zero push/pop spills. Loads,
stores, materialized bytes, scale, bounds, reduction, and packet-store
geometry are unchanged.

## Primitive and convergence island

Region-scoped PMU:

| Region | Core-cycle delta | Retired-instruction delta |
|---|---:|---:|
| Forward M -> QL2 | -86.3 | -144 |
| B3 M -> QL2 | +23.8 | +96 |
| QL2 add/Q24 | -49.4 | -96 |
| Complete convergence island | **-115.1** | **-144** |

The formal 16-launch SUPERcop-style result is `-96.66` core cycles with 95%
CI `[-97.06,-95.00]`, favorable in 16/16 launches. QL2 therefore receives:

```text
REPRESENTATIVE_ISLAND_PASS
```

The composed island is faster than the isolated primitive sum, so no hidden
materialization repayment appears at this boundary.

## Full caller and executable-image sensitivity

Two legitimate executable shapes give different full-caller conclusions
while the island remains stable:

| Image | Island core cycles | Full Encap core cycles | 95% CI |
|---|---:|---:|---:|
| Lean, before matched control | -93.86 | +11.88 | [-9.13,+32.31] |
| Expanded with matched control | -96.66 | **-83.16** | **[-100.88,-54.13]** |
| Common matched caller | — | **-119.72** | **[-134.50,-87.06]** |

The final PMU rerun reinforces the distinction between mechanism and delivery:
the island remains `-113.3` core cycles, but the ordinary and matched callers
move to `-173.0` and `-14.8` core cycles respectively. Both still retire
exactly 144 fewer instructions. Caller-level PMU magnitude is therefore
reported as attribution only, not as a promotion claim; the formal paired
SUPERcop-style timing above remains the primary result.

This proves two things separately:

1. shared QL2 is a real operation-class deletion and a strong caller-capable
   mechanism;
2. its natural full-caller delivery is not yet production-stable, because
   adding attribution-only code changed the sign of the ordinary caller while
   leaving the island result essentially unchanged.

## Decision

```yaml
GT32-QL2-SHARED-CONVERGENCE-103:
  correctness: PASS
  static_route_deletion: -144
  representative_island: PASS
  controlled_full_caller: PASS
  natural_image_robustness: FAIL
  status: CALLER_PASS_IMAGE_SENSITIVE
  production_promotion: DEFERRED
  production_modified: false
```

Do not reschedule the arithmetic or search a lucky placement. A future
promotion gate, if requested, must preserve the existing production hot-image
geometry and isolate the three private QL2 helpers in a controlled RX tail,
then repeat Keypair/Encap/Decap. Until that gate passes, `b2a4bea` remains the
production baseline.

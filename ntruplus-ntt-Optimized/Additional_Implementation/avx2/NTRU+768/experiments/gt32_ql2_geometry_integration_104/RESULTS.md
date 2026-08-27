# Results

## Geometry and correctness

- 84 pre-existing production-anchor symbols retain identical address, size,
  type, and machine bytes relative to the qualified `b2a4bea` E0V ELF.
- Control and QL2 images retain identical 611-byte Encap caller slots.
- The existing 4,914-byte E0V helper remains at the same page-aligned RX tail.
- The 6,226-byte QL2 cluster is appended in a separate page-aligned RX tail;
  its fixed order is Forward, B3, serializer.
- There is no RWX segment.
- 1000 deterministic Encapsulations, 768 noncanonical public keys, immutable
  inputs, ASan/UBSan, and both 948,402-byte KAT outputs pass byte-exactly.
- KAT SHA-256 remains
  `22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8`.

## Formal SUPERcop-style qualification

All campaigns use Core 1, fixed ELFs, ABBA/BAAB paired order, 16 blocks, and
both ASLR-on and ASLR-off.  The first campaign is retained but contains a few
whole-machine outliers; two independent confirmation campaigns were therefore
run without deleting or filtering the first result.

### Confirmation 1

| Setting | Operation | Mean delta | 95% CI | Negative blocks |
|---|---|---:|---:|---:|
| ASLR on | Keypair | -4.09 | [-37.70,+26.63] | 9/16 |
| ASLR on | Encap | **-127.75** | **[-232.25,-37.27]** | 14/16 |
| ASLR on | Decap | -59.05 | [-126.58,-5.00] | 9/16 |
| ASLR off | Keypair | -0.78 | [-14.39,+13.23] | 10/16 |
| ASLR off | Encap | **-84.23** | **[-91.39,-76.67]** | 16/16 |
| ASLR off | Decap | **+14.86** | **[+0.59,+29.02]** | 4/16 |

### Confirmation 2

| Setting | Operation | Mean delta | 95% CI | Negative blocks |
|---|---|---:|---:|---:|
| ASLR on | Keypair | -17.31 | [-38.38,+2.34] | 7/16 |
| ASLR on | Encap | **-71.50** | **[-115.02,-27.39]** | 14/16 |
| ASLR on | Decap | -20.42 | [-76.16,+25.64] | 9/16 |
| ASLR off | Keypair | -0.69 | [-20.36,+21.64] | 9/16 |
| ASLR off | Encap | **-81.09** | **[-93.61,-69.75]** | 16/16 |
| ASLR off | Decap | **+11.81** | **[+0.83,+23.61]** | 6/16 |

The geometry-preserved QL2 implementation therefore delivers a repeatable
roughly 80-cycle Encap improvement.  Keypair is neutral.  However, the small
ASLR-off Decap regression repeats in both clean confirmation campaigns.

## Decision

```yaml
GT32-QL2-GEOMETRY-INTEGRATION-104:
  architecture: PASS
  production_encap: PASS
  keypair_collateral: NEUTRAL
  decap_collateral: ASLR_OFF_REGRESSION_REPRODUCED
  production_promotion: DEFERRED
  official_comparison: NOT_RUN_UNQUALIFIED_CANDIDATE
  production_modified: false
```

The predeclared promotion rule required stable negative Encap and no stable
Keypair/Decap regression.  Because Decap regresses by about 12--15 cycles in
two independent ASLR-off campaigns, this experiment does not modify GT Clean.
The QL2 result remains a production-capable Encap mechanism; the remaining
problem is cross-operation executable delivery, not QL2 arithmetic.

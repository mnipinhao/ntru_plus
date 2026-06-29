# GT KEM profile summary and Slothy target audit

Date: 2026-06-29

Scope: documentation and target selection only.  This note does not change
production defaults, does not change Q31 behavior, does not run Slothy, and does
not start the `polyinv()` rewrite.

Source profile:

```sh
make -C aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

PMU settings:

```text
NTESTS=31
NITERATIONS=5000
NWARMUP=100
NINPUTS=64
CORE=3
correctness,total_mismatches=0,valid_cases=64
```

Full details and residual calculations are recorded in
`gt-production-kem-component-profile-pmu.md`.

## Q31 RC frozen conclusion

`direct32_q31` is complete as a default-off encap-only byte-contract release
candidate.

Contract:

```text
gate: GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
scope: encap only
consumer: immediate poly_tobytes(ct, &c)
generic poly_basemul_add: not overwritten
decap/arithmetic consumers: no Q31 call
public header exposure: none
```

PMU:

| window | current cycles/call | q31 cycles/call | delta |
| --- | ---: | ---: | ---: |
| direct `poly_basemul_add` | 2902.047 | 2486.768 | -415.279 |
| full encap | 38804.372 | 38336.448 | -467.924 |

Conclusion:

```text
Q31 should remain frozen as an opt-in encap byte-contract path.
Do not extend it into generic poly_basemul_add.
Do not use it in decap or arithmetic consumers.
```

## Keygen profile summary

`keypair_total = 39186.452 cycles/call`.

| component | cycles/call | keygen share | note |
| --- | ---: | ---: | --- |
| `keygen_polyinv_scaled_x2` | 10042.051 | 25.6% | two `poly_baseinv_scaled_r` calls |
| `keygen_sample_prebaseinv_x2` | 11811.740 | 30.1% | two sample/CBD/triple/NTT pre-baseinv paths |
| `keygen_public_arithmetic_x2` | 4086.035 | 10.4% | two scaled keypair basemuls |
| `keygen_pack_hashf_total` | 13168.972 | 33.6% | pk/sk packing plus `hash_f` |

Conclusion:

```text
polyinv/baseinv is the largest non-hash keygen block.
If keygen is selected as the next mainline, a polyinv algorithm rewrite is
supported by this profile.
Do not implement that rewrite in this task.
```

## Encap residual split conclusion

`encap_total = 38094.448 cycles/call`.

Hash-dominated blocks:

| component | cycles/call | encap share |
| --- | ---: | ---: |
| `encap_hash_f_pk` | 11914.910 | 31.3% |
| `encap_hash_h_msg` | 2753.841 | 7.2% |
| `encap_hash_g_body` | 13150.485 | 34.5% |

Remaining non-hash encap blocks:

| component | cycles/call | encap share |
| --- | ---: | ---: |
| `encap_ntt_r` | 2704.884 | 7.1% |
| `encap_ntt_m` | 2704.136 | 7.1% |
| `encap_basemul_add` | 2864.475 | 7.5% |

Residual conclusion:

```text
Encap residual is truly hash-dominated.
No hidden non-hash residual block above the 3% threshold remains.
Stop encap residual investigation.
```

This also explains the Q31 result: a local `poly_basemul_add` win can be real
and still only move full encap by about 1.2%.

## Decap profile summary

`decap_total = 33285.358 cycles/call`.

Important blocks:

| component | cycles/call | decap share | note |
| --- | ---: | ---: | --- |
| `decap_basemul_rminus1` | 2028.196 | 6.1% | first basemul |
| `decap_invntt_rminus1` | 4024.985 | 12.1% | InvNTT from rminus1 contract |
| `decap_verify_basemul` | 2823.360 | 8.5% | verification basemul |
| `decap_ntt_m1` | 2710.132 | 8.1% | recovered-message forward NTT |
| `decap_ntt_r1` | 2705.003 | 8.1% | re-encryption forward NTT |
| `decap_crepmod3` | 382.569 | 1.1% | small |

Boundary estimate:

```text
decap_basemul_invntt_rminus1_pair
  - decap_basemul_rminus1
  - decap_invntt_rminus1
= 80.175 cycles = 0.2% decap
```

Conclusion:

```text
The basemul -> InvNTT boundary estimate is too small to justify a
boundary/fusion mainline.
InvNTT itself is a meaningful local target.
Forward NTT is a meaningful repeated local target.
Generic/rminus1 basemul cleanup may be considered, but Q31 must not be reused
for decap because decap needs arithmetic-correct output.
crepmod3 is not a priority.
```

## Decision matrix

| decision | support from profile | status |
| --- | --- | --- |
| A. `polyinv` algorithm rewrite becomes mainline | `polyinv/baseinv x2` is 25.6% of keygen and the largest non-hash keygen block | Supported if optimizing keygen next; not started here |
| B. decap basemul -> InvNTT layout/fusion becomes mainline | Boundary estimate is only 80.175 cycles / 0.2% decap | Not supported |
| C. encap has a non-hash residual block worth fixing | Hidden non-hash residuals are below 3% full encap | Not supported |
| D. only local NTT/InvNTT/basemul cleanup remains | Repeated medium blocks remain, but no single large non-hash encap/decap residual | Supported for encap/decap |

## Slothy target audit

This is a target-selection audit only.  Slothy was not run.

| candidate | affected API | current cycles | API share | contract status | Slothy readiness | recommendation |
| --- | --- | ---: | ---: | --- | --- | --- |
| Forward NTT | keygen, encap, decap | encap `ntt_r` 2704.884; encap `ntt_m` 2704.136; decap `ntt_m1` 2710.132; decap `ntt_r1` 2705.003 | each 7.1-8.1%; repeated across APIs | Production path is valid; prior rowspec/output-layout experiments are not production candidates | Promising only after the exact production contract and output-layout target are fixed; current rowspec path should not be promoted | Promising cross-API target, but only after rowspec/output layout is fixed |
| InvNTT rminus1 | decap | 4024.985 | 12.1% decap | Production `poly_invntt_from_rminus1` contract is active and correctness-tested in full decap | Clean Slothy candidate if standalone correctness and full decap differential are available | Good local candidate; prepare contract and tests before scheduling |
| generic/rminus1 basemul | decap, keygen, encap | `basemul_rminus1` 2028.196; verify basemul 2823.360; encap add 2864.475 | 6.1-8.5% in decap, 7.5% in encap | Output must remain arithmetic-correct except the already-frozen encap Q31 byte-contract path | Possible local cleanup target after exact lane/output contract audit | Consider local cleanup; do not reuse Q31 for decap |
| basemul -> InvNTT fusion | decap | boundary estimate 80.175 | 0.2% decap | Pair path is correct, but no large adapter cost is visible | Not ready; current profile does not justify building a fusion prototype | Do not open as mainline from this data |
| encap residual/hash/copy | encap | hash_f 11914.910; hash_h 2753.841; hash_g 13150.485; non-hash residuals below threshold | hash blocks dominate; non-hash hidden residuals below 3% | Hash backend is out of scope; copy/CBD/SOTP are small | Not a Slothy target | Stop residual investigation |
| crepmod3 | decap | 382.569 | 1.1% decap | Correct and isolated | Too small to justify scheduling work | Not priority |
| polyinv | keygen | `keygen_polyinv_scaled_x2` 10042.051 | 25.6% keygen | Current algorithm is correct; rewrite not part of this task | Slothy is not the first step; algorithm/range design comes first | Handle separately as algorithm rewrite candidate, not here |

Final target-selection summary:

```text
If choosing a new mainline now, keygen polyinv/baseinv has the strongest
non-hash single-block evidence.

For encap/decap, the data supports smaller local arithmetic cleanup only:
forward NTT, InvNTT rminus1, and possibly basemul.  It does not support
reopening encap residual, crepmod3, or basemul->InvNTT fusion as major routes.
```

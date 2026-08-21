# GT32 experiment index: 030--059E

This index records the decision lineage after the representation survey in
experiments 013--029.  Experiments are default-off evidence unless their own
status explicitly says that a result was copied into GT Clean.  A local or
fixed-geometry win is not a production promotion.

## Reading the archive

The evidence levels are intentionally distinct:

1. **Static/generator gate** proves algebra, range, mapping, or a scoped lower
   bound.  It does not make a cycle claim.
2. **Matched local gate** identifies an intrinsic mechanism while holding code
   geometry fixed.
3. **Exact-image gate** decides whether that mechanism survives in a real
   linked operation.
4. **Formal SUPERcop-style benchmark** compares independent production images
   and determines the operation selector.

`superseded` means a later experiment corrected the interpretation; the old
measurement may remain valid.  `closed` is scoped to the stated ABI, ISA, and
consumer contract, not a universal impossibility proof.

## Production reference

[The 2026-08-20 formal run](gt32_supercop_clean_formal_20260820/) is the
archived production comparison before experiments 033--059 were adjudicated:

| Operation | GT Clean minus Official | Relative | Decision |
|---|---:|---:|---|
| Keypair | -302.98 cycles | -1.411% | GT wins |
| Encap | +245.24 cycles | +0.875% | Official wins |
| Decap | -188.57 cycles | -0.975% | GT wins |

The implementation selector therefore remained operation-specific.  The
formal result is an image-level benchmark; it must not be used as the cycle
cost of any individual leaf.

## 030--035: progressive M and Encap boundary work

| Gate | Status | Durable conclusion |
|---|---|---|
| [030](gt32_n5_progressive_soa_030/) | closed, scoped | Affine packed-to-M terminal routing has an exact 12-instruction minimum in the searched family; broader progressive-M work was already covered by the global-layout gates. |
| [031](gt32_encap_lifetime_031/) | correctness-qualified prototype | Encap can reuse a dead polynomial lifetime and reduce scratch by 1536 bytes without changing outputs.  Delivery required later causal gates. |
| [032](gt32_encap_b3_addm_032/) | local win, full-caller stop | B3 final-store add-m deletes 48 loads and 48 stores and wins locally, but does not produce a stable full-Encap improvement. |
| [032R](gt32_range_contract_audit_032r/) | correctness contract pass | The selected Q24 encoder is valid for the actual wider executable range; historical numeric symbol names are not current bounds. |
| [033](gt32_encap_delivery_033/) | closed | Equal-size offset cages proved address-sensitive delivery; no magic B3 padding was selected. |
| [033B](gt32_encap_delivery_033b/) | experimental order only | Deterministic hot-section ordering can alter whole-caller delivery, but is not itself a production arithmetic result. |
| [034](gt32_q24_canon_minuw_034/) | local qualified, not promoted | `vpaddw` + `vpminuw` is a real Q24 canonicalization win (about 20 core cycles per pack), but whole-Encap delivery did not justify direct promotion. |
| [035](gt32_encap_promotion_035/) | closed, no promotion | Fixed-ELF promotion gate retained Official for Encap and stopped treating a favorable local placement as a production claim. |

## 036--040: code shape and delivery causality

| Gate | Status | Durable conclusion |
|---|---|---|
| [036](gt32_compact_frontend_036/) | superseded by 036R | The historical whole-image improvement was real, but its original attribution to the compact active schedule was wrong. |
| [036R](gt32_compact_frontend_036r/) | complete reclassification | With later addresses fixed, the compact frontend is intrinsically neutral; releasing its padding changes later symbol placement and causes the large image effect. |
| [037](gt32_compact_q24_037/) | closed, not promoted | Compact Q24 pays a measurable dynamic entry fee and gives no stable whole-KEM gain. |
| [037R](gt32_compact_q24_037r/) | complete, not promoted | Equal-address compact Q24 is slower/neutral; footprint release is a separate image-layout effect. |
| [038](gt32_hot_code_pareto_038/) | no equal-address winner | Looping/compacting the tested Q24 and inverse bodies sacrifices dynamic scheduling freedom and does not intrinsically win. |
| [039](gt32_internal_abi_vzeroupper_039/) | closed | Removing internal `vzeroupper` at fixed-size AVX2 edges saves one instruction but has no promotion-grade cycle effect. |
| [040](gt32_delivery_robustness_040/) | closed | Code address affects both Official and GT.  No single hot cluster explains 100--200-cycle image swings; equal-size cages remain the correct mechanism gate. |

The combined result is:

```text
code compaction != intrinsic speedup
code relocation can change a whole image substantially
local mechanism decisions require fixed geometry
production decisions require the exact linked image
```

## 041--047: load-to-compute and B3 specialization

| Gate | Status | Durable conclusion |
|---|---|---|
| [041](gt32_load_to_compute_041/) | local mechanisms qualified | Decode mask residency saves about 6--7 cycles and B3 qinv preload about 9 cycles locally; Q24 constant residency is neutral/negative. |
| [042](gt32_load_to_compute_composite_042/) | closed, not selected | Combining locally valid changes is placement-sensitive and does not establish an Encap production win. |
| [043](gt32_load_to_compute_production_043/) | Encap rejected, Decap signal qualified | Exact-image DB is neutral for Keypair, unproven for Encap, and about 43 cycles faster for Decap. |
| [044](gt32_decap_load_to_compute_044/) | causal decomposition complete | The Decap effect belongs primarily to the general-B3 qinv-preload callsite; Decode3 and scale-B3 changes are not independently selected. |
| [045](gt32_decap_private_b3_045/) | fixed-geometry qualified, exact-image rejected | A Decap-private general-B3 is intrinsically faster, but adding the private symbol perturbs the image enough to lose production stability. |
| [046](gt32_shared_general_b3_preload_046/) | conditional, not promoted | Reusing the shared symbol avoids a clone, but the small image-level benefit is not repeat-stable and moves unrelated Keypair. |
| [047](gt32_cross_symbol_census_047/) | closed | No zero-repayment cross-symbol sharing candidate of at least 1 KiB exists in the selected image. |

This wave proves that more instructions can be faster: the winning B3 preload
trades 12 instructions for 36 fewer loads.  Selection is based on measured
resource and cycle behavior, not instruction count alone.

## 048--055: exact-production Encap attribution

| Gate | Status | Durable conclusion |
|---|---|---|
| [048](gt32_encap_context_reentry_048/) | complete | Real caller history erodes the GT island advantage by only about 11--12 cycles; it cannot explain the full Encap gap. |
| [049](gt32_exact_production_prefix_frontier_049/) | cumulative map | Prefix checkpoints locate where the GT-vs-Official gap moves, but adjacent prefix differences are not component costs. |
| [050](gt32_encap_fine_prefix_frontier_050/) | complete, later corrected | Both serializers worsen the cumulative gap; the apparent jump across `hash_g` was a checkpoint movement, not proof of Hash cost. |
| [051](gt32_encap_q24_packet_range_051/) | static hard stop | Every real Encap packet/lane remains in the full-reducer range class; producer-specific sign-only/one-q packing is unsafe. |
| [052](gt32_hash_handoff_052/) | closed | Same-address Hash timing is identical after GT and Official producers; store handoff, `mfence`, and common-copy hypotheses are rejected. |
| [052A](gt32_prefix_checkpoint_audit_052a/) | closed | The B2/B3 prefix difference is not a `hash_g` component cost. |
| [053](gt32_hash_code_address_053/) | closed | Hash/SHAKE address geometry contributes less than the actionable threshold; the Hash attribution branch is sealed. |
| [054](gt32_serializer_boundary_054/) | closed | Q24 costs about 20 TSC more than Official serialization at each real Encap site; this is real but below the architecture reopen threshold. |
| [055](gt32_exact_elf_dynamic_map_055/) | closed | Encap has distributed medium debts (Decode, CBD/context, B3 context, two serializers), offset by two faster Forwards; no single hidden leaf owns the full gap. |

The stable interpretation of Encap is therefore not “Hash is slow” and not
“one 150-cycle function is missing.”  It is a distributed integration cost
plus two real low-tens-of-cycles serializer boundaries.

## 056--057: data geometry and active working set

| Gate | Status | Durable conclusion |
|---|---|---|
| [056](gt32_encap_data_geometry_056/) | closed | Permuting the same five 1536-byte stack objects does not recover CBD, B3, or full-caller debt. |
| [057](gt32_encap_active_working_set_057/) | closed | Reusing one lifetime without deleting a complete store/reload does not yield a stable latency or L1D-pending win. |

Reopen the memory-side line only when a complete materialization, store/reload,
or operation class disappears, or when hardware sampling identifies a
specific stall-owning load.

## 058--059E: new quartic representations

| Gate | Status | Durable conclusion |
|---|---|---|
| [058](gt32_encap_tensor_basis_058/) | research foundation | Establishes the broader Encap tensor/representation search outside current B3 scheduling. |
| [059](gt32_quartic_tensor_059/) | algebra pass | Exact rank-7/rank-8 quartic bilinear families exist; algebraic product count alone is not a performance result. |
| [059B](gt32_quartic_tensor_lowering_059b/) | research continues | R7 even/odd lowering is executable in principle; producer/consumer-native quadratic leaves motivate the separate 060 architecture line. |
| [059C](gt32_persistent_r7_encap_059c/) | lowering candidate | Persistent seven-evaluation representation deletes current quartic operation classes but introduces wider storage and a late-exit problem. |
| [059D](gt32_persistent_r7_late_exit_059d/) | executable late-exit pass, interpretation corrected | The late exit is correct for degree-three reconstruction but expensive; its original lambda-product claim is superseded by 059E. |
| [059E](gt32_r7_consumer_island_059e/) | current E7 consumer island closed | Correct full product-plus-message-to-wire variants lose by 237--398 TSC.  Reopen only with a producer-native representation that keeps the late map sparse or a changed consumer contract. |

## Current research boundary

Production GT Clean remains separate from this archive.  The practical state
after 059E is:

- current N5/B3/I1 arithmetic and current Q24 micro-scheduling remain frozen;
- delivery experiments are diagnostic methodology, not padding recipes;
- the standard d=4/E7 late-exit consumer island is closed;
- future continuation requires a materially different producer-native
  representation, consumer contract, decomposition, prepared-key cost model,
  or ISA—not another rearrangement of the same local DAG.

## Artifact policy

Commit source, generators, proofs, compact analyzed results, exact manifests,
and status documents.  Do not commit reproducible build trees, benchmark
executables, raw `perf.data`, or complete copied SUPERcop exports.  Large raw
JSON is retained only when it is the primary statistical evidence and no
compact sufficient record exists.

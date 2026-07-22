# AArch64 benchmark result families

Commit benchmark evidence by optimization family. Keep only reproducible
`summary.md`, `summary.json`, and small hand-curated CSV files in Git. Generated
executables, dependency files, raw counter output, and build logs are local
artifacts.

## Production milestones

- `gt_vs_kpqc_after_invntt_promotion_2026-07-10/`
- `gt_production_g1r123s2_threeway/`
- `gt_production_cleanup_final_2026-07-21/`
- `gt_production_source_closure_2026-07-22/`

## Forward NTT

- `u01v3_g1_r123_paired_kem/`
- `gt_frontend_dce_canonical_neon_threeway_2026-07-18/`

## Serialization

- `serialization_candidates_2026-07-18/`
- `gt_kpqc_pack_profile_2026-07-18/`
- `gt_kpqc_component_profile_serialization_*/`
- `gt_kpqc_production_pack_promoted_2026-07-18/`
- `gt_production_pack_promoted_threeway_2026-07-18/`

## Base inversion

- `gt_baseinv_*.csv`
- `gt_kpqc_paper_hier_k8_*/`
- `gt_kpqc_component_profile_baseinv_tree_promoted_2026-07-19/`

## Inverse and pointwise integration

- `gt_kpqc_component_profile_post_f2_*/`
- `gt_kpqc_component_profile_q31_pair_promoted_2026-07-20/`

Directories containing only local `bin/`, `raw/`, or build-log artifacts are
not benchmark records and should not be staged.

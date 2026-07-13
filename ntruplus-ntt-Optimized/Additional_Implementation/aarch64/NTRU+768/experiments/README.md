# Experiment index

Experiment directories retain the source, proof, benchmark evidence, and
decision needed to reproduce prior optimization work. They are not production
dependencies.

| Experiment | Current disposition |
| --- | --- |
| `forward_ntt_phase123_u01/` | promoted: G1R123+S2 production artifact lives under `asm/gt/` |
| `keygen_sample_ntt_fusion/` | promoted: fresh scheduled Phase123 triple/add1 artifacts live under production paths; older inserted-multiply variants are stopped |
| `baseinv_hier_k8/` | promoted implementation path; retained for audit and candidate history |
| `invntt_next_wave/` | paused: range proofs and Slothy inputs retained; no active production dependency |
| `ntt_loose_contract/` | stopped: insufficient range proof |
| `keygen_public_arith_pair/` | rejected: measured regression |
| `keygen_direct_h_hinv/` | stopped: wrapper/floor model did not meet promotion bar |
| `keygen_finish_to_h_hinv_fused/` | design-only: no implementation candidate |
| `keygen_sample_prebaseinv_split/` | measurement-only PMU split |
| `base_gt_direct_bytes/` | document/model-only; includes direct32 finalizer prototype |
| `decap_verify_byte_contract/` | reference contract only |

New work should begin in a new, narrowly named directory with a README that
states its contract, correctness oracle, benchmark gate, and final decision.
When work finishes, update this table instead of leaving its status implicit.

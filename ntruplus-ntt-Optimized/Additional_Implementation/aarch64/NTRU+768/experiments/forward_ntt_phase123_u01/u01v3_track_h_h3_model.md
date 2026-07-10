# U01v3 Track H3 Minimal Block3 Reconstruction State

Status: model-only complete. No ASM emitted, no Slothy run, no Makefile or production change.

## Semantic dependency cone

For each Stage12 stripe `s`, define:

```text
L_s = A_s + C_s
M_s = A_s - C_s
H_s = B_s + D_s                  (mod q identity reduction)
T_s = w * (B_s - D_s) mod q      (w = -708 mod 3457)

Q[s]    = L_s + H_s
Q[8+s]  = L_s - H_s
Q[16+s] = M_s + T_s
Q[24+s] = M_s - T_s
```

This is a semantic, lane-wise finite-field model. Physical q-register names do not participate in the proof.

## Rank result

```text
Stage12 rank per stripe:                 4
rank(Q0..Q23), eight stripes:            24
rank(Q0..Q31), eight stripes:            32
missing rank for Q24..Q31 given Q0..Q23: 8
minimum exact reconstruction state:       8 vectors
```

The important point is that the eight stripes are independent. Knowing the first three outputs of each 4-point Stage12 transform leaves one independent vector dimension per stripe. Across eight stripes that is eight vectors, not one shared vector.

## H3a: retain 1-4 vectors

- 1 vectors: checked 8 subsets; best rank gain 1; 7 block3 dimensions remain.
- 2 vectors: checked 28 subsets; best rank gain 2; 6 block3 dimensions remain.
- 3 vectors: checked 56 subsets; best rank gain 3; 5 block3 dimensions remain.
- 4 vectors: checked 70 subsets; best rank gain 4; 4 block3 dimensions remain.

All H3a candidates fit the simple register-cardinality count, but none can reconstruct all `Q24..Q31`; they fail the semantic hard gate before register allocation matters.

## H3b: reduced basis

`M_s=A_s-C_s` or `T_s=w(B_s-D_s)` is enough together with `Q[16+s]`, but one such basis vector is required for every stripe:

- `H3b_reduced_basis_low_diff_M`: 8 vectors, reconstructs all = true, max live q regs including q0 = 33, extra arithmetic = 48.
- `H3b_reduced_basis_twisted_high_diff_T`: 8 vectors, reconstructs all = true, max live q regs including q0 = 33, extra arithmetic = 48.

A complete register-resident basis creates 24 existing E3 values + 8 basis values = 32 data vectors while q0 leaves only 31 data-capable q registers. A memory-resident basis uses the same 24 stores and 24 loads as G1, then adds 48 reconstruction instructions across three rows.

## H3c: linear combinations

- `H3c_four_pair_sums`: reconstructs all = false; gate = `reject_semantic_rank`.
- `H3c_general_linear_combinations_k1_to_k4`: reconstructs all = false; gate = `reject_semantic_rank`.
- `H3c_full_chain_basis_boundary`: reconstructs all = true; gate = `reject_no_compression`.

Cross-stripe sums and differences do not compress independent vector dimensions. Four pair sums leave four pair-difference dimensions unknown. An eight-vector invertible chain basis works, but is the same size as direct `Q24..Q31` and adds encode/decode arithmetic.

## Decision

```text
register_resident_primary_candidate: none
emit_physical_asm: false
hard_gate_status: stop_h3
```

H3 cannot replace G1's block3 scratch boundary with a smaller exact same-lane reconstruction state. The remaining viable Track H direction is H1/H2 producer-consumer lifetime reordering, where block3 is produced after earlier outputs have been consumed instead of being compressed.

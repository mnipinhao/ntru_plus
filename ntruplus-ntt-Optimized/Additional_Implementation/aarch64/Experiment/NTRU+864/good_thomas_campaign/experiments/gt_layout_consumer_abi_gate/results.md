# Results

Status: passed locally on 2026-08-31.

```text
gt864_layout_consumer_abi_gate=pass
forward_final_store=two_soa_tiles_of_8_leaves_per_96_bytes
basemul_input=soa_tile8,j0_then_j1_then_j2
basemuladd_addend=same_soa_tile8
physical_leaf_count=288
top_alpha_leaves=144
top_beta_leaves=144
mapping_sha256=a96a8cd03ecba6a15d539eaa00860501088796ffb15083d6bc72e55551444b4c
```

The gate checks source-level Forward stores, BaseMul/BaseMulAdd loads and
stores, all 288 BaseMul zeta lanes, the 144/144 alpha/beta partition, and the
exact physical-leaf to 2-by-9-by-16 logical map.

Physical groups `0..17` contain the 144 alpha leaves and groups `18..35`
contain the 144 beta leaves.  Corresponding alpha and beta groups have the
same `(row,column)` lane pattern.  A tile is not a fixed row or fixed column:
the stock factor-tree order mixes both coordinates inside each eight-lane
vector.  This is a legacy order, not a required BaseMul property; the data
lanes and `zetas_mul` lanes merely have to be permuted together.

No performance or Production claim is made.

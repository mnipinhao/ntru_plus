# F32X3 inverse NTT32 stage 0

`gt_d4aos_f32x3_invntt32_stage0_avx2` performs the 48 accepted intra-YMM
inverse length-2 groups.  It swaps qword pairs only within their 128-bit
branch half, forms canonical sum/difference, and stores the stage state.  The
reference checkpoint is `d4aos_f32x3_ref_inverse_checkpoint_stage0`.

The default-off sanitizer target passes 768 physical basis states and 10,000
deterministic canonical random states.  Unsanitized object audit: symbol size
0x92 bytes; emitted `vpermq`, `vpaddw`, and `vpsubw`; no calls and no stack
frame/vector spill.  This file records only stage 0, not a complete inverse.

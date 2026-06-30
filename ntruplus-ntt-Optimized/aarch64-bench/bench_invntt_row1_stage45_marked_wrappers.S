/*
 * Benchmark-only wrappers for materialized InvNTT rminus1 ROW1-STAGE45
 * Slothy input variants.
 *
 * These wrappers set the concrete live-in contract expected by
 * asm/slothy/window_inputs/invntt_rminus1_row1_stage45_stripes_marked.s and
 * the selected Slothy candidate.  They are not production entrypoints.
 */

.text
.align 2

.global bench_invntt_rminus1_row1_stage45_marked_canonical
.type bench_invntt_rminus1_row1_stage45_marked_canonical, %function
bench_invntt_rminus1_row1_stage45_marked_canonical:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    mov x2, x0
    mov x14, x1
    adr x5, .Lbench_invntt_row1_inv_consts
    ldr q0, [x5]
    adr x3, .Lbench_invntt_row1_stage45_consts
    bl invntt_rminus1_row1_stage45_stripes_marked_slothy_input
    ldp x29, x30, [sp], #16
    ret
.size bench_invntt_rminus1_row1_stage45_marked_canonical, .-bench_invntt_rminus1_row1_stage45_marked_canonical

.global bench_invntt_rminus1_row1_stage45_slothy_stripes2_3
.type bench_invntt_rminus1_row1_stage45_slothy_stripes2_3, %function
bench_invntt_rminus1_row1_stage45_slothy_stripes2_3:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    mov x2, x0
    mov x14, x1
    adr x5, .Lbench_invntt_row1_inv_consts
    ldr q0, [x5]
    adr x3, .Lbench_invntt_row1_stage45_consts
    bl invntt_rminus1_row1_stage45_stripes2_3_n1_slothy_candidate
    ldp x29, x30, [sp], #16
    ret
.size bench_invntt_rminus1_row1_stage45_slothy_stripes2_3, .-bench_invntt_rminus1_row1_stage45_slothy_stripes2_3

.global bench_invntt_rminus1_row1_stage45_slothy_all4
.type bench_invntt_rminus1_row1_stage45_slothy_all4, %function
bench_invntt_rminus1_row1_stage45_slothy_all4:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    mov x2, x0
    mov x14, x1
    adr x5, .Lbench_invntt_row1_inv_consts
    ldr q0, [x5]
    adr x3, .Lbench_invntt_row1_stage45_consts
    bl invntt_rminus1_row1_stage45_all4_n1_slothy_candidate
    ldp x29, x30, [sp], #16
    ret
.size bench_invntt_rminus1_row1_stage45_slothy_all4, .-bench_invntt_rminus1_row1_stage45_slothy_all4

.align 4
.Lbench_invntt_row1_inv_consts:
    .hword 3457, 19412, -723, -6853, 1634, 15488, -18, -171
    .hword -36, -341, 1701, 16123, 0, 0, 0, 0

.align 4
.Lbench_invntt_row1_stage45_consts:
    // j=0
    .hword      1,      1,    708,      0,      0,      0,      0,      0
    .hword      9,      9,   6711,      0,      0,      0,      0,      0
    // j=1
    .hword    -39,   -436,  -1015,      0,      0,      0,      0,      0
    .hword   -370,  -4133,  -9621,      0,      0,      0,      0,      0
    // j=2
    .hword   1521,    -39,     44,      0,      0,      0,      0,      0
    .hword  14417,   -370,    417,      0,      0,      0,      0,      0
    // j=3
    .hword   -550,   -281,   1558,      0,      0,      0,      0,      0
    .hword  -5213,  -2664,  14768,      0,      0,      0,      0,      0
    // j=4
    .hword    708,   1521,  -1716,      0,      0,      0,      0,      0
    .hword   6711,  14417, -16266,      0,      0,      0,      0,      0
    // j=5
    .hword     44,    588,   1464,      0,      0,      0,      0,      0
    .hword    417,   5573,  13877,      0,      0,      0,      0,      0
    // j=6
    .hword  -1716,   -550,   1241,      0,      0,      0,      0,      0
    .hword -16266,  -5213,  11763,      0,      0,      0,      0,      0
    // j=7
    .hword   1241,   1267,   1673,      0,      0,      0,      0,      0
    .hword  11763,  12010,  15858,      0,      0,      0,      0,      0

/*
 * Benchmark-only Slothy input for InvNTT rminus1 row1 stage45 stripe-pair
 * windows.  This file is generated from INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH
 * in asm/slothy/invntt_opt.production.s by
 * window_inputs/materialize_invntt_rminus1_row1_stage45_stripes.py.
 *
 * It is not included by production wrappers and must not replace
 * poly_invntt_from_rminus1.  The production row-level macro is already
 * cross-stripe scheduled, so this file materializes exact canonical
 * per-stripe windows for Slothy input labels without using the 337-instruction
 * parent row labels as a substitute.
 *
 * Region contract for each stripe-pair:
 *   live-in:  x14 = stage123 stripe scratch base
 *             x2  = row1 row-buffer output base
 *             x3  = invntt32_stage45_consts base
 *             v0  = q / Barrett constants
 *   live-out: memory side effects only, row-buffer q-stores at [x2,#offset]
 *   pointer mutation: none
 */

.text
.align 2
.global invntt_rminus1_row1_stage45_stripes_marked_slothy_input
.type invntt_rminus1_row1_stage45_stripes_marked_slothy_input, %function
invntt_rminus1_row1_stage45_stripes_marked_slothy_input:

slothy_start_invntt_rm1_row1_stage45_stripes0_1:
    /* stripe 0 */
    ldr q11, [x14, #48]
    ldr q7, [x3, #16]
    ldr q30, [x14, #32]
    ldr q5, [x3, #0]
    ldr q26, [x14, #16]
    ldr q17, [x14, #0]
    sqrdmulh v29.8h, v11.8h, v7.h[0]
    mul v23.8h, v11.8h, v5.h[0]
    mls v23.8h, v29.8h, v0.h[0]
    sqrdmulh v20.8h, v26.8h, v7.h[0]
    mul v10.8h, v26.8h, v5.h[0]
    add v19.8h, v30.8h, v23.8h
    sub v21.8h, v30.8h, v23.8h
    mls v10.8h, v20.8h, v0.h[0]
    sqrdmulh v6.8h, v19.8h, v7.h[1]
    sqrdmulh v22.8h, v21.8h, v7.h[2]
    mul v25.8h, v19.8h, v5.h[1]
    mls v25.8h, v6.8h, v0.h[0]
    add v9.8h, v17.8h, v10.8h
    mul v14.8h, v21.8h, v5.h[2]
    sub v7.8h, v17.8h, v10.8h
    mls v14.8h, v22.8h, v0.h[0]
    sub v29.8h, v9.8h, v25.8h
    add v17.8h, v9.8h, v25.8h
    sqdmulh v8.8h, v29.8h, v0.h[1]
    sub v23.8h, v7.8h, v14.8h
    sqdmulh v22.8h, v17.8h, v0.h[1]
    add v10.8h, v7.8h, v14.8h
    sqdmulh v3.8h, v23.8h, v0.h[1]
    srshr v13.8h, v8.8h, #11
    sqdmulh v28.8h, v10.8h, v0.h[1]
    srshr v9.8h, v22.8h, #11
    mls v29.8h, v13.8h, v0.h[0]
    srshr v18.8h, v3.8h, #11
    mls v17.8h, v9.8h, v0.h[0]
    srshr v27.8h, v28.8h, #11
    mls v23.8h, v18.8h, v0.h[0]
    mls v10.8h, v27.8h, v0.h[0]
    str q17, [x2, #0]
    str q23, [x2, #384]
    str q29, [x2, #256]
    str q10, [x2, #128]
    /* stripe 1 */
    ldr q11, [x14, #112]
    ldr q7, [x3, #48]
    ldr q30, [x14, #96]
    ldr q5, [x3, #32]
    ldr q26, [x14, #80]
    ldr q17, [x14, #64]
    sqrdmulh v29.8h, v11.8h, v7.h[0]
    mul v23.8h, v11.8h, v5.h[0]
    mls v23.8h, v29.8h, v0.h[0]
    sqrdmulh v20.8h, v26.8h, v7.h[0]
    mul v10.8h, v26.8h, v5.h[0]
    add v19.8h, v30.8h, v23.8h
    sub v21.8h, v30.8h, v23.8h
    mls v10.8h, v20.8h, v0.h[0]
    sqrdmulh v6.8h, v19.8h, v7.h[1]
    sqrdmulh v22.8h, v21.8h, v7.h[2]
    mul v25.8h, v19.8h, v5.h[1]
    mls v25.8h, v6.8h, v0.h[0]
    add v9.8h, v17.8h, v10.8h
    mul v14.8h, v21.8h, v5.h[2]
    sub v7.8h, v17.8h, v10.8h
    mls v14.8h, v22.8h, v0.h[0]
    sub v29.8h, v9.8h, v25.8h
    add v17.8h, v9.8h, v25.8h
    sqdmulh v8.8h, v29.8h, v0.h[1]
    sub v23.8h, v7.8h, v14.8h
    sqdmulh v22.8h, v17.8h, v0.h[1]
    add v10.8h, v7.8h, v14.8h
    sqdmulh v3.8h, v23.8h, v0.h[1]
    srshr v13.8h, v8.8h, #11
    sqdmulh v28.8h, v10.8h, v0.h[1]
    srshr v9.8h, v22.8h, #11
    mls v29.8h, v13.8h, v0.h[0]
    srshr v18.8h, v3.8h, #11
    mls v17.8h, v9.8h, v0.h[0]
    srshr v27.8h, v28.8h, #11
    mls v23.8h, v18.8h, v0.h[0]
    mls v10.8h, v27.8h, v0.h[0]
    str q17, [x2, #16]
    str q23, [x2, #400]
    str q29, [x2, #272]
    str q10, [x2, #144]
slothy_end_invntt_rm1_row1_stage45_stripes0_1:

slothy_start_invntt_rm1_row1_stage45_stripes2_3:
    /* stripe 2 */
    ldr q11, [x14, #176]
    ldr q7, [x3, #80]
    ldr q30, [x14, #160]
    ldr q5, [x3, #64]
    ldr q26, [x14, #144]
    ldr q17, [x14, #128]
    sqrdmulh v29.8h, v11.8h, v7.h[0]
    mul v23.8h, v11.8h, v5.h[0]
    mls v23.8h, v29.8h, v0.h[0]
    sqrdmulh v20.8h, v26.8h, v7.h[0]
    mul v10.8h, v26.8h, v5.h[0]
    add v19.8h, v30.8h, v23.8h
    sub v21.8h, v30.8h, v23.8h
    mls v10.8h, v20.8h, v0.h[0]
    sqrdmulh v6.8h, v19.8h, v7.h[1]
    sqrdmulh v22.8h, v21.8h, v7.h[2]
    mul v25.8h, v19.8h, v5.h[1]
    mls v25.8h, v6.8h, v0.h[0]
    add v9.8h, v17.8h, v10.8h
    mul v14.8h, v21.8h, v5.h[2]
    sub v7.8h, v17.8h, v10.8h
    mls v14.8h, v22.8h, v0.h[0]
    sub v29.8h, v9.8h, v25.8h
    add v17.8h, v9.8h, v25.8h
    sqdmulh v8.8h, v29.8h, v0.h[1]
    sub v23.8h, v7.8h, v14.8h
    sqdmulh v22.8h, v17.8h, v0.h[1]
    add v10.8h, v7.8h, v14.8h
    sqdmulh v3.8h, v23.8h, v0.h[1]
    srshr v13.8h, v8.8h, #11
    sqdmulh v28.8h, v10.8h, v0.h[1]
    srshr v9.8h, v22.8h, #11
    mls v29.8h, v13.8h, v0.h[0]
    srshr v18.8h, v3.8h, #11
    mls v17.8h, v9.8h, v0.h[0]
    srshr v27.8h, v28.8h, #11
    mls v23.8h, v18.8h, v0.h[0]
    mls v10.8h, v27.8h, v0.h[0]
    str q17, [x2, #32]
    str q23, [x2, #416]
    str q29, [x2, #288]
    str q10, [x2, #160]
    /* stripe 3 */
    ldr q11, [x14, #240]
    ldr q7, [x3, #112]
    ldr q30, [x14, #224]
    ldr q5, [x3, #96]
    ldr q26, [x14, #208]
    ldr q17, [x14, #192]
    sqrdmulh v29.8h, v11.8h, v7.h[0]
    mul v23.8h, v11.8h, v5.h[0]
    mls v23.8h, v29.8h, v0.h[0]
    sqrdmulh v20.8h, v26.8h, v7.h[0]
    mul v10.8h, v26.8h, v5.h[0]
    add v19.8h, v30.8h, v23.8h
    sub v21.8h, v30.8h, v23.8h
    mls v10.8h, v20.8h, v0.h[0]
    sqrdmulh v6.8h, v19.8h, v7.h[1]
    sqrdmulh v22.8h, v21.8h, v7.h[2]
    mul v25.8h, v19.8h, v5.h[1]
    mls v25.8h, v6.8h, v0.h[0]
    add v9.8h, v17.8h, v10.8h
    mul v14.8h, v21.8h, v5.h[2]
    sub v7.8h, v17.8h, v10.8h
    mls v14.8h, v22.8h, v0.h[0]
    sub v29.8h, v9.8h, v25.8h
    add v17.8h, v9.8h, v25.8h
    sqdmulh v8.8h, v29.8h, v0.h[1]
    sub v23.8h, v7.8h, v14.8h
    sqdmulh v22.8h, v17.8h, v0.h[1]
    add v10.8h, v7.8h, v14.8h
    sqdmulh v3.8h, v23.8h, v0.h[1]
    srshr v13.8h, v8.8h, #11
    sqdmulh v28.8h, v10.8h, v0.h[1]
    srshr v9.8h, v22.8h, #11
    mls v29.8h, v13.8h, v0.h[0]
    srshr v18.8h, v3.8h, #11
    mls v17.8h, v9.8h, v0.h[0]
    srshr v27.8h, v28.8h, #11
    mls v23.8h, v18.8h, v0.h[0]
    mls v10.8h, v27.8h, v0.h[0]
    str q17, [x2, #48]
    str q23, [x2, #432]
    str q29, [x2, #304]
    str q10, [x2, #176]
slothy_end_invntt_rm1_row1_stage45_stripes2_3:

slothy_start_invntt_rm1_row1_stage45_stripes4_5:
    /* stripe 4 */
    ldr q11, [x14, #304]
    ldr q7, [x3, #144]
    ldr q30, [x14, #288]
    ldr q5, [x3, #128]
    ldr q26, [x14, #272]
    ldr q17, [x14, #256]
    sqrdmulh v29.8h, v11.8h, v7.h[0]
    mul v23.8h, v11.8h, v5.h[0]
    mls v23.8h, v29.8h, v0.h[0]
    sqrdmulh v20.8h, v26.8h, v7.h[0]
    mul v10.8h, v26.8h, v5.h[0]
    add v19.8h, v30.8h, v23.8h
    sub v21.8h, v30.8h, v23.8h
    mls v10.8h, v20.8h, v0.h[0]
    sqrdmulh v6.8h, v19.8h, v7.h[1]
    sqrdmulh v22.8h, v21.8h, v7.h[2]
    mul v25.8h, v19.8h, v5.h[1]
    mls v25.8h, v6.8h, v0.h[0]
    add v9.8h, v17.8h, v10.8h
    mul v14.8h, v21.8h, v5.h[2]
    sub v7.8h, v17.8h, v10.8h
    mls v14.8h, v22.8h, v0.h[0]
    sub v29.8h, v9.8h, v25.8h
    add v17.8h, v9.8h, v25.8h
    sqdmulh v8.8h, v29.8h, v0.h[1]
    sub v23.8h, v7.8h, v14.8h
    sqdmulh v22.8h, v17.8h, v0.h[1]
    add v10.8h, v7.8h, v14.8h
    sqdmulh v3.8h, v23.8h, v0.h[1]
    srshr v13.8h, v8.8h, #11
    sqdmulh v28.8h, v10.8h, v0.h[1]
    srshr v9.8h, v22.8h, #11
    mls v29.8h, v13.8h, v0.h[0]
    srshr v18.8h, v3.8h, #11
    mls v17.8h, v9.8h, v0.h[0]
    srshr v27.8h, v28.8h, #11
    mls v23.8h, v18.8h, v0.h[0]
    mls v10.8h, v27.8h, v0.h[0]
    str q17, [x2, #64]
    str q23, [x2, #448]
    str q29, [x2, #320]
    str q10, [x2, #192]
    /* stripe 5 */
    ldr q11, [x14, #368]
    ldr q7, [x3, #176]
    ldr q30, [x14, #352]
    ldr q5, [x3, #160]
    ldr q26, [x14, #336]
    ldr q17, [x14, #320]
    sqrdmulh v29.8h, v11.8h, v7.h[0]
    mul v23.8h, v11.8h, v5.h[0]
    mls v23.8h, v29.8h, v0.h[0]
    sqrdmulh v20.8h, v26.8h, v7.h[0]
    mul v10.8h, v26.8h, v5.h[0]
    add v19.8h, v30.8h, v23.8h
    sub v21.8h, v30.8h, v23.8h
    mls v10.8h, v20.8h, v0.h[0]
    sqrdmulh v6.8h, v19.8h, v7.h[1]
    sqrdmulh v22.8h, v21.8h, v7.h[2]
    mul v25.8h, v19.8h, v5.h[1]
    mls v25.8h, v6.8h, v0.h[0]
    add v9.8h, v17.8h, v10.8h
    mul v14.8h, v21.8h, v5.h[2]
    sub v7.8h, v17.8h, v10.8h
    mls v14.8h, v22.8h, v0.h[0]
    sub v29.8h, v9.8h, v25.8h
    add v17.8h, v9.8h, v25.8h
    sqdmulh v8.8h, v29.8h, v0.h[1]
    sub v23.8h, v7.8h, v14.8h
    sqdmulh v22.8h, v17.8h, v0.h[1]
    add v10.8h, v7.8h, v14.8h
    sqdmulh v3.8h, v23.8h, v0.h[1]
    srshr v13.8h, v8.8h, #11
    sqdmulh v28.8h, v10.8h, v0.h[1]
    srshr v9.8h, v22.8h, #11
    mls v29.8h, v13.8h, v0.h[0]
    srshr v18.8h, v3.8h, #11
    mls v17.8h, v9.8h, v0.h[0]
    srshr v27.8h, v28.8h, #11
    mls v23.8h, v18.8h, v0.h[0]
    mls v10.8h, v27.8h, v0.h[0]
    str q17, [x2, #80]
    str q23, [x2, #464]
    str q29, [x2, #336]
    str q10, [x2, #208]
slothy_end_invntt_rm1_row1_stage45_stripes4_5:

slothy_start_invntt_rm1_row1_stage45_stripes6_7:
    /* stripe 6 */
    ldr q11, [x14, #432]
    ldr q7, [x3, #208]
    ldr q30, [x14, #416]
    ldr q5, [x3, #192]
    ldr q26, [x14, #400]
    ldr q17, [x14, #384]
    sqrdmulh v29.8h, v11.8h, v7.h[0]
    mul v23.8h, v11.8h, v5.h[0]
    mls v23.8h, v29.8h, v0.h[0]
    sqrdmulh v20.8h, v26.8h, v7.h[0]
    mul v10.8h, v26.8h, v5.h[0]
    add v19.8h, v30.8h, v23.8h
    sub v21.8h, v30.8h, v23.8h
    mls v10.8h, v20.8h, v0.h[0]
    sqrdmulh v6.8h, v19.8h, v7.h[1]
    sqrdmulh v22.8h, v21.8h, v7.h[2]
    mul v25.8h, v19.8h, v5.h[1]
    mls v25.8h, v6.8h, v0.h[0]
    add v9.8h, v17.8h, v10.8h
    mul v14.8h, v21.8h, v5.h[2]
    sub v7.8h, v17.8h, v10.8h
    mls v14.8h, v22.8h, v0.h[0]
    sub v29.8h, v9.8h, v25.8h
    add v17.8h, v9.8h, v25.8h
    sqdmulh v8.8h, v29.8h, v0.h[1]
    sub v23.8h, v7.8h, v14.8h
    sqdmulh v22.8h, v17.8h, v0.h[1]
    add v10.8h, v7.8h, v14.8h
    sqdmulh v3.8h, v23.8h, v0.h[1]
    srshr v13.8h, v8.8h, #11
    sqdmulh v28.8h, v10.8h, v0.h[1]
    srshr v9.8h, v22.8h, #11
    mls v29.8h, v13.8h, v0.h[0]
    srshr v18.8h, v3.8h, #11
    mls v17.8h, v9.8h, v0.h[0]
    srshr v27.8h, v28.8h, #11
    mls v23.8h, v18.8h, v0.h[0]
    mls v10.8h, v27.8h, v0.h[0]
    str q17, [x2, #96]
    str q23, [x2, #480]
    str q29, [x2, #352]
    str q10, [x2, #224]
    /* stripe 7 */
    ldr q11, [x14, #496]
    ldr q7, [x3, #240]
    ldr q30, [x14, #480]
    ldr q5, [x3, #224]
    ldr q26, [x14, #464]
    ldr q17, [x14, #448]
    sqrdmulh v29.8h, v11.8h, v7.h[0]
    mul v23.8h, v11.8h, v5.h[0]
    mls v23.8h, v29.8h, v0.h[0]
    sqrdmulh v20.8h, v26.8h, v7.h[0]
    mul v10.8h, v26.8h, v5.h[0]
    add v19.8h, v30.8h, v23.8h
    sub v21.8h, v30.8h, v23.8h
    mls v10.8h, v20.8h, v0.h[0]
    sqrdmulh v6.8h, v19.8h, v7.h[1]
    sqrdmulh v22.8h, v21.8h, v7.h[2]
    mul v25.8h, v19.8h, v5.h[1]
    mls v25.8h, v6.8h, v0.h[0]
    add v9.8h, v17.8h, v10.8h
    mul v14.8h, v21.8h, v5.h[2]
    sub v7.8h, v17.8h, v10.8h
    mls v14.8h, v22.8h, v0.h[0]
    sub v29.8h, v9.8h, v25.8h
    add v17.8h, v9.8h, v25.8h
    sqdmulh v8.8h, v29.8h, v0.h[1]
    sub v23.8h, v7.8h, v14.8h
    sqdmulh v22.8h, v17.8h, v0.h[1]
    add v10.8h, v7.8h, v14.8h
    sqdmulh v3.8h, v23.8h, v0.h[1]
    srshr v13.8h, v8.8h, #11
    sqdmulh v28.8h, v10.8h, v0.h[1]
    srshr v9.8h, v22.8h, #11
    mls v29.8h, v13.8h, v0.h[0]
    srshr v18.8h, v3.8h, #11
    mls v17.8h, v9.8h, v0.h[0]
    srshr v27.8h, v28.8h, #11
    mls v23.8h, v18.8h, v0.h[0]
    mls v10.8h, v27.8h, v0.h[0]
    str q17, [x2, #112]
    str q23, [x2, #496]
    str q29, [x2, #368]
    str q10, [x2, #240]
slothy_end_invntt_rm1_row1_stage45_stripes6_7:

    ret
.size invntt_rminus1_row1_stage45_stripes_marked_slothy_input, .-invntt_rminus1_row1_stage45_stripes_marked_slothy_input

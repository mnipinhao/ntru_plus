/*
 * Archive of inverse-NTT rowstage45/post prototype and bench fragments.
 *
 * Extracted from asm/slothy/invntt_opt.s on 2026-06-25 when production
 * wrappers were moved to asm/slothy/invntt_opt.production.s.
 *
 * This file is not included by production builds.  It preserves experiment
 * fragments so the production file can stay readable.  The legacy superset
 * asm/slothy/invntt_opt.s still remains as historical context for old wrappers.
 */

/* ---- original asm/slothy/invntt_opt.s:659-705: fastscale final-store prototype ---- */
.macro POST_STORE_PTR_FASTSCALE xvec, ptr, off_lo, off_hi
    /*
     * Experimental exactness probe:
     *
     * old:
     *   t2       = fqmul(ZMINUSZ5INV, diff)
     *   out_low  = fqmul(1/192, sum - t2)
     *   out_high = fqmul(1/96,  t2)
     *
     * new:
     *   t        = fqmul(ZMINUSZ5INV/192, diff)
     *   s        = fqmul(1/192, sum)
     *   out_low  = s - t
     *   out_high = 2*t
     *
     * This saves one fqmul per output vector but changes reduction order, so
     * exact representative tests decide whether it is usable.
     */
    ldr     q10, [x3], #16
    ldr     q11, [x3], #16
    sqrdmulh v12.8h, \xvec\().8h, v11.8h
    mul      v13.8h, \xvec\().8h, v10.8h
    mls      v13.8h, v12.8h, v0.h[0]

    ext      v14.16b, v13.16b, v13.16b, #8
    add      v24.8h, v13.8h, v14.8h
    sub      v16.8h, v13.8h, v14.8h

    sqrdmulh v17.8h, v16.8h, v15.h[3]
    mul      v18.8h, v16.8h, v15.h[2]
    mls      v18.8h, v17.8h, v0.h[0]

    sqrdmulh v20.8h, v24.8h, v0.h[7]
    mul      v21.8h, v24.8h, v0.h[6]
    mls      v21.8h, v20.8h, v0.h[0]

    sub      v21.8h, v21.8h, v18.8h
    add      v23.8h, v18.8h, v18.8h

.ifdef INVNTT_POST_FASTSCALE_REDUCE_OUTPUTS
    BARRETT_REDUCE v21, v20
    BARRETT_REDUCE v23, v20
.endif

    str      d21, [\ptr, #\off_lo]
    str      d23, [\ptr, #\off_hi]
.endm

/* ---- original asm/slothy/invntt_opt.s:828-1203: post Slothy prototype helpers that are not active production ---- */
.macro FUSED_POST_STRIPE_SLOTHY ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    /*
     * A72 Slothy schedule for one production-equivalent fused post-row stripe.
     * Source: asm/slothy/invntt_post_fused_dstore_clean.slothy.s, generated as
     * asm/slothy/invntt_post_fused_dstore.opt.s with allow_spills=false.
     *
     * The Slothy clean source uses q stores as live-out placeholders because
     * this checkout's target model does not parse non-stack d stores.  The
     * integrated path below keeps production's final d stores exactly.
     */
    ldr q7, [x9], #16
    ldr q20, [x10], #16
    ldr q17, [x8], #16
    ldr q30, [x3], #16
    ldr q11, [x3], #16
    ldr q6, [x3], #16
    ldr q29, [x3], #16
    ldr q3, [x3], #16
    sub v13.8h, v20.8h, v7.8h
    ldr q2, [x3], #16
    add v28.8h, v17.8h, v7.8h
    sub v5.8h, v17.8h, v7.8h
    sub v18.8h, v17.8h, v20.8h
    sqrdmulh v24.8h, v13.8h, v0.h[3]
    add v9.8h, v28.8h, v20.8h
    mul v21.8h, v13.8h, v0.h[2]
    sqdmulh v1.8h, v9.8h, v0.h[1]
    mls v21.8h, v24.8h, v0.h[0]
    srshr v13.8h, v1.8h, #11
    add v20.8h, v5.8h, v21.8h
    sub v21.8h, v18.8h, v21.8h
    mls v9.8h, v13.8h, v0.h[0]
    sqdmulh v13.8h, v20.8h, v0.h[1]
    sqdmulh v1.8h, v21.8h, v0.h[1]
    mul v17.8h, v9.8h, v30.8h
    srshr v8.8h, v13.8h, #11
    sqrdmulh v10.8h, v9.8h, v11.8h
    srshr v23.8h, v1.8h, #11
    mls v20.8h, v8.8h, v0.h[0]
    mls v21.8h, v23.8h, v0.h[0]
    mls v17.8h, v10.8h, v0.h[0]
    sqrdmulh v5.8h, v20.8h, v29.8h
    mul v27.8h, v20.8h, v6.8h
    ext v9.16b, v17.16b, v17.16b, #8
    mul v16.8h, v21.8h, v3.8h
    mls v27.8h, v5.8h, v0.h[0]
    sub v26.8h, v17.8h, v9.8h
    add v13.8h, v17.8h, v9.8h
    sqrdmulh v9.8h, v21.8h, v2.8h
    sqrdmulh v5.8h, v26.8h, v0.h[5]
    ext v11.16b, v27.16b, v27.16b, #8
    mul v20.8h, v26.8h, v0.h[4]
    mls v16.8h, v9.8h, v0.h[0]
    sub v28.8h, v27.8h, v11.8h
    add v23.8h, v27.8h, v11.8h
    mls v20.8h, v5.8h, v0.h[0]
    mul v11.8h, v28.8h, v0.h[4]
    ext v5.16b, v16.16b, v16.16b, #8
    sqrdmulh v29.8h, v28.8h, v0.h[5]
    sub v27.8h, v13.8h, v20.8h
    sub v8.8h, v16.8h, v5.8h
    sqrdmulh v30.8h, v20.8h, v15.h[1]
    add v14.8h, v16.8h, v5.8h
    sqrdmulh v18.8h, v27.8h, v0.h[7]
    sqrdmulh v25.8h, v8.8h, v0.h[5]
    mul v5.8h, v8.8h, v0.h[4]
    mls v11.8h, v29.8h, v0.h[0]
    mls v5.8h, v25.8h, v0.h[0]
    mul v20.8h, v20.8h, v15.h[0]
    sub v16.8h, v23.8h, v11.8h
    sqrdmulh v1.8h, v11.8h, v15.h[1]
    sub v4.8h, v14.8h, v5.8h
    sqrdmulh v22.8h, v16.8h, v0.h[7]
    sqrdmulh v19.8h, v4.8h, v0.h[7]
    sqrdmulh v3.8h, v5.8h, v15.h[1]
    mul v21.8h, v27.8h, v0.h[6]
    mul v29.8h, v11.8h, v15.h[0]
    mul v11.8h, v16.8h, v0.h[6]
    mul v16.8h, v4.8h, v0.h[6]
    mul v17.8h, v5.8h, v15.h[0]
    mls v16.8h, v19.8h, v0.h[0]
    mls v21.8h, v18.8h, v0.h[0]
    mls v20.8h, v30.8h, v0.h[0]
    str d16, [\ptr2, #\off2_lo]
    mls v17.8h, v3.8h, v0.h[0]
    str d21, [\ptr0, #\off0_lo]
    mls v29.8h, v1.8h, v0.h[0]
    str d20, [\ptr0, #\off0_hi]
    mls v11.8h, v22.8h, v0.h[0]
    str d17, [\ptr2, #\off2_hi]
    str d29, [\ptr1, #\off1_hi]
    str d11, [\ptr1, #\off1_lo]
.endm

.macro FUSED_POST_STRIPE_N1_SLOTHY ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    /*
     * Neoverse-N1 Slothy schedule used as a Cortex-A76-adjacent experiment
     * for Raspberry Pi 5.  The generated stream is embedded here directly;
     * the Slothy q-store live-out placeholders are converted back to the
     * production d stores below.
     */
    ldr q3, [x9], #16
    ldr q6, [x10], #16
    ldr q17, [x8], #16
    ldr q1, [x3], #16
    ldr q23, [x3], #16
    ldr q11, [x3], #16
    ldr q10, [x3], #16
    ldr q20, [x3], #16
    sub v29.8h, v6.8h, v3.8h
    ldr q28, [x3], #16
    add v27.8h, v17.8h, v3.8h
    sub v24.8h, v17.8h, v3.8h
    sub v14.8h, v17.8h, v6.8h
    add v8.8h, v27.8h, v6.8h
    sqrdmulh v13.8h, v29.8h, v0.h[3]
    sqdmulh v21.8h, v8.8h, v0.h[1]
    mul v17.8h, v29.8h, v0.h[2]
    mls v17.8h, v13.8h, v0.h[0]
    srshr v25.8h, v21.8h, #11
    add v21.8h, v24.8h, v17.8h
    mls v8.8h, v25.8h, v0.h[0]
    sub v13.8h, v14.8h, v17.8h
    sqdmulh v24.8h, v21.8h, v0.h[1]
    sqdmulh v26.8h, v13.8h, v0.h[1]
    mul v17.8h, v8.8h, v1.8h
    srshr v18.8h, v24.8h, #11
    sqrdmulh v24.8h, v8.8h, v23.8h
    srshr v19.8h, v26.8h, #11
    mls v21.8h, v18.8h, v0.h[0]
    mls v13.8h, v19.8h, v0.h[0]
    mls v17.8h, v24.8h, v0.h[0]
    mul v6.8h, v21.8h, v11.8h
    sqrdmulh v8.8h, v21.8h, v10.8h
    ext v16.16b, v17.16b, v17.16b, #8
    mul v21.8h, v13.8h, v20.8h
    sub v3.8h, v17.8h, v16.8h
    sqrdmulh v24.8h, v13.8h, v28.8h
    add v4.8h, v17.8h, v16.8h
    mls v6.8h, v8.8h, v0.h[0]
    sqrdmulh v28.8h, v3.8h, v0.h[5]
    mul v8.8h, v3.8h, v0.h[4]
    ext v17.16b, v6.16b, v6.16b, #8
    mls v21.8h, v24.8h, v0.h[0]
    sub v11.8h, v6.8h, v17.8h
    add v5.8h, v6.8h, v17.8h
    mls v8.8h, v28.8h, v0.h[0]
    sqrdmulh v10.8h, v11.8h, v0.h[5]
    ext v13.16b, v21.16b, v21.16b, #8
    mul v9.8h, v11.8h, v0.h[4]
    sub v28.8h, v21.8h, v13.8h
    add v14.8h, v21.8h, v13.8h
    sqrdmulh v20.8h, v8.8h, v15.h[1]
    sub v12.8h, v4.8h, v8.8h
    sqrdmulh v1.8h, v28.8h, v0.h[5]
    mul v3.8h, v28.8h, v0.h[4]
    mls v9.8h, v10.8h, v0.h[0]
    mls v3.8h, v1.8h, v0.h[0]
    sqrdmulh v6.8h, v12.8h, v0.h[7]
    sub v19.8h, v5.8h, v9.8h
    sqrdmulh v27.8h, v9.8h, v15.h[1]
    sub v17.8h, v14.8h, v3.8h
    sqrdmulh v23.8h, v3.8h, v15.h[1]
    sqrdmulh v28.8h, v19.8h, v0.h[7]
    sqrdmulh v29.8h, v17.8h, v0.h[7]
    mul v21.8h, v12.8h, v0.h[6]
    mul v24.8h, v3.8h, v15.h[0]
    mul v25.8h, v19.8h, v0.h[6]
    mul v3.8h, v8.8h, v15.h[0]
    mul v17.8h, v17.8h, v0.h[6]
    mul v14.8h, v9.8h, v15.h[0]
    mls v3.8h, v20.8h, v0.h[0]
    mls v17.8h, v29.8h, v0.h[0]
    mls v25.8h, v28.8h, v0.h[0]
    str d3, [\ptr0, #\off0_hi]
    mls v14.8h, v27.8h, v0.h[0]
    str d17, [\ptr2, #\off2_lo]
    mls v21.8h, v6.8h, v0.h[0]
    str d25, [\ptr1, #\off1_lo]
    mls v24.8h, v23.8h, v0.h[0]
    str d14, [\ptr1, #\off1_hi]
    str d21, [\ptr0, #\off0_lo]
    str d24, [\ptr2, #\off2_hi]
.endm

.macro FUSED_POST_STRIPE_N1_NODFTREDUCE_SLOTHY ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    /*
     * Neoverse-N1 Slothy schedule with the three post-DFT3 Barrett reductions
     * removed.  The generated stream is embedded here directly; final q-store
     * placeholders are converted back to production d stores.
     */
    ldr q9, [x9], #16
    ldr q3, [x10], #16
    ldr q12, [x3], #16
    ldr q28, [x8], #16
    ldr q16, [x3], #16
    ldr q30, [x3], #16
    ldr q18, [x3], #16
    ldr q27, [x3], #16
    ldr q13, [x3], #16
    sub v24.8h, v3.8h, v9.8h
    add v1.8h, v28.8h, v9.8h
    sub v20.8h, v28.8h, v3.8h
    sub v4.8h, v28.8h, v9.8h
    sqrdmulh v11.8h, v24.8h, v0.h[3]
    add v19.8h, v1.8h, v3.8h
    mul v24.8h, v24.8h, v0.h[2]
    sqrdmulh v28.8h, v19.8h, v16.8h
    mls v24.8h, v11.8h, v0.h[0]
    mul v12.8h, v19.8h, v12.8h
    mls v12.8h, v28.8h, v0.h[0]
    add v21.8h, v4.8h, v24.8h
    mul v3.8h, v21.8h, v30.8h
    sqrdmulh v28.8h, v21.8h, v18.8h
    sub v23.8h, v20.8h, v24.8h
    ext v19.16b, v12.16b, v12.16b, #8
    mul v9.8h, v23.8h, v27.8h
    add v29.8h, v12.8h, v19.8h
    sub v21.8h, v12.8h, v19.8h
    sqrdmulh v12.8h, v23.8h, v13.8h
    mls v3.8h, v28.8h, v0.h[0]
    sqrdmulh v5.8h, v21.8h, v0.h[5]
    mls v9.8h, v12.8h, v0.h[0]
    ext v12.16b, v3.16b, v3.16b, #8
    mul v24.8h, v21.8h, v0.h[4]
    sub v8.8h, v3.8h, v12.8h
    add v10.8h, v3.8h, v12.8h
    mls v24.8h, v5.8h, v0.h[0]
    ext v26.16b, v9.16b, v9.16b, #8
    sqrdmulh v27.8h, v8.8h, v0.h[5]
    sub v3.8h, v9.8h, v26.8h
    add v13.8h, v9.8h, v26.8h
    mul v23.8h, v8.8h, v0.h[4]
    sqrdmulh v8.8h, v3.8h, v0.h[5]
    mul v12.8h, v3.8h, v0.h[4]
    sub v2.8h, v29.8h, v24.8h
    mls v23.8h, v27.8h, v0.h[0]
    mls v12.8h, v8.8h, v0.h[0]
    sqrdmulh v14.8h, v2.8h, v0.h[7]
    sub v5.8h, v10.8h, v23.8h
    sqrdmulh v9.8h, v24.8h, v15.h[1]
    sub v13.8h, v13.8h, v12.8h
    sqrdmulh v16.8h, v23.8h, v15.h[1]
    sqrdmulh v6.8h, v5.8h, v0.h[7]
    sqrdmulh v20.8h, v13.8h, v0.h[7]
    sqrdmulh v1.8h, v12.8h, v15.h[1]
    mul v11.8h, v2.8h, v0.h[6]
    mul v3.8h, v13.8h, v0.h[6]
    mul v12.8h, v12.8h, v15.h[0]
    mul v13.8h, v23.8h, v15.h[0]
    mul v24.8h, v24.8h, v15.h[0]
    mul v19.8h, v5.8h, v0.h[6]
    mls v3.8h, v20.8h, v0.h[0]
    mls v12.8h, v1.8h, v0.h[0]
    mls v19.8h, v6.8h, v0.h[0]
    mls v24.8h, v9.8h, v0.h[0]
    mls v13.8h, v16.8h, v0.h[0]
    str d3, [\ptr2, #\off2_lo]
    mls v11.8h, v14.8h, v0.h[0]
    str d12, [\ptr2, #\off2_hi]
    str d24, [\ptr0, #\off0_hi]
    str d19, [\ptr1, #\off1_lo]
    str d13, [\ptr1, #\off1_hi]
    str d11, [\ptr0, #\off0_lo]
.endm

.macro FUSED_POST_STRIPE_BRANCHFOLD_A72_SLOTHY ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    /*
     * Cortex-A72 Slothy schedule for one promoted branchfold-reduce stripe.
     * Source of truth:
     * asm/slothy/invntt_post_branchfold_reduce_clean.slothy.s, generated as
     * asm/slothy/invntt_post_branchfold_reduce_a72.opt.s with
     * allow_spills=false.  The clean q-store placeholders are converted back
     * to production d stores below.
     */
    ldr q20, [x9], #16
    ldr q21, [x10], #16
    ldr q18, [x8], #16
    ldr q26, [x3], #16
    ldr q22, [x3], #16
    ldr q6, [x3], #16
    ldr q30, [x3], #16
    ldr q7, [x3], #16
    ldr q15, [x3], #16
    sub v3.8h, v21.8h, v20.8h
    ldr q23, [x3], #16
    add v1.8h, v18.8h, v20.8h
    sub v28.8h, v18.8h, v20.8h
    ldr q10, [x3], #16
    sub v18.8h, v18.8h, v21.8h
    ldr q8, [x3], #16
    ldr q11, [x3], #16
    ldr q4, [x3], #16
    sqrdmulh v24.8h, v3.8h, v0.h[3]
    ldr q9, [x3], #16
    add v2.8h, v1.8h, v21.8h
    mul v12.8h, v3.8h, v0.h[2]
    mul v26.8h, v2.8h, v26.8h
    sqrdmulh v19.8h, v2.8h, v22.8h
    mls v12.8h, v24.8h, v0.h[0]
    mul v3.8h, v2.8h, v6.8h
    sqrdmulh v13.8h, v2.8h, v30.8h
    add v24.8h, v28.8h, v12.8h
    sub v22.8h, v18.8h, v12.8h
    mls v26.8h, v19.8h, v0.h[0]
    mul v18.8h, v24.8h, v7.8h
    sqrdmulh v7.8h, v24.8h, v15.8h
    ext v30.16b, v26.16b, v26.16b, #8
    mul v19.8h, v24.8h, v23.8h
    sqrdmulh v17.8h, v24.8h, v10.8h
    add v21.8h, v26.8h, v30.8h
    mul v26.8h, v22.8h, v8.8h
    sqrdmulh v14.8h, v22.8h, v11.8h
    mul v30.8h, v22.8h, v4.8h
    sqrdmulh v9.8h, v22.8h, v9.8h
    mls v3.8h, v13.8h, v0.h[0]
    mls v18.8h, v7.8h, v0.h[0]
    mls v19.8h, v17.8h, v0.h[0]
    ext v28.16b, v3.16b, v3.16b, #8
    mls v26.8h, v14.8h, v0.h[0]
    ext v1.16b, v18.16b, v18.16b, #8
    add v16.8h, v3.8h, v28.8h
    sqdmulh v8.8h, v21.8h, v0.h[1]
    ext v7.16b, v19.16b, v19.16b, #8
    mls v30.8h, v9.8h, v0.h[0]
    add v18.8h, v18.8h, v1.8h
    ext v20.16b, v26.16b, v26.16b, #8
    add v11.8h, v19.8h, v7.8h
    sqdmulh v17.8h, v16.8h, v0.h[1]
    srshr v1.8h, v8.8h, #11
    add v26.8h, v26.8h, v20.8h
    sqdmulh v7.8h, v18.8h, v0.h[1]
    ext v10.16b, v30.16b, v30.16b, #8
    sqdmulh v22.8h, v11.8h, v0.h[1]
    srshr v9.8h, v17.8h, #11
    add v3.8h, v30.8h, v10.8h
    sqdmulh v12.8h, v26.8h, v0.h[1]
    srshr v25.8h, v7.8h, #11
    mls v16.8h, v9.8h, v0.h[0]
    srshr v20.8h, v22.8h, #11
    sqdmulh v13.8h, v3.8h, v0.h[1]
    srshr v10.8h, v12.8h, #11
    mls v11.8h, v20.8h, v0.h[0]
    str d16, [\ptr0, #\off0_hi]
    mls v18.8h, v25.8h, v0.h[0]
    srshr v2.8h, v13.8h, #11
    mls v26.8h, v10.8h, v0.h[0]
    str d11, [\ptr1, #\off1_hi]
    mls v3.8h, v2.8h, v0.h[0]
    str d18, [\ptr1, #\off1_lo]
    mls v21.8h, v1.8h, v0.h[0]
    str d26, [\ptr2, #\off2_lo]
    str d3, [\ptr2, #\off2_hi]
    str d21, [\ptr0, #\off0_lo]
.endm

.macro RUN_FUSED_POST_STRIPE ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
.ifdef INVNTT_USE_POST_BRANCHFOLD_A72_SLOTHY
    FUSED_POST_STRIPE_BRANCHFOLD_A72_SLOTHY \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.else
.ifdef INVNTT_USE_POST_FUSED_N1_NODFTREDUCE_SLOTHY
    FUSED_POST_STRIPE_N1_NODFTREDUCE_SLOTHY \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.else
.ifdef INVNTT_USE_POST_FUSED_N1_SLOTHY
    FUSED_POST_STRIPE_N1_SLOTHY \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.else
.ifdef INVNTT_USE_POST_FUSED_SLOTHY
    FUSED_POST_STRIPE_SLOTHY \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.else
    FUSED_POST_STRIPE \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.endif
.endif
.endif
.endif
.endm


/* ---- original asm/slothy/invntt_opt.s:1204-2399: rowstage45/post fused prototype macros ---- */
.macro POST_STORE_PTR_BRANCHFOLD_SAFE xvec, ptr, off_lo, off_hi
    /*
     * Branchfold final store using only v4-v6 and v10-v13 as temporaries.
     * The row-stage45-to-post prototype keeps stage45 outputs live in
     * v16-v27 while emitting several post stripes from those registers.
     */
    ldr     q10, [x3], #16
    ldr     q11, [x3], #16
    ldr     q12, [x3], #16
    ldr     q13, [x3], #16

    sqrdmulh v4.8h, \xvec\().8h, v11.8h
    mul      v5.8h, \xvec\().8h, v10.8h
    mls      v5.8h, v4.8h, v0.h[0]
    ext      v6.16b, v5.16b, v5.16b, #8
    add      v6.8h, v5.8h, v6.8h

    sqrdmulh v4.8h, \xvec\().8h, v13.8h
    mul      v5.8h, \xvec\().8h, v12.8h
    mls      v5.8h, v4.8h, v0.h[0]
    ext      v4.16b, v5.16b, v5.16b, #8
    add      v5.8h, v5.8h, v4.8h

.ifdef INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS
    BARRETT_REDUCE v6, v4
    BARRETT_REDUCE v5, v4
.endif

    str      d6, [\ptr, #\off_lo]
    str      d5, [\ptr, #\off_hi]
.endm

.macro FUSED_POST_STRIPE_REG_SAFE r0, r1, r2, ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    sub      v4.8h, \r2\().8h, \r1\().8h
    sqrdmulh v5.8h, v4.8h, v0.h[3]
    mul      v6.8h, v4.8h, v0.h[2]
    mls      v6.8h, v5.8h, v0.h[0]

    add      v7.8h, \r0\().8h, \r1\().8h
    add      v7.8h, v7.8h, \r2\().8h

    sub      v8.8h, \r0\().8h, \r1\().8h
    add      v8.8h, v8.8h, v6.8h

    sub      v9.8h, \r0\().8h, \r2\().8h
    sub      v9.8h, v9.8h, v6.8h

    POST_STORE_PTR_BRANCHFOLD_SAFE v7, \ptr0, \off0_lo, \off0_hi
    POST_STORE_PTR_BRANCHFOLD_SAFE v8, \ptr1, \off1_lo, \off1_hi
    POST_STORE_PTR_BRANCHFOLD_SAFE v9, \ptr2, \off2_lo, \off2_hi
.endm

.macro FUSED_POST_STRIPE_REG_UNSAFE r0, r1, r2, ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    /*
     * Register-fed form of the production branchfold post stripe.  This uses
     * the normal post helper, so it may clobber v17-v24 and must only run
     * after any still-needed row-stage45 outputs have been saved elsewhere.
     */
    sub      v4.8h, \r2\().8h, \r1\().8h
    sqrdmulh v5.8h, v4.8h, v0.h[3]
    mul      v6.8h, v4.8h, v0.h[2]
    mls      v6.8h, v5.8h, v0.h[0]

    add      v7.8h, \r0\().8h, \r1\().8h
    add      v7.8h, v7.8h, \r2\().8h

    sub      v8.8h, \r0\().8h, \r1\().8h
    add      v8.8h, v8.8h, v6.8h

    sub      v9.8h, \r0\().8h, \r2\().8h
    sub      v9.8h, v9.8h, v6.8h

    POST_STORE_PTR_BRANCHFOLD v7, \ptr0, \off0_lo, \off0_hi
    POST_STORE_PTR_BRANCHFOLD v8, \ptr1, \off1_lo, \off1_hi
    POST_STORE_PTR_BRANCHFOLD v9, \ptr2, \off2_lo, \off2_hi
.endm

.macro FUSED_POST_STRIPE_REG_BRANCHFOLD_A72_SLOTHY r0, r1, r2, ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    /*
     * Register-fed variant of FUSED_POST_STRIPE_BRANCHFOLD_A72_SLOTHY.
     * The first three memory input loads are replaced by moves into the same
     * allocated registers used by the generated schedule.
     */
    mov v20.16b, \r1\().16b
    mov v21.16b, \r2\().16b
    mov v18.16b, \r0\().16b
    ldr q26, [x3], #16
    ldr q22, [x3], #16
    ldr q6, [x3], #16
    ldr q30, [x3], #16
    ldr q7, [x3], #16
    ldr q15, [x3], #16
    sub v3.8h, v21.8h, v20.8h
    ldr q23, [x3], #16
    add v1.8h, v18.8h, v20.8h
    sub v28.8h, v18.8h, v20.8h
    ldr q10, [x3], #16
    sub v18.8h, v18.8h, v21.8h
    ldr q8, [x3], #16
    ldr q11, [x3], #16
    ldr q4, [x3], #16
    sqrdmulh v24.8h, v3.8h, v0.h[3]
    ldr q9, [x3], #16
    add v2.8h, v1.8h, v21.8h
    mul v12.8h, v3.8h, v0.h[2]
    mul v26.8h, v2.8h, v26.8h
    sqrdmulh v19.8h, v2.8h, v22.8h
    mls v12.8h, v24.8h, v0.h[0]
    mul v3.8h, v2.8h, v6.8h
    sqrdmulh v13.8h, v2.8h, v30.8h
    add v24.8h, v28.8h, v12.8h
    sub v22.8h, v18.8h, v12.8h
    mls v26.8h, v19.8h, v0.h[0]
    mul v18.8h, v24.8h, v7.8h
    sqrdmulh v7.8h, v24.8h, v15.8h
    ext v30.16b, v26.16b, v26.16b, #8
    mul v19.8h, v24.8h, v23.8h
    sqrdmulh v17.8h, v24.8h, v10.8h
    add v21.8h, v26.8h, v30.8h
    mul v26.8h, v22.8h, v8.8h
    sqrdmulh v14.8h, v22.8h, v11.8h
    mul v30.8h, v22.8h, v4.8h
    sqrdmulh v9.8h, v22.8h, v9.8h
    mls v3.8h, v13.8h, v0.h[0]
    mls v18.8h, v7.8h, v0.h[0]
    mls v19.8h, v17.8h, v0.h[0]
    ext v28.16b, v3.16b, v3.16b, #8
    mls v26.8h, v14.8h, v0.h[0]
    ext v1.16b, v18.16b, v18.16b, #8
    add v16.8h, v3.8h, v28.8h
    sqdmulh v8.8h, v21.8h, v0.h[1]
    ext v7.16b, v19.16b, v19.16b, #8
    mls v30.8h, v9.8h, v0.h[0]
    add v18.8h, v18.8h, v1.8h
    ext v20.16b, v26.16b, v26.16b, #8
    add v11.8h, v19.8h, v7.8h
    sqdmulh v17.8h, v16.8h, v0.h[1]
    srshr v1.8h, v8.8h, #11
    add v26.8h, v26.8h, v20.8h
    sqdmulh v7.8h, v18.8h, v0.h[1]
    ext v10.16b, v30.16b, v30.16b, #8
    sqdmulh v22.8h, v11.8h, v0.h[1]
    srshr v9.8h, v17.8h, #11
    add v3.8h, v30.8h, v10.8h
    sqdmulh v12.8h, v26.8h, v0.h[1]
    srshr v25.8h, v7.8h, #11
    mls v16.8h, v9.8h, v0.h[0]
    srshr v20.8h, v22.8h, #11
    sqdmulh v13.8h, v3.8h, v0.h[1]
    srshr v10.8h, v12.8h, #11
    mls v11.8h, v20.8h, v0.h[0]
    str d16, [\ptr0, #\off0_hi]
    mls v18.8h, v25.8h, v0.h[0]
    srshr v2.8h, v13.8h, #11
    mls v26.8h, v10.8h, v0.h[0]
    str d11, [\ptr1, #\off1_hi]
    mls v3.8h, v2.8h, v0.h[0]
    str d18, [\ptr1, #\off1_lo]
    mls v21.8h, v1.8h, v0.h[0]
    str d26, [\ptr2, #\off2_lo]
    str d3, [\ptr2, #\off2_hi]
    str d21, [\ptr0, #\off0_lo]
.endm

.macro RUN_FUSED_POST_STRIPE_REG r0, r1, r2, ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
.ifdef INVNTT_USE_POST_BRANCHFOLD_A72_SLOTHY
    FUSED_POST_STRIPE_REG_BRANCHFOLD_A72_SLOTHY \r0, \r1, \r2, \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.else
    FUSED_POST_STRIPE_REG_UNSAFE \r0, \r1, \r2, \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.endif
.endm

.macro FUSED_POST_STRIPE_REG_V16_V24_V12_N1_SLOTHY ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    /*
     * Historical N1 Slothy schedule for the discarded register-fed post
     * prototype.  Inputs are fixed to v16/v24/v12.
     */
    sub v10.8h, v12.8h, v24.8h
    sub v8.8h, v16.8h, v24.8h
    add v17.8h, v16.8h, v24.8h
    sub v19.8h, v16.8h, v12.8h
    ldr q11, [x3], #16
    sqrdmulh v25.8h, v10.8h, v0.h[3]
    add v18.8h, v17.8h, v12.8h
    ldr q29, [x3], #16
    mul v26.8h, v10.8h, v0.h[2]
    ldr q12, [x3], #16
    ldr q20, [x3], #16
    ldr q7, [x3], #16
    mul v30.8h, v18.8h, v11.8h
    ldr q27, [x3], #16
    mls v26.8h, v25.8h, v0.h[0]
    mul v17.8h, v18.8h, v12.8h
    ldr q12, [x3], #16
    ldr q25, [x3], #16
    ldr q23, [x3], #16
    sqrdmulh v29.8h, v18.8h, v29.8h
    ldr q10, [x3], #16
    add v14.8h, v8.8h, v26.8h
    sub v19.8h, v19.8h, v26.8h
    sqrdmulh v21.8h, v18.8h, v20.8h
    mul v26.8h, v14.8h, v12.8h
    ldr q12, [x3], #16
    ldr q11, [x3], #16
    sqrdmulh v28.8h, v14.8h, v25.8h
    sqrdmulh v3.8h, v19.8h, v10.8h
    mul v10.8h, v14.8h, v7.8h
    mls v30.8h, v29.8h, v0.h[0]
    sqrdmulh v4.8h, v14.8h, v27.8h
    sqrdmulh v25.8h, v19.8h, v11.8h
    ext v5.16b, v30.16b, v30.16b, #8
    mul v20.8h, v19.8h, v12.8h
    add v30.8h, v30.8h, v5.8h
    mls v26.8h, v28.8h, v0.h[0]
    mls v17.8h, v21.8h, v0.h[0]
    mul v13.8h, v19.8h, v23.8h
    ext v24.16b, v26.16b, v26.16b, #8
    mls v10.8h, v4.8h, v0.h[0]
    add v11.8h, v26.8h, v24.8h
    mls v13.8h, v3.8h, v0.h[0]
    ext v24.16b, v17.16b, v17.16b, #8
    mls v20.8h, v25.8h, v0.h[0]
    add v17.8h, v17.8h, v24.8h
    ext v3.16b, v10.16b, v10.16b, #8
    sqdmulh v22.8h, v30.8h, v0.h[1]
    ext v27.16b, v13.16b, v13.16b, #8
    add v10.8h, v10.8h, v3.8h
    sqdmulh v14.8h, v17.8h, v0.h[1]
    ext v24.16b, v20.16b, v20.16b, #8
    add v5.8h, v13.8h, v27.8h
    sqdmulh v4.8h, v10.8h, v0.h[1]
    add v8.8h, v20.8h, v24.8h
    srshr v7.8h, v22.8h, #11
    sqdmulh v28.8h, v11.8h, v0.h[1]
    srshr v22.8h, v14.8h, #11
    sqdmulh v25.8h, v5.8h, v0.h[1]
    srshr v19.8h, v4.8h, #11
    sqdmulh v18.8h, v8.8h, v0.h[1]
    srshr v26.8h, v28.8h, #11
    mls v17.8h, v22.8h, v0.h[0]
    srshr v14.8h, v25.8h, #11
    mls v10.8h, v19.8h, v0.h[0]
    srshr v29.8h, v18.8h, #11
    mls v30.8h, v7.8h, v0.h[0]
    str d17, [\ptr0, #\off0_hi]
    mls v11.8h, v26.8h, v0.h[0]
    str d10, [\ptr1, #\off1_lo]
    mls v8.8h, v29.8h, v0.h[0]
    str d30, [\ptr0, #\off0_lo]
    mls v5.8h, v14.8h, v0.h[0]
    str d11, [\ptr1, #\off1_hi]
    str d8, [\ptr2, #\off2_hi]
    str d5, [\ptr2, #\off2_lo]
.endm

.macro FUSED_POST_STRIPE_REG_V1_V2_V15_N1_SLOTHY ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    /*
     * Historical N1 Slothy schedule for the discarded register-fed post
     * prototype.  Inputs are fixed to v1/v2/v15.
     */
    sub v17.8h, v15.8h, v2.8h
    sub v20.8h, v1.8h, v15.8h
    ldr q25, [x3], #16
    sub v14.8h, v1.8h, v2.8h
    add v29.8h, v1.8h, v2.8h
    mul v26.8h, v17.8h, v0.h[2]
    ldr q22, [x3], #16
    ldr q12, [x3], #16
    sqrdmulh v13.8h, v17.8h, v0.h[3]
    add v5.8h, v29.8h, v15.8h
    ldr q8, [x3], #16
    ldr q29, [x3], #16
    mul v30.8h, v5.8h, v25.8h
    ldr q21, [x3], #16
    sqrdmulh v25.8h, v5.8h, v22.8h
    mls v26.8h, v13.8h, v0.h[0]
    sqrdmulh v28.8h, v5.8h, v8.8h
    mul v17.8h, v5.8h, v12.8h
    ldr q12, [x3], #16
    sub v18.8h, v20.8h, v26.8h
    ldr q5, [x3], #16
    add v23.8h, v14.8h, v26.8h
    mls v30.8h, v25.8h, v0.h[0]
    ldr q9, [x3], #16
    ldr q20, [x3], #16
    mul v10.8h, v23.8h, v12.8h
    ldr q12, [x3], #16
    ldr q4, [x3], #16
    sqrdmulh v25.8h, v23.8h, v21.8h
    ext v13.16b, v30.16b, v30.16b, #8
    mul v29.8h, v23.8h, v29.8h
    add v30.8h, v30.8h, v13.8h
    sqrdmulh v22.8h, v23.8h, v5.8h
    sqrdmulh v23.8h, v18.8h, v20.8h
    sqrdmulh v6.8h, v18.8h, v4.8h
    mul v20.8h, v18.8h, v9.8h
    mul v14.8h, v18.8h, v12.8h
    mls v17.8h, v28.8h, v0.h[0]
    mls v29.8h, v25.8h, v0.h[0]
    mls v10.8h, v22.8h, v0.h[0]
    ext v24.16b, v17.16b, v17.16b, #8
    mls v14.8h, v6.8h, v0.h[0]
    add v17.8h, v17.8h, v24.8h
    mls v20.8h, v23.8h, v0.h[0]
    ext v28.16b, v29.16b, v29.16b, #8
    ext v24.16b, v10.16b, v10.16b, #8
    add v11.8h, v29.8h, v28.8h
    sqdmulh v26.8h, v17.8h, v0.h[1]
    add v7.8h, v10.8h, v24.8h
    ext v24.16b, v14.16b, v14.16b, #8
    sqdmulh v10.8h, v30.8h, v0.h[1]
    ext v5.16b, v20.16b, v20.16b, #8
    add v13.8h, v14.8h, v24.8h
    sqdmulh v23.8h, v7.8h, v0.h[1]
    add v18.8h, v20.8h, v5.8h
    srshr v14.8h, v26.8h, #11
    sqdmulh v25.8h, v13.8h, v0.h[1]
    srshr v4.8h, v10.8h, #11
    sqdmulh v19.8h, v18.8h, v0.h[1]
    srshr v28.8h, v23.8h, #11
    sqdmulh v3.8h, v11.8h, v0.h[1]
    srshr v8.8h, v25.8h, #11
    mls v17.8h, v14.8h, v0.h[0]
    srshr v27.8h, v19.8h, #11
    mls v30.8h, v4.8h, v0.h[0]
    srshr v29.8h, v3.8h, #11
    mls v13.8h, v8.8h, v0.h[0]
    str d17, [\ptr0, #\off0_hi]
    mls v18.8h, v27.8h, v0.h[0]
    str d30, [\ptr0, #\off0_lo]
    mls v7.8h, v28.8h, v0.h[0]
    str d13, [\ptr2, #\off2_hi]
    mls v11.8h, v29.8h, v0.h[0]
    str d18, [\ptr2, #\off2_lo]
    str d7, [\ptr1, #\off1_hi]
    str d11, [\ptr1, #\off1_lo]
.endm

.macro SET_BRANCHFOLD_PTR_FOR_K k
    adr x3, inv_branchfold_vecs
.if (192 * \k) > 4095
    add x3, x3, #4096
    add x3, x3, #((192 * \k) - 4096)
.else
.if (192 * \k) != 0
    add x3, x3, #(192 * \k)
.endif
.endif
.endm

.macro FUSED_POST_STRIPE_REG_K r0, r1, r2, k, group, rem
    SET_BRANCHFOLD_PTR_FOR_K \k
.if \rem == 0
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_SAFE \r0, \r1, \r2, x11, 0, 768, x12, 0, 768, x13, 0, 768
.elseif \rem == 1
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_SAFE \r0, \r1, \r2, x13, 8, 776, x11, 8, 776, x12, 8, 776
.elseif \rem == 2
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_SAFE \r0, \r1, \r2, x12, 16, 784, x13, 16, 784, x11, 16, 784
.else
    .error "invalid post stripe remainder"
.endif
.endm

.macro RUN_FUSED_POST_STRIPE_REG_K r0, r1, r2, k, group, rem
    SET_BRANCHFOLD_PTR_FOR_K \k
.if \rem == 0
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE_REG \r0, \r1, \r2, x11, 0, 768, x12, 0, 768, x13, 0, 768
.elseif \rem == 1
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE_REG \r0, \r1, \r2, x13, 8, 776, x11, 8, 776, x12, 8, 776
.elseif \rem == 2
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE_REG \r0, \r1, \r2, x12, 16, 784, x13, 16, 784, x11, 16, 784
.else
    .error "invalid post stripe remainder"
.endif
.endm

.macro RUN_FUSED_POST_STRIPE_REG_V16_V24_V12_N1_K k, group, rem
    SET_BRANCHFOLD_PTR_FOR_K \k
.if \rem == 0
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_V16_V24_V12_N1_SLOTHY x11, 0, 768, x12, 0, 768, x13, 0, 768
.elseif \rem == 1
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_V16_V24_V12_N1_SLOTHY x13, 8, 776, x11, 8, 776, x12, 8, 776
.elseif \rem == 2
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_V16_V24_V12_N1_SLOTHY x12, 16, 784, x13, 16, 784, x11, 16, 784
.else
    .error "invalid post stripe remainder"
.endif
.endm

.macro RUN_FUSED_POST_STRIPE_REG_V1_V2_V15_N1_K k, group, rem
    SET_BRANCHFOLD_PTR_FOR_K \k
.if \rem == 0
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_V1_V2_V15_N1_SLOTHY x11, 0, 768, x12, 0, 768, x13, 0, 768
.elseif \rem == 1
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_V1_V2_V15_N1_SLOTHY x13, 8, 776, x11, 8, 776, x12, 8, 776
.elseif \rem == 2
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_V1_V2_V15_N1_SLOTHY x12, 16, 784, x13, 16, 784, x11, 16, 784
.else
    .error "invalid post stripe remainder"
.endif
.endm

.macro INVNTT32_STAGE45_STRIPE_SCRATCH_REG j, out0, out8, out16, out24
    adr x3, invntt32_stage45_consts
.if (32 * \j) != 0
    add x3, x3, #(32 * \j)
.endif
    ldr q1, [x3], #16
    ldr q2, [x3], #16

    ldr q3, [x14, #(64 * \j + 0)]
    ldr q4, [x14, #(64 * \j + 16)]
    ldr q5, [x14, #(64 * \j + 32)]
    ldr q6, [x14, #(64 * \j + 48)]

    INV_BUTTERFLY_LANE v3, v4, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v5, v6, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v3, v5, v1, 1, v2, 1, v11, v12
    INV_BUTTERFLY_LANE v4, v6, v1, 2, v2, 2, v11, v12

.ifdef INVNTT_USE_STAGE45_REDUCE_FUSION
    BARRETT_REDUCE v3, v12
    BARRETT_REDUCE v4, v12
    BARRETT_REDUCE v5, v12
    BARRETT_REDUCE v6, v12
.endif

    mov \out0\().16b, v3.16b
    mov \out8\().16b, v4.16b
    mov \out16\().16b, v5.16b
    mov \out24\().16b, v6.16b
.endm

.macro INVNTT32_STAGE45_STRIPE_SCRATCH_STORE4_SIMPLE j
    adr x3, invntt32_stage45_consts
.if (32 * \j) != 0
    add x3, x3, #(32 * \j)
.endif
    ldr q1, [x3], #16
    ldr q2, [x3], #16

    ldr q3, [x14, #(64 * \j + 0)]
    ldr q4, [x14, #(64 * \j + 16)]
    ldr q5, [x14, #(64 * \j + 32)]
    ldr q6, [x14, #(64 * \j + 48)]

    INV_BUTTERFLY_LANE v3, v4, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v5, v6, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v3, v5, v1, 1, v2, 1, v11, v12
    INV_BUTTERFLY_LANE v4, v6, v1, 2, v2, 2, v11, v12

.ifdef INVNTT_USE_STAGE45_REDUCE_FUSION
    BARRETT_REDUCE v3, v12
    BARRETT_REDUCE v4, v12
    BARRETT_REDUCE v5, v12
    BARRETT_REDUCE v6, v12
.endif

    str q3, [x2, #0]
    str q4, [x2, #16]
    str q5, [x2, #32]
    str q6, [x2, #48]
.endm

.macro INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_STORE4 j
    adr x3, invntt32_stage45_consts
.if (32 * \j) != 0
    add x3, x3, #(32 * \j)
.endif
    ldr q11, [x14, #(64 * \j + 48)]
    ldr q7, [x3, #16]
    ldr q30, [x14, #(64 * \j + 32)]
    ldr q5, [x3]
    ldr q26, [x14, #(64 * \j + 16)]
    ldr q17, [x14, #(64 * \j + 0)]
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
    str q10, [x2, #16]
    str q29, [x2, #32]
    str q23, [x2, #48]
.endm

.macro INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP0_STORE3 j, keep0
    adr x3, invntt32_stage45_consts
.if (32 * \j) != 0
    add x3, x3, #(32 * \j)
.endif
    ldr q11, [x14, #(64 * \j + 48)]
    ldr q7, [x3, #16]
    ldr q30, [x14, #(64 * \j + 32)]
    ldr q5, [x3]
    ldr q26, [x14, #(64 * \j + 16)]
    ldr q17, [x14, #(64 * \j + 0)]
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
    mov \keep0\().16b, v17.16b
    str q10, [x2, #16]
    str q29, [x2, #32]
    str q23, [x2, #48]
.endm

.macro INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 j, keep0, keep8
    adr x3, invntt32_stage45_consts
.if (32 * \j) != 0
    add x3, x3, #(32 * \j)
.endif
    ldr q11, [x14, #(64 * \j + 48)]
    ldr q7, [x3, #16]
    ldr q30, [x14, #(64 * \j + 32)]
    ldr q5, [x3]
    ldr q26, [x14, #(64 * \j + 16)]
    ldr q17, [x14, #(64 * \j + 0)]
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
    mov \keep0\().16b, v17.16b
    mov \keep8\().16b, v10.16b
    str q29, [x2, #32]
    str q23, [x2, #48]
.endm

.macro INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_POST01_STORE2 j, row0_0, row1_0, row0_8, row1_8, k0, group0, rem0, k8, group8, rem8
    /*
     * Combined row2 stage45 tail + post for output0/output8.
     *
     * row0_0/row1_0 and row0_8/row1_8 are already live from the previous two
     * row stage45 blocks.  This computes row2 stage45 once, stores output16
     * and output24 to the mini-buffer, and immediately consumes output0 and
     * output8 through the register-fed post helper.
     */
    adr x3, invntt32_stage45_consts
.if (32 * \j) != 0
    add x3, x3, #(32 * \j)
.endif
    ldr q11, [x14, #(64 * \j + 48)]
    ldr q7, [x3, #16]
    ldr q30, [x14, #(64 * \j + 32)]
    ldr q5, [x3]
    ldr q26, [x14, #(64 * \j + 16)]
    ldr q17, [x14, #(64 * \j + 0)]
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

    mov v15.16b, v10.16b
    str q29, [x2, #32]
    str q23, [x2, #48]

    RUN_FUSED_POST_STRIPE_REG_K \row0_0, \row1_0, v17, \k0, \group0, \rem0
    RUN_FUSED_POST_STRIPE_REG_K \row0_8, \row1_8, v15, \k8, \group8, \rem8
.endm

.macro INVNTT32_STAGE45_STRIPE_SCRATCH_STORE4 j
.ifdef INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_STORE4 \j
.else
    INVNTT32_STAGE45_STRIPE_SCRATCH_STORE4_SIMPLE \j
.endif
.endm

.macro ROWSTAGE45_POST_FUSED_STRIPE j, k0, group0, rem0, k8, group8, rem8, k16, group16, rem16, k24, group24, rem24
    add x14, sp, #32
    INVNTT32_STAGE45_STRIPE_SCRATCH_REG \j, v16, v17, v18, v19
    add x14, sp, #544
    INVNTT32_STAGE45_STRIPE_SCRATCH_REG \j, v20, v21, v22, v23
    add x14, sp, #1056
    INVNTT32_STAGE45_STRIPE_SCRATCH_REG \j, v24, v25, v26, v27

    FUSED_POST_STRIPE_REG_K v16, v20, v24, \k0, \group0, \rem0
    FUSED_POST_STRIPE_REG_K v17, v21, v25, \k8, \group8, \rem8
    FUSED_POST_STRIPE_REG_K v18, v22, v26, \k16, \group16, \rem16
    FUSED_POST_STRIPE_REG_K v19, v23, v27, \k24, \group24, \rem24
.endm

.macro SET_BRANCHFOLD_PTR_FOR_J j
    adr x3, inv_branchfold_vecs
.if (192 * \j) != 0
    add x3, x3, #(192 * \j)
.endif
.endm

.macro FUSED_POST_STRIPE_REG_AT_CURRENT_PTR r0, r1, r2, group, rem
.if \rem == 0
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_SAFE \r0, \r1, \r2, x11, 0, 768, x12, 0, 768, x13, 0, 768
.elseif \rem == 1
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_SAFE \r0, \r1, \r2, x13, 8, 776, x11, 8, 776, x12, 8, 776
.elseif \rem == 2
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    FUSED_POST_STRIPE_REG_SAFE \r0, \r1, \r2, x12, 16, 784, x13, 16, 784, x11, 16, 784
.else
    .error "invalid post stripe remainder"
.endif
.endm

.macro RUN_FUSED_POST_STRIPE_REG_AT_CURRENT_PTR r0, r1, r2, group, rem
.if \rem == 0
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE_REG \r0, \r1, \r2, x11, 0, 768, x12, 0, 768, x13, 0, 768
.elseif \rem == 1
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE_REG \r0, \r1, \r2, x13, 8, 776, x11, 8, 776, x12, 8, 776
.elseif \rem == 2
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE_REG \r0, \r1, \r2, x12, 16, 784, x13, 16, 784, x11, 16, 784
.else
    .error "invalid post stripe remainder"
.endif
.endm

.macro ROWSTAGE45_POST_REGFUSED_V3_STRIPE j, k0, group0, rem0, k8, group8, rem8, k16, group16, rem16, k24, group24, rem24
    add x14, sp, #32
    INVNTT32_STAGE45_STRIPE_SCRATCH_REG \j, v16, v17, v18, v19
    add x14, sp, #544
    INVNTT32_STAGE45_STRIPE_SCRATCH_REG \j, v20, v21, v22, v23
    add x14, sp, #1056
    INVNTT32_STAGE45_STRIPE_SCRATCH_REG \j, v24, v25, v26, v27

    SET_BRANCHFOLD_PTR_FOR_J \j
    FUSED_POST_STRIPE_REG_AT_CURRENT_PTR v16, v20, v24, \group0, \rem0
    add x3, x3, #1344
    FUSED_POST_STRIPE_REG_AT_CURRENT_PTR v17, v21, v25, \group8, \rem8
    add x3, x3, #1344
    FUSED_POST_STRIPE_REG_AT_CURRENT_PTR v18, v22, v26, \group16, \rem16
    add x3, x3, #1344
    FUSED_POST_STRIPE_REG_AT_CURRENT_PTR v19, v23, v27, \group24, \rem24
.endm

.macro FUSED_POST_STRIPE_MEM_K k, group, rem, off
    add x8, sp, #(1568 + 16 * \off)
    add x9, sp, #(1632 + 16 * \off)
    add x10, sp, #(1696 + 16 * \off)
    SET_BRANCHFOLD_PTR_FOR_K \k
.if \rem == 0
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
.elseif \rem == 1
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
.elseif \rem == 2
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE x12, 16, 784, x13, 16, 784, x11, 16, 784
.else
    .error "invalid post stripe remainder"
.endif
.endm

.macro FUSED_POST_STRIPE_MEM_AT_CURRENT_PTR group, rem, off
    add x8, sp, #(1568 + 16 * \off)
    add x9, sp, #(1632 + 16 * \off)
    add x10, sp, #(1696 + 16 * \off)
.if \rem == 0
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
.elseif \rem == 1
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
.elseif \rem == 2
    add x11, x19, #(24 * \group)
    add x12, x19, #(512 + 24 * \group)
    add x13, x19, #(256 + 24 * \group)
    RUN_FUSED_POST_STRIPE x12, 16, 784, x13, 16, 784, x11, 16, 784
.else
    .error "invalid post stripe remainder"
.endif
.endm

.macro ROWSTAGE45_POST_MINIBUF_STRIPE j, k0, group0, rem0, k8, group8, rem8, k16, group16, rem16, k24, group24, rem24
    add x14, sp, #32
    add x2, sp, #1568
    INVNTT32_STAGE45_STRIPE_SCRATCH_STORE4 \j
    add x14, sp, #544
    add x2, sp, #1632
    INVNTT32_STAGE45_STRIPE_SCRATCH_STORE4 \j
    add x14, sp, #1056
    add x2, sp, #1696
    INVNTT32_STAGE45_STRIPE_SCRATCH_STORE4 \j

    FUSED_POST_STRIPE_MEM_K \k0, \group0, \rem0, 0
    FUSED_POST_STRIPE_MEM_K \k8, \group8, \rem8, 1
    FUSED_POST_STRIPE_MEM_K \k16, \group16, \rem16, 2
    FUSED_POST_STRIPE_MEM_K \k24, \group24, \rem24, 3
.endm

.macro ROWSTAGE45_POST_REGFUSED_V3B_STRIPE j, k0, group0, rem0, k8, group8, rem8, k16, group16, rem16, k24, group24, rem24
    add x14, sp, #32
    add x2, sp, #1568
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP0_STORE3 \j, v16
    add x14, sp, #544
    add x2, sp, #1632
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP0_STORE3 \j, v24
    add x14, sp, #1056
    add x2, sp, #1696
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP0_STORE3 \j, v12

    RUN_FUSED_POST_STRIPE_REG_K v16, v24, v12, \k0, \group0, \rem0
    FUSED_POST_STRIPE_MEM_K \k8, \group8, \rem8, 1
    FUSED_POST_STRIPE_MEM_K \k16, \group16, \rem16, 2
    FUSED_POST_STRIPE_MEM_K \k24, \group24, \rem24, 3
.endm

.macro ROWSTAGE45_POST_REGFUSED_V4_STRIPE j, k0, group0, rem0, k8, group8, rem8, k16, group16, rem16, k24, group24, rem24
    add x14, sp, #32
    add x2, sp, #1568
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v16, v1
    add x14, sp, #544
    add x2, sp, #1632
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v24, v2
    add x14, sp, #1056
    add x2, sp, #1696
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v12, v15

    RUN_FUSED_POST_STRIPE_REG_K v16, v24, v12, \k0, \group0, \rem0
    RUN_FUSED_POST_STRIPE_REG_K v1, v2, v15, \k8, \group8, \rem8
    FUSED_POST_STRIPE_MEM_K \k16, \group16, \rem16, 2
    FUSED_POST_STRIPE_MEM_K \k24, \group24, \rem24, 3
.endm

.macro ROWSTAGE45_POST_REGFUSED_V4S_STRIPE j, k0, group0, rem0, k8, group8, rem8, k16, group16, rem16, k24, group24, rem24
    /*
     * v4 live-range cleanup: keep row1 output0 in v31 instead of v24.
     * The Slothy stage45 helper uses v24 as an internal temp, so v31 gives the
     * direct-fed output0 stripe a cleaner lifetime without changing dataflow.
     */
    add x14, sp, #32
    add x2, sp, #1568
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v16, v1
    add x14, sp, #544
    add x2, sp, #1632
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v31, v2
    add x14, sp, #1056
    add x2, sp, #1696
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v12, v15

    RUN_FUSED_POST_STRIPE_REG_K v16, v31, v12, \k0, \group0, \rem0
    RUN_FUSED_POST_STRIPE_REG_K v1, v2, v15, \k8, \group8, \rem8
    FUSED_POST_STRIPE_MEM_K \k16, \group16, \rem16, 2
    FUSED_POST_STRIPE_MEM_K \k24, \group24, \rem24, 3
.endm

.macro ROWSTAGE45_POST_COMBINED_V6_STRIPE j, k0, group0, rem0, k8, group8, rem8, k16, group16, rem16, k24, group24, rem24
    /*
     * Combined stage45/post prototype:
     *   - row0 and row1 produce output0/output8 as live inputs
     *   - row2 stage45 tail directly feeds output0/output8 post
     *   - output16/output24 remain on the stripe-local mini-buffer path
     */
    add x14, sp, #32
    add x2, sp, #1568
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v16, v1
    add x14, sp, #544
    add x2, sp, #1632
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v31, v2
    add x14, sp, #1056
    add x2, sp, #1696
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_POST01_STORE2 \j, v16, v31, v1, v2, \k0, \group0, \rem0, \k8, \group8, \rem8

    FUSED_POST_STRIPE_MEM_K \k16, \group16, \rem16, 2
    FUSED_POST_STRIPE_MEM_K \k24, \group24, \rem24, 3
.endm

.macro INVNTT32_STAGE45_POST01_STORE2_N1_COMBINED j, k0, group0, rem0, k8, group8, rem8
    /*
     * Slothy N1 schedule for one row2 stage45 tail plus the two direct-fed
     * post stripes.  Inputs:
     *   x14 = row2 stripe scratch base for j, x2 = row2 mini-buffer base
     *   v16/v31 = row0/row1 output0, v1/v2 = row0/row1 output8
     */
    SET_BRANCHFOLD_PTR_FOR_K_TO x15, \k0
    SET_BRANCHFOLD_PTR_FOR_K_TO x16, \k8
    SET_COMBINED_POST_PTRS x11, x12, x13, \group0, \rem0
    SET_COMBINED_POST_PTRS x4, x5, x6, \group8, \rem8
    adr x3, invntt32_stage45_consts
.if (32 * \j) != 0
    add x3, x3, #(32 * \j)
.endif

    ldr q11, [x3, #16]
    ldr q8, [x14, #48]
    ldr q17, [x16], #16
    ldr q20, [x16], #16
    ldr q29, [x14, #0]
    ldr q6, [x3]
    ldr q9, [x14, #16]
    sqrdmulh v5.8h, v8.8h, v11.h[0]
    mul v13.8h, v8.8h, v6.h[0]
    sqrdmulh v25.8h, v9.8h, v11.h[0]
    mls v13.8h, v5.8h, v0.h[0]
    ldr q5, [x14, #32]
    mul v14.8h, v9.8h, v6.h[0]
    add v9.8h, v1.8h, v2.8h
    mls v14.8h, v25.8h, v0.h[0]
    add v7.8h, v5.8h, v13.8h
    sub v21.8h, v5.8h, v13.8h
    sqrdmulh v5.8h, v7.8h, v11.h[1]
    sqrdmulh v23.8h, v21.8h, v11.h[2]
    sub v18.8h, v29.8h, v14.8h
    add v30.8h, v29.8h, v14.8h
    mul v3.8h, v7.8h, v6.h[1]
    mls v3.8h, v5.8h, v0.h[0]
    mul v19.8h, v21.8h, v6.h[2]
    ldr q6, [x16], #16
    ldr q29, [x16], #16
    add v21.8h, v16.8h, v31.8h
    mls v19.8h, v23.8h, v0.h[0]
    add v22.8h, v30.8h, v3.8h
    sub v13.8h, v30.8h, v3.8h
    ldr q3, [x15], #16
    sqdmulh v7.8h, v22.8h, v0.h[1]
    ldr q4, [x15], #16
    add v11.8h, v18.8h, v19.8h
    sqdmulh v5.8h, v13.8h, v0.h[1]
    sub v19.8h, v18.8h, v19.8h
    sqdmulh v27.8h, v11.8h, v0.h[1]
    srshr v10.8h, v7.8h, #11
    sqdmulh v14.8h, v19.8h, v0.h[1]
    srshr v26.8h, v5.8h, #11
    srshr v8.8h, v27.8h, #11
    mls v22.8h, v10.8h, v0.h[0]
    mls v13.8h, v26.8h, v0.h[0]
    srshr v23.8h, v14.8h, #11
    ldr q7, [x15], #16
    ldr q5, [x15], #16
    mls v11.8h, v8.8h, v0.h[0]
    add v28.8h, v21.8h, v22.8h
    mls v19.8h, v23.8h, v0.h[0]
    str q13, [x2, #32]
    sub v13.8h, v22.8h, v31.8h
    sqrdmulh v18.8h, v28.8h, v5.8h
    orr v15.16b, v11.16b, v11.16b
    ldr q11, [x16], #16
    sqrdmulh v10.8h, v13.8h, v0.h[3]
    ldr q25, [x16], #16
    add v26.8h, v9.8h, v15.8h
    str q19, [x2, #48]
    mul v13.8h, v13.8h, v0.h[2]
    mul v8.8h, v26.8h, v17.8h
    sub v17.8h, v15.8h, v2.8h
    sqrdmulh v5.8h, v17.8h, v0.h[3]
    sub v21.8h, v16.8h, v22.8h
    mul v9.8h, v17.8h, v0.h[2]
    ldr q17, [x16], #16
    mls v13.8h, v10.8h, v0.h[0]
    mls v9.8h, v5.8h, v0.h[0]
    sub v5.8h, v1.8h, v2.8h
    sqrdmulh v27.8h, v28.8h, v4.8h
    sub v14.8h, v21.8h, v13.8h
    mul v19.8h, v28.8h, v7.8h
    add v23.8h, v5.8h, v9.8h
    mls v19.8h, v18.8h, v0.h[0]
    ldr q5, [x16], #16
    mul v22.8h, v23.8h, v11.8h
    sub v11.8h, v16.8h, v31.8h
    add v21.8h, v11.8h, v13.8h
    mul v13.8h, v28.8h, v3.8h
    mls v13.8h, v27.8h, v0.h[0]
    sqrdmulh v10.8h, v23.8h, v25.8h
    mul v25.8h, v23.8h, v17.8h
    ldr q17, [x15], #16
    ldr q4, [x15], #16
    ldr q11, [x15], #16
    sqrdmulh v23.8h, v23.8h, v5.8h
    ldr q5, [x15], #16
    ext v28.16b, v13.16b, v13.16b, #8
    mls v22.8h, v10.8h, v0.h[0]
    add v13.8h, v13.8h, v28.8h
    sqrdmulh v7.8h, v21.8h, v5.8h
    ldr q5, [x15], #16
    mul v3.8h, v21.8h, v17.8h
    sqdmulh v28.8h, v13.8h, v0.h[1]
    mul v10.8h, v21.8h, v11.8h
    ldr q11, [x15], #16
    ldr q12, [x15], #16
    mls v10.8h, v7.8h, v0.h[0]
    srshr v28.8h, v28.8h, #11
    sqrdmulh v17.8h, v14.8h, v11.8h
    mul v5.8h, v14.8h, v5.8h
    ext v7.16b, v10.16b, v10.16b, #8
    sqrdmulh v11.8h, v21.8h, v4.8h
    add v10.8h, v10.8h, v7.8h
    mls v25.8h, v23.8h, v0.h[0]
    mul v23.8h, v14.8h, v12.8h
    ext v7.16b, v19.16b, v19.16b, #8
    mls v13.8h, v28.8h, v0.h[0]
    add v27.8h, v19.8h, v7.8h
    mls v5.8h, v17.8h, v0.h[0]
    ext v19.16b, v22.16b, v22.16b, #8
    ldr q7, [x16], #16
    add v4.8h, v22.8h, v19.8h
    sqdmulh v22.8h, v27.8h, v0.h[1]
    COMBINED_POST_STORE_LO d13, x11, \rem0
    ldr q13, [x15], #16
    sqdmulh v17.8h, v10.8h, v0.h[1]
    ext v19.16b, v5.16b, v5.16b, #8
    mls v3.8h, v11.8h, v0.h[0]
    add v19.8h, v5.8h, v19.8h
    sqrdmulh v21.8h, v14.8h, v13.8h
    srshr v28.8h, v17.8h, #11
    sqdmulh v17.8h, v4.8h, v0.h[1]
    srshr v13.8h, v22.8h, #11
    sqdmulh v14.8h, v19.8h, v0.h[1]
    mls v23.8h, v21.8h, v0.h[0]
    srshr v5.8h, v17.8h, #11
    ext v17.16b, v25.16b, v25.16b, #8
    mul v21.8h, v26.8h, v6.8h
    mls v10.8h, v28.8h, v0.h[0]
    add v22.8h, v25.8h, v17.8h
    ext v17.16b, v23.16b, v23.16b, #8
    ldr q25, [x16], #16
    mls v4.8h, v5.8h, v0.h[0]
    ldr q30, [x16], #16
    add v12.8h, v23.8h, v17.8h
    sqrdmulh v5.8h, v26.8h, v20.8h
    COMBINED_POST_STORE_HI d10, x12, \rem0
    sqdmulh v28.8h, v12.8h, v0.h[1]
    COMBINED_POST_STORE_LO d4, x5, \rem8
    ext v4.16b, v3.16b, v3.16b, #8
    mls v27.8h, v13.8h, v0.h[0]
    add v3.8h, v3.8h, v4.8h
    mls v8.8h, v5.8h, v0.h[0]
    sub v5.8h, v1.8h, v15.8h
    srshr v17.8h, v28.8h, #11
    sub v20.8h, v5.8h, v9.8h
    sqdmulh v4.8h, v3.8h, v0.h[1]
    sqrdmulh v25.8h, v20.8h, v25.8h
    ext v6.16b, v8.16b, v8.16b, #8
    mls v12.8h, v17.8h, v0.h[0]
    add v10.8h, v8.8h, v6.8h
    ldr q8, [x16], #16
    sqrdmulh v6.8h, v26.8h, v29.8h
    srshr v9.8h, v4.8h, #11
    sqdmulh v17.8h, v10.8h, v0.h[1]
    COMBINED_POST_STORE_HI d12, x13, \rem0
    mul v26.8h, v20.8h, v7.8h
    srshr v7.8h, v14.8h, #11
    sqrdmulh v5.8h, v20.8h, v8.8h
    srshr v11.8h, v17.8h, #11
    mls v21.8h, v6.8h, v0.h[0]
    mls v19.8h, v7.8h, v0.h[0]
    mul v17.8h, v20.8h, v30.8h
    mls v17.8h, v5.8h, v0.h[0]
    ext v5.16b, v21.16b, v21.16b, #8
    COMBINED_POST_STORE_LO d19, x13, \rem0
    mls v26.8h, v25.8h, v0.h[0]
    add v19.8h, v21.8h, v5.8h
    sqdmulh v7.8h, v19.8h, v0.h[1]
    ext v5.16b, v17.16b, v17.16b, #8
    sqdmulh v6.8h, v22.8h, v0.h[1]
    add v25.8h, v17.8h, v5.8h
    mls v3.8h, v9.8h, v0.h[0]
    ext v17.16b, v26.16b, v26.16b, #8
    srshr v8.8h, v7.8h, #11
    add v7.8h, v26.8h, v17.8h
    sqdmulh v5.8h, v25.8h, v0.h[1]
    srshr v13.8h, v6.8h, #11
    sqdmulh v6.8h, v7.8h, v0.h[1]
    COMBINED_POST_STORE_LO d3, x12, \rem0
    mls v19.8h, v8.8h, v0.h[0]
    srshr v21.8h, v5.8h, #11
    COMBINED_POST_STORE_HI d27, x11, \rem0
    mls v10.8h, v11.8h, v0.h[0]
    srshr v17.8h, v6.8h, #11
    mls v22.8h, v13.8h, v0.h[0]
    COMBINED_POST_STORE_HI d19, x4, \rem8
    mls v25.8h, v21.8h, v0.h[0]
    COMBINED_POST_STORE_LO d10, x4, \rem8
    mls v7.8h, v17.8h, v0.h[0]
    COMBINED_POST_STORE_HI d22, x5, \rem8
    COMBINED_POST_STORE_HI d25, x6, \rem8
    COMBINED_POST_STORE_LO d7, x6, \rem8
.endm

.macro ROWSTAGE45_POST_COMBINED_V7_SLOTHY_STRIPE j, k0, group0, rem0, k8, group8, rem8, k16, group16, rem16, k24, group24, rem24
    /*
     * v7: v6 dataflow, but row2 stage45 tail and the two direct-fed post
     * stripes use one clean N1 Slothy schedule.
     */
    add x14, sp, #32
    add x2, sp, #1568
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v16, v1
    add x14, sp, #544
    add x2, sp, #1632
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v31, v2
    add x14, sp, #(1056 + 64 * \j)
    add x2, sp, #1696
    INVNTT32_STAGE45_POST01_STORE2_N1_COMBINED \j, \k0, \group0, \rem0, \k8, \group8, \rem8

    FUSED_POST_STRIPE_MEM_K \k16, \group16, \rem16, 2
    FUSED_POST_STRIPE_MEM_K \k24, \group24, \rem24, 3
.endm

.macro ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_STRIPE j, k0, group0, rem0, k8, group8, rem8, k16, group16, rem16, k24, group24, rem24
    add x14, sp, #32
    add x2, sp, #1568
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v16, v1
    add x14, sp, #544
    add x2, sp, #1632
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v24, v2
    add x14, sp, #1056
    add x2, sp, #1696
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v12, v15

    RUN_FUSED_POST_STRIPE_REG_V16_V24_V12_N1_K \k0, \group0, \rem0
    RUN_FUSED_POST_STRIPE_REG_V1_V2_V15_N1_K \k8, \group8, \rem8
    FUSED_POST_STRIPE_MEM_K \k16, \group16, \rem16, 2
    FUSED_POST_STRIPE_MEM_K \k24, \group24, \rem24, 3
.endm

.macro ROWSTAGE45_POST_REGFUSED_V4P_STRIPE j, k0, group0, rem0, k8, group8, rem8, k16, group16, rem16, k24, group24, rem24
    add x14, sp, #32
    add x2, sp, #1568
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v16, v1
    add x14, sp, #544
    add x2, sp, #1632
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v24, v2
    add x14, sp, #1056
    add x2, sp, #1696
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH_KEEP01_STORE2 \j, v12, v15

/* ---- original asm/slothy/invntt_opt.s:2459-2908: prototype entry blocks and stack variants ---- */
.ifdef INVNTT_USE_ROWSTAGE45_POST_COMBINED_V6_PROTO
.equ INVNTT_STACK_SIZE, 1760
.equ INVNTT_SAVED_X0_OFFSET, 1768
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_PROTO
.equ INVNTT_STACK_SIZE, 1760
.equ INVNTT_SAVED_X0_OFFSET, 1768
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V4S_PROTO
.equ INVNTT_STACK_SIZE, 1760
.equ INVNTT_SAVED_X0_OFFSET, 1768
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V4P_PROTO
.equ INVNTT_STACK_SIZE, 1760
.equ INVNTT_SAVED_X0_OFFSET, 1768
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V4_PROTO
.equ INVNTT_STACK_SIZE, 1760
.equ INVNTT_SAVED_X0_OFFSET, 1768
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V3B_PROTO
.equ INVNTT_STACK_SIZE, 1760
.equ INVNTT_SAVED_X0_OFFSET, 1768
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V3_PROTO
.equ INVNTT_STACK_SIZE, 1568
.equ INVNTT_SAVED_X0_OFFSET, 1576
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_MINIBUF_PROTO
.equ INVNTT_STACK_SIZE, 1760
.equ INVNTT_SAVED_X0_OFFSET, 1768
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_FUSED_PROTO
.equ INVNTT_STACK_SIZE, 1568
.equ INVNTT_SAVED_X0_OFFSET, 1576
.else
.ifdef INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH
.equ INVNTT_STACK_SIZE, 2080
.equ INVNTT_SAVED_X0_OFFSET, 2088
.else
.equ INVNTT_STACK_SIZE, 1568
.equ INVNTT_SAVED_X0_OFFSET, 1576
.endif
.endif
.endif
.endif
.endif
.endif
.endif
.endif
.endif
.endif
.ifdef INVNTT_USE_ROWSTAGE45_POST_COMBINED_V6_PROTO
    stp x30, x19, [sp, #-16]!
    mov x19, x0
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_PROTO
    stp x30, x19, [sp, #-16]!
    mov x19, x0
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V4S_PROTO
    stp x30, x19, [sp, #-16]!
    mov x19, x0
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V4P_PROTO
    stp x30, x19, [sp, #-16]!
    mov x19, x0
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V4_PROTO
    stp x30, x19, [sp, #-16]!
    mov x19, x0
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V3B_PROTO
    stp x30, x19, [sp, #-16]!
    mov x19, x0
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V3_PROTO
    stp x30, x19, [sp, #-16]!
    mov x19, x0
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_MINIBUF_PROTO
    stp x30, x19, [sp, #-16]!
    mov x19, x0
.else
.ifdef INVNTT_USE_ROWSTAGE45_POST_FUSED_PROTO
    stp x30, x19, [sp, #-16]!
    mov x19, x0
.else
    stp x30, x0, [sp, #-16]!
.endif
.endif
.endif
.endif
.endif
.endif
.endif
.endif
.endif
    sub sp, sp, #INVNTT_STACK_SIZE
    str w15, [sp]

    adr x3, inv_consts
    ldr q0, [x3]

.ifdef INVNTT_USE_ROWSTAGE45_POST_COMBINED_V6_PROTO
    /*
     * Prototype v6:
     *   first combined stage45/post boundary.  Row2's stage45 output0/output8
     *   are consumed directly by the two register-fed post stripes inside the
     *   row2 stage45 macro.  Output16/output24 stay on the mini-buffer path.
     */
    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #32
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #544
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #1056
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY

.ifdef INVNTT_USE_ROWSTAGE45_POST_COMBINED_V7_SLOTHY_PROTO
    ROWSTAGE45_POST_COMBINED_V7_SLOTHY_STRIPE 0, 0, 0, 0, 8, 2, 2, 16, 5, 1, 24, 8, 0
    ROWSTAGE45_POST_COMBINED_V7_SLOTHY_STRIPE 1, 1, 0, 1, 9, 3, 0, 17, 5, 2, 25, 8, 1
    ROWSTAGE45_POST_COMBINED_V7_SLOTHY_STRIPE 2, 2, 0, 2, 10, 3, 1, 18, 6, 0, 26, 8, 2
    ROWSTAGE45_POST_COMBINED_V7_SLOTHY_STRIPE 3, 3, 1, 0, 11, 3, 2, 19, 6, 1, 27, 9, 0
    ROWSTAGE45_POST_COMBINED_V7_SLOTHY_STRIPE 4, 4, 1, 1, 12, 4, 0, 20, 6, 2, 28, 9, 1
    ROWSTAGE45_POST_COMBINED_V7_SLOTHY_STRIPE 5, 5, 1, 2, 13, 4, 1, 21, 7, 0, 29, 9, 2
    ROWSTAGE45_POST_COMBINED_V7_SLOTHY_STRIPE 6, 6, 2, 0, 14, 4, 2, 22, 7, 1, 30, 10, 0
    ROWSTAGE45_POST_COMBINED_V7_SLOTHY_STRIPE 7, 7, 2, 1, 15, 5, 0, 23, 7, 2, 31, 10, 1
.else
    ROWSTAGE45_POST_COMBINED_V6_STRIPE 0, 0, 0, 0, 8, 2, 2, 16, 5, 1, 24, 8, 0
    ROWSTAGE45_POST_COMBINED_V6_STRIPE 1, 1, 0, 1, 9, 3, 0, 17, 5, 2, 25, 8, 1
    ROWSTAGE45_POST_COMBINED_V6_STRIPE 2, 2, 0, 2, 10, 3, 1, 18, 6, 0, 26, 8, 2
    ROWSTAGE45_POST_COMBINED_V6_STRIPE 3, 3, 1, 0, 11, 3, 2, 19, 6, 1, 27, 9, 0
    ROWSTAGE45_POST_COMBINED_V6_STRIPE 4, 4, 1, 1, 12, 4, 0, 20, 6, 2, 28, 9, 1
    ROWSTAGE45_POST_COMBINED_V6_STRIPE 5, 5, 1, 2, 13, 4, 1, 21, 7, 0, 29, 9, 2
    ROWSTAGE45_POST_COMBINED_V6_STRIPE 6, 6, 2, 0, 14, 4, 2, 22, 7, 1, 30, 10, 0
    ROWSTAGE45_POST_COMBINED_V6_STRIPE 7, 7, 2, 1, 15, 5, 0, 23, 7, 2, 31, 10, 1
.endif

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.endif

.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_PROTO
    /*
     * Prototype v5:
     *   v4 dataflow, but the two register-fed post stripes use the historical
     *   N1 Slothy schedules above.  The standalone wrapper was removed after
     *   Pi 5 measurements showed this path was slower than stage123 scratch.
     */
    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #32
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #544
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #1056
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY

    ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_STRIPE 0, 0, 0, 0, 8, 2, 2, 16, 5, 1, 24, 8, 0
    ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_STRIPE 1, 1, 0, 1, 9, 3, 0, 17, 5, 2, 25, 8, 1
    ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_STRIPE 2, 2, 0, 2, 10, 3, 1, 18, 6, 0, 26, 8, 2
    ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_STRIPE 3, 3, 1, 0, 11, 3, 2, 19, 6, 1, 27, 9, 0
    ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_STRIPE 4, 4, 1, 1, 12, 4, 0, 20, 6, 2, 28, 9, 1
    ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_STRIPE 5, 5, 1, 2, 13, 4, 1, 21, 7, 0, 29, 9, 2
    ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_STRIPE 6, 6, 2, 0, 14, 4, 2, 22, 7, 1, 30, 10, 0
    ROWSTAGE45_POST_REGFUSED_V5_SLOTHYPOST_STRIPE 7, 7, 2, 1, 15, 5, 0, 23, 7, 2, 31, 10, 1

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.endif

.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V4S_PROTO
    /*
     * Prototype v4s:
     *   v4 dataflow with row1 output0 kept in v31 instead of v24.  This
     *   isolates whether v4's tight live-register choice is hiding a
     *   stage45/post boundary cost before trying a larger Slothy region.
     */
    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #32
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #544
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #1056
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY

    ROWSTAGE45_POST_REGFUSED_V4S_STRIPE 0, 0, 0, 0, 8, 2, 2, 16, 5, 1, 24, 8, 0
    ROWSTAGE45_POST_REGFUSED_V4S_STRIPE 1, 1, 0, 1, 9, 3, 0, 17, 5, 2, 25, 8, 1
    ROWSTAGE45_POST_REGFUSED_V4S_STRIPE 2, 2, 0, 2, 10, 3, 1, 18, 6, 0, 26, 8, 2
    ROWSTAGE45_POST_REGFUSED_V4S_STRIPE 3, 3, 1, 0, 11, 3, 2, 19, 6, 1, 27, 9, 0
    ROWSTAGE45_POST_REGFUSED_V4S_STRIPE 4, 4, 1, 1, 12, 4, 0, 20, 6, 2, 28, 9, 1
    ROWSTAGE45_POST_REGFUSED_V4S_STRIPE 5, 5, 1, 2, 13, 4, 1, 21, 7, 0, 29, 9, 2
    ROWSTAGE45_POST_REGFUSED_V4S_STRIPE 6, 6, 2, 0, 14, 4, 2, 22, 7, 1, 30, 10, 0
    ROWSTAGE45_POST_REGFUSED_V4S_STRIPE 7, 7, 2, 1, 15, 5, 0, 23, 7, 2, 31, 10, 1

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.endif

.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V4P_PROTO
    /*
     * Prototype v4p:
     *   same dataflow as v4, but branchfold constants are consumed from one
     *   base setup per stage45 stripe and then advanced by the fixed
     *   k->k+8 stride.
     */
    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #32
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #544
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #1056
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY

    ROWSTAGE45_POST_REGFUSED_V4P_STRIPE 0, 0, 0, 0, 8, 2, 2, 16, 5, 1, 24, 8, 0
    ROWSTAGE45_POST_REGFUSED_V4P_STRIPE 1, 1, 0, 1, 9, 3, 0, 17, 5, 2, 25, 8, 1
    ROWSTAGE45_POST_REGFUSED_V4P_STRIPE 2, 2, 0, 2, 10, 3, 1, 18, 6, 0, 26, 8, 2
    ROWSTAGE45_POST_REGFUSED_V4P_STRIPE 3, 3, 1, 0, 11, 3, 2, 19, 6, 1, 27, 9, 0
    ROWSTAGE45_POST_REGFUSED_V4P_STRIPE 4, 4, 1, 1, 12, 4, 0, 20, 6, 2, 28, 9, 1
    ROWSTAGE45_POST_REGFUSED_V4P_STRIPE 5, 5, 1, 2, 13, 4, 1, 21, 7, 0, 29, 9, 2
    ROWSTAGE45_POST_REGFUSED_V4P_STRIPE 6, 6, 2, 0, 14, 4, 2, 22, 7, 1, 30, 10, 0
    ROWSTAGE45_POST_REGFUSED_V4P_STRIPE 7, 7, 2, 1, 15, 5, 0, 23, 7, 2, 31, 10, 1

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.endif

.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V4_PROTO
    /*
     * Prototype v4:
     *   closer to the forward NTT fused-scatter idea than v3b.  For each
     *   stage45 stripe, output0 and output8 from all three rows stay in
     *   registers and feed post directly; only output16/output24 use the
     *   stripe-local mini-buffer.  This doubles the direct-fed portion while
     *   keeping live ranges small enough for the normal production post helper.
     */
    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #32
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #544
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #1056
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY

    ROWSTAGE45_POST_REGFUSED_V4_STRIPE 0, 0, 0, 0, 8, 2, 2, 16, 5, 1, 24, 8, 0
    ROWSTAGE45_POST_REGFUSED_V4_STRIPE 1, 1, 0, 1, 9, 3, 0, 17, 5, 2, 25, 8, 1
    ROWSTAGE45_POST_REGFUSED_V4_STRIPE 2, 2, 0, 2, 10, 3, 1, 18, 6, 0, 26, 8, 2
    ROWSTAGE45_POST_REGFUSED_V4_STRIPE 3, 3, 1, 0, 11, 3, 2, 19, 6, 1, 27, 9, 0
    ROWSTAGE45_POST_REGFUSED_V4_STRIPE 4, 4, 1, 1, 12, 4, 0, 20, 6, 2, 28, 9, 1
    ROWSTAGE45_POST_REGFUSED_V4_STRIPE 5, 5, 1, 2, 13, 4, 1, 21, 7, 0, 29, 9, 2
    ROWSTAGE45_POST_REGFUSED_V4_STRIPE 6, 6, 2, 0, 14, 4, 2, 22, 7, 1, 30, 10, 0
    ROWSTAGE45_POST_REGFUSED_V4_STRIPE 7, 7, 2, 1, 15, 5, 0, 23, 7, 2, 31, 10, 1

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.endif

.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V3B_PROTO
    /*
     * Prototype v3b:
     *   partial register-fused row-stage45-to-post flow.  For each stage45
     *   stripe, keep output0 from all three rows in registers and send it
     *   directly to post; store only outputs 8/16/24 into a stripe-local
     *   mini-buffer for the existing post macro.  This avoids v3a's
     *   conservative register-safe post helper while still reducing
     *   row-stage45/post memory traffic.
     */
    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #32
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #544
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #1056
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY

    ROWSTAGE45_POST_REGFUSED_V3B_STRIPE 0, 0, 0, 0, 8, 2, 2, 16, 5, 1, 24, 8, 0
    ROWSTAGE45_POST_REGFUSED_V3B_STRIPE 1, 1, 0, 1, 9, 3, 0, 17, 5, 2, 25, 8, 1
    ROWSTAGE45_POST_REGFUSED_V3B_STRIPE 2, 2, 0, 2, 10, 3, 1, 18, 6, 0, 26, 8, 2
    ROWSTAGE45_POST_REGFUSED_V3B_STRIPE 3, 3, 1, 0, 11, 3, 2, 19, 6, 1, 27, 9, 0
    ROWSTAGE45_POST_REGFUSED_V3B_STRIPE 4, 4, 1, 1, 12, 4, 0, 20, 6, 2, 28, 9, 1
    ROWSTAGE45_POST_REGFUSED_V3B_STRIPE 5, 5, 1, 2, 13, 4, 1, 21, 7, 0, 29, 9, 2
    ROWSTAGE45_POST_REGFUSED_V3B_STRIPE 6, 6, 2, 0, 14, 4, 2, 22, 7, 1, 30, 10, 0
    ROWSTAGE45_POST_REGFUSED_V3B_STRIPE 7, 7, 2, 1, 15, 5, 0, 23, 7, 2, 31, 10, 1

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.endif

.ifdef INVNTT_USE_ROWSTAGE45_POST_REGFUSED_V3_PROTO
    /*
     * Prototype v3a:
     *   true register-fused row-stage45-to-post flow, but with branchfold
     *   constants consumed from the existing k32-major table using one base
     *   setup per stage45 stripe instead of one setup per post output.
     */
    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #32
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #544
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #1056
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY

    ROWSTAGE45_POST_REGFUSED_V3_STRIPE 0, 0, 0, 0, 8, 2, 2, 16, 5, 1, 24, 8, 0
    ROWSTAGE45_POST_REGFUSED_V3_STRIPE 1, 1, 0, 1, 9, 3, 0, 17, 5, 2, 25, 8, 1
    ROWSTAGE45_POST_REGFUSED_V3_STRIPE 2, 2, 0, 2, 10, 3, 1, 18, 6, 0, 26, 8, 2
    ROWSTAGE45_POST_REGFUSED_V3_STRIPE 3, 3, 1, 0, 11, 3, 2, 19, 6, 1, 27, 9, 0
    ROWSTAGE45_POST_REGFUSED_V3_STRIPE 4, 4, 1, 1, 12, 4, 0, 20, 6, 2, 28, 9, 1
    ROWSTAGE45_POST_REGFUSED_V3_STRIPE 5, 5, 1, 2, 13, 4, 1, 21, 7, 0, 29, 9, 2
    ROWSTAGE45_POST_REGFUSED_V3_STRIPE 6, 6, 2, 0, 14, 4, 2, 22, 7, 1, 30, 10, 0
    ROWSTAGE45_POST_REGFUSED_V3_STRIPE 7, 7, 2, 1, 15, 5, 0, 23, 7, 2, 31, 10, 1

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.endif

.ifdef INVNTT_USE_ROWSTAGE45_POST_MINIBUF_PROTO
    /*
     * Prototype v2:
     *   stage123 stripe scratch rows -> Slothy stage45 stripe into a 12-vector
     *   mini buffer -> existing production post macro.  This keeps the
     *   row-stage45/post processing stripe-local while avoiding the very
     *   serialized register-safe post helper from the first prototype.
     */
    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #32
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #544
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #1056
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY

    ROWSTAGE45_POST_MINIBUF_STRIPE 0, 0, 0, 0, 8, 2, 2, 16, 5, 1, 24, 8, 0
    ROWSTAGE45_POST_MINIBUF_STRIPE 1, 1, 0, 1, 9, 3, 0, 17, 5, 2, 25, 8, 1
    ROWSTAGE45_POST_MINIBUF_STRIPE 2, 2, 0, 2, 10, 3, 1, 18, 6, 0, 26, 8, 2
    ROWSTAGE45_POST_MINIBUF_STRIPE 3, 3, 1, 0, 11, 3, 2, 19, 6, 1, 27, 9, 0
    ROWSTAGE45_POST_MINIBUF_STRIPE 4, 4, 1, 1, 12, 4, 0, 20, 6, 2, 28, 9, 1
    ROWSTAGE45_POST_MINIBUF_STRIPE 5, 5, 1, 2, 13, 4, 1, 21, 7, 0, 29, 9, 2
    ROWSTAGE45_POST_MINIBUF_STRIPE 6, 6, 2, 0, 14, 4, 2, 22, 7, 1, 30, 10, 0
    ROWSTAGE45_POST_MINIBUF_STRIPE 7, 7, 2, 1, 15, 5, 0, 23, 7, 2, 31, 10, 1

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.endif

.ifdef INVNTT_USE_ROWSTAGE45_POST_FUSED_PROTO
    /*
     * Prototype fused inverse path:
     *   1. Materialize only the three stage123 stripe-major scratch rows.
     *   2. For each stage45 stripe j, compute row0/row1/row2 outputs into
     *      registers v16-v27.
     *   3. Emit the four post stripes fed by those row outputs directly from
     *      registers, avoiding the full row-buffer store and reload.
     *
     * This is intentionally opt-in.  The stage45-to-register block is still a
     * hand-scheduled/simple macro; once the dataflow wins, it should get its
     * own clean Slothy region.
     */
    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #32
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #544
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, sp, #1056
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY

    ROWSTAGE45_POST_FUSED_STRIPE 0, 0, 0, 0, 8, 2, 2, 16, 5, 1, 24, 8, 0
    ROWSTAGE45_POST_FUSED_STRIPE 1, 1, 0, 1, 9, 3, 0, 17, 5, 2, 25, 8, 1
    ROWSTAGE45_POST_FUSED_STRIPE 2, 2, 0, 2, 10, 3, 1, 18, 6, 0, 26, 8, 2
    ROWSTAGE45_POST_FUSED_STRIPE 3, 3, 1, 0, 11, 3, 2, 19, 6, 1, 27, 9, 0
    ROWSTAGE45_POST_FUSED_STRIPE 4, 4, 1, 1, 12, 4, 0, 20, 6, 2, 28, 9, 1
    ROWSTAGE45_POST_FUSED_STRIPE 5, 5, 1, 2, 13, 4, 1, 21, 7, 0, 29, 9, 2
    ROWSTAGE45_POST_FUSED_STRIPE 6, 6, 2, 0, 14, 4, 2, 22, 7, 1, 30, 10, 0
    ROWSTAGE45_POST_FUSED_STRIPE 7, 7, 2, 1, 15, 5, 0, 23, 7, 2, 31, 10, 1

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.endif

/* ---- original asm/slothy/invntt_opt.s:2924-2946: old gather input materialization fallback ---- */
.ifdef INVNTT_USE_OLD_GATHER
    add x2, sp, #32
    adr x3, inv_gather_offsets
    add x4, x1, #768
    mov x5, #96
1:
    ldrh w6, [x3], #2
    add x7, x2, x6
    ldr d1, [x1], #8
    ldr d2, [x4], #8
    mov v1.d[1], v2.d[0]
    str q1, [x7]
    subs x5, x5, #1
    b.ne 1b

    /* Step 2: inverse row NTT32, bit-reversed k32 input -> natural k32 output. */
    add x2, sp, #32
    RUN_INVNTT32_ROW
    add x2, sp, #544
    RUN_INVNTT32_ROW
    add x2, sp, #1056
    RUN_INVNTT32_ROW
.else

/* ---- original asm/slothy/invntt_opt.s:3251-3503: bench-only symbols for row/post component probes ---- */
.ifdef INVNTT_BENCH_STAGES
.global poly_invntt_bench_rows
.global _poly_invntt_bench_rows
poly_invntt_bench_rows:
_poly_invntt_bench_rows:
.ifdef INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH
    stp x30, x19, [sp, #-16]!
    mov x19, x0
    sub sp, sp, #INVNTT_STACK_SIZE
    adr x3, inv_consts
    ldr q0, [x3]

    add x3, x1, #0
    add x4, x1, #768
    add x2, x19, #0
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

    add x3, x1, #0
    add x4, x1, #768
    add x2, x19, #512
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

    add x3, x1, #0
    add x4, x1, #768
    add x2, x19, #1024
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.else
    stp x30, x0, [sp, #-16]!
    adr x3, inv_consts
    ldr q0, [x3]

    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #0
    DIRECT_STAGE123_ROW0
    RUN_INVNTT32_STAGE45_ROW

    ldr x0, [sp, #8]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #512
    DIRECT_STAGE123_ROW1
    RUN_INVNTT32_STAGE45_ROW

    ldr x0, [sp, #8]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #1024
    DIRECT_STAGE123_ROW2
    RUN_INVNTT32_STAGE45_ROW

    ldp x30, x0, [sp], #16
    ret
.endif

.global poly_invntt_bench_row0
.global _poly_invntt_bench_row0
poly_invntt_bench_row0:
_poly_invntt_bench_row0:
.ifdef INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH
    stp x30, x19, [sp, #-16]!
    mov x19, x0
    sub sp, sp, #INVNTT_STACK_SIZE
    adr x3, inv_consts
    ldr q0, [x3]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x19, #0
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0
    RUN_INVNTT32_STAGE45_SCRATCH_ROW
    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.else
    stp x30, x0, [sp, #-16]!
    adr x3, inv_consts
    ldr q0, [x3]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #0
    DIRECT_STAGE123_ROW0
    RUN_INVNTT32_STAGE45_ROW
    ldp x30, x0, [sp], #16
    ret
.endif

.global poly_invntt_bench_row1
.global _poly_invntt_bench_row1
poly_invntt_bench_row1:
_poly_invntt_bench_row1:
.ifdef INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH
    stp x30, x19, [sp, #-16]!
    mov x19, x0
    sub sp, sp, #INVNTT_STACK_SIZE
    adr x3, inv_consts
    ldr q0, [x3]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x19, #0
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1
    RUN_INVNTT32_STAGE45_SCRATCH_ROW
    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.else
    stp x30, x0, [sp, #-16]!
    adr x3, inv_consts
    ldr q0, [x3]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #0
    DIRECT_STAGE123_ROW1
    RUN_INVNTT32_STAGE45_ROW
    ldp x30, x0, [sp], #16
    ret
.endif

.global poly_invntt_bench_row2
.global _poly_invntt_bench_row2
poly_invntt_bench_row2:
_poly_invntt_bench_row2:
.ifdef INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH
    stp x30, x19, [sp, #-16]!
    mov x19, x0
    sub sp, sp, #INVNTT_STACK_SIZE
    adr x3, inv_consts
    ldr q0, [x3]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x19, #0
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2
    RUN_INVNTT32_STAGE45_SCRATCH_ROW
    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x19, [sp], #16
    ret
.else
    stp x30, x0, [sp, #-16]!
    adr x3, inv_consts
    ldr q0, [x3]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #0
    DIRECT_STAGE123_ROW2
    RUN_INVNTT32_STAGE45_ROW
    ldp x30, x0, [sp], #16
    ret
.endif

.global poly_invntt_bench_post
.global _poly_invntt_bench_post
poly_invntt_bench_post:
_poly_invntt_bench_post:
    adr x3, inv_consts
    ldr q0, [x3]
    ldr q15, [x3, #16]
    add x8, x1, #0
    add x9, x1, #512
    add x10, x1, #1024
.ifdef INVNTT_USE_POST_BRANCHFOLD
    adr x3, inv_branchfold_vecs
.else
    adr x3, inv_untwist_vecs
.endif
.ifdef INVNTT_USE_POST_FASTSCALE
    // v15.h[2:3] contain ZMINUSZ5INV/192 and its precompute.
.endif
    add x11, x0, #0
    add x12, x0, #512
    add x13, x0, #256
    RUN_FUSED_POST_LOOP 5
    ret

.global poly_invntt_bench_post_dft3_raw
.global _poly_invntt_bench_post_dft3_raw
poly_invntt_bench_post_dft3_raw:
_poly_invntt_bench_post_dft3_raw:
    adr x3, inv_consts
    ldr q0, [x3]
    mov x2, x0
    add x8, x1, #0
    add x9, x1, #512
    add x10, x1, #1024
    mov x5, #32
6:
    POST_DFT3_STRIPE 0
    subs x5, x5, #1
    b.ne 6b
    ret

.global poly_invntt_bench_post_dft3_reduce
.global _poly_invntt_bench_post_dft3_reduce
poly_invntt_bench_post_dft3_reduce:
_poly_invntt_bench_post_dft3_reduce:
    adr x3, inv_consts
    ldr q0, [x3]
    mov x2, x0
    add x8, x1, #0
    add x9, x1, #512
    add x10, x1, #1024
    mov x5, #32
7:
    POST_DFT3_STRIPE 1
    subs x5, x5, #1
    b.ne 7b
    ret

.global poly_invntt_bench_post_untwist
.global _poly_invntt_bench_post_untwist
poly_invntt_bench_post_untwist:
_poly_invntt_bench_post_untwist:
    adr x3, inv_consts
    ldr q0, [x3]
    adr x3, inv_untwist_vecs
    mov x2, x0
    mov x5, #96
8:
    POST_UNTWIST_STRIPE
    subs x5, x5, #1
    b.ne 8b
    ret

.global poly_invntt_bench_post_finalmerge
.global _poly_invntt_bench_post_finalmerge
poly_invntt_bench_post_finalmerge:
_poly_invntt_bench_post_finalmerge:
    adr x3, inv_consts
    ldr q0, [x3]
    ldr q15, [x3, #16]
    mov x8, x1
    add x11, x0, #0
    add x12, x0, #512
    add x13, x0, #256
    mov x5, #10
9:
    POST_FINAL_MERGE_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    POST_FINAL_MERGE_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
    POST_FINAL_MERGE_STRIPE x12, 16, 784, x13, 16, 784, x11, 16, 784
    add x11, x11, #24
    add x12, x12, #24
    add x13, x13, #24
    subs x5, x5, #1
    b.ne 9b
    POST_FINAL_MERGE_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    POST_FINAL_MERGE_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
    ret
.endif

/* ---- original asm/slothy/invntt_opt.s:3511-3524: old gather offset table ---- */
.align 4
inv_gather_offsets:
    .hword      0,   1200,    864,     16,   1216,    880,     32,   1232
    .hword    896,     48,   1248,    912,     64,   1264,    928,     80
    .hword   1280,    944,     96,   1296,    960,    112,   1312,    976
    .hword    128,   1328,    992,    144,   1344,   1008,    160,   1360
    .hword    512,    176,   1376,    528,    192,   1392,    544,    208
    .hword   1408,    560,    224,   1424,    576,    240,   1440,    592
    .hword    256,   1456,    608,    272,   1472,    624,    288,   1488
    .hword    640,    304,   1504,    656,    320,   1520,    672,    336
    .hword   1024,    688,    352,   1040,    704,    368,   1056,    720
    .hword    384,   1072,    736,    400,   1088,    752,    416,   1104
    .hword    768,    432,   1120,    784,    448,   1136,    800,    464
    .hword   1152,    816,    480,   1168,    832,    496,   1184,    848


/*
 * Clean symbolic Slothy source for the NTRU+768 inverse Good-Thomas NTT.
 *
 * Production output is asm/slothy/invntt_opt.s and is included by
 * asm/inv_my_ntt.s.  This file documents the register-allocation source for
 * the inverse row kernel and the surrounding layout contract.
 *
 * Full inverse contract:
 *
 *   input layout: branch-major quartic block-major NTT output
 *     in[branch*384 + 4*physical_j + lane]
 *
 *   gather mapping into three rows of 32 vectors:
 *     k3     = (2*physical_j) mod 3
 *     k32_br = (11*physical_j) mod 32
 *     row[k3][k32_br] =
 *       [branch0 lane0..3, branch1 lane0..3]
 *
 *   inverse row NTT32:
 *     input order  = bit-reversed k32 order
 *     output order = natural k32 order
 *     root         = omega96^{-3}
 *     scale        = 32
 *
 *   inverse DFT3:
 *     runs across k3 for each natural k32
 *     leaves scale factor 3 unnormalized
 *
 *   untwist:
 *     branch b at logical index k is multiplied by F_b^k
 *
 *   final merge:
 *     removes the total factor 96.  The normal constants are
 *       1/192 = -18 mod q
 *       1/96  = -36 mod q
 *       ZMINUSZ5INV = 1634 mod q
 *
 * Table representation:
 *   Forward C reference tables in ntt.c are Montgomery-form because fqmul()
 *   consumes Montgomery constants.  The assembly tables in invntt_opt.s are
 *   normal centered multipliers paired with sqrdmulh precompute constants;
 *   they are not Montgomery-form tables.
 */

row_base .req x2
tbl_ptr  .req x3
count    .req x5
lo_off   .req w6
hi_off   .req w7
lo_ptr   .req x8
hi_ptr   .req x9
mul_w    .req w10
pre_w    .req w11

/*
 * Symbolic row-butterfly body.  Slothy should allocate the vector registers
 * inside this body while x8/x9/x10/x11 and v0 remain fixed by the table loop.
 * The surrounding table loop is intentionally outside the Slothy region
 * because this Slothy target model does not parse ldrh/ldrsh post-increment
 * table loads.
 *
 * v0.h[0] = q = 3457.
 * v0.h[1] = Barrett reduction multiplier.
 */
    .global invntt32_8way_symbolic
invntt32_8way_symbolic:
    adr tbl_ptr, invntt32_butterflies
    mov count, #80
invntt32_loop:
    ldrh  lo_off, [tbl_ptr], #2
    ldrh  hi_off, [tbl_ptr], #2
    ldrsh mul_w,  [tbl_ptr], #2
    ldrsh pre_w,  [tbl_ptr], #2
    add lo_ptr, row_base, lo_off
    add hi_ptr, row_base, hi_off
        slothy_start_invntt32:
                                               // Instructions:    17
                                               // Expected cycles: 31
                                               // Expected IPC:    0.55
                                               //
                                               // Cycle bound:     31.0
                                               // IPC bound:       0.55
                                               //
                                               // Wall time:     0.04s
                                               // User time:     0.04s
                                               //
                                               // ------ cycle (expected) ------>
                                               // 0                        25
                                               // |------------------------|-----
        ldr q19, [x9]                          // *..............................
        dup v24.8H, w11                        // ..*............................
        dup v15.8H, w10                        // ...*...........................
        sqrdmulh v18.8H, v19.8H, v24.8H        // .....*.........................
        mul v3.8H, v19.8H, v15.8H              // ......*........................
        ldr q14, [x8]                          // .......*.......................
        mls v3.8H, v18.8H, v0.H[0]             // ..........*....................
        add v28.8H, v14.8H, v3.8H              // ..............*................
        sub v3.8H, v14.8H, v3.8H               // ...............*...............
        sqdmulh v11.8H, v28.8H, v0.H[1]        // .................*.............
        sqdmulh v20.8H, v3.8H, v0.H[1]         // ..................*............
        srshr v10.8H, v11.8H, #11              // .....................*.........
        srshr v1.8H, v20.8H, #11               // ......................*........
        mls v28.8H, v10.8H, v0.H[0]            // ........................*......
        mls v3.8H, v1.8H, v0.H[0]              // .........................*.....
        str q28, [x8]                          // ............................*..
        str q3, [x9]                           // ..............................*

                                                             // ------ cycle (expected) ------>
                                                             // 0                        25
                                                             // |------------------------|-----
        // ldr Q<lo>, [x8]                                   // .......*.......................
        // ldr Q<hi>, [x9]                                   // *..............................
        // dup V<m>.8h, w10                                  // ...*...........................
        // dup V<p>.8h, w11                                  // ..*............................
        // sqrdmulh V<qhat>.8h, V<hi>.8h, V<p>.8h            // .....*.........................
        // mul      V<prod>.8h, V<hi>.8h, V<m>.8h            // ......*........................
        // mls      V<prod>.8h, V<qhat>.8h, v0.h[0]          // ..........*....................
        // add      V<sum>.8h, V<lo>.8h, V<prod>.8h          // ..............*................
        // sub      V<diff>.8h, V<lo>.8h, V<prod>.8h         // ...............*...............
        // sqdmulh  V<sum_red>.8h, V<sum>.8h, v0.h[1]        // .................*.............
        // srshr    V<sum_red>.8h, V<sum_red>.8h, #11        // .....................*.........
        // mls      V<sum>.8h, V<sum_red>.8h, v0.h[0]        // ........................*......
        // sqdmulh  V<diff_red>.8h, V<diff>.8h, v0.h[1]      // ..................*............
        // srshr    V<diff_red>.8h, V<diff_red>.8h, #11      // ......................*........
        // mls      V<diff>.8h, V<diff_red>.8h, v0.h[0]      // .........................*.....
        // str Q<sum>, [x8]                                  // ............................*..
        // str Q<diff>, [x9]                                 // ..............................*

        slothy_end_invntt32:

    subs count, count, #1
    b.ne invntt32_loop
    ret

.unreq row_base
.unreq tbl_ptr
.unreq count
.unreq lo_off
.unreq hi_off
.unreq lo_ptr
.unreq hi_ptr
.unreq mul_w
.unreq pre_w

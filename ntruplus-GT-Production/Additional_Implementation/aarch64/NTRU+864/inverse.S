/* Public AAPCS control wrappers. Arithmetic is in Slothy-allocated leaf cores.
 * Save d8-d15 once per public operation; x19-x28 hold state across core calls.
 * No scalar secret arithmetic except the fixed-length BaseInv failure scan,
 * whose result is a return value, never a branch.
 */
#ifdef __APPLE__
#define C(name) _##name
#else
#define C(name) name
#endif
.text
.macro SAVE_PUBLIC
    stp x29, x30, [sp, #-160]!
    mov x29, sp
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]
    stp x23, x24, [sp, #48]
    stp x25, x26, [sp, #64]
    stp x27, x28, [sp, #80]
    stp d8, d9, [sp, #96]
    stp d10, d11, [sp, #112]
    stp d12, d13, [sp, #128]
    stp d14, d15, [sp, #144]
.endm
.macro RESTORE_PUBLIC
    /* Erase volatile SIMD state, including high halves of v8-v15. */
    movi v0.16b, #0
    movi v1.16b, #0
    movi v2.16b, #0
    movi v3.16b, #0
    movi v4.16b, #0
    movi v5.16b, #0
    movi v6.16b, #0
    movi v7.16b, #0
    movi v8.16b, #0
    movi v9.16b, #0
    movi v10.16b, #0
    movi v11.16b, #0
    movi v12.16b, #0
    movi v13.16b, #0
    movi v14.16b, #0
    movi v15.16b, #0
    movi v16.16b, #0
    movi v17.16b, #0
    movi v18.16b, #0
    movi v19.16b, #0
    movi v20.16b, #0
    movi v21.16b, #0
    movi v22.16b, #0
    movi v23.16b, #0
    movi v24.16b, #0
    movi v25.16b, #0
    movi v26.16b, #0
    movi v27.16b, #0
    movi v28.16b, #0
    movi v29.16b, #0
    movi v30.16b, #0
    movi v31.16b, #0
    ldp d8, d9, [sp, #96]
    ldp d10, d11, [sp, #112]
    ldp d12, d13, [sp, #128]
    ldp d14, d15, [sp, #144]
    ldp x19, x20, [sp, #16]
    ldp x21, x22, [sp, #32]
    ldp x23, x24, [sp, #48]
    ldp x25, x26, [sp, #64]
    ldp x27, x28, [sp, #80]
    ldp x29, x30, [sp], #160
    ret
.endm
.macro COPY_TRIPLE dst, src
    ldp x8, x9, [\src, #0]
    stp x8, x9, [\dst, #0]
    ldp x8, x9, [\src, #16]
    stp x8, x9, [\dst, #16]
    ldp x8, x9, [\src, #32]
    stp x8, x9, [\dst, #32]
.endm

.p2align 4
.global C(baseinv_asm)
C(baseinv_asm):
    SAVE_PUBLIC
    mov x19, x0                 // output; exact out=in is legal
    mov x20, x1
    mov x21, x2                 // 36 zR vectors, advanced in tile order
    mov x22, x3                 // den[12][3][8]: 576 bytes, CALLER-OWNED
    add x23, x3, #576           // prefix[12][3][8]: 576 bytes
    add x24, x3, #1152          // running inverse[3][8]: 48 bytes
    mov x25, #0                // chain
    mov x27, x19
    mov x28, x20
    // Repeated numerator leaf ABI: v30=q and v31=-q^-1 mod 2^16.
    mov w8, #3457
    dup v30.8h, w8
    mov w8, #-12929
    dup v31.8h, w8
.Lbinv_chain:
    mov x26, #0                // step
.Lbinv_num:
    mov x0, x27
    mov x1, x28
    mov x2, x21
    mov x8, #48
    madd x3, x26, x8, x22
    add x3, x3, x25, lsl #4
    bl C(binv_num_pair)
    add x27, x27, #96
    add x28, x28, #96
    add x21, x21, #32
    add x26, x26, #2
    cmp x26, #12
    b.ne .Lbinv_num
    add x25, x25, #1
    cmp x25, #3
    b.ne .Lbinv_chain
    COPY_TRIPLE x23, x22
    mov x25, #1
.Lbinv_prefix:
    mov x8, #48
    madd x0, x25, x8, x23
    sub x1, x0, #48
    madd x2, x25, x8, x22
    bl C(binv_prefix3)
    add x25, x25, #1
    cmp x25, #12
    b.ne .Lbinv_prefix
    // Prefix values lie inside (-q,q), so only integer zero represents zero.
    // Branch-free failure: if any of the 24 lanes is zero, all 24 running
    // inverses are zeroed after the inversion, so every recovered denominator
    // and every output coefficient becomes zero -- the cleared output the
    // contract promises -- on the same instruction path.  The scan overlaps
    // the inversion.  x20 (the input pointer) is dead from here and carries
    // the flag.
    add x9, x23, #528
    ldp q0, q1, [x9]
    ldr q2, [x9, #32]
    cmeq v0.8h, v0.8h, #0
    cmeq v1.8h, v1.8h, #0
    cmeq v2.8h, v2.8h, #0
    orr v0.16b, v0.16b, v1.16b
    orr v0.16b, v0.16b, v2.16b
    umaxv h0, v0.8h
    umov w20, v0.h[0]           // 0xffff on failure, 0 on success
    mov x0, x24
    add x1, x23, #528
    bl C(binv_inverse3)
    dup v3.8h, w20
    ldp q0, q1, [x24]
    ldr q2, [x24, #32]
    bic v0.16b, v0.16b, v3.16b
    bic v1.16b, v1.16b, v3.16b
    bic v2.16b, v2.16b, v3.16b
    stp q0, q1, [x24]
    str q2, [x24, #32]
    mov x25, #11
.Lbinv_recover:
    mov x8, #48
    madd x0, x25, x8, x22
    madd x1, x25, x8, x23
    sub x1, x1, #48
    mov x2, x24
    mov x3, x0                 // den overwrite is safe: core loads first
    bl C(binv_recover3)
    subs x25, x25, #1
    b.ne .Lbinv_recover
    COPY_TRIPLE x22, x24
    mov x25, #0
    mov x27, x19
    // Middle batch kernels clobber volatile SIMD state; reload the finish constants.
    mov w8, #3457
    dup v30.8h, w8
    mov w8, #-12929
    dup v31.8h, w8
.Lbinv_finish_chain:
    mov x26, #0
.Lbinv_finish:
    mov x0, x27
    mov x8, #48
    madd x1, x26, x8, x22
    add x1, x1, x25, lsl #4
    bl C(binv_finish_tile)
    add x27, x27, #48
    add x26, x26, #1
    cmp x26, #12
    b.ne .Lbinv_finish
    add x25, x25, #1
    cmp x25, #3
    b.ne .Lbinv_finish_chain
    and w0, w20, #1
    RESTORE_PUBLIC

.p2align 4
#ifndef BASEINV_ONLY
.global C(basemul_rinv_asm)
C(basemul_rinv_asm):
    SAVE_PUBLIC
    mov x19, x0
    mov x20, x1
    mov x21, x2
    mov x22, x3
    mov x23, #36
.Lbm_tile:
    mov x0, x19
    mov x1, x20
    mov x2, x21
    mov x3, x22
    bl C(bm_rinv_tile)
    add x19, x19, #48
    add x20, x20, #48
    add x21, x21, #48
    add x22, x22, #16
    subs x23, x23, #1
    b.ne .Lbm_tile
    RESTORE_PUBLIC

.p2align 4
.global C(invntt_ternary_asm)
C(invntt_ternary_asm):
    SAVE_PUBLIC
    mov x19, x0
    mov x20, x1
    mov x21, x2
    mov x22, x3
    mov x23, x4
    mov x24, x5
    mov x25, x6                 // scratch, 1792 bytes, CALLER-OWNED
    // No initialization: the padding lanes never reach an output.  What stood
    // here cleared 256 bytes at sp + 1536, which is the caller's frame -- the
    // scratch has been caller-owned in x25 since P80.  Both the old and the
    // new consumer were measured insensitive to the padding's contents.
    // Fully unrolled i9 dispatch.  The loop bounds are fixed, so all twelve
    // address quadruples are compile-time constants; the madd chains and the
    // loop control disappear.
    mov x0, x25
    add x1, x25, #1536
    mov x2, x20
    mov x3, x21
    bl C(packed_i9)
    add x0, x25, #128
    add x1, x25, #1664
    add x2, x20, #48
    add x3, x21, #288
    bl C(packed_i9)
    add x0, x25, #512
    add x1, x25, #1538
    add x2, x20, #16
    mov x3, x21
    bl C(packed_i9)
    add x0, x25, #640
    add x1, x25, #1666
    add x2, x20, #64
    add x3, x21, #288
    bl C(packed_i9)
    add x0, x25, #1024
    add x1, x25, #1540
    add x2, x20, #32
    mov x3, x21
    bl C(packed_i9)
    add x0, x25, #1152
    add x1, x25, #1668
    add x2, x20, #80
    add x3, x21, #288
    bl C(packed_i9)
    add x0, x25, #8
    add x1, x25, #1542
    add x2, x20, #864
    add x3, x21, #576
    bl C(packed_i9)
    add x0, x25, #136
    add x1, x25, #1670
    add x2, x20, #912
    add x3, x21, #864
    bl C(packed_i9)
    add x0, x25, #520
    add x1, x25, #1544
    add x2, x20, #880
    add x3, x21, #576
    bl C(packed_i9)
    add x0, x25, #648
    add x1, x25, #1672
    add x2, x20, #928
    add x3, x21, #864
    bl C(packed_i9)
    add x0, x25, #1032
    add x1, x25, #1546
    add x2, x20, #896
    add x3, x21, #576
    bl C(packed_i9)
    add x0, x25, #1160
    add x1, x25, #1674
    add x2, x20, #944
    add x3, x21, #864
    bl C(packed_i9)
    /* Three paired main calls.  Each takes the two P8 blocks holding the same
     * j-half of two components -- or component 2's two j-halves -- and
     * rewrites them in place as eight-channel banks.  The route below reads
     * Q-bases (0,16,64) for top0 and (32,48,80) for top1, which are exactly
     * these six 256-byte blocks. */
    mov x2, #0
    mov x3, x22
    mov x4, x23
    mov x0, x25
    add x1, x25, #512
    bl C(invntt16_paired_asm)
    mov x2, #0
    mov x3, x22
    mov x4, x23
    add x0, x25, #256
    add x1, x25, #768
    bl C(invntt16_paired_asm)
    mov x2, #0
    mov x3, x22
    mov x4, x23
    add x0, x25, #1024
    add x1, x25, #1280
    bl C(invntt16_paired_asm)
    /* j = 8 writes its exact six bytes per group straight to the natural
     * address: one STR W plus one STRH, no lane ST3. */
    mov x0, x19
    add x1, x25, #1536
    mov x2, #0
    mov x3, x22
    mov x4, x24
    bl C(invntt_tail_direct_asm)
    /* Rows 0..7 leave as full-vector ST3.4h in natural component-interleaved
     * order with the raw-to-ternary reduction folded in, so no separate
     * crepmod3 pass follows. */
    mov x0, x19
    mov x1, x25
    bl C(invntt_route_asm)
    RESTORE_PUBLIC
#endif

/* Public AAPCS control wrappers. Arithmetic is in Slothy-allocated leaf cores.
 * Save d8-d15 once per public operation; x19-x28 hold state across core calls.
 * No scalar secret arithmetic except the fixed-length BaseInv failure scan.
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

.global C(gt864_tobytes_full_asm)
C(gt864_tobytes_full_asm):
    mov w5, #0
    b .Lfused_byte_public
.global C(gt864_tobytes_small_asm)
C(gt864_tobytes_small_asm):
    mov w5, #1
.Lfused_byte_public:
    SAVE_PUBLIC
    sub sp, sp, #432
    mov x19, x0
    mov x20, x1
    mov x21, x2
    mov x22, x3
    mov x23, x4
    mov x25, x5
    mov x26, #0
.Lfused_top:
    mov x27, #0
.Lfused_saved_pair:
    mov x9, #864
    madd x10, x26, x9, x20
    mov x11, #0
    mov x9, #16
    cbz x27, .Lfused_offsets
    mov x11, #32
    mov x9, #432
.Lfused_offsets:
    add x1, x10, x11
    add x2, x10, x9
    mov x9, #216
    mov x0, sp
    madd x0, x27, x9, x0
    mov x3, x21
    mov x4, x22
    cbnz x25, .Lfused_saved_small
    bl C(byte_pair_block)
    b .Lfused_saved_done
.Lfused_saved_small:
    bl C(byte_pair_small)
.Lfused_saved_done:
    add x27, x27, #1
    cmp x27, #2
    b.ne .Lfused_saved_pair
    mov x9, #864
    madd x10, x26, x9, x20
    add x1, x10, #448
    add x2, x10, #464
    mov x9, #648
    madd x0, x26, x9, x19
    mov x3, x21
    mov x4, x22
    mov x6, sp
    add x7, sp, #216
    mov x9, x23
    cbnz x25, .Lfused_stream_small
    bl C(pair_merge_full)
    b .Lfused_stream_done
.Lfused_stream_small:
    bl C(pair_merge_small)
.Lfused_stream_done:
    add x26, x26, #1
    cmp x26, #2
    b.ne .Lfused_top
    mov x9, sp
    mov x10, #27
.Lfused_wipe:
    stp xzr, xzr, [x9], #16
    subs x10, x10, #1
    b.ne .Lfused_wipe
    mov x0, x19
    add sp, sp, #432
    RESTORE_PUBLIC
byte_wrapper_end:

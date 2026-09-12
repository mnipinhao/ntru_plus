/* P9 public wrappers around the generated input-once cores.
 *
 * The generated C cores obey AAPCS64 themselves.  These wrappers additionally
 * erase every SIMD register before returning, while preserving the low halves
 * of v8-v15 as required by AAPCS64.  There is no coefficient scratch.
 */
#ifdef __APPLE__
#define C(name) _##name
#else
#define C(name) name
#endif

.text

.macro P9_PUBLIC name, inner
.p2align 4
.global C(\name)
C(\name):
    stp x29, x30, [sp, #-80]!
    mov x29, sp
    stp d8, d9, [sp, #16]
    stp d10, d11, [sp, #32]
    stp d12, d13, [sp, #48]
    stp d14, d15, [sp, #64]
    bl C(\inner)
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
    ldp d8, d9, [sp, #16]
    ldp d10, d11, [sp, #32]
    ldp d12, d13, [sp, #48]
    ldp d14, d15, [sp, #64]
    ldp x29, x30, [sp], #80
    ret
.endm

#ifdef P9_BUILD_FULL
P9_PUBLIC gt864_p9_tobytes_full_asm, gt864_p9_input_once_full_inner
#endif
#ifdef P9_BUILD_SMALL
P9_PUBLIC gt864_p9_tobytes_small_asm, gt864_p9_input_once_small_inner
#endif

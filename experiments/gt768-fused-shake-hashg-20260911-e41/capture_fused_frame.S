#ifdef __APPLE__
#define SYM_I(x) _##x
#define SYM(x) SYM_I(x)
#else
#define SYM(x) x
#endif
.text
.p2align 2
.global SYM(capture_fused_frame)
#ifndef __APPLE__
.type SYM(capture_fused_frame), %function
#endif
SYM(capture_fused_frame):
    stp x19, x30, [sp, #-16]!
    mov x19, x3
    bl SYM(ntruplus_hash_g_fused_aarch64)
    // Capture all caller-saved state registers before using any as scratch.
    stp x0, x1, [x19, #0]
    stp x2, x3, [x19, #16]
    stp x4, x5, [x19, #32]
    stp x6, x7, [x19, #48]
    stp x8, x9, [x19, #64]
    stp x10, x11, [x19, #80]
    stp x12, x13, [x19, #96]
    stp x14, x15, [x19, #112]
    stp x16, x17, [x19, #128]
    // Read the returned callee frame before any other function call.
    ldp x9, x10, [sp, #-144]
    stp x9, x10, [x19, #144]
    ldp x9, x10, [sp, #-128]
    stp x9, x10, [x19, #160]
    ldp x9, x10, [sp, #-112]
    stp x9, x10, [x19, #176]
    ldp x9, x10, [sp, #-96]
    stp x9, x10, [x19, #192]
    ldp x9, x10, [sp, #-80]
    stp x9, x10, [x19, #208]
    ldp x9, x10, [sp, #-64]
    stp x9, x10, [x19, #224]
    ldp x9, x10, [sp, #-48]
    stp x9, x10, [x19, #240]
    ldp x9, x10, [sp, #-32]
    stp x9, x10, [x19, #256]
    ldp x9, x10, [sp, #-16]
    stp x9, x10, [x19, #272]
    ldp x19, x30, [sp], #16
    ret
#ifndef __APPLE__
.size SYM(capture_fused_frame), .-SYM(capture_fused_frame)
.section .note.GNU-stack,"",%progbits
#endif

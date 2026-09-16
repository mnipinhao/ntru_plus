#ifndef BYTE_TARGET
#define BYTE_TARGET gt864_tobytes_full_asm
#endif
#ifdef __APPLE__
#define C_JOIN(name) _##name
#define C(name) C_JOIN(name)
#else
#define C(name) name
#endif
.text
.global C(probe_bytes)
C(probe_bytes):
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
    mov x19, #19
    mov x20, #20
    mov x21, #21
    mov x22, #22
    mov x23, #23
    mov x24, #24
    mov x25, #25
    mov x26, #26
    mov x27, #27
    mov x28, #28
    mov x8, #108
    fmov d8, x8
    mov x8, #109
    fmov d9, x8
    mov x8, #110
    fmov d10, x8
    mov x8, #111
    fmov d11, x8
    mov x8, #112
    fmov d12, x8
    mov x8, #113
    fmov d13, x8
    mov x8, #114
    fmov d14, x8
    mov x8, #115
    fmov d15, x8
    bl C(BYTE_TARGET)
    mov w0, #0
    cmp x19, #19
    cset w8, ne
    orr w0, w0, w8, lsl #8
    cmp x20, #20
    cset w8, ne
    orr w0, w0, w8, lsl #8
    cmp x21, #21
    cset w8, ne
    orr w0, w0, w8, lsl #8
    cmp x22, #22
    cset w8, ne
    orr w0, w0, w8, lsl #8
    cmp x23, #23
    cset w8, ne
    orr w0, w0, w8, lsl #8
    cmp x24, #24
    cset w8, ne
    orr w0, w0, w8, lsl #8
    cmp x25, #25
    cset w8, ne
    orr w0, w0, w8, lsl #8
    cmp x26, #26
    cset w8, ne
    orr w0, w0, w8, lsl #8
    cmp x27, #27
    cset w8, ne
    orr w0, w0, w8, lsl #8
    cmp x28, #28
    cset w8, ne
    orr w0, w0, w8, lsl #8
    fmov x9, d8
    cmp x9, #108
    cset w8, ne
    orr w0, w0, w8, lsl #8
    fmov x9, d9
    cmp x9, #109
    cset w8, ne
    orr w0, w0, w8, lsl #8
    fmov x9, d10
    cmp x9, #110
    cset w8, ne
    orr w0, w0, w8, lsl #8
    fmov x9, d11
    cmp x9, #111
    cset w8, ne
    orr w0, w0, w8, lsl #8
    fmov x9, d12
    cmp x9, #112
    cset w8, ne
    orr w0, w0, w8, lsl #8
    fmov x9, d13
    cmp x9, #113
    cset w8, ne
    orr w0, w0, w8, lsl #8
    fmov x9, d14
    cmp x9, #114
    cset w8, ne
    orr w0, w0, w8, lsl #8
    fmov x9, d15
    cmp x9, #115
    cset w8, ne
    orr w0, w0, w8, lsl #8
    cmp sp, x29
    cset w8, ne
    orr w0, w0, w8, lsl #8
    sub x9, sp, #816
    mov x10, #41
    mov x11, #0
.Lprobe_bytes_wipe:
    ldp x8, x12, [x9], #16
    orr x11, x11, x8
    orr x11, x11, x12
    subs x10, x10, #1
    b.ne .Lprobe_bytes_wipe
    cmp x11, #0
    cset w8, ne
    orr w0, w0, w8, lsl #9
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

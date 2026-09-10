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

/* Exact source extraction from gt864_native_public.S at commit 1558c548. */
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
    mov w0, #0
    b .Lbinv_wipe
.Lbinv_fail:

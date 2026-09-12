/* Exact source extraction from gt864_native_public.S at commit 1558c548. */
.Lbinv_chain:
    mov x26, #0
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

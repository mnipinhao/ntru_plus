.text
.global binv_num_pair_baseline
binv_num_pair_baseline:
    // P1 functional baseline for one adjacent pair.  This intentionally keeps
    // the two existing calls so the new pair kernel has a concrete baseline.
    stp x29, x30, [sp, #-48]!
    mov x29, sp
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]
    mov x19, x0
    mov x20, x1
    mov x21, x2
    mov x22, x3
    bl binv_num_tile
    add x0, x19, #48
    add x1, x20, #48
    add x2, x21, #16
    add x3, x22, #48
    bl binv_num_tile
    ldp x19, x20, [sp, #16]
    ldp x21, x22, [sp, #32]
    ldp x29, x30, [sp], #48
    ret

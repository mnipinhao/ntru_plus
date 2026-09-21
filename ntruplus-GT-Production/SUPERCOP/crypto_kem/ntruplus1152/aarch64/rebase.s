.text
.p2align 4
.global p65_rebase
p65_rebase:
    mov x2, #18
.Lp65_group:
    ld1 {v0.8h - v3.8h}, [x0]
    add x3, x0, #1152
    ld1 {v4.8h - v7.8h}, [x3]
    trn1 v8.8h, v0.8h, v1.8h
    trn2 v9.8h, v0.8h, v1.8h
    trn1 v10.8h, v2.8h, v3.8h
    trn2 v11.8h, v2.8h, v3.8h
    trn1 v12.8h, v4.8h, v5.8h
    trn2 v13.8h, v4.8h, v5.8h
    trn1 v14.8h, v6.8h, v7.8h
    trn2 v15.8h, v6.8h, v7.8h
    trn1 v16.4s, v8.4s, v10.4s
    trn2 v18.4s, v8.4s, v10.4s
    trn1 v17.4s, v9.4s, v11.4s
    trn2 v19.4s, v9.4s, v11.4s
    trn1 v20.4s, v12.4s, v14.4s
    trn2 v22.4s, v12.4s, v14.4s
    trn1 v21.4s, v13.4s, v15.4s
    trn2 v23.4s, v13.4s, v15.4s
    trn1 v0.2d, v16.2d, v20.2d
    trn2 v4.2d, v16.2d, v20.2d
    trn1 v1.2d, v17.2d, v21.2d
    trn2 v5.2d, v17.2d, v21.2d
    trn1 v2.2d, v18.2d, v22.2d
    trn2 v6.2d, v18.2d, v22.2d
    trn1 v3.2d, v19.2d, v23.2d
    trn2 v7.2d, v19.2d, v23.2d
    st1 {v0.8h - v3.8h}, [x1], #64
    st1 {v4.8h - v7.8h}, [x1], #64
    add x0, x0, #64
    subs x2, x2, #1
    b.ne .Lp65_group
    ret
.section .note.GNU-stack,"",%progbits

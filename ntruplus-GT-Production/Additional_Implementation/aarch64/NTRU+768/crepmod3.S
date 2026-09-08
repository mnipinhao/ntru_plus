/* Center modulo q then modulo 3; input [-3456,3456], output {-1,0,1}.
 * Two-pointer ABI, exact alias allowed. Constants/semantics follow Official. */
.text
.align 2
.global poly_crepmod3
.global _poly_crepmod3
poly_crepmod3:
_poly_crepmod3:
    mov w8, #1728
    dup v0.8h, w8
    neg v1.8h, v0.8h
    mov w8, #10923
    dup v2.8h, w8
    movi v3.8h, #3
    mov x8, #1536
.Lcrepmod3_loop:
    ld1 {v16.8h-v19.8h}, [x1], #64
    cmgt v20.8h, v16.8h, v0.8h
    cmgt v21.8h, v17.8h, v0.8h
    cmgt v22.8h, v18.8h, v0.8h
    cmgt v23.8h, v19.8h, v0.8h
    add v16.8h, v16.8h, v20.8h
    add v17.8h, v17.8h, v21.8h
    add v18.8h, v18.8h, v22.8h
    add v19.8h, v19.8h, v23.8h
    cmgt v20.8h, v1.8h, v16.8h
    cmgt v21.8h, v1.8h, v17.8h
    cmgt v22.8h, v1.8h, v18.8h
    cmgt v23.8h, v1.8h, v19.8h
    sub v16.8h, v16.8h, v20.8h
    sub v17.8h, v17.8h, v21.8h
    sub v18.8h, v18.8h, v22.8h
    sub v19.8h, v19.8h, v23.8h
    sqrdmulh v20.8h, v16.8h, v2.8h
    sqrdmulh v21.8h, v17.8h, v2.8h
    sqrdmulh v22.8h, v18.8h, v2.8h
    sqrdmulh v23.8h, v19.8h, v2.8h
    mls v16.8h, v20.8h, v3.8h
    mls v17.8h, v21.8h, v3.8h
    mls v18.8h, v22.8h, v3.8h
    mls v19.8h, v23.8h, v3.8h
    st1 {v16.8h-v19.8h}, [x0], #64
    subs x8, x8, #64
    b.ne .Lcrepmod3_loop
    ret

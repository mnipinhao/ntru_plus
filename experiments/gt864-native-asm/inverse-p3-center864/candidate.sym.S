.text
.global center864
center864:
    // Constants are outside the scheduled loop body.  generate_physical.py
    // binds these setup instructions to Slothy's allocated live-in registers.
    mov w4, #3457
    dup v0.8h, w4
    mov w4, #9
    dup v1.8h, w4
    mov w4, #1728
    dup v2.8h, w4
    mov x8, #27
.Lcenter864_loop:
    // live-in: x0 block pointer and symbolic q/reciprocal9/halfq vectors.
    // live-out: x0 and all three constant vectors unchanged; four centered vectors stored.
    // coefficient range: input abs <=6912; output abs <=1728.
    // reserved physical registers: x18-x30, sp, xzr; no fixed vector registers.
center864_body_slothy_start:
    ldr Q<a0>, [x0, #0]
    ldr Q<a1>, [x0, #16]
    ldr Q<a2>, [x0, #32]
    ldr Q<a3>, [x0, #48]
    sqrdmulh V<t0>.8h, V<a0>.8h, V<recip>.8h
    mls V<a0>.8h, V<t0>.8h, V<q>.8h
    sshr V<t0>.8h, V<a0>.8h, #15
    and V<t0>.16b, V<t0>.16b, V<q>.16b
    add V<a0>.8h, V<a0>.8h, V<t0>.8h
    cmgt V<t0>.8h, V<a0>.8h, V<halfq>.8h
    and V<t0>.16b, V<t0>.16b, V<q>.16b
    sub V<a0>.8h, V<a0>.8h, V<t0>.8h
    sqrdmulh V<t1>.8h, V<a1>.8h, V<recip>.8h
    mls V<a1>.8h, V<t1>.8h, V<q>.8h
    sshr V<t1>.8h, V<a1>.8h, #15
    and V<t1>.16b, V<t1>.16b, V<q>.16b
    add V<a1>.8h, V<a1>.8h, V<t1>.8h
    cmgt V<t1>.8h, V<a1>.8h, V<halfq>.8h
    and V<t1>.16b, V<t1>.16b, V<q>.16b
    sub V<a1>.8h, V<a1>.8h, V<t1>.8h
    sqrdmulh V<t2>.8h, V<a2>.8h, V<recip>.8h
    mls V<a2>.8h, V<t2>.8h, V<q>.8h
    sshr V<t2>.8h, V<a2>.8h, #15
    and V<t2>.16b, V<t2>.16b, V<q>.16b
    add V<a2>.8h, V<a2>.8h, V<t2>.8h
    cmgt V<t2>.8h, V<a2>.8h, V<halfq>.8h
    and V<t2>.16b, V<t2>.16b, V<q>.16b
    sub V<a2>.8h, V<a2>.8h, V<t2>.8h
    sqrdmulh V<t3>.8h, V<a3>.8h, V<recip>.8h
    mls V<a3>.8h, V<t3>.8h, V<q>.8h
    sshr V<t3>.8h, V<a3>.8h, #15
    and V<t3>.16b, V<t3>.16b, V<q>.16b
    add V<a3>.8h, V<a3>.8h, V<t3>.8h
    cmgt V<t3>.8h, V<a3>.8h, V<halfq>.8h
    and V<t3>.16b, V<t3>.16b, V<q>.16b
    sub V<a3>.8h, V<a3>.8h, V<t3>.8h
    str Q<a0>, [x0, #0]
    str Q<a1>, [x0, #16]
    str Q<a2>, [x0, #32]
    str Q<a3>, [x0, #48]
center864_body_slothy_end:
    add x0, x0, #64
    subs x8, x8, #1
    b.ne .Lcenter864_loop
    ret

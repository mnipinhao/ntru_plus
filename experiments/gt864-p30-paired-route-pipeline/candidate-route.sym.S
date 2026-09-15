#ifdef __APPLE__
#define p29_main_route _p29_main_route
#endif
.text
.p2align 4
.global p29_main_route
p29_main_route:
// live-in: x0 natural output, x1 P29 equal-half paired main scratch
// live-out: rows 0..7 of every top/t in natural component-interleaved order
// P30: adjacent records share one scheduling window; arithmetic and memory multiset unchanged
// range: raw abs<=4577, adjusted abs<=4576, ternary abs<=1
// reserved physical registers: x18-x30, sp and xzr
p29_main_route_slothy_start:
    mov w3, #1728
    dup V<tern_hi>.8h, w3
    mov w3, #-1728
    dup V<tern_lo>.8h, w3
    mov w3, #10923
    dup V<tern_recip>.8h, w3
    movi V<tern_three>.8h, #3
    mov x2, x0
    p30_route_pair0_start:
    ldr Q<q0_0_b0>, [x1, #0]
    cmgt V<main_0_0_b0_above>.8h, V<q0_0_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_0_b0_below>.8h, V<tern_lo>.8h, V<q0_0_b0>.8h
    add V<q0_0_b0>.8h, V<q0_0_b0>.8h, V<main_0_0_b0_above>.8h
    sub V<q0_0_b0>.8h, V<q0_0_b0>.8h, V<main_0_0_b0_below>.8h
    sqrdmulh V<main_0_0_b0_quot>.8h, V<q0_0_b0>.8h, V<tern_recip>.8h
    mls V<q0_0_b0>.8h, V<main_0_0_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_0_b1>, [x1, #256]
    cmgt V<main_0_0_b1_above>.8h, V<q0_0_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_0_b1_below>.8h, V<tern_lo>.8h, V<q0_0_b1>.8h
    add V<q0_0_b1>.8h, V<q0_0_b1>.8h, V<main_0_0_b1_above>.8h
    sub V<q0_0_b1>.8h, V<q0_0_b1>.8h, V<main_0_0_b1_below>.8h
    sqrdmulh V<main_0_0_b1_quot>.8h, V<q0_0_b1>.8h, V<tern_recip>.8h
    mls V<q0_0_b1>.8h, V<main_0_0_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_0_b2>, [x1, #1024]
    cmgt V<main_0_0_b2_above>.8h, V<q0_0_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_0_b2_below>.8h, V<tern_lo>.8h, V<q0_0_b2>.8h
    add V<q0_0_b2>.8h, V<q0_0_b2>.8h, V<main_0_0_b2_above>.8h
    sub V<q0_0_b2>.8h, V<q0_0_b2>.8h, V<main_0_0_b2_below>.8h
    sqrdmulh V<main_0_0_b2_quot>.8h, V<q0_0_b2>.8h, V<tern_recip>.8h
    mls V<q0_0_b2>.8h, V<main_0_0_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_0_c1lo>.16b, V<q0_0_b0>.16b, V<q0_0_b0>.16b, #8
    ext V<q0_0_c1hi>.16b, V<q0_0_b1>.16b, V<q0_0_b1>.16b, #8
    ext V<q0_0_c2hi>.16b, V<q0_0_b2>.16b, V<q0_0_b2>.16b, #8
    st3 {V<q0_0_b0>.4h, V<q0_0_c1lo>.4h, V<q0_0_b2>.4h}, [x2], #24
    st3 {V<q0_0_b1>.4h, V<q0_0_c1hi>.4h, V<q0_0_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q0_1_b0>, [x1, #16]
    cmgt V<main_0_1_b0_above>.8h, V<q0_1_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_1_b0_below>.8h, V<tern_lo>.8h, V<q0_1_b0>.8h
    add V<q0_1_b0>.8h, V<q0_1_b0>.8h, V<main_0_1_b0_above>.8h
    sub V<q0_1_b0>.8h, V<q0_1_b0>.8h, V<main_0_1_b0_below>.8h
    sqrdmulh V<main_0_1_b0_quot>.8h, V<q0_1_b0>.8h, V<tern_recip>.8h
    mls V<q0_1_b0>.8h, V<main_0_1_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_1_b1>, [x1, #272]
    cmgt V<main_0_1_b1_above>.8h, V<q0_1_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_1_b1_below>.8h, V<tern_lo>.8h, V<q0_1_b1>.8h
    add V<q0_1_b1>.8h, V<q0_1_b1>.8h, V<main_0_1_b1_above>.8h
    sub V<q0_1_b1>.8h, V<q0_1_b1>.8h, V<main_0_1_b1_below>.8h
    sqrdmulh V<main_0_1_b1_quot>.8h, V<q0_1_b1>.8h, V<tern_recip>.8h
    mls V<q0_1_b1>.8h, V<main_0_1_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_1_b2>, [x1, #1040]
    cmgt V<main_0_1_b2_above>.8h, V<q0_1_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_1_b2_below>.8h, V<tern_lo>.8h, V<q0_1_b2>.8h
    add V<q0_1_b2>.8h, V<q0_1_b2>.8h, V<main_0_1_b2_above>.8h
    sub V<q0_1_b2>.8h, V<q0_1_b2>.8h, V<main_0_1_b2_below>.8h
    sqrdmulh V<main_0_1_b2_quot>.8h, V<q0_1_b2>.8h, V<tern_recip>.8h
    mls V<q0_1_b2>.8h, V<main_0_1_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_1_c1lo>.16b, V<q0_1_b0>.16b, V<q0_1_b0>.16b, #8
    ext V<q0_1_c1hi>.16b, V<q0_1_b1>.16b, V<q0_1_b1>.16b, #8
    ext V<q0_1_c2hi>.16b, V<q0_1_b2>.16b, V<q0_1_b2>.16b, #8
    st3 {V<q0_1_b0>.4h, V<q0_1_c1lo>.4h, V<q0_1_b2>.4h}, [x2], #24
    st3 {V<q0_1_b1>.4h, V<q0_1_c1hi>.4h, V<q0_1_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair0_end:
    p30_route_pair1_start:
    ldr Q<q0_2_b0>, [x1, #32]
    cmgt V<main_0_2_b0_above>.8h, V<q0_2_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_2_b0_below>.8h, V<tern_lo>.8h, V<q0_2_b0>.8h
    add V<q0_2_b0>.8h, V<q0_2_b0>.8h, V<main_0_2_b0_above>.8h
    sub V<q0_2_b0>.8h, V<q0_2_b0>.8h, V<main_0_2_b0_below>.8h
    sqrdmulh V<main_0_2_b0_quot>.8h, V<q0_2_b0>.8h, V<tern_recip>.8h
    mls V<q0_2_b0>.8h, V<main_0_2_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_2_b1>, [x1, #288]
    cmgt V<main_0_2_b1_above>.8h, V<q0_2_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_2_b1_below>.8h, V<tern_lo>.8h, V<q0_2_b1>.8h
    add V<q0_2_b1>.8h, V<q0_2_b1>.8h, V<main_0_2_b1_above>.8h
    sub V<q0_2_b1>.8h, V<q0_2_b1>.8h, V<main_0_2_b1_below>.8h
    sqrdmulh V<main_0_2_b1_quot>.8h, V<q0_2_b1>.8h, V<tern_recip>.8h
    mls V<q0_2_b1>.8h, V<main_0_2_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_2_b2>, [x1, #1056]
    cmgt V<main_0_2_b2_above>.8h, V<q0_2_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_2_b2_below>.8h, V<tern_lo>.8h, V<q0_2_b2>.8h
    add V<q0_2_b2>.8h, V<q0_2_b2>.8h, V<main_0_2_b2_above>.8h
    sub V<q0_2_b2>.8h, V<q0_2_b2>.8h, V<main_0_2_b2_below>.8h
    sqrdmulh V<main_0_2_b2_quot>.8h, V<q0_2_b2>.8h, V<tern_recip>.8h
    mls V<q0_2_b2>.8h, V<main_0_2_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_2_c1lo>.16b, V<q0_2_b0>.16b, V<q0_2_b0>.16b, #8
    ext V<q0_2_c1hi>.16b, V<q0_2_b1>.16b, V<q0_2_b1>.16b, #8
    ext V<q0_2_c2hi>.16b, V<q0_2_b2>.16b, V<q0_2_b2>.16b, #8
    st3 {V<q0_2_b0>.4h, V<q0_2_c1lo>.4h, V<q0_2_b2>.4h}, [x2], #24
    st3 {V<q0_2_b1>.4h, V<q0_2_c1hi>.4h, V<q0_2_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q0_3_b0>, [x1, #48]
    cmgt V<main_0_3_b0_above>.8h, V<q0_3_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_3_b0_below>.8h, V<tern_lo>.8h, V<q0_3_b0>.8h
    add V<q0_3_b0>.8h, V<q0_3_b0>.8h, V<main_0_3_b0_above>.8h
    sub V<q0_3_b0>.8h, V<q0_3_b0>.8h, V<main_0_3_b0_below>.8h
    sqrdmulh V<main_0_3_b0_quot>.8h, V<q0_3_b0>.8h, V<tern_recip>.8h
    mls V<q0_3_b0>.8h, V<main_0_3_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_3_b1>, [x1, #304]
    cmgt V<main_0_3_b1_above>.8h, V<q0_3_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_3_b1_below>.8h, V<tern_lo>.8h, V<q0_3_b1>.8h
    add V<q0_3_b1>.8h, V<q0_3_b1>.8h, V<main_0_3_b1_above>.8h
    sub V<q0_3_b1>.8h, V<q0_3_b1>.8h, V<main_0_3_b1_below>.8h
    sqrdmulh V<main_0_3_b1_quot>.8h, V<q0_3_b1>.8h, V<tern_recip>.8h
    mls V<q0_3_b1>.8h, V<main_0_3_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_3_b2>, [x1, #1072]
    cmgt V<main_0_3_b2_above>.8h, V<q0_3_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_3_b2_below>.8h, V<tern_lo>.8h, V<q0_3_b2>.8h
    add V<q0_3_b2>.8h, V<q0_3_b2>.8h, V<main_0_3_b2_above>.8h
    sub V<q0_3_b2>.8h, V<q0_3_b2>.8h, V<main_0_3_b2_below>.8h
    sqrdmulh V<main_0_3_b2_quot>.8h, V<q0_3_b2>.8h, V<tern_recip>.8h
    mls V<q0_3_b2>.8h, V<main_0_3_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_3_c1lo>.16b, V<q0_3_b0>.16b, V<q0_3_b0>.16b, #8
    ext V<q0_3_c1hi>.16b, V<q0_3_b1>.16b, V<q0_3_b1>.16b, #8
    ext V<q0_3_c2hi>.16b, V<q0_3_b2>.16b, V<q0_3_b2>.16b, #8
    st3 {V<q0_3_b0>.4h, V<q0_3_c1lo>.4h, V<q0_3_b2>.4h}, [x2], #24
    st3 {V<q0_3_b1>.4h, V<q0_3_c1hi>.4h, V<q0_3_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair1_end:
    p30_route_pair2_start:
    ldr Q<q0_4_b0>, [x1, #64]
    cmgt V<main_0_4_b0_above>.8h, V<q0_4_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_4_b0_below>.8h, V<tern_lo>.8h, V<q0_4_b0>.8h
    add V<q0_4_b0>.8h, V<q0_4_b0>.8h, V<main_0_4_b0_above>.8h
    sub V<q0_4_b0>.8h, V<q0_4_b0>.8h, V<main_0_4_b0_below>.8h
    sqrdmulh V<main_0_4_b0_quot>.8h, V<q0_4_b0>.8h, V<tern_recip>.8h
    mls V<q0_4_b0>.8h, V<main_0_4_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_4_b1>, [x1, #320]
    cmgt V<main_0_4_b1_above>.8h, V<q0_4_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_4_b1_below>.8h, V<tern_lo>.8h, V<q0_4_b1>.8h
    add V<q0_4_b1>.8h, V<q0_4_b1>.8h, V<main_0_4_b1_above>.8h
    sub V<q0_4_b1>.8h, V<q0_4_b1>.8h, V<main_0_4_b1_below>.8h
    sqrdmulh V<main_0_4_b1_quot>.8h, V<q0_4_b1>.8h, V<tern_recip>.8h
    mls V<q0_4_b1>.8h, V<main_0_4_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_4_b2>, [x1, #1088]
    cmgt V<main_0_4_b2_above>.8h, V<q0_4_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_4_b2_below>.8h, V<tern_lo>.8h, V<q0_4_b2>.8h
    add V<q0_4_b2>.8h, V<q0_4_b2>.8h, V<main_0_4_b2_above>.8h
    sub V<q0_4_b2>.8h, V<q0_4_b2>.8h, V<main_0_4_b2_below>.8h
    sqrdmulh V<main_0_4_b2_quot>.8h, V<q0_4_b2>.8h, V<tern_recip>.8h
    mls V<q0_4_b2>.8h, V<main_0_4_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_4_c1lo>.16b, V<q0_4_b0>.16b, V<q0_4_b0>.16b, #8
    ext V<q0_4_c1hi>.16b, V<q0_4_b1>.16b, V<q0_4_b1>.16b, #8
    ext V<q0_4_c2hi>.16b, V<q0_4_b2>.16b, V<q0_4_b2>.16b, #8
    st3 {V<q0_4_b0>.4h, V<q0_4_c1lo>.4h, V<q0_4_b2>.4h}, [x2], #24
    st3 {V<q0_4_b1>.4h, V<q0_4_c1hi>.4h, V<q0_4_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q0_5_b0>, [x1, #80]
    cmgt V<main_0_5_b0_above>.8h, V<q0_5_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_5_b0_below>.8h, V<tern_lo>.8h, V<q0_5_b0>.8h
    add V<q0_5_b0>.8h, V<q0_5_b0>.8h, V<main_0_5_b0_above>.8h
    sub V<q0_5_b0>.8h, V<q0_5_b0>.8h, V<main_0_5_b0_below>.8h
    sqrdmulh V<main_0_5_b0_quot>.8h, V<q0_5_b0>.8h, V<tern_recip>.8h
    mls V<q0_5_b0>.8h, V<main_0_5_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_5_b1>, [x1, #336]
    cmgt V<main_0_5_b1_above>.8h, V<q0_5_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_5_b1_below>.8h, V<tern_lo>.8h, V<q0_5_b1>.8h
    add V<q0_5_b1>.8h, V<q0_5_b1>.8h, V<main_0_5_b1_above>.8h
    sub V<q0_5_b1>.8h, V<q0_5_b1>.8h, V<main_0_5_b1_below>.8h
    sqrdmulh V<main_0_5_b1_quot>.8h, V<q0_5_b1>.8h, V<tern_recip>.8h
    mls V<q0_5_b1>.8h, V<main_0_5_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_5_b2>, [x1, #1104]
    cmgt V<main_0_5_b2_above>.8h, V<q0_5_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_5_b2_below>.8h, V<tern_lo>.8h, V<q0_5_b2>.8h
    add V<q0_5_b2>.8h, V<q0_5_b2>.8h, V<main_0_5_b2_above>.8h
    sub V<q0_5_b2>.8h, V<q0_5_b2>.8h, V<main_0_5_b2_below>.8h
    sqrdmulh V<main_0_5_b2_quot>.8h, V<q0_5_b2>.8h, V<tern_recip>.8h
    mls V<q0_5_b2>.8h, V<main_0_5_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_5_c1lo>.16b, V<q0_5_b0>.16b, V<q0_5_b0>.16b, #8
    ext V<q0_5_c1hi>.16b, V<q0_5_b1>.16b, V<q0_5_b1>.16b, #8
    ext V<q0_5_c2hi>.16b, V<q0_5_b2>.16b, V<q0_5_b2>.16b, #8
    st3 {V<q0_5_b0>.4h, V<q0_5_c1lo>.4h, V<q0_5_b2>.4h}, [x2], #24
    st3 {V<q0_5_b1>.4h, V<q0_5_c1hi>.4h, V<q0_5_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair2_end:
    p30_route_pair3_start:
    ldr Q<q0_6_b0>, [x1, #96]
    cmgt V<main_0_6_b0_above>.8h, V<q0_6_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_6_b0_below>.8h, V<tern_lo>.8h, V<q0_6_b0>.8h
    add V<q0_6_b0>.8h, V<q0_6_b0>.8h, V<main_0_6_b0_above>.8h
    sub V<q0_6_b0>.8h, V<q0_6_b0>.8h, V<main_0_6_b0_below>.8h
    sqrdmulh V<main_0_6_b0_quot>.8h, V<q0_6_b0>.8h, V<tern_recip>.8h
    mls V<q0_6_b0>.8h, V<main_0_6_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_6_b1>, [x1, #352]
    cmgt V<main_0_6_b1_above>.8h, V<q0_6_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_6_b1_below>.8h, V<tern_lo>.8h, V<q0_6_b1>.8h
    add V<q0_6_b1>.8h, V<q0_6_b1>.8h, V<main_0_6_b1_above>.8h
    sub V<q0_6_b1>.8h, V<q0_6_b1>.8h, V<main_0_6_b1_below>.8h
    sqrdmulh V<main_0_6_b1_quot>.8h, V<q0_6_b1>.8h, V<tern_recip>.8h
    mls V<q0_6_b1>.8h, V<main_0_6_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_6_b2>, [x1, #1120]
    cmgt V<main_0_6_b2_above>.8h, V<q0_6_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_6_b2_below>.8h, V<tern_lo>.8h, V<q0_6_b2>.8h
    add V<q0_6_b2>.8h, V<q0_6_b2>.8h, V<main_0_6_b2_above>.8h
    sub V<q0_6_b2>.8h, V<q0_6_b2>.8h, V<main_0_6_b2_below>.8h
    sqrdmulh V<main_0_6_b2_quot>.8h, V<q0_6_b2>.8h, V<tern_recip>.8h
    mls V<q0_6_b2>.8h, V<main_0_6_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_6_c1lo>.16b, V<q0_6_b0>.16b, V<q0_6_b0>.16b, #8
    ext V<q0_6_c1hi>.16b, V<q0_6_b1>.16b, V<q0_6_b1>.16b, #8
    ext V<q0_6_c2hi>.16b, V<q0_6_b2>.16b, V<q0_6_b2>.16b, #8
    st3 {V<q0_6_b0>.4h, V<q0_6_c1lo>.4h, V<q0_6_b2>.4h}, [x2], #24
    st3 {V<q0_6_b1>.4h, V<q0_6_c1hi>.4h, V<q0_6_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q0_7_b0>, [x1, #112]
    cmgt V<main_0_7_b0_above>.8h, V<q0_7_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_7_b0_below>.8h, V<tern_lo>.8h, V<q0_7_b0>.8h
    add V<q0_7_b0>.8h, V<q0_7_b0>.8h, V<main_0_7_b0_above>.8h
    sub V<q0_7_b0>.8h, V<q0_7_b0>.8h, V<main_0_7_b0_below>.8h
    sqrdmulh V<main_0_7_b0_quot>.8h, V<q0_7_b0>.8h, V<tern_recip>.8h
    mls V<q0_7_b0>.8h, V<main_0_7_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_7_b1>, [x1, #368]
    cmgt V<main_0_7_b1_above>.8h, V<q0_7_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_7_b1_below>.8h, V<tern_lo>.8h, V<q0_7_b1>.8h
    add V<q0_7_b1>.8h, V<q0_7_b1>.8h, V<main_0_7_b1_above>.8h
    sub V<q0_7_b1>.8h, V<q0_7_b1>.8h, V<main_0_7_b1_below>.8h
    sqrdmulh V<main_0_7_b1_quot>.8h, V<q0_7_b1>.8h, V<tern_recip>.8h
    mls V<q0_7_b1>.8h, V<main_0_7_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_7_b2>, [x1, #1136]
    cmgt V<main_0_7_b2_above>.8h, V<q0_7_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_7_b2_below>.8h, V<tern_lo>.8h, V<q0_7_b2>.8h
    add V<q0_7_b2>.8h, V<q0_7_b2>.8h, V<main_0_7_b2_above>.8h
    sub V<q0_7_b2>.8h, V<q0_7_b2>.8h, V<main_0_7_b2_below>.8h
    sqrdmulh V<main_0_7_b2_quot>.8h, V<q0_7_b2>.8h, V<tern_recip>.8h
    mls V<q0_7_b2>.8h, V<main_0_7_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_7_c1lo>.16b, V<q0_7_b0>.16b, V<q0_7_b0>.16b, #8
    ext V<q0_7_c1hi>.16b, V<q0_7_b1>.16b, V<q0_7_b1>.16b, #8
    ext V<q0_7_c2hi>.16b, V<q0_7_b2>.16b, V<q0_7_b2>.16b, #8
    st3 {V<q0_7_b0>.4h, V<q0_7_c1lo>.4h, V<q0_7_b2>.4h}, [x2], #24
    st3 {V<q0_7_b1>.4h, V<q0_7_c1hi>.4h, V<q0_7_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair3_end:
    p30_route_pair4_start:
    ldr Q<q0_8_b0>, [x1, #128]
    cmgt V<main_0_8_b0_above>.8h, V<q0_8_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_8_b0_below>.8h, V<tern_lo>.8h, V<q0_8_b0>.8h
    add V<q0_8_b0>.8h, V<q0_8_b0>.8h, V<main_0_8_b0_above>.8h
    sub V<q0_8_b0>.8h, V<q0_8_b0>.8h, V<main_0_8_b0_below>.8h
    sqrdmulh V<main_0_8_b0_quot>.8h, V<q0_8_b0>.8h, V<tern_recip>.8h
    mls V<q0_8_b0>.8h, V<main_0_8_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_8_b1>, [x1, #384]
    cmgt V<main_0_8_b1_above>.8h, V<q0_8_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_8_b1_below>.8h, V<tern_lo>.8h, V<q0_8_b1>.8h
    add V<q0_8_b1>.8h, V<q0_8_b1>.8h, V<main_0_8_b1_above>.8h
    sub V<q0_8_b1>.8h, V<q0_8_b1>.8h, V<main_0_8_b1_below>.8h
    sqrdmulh V<main_0_8_b1_quot>.8h, V<q0_8_b1>.8h, V<tern_recip>.8h
    mls V<q0_8_b1>.8h, V<main_0_8_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_8_b2>, [x1, #1152]
    cmgt V<main_0_8_b2_above>.8h, V<q0_8_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_8_b2_below>.8h, V<tern_lo>.8h, V<q0_8_b2>.8h
    add V<q0_8_b2>.8h, V<q0_8_b2>.8h, V<main_0_8_b2_above>.8h
    sub V<q0_8_b2>.8h, V<q0_8_b2>.8h, V<main_0_8_b2_below>.8h
    sqrdmulh V<main_0_8_b2_quot>.8h, V<q0_8_b2>.8h, V<tern_recip>.8h
    mls V<q0_8_b2>.8h, V<main_0_8_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_8_c1lo>.16b, V<q0_8_b0>.16b, V<q0_8_b0>.16b, #8
    ext V<q0_8_c1hi>.16b, V<q0_8_b1>.16b, V<q0_8_b1>.16b, #8
    ext V<q0_8_c2hi>.16b, V<q0_8_b2>.16b, V<q0_8_b2>.16b, #8
    st3 {V<q0_8_b0>.4h, V<q0_8_c1lo>.4h, V<q0_8_b2>.4h}, [x2], #24
    st3 {V<q0_8_b1>.4h, V<q0_8_c1hi>.4h, V<q0_8_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q0_9_b0>, [x1, #144]
    cmgt V<main_0_9_b0_above>.8h, V<q0_9_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_9_b0_below>.8h, V<tern_lo>.8h, V<q0_9_b0>.8h
    add V<q0_9_b0>.8h, V<q0_9_b0>.8h, V<main_0_9_b0_above>.8h
    sub V<q0_9_b0>.8h, V<q0_9_b0>.8h, V<main_0_9_b0_below>.8h
    sqrdmulh V<main_0_9_b0_quot>.8h, V<q0_9_b0>.8h, V<tern_recip>.8h
    mls V<q0_9_b0>.8h, V<main_0_9_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_9_b1>, [x1, #400]
    cmgt V<main_0_9_b1_above>.8h, V<q0_9_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_9_b1_below>.8h, V<tern_lo>.8h, V<q0_9_b1>.8h
    add V<q0_9_b1>.8h, V<q0_9_b1>.8h, V<main_0_9_b1_above>.8h
    sub V<q0_9_b1>.8h, V<q0_9_b1>.8h, V<main_0_9_b1_below>.8h
    sqrdmulh V<main_0_9_b1_quot>.8h, V<q0_9_b1>.8h, V<tern_recip>.8h
    mls V<q0_9_b1>.8h, V<main_0_9_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_9_b2>, [x1, #1168]
    cmgt V<main_0_9_b2_above>.8h, V<q0_9_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_9_b2_below>.8h, V<tern_lo>.8h, V<q0_9_b2>.8h
    add V<q0_9_b2>.8h, V<q0_9_b2>.8h, V<main_0_9_b2_above>.8h
    sub V<q0_9_b2>.8h, V<q0_9_b2>.8h, V<main_0_9_b2_below>.8h
    sqrdmulh V<main_0_9_b2_quot>.8h, V<q0_9_b2>.8h, V<tern_recip>.8h
    mls V<q0_9_b2>.8h, V<main_0_9_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_9_c1lo>.16b, V<q0_9_b0>.16b, V<q0_9_b0>.16b, #8
    ext V<q0_9_c1hi>.16b, V<q0_9_b1>.16b, V<q0_9_b1>.16b, #8
    ext V<q0_9_c2hi>.16b, V<q0_9_b2>.16b, V<q0_9_b2>.16b, #8
    st3 {V<q0_9_b0>.4h, V<q0_9_c1lo>.4h, V<q0_9_b2>.4h}, [x2], #24
    st3 {V<q0_9_b1>.4h, V<q0_9_c1hi>.4h, V<q0_9_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair4_end:
    p30_route_pair5_start:
    ldr Q<q0_10_b0>, [x1, #160]
    cmgt V<main_0_10_b0_above>.8h, V<q0_10_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_10_b0_below>.8h, V<tern_lo>.8h, V<q0_10_b0>.8h
    add V<q0_10_b0>.8h, V<q0_10_b0>.8h, V<main_0_10_b0_above>.8h
    sub V<q0_10_b0>.8h, V<q0_10_b0>.8h, V<main_0_10_b0_below>.8h
    sqrdmulh V<main_0_10_b0_quot>.8h, V<q0_10_b0>.8h, V<tern_recip>.8h
    mls V<q0_10_b0>.8h, V<main_0_10_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_10_b1>, [x1, #416]
    cmgt V<main_0_10_b1_above>.8h, V<q0_10_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_10_b1_below>.8h, V<tern_lo>.8h, V<q0_10_b1>.8h
    add V<q0_10_b1>.8h, V<q0_10_b1>.8h, V<main_0_10_b1_above>.8h
    sub V<q0_10_b1>.8h, V<q0_10_b1>.8h, V<main_0_10_b1_below>.8h
    sqrdmulh V<main_0_10_b1_quot>.8h, V<q0_10_b1>.8h, V<tern_recip>.8h
    mls V<q0_10_b1>.8h, V<main_0_10_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_10_b2>, [x1, #1184]
    cmgt V<main_0_10_b2_above>.8h, V<q0_10_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_10_b2_below>.8h, V<tern_lo>.8h, V<q0_10_b2>.8h
    add V<q0_10_b2>.8h, V<q0_10_b2>.8h, V<main_0_10_b2_above>.8h
    sub V<q0_10_b2>.8h, V<q0_10_b2>.8h, V<main_0_10_b2_below>.8h
    sqrdmulh V<main_0_10_b2_quot>.8h, V<q0_10_b2>.8h, V<tern_recip>.8h
    mls V<q0_10_b2>.8h, V<main_0_10_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_10_c1lo>.16b, V<q0_10_b0>.16b, V<q0_10_b0>.16b, #8
    ext V<q0_10_c1hi>.16b, V<q0_10_b1>.16b, V<q0_10_b1>.16b, #8
    ext V<q0_10_c2hi>.16b, V<q0_10_b2>.16b, V<q0_10_b2>.16b, #8
    st3 {V<q0_10_b0>.4h, V<q0_10_c1lo>.4h, V<q0_10_b2>.4h}, [x2], #24
    st3 {V<q0_10_b1>.4h, V<q0_10_c1hi>.4h, V<q0_10_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q0_11_b0>, [x1, #176]
    cmgt V<main_0_11_b0_above>.8h, V<q0_11_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_11_b0_below>.8h, V<tern_lo>.8h, V<q0_11_b0>.8h
    add V<q0_11_b0>.8h, V<q0_11_b0>.8h, V<main_0_11_b0_above>.8h
    sub V<q0_11_b0>.8h, V<q0_11_b0>.8h, V<main_0_11_b0_below>.8h
    sqrdmulh V<main_0_11_b0_quot>.8h, V<q0_11_b0>.8h, V<tern_recip>.8h
    mls V<q0_11_b0>.8h, V<main_0_11_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_11_b1>, [x1, #432]
    cmgt V<main_0_11_b1_above>.8h, V<q0_11_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_11_b1_below>.8h, V<tern_lo>.8h, V<q0_11_b1>.8h
    add V<q0_11_b1>.8h, V<q0_11_b1>.8h, V<main_0_11_b1_above>.8h
    sub V<q0_11_b1>.8h, V<q0_11_b1>.8h, V<main_0_11_b1_below>.8h
    sqrdmulh V<main_0_11_b1_quot>.8h, V<q0_11_b1>.8h, V<tern_recip>.8h
    mls V<q0_11_b1>.8h, V<main_0_11_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_11_b2>, [x1, #1200]
    cmgt V<main_0_11_b2_above>.8h, V<q0_11_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_11_b2_below>.8h, V<tern_lo>.8h, V<q0_11_b2>.8h
    add V<q0_11_b2>.8h, V<q0_11_b2>.8h, V<main_0_11_b2_above>.8h
    sub V<q0_11_b2>.8h, V<q0_11_b2>.8h, V<main_0_11_b2_below>.8h
    sqrdmulh V<main_0_11_b2_quot>.8h, V<q0_11_b2>.8h, V<tern_recip>.8h
    mls V<q0_11_b2>.8h, V<main_0_11_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_11_c1lo>.16b, V<q0_11_b0>.16b, V<q0_11_b0>.16b, #8
    ext V<q0_11_c1hi>.16b, V<q0_11_b1>.16b, V<q0_11_b1>.16b, #8
    ext V<q0_11_c2hi>.16b, V<q0_11_b2>.16b, V<q0_11_b2>.16b, #8
    st3 {V<q0_11_b0>.4h, V<q0_11_c1lo>.4h, V<q0_11_b2>.4h}, [x2], #24
    st3 {V<q0_11_b1>.4h, V<q0_11_c1hi>.4h, V<q0_11_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair5_end:
    p30_route_pair6_start:
    ldr Q<q0_12_b0>, [x1, #192]
    cmgt V<main_0_12_b0_above>.8h, V<q0_12_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_12_b0_below>.8h, V<tern_lo>.8h, V<q0_12_b0>.8h
    add V<q0_12_b0>.8h, V<q0_12_b0>.8h, V<main_0_12_b0_above>.8h
    sub V<q0_12_b0>.8h, V<q0_12_b0>.8h, V<main_0_12_b0_below>.8h
    sqrdmulh V<main_0_12_b0_quot>.8h, V<q0_12_b0>.8h, V<tern_recip>.8h
    mls V<q0_12_b0>.8h, V<main_0_12_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_12_b1>, [x1, #448]
    cmgt V<main_0_12_b1_above>.8h, V<q0_12_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_12_b1_below>.8h, V<tern_lo>.8h, V<q0_12_b1>.8h
    add V<q0_12_b1>.8h, V<q0_12_b1>.8h, V<main_0_12_b1_above>.8h
    sub V<q0_12_b1>.8h, V<q0_12_b1>.8h, V<main_0_12_b1_below>.8h
    sqrdmulh V<main_0_12_b1_quot>.8h, V<q0_12_b1>.8h, V<tern_recip>.8h
    mls V<q0_12_b1>.8h, V<main_0_12_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_12_b2>, [x1, #1216]
    cmgt V<main_0_12_b2_above>.8h, V<q0_12_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_12_b2_below>.8h, V<tern_lo>.8h, V<q0_12_b2>.8h
    add V<q0_12_b2>.8h, V<q0_12_b2>.8h, V<main_0_12_b2_above>.8h
    sub V<q0_12_b2>.8h, V<q0_12_b2>.8h, V<main_0_12_b2_below>.8h
    sqrdmulh V<main_0_12_b2_quot>.8h, V<q0_12_b2>.8h, V<tern_recip>.8h
    mls V<q0_12_b2>.8h, V<main_0_12_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_12_c1lo>.16b, V<q0_12_b0>.16b, V<q0_12_b0>.16b, #8
    ext V<q0_12_c1hi>.16b, V<q0_12_b1>.16b, V<q0_12_b1>.16b, #8
    ext V<q0_12_c2hi>.16b, V<q0_12_b2>.16b, V<q0_12_b2>.16b, #8
    st3 {V<q0_12_b0>.4h, V<q0_12_c1lo>.4h, V<q0_12_b2>.4h}, [x2], #24
    st3 {V<q0_12_b1>.4h, V<q0_12_c1hi>.4h, V<q0_12_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q0_13_b0>, [x1, #208]
    cmgt V<main_0_13_b0_above>.8h, V<q0_13_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_13_b0_below>.8h, V<tern_lo>.8h, V<q0_13_b0>.8h
    add V<q0_13_b0>.8h, V<q0_13_b0>.8h, V<main_0_13_b0_above>.8h
    sub V<q0_13_b0>.8h, V<q0_13_b0>.8h, V<main_0_13_b0_below>.8h
    sqrdmulh V<main_0_13_b0_quot>.8h, V<q0_13_b0>.8h, V<tern_recip>.8h
    mls V<q0_13_b0>.8h, V<main_0_13_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_13_b1>, [x1, #464]
    cmgt V<main_0_13_b1_above>.8h, V<q0_13_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_13_b1_below>.8h, V<tern_lo>.8h, V<q0_13_b1>.8h
    add V<q0_13_b1>.8h, V<q0_13_b1>.8h, V<main_0_13_b1_above>.8h
    sub V<q0_13_b1>.8h, V<q0_13_b1>.8h, V<main_0_13_b1_below>.8h
    sqrdmulh V<main_0_13_b1_quot>.8h, V<q0_13_b1>.8h, V<tern_recip>.8h
    mls V<q0_13_b1>.8h, V<main_0_13_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_13_b2>, [x1, #1232]
    cmgt V<main_0_13_b2_above>.8h, V<q0_13_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_13_b2_below>.8h, V<tern_lo>.8h, V<q0_13_b2>.8h
    add V<q0_13_b2>.8h, V<q0_13_b2>.8h, V<main_0_13_b2_above>.8h
    sub V<q0_13_b2>.8h, V<q0_13_b2>.8h, V<main_0_13_b2_below>.8h
    sqrdmulh V<main_0_13_b2_quot>.8h, V<q0_13_b2>.8h, V<tern_recip>.8h
    mls V<q0_13_b2>.8h, V<main_0_13_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_13_c1lo>.16b, V<q0_13_b0>.16b, V<q0_13_b0>.16b, #8
    ext V<q0_13_c1hi>.16b, V<q0_13_b1>.16b, V<q0_13_b1>.16b, #8
    ext V<q0_13_c2hi>.16b, V<q0_13_b2>.16b, V<q0_13_b2>.16b, #8
    st3 {V<q0_13_b0>.4h, V<q0_13_c1lo>.4h, V<q0_13_b2>.4h}, [x2], #24
    st3 {V<q0_13_b1>.4h, V<q0_13_c1hi>.4h, V<q0_13_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair6_end:
    p30_route_pair7_start:
    ldr Q<q0_14_b0>, [x1, #224]
    cmgt V<main_0_14_b0_above>.8h, V<q0_14_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_14_b0_below>.8h, V<tern_lo>.8h, V<q0_14_b0>.8h
    add V<q0_14_b0>.8h, V<q0_14_b0>.8h, V<main_0_14_b0_above>.8h
    sub V<q0_14_b0>.8h, V<q0_14_b0>.8h, V<main_0_14_b0_below>.8h
    sqrdmulh V<main_0_14_b0_quot>.8h, V<q0_14_b0>.8h, V<tern_recip>.8h
    mls V<q0_14_b0>.8h, V<main_0_14_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_14_b1>, [x1, #480]
    cmgt V<main_0_14_b1_above>.8h, V<q0_14_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_14_b1_below>.8h, V<tern_lo>.8h, V<q0_14_b1>.8h
    add V<q0_14_b1>.8h, V<q0_14_b1>.8h, V<main_0_14_b1_above>.8h
    sub V<q0_14_b1>.8h, V<q0_14_b1>.8h, V<main_0_14_b1_below>.8h
    sqrdmulh V<main_0_14_b1_quot>.8h, V<q0_14_b1>.8h, V<tern_recip>.8h
    mls V<q0_14_b1>.8h, V<main_0_14_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_14_b2>, [x1, #1248]
    cmgt V<main_0_14_b2_above>.8h, V<q0_14_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_14_b2_below>.8h, V<tern_lo>.8h, V<q0_14_b2>.8h
    add V<q0_14_b2>.8h, V<q0_14_b2>.8h, V<main_0_14_b2_above>.8h
    sub V<q0_14_b2>.8h, V<q0_14_b2>.8h, V<main_0_14_b2_below>.8h
    sqrdmulh V<main_0_14_b2_quot>.8h, V<q0_14_b2>.8h, V<tern_recip>.8h
    mls V<q0_14_b2>.8h, V<main_0_14_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_14_c1lo>.16b, V<q0_14_b0>.16b, V<q0_14_b0>.16b, #8
    ext V<q0_14_c1hi>.16b, V<q0_14_b1>.16b, V<q0_14_b1>.16b, #8
    ext V<q0_14_c2hi>.16b, V<q0_14_b2>.16b, V<q0_14_b2>.16b, #8
    st3 {V<q0_14_b0>.4h, V<q0_14_c1lo>.4h, V<q0_14_b2>.4h}, [x2], #24
    st3 {V<q0_14_b1>.4h, V<q0_14_c1hi>.4h, V<q0_14_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q0_15_b0>, [x1, #240]
    cmgt V<main_0_15_b0_above>.8h, V<q0_15_b0>.8h, V<tern_hi>.8h
    cmgt V<main_0_15_b0_below>.8h, V<tern_lo>.8h, V<q0_15_b0>.8h
    add V<q0_15_b0>.8h, V<q0_15_b0>.8h, V<main_0_15_b0_above>.8h
    sub V<q0_15_b0>.8h, V<q0_15_b0>.8h, V<main_0_15_b0_below>.8h
    sqrdmulh V<main_0_15_b0_quot>.8h, V<q0_15_b0>.8h, V<tern_recip>.8h
    mls V<q0_15_b0>.8h, V<main_0_15_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q0_15_b1>, [x1, #496]
    cmgt V<main_0_15_b1_above>.8h, V<q0_15_b1>.8h, V<tern_hi>.8h
    cmgt V<main_0_15_b1_below>.8h, V<tern_lo>.8h, V<q0_15_b1>.8h
    add V<q0_15_b1>.8h, V<q0_15_b1>.8h, V<main_0_15_b1_above>.8h
    sub V<q0_15_b1>.8h, V<q0_15_b1>.8h, V<main_0_15_b1_below>.8h
    sqrdmulh V<main_0_15_b1_quot>.8h, V<q0_15_b1>.8h, V<tern_recip>.8h
    mls V<q0_15_b1>.8h, V<main_0_15_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q0_15_b2>, [x1, #1264]
    cmgt V<main_0_15_b2_above>.8h, V<q0_15_b2>.8h, V<tern_hi>.8h
    cmgt V<main_0_15_b2_below>.8h, V<tern_lo>.8h, V<q0_15_b2>.8h
    add V<q0_15_b2>.8h, V<q0_15_b2>.8h, V<main_0_15_b2_above>.8h
    sub V<q0_15_b2>.8h, V<q0_15_b2>.8h, V<main_0_15_b2_below>.8h
    sqrdmulh V<main_0_15_b2_quot>.8h, V<q0_15_b2>.8h, V<tern_recip>.8h
    mls V<q0_15_b2>.8h, V<main_0_15_b2_quot>.8h, V<tern_three>.8h
    ext V<q0_15_c1lo>.16b, V<q0_15_b0>.16b, V<q0_15_b0>.16b, #8
    ext V<q0_15_c1hi>.16b, V<q0_15_b1>.16b, V<q0_15_b1>.16b, #8
    ext V<q0_15_c2hi>.16b, V<q0_15_b2>.16b, V<q0_15_b2>.16b, #8
    st3 {V<q0_15_b0>.4h, V<q0_15_c1lo>.4h, V<q0_15_b2>.4h}, [x2], #24
    st3 {V<q0_15_b1>.4h, V<q0_15_c1hi>.4h, V<q0_15_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair7_end:
    p30_route_pair8_start:
    ldr Q<q1_0_b0>, [x1, #512]
    cmgt V<main_1_0_b0_above>.8h, V<q1_0_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_0_b0_below>.8h, V<tern_lo>.8h, V<q1_0_b0>.8h
    add V<q1_0_b0>.8h, V<q1_0_b0>.8h, V<main_1_0_b0_above>.8h
    sub V<q1_0_b0>.8h, V<q1_0_b0>.8h, V<main_1_0_b0_below>.8h
    sqrdmulh V<main_1_0_b0_quot>.8h, V<q1_0_b0>.8h, V<tern_recip>.8h
    mls V<q1_0_b0>.8h, V<main_1_0_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_0_b1>, [x1, #768]
    cmgt V<main_1_0_b1_above>.8h, V<q1_0_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_0_b1_below>.8h, V<tern_lo>.8h, V<q1_0_b1>.8h
    add V<q1_0_b1>.8h, V<q1_0_b1>.8h, V<main_1_0_b1_above>.8h
    sub V<q1_0_b1>.8h, V<q1_0_b1>.8h, V<main_1_0_b1_below>.8h
    sqrdmulh V<main_1_0_b1_quot>.8h, V<q1_0_b1>.8h, V<tern_recip>.8h
    mls V<q1_0_b1>.8h, V<main_1_0_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_0_b2>, [x1, #1280]
    cmgt V<main_1_0_b2_above>.8h, V<q1_0_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_0_b2_below>.8h, V<tern_lo>.8h, V<q1_0_b2>.8h
    add V<q1_0_b2>.8h, V<q1_0_b2>.8h, V<main_1_0_b2_above>.8h
    sub V<q1_0_b2>.8h, V<q1_0_b2>.8h, V<main_1_0_b2_below>.8h
    sqrdmulh V<main_1_0_b2_quot>.8h, V<q1_0_b2>.8h, V<tern_recip>.8h
    mls V<q1_0_b2>.8h, V<main_1_0_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_0_c1lo>.16b, V<q1_0_b0>.16b, V<q1_0_b0>.16b, #8
    ext V<q1_0_c1hi>.16b, V<q1_0_b1>.16b, V<q1_0_b1>.16b, #8
    ext V<q1_0_c2hi>.16b, V<q1_0_b2>.16b, V<q1_0_b2>.16b, #8
    st3 {V<q1_0_b0>.4h, V<q1_0_c1lo>.4h, V<q1_0_b2>.4h}, [x2], #24
    st3 {V<q1_0_b1>.4h, V<q1_0_c1hi>.4h, V<q1_0_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q1_1_b0>, [x1, #528]
    cmgt V<main_1_1_b0_above>.8h, V<q1_1_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_1_b0_below>.8h, V<tern_lo>.8h, V<q1_1_b0>.8h
    add V<q1_1_b0>.8h, V<q1_1_b0>.8h, V<main_1_1_b0_above>.8h
    sub V<q1_1_b0>.8h, V<q1_1_b0>.8h, V<main_1_1_b0_below>.8h
    sqrdmulh V<main_1_1_b0_quot>.8h, V<q1_1_b0>.8h, V<tern_recip>.8h
    mls V<q1_1_b0>.8h, V<main_1_1_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_1_b1>, [x1, #784]
    cmgt V<main_1_1_b1_above>.8h, V<q1_1_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_1_b1_below>.8h, V<tern_lo>.8h, V<q1_1_b1>.8h
    add V<q1_1_b1>.8h, V<q1_1_b1>.8h, V<main_1_1_b1_above>.8h
    sub V<q1_1_b1>.8h, V<q1_1_b1>.8h, V<main_1_1_b1_below>.8h
    sqrdmulh V<main_1_1_b1_quot>.8h, V<q1_1_b1>.8h, V<tern_recip>.8h
    mls V<q1_1_b1>.8h, V<main_1_1_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_1_b2>, [x1, #1296]
    cmgt V<main_1_1_b2_above>.8h, V<q1_1_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_1_b2_below>.8h, V<tern_lo>.8h, V<q1_1_b2>.8h
    add V<q1_1_b2>.8h, V<q1_1_b2>.8h, V<main_1_1_b2_above>.8h
    sub V<q1_1_b2>.8h, V<q1_1_b2>.8h, V<main_1_1_b2_below>.8h
    sqrdmulh V<main_1_1_b2_quot>.8h, V<q1_1_b2>.8h, V<tern_recip>.8h
    mls V<q1_1_b2>.8h, V<main_1_1_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_1_c1lo>.16b, V<q1_1_b0>.16b, V<q1_1_b0>.16b, #8
    ext V<q1_1_c1hi>.16b, V<q1_1_b1>.16b, V<q1_1_b1>.16b, #8
    ext V<q1_1_c2hi>.16b, V<q1_1_b2>.16b, V<q1_1_b2>.16b, #8
    st3 {V<q1_1_b0>.4h, V<q1_1_c1lo>.4h, V<q1_1_b2>.4h}, [x2], #24
    st3 {V<q1_1_b1>.4h, V<q1_1_c1hi>.4h, V<q1_1_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair8_end:
    p30_route_pair9_start:
    ldr Q<q1_2_b0>, [x1, #544]
    cmgt V<main_1_2_b0_above>.8h, V<q1_2_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_2_b0_below>.8h, V<tern_lo>.8h, V<q1_2_b0>.8h
    add V<q1_2_b0>.8h, V<q1_2_b0>.8h, V<main_1_2_b0_above>.8h
    sub V<q1_2_b0>.8h, V<q1_2_b0>.8h, V<main_1_2_b0_below>.8h
    sqrdmulh V<main_1_2_b0_quot>.8h, V<q1_2_b0>.8h, V<tern_recip>.8h
    mls V<q1_2_b0>.8h, V<main_1_2_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_2_b1>, [x1, #800]
    cmgt V<main_1_2_b1_above>.8h, V<q1_2_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_2_b1_below>.8h, V<tern_lo>.8h, V<q1_2_b1>.8h
    add V<q1_2_b1>.8h, V<q1_2_b1>.8h, V<main_1_2_b1_above>.8h
    sub V<q1_2_b1>.8h, V<q1_2_b1>.8h, V<main_1_2_b1_below>.8h
    sqrdmulh V<main_1_2_b1_quot>.8h, V<q1_2_b1>.8h, V<tern_recip>.8h
    mls V<q1_2_b1>.8h, V<main_1_2_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_2_b2>, [x1, #1312]
    cmgt V<main_1_2_b2_above>.8h, V<q1_2_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_2_b2_below>.8h, V<tern_lo>.8h, V<q1_2_b2>.8h
    add V<q1_2_b2>.8h, V<q1_2_b2>.8h, V<main_1_2_b2_above>.8h
    sub V<q1_2_b2>.8h, V<q1_2_b2>.8h, V<main_1_2_b2_below>.8h
    sqrdmulh V<main_1_2_b2_quot>.8h, V<q1_2_b2>.8h, V<tern_recip>.8h
    mls V<q1_2_b2>.8h, V<main_1_2_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_2_c1lo>.16b, V<q1_2_b0>.16b, V<q1_2_b0>.16b, #8
    ext V<q1_2_c1hi>.16b, V<q1_2_b1>.16b, V<q1_2_b1>.16b, #8
    ext V<q1_2_c2hi>.16b, V<q1_2_b2>.16b, V<q1_2_b2>.16b, #8
    st3 {V<q1_2_b0>.4h, V<q1_2_c1lo>.4h, V<q1_2_b2>.4h}, [x2], #24
    st3 {V<q1_2_b1>.4h, V<q1_2_c1hi>.4h, V<q1_2_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q1_3_b0>, [x1, #560]
    cmgt V<main_1_3_b0_above>.8h, V<q1_3_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_3_b0_below>.8h, V<tern_lo>.8h, V<q1_3_b0>.8h
    add V<q1_3_b0>.8h, V<q1_3_b0>.8h, V<main_1_3_b0_above>.8h
    sub V<q1_3_b0>.8h, V<q1_3_b0>.8h, V<main_1_3_b0_below>.8h
    sqrdmulh V<main_1_3_b0_quot>.8h, V<q1_3_b0>.8h, V<tern_recip>.8h
    mls V<q1_3_b0>.8h, V<main_1_3_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_3_b1>, [x1, #816]
    cmgt V<main_1_3_b1_above>.8h, V<q1_3_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_3_b1_below>.8h, V<tern_lo>.8h, V<q1_3_b1>.8h
    add V<q1_3_b1>.8h, V<q1_3_b1>.8h, V<main_1_3_b1_above>.8h
    sub V<q1_3_b1>.8h, V<q1_3_b1>.8h, V<main_1_3_b1_below>.8h
    sqrdmulh V<main_1_3_b1_quot>.8h, V<q1_3_b1>.8h, V<tern_recip>.8h
    mls V<q1_3_b1>.8h, V<main_1_3_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_3_b2>, [x1, #1328]
    cmgt V<main_1_3_b2_above>.8h, V<q1_3_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_3_b2_below>.8h, V<tern_lo>.8h, V<q1_3_b2>.8h
    add V<q1_3_b2>.8h, V<q1_3_b2>.8h, V<main_1_3_b2_above>.8h
    sub V<q1_3_b2>.8h, V<q1_3_b2>.8h, V<main_1_3_b2_below>.8h
    sqrdmulh V<main_1_3_b2_quot>.8h, V<q1_3_b2>.8h, V<tern_recip>.8h
    mls V<q1_3_b2>.8h, V<main_1_3_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_3_c1lo>.16b, V<q1_3_b0>.16b, V<q1_3_b0>.16b, #8
    ext V<q1_3_c1hi>.16b, V<q1_3_b1>.16b, V<q1_3_b1>.16b, #8
    ext V<q1_3_c2hi>.16b, V<q1_3_b2>.16b, V<q1_3_b2>.16b, #8
    st3 {V<q1_3_b0>.4h, V<q1_3_c1lo>.4h, V<q1_3_b2>.4h}, [x2], #24
    st3 {V<q1_3_b1>.4h, V<q1_3_c1hi>.4h, V<q1_3_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair9_end:
    p30_route_pair10_start:
    ldr Q<q1_4_b0>, [x1, #576]
    cmgt V<main_1_4_b0_above>.8h, V<q1_4_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_4_b0_below>.8h, V<tern_lo>.8h, V<q1_4_b0>.8h
    add V<q1_4_b0>.8h, V<q1_4_b0>.8h, V<main_1_4_b0_above>.8h
    sub V<q1_4_b0>.8h, V<q1_4_b0>.8h, V<main_1_4_b0_below>.8h
    sqrdmulh V<main_1_4_b0_quot>.8h, V<q1_4_b0>.8h, V<tern_recip>.8h
    mls V<q1_4_b0>.8h, V<main_1_4_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_4_b1>, [x1, #832]
    cmgt V<main_1_4_b1_above>.8h, V<q1_4_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_4_b1_below>.8h, V<tern_lo>.8h, V<q1_4_b1>.8h
    add V<q1_4_b1>.8h, V<q1_4_b1>.8h, V<main_1_4_b1_above>.8h
    sub V<q1_4_b1>.8h, V<q1_4_b1>.8h, V<main_1_4_b1_below>.8h
    sqrdmulh V<main_1_4_b1_quot>.8h, V<q1_4_b1>.8h, V<tern_recip>.8h
    mls V<q1_4_b1>.8h, V<main_1_4_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_4_b2>, [x1, #1344]
    cmgt V<main_1_4_b2_above>.8h, V<q1_4_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_4_b2_below>.8h, V<tern_lo>.8h, V<q1_4_b2>.8h
    add V<q1_4_b2>.8h, V<q1_4_b2>.8h, V<main_1_4_b2_above>.8h
    sub V<q1_4_b2>.8h, V<q1_4_b2>.8h, V<main_1_4_b2_below>.8h
    sqrdmulh V<main_1_4_b2_quot>.8h, V<q1_4_b2>.8h, V<tern_recip>.8h
    mls V<q1_4_b2>.8h, V<main_1_4_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_4_c1lo>.16b, V<q1_4_b0>.16b, V<q1_4_b0>.16b, #8
    ext V<q1_4_c1hi>.16b, V<q1_4_b1>.16b, V<q1_4_b1>.16b, #8
    ext V<q1_4_c2hi>.16b, V<q1_4_b2>.16b, V<q1_4_b2>.16b, #8
    st3 {V<q1_4_b0>.4h, V<q1_4_c1lo>.4h, V<q1_4_b2>.4h}, [x2], #24
    st3 {V<q1_4_b1>.4h, V<q1_4_c1hi>.4h, V<q1_4_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q1_5_b0>, [x1, #592]
    cmgt V<main_1_5_b0_above>.8h, V<q1_5_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_5_b0_below>.8h, V<tern_lo>.8h, V<q1_5_b0>.8h
    add V<q1_5_b0>.8h, V<q1_5_b0>.8h, V<main_1_5_b0_above>.8h
    sub V<q1_5_b0>.8h, V<q1_5_b0>.8h, V<main_1_5_b0_below>.8h
    sqrdmulh V<main_1_5_b0_quot>.8h, V<q1_5_b0>.8h, V<tern_recip>.8h
    mls V<q1_5_b0>.8h, V<main_1_5_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_5_b1>, [x1, #848]
    cmgt V<main_1_5_b1_above>.8h, V<q1_5_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_5_b1_below>.8h, V<tern_lo>.8h, V<q1_5_b1>.8h
    add V<q1_5_b1>.8h, V<q1_5_b1>.8h, V<main_1_5_b1_above>.8h
    sub V<q1_5_b1>.8h, V<q1_5_b1>.8h, V<main_1_5_b1_below>.8h
    sqrdmulh V<main_1_5_b1_quot>.8h, V<q1_5_b1>.8h, V<tern_recip>.8h
    mls V<q1_5_b1>.8h, V<main_1_5_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_5_b2>, [x1, #1360]
    cmgt V<main_1_5_b2_above>.8h, V<q1_5_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_5_b2_below>.8h, V<tern_lo>.8h, V<q1_5_b2>.8h
    add V<q1_5_b2>.8h, V<q1_5_b2>.8h, V<main_1_5_b2_above>.8h
    sub V<q1_5_b2>.8h, V<q1_5_b2>.8h, V<main_1_5_b2_below>.8h
    sqrdmulh V<main_1_5_b2_quot>.8h, V<q1_5_b2>.8h, V<tern_recip>.8h
    mls V<q1_5_b2>.8h, V<main_1_5_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_5_c1lo>.16b, V<q1_5_b0>.16b, V<q1_5_b0>.16b, #8
    ext V<q1_5_c1hi>.16b, V<q1_5_b1>.16b, V<q1_5_b1>.16b, #8
    ext V<q1_5_c2hi>.16b, V<q1_5_b2>.16b, V<q1_5_b2>.16b, #8
    st3 {V<q1_5_b0>.4h, V<q1_5_c1lo>.4h, V<q1_5_b2>.4h}, [x2], #24
    st3 {V<q1_5_b1>.4h, V<q1_5_c1hi>.4h, V<q1_5_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair10_end:
    p30_route_pair11_start:
    ldr Q<q1_6_b0>, [x1, #608]
    cmgt V<main_1_6_b0_above>.8h, V<q1_6_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_6_b0_below>.8h, V<tern_lo>.8h, V<q1_6_b0>.8h
    add V<q1_6_b0>.8h, V<q1_6_b0>.8h, V<main_1_6_b0_above>.8h
    sub V<q1_6_b0>.8h, V<q1_6_b0>.8h, V<main_1_6_b0_below>.8h
    sqrdmulh V<main_1_6_b0_quot>.8h, V<q1_6_b0>.8h, V<tern_recip>.8h
    mls V<q1_6_b0>.8h, V<main_1_6_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_6_b1>, [x1, #864]
    cmgt V<main_1_6_b1_above>.8h, V<q1_6_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_6_b1_below>.8h, V<tern_lo>.8h, V<q1_6_b1>.8h
    add V<q1_6_b1>.8h, V<q1_6_b1>.8h, V<main_1_6_b1_above>.8h
    sub V<q1_6_b1>.8h, V<q1_6_b1>.8h, V<main_1_6_b1_below>.8h
    sqrdmulh V<main_1_6_b1_quot>.8h, V<q1_6_b1>.8h, V<tern_recip>.8h
    mls V<q1_6_b1>.8h, V<main_1_6_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_6_b2>, [x1, #1376]
    cmgt V<main_1_6_b2_above>.8h, V<q1_6_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_6_b2_below>.8h, V<tern_lo>.8h, V<q1_6_b2>.8h
    add V<q1_6_b2>.8h, V<q1_6_b2>.8h, V<main_1_6_b2_above>.8h
    sub V<q1_6_b2>.8h, V<q1_6_b2>.8h, V<main_1_6_b2_below>.8h
    sqrdmulh V<main_1_6_b2_quot>.8h, V<q1_6_b2>.8h, V<tern_recip>.8h
    mls V<q1_6_b2>.8h, V<main_1_6_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_6_c1lo>.16b, V<q1_6_b0>.16b, V<q1_6_b0>.16b, #8
    ext V<q1_6_c1hi>.16b, V<q1_6_b1>.16b, V<q1_6_b1>.16b, #8
    ext V<q1_6_c2hi>.16b, V<q1_6_b2>.16b, V<q1_6_b2>.16b, #8
    st3 {V<q1_6_b0>.4h, V<q1_6_c1lo>.4h, V<q1_6_b2>.4h}, [x2], #24
    st3 {V<q1_6_b1>.4h, V<q1_6_c1hi>.4h, V<q1_6_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q1_7_b0>, [x1, #624]
    cmgt V<main_1_7_b0_above>.8h, V<q1_7_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_7_b0_below>.8h, V<tern_lo>.8h, V<q1_7_b0>.8h
    add V<q1_7_b0>.8h, V<q1_7_b0>.8h, V<main_1_7_b0_above>.8h
    sub V<q1_7_b0>.8h, V<q1_7_b0>.8h, V<main_1_7_b0_below>.8h
    sqrdmulh V<main_1_7_b0_quot>.8h, V<q1_7_b0>.8h, V<tern_recip>.8h
    mls V<q1_7_b0>.8h, V<main_1_7_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_7_b1>, [x1, #880]
    cmgt V<main_1_7_b1_above>.8h, V<q1_7_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_7_b1_below>.8h, V<tern_lo>.8h, V<q1_7_b1>.8h
    add V<q1_7_b1>.8h, V<q1_7_b1>.8h, V<main_1_7_b1_above>.8h
    sub V<q1_7_b1>.8h, V<q1_7_b1>.8h, V<main_1_7_b1_below>.8h
    sqrdmulh V<main_1_7_b1_quot>.8h, V<q1_7_b1>.8h, V<tern_recip>.8h
    mls V<q1_7_b1>.8h, V<main_1_7_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_7_b2>, [x1, #1392]
    cmgt V<main_1_7_b2_above>.8h, V<q1_7_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_7_b2_below>.8h, V<tern_lo>.8h, V<q1_7_b2>.8h
    add V<q1_7_b2>.8h, V<q1_7_b2>.8h, V<main_1_7_b2_above>.8h
    sub V<q1_7_b2>.8h, V<q1_7_b2>.8h, V<main_1_7_b2_below>.8h
    sqrdmulh V<main_1_7_b2_quot>.8h, V<q1_7_b2>.8h, V<tern_recip>.8h
    mls V<q1_7_b2>.8h, V<main_1_7_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_7_c1lo>.16b, V<q1_7_b0>.16b, V<q1_7_b0>.16b, #8
    ext V<q1_7_c1hi>.16b, V<q1_7_b1>.16b, V<q1_7_b1>.16b, #8
    ext V<q1_7_c2hi>.16b, V<q1_7_b2>.16b, V<q1_7_b2>.16b, #8
    st3 {V<q1_7_b0>.4h, V<q1_7_c1lo>.4h, V<q1_7_b2>.4h}, [x2], #24
    st3 {V<q1_7_b1>.4h, V<q1_7_c1hi>.4h, V<q1_7_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair11_end:
    p30_route_pair12_start:
    ldr Q<q1_8_b0>, [x1, #640]
    cmgt V<main_1_8_b0_above>.8h, V<q1_8_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_8_b0_below>.8h, V<tern_lo>.8h, V<q1_8_b0>.8h
    add V<q1_8_b0>.8h, V<q1_8_b0>.8h, V<main_1_8_b0_above>.8h
    sub V<q1_8_b0>.8h, V<q1_8_b0>.8h, V<main_1_8_b0_below>.8h
    sqrdmulh V<main_1_8_b0_quot>.8h, V<q1_8_b0>.8h, V<tern_recip>.8h
    mls V<q1_8_b0>.8h, V<main_1_8_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_8_b1>, [x1, #896]
    cmgt V<main_1_8_b1_above>.8h, V<q1_8_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_8_b1_below>.8h, V<tern_lo>.8h, V<q1_8_b1>.8h
    add V<q1_8_b1>.8h, V<q1_8_b1>.8h, V<main_1_8_b1_above>.8h
    sub V<q1_8_b1>.8h, V<q1_8_b1>.8h, V<main_1_8_b1_below>.8h
    sqrdmulh V<main_1_8_b1_quot>.8h, V<q1_8_b1>.8h, V<tern_recip>.8h
    mls V<q1_8_b1>.8h, V<main_1_8_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_8_b2>, [x1, #1408]
    cmgt V<main_1_8_b2_above>.8h, V<q1_8_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_8_b2_below>.8h, V<tern_lo>.8h, V<q1_8_b2>.8h
    add V<q1_8_b2>.8h, V<q1_8_b2>.8h, V<main_1_8_b2_above>.8h
    sub V<q1_8_b2>.8h, V<q1_8_b2>.8h, V<main_1_8_b2_below>.8h
    sqrdmulh V<main_1_8_b2_quot>.8h, V<q1_8_b2>.8h, V<tern_recip>.8h
    mls V<q1_8_b2>.8h, V<main_1_8_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_8_c1lo>.16b, V<q1_8_b0>.16b, V<q1_8_b0>.16b, #8
    ext V<q1_8_c1hi>.16b, V<q1_8_b1>.16b, V<q1_8_b1>.16b, #8
    ext V<q1_8_c2hi>.16b, V<q1_8_b2>.16b, V<q1_8_b2>.16b, #8
    st3 {V<q1_8_b0>.4h, V<q1_8_c1lo>.4h, V<q1_8_b2>.4h}, [x2], #24
    st3 {V<q1_8_b1>.4h, V<q1_8_c1hi>.4h, V<q1_8_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q1_9_b0>, [x1, #656]
    cmgt V<main_1_9_b0_above>.8h, V<q1_9_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_9_b0_below>.8h, V<tern_lo>.8h, V<q1_9_b0>.8h
    add V<q1_9_b0>.8h, V<q1_9_b0>.8h, V<main_1_9_b0_above>.8h
    sub V<q1_9_b0>.8h, V<q1_9_b0>.8h, V<main_1_9_b0_below>.8h
    sqrdmulh V<main_1_9_b0_quot>.8h, V<q1_9_b0>.8h, V<tern_recip>.8h
    mls V<q1_9_b0>.8h, V<main_1_9_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_9_b1>, [x1, #912]
    cmgt V<main_1_9_b1_above>.8h, V<q1_9_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_9_b1_below>.8h, V<tern_lo>.8h, V<q1_9_b1>.8h
    add V<q1_9_b1>.8h, V<q1_9_b1>.8h, V<main_1_9_b1_above>.8h
    sub V<q1_9_b1>.8h, V<q1_9_b1>.8h, V<main_1_9_b1_below>.8h
    sqrdmulh V<main_1_9_b1_quot>.8h, V<q1_9_b1>.8h, V<tern_recip>.8h
    mls V<q1_9_b1>.8h, V<main_1_9_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_9_b2>, [x1, #1424]
    cmgt V<main_1_9_b2_above>.8h, V<q1_9_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_9_b2_below>.8h, V<tern_lo>.8h, V<q1_9_b2>.8h
    add V<q1_9_b2>.8h, V<q1_9_b2>.8h, V<main_1_9_b2_above>.8h
    sub V<q1_9_b2>.8h, V<q1_9_b2>.8h, V<main_1_9_b2_below>.8h
    sqrdmulh V<main_1_9_b2_quot>.8h, V<q1_9_b2>.8h, V<tern_recip>.8h
    mls V<q1_9_b2>.8h, V<main_1_9_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_9_c1lo>.16b, V<q1_9_b0>.16b, V<q1_9_b0>.16b, #8
    ext V<q1_9_c1hi>.16b, V<q1_9_b1>.16b, V<q1_9_b1>.16b, #8
    ext V<q1_9_c2hi>.16b, V<q1_9_b2>.16b, V<q1_9_b2>.16b, #8
    st3 {V<q1_9_b0>.4h, V<q1_9_c1lo>.4h, V<q1_9_b2>.4h}, [x2], #24
    st3 {V<q1_9_b1>.4h, V<q1_9_c1hi>.4h, V<q1_9_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair12_end:
    p30_route_pair13_start:
    ldr Q<q1_10_b0>, [x1, #672]
    cmgt V<main_1_10_b0_above>.8h, V<q1_10_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_10_b0_below>.8h, V<tern_lo>.8h, V<q1_10_b0>.8h
    add V<q1_10_b0>.8h, V<q1_10_b0>.8h, V<main_1_10_b0_above>.8h
    sub V<q1_10_b0>.8h, V<q1_10_b0>.8h, V<main_1_10_b0_below>.8h
    sqrdmulh V<main_1_10_b0_quot>.8h, V<q1_10_b0>.8h, V<tern_recip>.8h
    mls V<q1_10_b0>.8h, V<main_1_10_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_10_b1>, [x1, #928]
    cmgt V<main_1_10_b1_above>.8h, V<q1_10_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_10_b1_below>.8h, V<tern_lo>.8h, V<q1_10_b1>.8h
    add V<q1_10_b1>.8h, V<q1_10_b1>.8h, V<main_1_10_b1_above>.8h
    sub V<q1_10_b1>.8h, V<q1_10_b1>.8h, V<main_1_10_b1_below>.8h
    sqrdmulh V<main_1_10_b1_quot>.8h, V<q1_10_b1>.8h, V<tern_recip>.8h
    mls V<q1_10_b1>.8h, V<main_1_10_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_10_b2>, [x1, #1440]
    cmgt V<main_1_10_b2_above>.8h, V<q1_10_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_10_b2_below>.8h, V<tern_lo>.8h, V<q1_10_b2>.8h
    add V<q1_10_b2>.8h, V<q1_10_b2>.8h, V<main_1_10_b2_above>.8h
    sub V<q1_10_b2>.8h, V<q1_10_b2>.8h, V<main_1_10_b2_below>.8h
    sqrdmulh V<main_1_10_b2_quot>.8h, V<q1_10_b2>.8h, V<tern_recip>.8h
    mls V<q1_10_b2>.8h, V<main_1_10_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_10_c1lo>.16b, V<q1_10_b0>.16b, V<q1_10_b0>.16b, #8
    ext V<q1_10_c1hi>.16b, V<q1_10_b1>.16b, V<q1_10_b1>.16b, #8
    ext V<q1_10_c2hi>.16b, V<q1_10_b2>.16b, V<q1_10_b2>.16b, #8
    st3 {V<q1_10_b0>.4h, V<q1_10_c1lo>.4h, V<q1_10_b2>.4h}, [x2], #24
    st3 {V<q1_10_b1>.4h, V<q1_10_c1hi>.4h, V<q1_10_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q1_11_b0>, [x1, #688]
    cmgt V<main_1_11_b0_above>.8h, V<q1_11_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_11_b0_below>.8h, V<tern_lo>.8h, V<q1_11_b0>.8h
    add V<q1_11_b0>.8h, V<q1_11_b0>.8h, V<main_1_11_b0_above>.8h
    sub V<q1_11_b0>.8h, V<q1_11_b0>.8h, V<main_1_11_b0_below>.8h
    sqrdmulh V<main_1_11_b0_quot>.8h, V<q1_11_b0>.8h, V<tern_recip>.8h
    mls V<q1_11_b0>.8h, V<main_1_11_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_11_b1>, [x1, #944]
    cmgt V<main_1_11_b1_above>.8h, V<q1_11_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_11_b1_below>.8h, V<tern_lo>.8h, V<q1_11_b1>.8h
    add V<q1_11_b1>.8h, V<q1_11_b1>.8h, V<main_1_11_b1_above>.8h
    sub V<q1_11_b1>.8h, V<q1_11_b1>.8h, V<main_1_11_b1_below>.8h
    sqrdmulh V<main_1_11_b1_quot>.8h, V<q1_11_b1>.8h, V<tern_recip>.8h
    mls V<q1_11_b1>.8h, V<main_1_11_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_11_b2>, [x1, #1456]
    cmgt V<main_1_11_b2_above>.8h, V<q1_11_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_11_b2_below>.8h, V<tern_lo>.8h, V<q1_11_b2>.8h
    add V<q1_11_b2>.8h, V<q1_11_b2>.8h, V<main_1_11_b2_above>.8h
    sub V<q1_11_b2>.8h, V<q1_11_b2>.8h, V<main_1_11_b2_below>.8h
    sqrdmulh V<main_1_11_b2_quot>.8h, V<q1_11_b2>.8h, V<tern_recip>.8h
    mls V<q1_11_b2>.8h, V<main_1_11_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_11_c1lo>.16b, V<q1_11_b0>.16b, V<q1_11_b0>.16b, #8
    ext V<q1_11_c1hi>.16b, V<q1_11_b1>.16b, V<q1_11_b1>.16b, #8
    ext V<q1_11_c2hi>.16b, V<q1_11_b2>.16b, V<q1_11_b2>.16b, #8
    st3 {V<q1_11_b0>.4h, V<q1_11_c1lo>.4h, V<q1_11_b2>.4h}, [x2], #24
    st3 {V<q1_11_b1>.4h, V<q1_11_c1hi>.4h, V<q1_11_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair13_end:
    p30_route_pair14_start:
    ldr Q<q1_12_b0>, [x1, #704]
    cmgt V<main_1_12_b0_above>.8h, V<q1_12_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_12_b0_below>.8h, V<tern_lo>.8h, V<q1_12_b0>.8h
    add V<q1_12_b0>.8h, V<q1_12_b0>.8h, V<main_1_12_b0_above>.8h
    sub V<q1_12_b0>.8h, V<q1_12_b0>.8h, V<main_1_12_b0_below>.8h
    sqrdmulh V<main_1_12_b0_quot>.8h, V<q1_12_b0>.8h, V<tern_recip>.8h
    mls V<q1_12_b0>.8h, V<main_1_12_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_12_b1>, [x1, #960]
    cmgt V<main_1_12_b1_above>.8h, V<q1_12_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_12_b1_below>.8h, V<tern_lo>.8h, V<q1_12_b1>.8h
    add V<q1_12_b1>.8h, V<q1_12_b1>.8h, V<main_1_12_b1_above>.8h
    sub V<q1_12_b1>.8h, V<q1_12_b1>.8h, V<main_1_12_b1_below>.8h
    sqrdmulh V<main_1_12_b1_quot>.8h, V<q1_12_b1>.8h, V<tern_recip>.8h
    mls V<q1_12_b1>.8h, V<main_1_12_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_12_b2>, [x1, #1472]
    cmgt V<main_1_12_b2_above>.8h, V<q1_12_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_12_b2_below>.8h, V<tern_lo>.8h, V<q1_12_b2>.8h
    add V<q1_12_b2>.8h, V<q1_12_b2>.8h, V<main_1_12_b2_above>.8h
    sub V<q1_12_b2>.8h, V<q1_12_b2>.8h, V<main_1_12_b2_below>.8h
    sqrdmulh V<main_1_12_b2_quot>.8h, V<q1_12_b2>.8h, V<tern_recip>.8h
    mls V<q1_12_b2>.8h, V<main_1_12_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_12_c1lo>.16b, V<q1_12_b0>.16b, V<q1_12_b0>.16b, #8
    ext V<q1_12_c1hi>.16b, V<q1_12_b1>.16b, V<q1_12_b1>.16b, #8
    ext V<q1_12_c2hi>.16b, V<q1_12_b2>.16b, V<q1_12_b2>.16b, #8
    st3 {V<q1_12_b0>.4h, V<q1_12_c1lo>.4h, V<q1_12_b2>.4h}, [x2], #24
    st3 {V<q1_12_b1>.4h, V<q1_12_c1hi>.4h, V<q1_12_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q1_13_b0>, [x1, #720]
    cmgt V<main_1_13_b0_above>.8h, V<q1_13_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_13_b0_below>.8h, V<tern_lo>.8h, V<q1_13_b0>.8h
    add V<q1_13_b0>.8h, V<q1_13_b0>.8h, V<main_1_13_b0_above>.8h
    sub V<q1_13_b0>.8h, V<q1_13_b0>.8h, V<main_1_13_b0_below>.8h
    sqrdmulh V<main_1_13_b0_quot>.8h, V<q1_13_b0>.8h, V<tern_recip>.8h
    mls V<q1_13_b0>.8h, V<main_1_13_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_13_b1>, [x1, #976]
    cmgt V<main_1_13_b1_above>.8h, V<q1_13_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_13_b1_below>.8h, V<tern_lo>.8h, V<q1_13_b1>.8h
    add V<q1_13_b1>.8h, V<q1_13_b1>.8h, V<main_1_13_b1_above>.8h
    sub V<q1_13_b1>.8h, V<q1_13_b1>.8h, V<main_1_13_b1_below>.8h
    sqrdmulh V<main_1_13_b1_quot>.8h, V<q1_13_b1>.8h, V<tern_recip>.8h
    mls V<q1_13_b1>.8h, V<main_1_13_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_13_b2>, [x1, #1488]
    cmgt V<main_1_13_b2_above>.8h, V<q1_13_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_13_b2_below>.8h, V<tern_lo>.8h, V<q1_13_b2>.8h
    add V<q1_13_b2>.8h, V<q1_13_b2>.8h, V<main_1_13_b2_above>.8h
    sub V<q1_13_b2>.8h, V<q1_13_b2>.8h, V<main_1_13_b2_below>.8h
    sqrdmulh V<main_1_13_b2_quot>.8h, V<q1_13_b2>.8h, V<tern_recip>.8h
    mls V<q1_13_b2>.8h, V<main_1_13_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_13_c1lo>.16b, V<q1_13_b0>.16b, V<q1_13_b0>.16b, #8
    ext V<q1_13_c1hi>.16b, V<q1_13_b1>.16b, V<q1_13_b1>.16b, #8
    ext V<q1_13_c2hi>.16b, V<q1_13_b2>.16b, V<q1_13_b2>.16b, #8
    st3 {V<q1_13_b0>.4h, V<q1_13_c1lo>.4h, V<q1_13_b2>.4h}, [x2], #24
    st3 {V<q1_13_b1>.4h, V<q1_13_c1hi>.4h, V<q1_13_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair14_end:
    p30_route_pair15_start:
    ldr Q<q1_14_b0>, [x1, #736]
    cmgt V<main_1_14_b0_above>.8h, V<q1_14_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_14_b0_below>.8h, V<tern_lo>.8h, V<q1_14_b0>.8h
    add V<q1_14_b0>.8h, V<q1_14_b0>.8h, V<main_1_14_b0_above>.8h
    sub V<q1_14_b0>.8h, V<q1_14_b0>.8h, V<main_1_14_b0_below>.8h
    sqrdmulh V<main_1_14_b0_quot>.8h, V<q1_14_b0>.8h, V<tern_recip>.8h
    mls V<q1_14_b0>.8h, V<main_1_14_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_14_b1>, [x1, #992]
    cmgt V<main_1_14_b1_above>.8h, V<q1_14_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_14_b1_below>.8h, V<tern_lo>.8h, V<q1_14_b1>.8h
    add V<q1_14_b1>.8h, V<q1_14_b1>.8h, V<main_1_14_b1_above>.8h
    sub V<q1_14_b1>.8h, V<q1_14_b1>.8h, V<main_1_14_b1_below>.8h
    sqrdmulh V<main_1_14_b1_quot>.8h, V<q1_14_b1>.8h, V<tern_recip>.8h
    mls V<q1_14_b1>.8h, V<main_1_14_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_14_b2>, [x1, #1504]
    cmgt V<main_1_14_b2_above>.8h, V<q1_14_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_14_b2_below>.8h, V<tern_lo>.8h, V<q1_14_b2>.8h
    add V<q1_14_b2>.8h, V<q1_14_b2>.8h, V<main_1_14_b2_above>.8h
    sub V<q1_14_b2>.8h, V<q1_14_b2>.8h, V<main_1_14_b2_below>.8h
    sqrdmulh V<main_1_14_b2_quot>.8h, V<q1_14_b2>.8h, V<tern_recip>.8h
    mls V<q1_14_b2>.8h, V<main_1_14_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_14_c1lo>.16b, V<q1_14_b0>.16b, V<q1_14_b0>.16b, #8
    ext V<q1_14_c1hi>.16b, V<q1_14_b1>.16b, V<q1_14_b1>.16b, #8
    ext V<q1_14_c2hi>.16b, V<q1_14_b2>.16b, V<q1_14_b2>.16b, #8
    st3 {V<q1_14_b0>.4h, V<q1_14_c1lo>.4h, V<q1_14_b2>.4h}, [x2], #24
    st3 {V<q1_14_b1>.4h, V<q1_14_c1hi>.4h, V<q1_14_c2hi>.4h}, [x2], #24
    add x2, x2, #6


    ldr Q<q1_15_b0>, [x1, #752]
    cmgt V<main_1_15_b0_above>.8h, V<q1_15_b0>.8h, V<tern_hi>.8h
    cmgt V<main_1_15_b0_below>.8h, V<tern_lo>.8h, V<q1_15_b0>.8h
    add V<q1_15_b0>.8h, V<q1_15_b0>.8h, V<main_1_15_b0_above>.8h
    sub V<q1_15_b0>.8h, V<q1_15_b0>.8h, V<main_1_15_b0_below>.8h
    sqrdmulh V<main_1_15_b0_quot>.8h, V<q1_15_b0>.8h, V<tern_recip>.8h
    mls V<q1_15_b0>.8h, V<main_1_15_b0_quot>.8h, V<tern_three>.8h
    ldr Q<q1_15_b1>, [x1, #1008]
    cmgt V<main_1_15_b1_above>.8h, V<q1_15_b1>.8h, V<tern_hi>.8h
    cmgt V<main_1_15_b1_below>.8h, V<tern_lo>.8h, V<q1_15_b1>.8h
    add V<q1_15_b1>.8h, V<q1_15_b1>.8h, V<main_1_15_b1_above>.8h
    sub V<q1_15_b1>.8h, V<q1_15_b1>.8h, V<main_1_15_b1_below>.8h
    sqrdmulh V<main_1_15_b1_quot>.8h, V<q1_15_b1>.8h, V<tern_recip>.8h
    mls V<q1_15_b1>.8h, V<main_1_15_b1_quot>.8h, V<tern_three>.8h
    ldr Q<q1_15_b2>, [x1, #1520]
    cmgt V<main_1_15_b2_above>.8h, V<q1_15_b2>.8h, V<tern_hi>.8h
    cmgt V<main_1_15_b2_below>.8h, V<tern_lo>.8h, V<q1_15_b2>.8h
    add V<q1_15_b2>.8h, V<q1_15_b2>.8h, V<main_1_15_b2_above>.8h
    sub V<q1_15_b2>.8h, V<q1_15_b2>.8h, V<main_1_15_b2_below>.8h
    sqrdmulh V<main_1_15_b2_quot>.8h, V<q1_15_b2>.8h, V<tern_recip>.8h
    mls V<q1_15_b2>.8h, V<main_1_15_b2_quot>.8h, V<tern_three>.8h
    ext V<q1_15_c1lo>.16b, V<q1_15_b0>.16b, V<q1_15_b0>.16b, #8
    ext V<q1_15_c1hi>.16b, V<q1_15_b1>.16b, V<q1_15_b1>.16b, #8
    ext V<q1_15_c2hi>.16b, V<q1_15_b2>.16b, V<q1_15_b2>.16b, #8
    st3 {V<q1_15_b0>.4h, V<q1_15_c1lo>.4h, V<q1_15_b2>.4h}, [x2], #24
    st3 {V<q1_15_b1>.4h, V<q1_15_c1hi>.4h, V<q1_15_c2hi>.4h}, [x2], #24
    add x2, x2, #6
    p30_route_pair15_end:
p29_main_route_slothy_end:
    ret

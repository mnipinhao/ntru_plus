#ifdef __APPLE__
#define p32_i16_terminal6 _p32_i16_terminal6
#endif
.text
.global p32_i16_terminal6
p32_i16_terminal6:
// live-in: x0 natural output, x1 six preterminal blocks, x4 composite table
// live-out: exact 768 main natural raw int16 coefficient stores
// coefficient range: preterminal abs<=21397, output abs<=4454
// reserved physical registers: x18-x30, sp, xzr; fixed v26-v31
p32_i16_terminal6_slothy_start:
mov w8, #3457
dup v30.8h, w8
mov w8, #9
dup v31.8h, w8
p32_terminal_0_start:
    ldr q26, [x4, #0]
    ldr q27, [x4, #16]
    ldr q28, [x4, #32]
    ldr q29, [x4, #48]
    p32_terminal_0_g0_start:
    ldr Q<t0_g0_x>, [x1, #0]
    sqrdmulh V<t0_g0_lq>.8h, V<t0_g0_x>.8h, v27.8h
    sqrdmulh V<t0_g0_hq>.8h, V<t0_g0_x>.8h, v29.8h
    mul V<t0_g0_low>.8h, V<t0_g0_x>.8h, v26.8h
    mul V<t0_g0_high>.8h, V<t0_g0_x>.8h, v28.8h
    mls V<t0_g0_low>.8h, V<t0_g0_lq>.8h, v30.8h
    mls V<t0_g0_high>.8h, V<t0_g0_hq>.8h, v30.8h
    ext V<t0_g0_lr>.16b, V<t0_g0_low>.16b, V<t0_g0_low>.16b, #8
    ext V<t0_g0_hr>.16b, V<t0_g0_high>.16b, V<t0_g0_high>.16b, #8
    add V<t0_g0_low>.8h, V<t0_g0_low>.8h, V<t0_g0_lr>.8h
    add V<t0_g0_high>.8h, V<t0_g0_high>.8h, V<t0_g0_hr>.8h
    sqrdmulh V<t0_g0_rl>.8h, V<t0_g0_low>.8h, v31.8h
    mls V<t0_g0_low>.8h, V<t0_g0_rl>.8h, v30.8h
    sqrdmulh V<t0_g0_rh>.8h, V<t0_g0_high>.8h, v31.8h
    mls V<t0_g0_high>.8h, V<t0_g0_rh>.8h, v30.8h
    umov w9, V<t0_g0_high>.h[0]
    strh w9, [x0, #864]
    umov w9, V<t0_g0_high>.h[1]
    strh w9, [x0, #870]
    umov w9, V<t0_g0_high>.h[2]
    strh w9, [x0, #876]
    umov w9, V<t0_g0_high>.h[3]
    strh w9, [x0, #882]
    umov w9, V<t0_g0_low>.h[0]
    strh w9, [x0, #0]
    umov w9, V<t0_g0_low>.h[1]
    strh w9, [x0, #6]
    umov w9, V<t0_g0_low>.h[2]
    strh w9, [x0, #12]
    umov w9, V<t0_g0_low>.h[3]
    strh w9, [x0, #18]
    p32_terminal_0_g0_end:
    p32_terminal_0_g1_start:
    ldr Q<t0_g1_x>, [x1, #256]
    sqrdmulh V<t0_g1_lq>.8h, V<t0_g1_x>.8h, v27.8h
    sqrdmulh V<t0_g1_hq>.8h, V<t0_g1_x>.8h, v29.8h
    mul V<t0_g1_low>.8h, V<t0_g1_x>.8h, v26.8h
    mul V<t0_g1_high>.8h, V<t0_g1_x>.8h, v28.8h
    mls V<t0_g1_low>.8h, V<t0_g1_lq>.8h, v30.8h
    mls V<t0_g1_high>.8h, V<t0_g1_hq>.8h, v30.8h
    ext V<t0_g1_lr>.16b, V<t0_g1_low>.16b, V<t0_g1_low>.16b, #8
    ext V<t0_g1_hr>.16b, V<t0_g1_high>.16b, V<t0_g1_high>.16b, #8
    add V<t0_g1_low>.8h, V<t0_g1_low>.8h, V<t0_g1_lr>.8h
    add V<t0_g1_high>.8h, V<t0_g1_high>.8h, V<t0_g1_hr>.8h
    sqrdmulh V<t0_g1_rl>.8h, V<t0_g1_low>.8h, v31.8h
    mls V<t0_g1_low>.8h, V<t0_g1_rl>.8h, v30.8h
    sqrdmulh V<t0_g1_rh>.8h, V<t0_g1_high>.8h, v31.8h
    mls V<t0_g1_high>.8h, V<t0_g1_rh>.8h, v30.8h
    umov w9, V<t0_g1_high>.h[0]
    strh w9, [x0, #888]
    umov w9, V<t0_g1_high>.h[1]
    strh w9, [x0, #894]
    umov w9, V<t0_g1_high>.h[2]
    strh w9, [x0, #900]
    umov w9, V<t0_g1_high>.h[3]
    strh w9, [x0, #906]
    umov w9, V<t0_g1_low>.h[0]
    strh w9, [x0, #24]
    umov w9, V<t0_g1_low>.h[1]
    strh w9, [x0, #30]
    umov w9, V<t0_g1_low>.h[2]
    strh w9, [x0, #36]
    umov w9, V<t0_g1_low>.h[3]
    strh w9, [x0, #42]
    p32_terminal_0_g1_end:
    p32_terminal_0_g2_start:
    ldr Q<t0_g2_x>, [x1, #512]
    sqrdmulh V<t0_g2_lq>.8h, V<t0_g2_x>.8h, v27.8h
    sqrdmulh V<t0_g2_hq>.8h, V<t0_g2_x>.8h, v29.8h
    mul V<t0_g2_low>.8h, V<t0_g2_x>.8h, v26.8h
    mul V<t0_g2_high>.8h, V<t0_g2_x>.8h, v28.8h
    mls V<t0_g2_low>.8h, V<t0_g2_lq>.8h, v30.8h
    mls V<t0_g2_high>.8h, V<t0_g2_hq>.8h, v30.8h
    ext V<t0_g2_lr>.16b, V<t0_g2_low>.16b, V<t0_g2_low>.16b, #8
    ext V<t0_g2_hr>.16b, V<t0_g2_high>.16b, V<t0_g2_high>.16b, #8
    add V<t0_g2_low>.8h, V<t0_g2_low>.8h, V<t0_g2_lr>.8h
    add V<t0_g2_high>.8h, V<t0_g2_high>.8h, V<t0_g2_hr>.8h
    sqrdmulh V<t0_g2_rl>.8h, V<t0_g2_low>.8h, v31.8h
    mls V<t0_g2_low>.8h, V<t0_g2_rl>.8h, v30.8h
    sqrdmulh V<t0_g2_rh>.8h, V<t0_g2_high>.8h, v31.8h
    mls V<t0_g2_high>.8h, V<t0_g2_rh>.8h, v30.8h
    umov w9, V<t0_g2_high>.h[0]
    strh w9, [x0, #866]
    umov w9, V<t0_g2_high>.h[1]
    strh w9, [x0, #872]
    umov w9, V<t0_g2_high>.h[2]
    strh w9, [x0, #878]
    umov w9, V<t0_g2_high>.h[3]
    strh w9, [x0, #884]
    umov w9, V<t0_g2_low>.h[0]
    strh w9, [x0, #2]
    umov w9, V<t0_g2_low>.h[1]
    strh w9, [x0, #8]
    umov w9, V<t0_g2_low>.h[2]
    strh w9, [x0, #14]
    umov w9, V<t0_g2_low>.h[3]
    strh w9, [x0, #20]
    p32_terminal_0_g2_end:
    p32_terminal_0_g3_start:
    ldr Q<t0_g3_x>, [x1, #768]
    sqrdmulh V<t0_g3_lq>.8h, V<t0_g3_x>.8h, v27.8h
    sqrdmulh V<t0_g3_hq>.8h, V<t0_g3_x>.8h, v29.8h
    mul V<t0_g3_low>.8h, V<t0_g3_x>.8h, v26.8h
    mul V<t0_g3_high>.8h, V<t0_g3_x>.8h, v28.8h
    mls V<t0_g3_low>.8h, V<t0_g3_lq>.8h, v30.8h
    mls V<t0_g3_high>.8h, V<t0_g3_hq>.8h, v30.8h
    ext V<t0_g3_lr>.16b, V<t0_g3_low>.16b, V<t0_g3_low>.16b, #8
    ext V<t0_g3_hr>.16b, V<t0_g3_high>.16b, V<t0_g3_high>.16b, #8
    add V<t0_g3_low>.8h, V<t0_g3_low>.8h, V<t0_g3_lr>.8h
    add V<t0_g3_high>.8h, V<t0_g3_high>.8h, V<t0_g3_hr>.8h
    sqrdmulh V<t0_g3_rl>.8h, V<t0_g3_low>.8h, v31.8h
    mls V<t0_g3_low>.8h, V<t0_g3_rl>.8h, v30.8h
    sqrdmulh V<t0_g3_rh>.8h, V<t0_g3_high>.8h, v31.8h
    mls V<t0_g3_high>.8h, V<t0_g3_rh>.8h, v30.8h
    umov w9, V<t0_g3_high>.h[0]
    strh w9, [x0, #890]
    umov w9, V<t0_g3_high>.h[1]
    strh w9, [x0, #896]
    umov w9, V<t0_g3_high>.h[2]
    strh w9, [x0, #902]
    umov w9, V<t0_g3_high>.h[3]
    strh w9, [x0, #908]
    umov w9, V<t0_g3_low>.h[0]
    strh w9, [x0, #26]
    umov w9, V<t0_g3_low>.h[1]
    strh w9, [x0, #32]
    umov w9, V<t0_g3_low>.h[2]
    strh w9, [x0, #38]
    umov w9, V<t0_g3_low>.h[3]
    strh w9, [x0, #44]
    p32_terminal_0_g3_end:
    p32_terminal_0_g4_start:
    ldr Q<t0_g4_x>, [x1, #1024]
    sqrdmulh V<t0_g4_lq>.8h, V<t0_g4_x>.8h, v27.8h
    sqrdmulh V<t0_g4_hq>.8h, V<t0_g4_x>.8h, v29.8h
    mul V<t0_g4_low>.8h, V<t0_g4_x>.8h, v26.8h
    mul V<t0_g4_high>.8h, V<t0_g4_x>.8h, v28.8h
    mls V<t0_g4_low>.8h, V<t0_g4_lq>.8h, v30.8h
    mls V<t0_g4_high>.8h, V<t0_g4_hq>.8h, v30.8h
    ext V<t0_g4_lr>.16b, V<t0_g4_low>.16b, V<t0_g4_low>.16b, #8
    ext V<t0_g4_hr>.16b, V<t0_g4_high>.16b, V<t0_g4_high>.16b, #8
    add V<t0_g4_low>.8h, V<t0_g4_low>.8h, V<t0_g4_lr>.8h
    add V<t0_g4_high>.8h, V<t0_g4_high>.8h, V<t0_g4_hr>.8h
    sqrdmulh V<t0_g4_rl>.8h, V<t0_g4_low>.8h, v31.8h
    mls V<t0_g4_low>.8h, V<t0_g4_rl>.8h, v30.8h
    sqrdmulh V<t0_g4_rh>.8h, V<t0_g4_high>.8h, v31.8h
    mls V<t0_g4_high>.8h, V<t0_g4_rh>.8h, v30.8h
    umov w9, V<t0_g4_high>.h[0]
    strh w9, [x0, #868]
    umov w9, V<t0_g4_high>.h[1]
    strh w9, [x0, #874]
    umov w9, V<t0_g4_high>.h[2]
    strh w9, [x0, #880]
    umov w9, V<t0_g4_high>.h[3]
    strh w9, [x0, #886]
    umov w9, V<t0_g4_low>.h[0]
    strh w9, [x0, #4]
    umov w9, V<t0_g4_low>.h[1]
    strh w9, [x0, #10]
    umov w9, V<t0_g4_low>.h[2]
    strh w9, [x0, #16]
    umov w9, V<t0_g4_low>.h[3]
    strh w9, [x0, #22]
    p32_terminal_0_g4_end:
    p32_terminal_0_g5_start:
    ldr Q<t0_g5_x>, [x1, #1280]
    sqrdmulh V<t0_g5_lq>.8h, V<t0_g5_x>.8h, v27.8h
    sqrdmulh V<t0_g5_hq>.8h, V<t0_g5_x>.8h, v29.8h
    mul V<t0_g5_low>.8h, V<t0_g5_x>.8h, v26.8h
    mul V<t0_g5_high>.8h, V<t0_g5_x>.8h, v28.8h
    mls V<t0_g5_low>.8h, V<t0_g5_lq>.8h, v30.8h
    mls V<t0_g5_high>.8h, V<t0_g5_hq>.8h, v30.8h
    ext V<t0_g5_lr>.16b, V<t0_g5_low>.16b, V<t0_g5_low>.16b, #8
    ext V<t0_g5_hr>.16b, V<t0_g5_high>.16b, V<t0_g5_high>.16b, #8
    add V<t0_g5_low>.8h, V<t0_g5_low>.8h, V<t0_g5_lr>.8h
    add V<t0_g5_high>.8h, V<t0_g5_high>.8h, V<t0_g5_hr>.8h
    sqrdmulh V<t0_g5_rl>.8h, V<t0_g5_low>.8h, v31.8h
    mls V<t0_g5_low>.8h, V<t0_g5_rl>.8h, v30.8h
    sqrdmulh V<t0_g5_rh>.8h, V<t0_g5_high>.8h, v31.8h
    mls V<t0_g5_high>.8h, V<t0_g5_rh>.8h, v30.8h
    umov w9, V<t0_g5_high>.h[0]
    strh w9, [x0, #892]
    umov w9, V<t0_g5_high>.h[1]
    strh w9, [x0, #898]
    umov w9, V<t0_g5_high>.h[2]
    strh w9, [x0, #904]
    umov w9, V<t0_g5_high>.h[3]
    strh w9, [x0, #910]
    umov w9, V<t0_g5_low>.h[0]
    strh w9, [x0, #28]
    umov w9, V<t0_g5_low>.h[1]
    strh w9, [x0, #34]
    umov w9, V<t0_g5_low>.h[2]
    strh w9, [x0, #40]
    umov w9, V<t0_g5_low>.h[3]
    strh w9, [x0, #46]
    p32_terminal_0_g5_end:
p32_terminal_0_end:
p32_terminal_1_start:
    ldr q26, [x4, #64]
    ldr q27, [x4, #80]
    ldr q28, [x4, #96]
    ldr q29, [x4, #112]
    p32_terminal_1_g0_start:
    ldr Q<t1_g0_x>, [x1, #16]
    sqrdmulh V<t1_g0_lq>.8h, V<t1_g0_x>.8h, v27.8h
    sqrdmulh V<t1_g0_hq>.8h, V<t1_g0_x>.8h, v29.8h
    mul V<t1_g0_low>.8h, V<t1_g0_x>.8h, v26.8h
    mul V<t1_g0_high>.8h, V<t1_g0_x>.8h, v28.8h
    mls V<t1_g0_low>.8h, V<t1_g0_lq>.8h, v30.8h
    mls V<t1_g0_high>.8h, V<t1_g0_hq>.8h, v30.8h
    ext V<t1_g0_lr>.16b, V<t1_g0_low>.16b, V<t1_g0_low>.16b, #8
    ext V<t1_g0_hr>.16b, V<t1_g0_high>.16b, V<t1_g0_high>.16b, #8
    add V<t1_g0_low>.8h, V<t1_g0_low>.8h, V<t1_g0_lr>.8h
    add V<t1_g0_high>.8h, V<t1_g0_high>.8h, V<t1_g0_hr>.8h
    umov w9, V<t1_g0_high>.h[0]
    strh w9, [x0, #918]
    umov w9, V<t1_g0_high>.h[1]
    strh w9, [x0, #924]
    umov w9, V<t1_g0_high>.h[2]
    strh w9, [x0, #930]
    umov w9, V<t1_g0_high>.h[3]
    strh w9, [x0, #936]
    umov w9, V<t1_g0_low>.h[0]
    strh w9, [x0, #54]
    umov w9, V<t1_g0_low>.h[1]
    strh w9, [x0, #60]
    umov w9, V<t1_g0_low>.h[2]
    strh w9, [x0, #66]
    umov w9, V<t1_g0_low>.h[3]
    strh w9, [x0, #72]
    p32_terminal_1_g0_end:
    p32_terminal_1_g1_start:
    ldr Q<t1_g1_x>, [x1, #272]
    sqrdmulh V<t1_g1_lq>.8h, V<t1_g1_x>.8h, v27.8h
    sqrdmulh V<t1_g1_hq>.8h, V<t1_g1_x>.8h, v29.8h
    mul V<t1_g1_low>.8h, V<t1_g1_x>.8h, v26.8h
    mul V<t1_g1_high>.8h, V<t1_g1_x>.8h, v28.8h
    mls V<t1_g1_low>.8h, V<t1_g1_lq>.8h, v30.8h
    mls V<t1_g1_high>.8h, V<t1_g1_hq>.8h, v30.8h
    ext V<t1_g1_lr>.16b, V<t1_g1_low>.16b, V<t1_g1_low>.16b, #8
    ext V<t1_g1_hr>.16b, V<t1_g1_high>.16b, V<t1_g1_high>.16b, #8
    add V<t1_g1_low>.8h, V<t1_g1_low>.8h, V<t1_g1_lr>.8h
    add V<t1_g1_high>.8h, V<t1_g1_high>.8h, V<t1_g1_hr>.8h
    umov w9, V<t1_g1_high>.h[0]
    strh w9, [x0, #942]
    umov w9, V<t1_g1_high>.h[1]
    strh w9, [x0, #948]
    umov w9, V<t1_g1_high>.h[2]
    strh w9, [x0, #954]
    umov w9, V<t1_g1_high>.h[3]
    strh w9, [x0, #960]
    umov w9, V<t1_g1_low>.h[0]
    strh w9, [x0, #78]
    umov w9, V<t1_g1_low>.h[1]
    strh w9, [x0, #84]
    umov w9, V<t1_g1_low>.h[2]
    strh w9, [x0, #90]
    umov w9, V<t1_g1_low>.h[3]
    strh w9, [x0, #96]
    p32_terminal_1_g1_end:
    p32_terminal_1_g2_start:
    ldr Q<t1_g2_x>, [x1, #528]
    sqrdmulh V<t1_g2_lq>.8h, V<t1_g2_x>.8h, v27.8h
    sqrdmulh V<t1_g2_hq>.8h, V<t1_g2_x>.8h, v29.8h
    mul V<t1_g2_low>.8h, V<t1_g2_x>.8h, v26.8h
    mul V<t1_g2_high>.8h, V<t1_g2_x>.8h, v28.8h
    mls V<t1_g2_low>.8h, V<t1_g2_lq>.8h, v30.8h
    mls V<t1_g2_high>.8h, V<t1_g2_hq>.8h, v30.8h
    ext V<t1_g2_lr>.16b, V<t1_g2_low>.16b, V<t1_g2_low>.16b, #8
    ext V<t1_g2_hr>.16b, V<t1_g2_high>.16b, V<t1_g2_high>.16b, #8
    add V<t1_g2_low>.8h, V<t1_g2_low>.8h, V<t1_g2_lr>.8h
    add V<t1_g2_high>.8h, V<t1_g2_high>.8h, V<t1_g2_hr>.8h
    umov w9, V<t1_g2_high>.h[0]
    strh w9, [x0, #920]
    umov w9, V<t1_g2_high>.h[1]
    strh w9, [x0, #926]
    umov w9, V<t1_g2_high>.h[2]
    strh w9, [x0, #932]
    umov w9, V<t1_g2_high>.h[3]
    strh w9, [x0, #938]
    umov w9, V<t1_g2_low>.h[0]
    strh w9, [x0, #56]
    umov w9, V<t1_g2_low>.h[1]
    strh w9, [x0, #62]
    umov w9, V<t1_g2_low>.h[2]
    strh w9, [x0, #68]
    umov w9, V<t1_g2_low>.h[3]
    strh w9, [x0, #74]
    p32_terminal_1_g2_end:
    p32_terminal_1_g3_start:
    ldr Q<t1_g3_x>, [x1, #784]
    sqrdmulh V<t1_g3_lq>.8h, V<t1_g3_x>.8h, v27.8h
    sqrdmulh V<t1_g3_hq>.8h, V<t1_g3_x>.8h, v29.8h
    mul V<t1_g3_low>.8h, V<t1_g3_x>.8h, v26.8h
    mul V<t1_g3_high>.8h, V<t1_g3_x>.8h, v28.8h
    mls V<t1_g3_low>.8h, V<t1_g3_lq>.8h, v30.8h
    mls V<t1_g3_high>.8h, V<t1_g3_hq>.8h, v30.8h
    ext V<t1_g3_lr>.16b, V<t1_g3_low>.16b, V<t1_g3_low>.16b, #8
    ext V<t1_g3_hr>.16b, V<t1_g3_high>.16b, V<t1_g3_high>.16b, #8
    add V<t1_g3_low>.8h, V<t1_g3_low>.8h, V<t1_g3_lr>.8h
    add V<t1_g3_high>.8h, V<t1_g3_high>.8h, V<t1_g3_hr>.8h
    umov w9, V<t1_g3_high>.h[0]
    strh w9, [x0, #944]
    umov w9, V<t1_g3_high>.h[1]
    strh w9, [x0, #950]
    umov w9, V<t1_g3_high>.h[2]
    strh w9, [x0, #956]
    umov w9, V<t1_g3_high>.h[3]
    strh w9, [x0, #962]
    umov w9, V<t1_g3_low>.h[0]
    strh w9, [x0, #80]
    umov w9, V<t1_g3_low>.h[1]
    strh w9, [x0, #86]
    umov w9, V<t1_g3_low>.h[2]
    strh w9, [x0, #92]
    umov w9, V<t1_g3_low>.h[3]
    strh w9, [x0, #98]
    p32_terminal_1_g3_end:
    p32_terminal_1_g4_start:
    ldr Q<t1_g4_x>, [x1, #1040]
    sqrdmulh V<t1_g4_lq>.8h, V<t1_g4_x>.8h, v27.8h
    sqrdmulh V<t1_g4_hq>.8h, V<t1_g4_x>.8h, v29.8h
    mul V<t1_g4_low>.8h, V<t1_g4_x>.8h, v26.8h
    mul V<t1_g4_high>.8h, V<t1_g4_x>.8h, v28.8h
    mls V<t1_g4_low>.8h, V<t1_g4_lq>.8h, v30.8h
    mls V<t1_g4_high>.8h, V<t1_g4_hq>.8h, v30.8h
    ext V<t1_g4_lr>.16b, V<t1_g4_low>.16b, V<t1_g4_low>.16b, #8
    ext V<t1_g4_hr>.16b, V<t1_g4_high>.16b, V<t1_g4_high>.16b, #8
    add V<t1_g4_low>.8h, V<t1_g4_low>.8h, V<t1_g4_lr>.8h
    add V<t1_g4_high>.8h, V<t1_g4_high>.8h, V<t1_g4_hr>.8h
    umov w9, V<t1_g4_high>.h[0]
    strh w9, [x0, #922]
    umov w9, V<t1_g4_high>.h[1]
    strh w9, [x0, #928]
    umov w9, V<t1_g4_high>.h[2]
    strh w9, [x0, #934]
    umov w9, V<t1_g4_high>.h[3]
    strh w9, [x0, #940]
    umov w9, V<t1_g4_low>.h[0]
    strh w9, [x0, #58]
    umov w9, V<t1_g4_low>.h[1]
    strh w9, [x0, #64]
    umov w9, V<t1_g4_low>.h[2]
    strh w9, [x0, #70]
    umov w9, V<t1_g4_low>.h[3]
    strh w9, [x0, #76]
    p32_terminal_1_g4_end:
    p32_terminal_1_g5_start:
    ldr Q<t1_g5_x>, [x1, #1296]
    sqrdmulh V<t1_g5_lq>.8h, V<t1_g5_x>.8h, v27.8h
    sqrdmulh V<t1_g5_hq>.8h, V<t1_g5_x>.8h, v29.8h
    mul V<t1_g5_low>.8h, V<t1_g5_x>.8h, v26.8h
    mul V<t1_g5_high>.8h, V<t1_g5_x>.8h, v28.8h
    mls V<t1_g5_low>.8h, V<t1_g5_lq>.8h, v30.8h
    mls V<t1_g5_high>.8h, V<t1_g5_hq>.8h, v30.8h
    ext V<t1_g5_lr>.16b, V<t1_g5_low>.16b, V<t1_g5_low>.16b, #8
    ext V<t1_g5_hr>.16b, V<t1_g5_high>.16b, V<t1_g5_high>.16b, #8
    add V<t1_g5_low>.8h, V<t1_g5_low>.8h, V<t1_g5_lr>.8h
    add V<t1_g5_high>.8h, V<t1_g5_high>.8h, V<t1_g5_hr>.8h
    umov w9, V<t1_g5_high>.h[0]
    strh w9, [x0, #946]
    umov w9, V<t1_g5_high>.h[1]
    strh w9, [x0, #952]
    umov w9, V<t1_g5_high>.h[2]
    strh w9, [x0, #958]
    umov w9, V<t1_g5_high>.h[3]
    strh w9, [x0, #964]
    umov w9, V<t1_g5_low>.h[0]
    strh w9, [x0, #82]
    umov w9, V<t1_g5_low>.h[1]
    strh w9, [x0, #88]
    umov w9, V<t1_g5_low>.h[2]
    strh w9, [x0, #94]
    umov w9, V<t1_g5_low>.h[3]
    strh w9, [x0, #100]
    p32_terminal_1_g5_end:
p32_terminal_1_end:
p32_terminal_2_start:
    ldr q26, [x4, #128]
    ldr q27, [x4, #144]
    ldr q28, [x4, #160]
    ldr q29, [x4, #176]
    p32_terminal_2_g0_start:
    ldr Q<t2_g0_x>, [x1, #32]
    sqrdmulh V<t2_g0_lq>.8h, V<t2_g0_x>.8h, v27.8h
    sqrdmulh V<t2_g0_hq>.8h, V<t2_g0_x>.8h, v29.8h
    mul V<t2_g0_low>.8h, V<t2_g0_x>.8h, v26.8h
    mul V<t2_g0_high>.8h, V<t2_g0_x>.8h, v28.8h
    mls V<t2_g0_low>.8h, V<t2_g0_lq>.8h, v30.8h
    mls V<t2_g0_high>.8h, V<t2_g0_hq>.8h, v30.8h
    ext V<t2_g0_lr>.16b, V<t2_g0_low>.16b, V<t2_g0_low>.16b, #8
    ext V<t2_g0_hr>.16b, V<t2_g0_high>.16b, V<t2_g0_high>.16b, #8
    add V<t2_g0_low>.8h, V<t2_g0_low>.8h, V<t2_g0_lr>.8h
    add V<t2_g0_high>.8h, V<t2_g0_high>.8h, V<t2_g0_hr>.8h
    sqrdmulh V<t2_g0_rh>.8h, V<t2_g0_high>.8h, v31.8h
    mls V<t2_g0_high>.8h, V<t2_g0_rh>.8h, v30.8h
    umov w9, V<t2_g0_high>.h[0]
    strh w9, [x0, #972]
    umov w9, V<t2_g0_high>.h[1]
    strh w9, [x0, #978]
    umov w9, V<t2_g0_high>.h[2]
    strh w9, [x0, #984]
    umov w9, V<t2_g0_high>.h[3]
    strh w9, [x0, #990]
    umov w9, V<t2_g0_low>.h[0]
    strh w9, [x0, #108]
    umov w9, V<t2_g0_low>.h[1]
    strh w9, [x0, #114]
    umov w9, V<t2_g0_low>.h[2]
    strh w9, [x0, #120]
    umov w9, V<t2_g0_low>.h[3]
    strh w9, [x0, #126]
    p32_terminal_2_g0_end:
    p32_terminal_2_g1_start:
    ldr Q<t2_g1_x>, [x1, #288]
    sqrdmulh V<t2_g1_lq>.8h, V<t2_g1_x>.8h, v27.8h
    sqrdmulh V<t2_g1_hq>.8h, V<t2_g1_x>.8h, v29.8h
    mul V<t2_g1_low>.8h, V<t2_g1_x>.8h, v26.8h
    mul V<t2_g1_high>.8h, V<t2_g1_x>.8h, v28.8h
    mls V<t2_g1_low>.8h, V<t2_g1_lq>.8h, v30.8h
    mls V<t2_g1_high>.8h, V<t2_g1_hq>.8h, v30.8h
    ext V<t2_g1_lr>.16b, V<t2_g1_low>.16b, V<t2_g1_low>.16b, #8
    ext V<t2_g1_hr>.16b, V<t2_g1_high>.16b, V<t2_g1_high>.16b, #8
    add V<t2_g1_low>.8h, V<t2_g1_low>.8h, V<t2_g1_lr>.8h
    add V<t2_g1_high>.8h, V<t2_g1_high>.8h, V<t2_g1_hr>.8h
    sqrdmulh V<t2_g1_rh>.8h, V<t2_g1_high>.8h, v31.8h
    mls V<t2_g1_high>.8h, V<t2_g1_rh>.8h, v30.8h
    umov w9, V<t2_g1_high>.h[0]
    strh w9, [x0, #996]
    umov w9, V<t2_g1_high>.h[1]
    strh w9, [x0, #1002]
    umov w9, V<t2_g1_high>.h[2]
    strh w9, [x0, #1008]
    umov w9, V<t2_g1_high>.h[3]
    strh w9, [x0, #1014]
    umov w9, V<t2_g1_low>.h[0]
    strh w9, [x0, #132]
    umov w9, V<t2_g1_low>.h[1]
    strh w9, [x0, #138]
    umov w9, V<t2_g1_low>.h[2]
    strh w9, [x0, #144]
    umov w9, V<t2_g1_low>.h[3]
    strh w9, [x0, #150]
    p32_terminal_2_g1_end:
    p32_terminal_2_g2_start:
    ldr Q<t2_g2_x>, [x1, #544]
    sqrdmulh V<t2_g2_lq>.8h, V<t2_g2_x>.8h, v27.8h
    sqrdmulh V<t2_g2_hq>.8h, V<t2_g2_x>.8h, v29.8h
    mul V<t2_g2_low>.8h, V<t2_g2_x>.8h, v26.8h
    mul V<t2_g2_high>.8h, V<t2_g2_x>.8h, v28.8h
    mls V<t2_g2_low>.8h, V<t2_g2_lq>.8h, v30.8h
    mls V<t2_g2_high>.8h, V<t2_g2_hq>.8h, v30.8h
    ext V<t2_g2_lr>.16b, V<t2_g2_low>.16b, V<t2_g2_low>.16b, #8
    ext V<t2_g2_hr>.16b, V<t2_g2_high>.16b, V<t2_g2_high>.16b, #8
    add V<t2_g2_low>.8h, V<t2_g2_low>.8h, V<t2_g2_lr>.8h
    add V<t2_g2_high>.8h, V<t2_g2_high>.8h, V<t2_g2_hr>.8h
    sqrdmulh V<t2_g2_rh>.8h, V<t2_g2_high>.8h, v31.8h
    mls V<t2_g2_high>.8h, V<t2_g2_rh>.8h, v30.8h
    umov w9, V<t2_g2_high>.h[0]
    strh w9, [x0, #974]
    umov w9, V<t2_g2_high>.h[1]
    strh w9, [x0, #980]
    umov w9, V<t2_g2_high>.h[2]
    strh w9, [x0, #986]
    umov w9, V<t2_g2_high>.h[3]
    strh w9, [x0, #992]
    umov w9, V<t2_g2_low>.h[0]
    strh w9, [x0, #110]
    umov w9, V<t2_g2_low>.h[1]
    strh w9, [x0, #116]
    umov w9, V<t2_g2_low>.h[2]
    strh w9, [x0, #122]
    umov w9, V<t2_g2_low>.h[3]
    strh w9, [x0, #128]
    p32_terminal_2_g2_end:
    p32_terminal_2_g3_start:
    ldr Q<t2_g3_x>, [x1, #800]
    sqrdmulh V<t2_g3_lq>.8h, V<t2_g3_x>.8h, v27.8h
    sqrdmulh V<t2_g3_hq>.8h, V<t2_g3_x>.8h, v29.8h
    mul V<t2_g3_low>.8h, V<t2_g3_x>.8h, v26.8h
    mul V<t2_g3_high>.8h, V<t2_g3_x>.8h, v28.8h
    mls V<t2_g3_low>.8h, V<t2_g3_lq>.8h, v30.8h
    mls V<t2_g3_high>.8h, V<t2_g3_hq>.8h, v30.8h
    ext V<t2_g3_lr>.16b, V<t2_g3_low>.16b, V<t2_g3_low>.16b, #8
    ext V<t2_g3_hr>.16b, V<t2_g3_high>.16b, V<t2_g3_high>.16b, #8
    add V<t2_g3_low>.8h, V<t2_g3_low>.8h, V<t2_g3_lr>.8h
    add V<t2_g3_high>.8h, V<t2_g3_high>.8h, V<t2_g3_hr>.8h
    sqrdmulh V<t2_g3_rh>.8h, V<t2_g3_high>.8h, v31.8h
    mls V<t2_g3_high>.8h, V<t2_g3_rh>.8h, v30.8h
    umov w9, V<t2_g3_high>.h[0]
    strh w9, [x0, #998]
    umov w9, V<t2_g3_high>.h[1]
    strh w9, [x0, #1004]
    umov w9, V<t2_g3_high>.h[2]
    strh w9, [x0, #1010]
    umov w9, V<t2_g3_high>.h[3]
    strh w9, [x0, #1016]
    umov w9, V<t2_g3_low>.h[0]
    strh w9, [x0, #134]
    umov w9, V<t2_g3_low>.h[1]
    strh w9, [x0, #140]
    umov w9, V<t2_g3_low>.h[2]
    strh w9, [x0, #146]
    umov w9, V<t2_g3_low>.h[3]
    strh w9, [x0, #152]
    p32_terminal_2_g3_end:
    p32_terminal_2_g4_start:
    ldr Q<t2_g4_x>, [x1, #1056]
    sqrdmulh V<t2_g4_lq>.8h, V<t2_g4_x>.8h, v27.8h
    sqrdmulh V<t2_g4_hq>.8h, V<t2_g4_x>.8h, v29.8h
    mul V<t2_g4_low>.8h, V<t2_g4_x>.8h, v26.8h
    mul V<t2_g4_high>.8h, V<t2_g4_x>.8h, v28.8h
    mls V<t2_g4_low>.8h, V<t2_g4_lq>.8h, v30.8h
    mls V<t2_g4_high>.8h, V<t2_g4_hq>.8h, v30.8h
    ext V<t2_g4_lr>.16b, V<t2_g4_low>.16b, V<t2_g4_low>.16b, #8
    ext V<t2_g4_hr>.16b, V<t2_g4_high>.16b, V<t2_g4_high>.16b, #8
    add V<t2_g4_low>.8h, V<t2_g4_low>.8h, V<t2_g4_lr>.8h
    add V<t2_g4_high>.8h, V<t2_g4_high>.8h, V<t2_g4_hr>.8h
    sqrdmulh V<t2_g4_rh>.8h, V<t2_g4_high>.8h, v31.8h
    mls V<t2_g4_high>.8h, V<t2_g4_rh>.8h, v30.8h
    umov w9, V<t2_g4_high>.h[0]
    strh w9, [x0, #976]
    umov w9, V<t2_g4_high>.h[1]
    strh w9, [x0, #982]
    umov w9, V<t2_g4_high>.h[2]
    strh w9, [x0, #988]
    umov w9, V<t2_g4_high>.h[3]
    strh w9, [x0, #994]
    umov w9, V<t2_g4_low>.h[0]
    strh w9, [x0, #112]
    umov w9, V<t2_g4_low>.h[1]
    strh w9, [x0, #118]
    umov w9, V<t2_g4_low>.h[2]
    strh w9, [x0, #124]
    umov w9, V<t2_g4_low>.h[3]
    strh w9, [x0, #130]
    p32_terminal_2_g4_end:
    p32_terminal_2_g5_start:
    ldr Q<t2_g5_x>, [x1, #1312]
    sqrdmulh V<t2_g5_lq>.8h, V<t2_g5_x>.8h, v27.8h
    sqrdmulh V<t2_g5_hq>.8h, V<t2_g5_x>.8h, v29.8h
    mul V<t2_g5_low>.8h, V<t2_g5_x>.8h, v26.8h
    mul V<t2_g5_high>.8h, V<t2_g5_x>.8h, v28.8h
    mls V<t2_g5_low>.8h, V<t2_g5_lq>.8h, v30.8h
    mls V<t2_g5_high>.8h, V<t2_g5_hq>.8h, v30.8h
    ext V<t2_g5_lr>.16b, V<t2_g5_low>.16b, V<t2_g5_low>.16b, #8
    ext V<t2_g5_hr>.16b, V<t2_g5_high>.16b, V<t2_g5_high>.16b, #8
    add V<t2_g5_low>.8h, V<t2_g5_low>.8h, V<t2_g5_lr>.8h
    add V<t2_g5_high>.8h, V<t2_g5_high>.8h, V<t2_g5_hr>.8h
    sqrdmulh V<t2_g5_rh>.8h, V<t2_g5_high>.8h, v31.8h
    mls V<t2_g5_high>.8h, V<t2_g5_rh>.8h, v30.8h
    umov w9, V<t2_g5_high>.h[0]
    strh w9, [x0, #1000]
    umov w9, V<t2_g5_high>.h[1]
    strh w9, [x0, #1006]
    umov w9, V<t2_g5_high>.h[2]
    strh w9, [x0, #1012]
    umov w9, V<t2_g5_high>.h[3]
    strh w9, [x0, #1018]
    umov w9, V<t2_g5_low>.h[0]
    strh w9, [x0, #136]
    umov w9, V<t2_g5_low>.h[1]
    strh w9, [x0, #142]
    umov w9, V<t2_g5_low>.h[2]
    strh w9, [x0, #148]
    umov w9, V<t2_g5_low>.h[3]
    strh w9, [x0, #154]
    p32_terminal_2_g5_end:
p32_terminal_2_end:
p32_terminal_3_start:
    ldr q26, [x4, #192]
    ldr q27, [x4, #208]
    ldr q28, [x4, #224]
    ldr q29, [x4, #240]
    p32_terminal_3_g0_start:
    ldr Q<t3_g0_x>, [x1, #48]
    sqrdmulh V<t3_g0_lq>.8h, V<t3_g0_x>.8h, v27.8h
    sqrdmulh V<t3_g0_hq>.8h, V<t3_g0_x>.8h, v29.8h
    mul V<t3_g0_low>.8h, V<t3_g0_x>.8h, v26.8h
    mul V<t3_g0_high>.8h, V<t3_g0_x>.8h, v28.8h
    mls V<t3_g0_low>.8h, V<t3_g0_lq>.8h, v30.8h
    mls V<t3_g0_high>.8h, V<t3_g0_hq>.8h, v30.8h
    ext V<t3_g0_lr>.16b, V<t3_g0_low>.16b, V<t3_g0_low>.16b, #8
    ext V<t3_g0_hr>.16b, V<t3_g0_high>.16b, V<t3_g0_high>.16b, #8
    add V<t3_g0_low>.8h, V<t3_g0_low>.8h, V<t3_g0_lr>.8h
    add V<t3_g0_high>.8h, V<t3_g0_high>.8h, V<t3_g0_hr>.8h
    umov w9, V<t3_g0_high>.h[0]
    strh w9, [x0, #1026]
    umov w9, V<t3_g0_high>.h[1]
    strh w9, [x0, #1032]
    umov w9, V<t3_g0_high>.h[2]
    strh w9, [x0, #1038]
    umov w9, V<t3_g0_high>.h[3]
    strh w9, [x0, #1044]
    umov w9, V<t3_g0_low>.h[0]
    strh w9, [x0, #162]
    umov w9, V<t3_g0_low>.h[1]
    strh w9, [x0, #168]
    umov w9, V<t3_g0_low>.h[2]
    strh w9, [x0, #174]
    umov w9, V<t3_g0_low>.h[3]
    strh w9, [x0, #180]
    p32_terminal_3_g0_end:
    p32_terminal_3_g1_start:
    ldr Q<t3_g1_x>, [x1, #304]
    sqrdmulh V<t3_g1_lq>.8h, V<t3_g1_x>.8h, v27.8h
    sqrdmulh V<t3_g1_hq>.8h, V<t3_g1_x>.8h, v29.8h
    mul V<t3_g1_low>.8h, V<t3_g1_x>.8h, v26.8h
    mul V<t3_g1_high>.8h, V<t3_g1_x>.8h, v28.8h
    mls V<t3_g1_low>.8h, V<t3_g1_lq>.8h, v30.8h
    mls V<t3_g1_high>.8h, V<t3_g1_hq>.8h, v30.8h
    ext V<t3_g1_lr>.16b, V<t3_g1_low>.16b, V<t3_g1_low>.16b, #8
    ext V<t3_g1_hr>.16b, V<t3_g1_high>.16b, V<t3_g1_high>.16b, #8
    add V<t3_g1_low>.8h, V<t3_g1_low>.8h, V<t3_g1_lr>.8h
    add V<t3_g1_high>.8h, V<t3_g1_high>.8h, V<t3_g1_hr>.8h
    umov w9, V<t3_g1_high>.h[0]
    strh w9, [x0, #1050]
    umov w9, V<t3_g1_high>.h[1]
    strh w9, [x0, #1056]
    umov w9, V<t3_g1_high>.h[2]
    strh w9, [x0, #1062]
    umov w9, V<t3_g1_high>.h[3]
    strh w9, [x0, #1068]
    umov w9, V<t3_g1_low>.h[0]
    strh w9, [x0, #186]
    umov w9, V<t3_g1_low>.h[1]
    strh w9, [x0, #192]
    umov w9, V<t3_g1_low>.h[2]
    strh w9, [x0, #198]
    umov w9, V<t3_g1_low>.h[3]
    strh w9, [x0, #204]
    p32_terminal_3_g1_end:
    p32_terminal_3_g2_start:
    ldr Q<t3_g2_x>, [x1, #560]
    sqrdmulh V<t3_g2_lq>.8h, V<t3_g2_x>.8h, v27.8h
    sqrdmulh V<t3_g2_hq>.8h, V<t3_g2_x>.8h, v29.8h
    mul V<t3_g2_low>.8h, V<t3_g2_x>.8h, v26.8h
    mul V<t3_g2_high>.8h, V<t3_g2_x>.8h, v28.8h
    mls V<t3_g2_low>.8h, V<t3_g2_lq>.8h, v30.8h
    mls V<t3_g2_high>.8h, V<t3_g2_hq>.8h, v30.8h
    ext V<t3_g2_lr>.16b, V<t3_g2_low>.16b, V<t3_g2_low>.16b, #8
    ext V<t3_g2_hr>.16b, V<t3_g2_high>.16b, V<t3_g2_high>.16b, #8
    add V<t3_g2_low>.8h, V<t3_g2_low>.8h, V<t3_g2_lr>.8h
    add V<t3_g2_high>.8h, V<t3_g2_high>.8h, V<t3_g2_hr>.8h
    umov w9, V<t3_g2_high>.h[0]
    strh w9, [x0, #1028]
    umov w9, V<t3_g2_high>.h[1]
    strh w9, [x0, #1034]
    umov w9, V<t3_g2_high>.h[2]
    strh w9, [x0, #1040]
    umov w9, V<t3_g2_high>.h[3]
    strh w9, [x0, #1046]
    umov w9, V<t3_g2_low>.h[0]
    strh w9, [x0, #164]
    umov w9, V<t3_g2_low>.h[1]
    strh w9, [x0, #170]
    umov w9, V<t3_g2_low>.h[2]
    strh w9, [x0, #176]
    umov w9, V<t3_g2_low>.h[3]
    strh w9, [x0, #182]
    p32_terminal_3_g2_end:
    p32_terminal_3_g3_start:
    ldr Q<t3_g3_x>, [x1, #816]
    sqrdmulh V<t3_g3_lq>.8h, V<t3_g3_x>.8h, v27.8h
    sqrdmulh V<t3_g3_hq>.8h, V<t3_g3_x>.8h, v29.8h
    mul V<t3_g3_low>.8h, V<t3_g3_x>.8h, v26.8h
    mul V<t3_g3_high>.8h, V<t3_g3_x>.8h, v28.8h
    mls V<t3_g3_low>.8h, V<t3_g3_lq>.8h, v30.8h
    mls V<t3_g3_high>.8h, V<t3_g3_hq>.8h, v30.8h
    ext V<t3_g3_lr>.16b, V<t3_g3_low>.16b, V<t3_g3_low>.16b, #8
    ext V<t3_g3_hr>.16b, V<t3_g3_high>.16b, V<t3_g3_high>.16b, #8
    add V<t3_g3_low>.8h, V<t3_g3_low>.8h, V<t3_g3_lr>.8h
    add V<t3_g3_high>.8h, V<t3_g3_high>.8h, V<t3_g3_hr>.8h
    umov w9, V<t3_g3_high>.h[0]
    strh w9, [x0, #1052]
    umov w9, V<t3_g3_high>.h[1]
    strh w9, [x0, #1058]
    umov w9, V<t3_g3_high>.h[2]
    strh w9, [x0, #1064]
    umov w9, V<t3_g3_high>.h[3]
    strh w9, [x0, #1070]
    umov w9, V<t3_g3_low>.h[0]
    strh w9, [x0, #188]
    umov w9, V<t3_g3_low>.h[1]
    strh w9, [x0, #194]
    umov w9, V<t3_g3_low>.h[2]
    strh w9, [x0, #200]
    umov w9, V<t3_g3_low>.h[3]
    strh w9, [x0, #206]
    p32_terminal_3_g3_end:
    p32_terminal_3_g4_start:
    ldr Q<t3_g4_x>, [x1, #1072]
    sqrdmulh V<t3_g4_lq>.8h, V<t3_g4_x>.8h, v27.8h
    sqrdmulh V<t3_g4_hq>.8h, V<t3_g4_x>.8h, v29.8h
    mul V<t3_g4_low>.8h, V<t3_g4_x>.8h, v26.8h
    mul V<t3_g4_high>.8h, V<t3_g4_x>.8h, v28.8h
    mls V<t3_g4_low>.8h, V<t3_g4_lq>.8h, v30.8h
    mls V<t3_g4_high>.8h, V<t3_g4_hq>.8h, v30.8h
    ext V<t3_g4_lr>.16b, V<t3_g4_low>.16b, V<t3_g4_low>.16b, #8
    ext V<t3_g4_hr>.16b, V<t3_g4_high>.16b, V<t3_g4_high>.16b, #8
    add V<t3_g4_low>.8h, V<t3_g4_low>.8h, V<t3_g4_lr>.8h
    add V<t3_g4_high>.8h, V<t3_g4_high>.8h, V<t3_g4_hr>.8h
    umov w9, V<t3_g4_high>.h[0]
    strh w9, [x0, #1030]
    umov w9, V<t3_g4_high>.h[1]
    strh w9, [x0, #1036]
    umov w9, V<t3_g4_high>.h[2]
    strh w9, [x0, #1042]
    umov w9, V<t3_g4_high>.h[3]
    strh w9, [x0, #1048]
    umov w9, V<t3_g4_low>.h[0]
    strh w9, [x0, #166]
    umov w9, V<t3_g4_low>.h[1]
    strh w9, [x0, #172]
    umov w9, V<t3_g4_low>.h[2]
    strh w9, [x0, #178]
    umov w9, V<t3_g4_low>.h[3]
    strh w9, [x0, #184]
    p32_terminal_3_g4_end:
    p32_terminal_3_g5_start:
    ldr Q<t3_g5_x>, [x1, #1328]
    sqrdmulh V<t3_g5_lq>.8h, V<t3_g5_x>.8h, v27.8h
    sqrdmulh V<t3_g5_hq>.8h, V<t3_g5_x>.8h, v29.8h
    mul V<t3_g5_low>.8h, V<t3_g5_x>.8h, v26.8h
    mul V<t3_g5_high>.8h, V<t3_g5_x>.8h, v28.8h
    mls V<t3_g5_low>.8h, V<t3_g5_lq>.8h, v30.8h
    mls V<t3_g5_high>.8h, V<t3_g5_hq>.8h, v30.8h
    ext V<t3_g5_lr>.16b, V<t3_g5_low>.16b, V<t3_g5_low>.16b, #8
    ext V<t3_g5_hr>.16b, V<t3_g5_high>.16b, V<t3_g5_high>.16b, #8
    add V<t3_g5_low>.8h, V<t3_g5_low>.8h, V<t3_g5_lr>.8h
    add V<t3_g5_high>.8h, V<t3_g5_high>.8h, V<t3_g5_hr>.8h
    umov w9, V<t3_g5_high>.h[0]
    strh w9, [x0, #1054]
    umov w9, V<t3_g5_high>.h[1]
    strh w9, [x0, #1060]
    umov w9, V<t3_g5_high>.h[2]
    strh w9, [x0, #1066]
    umov w9, V<t3_g5_high>.h[3]
    strh w9, [x0, #1072]
    umov w9, V<t3_g5_low>.h[0]
    strh w9, [x0, #190]
    umov w9, V<t3_g5_low>.h[1]
    strh w9, [x0, #196]
    umov w9, V<t3_g5_low>.h[2]
    strh w9, [x0, #202]
    umov w9, V<t3_g5_low>.h[3]
    strh w9, [x0, #208]
    p32_terminal_3_g5_end:
p32_terminal_3_end:
p32_terminal_4_start:
    ldr q26, [x4, #256]
    ldr q27, [x4, #272]
    ldr q28, [x4, #288]
    ldr q29, [x4, #304]
    p32_terminal_4_g0_start:
    ldr Q<t4_g0_x>, [x1, #64]
    sqrdmulh V<t4_g0_lq>.8h, V<t4_g0_x>.8h, v27.8h
    sqrdmulh V<t4_g0_hq>.8h, V<t4_g0_x>.8h, v29.8h
    mul V<t4_g0_low>.8h, V<t4_g0_x>.8h, v26.8h
    mul V<t4_g0_high>.8h, V<t4_g0_x>.8h, v28.8h
    mls V<t4_g0_low>.8h, V<t4_g0_lq>.8h, v30.8h
    mls V<t4_g0_high>.8h, V<t4_g0_hq>.8h, v30.8h
    ext V<t4_g0_lr>.16b, V<t4_g0_low>.16b, V<t4_g0_low>.16b, #8
    ext V<t4_g0_hr>.16b, V<t4_g0_high>.16b, V<t4_g0_high>.16b, #8
    add V<t4_g0_low>.8h, V<t4_g0_low>.8h, V<t4_g0_lr>.8h
    add V<t4_g0_high>.8h, V<t4_g0_high>.8h, V<t4_g0_hr>.8h
    umov w9, V<t4_g0_high>.h[0]
    strh w9, [x0, #1080]
    umov w9, V<t4_g0_high>.h[1]
    strh w9, [x0, #1086]
    umov w9, V<t4_g0_high>.h[2]
    strh w9, [x0, #1092]
    umov w9, V<t4_g0_high>.h[3]
    strh w9, [x0, #1098]
    umov w9, V<t4_g0_low>.h[0]
    strh w9, [x0, #216]
    umov w9, V<t4_g0_low>.h[1]
    strh w9, [x0, #222]
    umov w9, V<t4_g0_low>.h[2]
    strh w9, [x0, #228]
    umov w9, V<t4_g0_low>.h[3]
    strh w9, [x0, #234]
    p32_terminal_4_g0_end:
    p32_terminal_4_g1_start:
    ldr Q<t4_g1_x>, [x1, #320]
    sqrdmulh V<t4_g1_lq>.8h, V<t4_g1_x>.8h, v27.8h
    sqrdmulh V<t4_g1_hq>.8h, V<t4_g1_x>.8h, v29.8h
    mul V<t4_g1_low>.8h, V<t4_g1_x>.8h, v26.8h
    mul V<t4_g1_high>.8h, V<t4_g1_x>.8h, v28.8h
    mls V<t4_g1_low>.8h, V<t4_g1_lq>.8h, v30.8h
    mls V<t4_g1_high>.8h, V<t4_g1_hq>.8h, v30.8h
    ext V<t4_g1_lr>.16b, V<t4_g1_low>.16b, V<t4_g1_low>.16b, #8
    ext V<t4_g1_hr>.16b, V<t4_g1_high>.16b, V<t4_g1_high>.16b, #8
    add V<t4_g1_low>.8h, V<t4_g1_low>.8h, V<t4_g1_lr>.8h
    add V<t4_g1_high>.8h, V<t4_g1_high>.8h, V<t4_g1_hr>.8h
    umov w9, V<t4_g1_high>.h[0]
    strh w9, [x0, #1104]
    umov w9, V<t4_g1_high>.h[1]
    strh w9, [x0, #1110]
    umov w9, V<t4_g1_high>.h[2]
    strh w9, [x0, #1116]
    umov w9, V<t4_g1_high>.h[3]
    strh w9, [x0, #1122]
    umov w9, V<t4_g1_low>.h[0]
    strh w9, [x0, #240]
    umov w9, V<t4_g1_low>.h[1]
    strh w9, [x0, #246]
    umov w9, V<t4_g1_low>.h[2]
    strh w9, [x0, #252]
    umov w9, V<t4_g1_low>.h[3]
    strh w9, [x0, #258]
    p32_terminal_4_g1_end:
    p32_terminal_4_g2_start:
    ldr Q<t4_g2_x>, [x1, #576]
    sqrdmulh V<t4_g2_lq>.8h, V<t4_g2_x>.8h, v27.8h
    sqrdmulh V<t4_g2_hq>.8h, V<t4_g2_x>.8h, v29.8h
    mul V<t4_g2_low>.8h, V<t4_g2_x>.8h, v26.8h
    mul V<t4_g2_high>.8h, V<t4_g2_x>.8h, v28.8h
    mls V<t4_g2_low>.8h, V<t4_g2_lq>.8h, v30.8h
    mls V<t4_g2_high>.8h, V<t4_g2_hq>.8h, v30.8h
    ext V<t4_g2_lr>.16b, V<t4_g2_low>.16b, V<t4_g2_low>.16b, #8
    ext V<t4_g2_hr>.16b, V<t4_g2_high>.16b, V<t4_g2_high>.16b, #8
    add V<t4_g2_low>.8h, V<t4_g2_low>.8h, V<t4_g2_lr>.8h
    add V<t4_g2_high>.8h, V<t4_g2_high>.8h, V<t4_g2_hr>.8h
    umov w9, V<t4_g2_high>.h[0]
    strh w9, [x0, #1082]
    umov w9, V<t4_g2_high>.h[1]
    strh w9, [x0, #1088]
    umov w9, V<t4_g2_high>.h[2]
    strh w9, [x0, #1094]
    umov w9, V<t4_g2_high>.h[3]
    strh w9, [x0, #1100]
    umov w9, V<t4_g2_low>.h[0]
    strh w9, [x0, #218]
    umov w9, V<t4_g2_low>.h[1]
    strh w9, [x0, #224]
    umov w9, V<t4_g2_low>.h[2]
    strh w9, [x0, #230]
    umov w9, V<t4_g2_low>.h[3]
    strh w9, [x0, #236]
    p32_terminal_4_g2_end:
    p32_terminal_4_g3_start:
    ldr Q<t4_g3_x>, [x1, #832]
    sqrdmulh V<t4_g3_lq>.8h, V<t4_g3_x>.8h, v27.8h
    sqrdmulh V<t4_g3_hq>.8h, V<t4_g3_x>.8h, v29.8h
    mul V<t4_g3_low>.8h, V<t4_g3_x>.8h, v26.8h
    mul V<t4_g3_high>.8h, V<t4_g3_x>.8h, v28.8h
    mls V<t4_g3_low>.8h, V<t4_g3_lq>.8h, v30.8h
    mls V<t4_g3_high>.8h, V<t4_g3_hq>.8h, v30.8h
    ext V<t4_g3_lr>.16b, V<t4_g3_low>.16b, V<t4_g3_low>.16b, #8
    ext V<t4_g3_hr>.16b, V<t4_g3_high>.16b, V<t4_g3_high>.16b, #8
    add V<t4_g3_low>.8h, V<t4_g3_low>.8h, V<t4_g3_lr>.8h
    add V<t4_g3_high>.8h, V<t4_g3_high>.8h, V<t4_g3_hr>.8h
    umov w9, V<t4_g3_high>.h[0]
    strh w9, [x0, #1106]
    umov w9, V<t4_g3_high>.h[1]
    strh w9, [x0, #1112]
    umov w9, V<t4_g3_high>.h[2]
    strh w9, [x0, #1118]
    umov w9, V<t4_g3_high>.h[3]
    strh w9, [x0, #1124]
    umov w9, V<t4_g3_low>.h[0]
    strh w9, [x0, #242]
    umov w9, V<t4_g3_low>.h[1]
    strh w9, [x0, #248]
    umov w9, V<t4_g3_low>.h[2]
    strh w9, [x0, #254]
    umov w9, V<t4_g3_low>.h[3]
    strh w9, [x0, #260]
    p32_terminal_4_g3_end:
    p32_terminal_4_g4_start:
    ldr Q<t4_g4_x>, [x1, #1088]
    sqrdmulh V<t4_g4_lq>.8h, V<t4_g4_x>.8h, v27.8h
    sqrdmulh V<t4_g4_hq>.8h, V<t4_g4_x>.8h, v29.8h
    mul V<t4_g4_low>.8h, V<t4_g4_x>.8h, v26.8h
    mul V<t4_g4_high>.8h, V<t4_g4_x>.8h, v28.8h
    mls V<t4_g4_low>.8h, V<t4_g4_lq>.8h, v30.8h
    mls V<t4_g4_high>.8h, V<t4_g4_hq>.8h, v30.8h
    ext V<t4_g4_lr>.16b, V<t4_g4_low>.16b, V<t4_g4_low>.16b, #8
    ext V<t4_g4_hr>.16b, V<t4_g4_high>.16b, V<t4_g4_high>.16b, #8
    add V<t4_g4_low>.8h, V<t4_g4_low>.8h, V<t4_g4_lr>.8h
    add V<t4_g4_high>.8h, V<t4_g4_high>.8h, V<t4_g4_hr>.8h
    umov w9, V<t4_g4_high>.h[0]
    strh w9, [x0, #1084]
    umov w9, V<t4_g4_high>.h[1]
    strh w9, [x0, #1090]
    umov w9, V<t4_g4_high>.h[2]
    strh w9, [x0, #1096]
    umov w9, V<t4_g4_high>.h[3]
    strh w9, [x0, #1102]
    umov w9, V<t4_g4_low>.h[0]
    strh w9, [x0, #220]
    umov w9, V<t4_g4_low>.h[1]
    strh w9, [x0, #226]
    umov w9, V<t4_g4_low>.h[2]
    strh w9, [x0, #232]
    umov w9, V<t4_g4_low>.h[3]
    strh w9, [x0, #238]
    p32_terminal_4_g4_end:
    p32_terminal_4_g5_start:
    ldr Q<t4_g5_x>, [x1, #1344]
    sqrdmulh V<t4_g5_lq>.8h, V<t4_g5_x>.8h, v27.8h
    sqrdmulh V<t4_g5_hq>.8h, V<t4_g5_x>.8h, v29.8h
    mul V<t4_g5_low>.8h, V<t4_g5_x>.8h, v26.8h
    mul V<t4_g5_high>.8h, V<t4_g5_x>.8h, v28.8h
    mls V<t4_g5_low>.8h, V<t4_g5_lq>.8h, v30.8h
    mls V<t4_g5_high>.8h, V<t4_g5_hq>.8h, v30.8h
    ext V<t4_g5_lr>.16b, V<t4_g5_low>.16b, V<t4_g5_low>.16b, #8
    ext V<t4_g5_hr>.16b, V<t4_g5_high>.16b, V<t4_g5_high>.16b, #8
    add V<t4_g5_low>.8h, V<t4_g5_low>.8h, V<t4_g5_lr>.8h
    add V<t4_g5_high>.8h, V<t4_g5_high>.8h, V<t4_g5_hr>.8h
    umov w9, V<t4_g5_high>.h[0]
    strh w9, [x0, #1108]
    umov w9, V<t4_g5_high>.h[1]
    strh w9, [x0, #1114]
    umov w9, V<t4_g5_high>.h[2]
    strh w9, [x0, #1120]
    umov w9, V<t4_g5_high>.h[3]
    strh w9, [x0, #1126]
    umov w9, V<t4_g5_low>.h[0]
    strh w9, [x0, #244]
    umov w9, V<t4_g5_low>.h[1]
    strh w9, [x0, #250]
    umov w9, V<t4_g5_low>.h[2]
    strh w9, [x0, #256]
    umov w9, V<t4_g5_low>.h[3]
    strh w9, [x0, #262]
    p32_terminal_4_g5_end:
p32_terminal_4_end:
p32_terminal_5_start:
    ldr q26, [x4, #320]
    ldr q27, [x4, #336]
    ldr q28, [x4, #352]
    ldr q29, [x4, #368]
    p32_terminal_5_g0_start:
    ldr Q<t5_g0_x>, [x1, #80]
    sqrdmulh V<t5_g0_lq>.8h, V<t5_g0_x>.8h, v27.8h
    sqrdmulh V<t5_g0_hq>.8h, V<t5_g0_x>.8h, v29.8h
    mul V<t5_g0_low>.8h, V<t5_g0_x>.8h, v26.8h
    mul V<t5_g0_high>.8h, V<t5_g0_x>.8h, v28.8h
    mls V<t5_g0_low>.8h, V<t5_g0_lq>.8h, v30.8h
    mls V<t5_g0_high>.8h, V<t5_g0_hq>.8h, v30.8h
    ext V<t5_g0_lr>.16b, V<t5_g0_low>.16b, V<t5_g0_low>.16b, #8
    ext V<t5_g0_hr>.16b, V<t5_g0_high>.16b, V<t5_g0_high>.16b, #8
    add V<t5_g0_low>.8h, V<t5_g0_low>.8h, V<t5_g0_lr>.8h
    add V<t5_g0_high>.8h, V<t5_g0_high>.8h, V<t5_g0_hr>.8h
    umov w9, V<t5_g0_high>.h[0]
    strh w9, [x0, #1134]
    umov w9, V<t5_g0_high>.h[1]
    strh w9, [x0, #1140]
    umov w9, V<t5_g0_high>.h[2]
    strh w9, [x0, #1146]
    umov w9, V<t5_g0_high>.h[3]
    strh w9, [x0, #1152]
    umov w9, V<t5_g0_low>.h[0]
    strh w9, [x0, #270]
    umov w9, V<t5_g0_low>.h[1]
    strh w9, [x0, #276]
    umov w9, V<t5_g0_low>.h[2]
    strh w9, [x0, #282]
    umov w9, V<t5_g0_low>.h[3]
    strh w9, [x0, #288]
    p32_terminal_5_g0_end:
    p32_terminal_5_g1_start:
    ldr Q<t5_g1_x>, [x1, #336]
    sqrdmulh V<t5_g1_lq>.8h, V<t5_g1_x>.8h, v27.8h
    sqrdmulh V<t5_g1_hq>.8h, V<t5_g1_x>.8h, v29.8h
    mul V<t5_g1_low>.8h, V<t5_g1_x>.8h, v26.8h
    mul V<t5_g1_high>.8h, V<t5_g1_x>.8h, v28.8h
    mls V<t5_g1_low>.8h, V<t5_g1_lq>.8h, v30.8h
    mls V<t5_g1_high>.8h, V<t5_g1_hq>.8h, v30.8h
    ext V<t5_g1_lr>.16b, V<t5_g1_low>.16b, V<t5_g1_low>.16b, #8
    ext V<t5_g1_hr>.16b, V<t5_g1_high>.16b, V<t5_g1_high>.16b, #8
    add V<t5_g1_low>.8h, V<t5_g1_low>.8h, V<t5_g1_lr>.8h
    add V<t5_g1_high>.8h, V<t5_g1_high>.8h, V<t5_g1_hr>.8h
    umov w9, V<t5_g1_high>.h[0]
    strh w9, [x0, #1158]
    umov w9, V<t5_g1_high>.h[1]
    strh w9, [x0, #1164]
    umov w9, V<t5_g1_high>.h[2]
    strh w9, [x0, #1170]
    umov w9, V<t5_g1_high>.h[3]
    strh w9, [x0, #1176]
    umov w9, V<t5_g1_low>.h[0]
    strh w9, [x0, #294]
    umov w9, V<t5_g1_low>.h[1]
    strh w9, [x0, #300]
    umov w9, V<t5_g1_low>.h[2]
    strh w9, [x0, #306]
    umov w9, V<t5_g1_low>.h[3]
    strh w9, [x0, #312]
    p32_terminal_5_g1_end:
    p32_terminal_5_g2_start:
    ldr Q<t5_g2_x>, [x1, #592]
    sqrdmulh V<t5_g2_lq>.8h, V<t5_g2_x>.8h, v27.8h
    sqrdmulh V<t5_g2_hq>.8h, V<t5_g2_x>.8h, v29.8h
    mul V<t5_g2_low>.8h, V<t5_g2_x>.8h, v26.8h
    mul V<t5_g2_high>.8h, V<t5_g2_x>.8h, v28.8h
    mls V<t5_g2_low>.8h, V<t5_g2_lq>.8h, v30.8h
    mls V<t5_g2_high>.8h, V<t5_g2_hq>.8h, v30.8h
    ext V<t5_g2_lr>.16b, V<t5_g2_low>.16b, V<t5_g2_low>.16b, #8
    ext V<t5_g2_hr>.16b, V<t5_g2_high>.16b, V<t5_g2_high>.16b, #8
    add V<t5_g2_low>.8h, V<t5_g2_low>.8h, V<t5_g2_lr>.8h
    add V<t5_g2_high>.8h, V<t5_g2_high>.8h, V<t5_g2_hr>.8h
    umov w9, V<t5_g2_high>.h[0]
    strh w9, [x0, #1136]
    umov w9, V<t5_g2_high>.h[1]
    strh w9, [x0, #1142]
    umov w9, V<t5_g2_high>.h[2]
    strh w9, [x0, #1148]
    umov w9, V<t5_g2_high>.h[3]
    strh w9, [x0, #1154]
    umov w9, V<t5_g2_low>.h[0]
    strh w9, [x0, #272]
    umov w9, V<t5_g2_low>.h[1]
    strh w9, [x0, #278]
    umov w9, V<t5_g2_low>.h[2]
    strh w9, [x0, #284]
    umov w9, V<t5_g2_low>.h[3]
    strh w9, [x0, #290]
    p32_terminal_5_g2_end:
    p32_terminal_5_g3_start:
    ldr Q<t5_g3_x>, [x1, #848]
    sqrdmulh V<t5_g3_lq>.8h, V<t5_g3_x>.8h, v27.8h
    sqrdmulh V<t5_g3_hq>.8h, V<t5_g3_x>.8h, v29.8h
    mul V<t5_g3_low>.8h, V<t5_g3_x>.8h, v26.8h
    mul V<t5_g3_high>.8h, V<t5_g3_x>.8h, v28.8h
    mls V<t5_g3_low>.8h, V<t5_g3_lq>.8h, v30.8h
    mls V<t5_g3_high>.8h, V<t5_g3_hq>.8h, v30.8h
    ext V<t5_g3_lr>.16b, V<t5_g3_low>.16b, V<t5_g3_low>.16b, #8
    ext V<t5_g3_hr>.16b, V<t5_g3_high>.16b, V<t5_g3_high>.16b, #8
    add V<t5_g3_low>.8h, V<t5_g3_low>.8h, V<t5_g3_lr>.8h
    add V<t5_g3_high>.8h, V<t5_g3_high>.8h, V<t5_g3_hr>.8h
    umov w9, V<t5_g3_high>.h[0]
    strh w9, [x0, #1160]
    umov w9, V<t5_g3_high>.h[1]
    strh w9, [x0, #1166]
    umov w9, V<t5_g3_high>.h[2]
    strh w9, [x0, #1172]
    umov w9, V<t5_g3_high>.h[3]
    strh w9, [x0, #1178]
    umov w9, V<t5_g3_low>.h[0]
    strh w9, [x0, #296]
    umov w9, V<t5_g3_low>.h[1]
    strh w9, [x0, #302]
    umov w9, V<t5_g3_low>.h[2]
    strh w9, [x0, #308]
    umov w9, V<t5_g3_low>.h[3]
    strh w9, [x0, #314]
    p32_terminal_5_g3_end:
    p32_terminal_5_g4_start:
    ldr Q<t5_g4_x>, [x1, #1104]
    sqrdmulh V<t5_g4_lq>.8h, V<t5_g4_x>.8h, v27.8h
    sqrdmulh V<t5_g4_hq>.8h, V<t5_g4_x>.8h, v29.8h
    mul V<t5_g4_low>.8h, V<t5_g4_x>.8h, v26.8h
    mul V<t5_g4_high>.8h, V<t5_g4_x>.8h, v28.8h
    mls V<t5_g4_low>.8h, V<t5_g4_lq>.8h, v30.8h
    mls V<t5_g4_high>.8h, V<t5_g4_hq>.8h, v30.8h
    ext V<t5_g4_lr>.16b, V<t5_g4_low>.16b, V<t5_g4_low>.16b, #8
    ext V<t5_g4_hr>.16b, V<t5_g4_high>.16b, V<t5_g4_high>.16b, #8
    add V<t5_g4_low>.8h, V<t5_g4_low>.8h, V<t5_g4_lr>.8h
    add V<t5_g4_high>.8h, V<t5_g4_high>.8h, V<t5_g4_hr>.8h
    umov w9, V<t5_g4_high>.h[0]
    strh w9, [x0, #1138]
    umov w9, V<t5_g4_high>.h[1]
    strh w9, [x0, #1144]
    umov w9, V<t5_g4_high>.h[2]
    strh w9, [x0, #1150]
    umov w9, V<t5_g4_high>.h[3]
    strh w9, [x0, #1156]
    umov w9, V<t5_g4_low>.h[0]
    strh w9, [x0, #274]
    umov w9, V<t5_g4_low>.h[1]
    strh w9, [x0, #280]
    umov w9, V<t5_g4_low>.h[2]
    strh w9, [x0, #286]
    umov w9, V<t5_g4_low>.h[3]
    strh w9, [x0, #292]
    p32_terminal_5_g4_end:
    p32_terminal_5_g5_start:
    ldr Q<t5_g5_x>, [x1, #1360]
    sqrdmulh V<t5_g5_lq>.8h, V<t5_g5_x>.8h, v27.8h
    sqrdmulh V<t5_g5_hq>.8h, V<t5_g5_x>.8h, v29.8h
    mul V<t5_g5_low>.8h, V<t5_g5_x>.8h, v26.8h
    mul V<t5_g5_high>.8h, V<t5_g5_x>.8h, v28.8h
    mls V<t5_g5_low>.8h, V<t5_g5_lq>.8h, v30.8h
    mls V<t5_g5_high>.8h, V<t5_g5_hq>.8h, v30.8h
    ext V<t5_g5_lr>.16b, V<t5_g5_low>.16b, V<t5_g5_low>.16b, #8
    ext V<t5_g5_hr>.16b, V<t5_g5_high>.16b, V<t5_g5_high>.16b, #8
    add V<t5_g5_low>.8h, V<t5_g5_low>.8h, V<t5_g5_lr>.8h
    add V<t5_g5_high>.8h, V<t5_g5_high>.8h, V<t5_g5_hr>.8h
    umov w9, V<t5_g5_high>.h[0]
    strh w9, [x0, #1162]
    umov w9, V<t5_g5_high>.h[1]
    strh w9, [x0, #1168]
    umov w9, V<t5_g5_high>.h[2]
    strh w9, [x0, #1174]
    umov w9, V<t5_g5_high>.h[3]
    strh w9, [x0, #1180]
    umov w9, V<t5_g5_low>.h[0]
    strh w9, [x0, #298]
    umov w9, V<t5_g5_low>.h[1]
    strh w9, [x0, #304]
    umov w9, V<t5_g5_low>.h[2]
    strh w9, [x0, #310]
    umov w9, V<t5_g5_low>.h[3]
    strh w9, [x0, #316]
    p32_terminal_5_g5_end:
p32_terminal_5_end:
p32_terminal_6_start:
    ldr q26, [x4, #384]
    ldr q27, [x4, #400]
    ldr q28, [x4, #416]
    ldr q29, [x4, #432]
    p32_terminal_6_g0_start:
    ldr Q<t6_g0_x>, [x1, #96]
    sqrdmulh V<t6_g0_lq>.8h, V<t6_g0_x>.8h, v27.8h
    sqrdmulh V<t6_g0_hq>.8h, V<t6_g0_x>.8h, v29.8h
    mul V<t6_g0_low>.8h, V<t6_g0_x>.8h, v26.8h
    mul V<t6_g0_high>.8h, V<t6_g0_x>.8h, v28.8h
    mls V<t6_g0_low>.8h, V<t6_g0_lq>.8h, v30.8h
    mls V<t6_g0_high>.8h, V<t6_g0_hq>.8h, v30.8h
    ext V<t6_g0_lr>.16b, V<t6_g0_low>.16b, V<t6_g0_low>.16b, #8
    ext V<t6_g0_hr>.16b, V<t6_g0_high>.16b, V<t6_g0_high>.16b, #8
    add V<t6_g0_low>.8h, V<t6_g0_low>.8h, V<t6_g0_lr>.8h
    add V<t6_g0_high>.8h, V<t6_g0_high>.8h, V<t6_g0_hr>.8h
    umov w9, V<t6_g0_high>.h[0]
    strh w9, [x0, #1188]
    umov w9, V<t6_g0_high>.h[1]
    strh w9, [x0, #1194]
    umov w9, V<t6_g0_high>.h[2]
    strh w9, [x0, #1200]
    umov w9, V<t6_g0_high>.h[3]
    strh w9, [x0, #1206]
    umov w9, V<t6_g0_low>.h[0]
    strh w9, [x0, #324]
    umov w9, V<t6_g0_low>.h[1]
    strh w9, [x0, #330]
    umov w9, V<t6_g0_low>.h[2]
    strh w9, [x0, #336]
    umov w9, V<t6_g0_low>.h[3]
    strh w9, [x0, #342]
    p32_terminal_6_g0_end:
    p32_terminal_6_g1_start:
    ldr Q<t6_g1_x>, [x1, #352]
    sqrdmulh V<t6_g1_lq>.8h, V<t6_g1_x>.8h, v27.8h
    sqrdmulh V<t6_g1_hq>.8h, V<t6_g1_x>.8h, v29.8h
    mul V<t6_g1_low>.8h, V<t6_g1_x>.8h, v26.8h
    mul V<t6_g1_high>.8h, V<t6_g1_x>.8h, v28.8h
    mls V<t6_g1_low>.8h, V<t6_g1_lq>.8h, v30.8h
    mls V<t6_g1_high>.8h, V<t6_g1_hq>.8h, v30.8h
    ext V<t6_g1_lr>.16b, V<t6_g1_low>.16b, V<t6_g1_low>.16b, #8
    ext V<t6_g1_hr>.16b, V<t6_g1_high>.16b, V<t6_g1_high>.16b, #8
    add V<t6_g1_low>.8h, V<t6_g1_low>.8h, V<t6_g1_lr>.8h
    add V<t6_g1_high>.8h, V<t6_g1_high>.8h, V<t6_g1_hr>.8h
    umov w9, V<t6_g1_high>.h[0]
    strh w9, [x0, #1212]
    umov w9, V<t6_g1_high>.h[1]
    strh w9, [x0, #1218]
    umov w9, V<t6_g1_high>.h[2]
    strh w9, [x0, #1224]
    umov w9, V<t6_g1_high>.h[3]
    strh w9, [x0, #1230]
    umov w9, V<t6_g1_low>.h[0]
    strh w9, [x0, #348]
    umov w9, V<t6_g1_low>.h[1]
    strh w9, [x0, #354]
    umov w9, V<t6_g1_low>.h[2]
    strh w9, [x0, #360]
    umov w9, V<t6_g1_low>.h[3]
    strh w9, [x0, #366]
    p32_terminal_6_g1_end:
    p32_terminal_6_g2_start:
    ldr Q<t6_g2_x>, [x1, #608]
    sqrdmulh V<t6_g2_lq>.8h, V<t6_g2_x>.8h, v27.8h
    sqrdmulh V<t6_g2_hq>.8h, V<t6_g2_x>.8h, v29.8h
    mul V<t6_g2_low>.8h, V<t6_g2_x>.8h, v26.8h
    mul V<t6_g2_high>.8h, V<t6_g2_x>.8h, v28.8h
    mls V<t6_g2_low>.8h, V<t6_g2_lq>.8h, v30.8h
    mls V<t6_g2_high>.8h, V<t6_g2_hq>.8h, v30.8h
    ext V<t6_g2_lr>.16b, V<t6_g2_low>.16b, V<t6_g2_low>.16b, #8
    ext V<t6_g2_hr>.16b, V<t6_g2_high>.16b, V<t6_g2_high>.16b, #8
    add V<t6_g2_low>.8h, V<t6_g2_low>.8h, V<t6_g2_lr>.8h
    add V<t6_g2_high>.8h, V<t6_g2_high>.8h, V<t6_g2_hr>.8h
    umov w9, V<t6_g2_high>.h[0]
    strh w9, [x0, #1190]
    umov w9, V<t6_g2_high>.h[1]
    strh w9, [x0, #1196]
    umov w9, V<t6_g2_high>.h[2]
    strh w9, [x0, #1202]
    umov w9, V<t6_g2_high>.h[3]
    strh w9, [x0, #1208]
    umov w9, V<t6_g2_low>.h[0]
    strh w9, [x0, #326]
    umov w9, V<t6_g2_low>.h[1]
    strh w9, [x0, #332]
    umov w9, V<t6_g2_low>.h[2]
    strh w9, [x0, #338]
    umov w9, V<t6_g2_low>.h[3]
    strh w9, [x0, #344]
    p32_terminal_6_g2_end:
    p32_terminal_6_g3_start:
    ldr Q<t6_g3_x>, [x1, #864]
    sqrdmulh V<t6_g3_lq>.8h, V<t6_g3_x>.8h, v27.8h
    sqrdmulh V<t6_g3_hq>.8h, V<t6_g3_x>.8h, v29.8h
    mul V<t6_g3_low>.8h, V<t6_g3_x>.8h, v26.8h
    mul V<t6_g3_high>.8h, V<t6_g3_x>.8h, v28.8h
    mls V<t6_g3_low>.8h, V<t6_g3_lq>.8h, v30.8h
    mls V<t6_g3_high>.8h, V<t6_g3_hq>.8h, v30.8h
    ext V<t6_g3_lr>.16b, V<t6_g3_low>.16b, V<t6_g3_low>.16b, #8
    ext V<t6_g3_hr>.16b, V<t6_g3_high>.16b, V<t6_g3_high>.16b, #8
    add V<t6_g3_low>.8h, V<t6_g3_low>.8h, V<t6_g3_lr>.8h
    add V<t6_g3_high>.8h, V<t6_g3_high>.8h, V<t6_g3_hr>.8h
    umov w9, V<t6_g3_high>.h[0]
    strh w9, [x0, #1214]
    umov w9, V<t6_g3_high>.h[1]
    strh w9, [x0, #1220]
    umov w9, V<t6_g3_high>.h[2]
    strh w9, [x0, #1226]
    umov w9, V<t6_g3_high>.h[3]
    strh w9, [x0, #1232]
    umov w9, V<t6_g3_low>.h[0]
    strh w9, [x0, #350]
    umov w9, V<t6_g3_low>.h[1]
    strh w9, [x0, #356]
    umov w9, V<t6_g3_low>.h[2]
    strh w9, [x0, #362]
    umov w9, V<t6_g3_low>.h[3]
    strh w9, [x0, #368]
    p32_terminal_6_g3_end:
    p32_terminal_6_g4_start:
    ldr Q<t6_g4_x>, [x1, #1120]
    sqrdmulh V<t6_g4_lq>.8h, V<t6_g4_x>.8h, v27.8h
    sqrdmulh V<t6_g4_hq>.8h, V<t6_g4_x>.8h, v29.8h
    mul V<t6_g4_low>.8h, V<t6_g4_x>.8h, v26.8h
    mul V<t6_g4_high>.8h, V<t6_g4_x>.8h, v28.8h
    mls V<t6_g4_low>.8h, V<t6_g4_lq>.8h, v30.8h
    mls V<t6_g4_high>.8h, V<t6_g4_hq>.8h, v30.8h
    ext V<t6_g4_lr>.16b, V<t6_g4_low>.16b, V<t6_g4_low>.16b, #8
    ext V<t6_g4_hr>.16b, V<t6_g4_high>.16b, V<t6_g4_high>.16b, #8
    add V<t6_g4_low>.8h, V<t6_g4_low>.8h, V<t6_g4_lr>.8h
    add V<t6_g4_high>.8h, V<t6_g4_high>.8h, V<t6_g4_hr>.8h
    umov w9, V<t6_g4_high>.h[0]
    strh w9, [x0, #1192]
    umov w9, V<t6_g4_high>.h[1]
    strh w9, [x0, #1198]
    umov w9, V<t6_g4_high>.h[2]
    strh w9, [x0, #1204]
    umov w9, V<t6_g4_high>.h[3]
    strh w9, [x0, #1210]
    umov w9, V<t6_g4_low>.h[0]
    strh w9, [x0, #328]
    umov w9, V<t6_g4_low>.h[1]
    strh w9, [x0, #334]
    umov w9, V<t6_g4_low>.h[2]
    strh w9, [x0, #340]
    umov w9, V<t6_g4_low>.h[3]
    strh w9, [x0, #346]
    p32_terminal_6_g4_end:
    p32_terminal_6_g5_start:
    ldr Q<t6_g5_x>, [x1, #1376]
    sqrdmulh V<t6_g5_lq>.8h, V<t6_g5_x>.8h, v27.8h
    sqrdmulh V<t6_g5_hq>.8h, V<t6_g5_x>.8h, v29.8h
    mul V<t6_g5_low>.8h, V<t6_g5_x>.8h, v26.8h
    mul V<t6_g5_high>.8h, V<t6_g5_x>.8h, v28.8h
    mls V<t6_g5_low>.8h, V<t6_g5_lq>.8h, v30.8h
    mls V<t6_g5_high>.8h, V<t6_g5_hq>.8h, v30.8h
    ext V<t6_g5_lr>.16b, V<t6_g5_low>.16b, V<t6_g5_low>.16b, #8
    ext V<t6_g5_hr>.16b, V<t6_g5_high>.16b, V<t6_g5_high>.16b, #8
    add V<t6_g5_low>.8h, V<t6_g5_low>.8h, V<t6_g5_lr>.8h
    add V<t6_g5_high>.8h, V<t6_g5_high>.8h, V<t6_g5_hr>.8h
    umov w9, V<t6_g5_high>.h[0]
    strh w9, [x0, #1216]
    umov w9, V<t6_g5_high>.h[1]
    strh w9, [x0, #1222]
    umov w9, V<t6_g5_high>.h[2]
    strh w9, [x0, #1228]
    umov w9, V<t6_g5_high>.h[3]
    strh w9, [x0, #1234]
    umov w9, V<t6_g5_low>.h[0]
    strh w9, [x0, #352]
    umov w9, V<t6_g5_low>.h[1]
    strh w9, [x0, #358]
    umov w9, V<t6_g5_low>.h[2]
    strh w9, [x0, #364]
    umov w9, V<t6_g5_low>.h[3]
    strh w9, [x0, #370]
    p32_terminal_6_g5_end:
p32_terminal_6_end:
p32_terminal_7_start:
    ldr q26, [x4, #448]
    ldr q27, [x4, #464]
    ldr q28, [x4, #480]
    ldr q29, [x4, #496]
    p32_terminal_7_g0_start:
    ldr Q<t7_g0_x>, [x1, #112]
    sqrdmulh V<t7_g0_lq>.8h, V<t7_g0_x>.8h, v27.8h
    sqrdmulh V<t7_g0_hq>.8h, V<t7_g0_x>.8h, v29.8h
    mul V<t7_g0_low>.8h, V<t7_g0_x>.8h, v26.8h
    mul V<t7_g0_high>.8h, V<t7_g0_x>.8h, v28.8h
    mls V<t7_g0_low>.8h, V<t7_g0_lq>.8h, v30.8h
    mls V<t7_g0_high>.8h, V<t7_g0_hq>.8h, v30.8h
    ext V<t7_g0_lr>.16b, V<t7_g0_low>.16b, V<t7_g0_low>.16b, #8
    ext V<t7_g0_hr>.16b, V<t7_g0_high>.16b, V<t7_g0_high>.16b, #8
    add V<t7_g0_low>.8h, V<t7_g0_low>.8h, V<t7_g0_lr>.8h
    add V<t7_g0_high>.8h, V<t7_g0_high>.8h, V<t7_g0_hr>.8h
    umov w9, V<t7_g0_high>.h[0]
    strh w9, [x0, #1242]
    umov w9, V<t7_g0_high>.h[1]
    strh w9, [x0, #1248]
    umov w9, V<t7_g0_high>.h[2]
    strh w9, [x0, #1254]
    umov w9, V<t7_g0_high>.h[3]
    strh w9, [x0, #1260]
    umov w9, V<t7_g0_low>.h[0]
    strh w9, [x0, #378]
    umov w9, V<t7_g0_low>.h[1]
    strh w9, [x0, #384]
    umov w9, V<t7_g0_low>.h[2]
    strh w9, [x0, #390]
    umov w9, V<t7_g0_low>.h[3]
    strh w9, [x0, #396]
    p32_terminal_7_g0_end:
    p32_terminal_7_g1_start:
    ldr Q<t7_g1_x>, [x1, #368]
    sqrdmulh V<t7_g1_lq>.8h, V<t7_g1_x>.8h, v27.8h
    sqrdmulh V<t7_g1_hq>.8h, V<t7_g1_x>.8h, v29.8h
    mul V<t7_g1_low>.8h, V<t7_g1_x>.8h, v26.8h
    mul V<t7_g1_high>.8h, V<t7_g1_x>.8h, v28.8h
    mls V<t7_g1_low>.8h, V<t7_g1_lq>.8h, v30.8h
    mls V<t7_g1_high>.8h, V<t7_g1_hq>.8h, v30.8h
    ext V<t7_g1_lr>.16b, V<t7_g1_low>.16b, V<t7_g1_low>.16b, #8
    ext V<t7_g1_hr>.16b, V<t7_g1_high>.16b, V<t7_g1_high>.16b, #8
    add V<t7_g1_low>.8h, V<t7_g1_low>.8h, V<t7_g1_lr>.8h
    add V<t7_g1_high>.8h, V<t7_g1_high>.8h, V<t7_g1_hr>.8h
    umov w9, V<t7_g1_high>.h[0]
    strh w9, [x0, #1266]
    umov w9, V<t7_g1_high>.h[1]
    strh w9, [x0, #1272]
    umov w9, V<t7_g1_high>.h[2]
    strh w9, [x0, #1278]
    umov w9, V<t7_g1_high>.h[3]
    strh w9, [x0, #1284]
    umov w9, V<t7_g1_low>.h[0]
    strh w9, [x0, #402]
    umov w9, V<t7_g1_low>.h[1]
    strh w9, [x0, #408]
    umov w9, V<t7_g1_low>.h[2]
    strh w9, [x0, #414]
    umov w9, V<t7_g1_low>.h[3]
    strh w9, [x0, #420]
    p32_terminal_7_g1_end:
    p32_terminal_7_g2_start:
    ldr Q<t7_g2_x>, [x1, #624]
    sqrdmulh V<t7_g2_lq>.8h, V<t7_g2_x>.8h, v27.8h
    sqrdmulh V<t7_g2_hq>.8h, V<t7_g2_x>.8h, v29.8h
    mul V<t7_g2_low>.8h, V<t7_g2_x>.8h, v26.8h
    mul V<t7_g2_high>.8h, V<t7_g2_x>.8h, v28.8h
    mls V<t7_g2_low>.8h, V<t7_g2_lq>.8h, v30.8h
    mls V<t7_g2_high>.8h, V<t7_g2_hq>.8h, v30.8h
    ext V<t7_g2_lr>.16b, V<t7_g2_low>.16b, V<t7_g2_low>.16b, #8
    ext V<t7_g2_hr>.16b, V<t7_g2_high>.16b, V<t7_g2_high>.16b, #8
    add V<t7_g2_low>.8h, V<t7_g2_low>.8h, V<t7_g2_lr>.8h
    add V<t7_g2_high>.8h, V<t7_g2_high>.8h, V<t7_g2_hr>.8h
    umov w9, V<t7_g2_high>.h[0]
    strh w9, [x0, #1244]
    umov w9, V<t7_g2_high>.h[1]
    strh w9, [x0, #1250]
    umov w9, V<t7_g2_high>.h[2]
    strh w9, [x0, #1256]
    umov w9, V<t7_g2_high>.h[3]
    strh w9, [x0, #1262]
    umov w9, V<t7_g2_low>.h[0]
    strh w9, [x0, #380]
    umov w9, V<t7_g2_low>.h[1]
    strh w9, [x0, #386]
    umov w9, V<t7_g2_low>.h[2]
    strh w9, [x0, #392]
    umov w9, V<t7_g2_low>.h[3]
    strh w9, [x0, #398]
    p32_terminal_7_g2_end:
    p32_terminal_7_g3_start:
    ldr Q<t7_g3_x>, [x1, #880]
    sqrdmulh V<t7_g3_lq>.8h, V<t7_g3_x>.8h, v27.8h
    sqrdmulh V<t7_g3_hq>.8h, V<t7_g3_x>.8h, v29.8h
    mul V<t7_g3_low>.8h, V<t7_g3_x>.8h, v26.8h
    mul V<t7_g3_high>.8h, V<t7_g3_x>.8h, v28.8h
    mls V<t7_g3_low>.8h, V<t7_g3_lq>.8h, v30.8h
    mls V<t7_g3_high>.8h, V<t7_g3_hq>.8h, v30.8h
    ext V<t7_g3_lr>.16b, V<t7_g3_low>.16b, V<t7_g3_low>.16b, #8
    ext V<t7_g3_hr>.16b, V<t7_g3_high>.16b, V<t7_g3_high>.16b, #8
    add V<t7_g3_low>.8h, V<t7_g3_low>.8h, V<t7_g3_lr>.8h
    add V<t7_g3_high>.8h, V<t7_g3_high>.8h, V<t7_g3_hr>.8h
    umov w9, V<t7_g3_high>.h[0]
    strh w9, [x0, #1268]
    umov w9, V<t7_g3_high>.h[1]
    strh w9, [x0, #1274]
    umov w9, V<t7_g3_high>.h[2]
    strh w9, [x0, #1280]
    umov w9, V<t7_g3_high>.h[3]
    strh w9, [x0, #1286]
    umov w9, V<t7_g3_low>.h[0]
    strh w9, [x0, #404]
    umov w9, V<t7_g3_low>.h[1]
    strh w9, [x0, #410]
    umov w9, V<t7_g3_low>.h[2]
    strh w9, [x0, #416]
    umov w9, V<t7_g3_low>.h[3]
    strh w9, [x0, #422]
    p32_terminal_7_g3_end:
    p32_terminal_7_g4_start:
    ldr Q<t7_g4_x>, [x1, #1136]
    sqrdmulh V<t7_g4_lq>.8h, V<t7_g4_x>.8h, v27.8h
    sqrdmulh V<t7_g4_hq>.8h, V<t7_g4_x>.8h, v29.8h
    mul V<t7_g4_low>.8h, V<t7_g4_x>.8h, v26.8h
    mul V<t7_g4_high>.8h, V<t7_g4_x>.8h, v28.8h
    mls V<t7_g4_low>.8h, V<t7_g4_lq>.8h, v30.8h
    mls V<t7_g4_high>.8h, V<t7_g4_hq>.8h, v30.8h
    ext V<t7_g4_lr>.16b, V<t7_g4_low>.16b, V<t7_g4_low>.16b, #8
    ext V<t7_g4_hr>.16b, V<t7_g4_high>.16b, V<t7_g4_high>.16b, #8
    add V<t7_g4_low>.8h, V<t7_g4_low>.8h, V<t7_g4_lr>.8h
    add V<t7_g4_high>.8h, V<t7_g4_high>.8h, V<t7_g4_hr>.8h
    umov w9, V<t7_g4_high>.h[0]
    strh w9, [x0, #1246]
    umov w9, V<t7_g4_high>.h[1]
    strh w9, [x0, #1252]
    umov w9, V<t7_g4_high>.h[2]
    strh w9, [x0, #1258]
    umov w9, V<t7_g4_high>.h[3]
    strh w9, [x0, #1264]
    umov w9, V<t7_g4_low>.h[0]
    strh w9, [x0, #382]
    umov w9, V<t7_g4_low>.h[1]
    strh w9, [x0, #388]
    umov w9, V<t7_g4_low>.h[2]
    strh w9, [x0, #394]
    umov w9, V<t7_g4_low>.h[3]
    strh w9, [x0, #400]
    p32_terminal_7_g4_end:
    p32_terminal_7_g5_start:
    ldr Q<t7_g5_x>, [x1, #1392]
    sqrdmulh V<t7_g5_lq>.8h, V<t7_g5_x>.8h, v27.8h
    sqrdmulh V<t7_g5_hq>.8h, V<t7_g5_x>.8h, v29.8h
    mul V<t7_g5_low>.8h, V<t7_g5_x>.8h, v26.8h
    mul V<t7_g5_high>.8h, V<t7_g5_x>.8h, v28.8h
    mls V<t7_g5_low>.8h, V<t7_g5_lq>.8h, v30.8h
    mls V<t7_g5_high>.8h, V<t7_g5_hq>.8h, v30.8h
    ext V<t7_g5_lr>.16b, V<t7_g5_low>.16b, V<t7_g5_low>.16b, #8
    ext V<t7_g5_hr>.16b, V<t7_g5_high>.16b, V<t7_g5_high>.16b, #8
    add V<t7_g5_low>.8h, V<t7_g5_low>.8h, V<t7_g5_lr>.8h
    add V<t7_g5_high>.8h, V<t7_g5_high>.8h, V<t7_g5_hr>.8h
    umov w9, V<t7_g5_high>.h[0]
    strh w9, [x0, #1270]
    umov w9, V<t7_g5_high>.h[1]
    strh w9, [x0, #1276]
    umov w9, V<t7_g5_high>.h[2]
    strh w9, [x0, #1282]
    umov w9, V<t7_g5_high>.h[3]
    strh w9, [x0, #1288]
    umov w9, V<t7_g5_low>.h[0]
    strh w9, [x0, #406]
    umov w9, V<t7_g5_low>.h[1]
    strh w9, [x0, #412]
    umov w9, V<t7_g5_low>.h[2]
    strh w9, [x0, #418]
    umov w9, V<t7_g5_low>.h[3]
    strh w9, [x0, #424]
    p32_terminal_7_g5_end:
p32_terminal_7_end:
p32_terminal_8_start:
    ldr q26, [x4, #512]
    ldr q27, [x4, #528]
    ldr q28, [x4, #544]
    ldr q29, [x4, #560]
    p32_terminal_8_g0_start:
    ldr Q<t8_g0_x>, [x1, #128]
    sqrdmulh V<t8_g0_lq>.8h, V<t8_g0_x>.8h, v27.8h
    sqrdmulh V<t8_g0_hq>.8h, V<t8_g0_x>.8h, v29.8h
    mul V<t8_g0_low>.8h, V<t8_g0_x>.8h, v26.8h
    mul V<t8_g0_high>.8h, V<t8_g0_x>.8h, v28.8h
    mls V<t8_g0_low>.8h, V<t8_g0_lq>.8h, v30.8h
    mls V<t8_g0_high>.8h, V<t8_g0_hq>.8h, v30.8h
    ext V<t8_g0_lr>.16b, V<t8_g0_low>.16b, V<t8_g0_low>.16b, #8
    ext V<t8_g0_hr>.16b, V<t8_g0_high>.16b, V<t8_g0_high>.16b, #8
    add V<t8_g0_low>.8h, V<t8_g0_low>.8h, V<t8_g0_lr>.8h
    add V<t8_g0_high>.8h, V<t8_g0_high>.8h, V<t8_g0_hr>.8h
    sqrdmulh V<t8_g0_rh>.8h, V<t8_g0_high>.8h, v31.8h
    mls V<t8_g0_high>.8h, V<t8_g0_rh>.8h, v30.8h
    umov w9, V<t8_g0_high>.h[0]
    strh w9, [x0, #1296]
    umov w9, V<t8_g0_high>.h[1]
    strh w9, [x0, #1302]
    umov w9, V<t8_g0_high>.h[2]
    strh w9, [x0, #1308]
    umov w9, V<t8_g0_high>.h[3]
    strh w9, [x0, #1314]
    umov w9, V<t8_g0_low>.h[0]
    strh w9, [x0, #432]
    umov w9, V<t8_g0_low>.h[1]
    strh w9, [x0, #438]
    umov w9, V<t8_g0_low>.h[2]
    strh w9, [x0, #444]
    umov w9, V<t8_g0_low>.h[3]
    strh w9, [x0, #450]
    p32_terminal_8_g0_end:
    p32_terminal_8_g1_start:
    ldr Q<t8_g1_x>, [x1, #384]
    sqrdmulh V<t8_g1_lq>.8h, V<t8_g1_x>.8h, v27.8h
    sqrdmulh V<t8_g1_hq>.8h, V<t8_g1_x>.8h, v29.8h
    mul V<t8_g1_low>.8h, V<t8_g1_x>.8h, v26.8h
    mul V<t8_g1_high>.8h, V<t8_g1_x>.8h, v28.8h
    mls V<t8_g1_low>.8h, V<t8_g1_lq>.8h, v30.8h
    mls V<t8_g1_high>.8h, V<t8_g1_hq>.8h, v30.8h
    ext V<t8_g1_lr>.16b, V<t8_g1_low>.16b, V<t8_g1_low>.16b, #8
    ext V<t8_g1_hr>.16b, V<t8_g1_high>.16b, V<t8_g1_high>.16b, #8
    add V<t8_g1_low>.8h, V<t8_g1_low>.8h, V<t8_g1_lr>.8h
    add V<t8_g1_high>.8h, V<t8_g1_high>.8h, V<t8_g1_hr>.8h
    sqrdmulh V<t8_g1_rh>.8h, V<t8_g1_high>.8h, v31.8h
    mls V<t8_g1_high>.8h, V<t8_g1_rh>.8h, v30.8h
    umov w9, V<t8_g1_high>.h[0]
    strh w9, [x0, #1320]
    umov w9, V<t8_g1_high>.h[1]
    strh w9, [x0, #1326]
    umov w9, V<t8_g1_high>.h[2]
    strh w9, [x0, #1332]
    umov w9, V<t8_g1_high>.h[3]
    strh w9, [x0, #1338]
    umov w9, V<t8_g1_low>.h[0]
    strh w9, [x0, #456]
    umov w9, V<t8_g1_low>.h[1]
    strh w9, [x0, #462]
    umov w9, V<t8_g1_low>.h[2]
    strh w9, [x0, #468]
    umov w9, V<t8_g1_low>.h[3]
    strh w9, [x0, #474]
    p32_terminal_8_g1_end:
    p32_terminal_8_g2_start:
    ldr Q<t8_g2_x>, [x1, #640]
    sqrdmulh V<t8_g2_lq>.8h, V<t8_g2_x>.8h, v27.8h
    sqrdmulh V<t8_g2_hq>.8h, V<t8_g2_x>.8h, v29.8h
    mul V<t8_g2_low>.8h, V<t8_g2_x>.8h, v26.8h
    mul V<t8_g2_high>.8h, V<t8_g2_x>.8h, v28.8h
    mls V<t8_g2_low>.8h, V<t8_g2_lq>.8h, v30.8h
    mls V<t8_g2_high>.8h, V<t8_g2_hq>.8h, v30.8h
    ext V<t8_g2_lr>.16b, V<t8_g2_low>.16b, V<t8_g2_low>.16b, #8
    ext V<t8_g2_hr>.16b, V<t8_g2_high>.16b, V<t8_g2_high>.16b, #8
    add V<t8_g2_low>.8h, V<t8_g2_low>.8h, V<t8_g2_lr>.8h
    add V<t8_g2_high>.8h, V<t8_g2_high>.8h, V<t8_g2_hr>.8h
    sqrdmulh V<t8_g2_rh>.8h, V<t8_g2_high>.8h, v31.8h
    mls V<t8_g2_high>.8h, V<t8_g2_rh>.8h, v30.8h
    umov w9, V<t8_g2_high>.h[0]
    strh w9, [x0, #1298]
    umov w9, V<t8_g2_high>.h[1]
    strh w9, [x0, #1304]
    umov w9, V<t8_g2_high>.h[2]
    strh w9, [x0, #1310]
    umov w9, V<t8_g2_high>.h[3]
    strh w9, [x0, #1316]
    umov w9, V<t8_g2_low>.h[0]
    strh w9, [x0, #434]
    umov w9, V<t8_g2_low>.h[1]
    strh w9, [x0, #440]
    umov w9, V<t8_g2_low>.h[2]
    strh w9, [x0, #446]
    umov w9, V<t8_g2_low>.h[3]
    strh w9, [x0, #452]
    p32_terminal_8_g2_end:
    p32_terminal_8_g3_start:
    ldr Q<t8_g3_x>, [x1, #896]
    sqrdmulh V<t8_g3_lq>.8h, V<t8_g3_x>.8h, v27.8h
    sqrdmulh V<t8_g3_hq>.8h, V<t8_g3_x>.8h, v29.8h
    mul V<t8_g3_low>.8h, V<t8_g3_x>.8h, v26.8h
    mul V<t8_g3_high>.8h, V<t8_g3_x>.8h, v28.8h
    mls V<t8_g3_low>.8h, V<t8_g3_lq>.8h, v30.8h
    mls V<t8_g3_high>.8h, V<t8_g3_hq>.8h, v30.8h
    ext V<t8_g3_lr>.16b, V<t8_g3_low>.16b, V<t8_g3_low>.16b, #8
    ext V<t8_g3_hr>.16b, V<t8_g3_high>.16b, V<t8_g3_high>.16b, #8
    add V<t8_g3_low>.8h, V<t8_g3_low>.8h, V<t8_g3_lr>.8h
    add V<t8_g3_high>.8h, V<t8_g3_high>.8h, V<t8_g3_hr>.8h
    sqrdmulh V<t8_g3_rh>.8h, V<t8_g3_high>.8h, v31.8h
    mls V<t8_g3_high>.8h, V<t8_g3_rh>.8h, v30.8h
    umov w9, V<t8_g3_high>.h[0]
    strh w9, [x0, #1322]
    umov w9, V<t8_g3_high>.h[1]
    strh w9, [x0, #1328]
    umov w9, V<t8_g3_high>.h[2]
    strh w9, [x0, #1334]
    umov w9, V<t8_g3_high>.h[3]
    strh w9, [x0, #1340]
    umov w9, V<t8_g3_low>.h[0]
    strh w9, [x0, #458]
    umov w9, V<t8_g3_low>.h[1]
    strh w9, [x0, #464]
    umov w9, V<t8_g3_low>.h[2]
    strh w9, [x0, #470]
    umov w9, V<t8_g3_low>.h[3]
    strh w9, [x0, #476]
    p32_terminal_8_g3_end:
    p32_terminal_8_g4_start:
    ldr Q<t8_g4_x>, [x1, #1152]
    sqrdmulh V<t8_g4_lq>.8h, V<t8_g4_x>.8h, v27.8h
    sqrdmulh V<t8_g4_hq>.8h, V<t8_g4_x>.8h, v29.8h
    mul V<t8_g4_low>.8h, V<t8_g4_x>.8h, v26.8h
    mul V<t8_g4_high>.8h, V<t8_g4_x>.8h, v28.8h
    mls V<t8_g4_low>.8h, V<t8_g4_lq>.8h, v30.8h
    mls V<t8_g4_high>.8h, V<t8_g4_hq>.8h, v30.8h
    ext V<t8_g4_lr>.16b, V<t8_g4_low>.16b, V<t8_g4_low>.16b, #8
    ext V<t8_g4_hr>.16b, V<t8_g4_high>.16b, V<t8_g4_high>.16b, #8
    add V<t8_g4_low>.8h, V<t8_g4_low>.8h, V<t8_g4_lr>.8h
    add V<t8_g4_high>.8h, V<t8_g4_high>.8h, V<t8_g4_hr>.8h
    sqrdmulh V<t8_g4_rh>.8h, V<t8_g4_high>.8h, v31.8h
    mls V<t8_g4_high>.8h, V<t8_g4_rh>.8h, v30.8h
    umov w9, V<t8_g4_high>.h[0]
    strh w9, [x0, #1300]
    umov w9, V<t8_g4_high>.h[1]
    strh w9, [x0, #1306]
    umov w9, V<t8_g4_high>.h[2]
    strh w9, [x0, #1312]
    umov w9, V<t8_g4_high>.h[3]
    strh w9, [x0, #1318]
    umov w9, V<t8_g4_low>.h[0]
    strh w9, [x0, #436]
    umov w9, V<t8_g4_low>.h[1]
    strh w9, [x0, #442]
    umov w9, V<t8_g4_low>.h[2]
    strh w9, [x0, #448]
    umov w9, V<t8_g4_low>.h[3]
    strh w9, [x0, #454]
    p32_terminal_8_g4_end:
    p32_terminal_8_g5_start:
    ldr Q<t8_g5_x>, [x1, #1408]
    sqrdmulh V<t8_g5_lq>.8h, V<t8_g5_x>.8h, v27.8h
    sqrdmulh V<t8_g5_hq>.8h, V<t8_g5_x>.8h, v29.8h
    mul V<t8_g5_low>.8h, V<t8_g5_x>.8h, v26.8h
    mul V<t8_g5_high>.8h, V<t8_g5_x>.8h, v28.8h
    mls V<t8_g5_low>.8h, V<t8_g5_lq>.8h, v30.8h
    mls V<t8_g5_high>.8h, V<t8_g5_hq>.8h, v30.8h
    ext V<t8_g5_lr>.16b, V<t8_g5_low>.16b, V<t8_g5_low>.16b, #8
    ext V<t8_g5_hr>.16b, V<t8_g5_high>.16b, V<t8_g5_high>.16b, #8
    add V<t8_g5_low>.8h, V<t8_g5_low>.8h, V<t8_g5_lr>.8h
    add V<t8_g5_high>.8h, V<t8_g5_high>.8h, V<t8_g5_hr>.8h
    sqrdmulh V<t8_g5_rh>.8h, V<t8_g5_high>.8h, v31.8h
    mls V<t8_g5_high>.8h, V<t8_g5_rh>.8h, v30.8h
    umov w9, V<t8_g5_high>.h[0]
    strh w9, [x0, #1324]
    umov w9, V<t8_g5_high>.h[1]
    strh w9, [x0, #1330]
    umov w9, V<t8_g5_high>.h[2]
    strh w9, [x0, #1336]
    umov w9, V<t8_g5_high>.h[3]
    strh w9, [x0, #1342]
    umov w9, V<t8_g5_low>.h[0]
    strh w9, [x0, #460]
    umov w9, V<t8_g5_low>.h[1]
    strh w9, [x0, #466]
    umov w9, V<t8_g5_low>.h[2]
    strh w9, [x0, #472]
    umov w9, V<t8_g5_low>.h[3]
    strh w9, [x0, #478]
    p32_terminal_8_g5_end:
p32_terminal_8_end:
p32_terminal_9_start:
    ldr q26, [x4, #576]
    ldr q27, [x4, #592]
    ldr q28, [x4, #608]
    ldr q29, [x4, #624]
    p32_terminal_9_g0_start:
    ldr Q<t9_g0_x>, [x1, #144]
    sqrdmulh V<t9_g0_lq>.8h, V<t9_g0_x>.8h, v27.8h
    sqrdmulh V<t9_g0_hq>.8h, V<t9_g0_x>.8h, v29.8h
    mul V<t9_g0_low>.8h, V<t9_g0_x>.8h, v26.8h
    mul V<t9_g0_high>.8h, V<t9_g0_x>.8h, v28.8h
    mls V<t9_g0_low>.8h, V<t9_g0_lq>.8h, v30.8h
    mls V<t9_g0_high>.8h, V<t9_g0_hq>.8h, v30.8h
    ext V<t9_g0_lr>.16b, V<t9_g0_low>.16b, V<t9_g0_low>.16b, #8
    ext V<t9_g0_hr>.16b, V<t9_g0_high>.16b, V<t9_g0_high>.16b, #8
    add V<t9_g0_low>.8h, V<t9_g0_low>.8h, V<t9_g0_lr>.8h
    add V<t9_g0_high>.8h, V<t9_g0_high>.8h, V<t9_g0_hr>.8h
    umov w9, V<t9_g0_high>.h[0]
    strh w9, [x0, #1350]
    umov w9, V<t9_g0_high>.h[1]
    strh w9, [x0, #1356]
    umov w9, V<t9_g0_high>.h[2]
    strh w9, [x0, #1362]
    umov w9, V<t9_g0_high>.h[3]
    strh w9, [x0, #1368]
    umov w9, V<t9_g0_low>.h[0]
    strh w9, [x0, #486]
    umov w9, V<t9_g0_low>.h[1]
    strh w9, [x0, #492]
    umov w9, V<t9_g0_low>.h[2]
    strh w9, [x0, #498]
    umov w9, V<t9_g0_low>.h[3]
    strh w9, [x0, #504]
    p32_terminal_9_g0_end:
    p32_terminal_9_g1_start:
    ldr Q<t9_g1_x>, [x1, #400]
    sqrdmulh V<t9_g1_lq>.8h, V<t9_g1_x>.8h, v27.8h
    sqrdmulh V<t9_g1_hq>.8h, V<t9_g1_x>.8h, v29.8h
    mul V<t9_g1_low>.8h, V<t9_g1_x>.8h, v26.8h
    mul V<t9_g1_high>.8h, V<t9_g1_x>.8h, v28.8h
    mls V<t9_g1_low>.8h, V<t9_g1_lq>.8h, v30.8h
    mls V<t9_g1_high>.8h, V<t9_g1_hq>.8h, v30.8h
    ext V<t9_g1_lr>.16b, V<t9_g1_low>.16b, V<t9_g1_low>.16b, #8
    ext V<t9_g1_hr>.16b, V<t9_g1_high>.16b, V<t9_g1_high>.16b, #8
    add V<t9_g1_low>.8h, V<t9_g1_low>.8h, V<t9_g1_lr>.8h
    add V<t9_g1_high>.8h, V<t9_g1_high>.8h, V<t9_g1_hr>.8h
    umov w9, V<t9_g1_high>.h[0]
    strh w9, [x0, #1374]
    umov w9, V<t9_g1_high>.h[1]
    strh w9, [x0, #1380]
    umov w9, V<t9_g1_high>.h[2]
    strh w9, [x0, #1386]
    umov w9, V<t9_g1_high>.h[3]
    strh w9, [x0, #1392]
    umov w9, V<t9_g1_low>.h[0]
    strh w9, [x0, #510]
    umov w9, V<t9_g1_low>.h[1]
    strh w9, [x0, #516]
    umov w9, V<t9_g1_low>.h[2]
    strh w9, [x0, #522]
    umov w9, V<t9_g1_low>.h[3]
    strh w9, [x0, #528]
    p32_terminal_9_g1_end:
    p32_terminal_9_g2_start:
    ldr Q<t9_g2_x>, [x1, #656]
    sqrdmulh V<t9_g2_lq>.8h, V<t9_g2_x>.8h, v27.8h
    sqrdmulh V<t9_g2_hq>.8h, V<t9_g2_x>.8h, v29.8h
    mul V<t9_g2_low>.8h, V<t9_g2_x>.8h, v26.8h
    mul V<t9_g2_high>.8h, V<t9_g2_x>.8h, v28.8h
    mls V<t9_g2_low>.8h, V<t9_g2_lq>.8h, v30.8h
    mls V<t9_g2_high>.8h, V<t9_g2_hq>.8h, v30.8h
    ext V<t9_g2_lr>.16b, V<t9_g2_low>.16b, V<t9_g2_low>.16b, #8
    ext V<t9_g2_hr>.16b, V<t9_g2_high>.16b, V<t9_g2_high>.16b, #8
    add V<t9_g2_low>.8h, V<t9_g2_low>.8h, V<t9_g2_lr>.8h
    add V<t9_g2_high>.8h, V<t9_g2_high>.8h, V<t9_g2_hr>.8h
    umov w9, V<t9_g2_high>.h[0]
    strh w9, [x0, #1352]
    umov w9, V<t9_g2_high>.h[1]
    strh w9, [x0, #1358]
    umov w9, V<t9_g2_high>.h[2]
    strh w9, [x0, #1364]
    umov w9, V<t9_g2_high>.h[3]
    strh w9, [x0, #1370]
    umov w9, V<t9_g2_low>.h[0]
    strh w9, [x0, #488]
    umov w9, V<t9_g2_low>.h[1]
    strh w9, [x0, #494]
    umov w9, V<t9_g2_low>.h[2]
    strh w9, [x0, #500]
    umov w9, V<t9_g2_low>.h[3]
    strh w9, [x0, #506]
    p32_terminal_9_g2_end:
    p32_terminal_9_g3_start:
    ldr Q<t9_g3_x>, [x1, #912]
    sqrdmulh V<t9_g3_lq>.8h, V<t9_g3_x>.8h, v27.8h
    sqrdmulh V<t9_g3_hq>.8h, V<t9_g3_x>.8h, v29.8h
    mul V<t9_g3_low>.8h, V<t9_g3_x>.8h, v26.8h
    mul V<t9_g3_high>.8h, V<t9_g3_x>.8h, v28.8h
    mls V<t9_g3_low>.8h, V<t9_g3_lq>.8h, v30.8h
    mls V<t9_g3_high>.8h, V<t9_g3_hq>.8h, v30.8h
    ext V<t9_g3_lr>.16b, V<t9_g3_low>.16b, V<t9_g3_low>.16b, #8
    ext V<t9_g3_hr>.16b, V<t9_g3_high>.16b, V<t9_g3_high>.16b, #8
    add V<t9_g3_low>.8h, V<t9_g3_low>.8h, V<t9_g3_lr>.8h
    add V<t9_g3_high>.8h, V<t9_g3_high>.8h, V<t9_g3_hr>.8h
    umov w9, V<t9_g3_high>.h[0]
    strh w9, [x0, #1376]
    umov w9, V<t9_g3_high>.h[1]
    strh w9, [x0, #1382]
    umov w9, V<t9_g3_high>.h[2]
    strh w9, [x0, #1388]
    umov w9, V<t9_g3_high>.h[3]
    strh w9, [x0, #1394]
    umov w9, V<t9_g3_low>.h[0]
    strh w9, [x0, #512]
    umov w9, V<t9_g3_low>.h[1]
    strh w9, [x0, #518]
    umov w9, V<t9_g3_low>.h[2]
    strh w9, [x0, #524]
    umov w9, V<t9_g3_low>.h[3]
    strh w9, [x0, #530]
    p32_terminal_9_g3_end:
    p32_terminal_9_g4_start:
    ldr Q<t9_g4_x>, [x1, #1168]
    sqrdmulh V<t9_g4_lq>.8h, V<t9_g4_x>.8h, v27.8h
    sqrdmulh V<t9_g4_hq>.8h, V<t9_g4_x>.8h, v29.8h
    mul V<t9_g4_low>.8h, V<t9_g4_x>.8h, v26.8h
    mul V<t9_g4_high>.8h, V<t9_g4_x>.8h, v28.8h
    mls V<t9_g4_low>.8h, V<t9_g4_lq>.8h, v30.8h
    mls V<t9_g4_high>.8h, V<t9_g4_hq>.8h, v30.8h
    ext V<t9_g4_lr>.16b, V<t9_g4_low>.16b, V<t9_g4_low>.16b, #8
    ext V<t9_g4_hr>.16b, V<t9_g4_high>.16b, V<t9_g4_high>.16b, #8
    add V<t9_g4_low>.8h, V<t9_g4_low>.8h, V<t9_g4_lr>.8h
    add V<t9_g4_high>.8h, V<t9_g4_high>.8h, V<t9_g4_hr>.8h
    umov w9, V<t9_g4_high>.h[0]
    strh w9, [x0, #1354]
    umov w9, V<t9_g4_high>.h[1]
    strh w9, [x0, #1360]
    umov w9, V<t9_g4_high>.h[2]
    strh w9, [x0, #1366]
    umov w9, V<t9_g4_high>.h[3]
    strh w9, [x0, #1372]
    umov w9, V<t9_g4_low>.h[0]
    strh w9, [x0, #490]
    umov w9, V<t9_g4_low>.h[1]
    strh w9, [x0, #496]
    umov w9, V<t9_g4_low>.h[2]
    strh w9, [x0, #502]
    umov w9, V<t9_g4_low>.h[3]
    strh w9, [x0, #508]
    p32_terminal_9_g4_end:
    p32_terminal_9_g5_start:
    ldr Q<t9_g5_x>, [x1, #1424]
    sqrdmulh V<t9_g5_lq>.8h, V<t9_g5_x>.8h, v27.8h
    sqrdmulh V<t9_g5_hq>.8h, V<t9_g5_x>.8h, v29.8h
    mul V<t9_g5_low>.8h, V<t9_g5_x>.8h, v26.8h
    mul V<t9_g5_high>.8h, V<t9_g5_x>.8h, v28.8h
    mls V<t9_g5_low>.8h, V<t9_g5_lq>.8h, v30.8h
    mls V<t9_g5_high>.8h, V<t9_g5_hq>.8h, v30.8h
    ext V<t9_g5_lr>.16b, V<t9_g5_low>.16b, V<t9_g5_low>.16b, #8
    ext V<t9_g5_hr>.16b, V<t9_g5_high>.16b, V<t9_g5_high>.16b, #8
    add V<t9_g5_low>.8h, V<t9_g5_low>.8h, V<t9_g5_lr>.8h
    add V<t9_g5_high>.8h, V<t9_g5_high>.8h, V<t9_g5_hr>.8h
    umov w9, V<t9_g5_high>.h[0]
    strh w9, [x0, #1378]
    umov w9, V<t9_g5_high>.h[1]
    strh w9, [x0, #1384]
    umov w9, V<t9_g5_high>.h[2]
    strh w9, [x0, #1390]
    umov w9, V<t9_g5_high>.h[3]
    strh w9, [x0, #1396]
    umov w9, V<t9_g5_low>.h[0]
    strh w9, [x0, #514]
    umov w9, V<t9_g5_low>.h[1]
    strh w9, [x0, #520]
    umov w9, V<t9_g5_low>.h[2]
    strh w9, [x0, #526]
    umov w9, V<t9_g5_low>.h[3]
    strh w9, [x0, #532]
    p32_terminal_9_g5_end:
p32_terminal_9_end:
p32_terminal_10_start:
    ldr q26, [x4, #640]
    ldr q27, [x4, #656]
    ldr q28, [x4, #672]
    ldr q29, [x4, #688]
    p32_terminal_10_g0_start:
    ldr Q<t10_g0_x>, [x1, #160]
    sqrdmulh V<t10_g0_lq>.8h, V<t10_g0_x>.8h, v27.8h
    sqrdmulh V<t10_g0_hq>.8h, V<t10_g0_x>.8h, v29.8h
    mul V<t10_g0_low>.8h, V<t10_g0_x>.8h, v26.8h
    mul V<t10_g0_high>.8h, V<t10_g0_x>.8h, v28.8h
    mls V<t10_g0_low>.8h, V<t10_g0_lq>.8h, v30.8h
    mls V<t10_g0_high>.8h, V<t10_g0_hq>.8h, v30.8h
    ext V<t10_g0_lr>.16b, V<t10_g0_low>.16b, V<t10_g0_low>.16b, #8
    ext V<t10_g0_hr>.16b, V<t10_g0_high>.16b, V<t10_g0_high>.16b, #8
    add V<t10_g0_low>.8h, V<t10_g0_low>.8h, V<t10_g0_lr>.8h
    add V<t10_g0_high>.8h, V<t10_g0_high>.8h, V<t10_g0_hr>.8h
    sqrdmulh V<t10_g0_rh>.8h, V<t10_g0_high>.8h, v31.8h
    mls V<t10_g0_high>.8h, V<t10_g0_rh>.8h, v30.8h
    umov w9, V<t10_g0_high>.h[0]
    strh w9, [x0, #1404]
    umov w9, V<t10_g0_high>.h[1]
    strh w9, [x0, #1410]
    umov w9, V<t10_g0_high>.h[2]
    strh w9, [x0, #1416]
    umov w9, V<t10_g0_high>.h[3]
    strh w9, [x0, #1422]
    umov w9, V<t10_g0_low>.h[0]
    strh w9, [x0, #540]
    umov w9, V<t10_g0_low>.h[1]
    strh w9, [x0, #546]
    umov w9, V<t10_g0_low>.h[2]
    strh w9, [x0, #552]
    umov w9, V<t10_g0_low>.h[3]
    strh w9, [x0, #558]
    p32_terminal_10_g0_end:
    p32_terminal_10_g1_start:
    ldr Q<t10_g1_x>, [x1, #416]
    sqrdmulh V<t10_g1_lq>.8h, V<t10_g1_x>.8h, v27.8h
    sqrdmulh V<t10_g1_hq>.8h, V<t10_g1_x>.8h, v29.8h
    mul V<t10_g1_low>.8h, V<t10_g1_x>.8h, v26.8h
    mul V<t10_g1_high>.8h, V<t10_g1_x>.8h, v28.8h
    mls V<t10_g1_low>.8h, V<t10_g1_lq>.8h, v30.8h
    mls V<t10_g1_high>.8h, V<t10_g1_hq>.8h, v30.8h
    ext V<t10_g1_lr>.16b, V<t10_g1_low>.16b, V<t10_g1_low>.16b, #8
    ext V<t10_g1_hr>.16b, V<t10_g1_high>.16b, V<t10_g1_high>.16b, #8
    add V<t10_g1_low>.8h, V<t10_g1_low>.8h, V<t10_g1_lr>.8h
    add V<t10_g1_high>.8h, V<t10_g1_high>.8h, V<t10_g1_hr>.8h
    sqrdmulh V<t10_g1_rh>.8h, V<t10_g1_high>.8h, v31.8h
    mls V<t10_g1_high>.8h, V<t10_g1_rh>.8h, v30.8h
    umov w9, V<t10_g1_high>.h[0]
    strh w9, [x0, #1428]
    umov w9, V<t10_g1_high>.h[1]
    strh w9, [x0, #1434]
    umov w9, V<t10_g1_high>.h[2]
    strh w9, [x0, #1440]
    umov w9, V<t10_g1_high>.h[3]
    strh w9, [x0, #1446]
    umov w9, V<t10_g1_low>.h[0]
    strh w9, [x0, #564]
    umov w9, V<t10_g1_low>.h[1]
    strh w9, [x0, #570]
    umov w9, V<t10_g1_low>.h[2]
    strh w9, [x0, #576]
    umov w9, V<t10_g1_low>.h[3]
    strh w9, [x0, #582]
    p32_terminal_10_g1_end:
    p32_terminal_10_g2_start:
    ldr Q<t10_g2_x>, [x1, #672]
    sqrdmulh V<t10_g2_lq>.8h, V<t10_g2_x>.8h, v27.8h
    sqrdmulh V<t10_g2_hq>.8h, V<t10_g2_x>.8h, v29.8h
    mul V<t10_g2_low>.8h, V<t10_g2_x>.8h, v26.8h
    mul V<t10_g2_high>.8h, V<t10_g2_x>.8h, v28.8h
    mls V<t10_g2_low>.8h, V<t10_g2_lq>.8h, v30.8h
    mls V<t10_g2_high>.8h, V<t10_g2_hq>.8h, v30.8h
    ext V<t10_g2_lr>.16b, V<t10_g2_low>.16b, V<t10_g2_low>.16b, #8
    ext V<t10_g2_hr>.16b, V<t10_g2_high>.16b, V<t10_g2_high>.16b, #8
    add V<t10_g2_low>.8h, V<t10_g2_low>.8h, V<t10_g2_lr>.8h
    add V<t10_g2_high>.8h, V<t10_g2_high>.8h, V<t10_g2_hr>.8h
    sqrdmulh V<t10_g2_rh>.8h, V<t10_g2_high>.8h, v31.8h
    mls V<t10_g2_high>.8h, V<t10_g2_rh>.8h, v30.8h
    umov w9, V<t10_g2_high>.h[0]
    strh w9, [x0, #1406]
    umov w9, V<t10_g2_high>.h[1]
    strh w9, [x0, #1412]
    umov w9, V<t10_g2_high>.h[2]
    strh w9, [x0, #1418]
    umov w9, V<t10_g2_high>.h[3]
    strh w9, [x0, #1424]
    umov w9, V<t10_g2_low>.h[0]
    strh w9, [x0, #542]
    umov w9, V<t10_g2_low>.h[1]
    strh w9, [x0, #548]
    umov w9, V<t10_g2_low>.h[2]
    strh w9, [x0, #554]
    umov w9, V<t10_g2_low>.h[3]
    strh w9, [x0, #560]
    p32_terminal_10_g2_end:
    p32_terminal_10_g3_start:
    ldr Q<t10_g3_x>, [x1, #928]
    sqrdmulh V<t10_g3_lq>.8h, V<t10_g3_x>.8h, v27.8h
    sqrdmulh V<t10_g3_hq>.8h, V<t10_g3_x>.8h, v29.8h
    mul V<t10_g3_low>.8h, V<t10_g3_x>.8h, v26.8h
    mul V<t10_g3_high>.8h, V<t10_g3_x>.8h, v28.8h
    mls V<t10_g3_low>.8h, V<t10_g3_lq>.8h, v30.8h
    mls V<t10_g3_high>.8h, V<t10_g3_hq>.8h, v30.8h
    ext V<t10_g3_lr>.16b, V<t10_g3_low>.16b, V<t10_g3_low>.16b, #8
    ext V<t10_g3_hr>.16b, V<t10_g3_high>.16b, V<t10_g3_high>.16b, #8
    add V<t10_g3_low>.8h, V<t10_g3_low>.8h, V<t10_g3_lr>.8h
    add V<t10_g3_high>.8h, V<t10_g3_high>.8h, V<t10_g3_hr>.8h
    sqrdmulh V<t10_g3_rh>.8h, V<t10_g3_high>.8h, v31.8h
    mls V<t10_g3_high>.8h, V<t10_g3_rh>.8h, v30.8h
    umov w9, V<t10_g3_high>.h[0]
    strh w9, [x0, #1430]
    umov w9, V<t10_g3_high>.h[1]
    strh w9, [x0, #1436]
    umov w9, V<t10_g3_high>.h[2]
    strh w9, [x0, #1442]
    umov w9, V<t10_g3_high>.h[3]
    strh w9, [x0, #1448]
    umov w9, V<t10_g3_low>.h[0]
    strh w9, [x0, #566]
    umov w9, V<t10_g3_low>.h[1]
    strh w9, [x0, #572]
    umov w9, V<t10_g3_low>.h[2]
    strh w9, [x0, #578]
    umov w9, V<t10_g3_low>.h[3]
    strh w9, [x0, #584]
    p32_terminal_10_g3_end:
    p32_terminal_10_g4_start:
    ldr Q<t10_g4_x>, [x1, #1184]
    sqrdmulh V<t10_g4_lq>.8h, V<t10_g4_x>.8h, v27.8h
    sqrdmulh V<t10_g4_hq>.8h, V<t10_g4_x>.8h, v29.8h
    mul V<t10_g4_low>.8h, V<t10_g4_x>.8h, v26.8h
    mul V<t10_g4_high>.8h, V<t10_g4_x>.8h, v28.8h
    mls V<t10_g4_low>.8h, V<t10_g4_lq>.8h, v30.8h
    mls V<t10_g4_high>.8h, V<t10_g4_hq>.8h, v30.8h
    ext V<t10_g4_lr>.16b, V<t10_g4_low>.16b, V<t10_g4_low>.16b, #8
    ext V<t10_g4_hr>.16b, V<t10_g4_high>.16b, V<t10_g4_high>.16b, #8
    add V<t10_g4_low>.8h, V<t10_g4_low>.8h, V<t10_g4_lr>.8h
    add V<t10_g4_high>.8h, V<t10_g4_high>.8h, V<t10_g4_hr>.8h
    sqrdmulh V<t10_g4_rh>.8h, V<t10_g4_high>.8h, v31.8h
    mls V<t10_g4_high>.8h, V<t10_g4_rh>.8h, v30.8h
    umov w9, V<t10_g4_high>.h[0]
    strh w9, [x0, #1408]
    umov w9, V<t10_g4_high>.h[1]
    strh w9, [x0, #1414]
    umov w9, V<t10_g4_high>.h[2]
    strh w9, [x0, #1420]
    umov w9, V<t10_g4_high>.h[3]
    strh w9, [x0, #1426]
    umov w9, V<t10_g4_low>.h[0]
    strh w9, [x0, #544]
    umov w9, V<t10_g4_low>.h[1]
    strh w9, [x0, #550]
    umov w9, V<t10_g4_low>.h[2]
    strh w9, [x0, #556]
    umov w9, V<t10_g4_low>.h[3]
    strh w9, [x0, #562]
    p32_terminal_10_g4_end:
    p32_terminal_10_g5_start:
    ldr Q<t10_g5_x>, [x1, #1440]
    sqrdmulh V<t10_g5_lq>.8h, V<t10_g5_x>.8h, v27.8h
    sqrdmulh V<t10_g5_hq>.8h, V<t10_g5_x>.8h, v29.8h
    mul V<t10_g5_low>.8h, V<t10_g5_x>.8h, v26.8h
    mul V<t10_g5_high>.8h, V<t10_g5_x>.8h, v28.8h
    mls V<t10_g5_low>.8h, V<t10_g5_lq>.8h, v30.8h
    mls V<t10_g5_high>.8h, V<t10_g5_hq>.8h, v30.8h
    ext V<t10_g5_lr>.16b, V<t10_g5_low>.16b, V<t10_g5_low>.16b, #8
    ext V<t10_g5_hr>.16b, V<t10_g5_high>.16b, V<t10_g5_high>.16b, #8
    add V<t10_g5_low>.8h, V<t10_g5_low>.8h, V<t10_g5_lr>.8h
    add V<t10_g5_high>.8h, V<t10_g5_high>.8h, V<t10_g5_hr>.8h
    sqrdmulh V<t10_g5_rh>.8h, V<t10_g5_high>.8h, v31.8h
    mls V<t10_g5_high>.8h, V<t10_g5_rh>.8h, v30.8h
    umov w9, V<t10_g5_high>.h[0]
    strh w9, [x0, #1432]
    umov w9, V<t10_g5_high>.h[1]
    strh w9, [x0, #1438]
    umov w9, V<t10_g5_high>.h[2]
    strh w9, [x0, #1444]
    umov w9, V<t10_g5_high>.h[3]
    strh w9, [x0, #1450]
    umov w9, V<t10_g5_low>.h[0]
    strh w9, [x0, #568]
    umov w9, V<t10_g5_low>.h[1]
    strh w9, [x0, #574]
    umov w9, V<t10_g5_low>.h[2]
    strh w9, [x0, #580]
    umov w9, V<t10_g5_low>.h[3]
    strh w9, [x0, #586]
    p32_terminal_10_g5_end:
p32_terminal_10_end:
p32_terminal_11_start:
    ldr q26, [x4, #704]
    ldr q27, [x4, #720]
    ldr q28, [x4, #736]
    ldr q29, [x4, #752]
    p32_terminal_11_g0_start:
    ldr Q<t11_g0_x>, [x1, #176]
    sqrdmulh V<t11_g0_lq>.8h, V<t11_g0_x>.8h, v27.8h
    sqrdmulh V<t11_g0_hq>.8h, V<t11_g0_x>.8h, v29.8h
    mul V<t11_g0_low>.8h, V<t11_g0_x>.8h, v26.8h
    mul V<t11_g0_high>.8h, V<t11_g0_x>.8h, v28.8h
    mls V<t11_g0_low>.8h, V<t11_g0_lq>.8h, v30.8h
    mls V<t11_g0_high>.8h, V<t11_g0_hq>.8h, v30.8h
    ext V<t11_g0_lr>.16b, V<t11_g0_low>.16b, V<t11_g0_low>.16b, #8
    ext V<t11_g0_hr>.16b, V<t11_g0_high>.16b, V<t11_g0_high>.16b, #8
    add V<t11_g0_low>.8h, V<t11_g0_low>.8h, V<t11_g0_lr>.8h
    add V<t11_g0_high>.8h, V<t11_g0_high>.8h, V<t11_g0_hr>.8h
    umov w9, V<t11_g0_high>.h[0]
    strh w9, [x0, #1458]
    umov w9, V<t11_g0_high>.h[1]
    strh w9, [x0, #1464]
    umov w9, V<t11_g0_high>.h[2]
    strh w9, [x0, #1470]
    umov w9, V<t11_g0_high>.h[3]
    strh w9, [x0, #1476]
    umov w9, V<t11_g0_low>.h[0]
    strh w9, [x0, #594]
    umov w9, V<t11_g0_low>.h[1]
    strh w9, [x0, #600]
    umov w9, V<t11_g0_low>.h[2]
    strh w9, [x0, #606]
    umov w9, V<t11_g0_low>.h[3]
    strh w9, [x0, #612]
    p32_terminal_11_g0_end:
    p32_terminal_11_g1_start:
    ldr Q<t11_g1_x>, [x1, #432]
    sqrdmulh V<t11_g1_lq>.8h, V<t11_g1_x>.8h, v27.8h
    sqrdmulh V<t11_g1_hq>.8h, V<t11_g1_x>.8h, v29.8h
    mul V<t11_g1_low>.8h, V<t11_g1_x>.8h, v26.8h
    mul V<t11_g1_high>.8h, V<t11_g1_x>.8h, v28.8h
    mls V<t11_g1_low>.8h, V<t11_g1_lq>.8h, v30.8h
    mls V<t11_g1_high>.8h, V<t11_g1_hq>.8h, v30.8h
    ext V<t11_g1_lr>.16b, V<t11_g1_low>.16b, V<t11_g1_low>.16b, #8
    ext V<t11_g1_hr>.16b, V<t11_g1_high>.16b, V<t11_g1_high>.16b, #8
    add V<t11_g1_low>.8h, V<t11_g1_low>.8h, V<t11_g1_lr>.8h
    add V<t11_g1_high>.8h, V<t11_g1_high>.8h, V<t11_g1_hr>.8h
    umov w9, V<t11_g1_high>.h[0]
    strh w9, [x0, #1482]
    umov w9, V<t11_g1_high>.h[1]
    strh w9, [x0, #1488]
    umov w9, V<t11_g1_high>.h[2]
    strh w9, [x0, #1494]
    umov w9, V<t11_g1_high>.h[3]
    strh w9, [x0, #1500]
    umov w9, V<t11_g1_low>.h[0]
    strh w9, [x0, #618]
    umov w9, V<t11_g1_low>.h[1]
    strh w9, [x0, #624]
    umov w9, V<t11_g1_low>.h[2]
    strh w9, [x0, #630]
    umov w9, V<t11_g1_low>.h[3]
    strh w9, [x0, #636]
    p32_terminal_11_g1_end:
    p32_terminal_11_g2_start:
    ldr Q<t11_g2_x>, [x1, #688]
    sqrdmulh V<t11_g2_lq>.8h, V<t11_g2_x>.8h, v27.8h
    sqrdmulh V<t11_g2_hq>.8h, V<t11_g2_x>.8h, v29.8h
    mul V<t11_g2_low>.8h, V<t11_g2_x>.8h, v26.8h
    mul V<t11_g2_high>.8h, V<t11_g2_x>.8h, v28.8h
    mls V<t11_g2_low>.8h, V<t11_g2_lq>.8h, v30.8h
    mls V<t11_g2_high>.8h, V<t11_g2_hq>.8h, v30.8h
    ext V<t11_g2_lr>.16b, V<t11_g2_low>.16b, V<t11_g2_low>.16b, #8
    ext V<t11_g2_hr>.16b, V<t11_g2_high>.16b, V<t11_g2_high>.16b, #8
    add V<t11_g2_low>.8h, V<t11_g2_low>.8h, V<t11_g2_lr>.8h
    add V<t11_g2_high>.8h, V<t11_g2_high>.8h, V<t11_g2_hr>.8h
    umov w9, V<t11_g2_high>.h[0]
    strh w9, [x0, #1460]
    umov w9, V<t11_g2_high>.h[1]
    strh w9, [x0, #1466]
    umov w9, V<t11_g2_high>.h[2]
    strh w9, [x0, #1472]
    umov w9, V<t11_g2_high>.h[3]
    strh w9, [x0, #1478]
    umov w9, V<t11_g2_low>.h[0]
    strh w9, [x0, #596]
    umov w9, V<t11_g2_low>.h[1]
    strh w9, [x0, #602]
    umov w9, V<t11_g2_low>.h[2]
    strh w9, [x0, #608]
    umov w9, V<t11_g2_low>.h[3]
    strh w9, [x0, #614]
    p32_terminal_11_g2_end:
    p32_terminal_11_g3_start:
    ldr Q<t11_g3_x>, [x1, #944]
    sqrdmulh V<t11_g3_lq>.8h, V<t11_g3_x>.8h, v27.8h
    sqrdmulh V<t11_g3_hq>.8h, V<t11_g3_x>.8h, v29.8h
    mul V<t11_g3_low>.8h, V<t11_g3_x>.8h, v26.8h
    mul V<t11_g3_high>.8h, V<t11_g3_x>.8h, v28.8h
    mls V<t11_g3_low>.8h, V<t11_g3_lq>.8h, v30.8h
    mls V<t11_g3_high>.8h, V<t11_g3_hq>.8h, v30.8h
    ext V<t11_g3_lr>.16b, V<t11_g3_low>.16b, V<t11_g3_low>.16b, #8
    ext V<t11_g3_hr>.16b, V<t11_g3_high>.16b, V<t11_g3_high>.16b, #8
    add V<t11_g3_low>.8h, V<t11_g3_low>.8h, V<t11_g3_lr>.8h
    add V<t11_g3_high>.8h, V<t11_g3_high>.8h, V<t11_g3_hr>.8h
    umov w9, V<t11_g3_high>.h[0]
    strh w9, [x0, #1484]
    umov w9, V<t11_g3_high>.h[1]
    strh w9, [x0, #1490]
    umov w9, V<t11_g3_high>.h[2]
    strh w9, [x0, #1496]
    umov w9, V<t11_g3_high>.h[3]
    strh w9, [x0, #1502]
    umov w9, V<t11_g3_low>.h[0]
    strh w9, [x0, #620]
    umov w9, V<t11_g3_low>.h[1]
    strh w9, [x0, #626]
    umov w9, V<t11_g3_low>.h[2]
    strh w9, [x0, #632]
    umov w9, V<t11_g3_low>.h[3]
    strh w9, [x0, #638]
    p32_terminal_11_g3_end:
    p32_terminal_11_g4_start:
    ldr Q<t11_g4_x>, [x1, #1200]
    sqrdmulh V<t11_g4_lq>.8h, V<t11_g4_x>.8h, v27.8h
    sqrdmulh V<t11_g4_hq>.8h, V<t11_g4_x>.8h, v29.8h
    mul V<t11_g4_low>.8h, V<t11_g4_x>.8h, v26.8h
    mul V<t11_g4_high>.8h, V<t11_g4_x>.8h, v28.8h
    mls V<t11_g4_low>.8h, V<t11_g4_lq>.8h, v30.8h
    mls V<t11_g4_high>.8h, V<t11_g4_hq>.8h, v30.8h
    ext V<t11_g4_lr>.16b, V<t11_g4_low>.16b, V<t11_g4_low>.16b, #8
    ext V<t11_g4_hr>.16b, V<t11_g4_high>.16b, V<t11_g4_high>.16b, #8
    add V<t11_g4_low>.8h, V<t11_g4_low>.8h, V<t11_g4_lr>.8h
    add V<t11_g4_high>.8h, V<t11_g4_high>.8h, V<t11_g4_hr>.8h
    umov w9, V<t11_g4_high>.h[0]
    strh w9, [x0, #1462]
    umov w9, V<t11_g4_high>.h[1]
    strh w9, [x0, #1468]
    umov w9, V<t11_g4_high>.h[2]
    strh w9, [x0, #1474]
    umov w9, V<t11_g4_high>.h[3]
    strh w9, [x0, #1480]
    umov w9, V<t11_g4_low>.h[0]
    strh w9, [x0, #598]
    umov w9, V<t11_g4_low>.h[1]
    strh w9, [x0, #604]
    umov w9, V<t11_g4_low>.h[2]
    strh w9, [x0, #610]
    umov w9, V<t11_g4_low>.h[3]
    strh w9, [x0, #616]
    p32_terminal_11_g4_end:
    p32_terminal_11_g5_start:
    ldr Q<t11_g5_x>, [x1, #1456]
    sqrdmulh V<t11_g5_lq>.8h, V<t11_g5_x>.8h, v27.8h
    sqrdmulh V<t11_g5_hq>.8h, V<t11_g5_x>.8h, v29.8h
    mul V<t11_g5_low>.8h, V<t11_g5_x>.8h, v26.8h
    mul V<t11_g5_high>.8h, V<t11_g5_x>.8h, v28.8h
    mls V<t11_g5_low>.8h, V<t11_g5_lq>.8h, v30.8h
    mls V<t11_g5_high>.8h, V<t11_g5_hq>.8h, v30.8h
    ext V<t11_g5_lr>.16b, V<t11_g5_low>.16b, V<t11_g5_low>.16b, #8
    ext V<t11_g5_hr>.16b, V<t11_g5_high>.16b, V<t11_g5_high>.16b, #8
    add V<t11_g5_low>.8h, V<t11_g5_low>.8h, V<t11_g5_lr>.8h
    add V<t11_g5_high>.8h, V<t11_g5_high>.8h, V<t11_g5_hr>.8h
    umov w9, V<t11_g5_high>.h[0]
    strh w9, [x0, #1486]
    umov w9, V<t11_g5_high>.h[1]
    strh w9, [x0, #1492]
    umov w9, V<t11_g5_high>.h[2]
    strh w9, [x0, #1498]
    umov w9, V<t11_g5_high>.h[3]
    strh w9, [x0, #1504]
    umov w9, V<t11_g5_low>.h[0]
    strh w9, [x0, #622]
    umov w9, V<t11_g5_low>.h[1]
    strh w9, [x0, #628]
    umov w9, V<t11_g5_low>.h[2]
    strh w9, [x0, #634]
    umov w9, V<t11_g5_low>.h[3]
    strh w9, [x0, #640]
    p32_terminal_11_g5_end:
p32_terminal_11_end:
p32_terminal_12_start:
    ldr q26, [x4, #768]
    ldr q27, [x4, #784]
    ldr q28, [x4, #800]
    ldr q29, [x4, #816]
    p32_terminal_12_g0_start:
    ldr Q<t12_g0_x>, [x1, #192]
    sqrdmulh V<t12_g0_lq>.8h, V<t12_g0_x>.8h, v27.8h
    sqrdmulh V<t12_g0_hq>.8h, V<t12_g0_x>.8h, v29.8h
    mul V<t12_g0_low>.8h, V<t12_g0_x>.8h, v26.8h
    mul V<t12_g0_high>.8h, V<t12_g0_x>.8h, v28.8h
    mls V<t12_g0_low>.8h, V<t12_g0_lq>.8h, v30.8h
    mls V<t12_g0_high>.8h, V<t12_g0_hq>.8h, v30.8h
    ext V<t12_g0_lr>.16b, V<t12_g0_low>.16b, V<t12_g0_low>.16b, #8
    ext V<t12_g0_hr>.16b, V<t12_g0_high>.16b, V<t12_g0_high>.16b, #8
    add V<t12_g0_low>.8h, V<t12_g0_low>.8h, V<t12_g0_lr>.8h
    add V<t12_g0_high>.8h, V<t12_g0_high>.8h, V<t12_g0_hr>.8h
    sqrdmulh V<t12_g0_rl>.8h, V<t12_g0_low>.8h, v31.8h
    mls V<t12_g0_low>.8h, V<t12_g0_rl>.8h, v30.8h
    umov w9, V<t12_g0_high>.h[0]
    strh w9, [x0, #1512]
    umov w9, V<t12_g0_high>.h[1]
    strh w9, [x0, #1518]
    umov w9, V<t12_g0_high>.h[2]
    strh w9, [x0, #1524]
    umov w9, V<t12_g0_high>.h[3]
    strh w9, [x0, #1530]
    umov w9, V<t12_g0_low>.h[0]
    strh w9, [x0, #648]
    umov w9, V<t12_g0_low>.h[1]
    strh w9, [x0, #654]
    umov w9, V<t12_g0_low>.h[2]
    strh w9, [x0, #660]
    umov w9, V<t12_g0_low>.h[3]
    strh w9, [x0, #666]
    p32_terminal_12_g0_end:
    p32_terminal_12_g1_start:
    ldr Q<t12_g1_x>, [x1, #448]
    sqrdmulh V<t12_g1_lq>.8h, V<t12_g1_x>.8h, v27.8h
    sqrdmulh V<t12_g1_hq>.8h, V<t12_g1_x>.8h, v29.8h
    mul V<t12_g1_low>.8h, V<t12_g1_x>.8h, v26.8h
    mul V<t12_g1_high>.8h, V<t12_g1_x>.8h, v28.8h
    mls V<t12_g1_low>.8h, V<t12_g1_lq>.8h, v30.8h
    mls V<t12_g1_high>.8h, V<t12_g1_hq>.8h, v30.8h
    ext V<t12_g1_lr>.16b, V<t12_g1_low>.16b, V<t12_g1_low>.16b, #8
    ext V<t12_g1_hr>.16b, V<t12_g1_high>.16b, V<t12_g1_high>.16b, #8
    add V<t12_g1_low>.8h, V<t12_g1_low>.8h, V<t12_g1_lr>.8h
    add V<t12_g1_high>.8h, V<t12_g1_high>.8h, V<t12_g1_hr>.8h
    sqrdmulh V<t12_g1_rl>.8h, V<t12_g1_low>.8h, v31.8h
    mls V<t12_g1_low>.8h, V<t12_g1_rl>.8h, v30.8h
    umov w9, V<t12_g1_high>.h[0]
    strh w9, [x0, #1536]
    umov w9, V<t12_g1_high>.h[1]
    strh w9, [x0, #1542]
    umov w9, V<t12_g1_high>.h[2]
    strh w9, [x0, #1548]
    umov w9, V<t12_g1_high>.h[3]
    strh w9, [x0, #1554]
    umov w9, V<t12_g1_low>.h[0]
    strh w9, [x0, #672]
    umov w9, V<t12_g1_low>.h[1]
    strh w9, [x0, #678]
    umov w9, V<t12_g1_low>.h[2]
    strh w9, [x0, #684]
    umov w9, V<t12_g1_low>.h[3]
    strh w9, [x0, #690]
    p32_terminal_12_g1_end:
    p32_terminal_12_g2_start:
    ldr Q<t12_g2_x>, [x1, #704]
    sqrdmulh V<t12_g2_lq>.8h, V<t12_g2_x>.8h, v27.8h
    sqrdmulh V<t12_g2_hq>.8h, V<t12_g2_x>.8h, v29.8h
    mul V<t12_g2_low>.8h, V<t12_g2_x>.8h, v26.8h
    mul V<t12_g2_high>.8h, V<t12_g2_x>.8h, v28.8h
    mls V<t12_g2_low>.8h, V<t12_g2_lq>.8h, v30.8h
    mls V<t12_g2_high>.8h, V<t12_g2_hq>.8h, v30.8h
    ext V<t12_g2_lr>.16b, V<t12_g2_low>.16b, V<t12_g2_low>.16b, #8
    ext V<t12_g2_hr>.16b, V<t12_g2_high>.16b, V<t12_g2_high>.16b, #8
    add V<t12_g2_low>.8h, V<t12_g2_low>.8h, V<t12_g2_lr>.8h
    add V<t12_g2_high>.8h, V<t12_g2_high>.8h, V<t12_g2_hr>.8h
    sqrdmulh V<t12_g2_rl>.8h, V<t12_g2_low>.8h, v31.8h
    mls V<t12_g2_low>.8h, V<t12_g2_rl>.8h, v30.8h
    umov w9, V<t12_g2_high>.h[0]
    strh w9, [x0, #1514]
    umov w9, V<t12_g2_high>.h[1]
    strh w9, [x0, #1520]
    umov w9, V<t12_g2_high>.h[2]
    strh w9, [x0, #1526]
    umov w9, V<t12_g2_high>.h[3]
    strh w9, [x0, #1532]
    umov w9, V<t12_g2_low>.h[0]
    strh w9, [x0, #650]
    umov w9, V<t12_g2_low>.h[1]
    strh w9, [x0, #656]
    umov w9, V<t12_g2_low>.h[2]
    strh w9, [x0, #662]
    umov w9, V<t12_g2_low>.h[3]
    strh w9, [x0, #668]
    p32_terminal_12_g2_end:
    p32_terminal_12_g3_start:
    ldr Q<t12_g3_x>, [x1, #960]
    sqrdmulh V<t12_g3_lq>.8h, V<t12_g3_x>.8h, v27.8h
    sqrdmulh V<t12_g3_hq>.8h, V<t12_g3_x>.8h, v29.8h
    mul V<t12_g3_low>.8h, V<t12_g3_x>.8h, v26.8h
    mul V<t12_g3_high>.8h, V<t12_g3_x>.8h, v28.8h
    mls V<t12_g3_low>.8h, V<t12_g3_lq>.8h, v30.8h
    mls V<t12_g3_high>.8h, V<t12_g3_hq>.8h, v30.8h
    ext V<t12_g3_lr>.16b, V<t12_g3_low>.16b, V<t12_g3_low>.16b, #8
    ext V<t12_g3_hr>.16b, V<t12_g3_high>.16b, V<t12_g3_high>.16b, #8
    add V<t12_g3_low>.8h, V<t12_g3_low>.8h, V<t12_g3_lr>.8h
    add V<t12_g3_high>.8h, V<t12_g3_high>.8h, V<t12_g3_hr>.8h
    sqrdmulh V<t12_g3_rl>.8h, V<t12_g3_low>.8h, v31.8h
    mls V<t12_g3_low>.8h, V<t12_g3_rl>.8h, v30.8h
    umov w9, V<t12_g3_high>.h[0]
    strh w9, [x0, #1538]
    umov w9, V<t12_g3_high>.h[1]
    strh w9, [x0, #1544]
    umov w9, V<t12_g3_high>.h[2]
    strh w9, [x0, #1550]
    umov w9, V<t12_g3_high>.h[3]
    strh w9, [x0, #1556]
    umov w9, V<t12_g3_low>.h[0]
    strh w9, [x0, #674]
    umov w9, V<t12_g3_low>.h[1]
    strh w9, [x0, #680]
    umov w9, V<t12_g3_low>.h[2]
    strh w9, [x0, #686]
    umov w9, V<t12_g3_low>.h[3]
    strh w9, [x0, #692]
    p32_terminal_12_g3_end:
    p32_terminal_12_g4_start:
    ldr Q<t12_g4_x>, [x1, #1216]
    sqrdmulh V<t12_g4_lq>.8h, V<t12_g4_x>.8h, v27.8h
    sqrdmulh V<t12_g4_hq>.8h, V<t12_g4_x>.8h, v29.8h
    mul V<t12_g4_low>.8h, V<t12_g4_x>.8h, v26.8h
    mul V<t12_g4_high>.8h, V<t12_g4_x>.8h, v28.8h
    mls V<t12_g4_low>.8h, V<t12_g4_lq>.8h, v30.8h
    mls V<t12_g4_high>.8h, V<t12_g4_hq>.8h, v30.8h
    ext V<t12_g4_lr>.16b, V<t12_g4_low>.16b, V<t12_g4_low>.16b, #8
    ext V<t12_g4_hr>.16b, V<t12_g4_high>.16b, V<t12_g4_high>.16b, #8
    add V<t12_g4_low>.8h, V<t12_g4_low>.8h, V<t12_g4_lr>.8h
    add V<t12_g4_high>.8h, V<t12_g4_high>.8h, V<t12_g4_hr>.8h
    sqrdmulh V<t12_g4_rl>.8h, V<t12_g4_low>.8h, v31.8h
    mls V<t12_g4_low>.8h, V<t12_g4_rl>.8h, v30.8h
    umov w9, V<t12_g4_high>.h[0]
    strh w9, [x0, #1516]
    umov w9, V<t12_g4_high>.h[1]
    strh w9, [x0, #1522]
    umov w9, V<t12_g4_high>.h[2]
    strh w9, [x0, #1528]
    umov w9, V<t12_g4_high>.h[3]
    strh w9, [x0, #1534]
    umov w9, V<t12_g4_low>.h[0]
    strh w9, [x0, #652]
    umov w9, V<t12_g4_low>.h[1]
    strh w9, [x0, #658]
    umov w9, V<t12_g4_low>.h[2]
    strh w9, [x0, #664]
    umov w9, V<t12_g4_low>.h[3]
    strh w9, [x0, #670]
    p32_terminal_12_g4_end:
    p32_terminal_12_g5_start:
    ldr Q<t12_g5_x>, [x1, #1472]
    sqrdmulh V<t12_g5_lq>.8h, V<t12_g5_x>.8h, v27.8h
    sqrdmulh V<t12_g5_hq>.8h, V<t12_g5_x>.8h, v29.8h
    mul V<t12_g5_low>.8h, V<t12_g5_x>.8h, v26.8h
    mul V<t12_g5_high>.8h, V<t12_g5_x>.8h, v28.8h
    mls V<t12_g5_low>.8h, V<t12_g5_lq>.8h, v30.8h
    mls V<t12_g5_high>.8h, V<t12_g5_hq>.8h, v30.8h
    ext V<t12_g5_lr>.16b, V<t12_g5_low>.16b, V<t12_g5_low>.16b, #8
    ext V<t12_g5_hr>.16b, V<t12_g5_high>.16b, V<t12_g5_high>.16b, #8
    add V<t12_g5_low>.8h, V<t12_g5_low>.8h, V<t12_g5_lr>.8h
    add V<t12_g5_high>.8h, V<t12_g5_high>.8h, V<t12_g5_hr>.8h
    sqrdmulh V<t12_g5_rl>.8h, V<t12_g5_low>.8h, v31.8h
    mls V<t12_g5_low>.8h, V<t12_g5_rl>.8h, v30.8h
    umov w9, V<t12_g5_high>.h[0]
    strh w9, [x0, #1540]
    umov w9, V<t12_g5_high>.h[1]
    strh w9, [x0, #1546]
    umov w9, V<t12_g5_high>.h[2]
    strh w9, [x0, #1552]
    umov w9, V<t12_g5_high>.h[3]
    strh w9, [x0, #1558]
    umov w9, V<t12_g5_low>.h[0]
    strh w9, [x0, #676]
    umov w9, V<t12_g5_low>.h[1]
    strh w9, [x0, #682]
    umov w9, V<t12_g5_low>.h[2]
    strh w9, [x0, #688]
    umov w9, V<t12_g5_low>.h[3]
    strh w9, [x0, #694]
    p32_terminal_12_g5_end:
p32_terminal_12_end:
p32_terminal_13_start:
    ldr q26, [x4, #832]
    ldr q27, [x4, #848]
    ldr q28, [x4, #864]
    ldr q29, [x4, #880]
    p32_terminal_13_g0_start:
    ldr Q<t13_g0_x>, [x1, #208]
    sqrdmulh V<t13_g0_lq>.8h, V<t13_g0_x>.8h, v27.8h
    sqrdmulh V<t13_g0_hq>.8h, V<t13_g0_x>.8h, v29.8h
    mul V<t13_g0_low>.8h, V<t13_g0_x>.8h, v26.8h
    mul V<t13_g0_high>.8h, V<t13_g0_x>.8h, v28.8h
    mls V<t13_g0_low>.8h, V<t13_g0_lq>.8h, v30.8h
    mls V<t13_g0_high>.8h, V<t13_g0_hq>.8h, v30.8h
    ext V<t13_g0_lr>.16b, V<t13_g0_low>.16b, V<t13_g0_low>.16b, #8
    ext V<t13_g0_hr>.16b, V<t13_g0_high>.16b, V<t13_g0_high>.16b, #8
    add V<t13_g0_low>.8h, V<t13_g0_low>.8h, V<t13_g0_lr>.8h
    add V<t13_g0_high>.8h, V<t13_g0_high>.8h, V<t13_g0_hr>.8h
    umov w9, V<t13_g0_high>.h[0]
    strh w9, [x0, #1566]
    umov w9, V<t13_g0_high>.h[1]
    strh w9, [x0, #1572]
    umov w9, V<t13_g0_high>.h[2]
    strh w9, [x0, #1578]
    umov w9, V<t13_g0_high>.h[3]
    strh w9, [x0, #1584]
    umov w9, V<t13_g0_low>.h[0]
    strh w9, [x0, #702]
    umov w9, V<t13_g0_low>.h[1]
    strh w9, [x0, #708]
    umov w9, V<t13_g0_low>.h[2]
    strh w9, [x0, #714]
    umov w9, V<t13_g0_low>.h[3]
    strh w9, [x0, #720]
    p32_terminal_13_g0_end:
    p32_terminal_13_g1_start:
    ldr Q<t13_g1_x>, [x1, #464]
    sqrdmulh V<t13_g1_lq>.8h, V<t13_g1_x>.8h, v27.8h
    sqrdmulh V<t13_g1_hq>.8h, V<t13_g1_x>.8h, v29.8h
    mul V<t13_g1_low>.8h, V<t13_g1_x>.8h, v26.8h
    mul V<t13_g1_high>.8h, V<t13_g1_x>.8h, v28.8h
    mls V<t13_g1_low>.8h, V<t13_g1_lq>.8h, v30.8h
    mls V<t13_g1_high>.8h, V<t13_g1_hq>.8h, v30.8h
    ext V<t13_g1_lr>.16b, V<t13_g1_low>.16b, V<t13_g1_low>.16b, #8
    ext V<t13_g1_hr>.16b, V<t13_g1_high>.16b, V<t13_g1_high>.16b, #8
    add V<t13_g1_low>.8h, V<t13_g1_low>.8h, V<t13_g1_lr>.8h
    add V<t13_g1_high>.8h, V<t13_g1_high>.8h, V<t13_g1_hr>.8h
    umov w9, V<t13_g1_high>.h[0]
    strh w9, [x0, #1590]
    umov w9, V<t13_g1_high>.h[1]
    strh w9, [x0, #1596]
    umov w9, V<t13_g1_high>.h[2]
    strh w9, [x0, #1602]
    umov w9, V<t13_g1_high>.h[3]
    strh w9, [x0, #1608]
    umov w9, V<t13_g1_low>.h[0]
    strh w9, [x0, #726]
    umov w9, V<t13_g1_low>.h[1]
    strh w9, [x0, #732]
    umov w9, V<t13_g1_low>.h[2]
    strh w9, [x0, #738]
    umov w9, V<t13_g1_low>.h[3]
    strh w9, [x0, #744]
    p32_terminal_13_g1_end:
    p32_terminal_13_g2_start:
    ldr Q<t13_g2_x>, [x1, #720]
    sqrdmulh V<t13_g2_lq>.8h, V<t13_g2_x>.8h, v27.8h
    sqrdmulh V<t13_g2_hq>.8h, V<t13_g2_x>.8h, v29.8h
    mul V<t13_g2_low>.8h, V<t13_g2_x>.8h, v26.8h
    mul V<t13_g2_high>.8h, V<t13_g2_x>.8h, v28.8h
    mls V<t13_g2_low>.8h, V<t13_g2_lq>.8h, v30.8h
    mls V<t13_g2_high>.8h, V<t13_g2_hq>.8h, v30.8h
    ext V<t13_g2_lr>.16b, V<t13_g2_low>.16b, V<t13_g2_low>.16b, #8
    ext V<t13_g2_hr>.16b, V<t13_g2_high>.16b, V<t13_g2_high>.16b, #8
    add V<t13_g2_low>.8h, V<t13_g2_low>.8h, V<t13_g2_lr>.8h
    add V<t13_g2_high>.8h, V<t13_g2_high>.8h, V<t13_g2_hr>.8h
    umov w9, V<t13_g2_high>.h[0]
    strh w9, [x0, #1568]
    umov w9, V<t13_g2_high>.h[1]
    strh w9, [x0, #1574]
    umov w9, V<t13_g2_high>.h[2]
    strh w9, [x0, #1580]
    umov w9, V<t13_g2_high>.h[3]
    strh w9, [x0, #1586]
    umov w9, V<t13_g2_low>.h[0]
    strh w9, [x0, #704]
    umov w9, V<t13_g2_low>.h[1]
    strh w9, [x0, #710]
    umov w9, V<t13_g2_low>.h[2]
    strh w9, [x0, #716]
    umov w9, V<t13_g2_low>.h[3]
    strh w9, [x0, #722]
    p32_terminal_13_g2_end:
    p32_terminal_13_g3_start:
    ldr Q<t13_g3_x>, [x1, #976]
    sqrdmulh V<t13_g3_lq>.8h, V<t13_g3_x>.8h, v27.8h
    sqrdmulh V<t13_g3_hq>.8h, V<t13_g3_x>.8h, v29.8h
    mul V<t13_g3_low>.8h, V<t13_g3_x>.8h, v26.8h
    mul V<t13_g3_high>.8h, V<t13_g3_x>.8h, v28.8h
    mls V<t13_g3_low>.8h, V<t13_g3_lq>.8h, v30.8h
    mls V<t13_g3_high>.8h, V<t13_g3_hq>.8h, v30.8h
    ext V<t13_g3_lr>.16b, V<t13_g3_low>.16b, V<t13_g3_low>.16b, #8
    ext V<t13_g3_hr>.16b, V<t13_g3_high>.16b, V<t13_g3_high>.16b, #8
    add V<t13_g3_low>.8h, V<t13_g3_low>.8h, V<t13_g3_lr>.8h
    add V<t13_g3_high>.8h, V<t13_g3_high>.8h, V<t13_g3_hr>.8h
    umov w9, V<t13_g3_high>.h[0]
    strh w9, [x0, #1592]
    umov w9, V<t13_g3_high>.h[1]
    strh w9, [x0, #1598]
    umov w9, V<t13_g3_high>.h[2]
    strh w9, [x0, #1604]
    umov w9, V<t13_g3_high>.h[3]
    strh w9, [x0, #1610]
    umov w9, V<t13_g3_low>.h[0]
    strh w9, [x0, #728]
    umov w9, V<t13_g3_low>.h[1]
    strh w9, [x0, #734]
    umov w9, V<t13_g3_low>.h[2]
    strh w9, [x0, #740]
    umov w9, V<t13_g3_low>.h[3]
    strh w9, [x0, #746]
    p32_terminal_13_g3_end:
    p32_terminal_13_g4_start:
    ldr Q<t13_g4_x>, [x1, #1232]
    sqrdmulh V<t13_g4_lq>.8h, V<t13_g4_x>.8h, v27.8h
    sqrdmulh V<t13_g4_hq>.8h, V<t13_g4_x>.8h, v29.8h
    mul V<t13_g4_low>.8h, V<t13_g4_x>.8h, v26.8h
    mul V<t13_g4_high>.8h, V<t13_g4_x>.8h, v28.8h
    mls V<t13_g4_low>.8h, V<t13_g4_lq>.8h, v30.8h
    mls V<t13_g4_high>.8h, V<t13_g4_hq>.8h, v30.8h
    ext V<t13_g4_lr>.16b, V<t13_g4_low>.16b, V<t13_g4_low>.16b, #8
    ext V<t13_g4_hr>.16b, V<t13_g4_high>.16b, V<t13_g4_high>.16b, #8
    add V<t13_g4_low>.8h, V<t13_g4_low>.8h, V<t13_g4_lr>.8h
    add V<t13_g4_high>.8h, V<t13_g4_high>.8h, V<t13_g4_hr>.8h
    umov w9, V<t13_g4_high>.h[0]
    strh w9, [x0, #1570]
    umov w9, V<t13_g4_high>.h[1]
    strh w9, [x0, #1576]
    umov w9, V<t13_g4_high>.h[2]
    strh w9, [x0, #1582]
    umov w9, V<t13_g4_high>.h[3]
    strh w9, [x0, #1588]
    umov w9, V<t13_g4_low>.h[0]
    strh w9, [x0, #706]
    umov w9, V<t13_g4_low>.h[1]
    strh w9, [x0, #712]
    umov w9, V<t13_g4_low>.h[2]
    strh w9, [x0, #718]
    umov w9, V<t13_g4_low>.h[3]
    strh w9, [x0, #724]
    p32_terminal_13_g4_end:
    p32_terminal_13_g5_start:
    ldr Q<t13_g5_x>, [x1, #1488]
    sqrdmulh V<t13_g5_lq>.8h, V<t13_g5_x>.8h, v27.8h
    sqrdmulh V<t13_g5_hq>.8h, V<t13_g5_x>.8h, v29.8h
    mul V<t13_g5_low>.8h, V<t13_g5_x>.8h, v26.8h
    mul V<t13_g5_high>.8h, V<t13_g5_x>.8h, v28.8h
    mls V<t13_g5_low>.8h, V<t13_g5_lq>.8h, v30.8h
    mls V<t13_g5_high>.8h, V<t13_g5_hq>.8h, v30.8h
    ext V<t13_g5_lr>.16b, V<t13_g5_low>.16b, V<t13_g5_low>.16b, #8
    ext V<t13_g5_hr>.16b, V<t13_g5_high>.16b, V<t13_g5_high>.16b, #8
    add V<t13_g5_low>.8h, V<t13_g5_low>.8h, V<t13_g5_lr>.8h
    add V<t13_g5_high>.8h, V<t13_g5_high>.8h, V<t13_g5_hr>.8h
    umov w9, V<t13_g5_high>.h[0]
    strh w9, [x0, #1594]
    umov w9, V<t13_g5_high>.h[1]
    strh w9, [x0, #1600]
    umov w9, V<t13_g5_high>.h[2]
    strh w9, [x0, #1606]
    umov w9, V<t13_g5_high>.h[3]
    strh w9, [x0, #1612]
    umov w9, V<t13_g5_low>.h[0]
    strh w9, [x0, #730]
    umov w9, V<t13_g5_low>.h[1]
    strh w9, [x0, #736]
    umov w9, V<t13_g5_low>.h[2]
    strh w9, [x0, #742]
    umov w9, V<t13_g5_low>.h[3]
    strh w9, [x0, #748]
    p32_terminal_13_g5_end:
p32_terminal_13_end:
p32_terminal_14_start:
    ldr q26, [x4, #896]
    ldr q27, [x4, #912]
    ldr q28, [x4, #928]
    ldr q29, [x4, #944]
    p32_terminal_14_g0_start:
    ldr Q<t14_g0_x>, [x1, #224]
    sqrdmulh V<t14_g0_lq>.8h, V<t14_g0_x>.8h, v27.8h
    sqrdmulh V<t14_g0_hq>.8h, V<t14_g0_x>.8h, v29.8h
    mul V<t14_g0_low>.8h, V<t14_g0_x>.8h, v26.8h
    mul V<t14_g0_high>.8h, V<t14_g0_x>.8h, v28.8h
    mls V<t14_g0_low>.8h, V<t14_g0_lq>.8h, v30.8h
    mls V<t14_g0_high>.8h, V<t14_g0_hq>.8h, v30.8h
    ext V<t14_g0_lr>.16b, V<t14_g0_low>.16b, V<t14_g0_low>.16b, #8
    ext V<t14_g0_hr>.16b, V<t14_g0_high>.16b, V<t14_g0_high>.16b, #8
    add V<t14_g0_low>.8h, V<t14_g0_low>.8h, V<t14_g0_lr>.8h
    add V<t14_g0_high>.8h, V<t14_g0_high>.8h, V<t14_g0_hr>.8h
    umov w9, V<t14_g0_high>.h[0]
    strh w9, [x0, #1620]
    umov w9, V<t14_g0_high>.h[1]
    strh w9, [x0, #1626]
    umov w9, V<t14_g0_high>.h[2]
    strh w9, [x0, #1632]
    umov w9, V<t14_g0_high>.h[3]
    strh w9, [x0, #1638]
    umov w9, V<t14_g0_low>.h[0]
    strh w9, [x0, #756]
    umov w9, V<t14_g0_low>.h[1]
    strh w9, [x0, #762]
    umov w9, V<t14_g0_low>.h[2]
    strh w9, [x0, #768]
    umov w9, V<t14_g0_low>.h[3]
    strh w9, [x0, #774]
    p32_terminal_14_g0_end:
    p32_terminal_14_g1_start:
    ldr Q<t14_g1_x>, [x1, #480]
    sqrdmulh V<t14_g1_lq>.8h, V<t14_g1_x>.8h, v27.8h
    sqrdmulh V<t14_g1_hq>.8h, V<t14_g1_x>.8h, v29.8h
    mul V<t14_g1_low>.8h, V<t14_g1_x>.8h, v26.8h
    mul V<t14_g1_high>.8h, V<t14_g1_x>.8h, v28.8h
    mls V<t14_g1_low>.8h, V<t14_g1_lq>.8h, v30.8h
    mls V<t14_g1_high>.8h, V<t14_g1_hq>.8h, v30.8h
    ext V<t14_g1_lr>.16b, V<t14_g1_low>.16b, V<t14_g1_low>.16b, #8
    ext V<t14_g1_hr>.16b, V<t14_g1_high>.16b, V<t14_g1_high>.16b, #8
    add V<t14_g1_low>.8h, V<t14_g1_low>.8h, V<t14_g1_lr>.8h
    add V<t14_g1_high>.8h, V<t14_g1_high>.8h, V<t14_g1_hr>.8h
    umov w9, V<t14_g1_high>.h[0]
    strh w9, [x0, #1644]
    umov w9, V<t14_g1_high>.h[1]
    strh w9, [x0, #1650]
    umov w9, V<t14_g1_high>.h[2]
    strh w9, [x0, #1656]
    umov w9, V<t14_g1_high>.h[3]
    strh w9, [x0, #1662]
    umov w9, V<t14_g1_low>.h[0]
    strh w9, [x0, #780]
    umov w9, V<t14_g1_low>.h[1]
    strh w9, [x0, #786]
    umov w9, V<t14_g1_low>.h[2]
    strh w9, [x0, #792]
    umov w9, V<t14_g1_low>.h[3]
    strh w9, [x0, #798]
    p32_terminal_14_g1_end:
    p32_terminal_14_g2_start:
    ldr Q<t14_g2_x>, [x1, #736]
    sqrdmulh V<t14_g2_lq>.8h, V<t14_g2_x>.8h, v27.8h
    sqrdmulh V<t14_g2_hq>.8h, V<t14_g2_x>.8h, v29.8h
    mul V<t14_g2_low>.8h, V<t14_g2_x>.8h, v26.8h
    mul V<t14_g2_high>.8h, V<t14_g2_x>.8h, v28.8h
    mls V<t14_g2_low>.8h, V<t14_g2_lq>.8h, v30.8h
    mls V<t14_g2_high>.8h, V<t14_g2_hq>.8h, v30.8h
    ext V<t14_g2_lr>.16b, V<t14_g2_low>.16b, V<t14_g2_low>.16b, #8
    ext V<t14_g2_hr>.16b, V<t14_g2_high>.16b, V<t14_g2_high>.16b, #8
    add V<t14_g2_low>.8h, V<t14_g2_low>.8h, V<t14_g2_lr>.8h
    add V<t14_g2_high>.8h, V<t14_g2_high>.8h, V<t14_g2_hr>.8h
    umov w9, V<t14_g2_high>.h[0]
    strh w9, [x0, #1622]
    umov w9, V<t14_g2_high>.h[1]
    strh w9, [x0, #1628]
    umov w9, V<t14_g2_high>.h[2]
    strh w9, [x0, #1634]
    umov w9, V<t14_g2_high>.h[3]
    strh w9, [x0, #1640]
    umov w9, V<t14_g2_low>.h[0]
    strh w9, [x0, #758]
    umov w9, V<t14_g2_low>.h[1]
    strh w9, [x0, #764]
    umov w9, V<t14_g2_low>.h[2]
    strh w9, [x0, #770]
    umov w9, V<t14_g2_low>.h[3]
    strh w9, [x0, #776]
    p32_terminal_14_g2_end:
    p32_terminal_14_g3_start:
    ldr Q<t14_g3_x>, [x1, #992]
    sqrdmulh V<t14_g3_lq>.8h, V<t14_g3_x>.8h, v27.8h
    sqrdmulh V<t14_g3_hq>.8h, V<t14_g3_x>.8h, v29.8h
    mul V<t14_g3_low>.8h, V<t14_g3_x>.8h, v26.8h
    mul V<t14_g3_high>.8h, V<t14_g3_x>.8h, v28.8h
    mls V<t14_g3_low>.8h, V<t14_g3_lq>.8h, v30.8h
    mls V<t14_g3_high>.8h, V<t14_g3_hq>.8h, v30.8h
    ext V<t14_g3_lr>.16b, V<t14_g3_low>.16b, V<t14_g3_low>.16b, #8
    ext V<t14_g3_hr>.16b, V<t14_g3_high>.16b, V<t14_g3_high>.16b, #8
    add V<t14_g3_low>.8h, V<t14_g3_low>.8h, V<t14_g3_lr>.8h
    add V<t14_g3_high>.8h, V<t14_g3_high>.8h, V<t14_g3_hr>.8h
    umov w9, V<t14_g3_high>.h[0]
    strh w9, [x0, #1646]
    umov w9, V<t14_g3_high>.h[1]
    strh w9, [x0, #1652]
    umov w9, V<t14_g3_high>.h[2]
    strh w9, [x0, #1658]
    umov w9, V<t14_g3_high>.h[3]
    strh w9, [x0, #1664]
    umov w9, V<t14_g3_low>.h[0]
    strh w9, [x0, #782]
    umov w9, V<t14_g3_low>.h[1]
    strh w9, [x0, #788]
    umov w9, V<t14_g3_low>.h[2]
    strh w9, [x0, #794]
    umov w9, V<t14_g3_low>.h[3]
    strh w9, [x0, #800]
    p32_terminal_14_g3_end:
    p32_terminal_14_g4_start:
    ldr Q<t14_g4_x>, [x1, #1248]
    sqrdmulh V<t14_g4_lq>.8h, V<t14_g4_x>.8h, v27.8h
    sqrdmulh V<t14_g4_hq>.8h, V<t14_g4_x>.8h, v29.8h
    mul V<t14_g4_low>.8h, V<t14_g4_x>.8h, v26.8h
    mul V<t14_g4_high>.8h, V<t14_g4_x>.8h, v28.8h
    mls V<t14_g4_low>.8h, V<t14_g4_lq>.8h, v30.8h
    mls V<t14_g4_high>.8h, V<t14_g4_hq>.8h, v30.8h
    ext V<t14_g4_lr>.16b, V<t14_g4_low>.16b, V<t14_g4_low>.16b, #8
    ext V<t14_g4_hr>.16b, V<t14_g4_high>.16b, V<t14_g4_high>.16b, #8
    add V<t14_g4_low>.8h, V<t14_g4_low>.8h, V<t14_g4_lr>.8h
    add V<t14_g4_high>.8h, V<t14_g4_high>.8h, V<t14_g4_hr>.8h
    umov w9, V<t14_g4_high>.h[0]
    strh w9, [x0, #1624]
    umov w9, V<t14_g4_high>.h[1]
    strh w9, [x0, #1630]
    umov w9, V<t14_g4_high>.h[2]
    strh w9, [x0, #1636]
    umov w9, V<t14_g4_high>.h[3]
    strh w9, [x0, #1642]
    umov w9, V<t14_g4_low>.h[0]
    strh w9, [x0, #760]
    umov w9, V<t14_g4_low>.h[1]
    strh w9, [x0, #766]
    umov w9, V<t14_g4_low>.h[2]
    strh w9, [x0, #772]
    umov w9, V<t14_g4_low>.h[3]
    strh w9, [x0, #778]
    p32_terminal_14_g4_end:
    p32_terminal_14_g5_start:
    ldr Q<t14_g5_x>, [x1, #1504]
    sqrdmulh V<t14_g5_lq>.8h, V<t14_g5_x>.8h, v27.8h
    sqrdmulh V<t14_g5_hq>.8h, V<t14_g5_x>.8h, v29.8h
    mul V<t14_g5_low>.8h, V<t14_g5_x>.8h, v26.8h
    mul V<t14_g5_high>.8h, V<t14_g5_x>.8h, v28.8h
    mls V<t14_g5_low>.8h, V<t14_g5_lq>.8h, v30.8h
    mls V<t14_g5_high>.8h, V<t14_g5_hq>.8h, v30.8h
    ext V<t14_g5_lr>.16b, V<t14_g5_low>.16b, V<t14_g5_low>.16b, #8
    ext V<t14_g5_hr>.16b, V<t14_g5_high>.16b, V<t14_g5_high>.16b, #8
    add V<t14_g5_low>.8h, V<t14_g5_low>.8h, V<t14_g5_lr>.8h
    add V<t14_g5_high>.8h, V<t14_g5_high>.8h, V<t14_g5_hr>.8h
    umov w9, V<t14_g5_high>.h[0]
    strh w9, [x0, #1648]
    umov w9, V<t14_g5_high>.h[1]
    strh w9, [x0, #1654]
    umov w9, V<t14_g5_high>.h[2]
    strh w9, [x0, #1660]
    umov w9, V<t14_g5_high>.h[3]
    strh w9, [x0, #1666]
    umov w9, V<t14_g5_low>.h[0]
    strh w9, [x0, #784]
    umov w9, V<t14_g5_low>.h[1]
    strh w9, [x0, #790]
    umov w9, V<t14_g5_low>.h[2]
    strh w9, [x0, #796]
    umov w9, V<t14_g5_low>.h[3]
    strh w9, [x0, #802]
    p32_terminal_14_g5_end:
p32_terminal_14_end:
p32_terminal_15_start:
    ldr q26, [x4, #960]
    ldr q27, [x4, #976]
    ldr q28, [x4, #992]
    ldr q29, [x4, #1008]
    p32_terminal_15_g0_start:
    ldr Q<t15_g0_x>, [x1, #240]
    sqrdmulh V<t15_g0_lq>.8h, V<t15_g0_x>.8h, v27.8h
    sqrdmulh V<t15_g0_hq>.8h, V<t15_g0_x>.8h, v29.8h
    mul V<t15_g0_low>.8h, V<t15_g0_x>.8h, v26.8h
    mul V<t15_g0_high>.8h, V<t15_g0_x>.8h, v28.8h
    mls V<t15_g0_low>.8h, V<t15_g0_lq>.8h, v30.8h
    mls V<t15_g0_high>.8h, V<t15_g0_hq>.8h, v30.8h
    ext V<t15_g0_lr>.16b, V<t15_g0_low>.16b, V<t15_g0_low>.16b, #8
    ext V<t15_g0_hr>.16b, V<t15_g0_high>.16b, V<t15_g0_high>.16b, #8
    add V<t15_g0_low>.8h, V<t15_g0_low>.8h, V<t15_g0_lr>.8h
    add V<t15_g0_high>.8h, V<t15_g0_high>.8h, V<t15_g0_hr>.8h
    umov w9, V<t15_g0_high>.h[0]
    strh w9, [x0, #1674]
    umov w9, V<t15_g0_high>.h[1]
    strh w9, [x0, #1680]
    umov w9, V<t15_g0_high>.h[2]
    strh w9, [x0, #1686]
    umov w9, V<t15_g0_high>.h[3]
    strh w9, [x0, #1692]
    umov w9, V<t15_g0_low>.h[0]
    strh w9, [x0, #810]
    umov w9, V<t15_g0_low>.h[1]
    strh w9, [x0, #816]
    umov w9, V<t15_g0_low>.h[2]
    strh w9, [x0, #822]
    umov w9, V<t15_g0_low>.h[3]
    strh w9, [x0, #828]
    p32_terminal_15_g0_end:
    p32_terminal_15_g1_start:
    ldr Q<t15_g1_x>, [x1, #496]
    sqrdmulh V<t15_g1_lq>.8h, V<t15_g1_x>.8h, v27.8h
    sqrdmulh V<t15_g1_hq>.8h, V<t15_g1_x>.8h, v29.8h
    mul V<t15_g1_low>.8h, V<t15_g1_x>.8h, v26.8h
    mul V<t15_g1_high>.8h, V<t15_g1_x>.8h, v28.8h
    mls V<t15_g1_low>.8h, V<t15_g1_lq>.8h, v30.8h
    mls V<t15_g1_high>.8h, V<t15_g1_hq>.8h, v30.8h
    ext V<t15_g1_lr>.16b, V<t15_g1_low>.16b, V<t15_g1_low>.16b, #8
    ext V<t15_g1_hr>.16b, V<t15_g1_high>.16b, V<t15_g1_high>.16b, #8
    add V<t15_g1_low>.8h, V<t15_g1_low>.8h, V<t15_g1_lr>.8h
    add V<t15_g1_high>.8h, V<t15_g1_high>.8h, V<t15_g1_hr>.8h
    umov w9, V<t15_g1_high>.h[0]
    strh w9, [x0, #1698]
    umov w9, V<t15_g1_high>.h[1]
    strh w9, [x0, #1704]
    umov w9, V<t15_g1_high>.h[2]
    strh w9, [x0, #1710]
    umov w9, V<t15_g1_high>.h[3]
    strh w9, [x0, #1716]
    umov w9, V<t15_g1_low>.h[0]
    strh w9, [x0, #834]
    umov w9, V<t15_g1_low>.h[1]
    strh w9, [x0, #840]
    umov w9, V<t15_g1_low>.h[2]
    strh w9, [x0, #846]
    umov w9, V<t15_g1_low>.h[3]
    strh w9, [x0, #852]
    p32_terminal_15_g1_end:
    p32_terminal_15_g2_start:
    ldr Q<t15_g2_x>, [x1, #752]
    sqrdmulh V<t15_g2_lq>.8h, V<t15_g2_x>.8h, v27.8h
    sqrdmulh V<t15_g2_hq>.8h, V<t15_g2_x>.8h, v29.8h
    mul V<t15_g2_low>.8h, V<t15_g2_x>.8h, v26.8h
    mul V<t15_g2_high>.8h, V<t15_g2_x>.8h, v28.8h
    mls V<t15_g2_low>.8h, V<t15_g2_lq>.8h, v30.8h
    mls V<t15_g2_high>.8h, V<t15_g2_hq>.8h, v30.8h
    ext V<t15_g2_lr>.16b, V<t15_g2_low>.16b, V<t15_g2_low>.16b, #8
    ext V<t15_g2_hr>.16b, V<t15_g2_high>.16b, V<t15_g2_high>.16b, #8
    add V<t15_g2_low>.8h, V<t15_g2_low>.8h, V<t15_g2_lr>.8h
    add V<t15_g2_high>.8h, V<t15_g2_high>.8h, V<t15_g2_hr>.8h
    umov w9, V<t15_g2_high>.h[0]
    strh w9, [x0, #1676]
    umov w9, V<t15_g2_high>.h[1]
    strh w9, [x0, #1682]
    umov w9, V<t15_g2_high>.h[2]
    strh w9, [x0, #1688]
    umov w9, V<t15_g2_high>.h[3]
    strh w9, [x0, #1694]
    umov w9, V<t15_g2_low>.h[0]
    strh w9, [x0, #812]
    umov w9, V<t15_g2_low>.h[1]
    strh w9, [x0, #818]
    umov w9, V<t15_g2_low>.h[2]
    strh w9, [x0, #824]
    umov w9, V<t15_g2_low>.h[3]
    strh w9, [x0, #830]
    p32_terminal_15_g2_end:
    p32_terminal_15_g3_start:
    ldr Q<t15_g3_x>, [x1, #1008]
    sqrdmulh V<t15_g3_lq>.8h, V<t15_g3_x>.8h, v27.8h
    sqrdmulh V<t15_g3_hq>.8h, V<t15_g3_x>.8h, v29.8h
    mul V<t15_g3_low>.8h, V<t15_g3_x>.8h, v26.8h
    mul V<t15_g3_high>.8h, V<t15_g3_x>.8h, v28.8h
    mls V<t15_g3_low>.8h, V<t15_g3_lq>.8h, v30.8h
    mls V<t15_g3_high>.8h, V<t15_g3_hq>.8h, v30.8h
    ext V<t15_g3_lr>.16b, V<t15_g3_low>.16b, V<t15_g3_low>.16b, #8
    ext V<t15_g3_hr>.16b, V<t15_g3_high>.16b, V<t15_g3_high>.16b, #8
    add V<t15_g3_low>.8h, V<t15_g3_low>.8h, V<t15_g3_lr>.8h
    add V<t15_g3_high>.8h, V<t15_g3_high>.8h, V<t15_g3_hr>.8h
    umov w9, V<t15_g3_high>.h[0]
    strh w9, [x0, #1700]
    umov w9, V<t15_g3_high>.h[1]
    strh w9, [x0, #1706]
    umov w9, V<t15_g3_high>.h[2]
    strh w9, [x0, #1712]
    umov w9, V<t15_g3_high>.h[3]
    strh w9, [x0, #1718]
    umov w9, V<t15_g3_low>.h[0]
    strh w9, [x0, #836]
    umov w9, V<t15_g3_low>.h[1]
    strh w9, [x0, #842]
    umov w9, V<t15_g3_low>.h[2]
    strh w9, [x0, #848]
    umov w9, V<t15_g3_low>.h[3]
    strh w9, [x0, #854]
    p32_terminal_15_g3_end:
    p32_terminal_15_g4_start:
    ldr Q<t15_g4_x>, [x1, #1264]
    sqrdmulh V<t15_g4_lq>.8h, V<t15_g4_x>.8h, v27.8h
    sqrdmulh V<t15_g4_hq>.8h, V<t15_g4_x>.8h, v29.8h
    mul V<t15_g4_low>.8h, V<t15_g4_x>.8h, v26.8h
    mul V<t15_g4_high>.8h, V<t15_g4_x>.8h, v28.8h
    mls V<t15_g4_low>.8h, V<t15_g4_lq>.8h, v30.8h
    mls V<t15_g4_high>.8h, V<t15_g4_hq>.8h, v30.8h
    ext V<t15_g4_lr>.16b, V<t15_g4_low>.16b, V<t15_g4_low>.16b, #8
    ext V<t15_g4_hr>.16b, V<t15_g4_high>.16b, V<t15_g4_high>.16b, #8
    add V<t15_g4_low>.8h, V<t15_g4_low>.8h, V<t15_g4_lr>.8h
    add V<t15_g4_high>.8h, V<t15_g4_high>.8h, V<t15_g4_hr>.8h
    umov w9, V<t15_g4_high>.h[0]
    strh w9, [x0, #1678]
    umov w9, V<t15_g4_high>.h[1]
    strh w9, [x0, #1684]
    umov w9, V<t15_g4_high>.h[2]
    strh w9, [x0, #1690]
    umov w9, V<t15_g4_high>.h[3]
    strh w9, [x0, #1696]
    umov w9, V<t15_g4_low>.h[0]
    strh w9, [x0, #814]
    umov w9, V<t15_g4_low>.h[1]
    strh w9, [x0, #820]
    umov w9, V<t15_g4_low>.h[2]
    strh w9, [x0, #826]
    umov w9, V<t15_g4_low>.h[3]
    strh w9, [x0, #832]
    p32_terminal_15_g4_end:
    p32_terminal_15_g5_start:
    ldr Q<t15_g5_x>, [x1, #1520]
    sqrdmulh V<t15_g5_lq>.8h, V<t15_g5_x>.8h, v27.8h
    sqrdmulh V<t15_g5_hq>.8h, V<t15_g5_x>.8h, v29.8h
    mul V<t15_g5_low>.8h, V<t15_g5_x>.8h, v26.8h
    mul V<t15_g5_high>.8h, V<t15_g5_x>.8h, v28.8h
    mls V<t15_g5_low>.8h, V<t15_g5_lq>.8h, v30.8h
    mls V<t15_g5_high>.8h, V<t15_g5_hq>.8h, v30.8h
    ext V<t15_g5_lr>.16b, V<t15_g5_low>.16b, V<t15_g5_low>.16b, #8
    ext V<t15_g5_hr>.16b, V<t15_g5_high>.16b, V<t15_g5_high>.16b, #8
    add V<t15_g5_low>.8h, V<t15_g5_low>.8h, V<t15_g5_lr>.8h
    add V<t15_g5_high>.8h, V<t15_g5_high>.8h, V<t15_g5_hr>.8h
    umov w9, V<t15_g5_high>.h[0]
    strh w9, [x0, #1702]
    umov w9, V<t15_g5_high>.h[1]
    strh w9, [x0, #1708]
    umov w9, V<t15_g5_high>.h[2]
    strh w9, [x0, #1714]
    umov w9, V<t15_g5_high>.h[3]
    strh w9, [x0, #1720]
    umov w9, V<t15_g5_low>.h[0]
    strh w9, [x0, #838]
    umov w9, V<t15_g5_low>.h[1]
    strh w9, [x0, #844]
    umov w9, V<t15_g5_low>.h[2]
    strh w9, [x0, #850]
    umov w9, V<t15_g5_low>.h[3]
    strh w9, [x0, #856]
    p32_terminal_15_g5_end:
p32_terminal_15_end:
p32_i16_terminal6_slothy_end:
    ret

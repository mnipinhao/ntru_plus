#ifdef __APPLE__
#define p28_route_ternary _p28_route_ternary
#endif
.text
.p2align 4
.global p28_route_ternary
p28_route_ternary:
// live-in: x0 distinct natural output, x1 dense scratch, x2 public masks
// live-out: 864 natural-order ternary coefficients at x0
// coefficient range: raw abs<=4577, adjusted abs<=4576, ternary abs<=1
// fixed physical registers: v0-v3 resident source bank; v4-v7 constants
p28_route_slothy_start:
    mov w3, #1728
    dup v4.8h, w3
    mov w3, #-1728
    dup v5.8h, w3
    mov w3, #10923
    dup v6.8h, w3
    movi v7.8h, #3
p28s_route_window_0_start:
    ldr q0, [x1, #0]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #256]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #0]
p28s_route_window_0_end:
p28s_route_window_1_start:
    ldr q2, [x1, #768]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #16]
p28s_route_window_1_end:
p28s_route_window_2_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #32]
p28s_route_window_2_end:
p28s_route_window_3_start:
    ldr q0, [x1, #1536]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #16]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #272]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #48]
p28s_route_window_3_end:
p28s_route_window_4_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #64]
p28s_route_window_4_end:
p28s_route_window_5_start:
    ldr q1, [x1, #784]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #80]
p28s_route_window_5_end:
p28s_route_window_6_start:
    ldr q3, [x1, #32]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #96]
p28s_route_window_6_end:
p28s_route_window_7_start:
    ldr q1, [x1, #288]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #112]
p28s_route_window_7_end:
p28s_route_window_8_start:
    ldr q2, [x1, #800]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #128]
p28s_route_window_8_end:
p28s_route_window_9_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #144]
p28s_route_window_9_end:
p28s_route_window_10_start:
    ldr q0, [x1, #1552]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #48]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #304]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #160]
p28s_route_window_10_end:
p28s_route_window_11_start:
    ldr q3, [x1, #816]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #176]
p28s_route_window_11_end:
p28s_route_window_12_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #192]
p28s_route_window_12_end:
p28s_route_window_13_start:
    ldr q1, [x1, #64]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #320]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #208]
p28s_route_window_13_end:
p28s_route_window_14_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #224]
p28s_route_window_14_end:
p28s_route_window_15_start:
    ldr q1, [x1, #832]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #240]
p28s_route_window_15_end:
p28s_route_window_16_start:
    ldr q3, [x1, #80]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #256]
p28s_route_window_16_end:
p28s_route_window_17_start:
    ldr q1, [x1, #336]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #272]
p28s_route_window_17_end:
p28s_route_window_18_start:
    ldr q2, [x1, #848]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #288]
p28s_route_window_18_end:
p28s_route_window_19_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #304]
p28s_route_window_19_end:
p28s_route_window_20_start:
    ldr q0, [x1, #1568]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #96]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #352]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #320]
p28s_route_window_20_end:
p28s_route_window_21_start:
    ldr q3, [x1, #864]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #336]
p28s_route_window_21_end:
p28s_route_window_22_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #352]
p28s_route_window_22_end:
p28s_route_window_23_start:
    ldr q1, [x1, #112]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #368]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #368]
p28s_route_window_23_end:
p28s_route_window_24_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #384]
p28s_route_window_24_end:
p28s_route_window_25_start:
    ldr q1, [x1, #880]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #400]
p28s_route_window_25_end:
p28s_route_window_26_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #416]
p28s_route_window_26_end:
p28s_route_window_27_start:
    ldr q0, [x1, #128]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #384]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #432]
p28s_route_window_27_end:
p28s_route_window_28_start:
    ldr q2, [x1, #896]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #448]
p28s_route_window_28_end:
p28s_route_window_29_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #464]
p28s_route_window_29_end:
p28s_route_window_30_start:
    ldr q0, [x1, #1584]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #144]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #400]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #480]
p28s_route_window_30_end:
p28s_route_window_31_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #496]
p28s_route_window_31_end:
p28s_route_window_32_start:
    ldr q1, [x1, #912]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #512]
p28s_route_window_32_end:
p28s_route_window_33_start:
    ldr q3, [x1, #160]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #528]
p28s_route_window_33_end:
p28s_route_window_34_start:
    ldr q1, [x1, #416]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #544]
p28s_route_window_34_end:
p28s_route_window_35_start:
    ldr q2, [x1, #928]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #560]
p28s_route_window_35_end:
p28s_route_window_36_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #576]
p28s_route_window_36_end:
p28s_route_window_37_start:
    ldr q0, [x1, #1600]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #176]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #432]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #592]
p28s_route_window_37_end:
p28s_route_window_38_start:
    ldr q3, [x1, #944]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #608]
p28s_route_window_38_end:
p28s_route_window_39_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #624]
p28s_route_window_39_end:
p28s_route_window_40_start:
    ldr q1, [x1, #192]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #448]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #640]
p28s_route_window_40_end:
p28s_route_window_41_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #656]
p28s_route_window_41_end:
p28s_route_window_42_start:
    ldr q1, [x1, #960]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #672]
p28s_route_window_42_end:
p28s_route_window_43_start:
    ldr q3, [x1, #208]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #688]
p28s_route_window_43_end:
p28s_route_window_44_start:
    ldr q1, [x1, #464]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #704]
p28s_route_window_44_end:
p28s_route_window_45_start:
    ldr q2, [x1, #976]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #720]
p28s_route_window_45_end:
p28s_route_window_46_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #736]
p28s_route_window_46_end:
p28s_route_window_47_start:
    ldr q0, [x1, #1616]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #224]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #480]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #752]
p28s_route_window_47_end:
p28s_route_window_48_start:
    ldr q3, [x1, #992]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #768]
p28s_route_window_48_end:
p28s_route_window_49_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #784]
p28s_route_window_49_end:
p28s_route_window_50_start:
    ldr q1, [x1, #240]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #496]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #800]
p28s_route_window_50_end:
p28s_route_window_51_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #816]
p28s_route_window_51_end:
p28s_route_window_52_start:
    ldr q1, [x1, #1008]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #832]
p28s_route_window_52_end:
p28s_route_window_53_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #848]
p28s_route_window_53_end:
p28s_route_window_54_start:
    ldr q0, [x1, #512]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #1024]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #864]
p28s_route_window_54_end:
p28s_route_window_55_start:
    ldr q2, [x1, #1280]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #880]
p28s_route_window_55_end:
p28s_route_window_56_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #896]
p28s_route_window_56_end:
p28s_route_window_57_start:
    ldr q0, [x1, #1632]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #528]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #1040]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #912]
p28s_route_window_57_end:
p28s_route_window_58_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #928]
p28s_route_window_58_end:
p28s_route_window_59_start:
    ldr q1, [x1, #1296]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #944]
p28s_route_window_59_end:
p28s_route_window_60_start:
    ldr q3, [x1, #544]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #960]
p28s_route_window_60_end:
p28s_route_window_61_start:
    ldr q1, [x1, #1056]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #976]
p28s_route_window_61_end:
p28s_route_window_62_start:
    ldr q2, [x1, #1312]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #992]
p28s_route_window_62_end:
p28s_route_window_63_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1008]
p28s_route_window_63_end:
p28s_route_window_64_start:
    ldr q0, [x1, #1648]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #560]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #1072]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1024]
p28s_route_window_64_end:
p28s_route_window_65_start:
    ldr q3, [x1, #1328]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1040]
p28s_route_window_65_end:
p28s_route_window_66_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1056]
p28s_route_window_66_end:
p28s_route_window_67_start:
    ldr q1, [x1, #576]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #1088]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1072]
p28s_route_window_67_end:
p28s_route_window_68_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1088]
p28s_route_window_68_end:
p28s_route_window_69_start:
    ldr q1, [x1, #1344]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1104]
p28s_route_window_69_end:
p28s_route_window_70_start:
    ldr q3, [x1, #592]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1120]
p28s_route_window_70_end:
p28s_route_window_71_start:
    ldr q1, [x1, #1104]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1136]
p28s_route_window_71_end:
p28s_route_window_72_start:
    ldr q2, [x1, #1360]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1152]
p28s_route_window_72_end:
p28s_route_window_73_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1168]
p28s_route_window_73_end:
p28s_route_window_74_start:
    ldr q0, [x1, #1664]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #608]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #1120]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1184]
p28s_route_window_74_end:
p28s_route_window_75_start:
    ldr q3, [x1, #1376]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1200]
p28s_route_window_75_end:
p28s_route_window_76_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1216]
p28s_route_window_76_end:
p28s_route_window_77_start:
    ldr q1, [x1, #624]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #1136]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1232]
p28s_route_window_77_end:
p28s_route_window_78_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1248]
p28s_route_window_78_end:
p28s_route_window_79_start:
    ldr q1, [x1, #1392]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1264]
p28s_route_window_79_end:
p28s_route_window_80_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1280]
p28s_route_window_80_end:
p28s_route_window_81_start:
    ldr q0, [x1, #640]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #1152]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1296]
p28s_route_window_81_end:
p28s_route_window_82_start:
    ldr q2, [x1, #1408]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1312]
p28s_route_window_82_end:
p28s_route_window_83_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1328]
p28s_route_window_83_end:
p28s_route_window_84_start:
    ldr q0, [x1, #1680]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #656]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #1168]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1344]
p28s_route_window_84_end:
p28s_route_window_85_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1360]
p28s_route_window_85_end:
p28s_route_window_86_start:
    ldr q1, [x1, #1424]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1376]
p28s_route_window_86_end:
p28s_route_window_87_start:
    ldr q3, [x1, #672]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1392]
p28s_route_window_87_end:
p28s_route_window_88_start:
    ldr q1, [x1, #1184]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1408]
p28s_route_window_88_end:
p28s_route_window_89_start:
    ldr q2, [x1, #1440]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1424]
p28s_route_window_89_end:
p28s_route_window_90_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1440]
p28s_route_window_90_end:
p28s_route_window_91_start:
    ldr q0, [x1, #1696]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #688]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #1200]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1456]
p28s_route_window_91_end:
p28s_route_window_92_start:
    ldr q3, [x1, #1456]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1472]
p28s_route_window_92_end:
p28s_route_window_93_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1488]
p28s_route_window_93_end:
p28s_route_window_94_start:
    ldr q1, [x1, #704]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #1216]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1504]
p28s_route_window_94_end:
p28s_route_window_95_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1520]
p28s_route_window_95_end:
p28s_route_window_96_start:
    ldr q1, [x1, #1472]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1536]
p28s_route_window_96_end:
p28s_route_window_97_start:
    ldr q3, [x1, #720]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1552]
p28s_route_window_97_end:
p28s_route_window_98_start:
    ldr q1, [x1, #1232]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1568]
p28s_route_window_98_end:
p28s_route_window_99_start:
    ldr q2, [x1, #1488]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1584]
p28s_route_window_99_end:
p28s_route_window_100_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1600]
p28s_route_window_100_end:
p28s_route_window_101_start:
    ldr q0, [x1, #1712]
    cmgt v8.8h, v0.8h, v4.8h
    cmgt v9.8h, v5.8h, v0.8h
    add v0.8h, v0.8h, v8.8h
    sub v0.8h, v0.8h, v9.8h
    sqrdmulh v8.8h, v0.8h, v6.8h
    mls v0.8h, v8.8h, v7.8h
    ldr q1, [x1, #736]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #1248]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1616]
p28s_route_window_101_end:
p28s_route_window_102_start:
    ldr q3, [x1, #1504]
    cmgt v8.8h, v3.8h, v4.8h
    cmgt v9.8h, v5.8h, v3.8h
    add v3.8h, v3.8h, v8.8h
    sub v3.8h, v3.8h, v9.8h
    sqrdmulh v8.8h, v3.8h, v6.8h
    mls v3.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1632]
p28s_route_window_102_end:
p28s_route_window_103_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1648]
p28s_route_window_103_end:
p28s_route_window_104_start:
    ldr q1, [x1, #752]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldr q2, [x1, #1264]
    cmgt v8.8h, v2.8h, v4.8h
    cmgt v9.8h, v5.8h, v2.8h
    add v2.8h, v2.8h, v8.8h
    sub v2.8h, v2.8h, v9.8h
    sqrdmulh v8.8h, v2.8h, v6.8h
    mls v2.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1664]
p28s_route_window_104_end:
p28s_route_window_105_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1680]
p28s_route_window_105_end:
p28s_route_window_106_start:
    ldr q1, [x1, #1520]
    cmgt v8.8h, v1.8h, v4.8h
    cmgt v9.8h, v5.8h, v1.8h
    add v1.8h, v1.8h, v8.8h
    sub v1.8h, v1.8h, v9.8h
    sqrdmulh v8.8h, v1.8h, v6.8h
    mls v1.8h, v8.8h, v7.8h
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1696]
p28s_route_window_106_end:
p28s_route_window_107_start:
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1712]
p28s_route_window_107_end:
p28_route_slothy_end:
    ret

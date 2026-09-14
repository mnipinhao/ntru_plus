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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #32]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #64]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #144]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #192]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #224]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #304]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #352]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #384]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #416]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #464]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #496]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #576]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #624]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #656]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #736]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #784]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #816]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #848]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #896]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #928]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1008]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1056]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1088]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1168]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1216]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1248]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1280]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1328]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1360]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1440]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1488]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1520]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1600]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1648]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1680]
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
    ldp q8, q9, [x2], #32
    tbl v10.16b, {v0.16b, v1.16b}, v8.16b
    tbl v11.16b, {v2.16b, v3.16b}, v9.16b
    orr v10.16b, v10.16b, v11.16b
    str q10, [x0, #1712]
p28_route_slothy_end:
    ret

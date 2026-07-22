baseline_row0_pair01_start:
    ldr d3, [x3, #0]
    ldr d12, [x4, #0]
    mov v3.d[1], v12.d[0]
    ldr d4, [x3, #24]
    ldr d12, [x4, #24]
    mov v4.d[1], v12.d[0]
    ldr d5, [x3, #48]
    ldr d12, [x4, #48]
    mov v5.d[1], v12.d[0]
    ldr d6, [x3, #72]
    ldr d12, [x4, #72]
    mov v6.d[1], v12.d[0]
    ldr d7, [x3, #96]
    ldr d12, [x4, #96]
    mov v7.d[1], v12.d[0]
    ldr d8, [x3, #120]
    ldr d12, [x4, #120]
    mov v8.d[1], v12.d[0]
    ldr d9, [x3, #144]
    ldr d12, [x4, #144]
    mov v9.d[1], v12.d[0]
    ldr d10, [x3, #168]
    ldr d12, [x4, #168]
    mov v10.d[1], v12.d[0]
    mov v12.16b, v3.16b
    add v3.8h, v3.8h, v4.8h
    sub v4.8h, v12.8h, v4.8h
    mov v12.16b, v5.16b
    add v5.8h, v5.8h, v6.8h
    sub v6.8h, v12.8h, v6.8h
    mov v12.16b, v7.16b
    add v7.8h, v7.8h, v8.8h
    sub v8.8h, v12.8h, v8.8h
    mov v12.16b, v9.16b
    add v9.8h, v9.8h, v10.8h
    sub v10.8h, v12.8h, v10.8h
    mov v12.16b, v3.16b
    add v3.8h, v3.8h, v5.8h
    sub v5.8h, v12.8h, v5.8h
    sqrdmulh v12.8h, v6.8h, v2.h[1]
    mul v11.8h, v6.8h, v1.h[1]
    mls v11.8h, v12.8h, v0.h[0]
    mov v12.16b, v4.16b
    add v4.8h, v4.8h, v11.8h
    sub v6.8h, v12.8h, v11.8h
    mov v12.16b, v7.16b
    add v7.8h, v7.8h, v9.8h
    sub v9.8h, v12.8h, v9.8h
    sqrdmulh v12.8h, v10.8h, v2.h[1]
    mul v11.8h, v10.8h, v1.h[1]
    mls v11.8h, v12.8h, v0.h[0]
    mov v12.16b, v8.16b
    add v8.8h, v8.8h, v11.8h
    sub v10.8h, v12.8h, v11.8h
    mov v12.16b, v3.16b
    add v3.8h, v3.8h, v7.8h
    sub v7.8h, v12.8h, v7.8h
    sqrdmulh v12.8h, v8.8h, v2.h[2]
    mul v11.8h, v8.8h, v1.h[2]
    mls v11.8h, v12.8h, v0.h[0]
    mov v12.16b, v4.16b
    add v4.8h, v4.8h, v11.8h
    sub v8.8h, v12.8h, v11.8h
    sqrdmulh v12.8h, v9.8h, v2.h[3]
    mul v11.8h, v9.8h, v1.h[3]
    mls v11.8h, v12.8h, v0.h[0]
    mov v12.16b, v5.16b
    add v5.8h, v5.8h, v11.8h
    sub v9.8h, v12.8h, v11.8h
    sqrdmulh v12.8h, v10.8h, v2.h[4]
    mul v11.8h, v10.8h, v1.h[4]
    mls v11.8h, v12.8h, v0.h[0]
    mov v12.16b, v6.16b
    add v6.8h, v6.8h, v11.8h
    sub v10.8h, v12.8h, v11.8h
    str q3, [x14, #0]
    str q4, [x14, #64]
    str q5, [x14, #128]
    str q6, [x14, #192]
    str q7, [x14, #256]
    str q8, [x14, #320]
    str q9, [x14, #384]
    str q10, [x14, #448]
    ldr d3, [x3, #192]
    ldr d12, [x4, #192]
    mov v3.d[1], v12.d[0]
    ldr d4, [x3, #216]
    ldr d12, [x4, #216]
    mov v4.d[1], v12.d[0]
    ldr d5, [x3, #240]
    ldr d12, [x4, #240]
    mov v5.d[1], v12.d[0]
    ldr d6, [x3, #264]
    ldr d12, [x4, #264]
    mov v6.d[1], v12.d[0]
    ldr d7, [x3, #288]
    ldr d12, [x4, #288]
    mov v7.d[1], v12.d[0]
    ldr d8, [x3, #312]
    ldr d12, [x4, #312]
    mov v8.d[1], v12.d[0]
    ldr d9, [x3, #336]
    ldr d12, [x4, #336]
    mov v9.d[1], v12.d[0]
    ldr d10, [x3, #360]
    ldr d12, [x4, #360]
    mov v10.d[1], v12.d[0]
    mov v12.16b, v3.16b
    add v3.8h, v3.8h, v4.8h
    sub v4.8h, v12.8h, v4.8h
    mov v12.16b, v5.16b
    add v5.8h, v5.8h, v6.8h
    sub v6.8h, v12.8h, v6.8h
    mov v12.16b, v7.16b
    add v7.8h, v7.8h, v8.8h
    sub v8.8h, v12.8h, v8.8h
    mov v12.16b, v9.16b
    add v9.8h, v9.8h, v10.8h
    sub v10.8h, v12.8h, v10.8h
    mov v12.16b, v3.16b
    add v3.8h, v3.8h, v5.8h
    sub v5.8h, v12.8h, v5.8h
    sqrdmulh v12.8h, v6.8h, v2.h[1]
    mul v11.8h, v6.8h, v1.h[1]
    mls v11.8h, v12.8h, v0.h[0]
    mov v12.16b, v4.16b
    add v4.8h, v4.8h, v11.8h
    sub v6.8h, v12.8h, v11.8h
    mov v12.16b, v7.16b
    add v7.8h, v7.8h, v9.8h
    sub v9.8h, v12.8h, v9.8h
    sqrdmulh v12.8h, v10.8h, v2.h[1]
    mul v11.8h, v10.8h, v1.h[1]
    mls v11.8h, v12.8h, v0.h[0]
    mov v12.16b, v8.16b
    add v8.8h, v8.8h, v11.8h
    sub v10.8h, v12.8h, v11.8h
    mov v12.16b, v3.16b
    add v3.8h, v3.8h, v7.8h
    sub v7.8h, v12.8h, v7.8h
    sqrdmulh v12.8h, v8.8h, v2.h[2]
    mul v11.8h, v8.8h, v1.h[2]
    mls v11.8h, v12.8h, v0.h[0]
    mov v12.16b, v4.16b
    add v4.8h, v4.8h, v11.8h
    sub v8.8h, v12.8h, v11.8h
    sqrdmulh v12.8h, v9.8h, v2.h[3]
    mul v11.8h, v9.8h, v1.h[3]
    mls v11.8h, v12.8h, v0.h[0]
    mov v12.16b, v5.16b
    add v5.8h, v5.8h, v11.8h
    sub v9.8h, v12.8h, v11.8h
    sqrdmulh v12.8h, v10.8h, v2.h[4]
    mul v11.8h, v10.8h, v1.h[4]
    mls v11.8h, v12.8h, v0.h[0]
    mov v12.16b, v6.16b
    add v6.8h, v6.8h, v11.8h
    sub v10.8h, v12.8h, v11.8h
    str q3, [x14, #16]
    str q4, [x14, #80]
    str q5, [x14, #144]
    str q6, [x14, #208]
    str q7, [x14, #272]
    str q8, [x14, #336]
    str q9, [x14, #400]
    str q10, [x14, #464]
baseline_row0_pair01_end:

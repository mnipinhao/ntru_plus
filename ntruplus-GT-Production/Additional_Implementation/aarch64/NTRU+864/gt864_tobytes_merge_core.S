/* Exact scheduled instructions; comments omitted. See TOBYTES-INTEGRATION.md. */
#ifdef __APPLE__
#define byte_merge_row _byte_merge_row
#endif
.text
.global byte_merge_row
byte_merge_row:
        byte_merge_row_slothy_start:
        ldr q25, [x2, #0]
        add x12, x1, #16
        ldr q9, [x1, #0]
        ldr d10, [x12]
        add x12, x2, #16
        ldr q11, [x3, #0]
        ldr q24, [x4, #0]
        ldr d26, [x12]
        add x12, x3, #16
        tbl v19.16B, {v9.16B, v10.16B}, v24.16B
        ldr q24, [x4, #16]
        tbl v0.16B, {v25.16B, v26.16B}, v24.16B
        ldr q24, [x4, #32]
        ldr d12, [x12]
        tbl v21.16B, {v11.16B, v12.16B}, v24.16B
        orr v24.16B, v19.16B, v0.16B
        orr v24.16B, v24.16B, v21.16B
        str q24, [x0, #0]
        ldr q24, [x4, #48]
        tbl v19.16B, {v9.16B, v10.16B}, v24.16B
        ldr q24, [x4, #64]
        tbl v0.16B, {v25.16B, v26.16B}, v24.16B
        ldr q24, [x4, #80]
        tbl v21.16B, {v11.16B, v12.16B}, v24.16B
        orr v24.16B, v19.16B, v0.16B
        orr v24.16B, v24.16B, v21.16B
        str q24, [x0, #16]
        ldr q24, [x4, #96]
        tbl v19.16B, {v9.16B, v10.16B}, v24.16B
        ldr q24, [x4, #112]
        tbl v0.16B, {v25.16B, v26.16B}, v24.16B
        ldr q24, [x4, #128]
        tbl v21.16B, {v11.16B, v12.16B}, v24.16B
        orr v24.16B, v19.16B, v0.16B
        orr v24.16B, v24.16B, v21.16B
        str q24, [x0, #32]
        ldr q24, [x4, #144]
        tbl v19.16B, {v9.16B, v10.16B}, v24.16B
        ldr q24, [x4, #160]
        tbl v0.16B, {v25.16B, v26.16B}, v24.16B
        ldr q24, [x4, #176]
        tbl v21.16B, {v11.16B, v12.16B}, v24.16B
        orr v24.16B, v19.16B, v0.16B
        orr v24.16B, v24.16B, v21.16B
        str q24, [x0, #48]
        ldr q24, [x4, #192]
        tbl v19.16B, {v9.16B, v10.16B}, v24.16B
        ldr q24, [x4, #208]
        tbl v0.16B, {v25.16B, v26.16B}, v24.16B
        ldr q24, [x4, #224]
        tbl v21.16B, {v11.16B, v12.16B}, v24.16B
        orr v24.16B, v19.16B, v0.16B
        orr v24.16B, v24.16B, v21.16B
        str d24, [x0, #64]
        byte_merge_row_slothy_end:
    ret

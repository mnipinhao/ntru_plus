/* P34 probes.  Every entry here saves d8-d15, because the things it calls or
 * emits clobber them: ntt9_asm relies on its ntt.S wrapper for that save, and
 * the floor probes issue into the whole vector file on purpose.
 *
 * floor_gt_asm   -- GT's exact forward multiply multiset, all chains independent:
 *                   8 banks x 75 (sqrdmulh, mul, mls) = 1800, plus ntt_top's
 *                   80 plain `mul` = 1880 vector multiply-class ops.
 * floor_off_asm  -- the official's exact multiset, same construction:
 *                   8 x (36 sqrdmulh + 45 mul + 36 mls) = 936, plus
 *                   18 x (24 sqrdmulh + 16 mul + 24 mls) = 1152, total 2088.
 */
.text
.p2align 2

.macro SAVE_D
    stp d8,  d9,  [sp, #-64]!
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
.endm
.macro RESTORE_D
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    ldp d8,  d9,  [sp], #64
.endm

/* ---- ntt9 called safely: void ntt9_probe(int16_t *out, const int16_t *scr) ---- */
.global ntt9_probe
ntt9_probe:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    SAVE_D
    bl  ntt9_asm
    RESTORE_D
    ldp x29, x30, [sp], #16
    ret

/* 15 independent Montgomery triples, so nothing in a block depends on anything
 * else in it; repeated five times gives one bank's 75. */
.macro MT d, a, b
    sqrdmulh v\d\().8h, v\a\().8h, v\b\().8h
    mul      v\d\().8h, v\a\().8h, v\b\().8h
    mls      v\d\().8h, v\d\().8h, v\b\().8h
.endm
.macro BLOCK15
    MT 16,1,2   ; MT 17,3,4   ; MT 18,5,6   ; MT 19,7,8   ; MT 20,9,10
    MT 21,1,3   ; MT 22,2,4   ; MT 23,5,7   ; MT 24,6,8   ; MT 25,9,1
    MT 26,2,5   ; MT 27,3,6   ; MT 28,4,7   ; MT 29,8,9   ; MT 30,10,1
.endm

.global floor_gt_asm
floor_gt_asm:
    SAVE_D
    .rept 8
        BLOCK15 ; BLOCK15 ; BLOCK15 ; BLOCK15 ; BLOCK15
    .endr
    .rept 80
        mul v31.8h, v1.8h, v2.8h
    .endr
    RESTORE_D
    ret

.global floor_off_asm
floor_off_asm:
    SAVE_D
    .rept 8
        .rept 12
            sqrdmulh v16.8h, v1.8h,  v2.8h
            sqrdmulh v17.8h, v3.8h,  v4.8h
            sqrdmulh v18.8h, v5.8h,  v6.8h
            mls      v19.8h, v7.8h,  v8.8h
            mls      v20.8h, v9.8h,  v10.8h
            mls      v21.8h, v11.8h, v12.8h
        .endr
        .rept 15
            mul      v22.8h, v1.8h,  v2.8h
            mul      v23.8h, v3.8h,  v4.8h
            mul      v24.8h, v5.8h,  v6.8h
        .endr
    .endr
    .rept 18
        .rept 8
            sqrdmulh v25.8h, v1.8h,  v2.8h
            sqrdmulh v26.8h, v3.8h,  v4.8h
            sqrdmulh v27.8h, v5.8h,  v6.8h
            mls      v28.8h, v7.8h,  v8.8h
            mls      v29.8h, v9.8h,  v10.8h
            mls      v30.8h, v11.8h, v12.8h
        .endr
        .rept 16
            mul      v31.8h, v1.8h,  v2.8h
        .endr
    .endr
    RESTORE_D
    ret

/* ---- floor_top_asm: ntt_top's exact loop mix, every chain independent ----
 *
 * Per iteration ntt_top issues 2 ld4(4x8H), 5 mul, 14 add, 5 sub, 2 ldr d,
 * 2 mov(d-lane), 9 str q + 1 str q = 10 str q; 39 instructions, 16 iterations.
 * Here the same 39 instructions read only preloaded v0-v7 and write v16-v27
 * round robin, so nothing in an iteration waits on anything else in it.
 * x0 must point at 256 writable bytes; x1 at 256 readable bytes.
 */
.global floor_top_asm
floor_top_asm:
    SAVE_D
    mov x9, #16
.Lfloor_top_loop:
    ld4 {v8.8h,  v9.8h,  v10.8h, v11.8h}, [x1]
    ld4 {v12.8h, v13.8h, v14.8h, v15.8h}, [x1]
    mul v16.8h, v0.8h, v1.8h
    mul v17.8h, v2.8h, v3.8h
    mul v18.8h, v4.8h, v5.8h
    mul v19.8h, v6.8h, v7.8h
    mul v20.8h, v0.8h, v2.8h
    add v21.8h, v0.8h, v1.8h
    add v22.8h, v2.8h, v3.8h
    add v23.8h, v4.8h, v5.8h
    add v24.8h, v6.8h, v7.8h
    add v25.8h, v0.8h, v3.8h
    add v26.8h, v1.8h, v4.8h
    add v27.8h, v2.8h, v5.8h
    add v28.8h, v3.8h, v6.8h
    add v29.8h, v4.8h, v7.8h
    add v30.8h, v5.8h, v0.8h
    add v31.8h, v6.8h, v1.8h
    add v8.8h,  v7.8h, v2.8h
    add v9.8h,  v0.8h, v4.8h
    add v10.8h, v1.8h, v5.8h
    sub v11.8h, v0.8h, v1.8h
    sub v12.8h, v2.8h, v3.8h
    sub v13.8h, v4.8h, v5.8h
    sub v14.8h, v6.8h, v7.8h
    sub v15.8h, v0.8h, v5.8h
    ldr d1, [x1]
    ldr d2, [x1, #8]
    mov v3.d[0], v0.d[0]
    mov v4.d[1], v0.d[0]
    str q16, [x0]
    str q17, [x0, #16]
    str q18, [x0, #32]
    str q19, [x0, #48]
    str q20, [x0, #64]
    str q21, [x0, #80]
    str q22, [x0, #96]
    str q23, [x0, #112]
    str q24, [x0, #128]
    str q25, [x0, #144]
    subs x9, x9, #1
    b.ne .Lfloor_top_loop
    RESTORE_D
    ret

#if defined(__ELF__)
.section .note.GNU-stack,"",%progbits
#endif

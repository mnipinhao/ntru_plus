.text
.align 2

.equ GT_TMVP_STATUS_OK, 0
.equ GT_TMVP_STATUS_INVALID_ARGUMENT, 1
.equ GT_TMVP_BRANCH_N, 384
.equ GT_TMVP_ROW_N, 32
.equ GT_TMVP_ROW_STRIDE, 128
.equ GT_TMVP_ROWPACK_LANE_BYTES, 64

/*
 * Experimental complete-NTT32 quartic TMVP rowpack boundary.
 *
 * Layout:
 *   coeff[branch*384 + row*128 + lane*32 + k32]
 *
 * This revision processes eight consecutive k32 positions at a time.  The
 * arithmetic mirrors production asm/base_gt.S, but the loads/stores are
 * rowpack-contiguous and lambda is loaded from a rowpack-vector-order table:
 *
 *   physical_j = (32*row + 3*k32) mod 96
 */

.macro GT_TMVP_LOAD_LAMBDA_VECTOR
	add w13, w24, w24, lsl #1
	add w13, w25, w13
	lsl w13, w13, #6
	add w13, w13, w26, lsl #1
	uxtw x13, w13
	add x14, x23, x13
	ldr q1, [x14]
.endm

.macro GT_TMVP_ROWPACK_BASE inreg_a, inreg_b, outreg
	mov w8, #GT_TMVP_BRANCH_N
	madd w8, w24, w8, w26
	add w8, w8, w25, lsl #7
	uxtw x8, w8
	add \inreg_a, x20, x8, lsl #1
	add \inreg_b, x21, x8, lsl #1
	add \outreg, x19, x8, lsl #1
.endm

.macro GT_TMVP_LOAD_AB inreg_a, inreg_b
	ldr q4, [\inreg_a]
	ldr q5, [\inreg_a, #GT_TMVP_ROWPACK_LANE_BYTES]
	ldr q6, [\inreg_a, #(2 * GT_TMVP_ROWPACK_LANE_BYTES)]
	ldr q7, [\inreg_a, #(3 * GT_TMVP_ROWPACK_LANE_BYTES)]

	ldr q8, [\inreg_b]
	ldr q9, [\inreg_b, #GT_TMVP_ROWPACK_LANE_BYTES]
	ldr q10, [\inreg_b, #(2 * GT_TMVP_ROWPACK_LANE_BYTES)]
	ldr q11, [\inreg_b, #(3 * GT_TMVP_ROWPACK_LANE_BYTES)]
.endm

.macro GT_TMVP_BOUND_VECTOR reg
	cmgt v29.8h, \reg\().8h, v2.8h
	cmgt v30.8h, v3.8h, \reg\().8h
	and v29.16b, v29.16b, v31.16b
	and v30.16b, v30.16b, v31.16b
	sub \reg\().8h, \reg\().8h, v29.8h
	add \reg\().8h, \reg\().8h, v30.8h
.endm

.macro GT_TMVP_BOUND_AB
	GT_TMVP_BOUND_VECTOR v4
	GT_TMVP_BOUND_VECTOR v5
	GT_TMVP_BOUND_VECTOR v6
	GT_TMVP_BOUND_VECTOR v7
	GT_TMVP_BOUND_VECTOR v8
	GT_TMVP_BOUND_VECTOR v9
	GT_TMVP_BOUND_VECTOR v10
	GT_TMVP_BOUND_VECTOR v11
.endm

.macro GT_TMVP_BOUND_C
	GT_TMVP_BOUND_VECTOR v12
	GT_TMVP_BOUND_VECTOR v13
	GT_TMVP_BOUND_VECTOR v14
	GT_TMVP_BOUND_VECTOR v15
.endm

.macro GT_TMVP_STORE_RESULT outreg
	str q8, [\outreg]
	str q9, [\outreg, #GT_TMVP_ROWPACK_LANE_BYTES]
	str q10, [\outreg, #(2 * GT_TMVP_ROWPACK_LANE_BYTES)]
	str q11, [\outreg, #(3 * GT_TMVP_ROWPACK_LANE_BYTES)]
.endm

.macro GT_TMVP_DIRECT_LOAD_AB_ONE lane
	ldrh w13, [x15], #2
	add x14, x9, x13
	ld1 {v4.h}[\lane], [x14], #2
	ld1 {v5.h}[\lane], [x14], #2
	ld1 {v6.h}[\lane], [x14], #2
	ld1 {v7.h}[\lane], [x14]

	add x14, x10, x13
	ld1 {v8.h}[\lane], [x14], #2
	ld1 {v9.h}[\lane], [x14], #2
	ld1 {v10.h}[\lane], [x14], #2
	ld1 {v11.h}[\lane], [x14]
.endm

.macro GT_TMVP_DIRECT_LOAD_C_ONE lane
	add x14, x12, x13
	ld1 {v12.h}[\lane], [x14], #2
	ld1 {v13.h}[\lane], [x14], #2
	ld1 {v14.h}[\lane], [x14], #2
	ld1 {v15.h}[\lane], [x14]
.endm

.macro GT_TMVP_DIRECT_LOAD_AB
	GT_TMVP_DIRECT_LOAD_AB_ONE 0
	GT_TMVP_DIRECT_LOAD_AB_ONE 1
	GT_TMVP_DIRECT_LOAD_AB_ONE 2
	GT_TMVP_DIRECT_LOAD_AB_ONE 3
	GT_TMVP_DIRECT_LOAD_AB_ONE 4
	GT_TMVP_DIRECT_LOAD_AB_ONE 5
	GT_TMVP_DIRECT_LOAD_AB_ONE 6
	GT_TMVP_DIRECT_LOAD_AB_ONE 7
.endm

.macro GT_TMVP_DIRECT_LOAD_ABC_ONE lane
	GT_TMVP_DIRECT_LOAD_AB_ONE \lane
	GT_TMVP_DIRECT_LOAD_C_ONE \lane
.endm

.macro GT_TMVP_DIRECT_LOAD_ABC
	GT_TMVP_DIRECT_LOAD_ABC_ONE 0
	GT_TMVP_DIRECT_LOAD_ABC_ONE 1
	GT_TMVP_DIRECT_LOAD_ABC_ONE 2
	GT_TMVP_DIRECT_LOAD_ABC_ONE 3
	GT_TMVP_DIRECT_LOAD_ABC_ONE 4
	GT_TMVP_DIRECT_LOAD_ABC_ONE 5
	GT_TMVP_DIRECT_LOAD_ABC_ONE 6
	GT_TMVP_DIRECT_LOAD_ABC_ONE 7
.endm

.macro GT_TMVP_DIRECT_STORE_ONE lane
	ldrh w13, [x15], #2
	add x14, x11, x13
	st1 {v8.h}[\lane], [x14], #2
	st1 {v9.h}[\lane], [x14], #2
	st1 {v10.h}[\lane], [x14], #2
	st1 {v11.h}[\lane], [x14]
.endm

.macro GT_TMVP_DIRECT_STORE_RESULT
	GT_TMVP_DIRECT_STORE_ONE 0
	GT_TMVP_DIRECT_STORE_ONE 1
	GT_TMVP_DIRECT_STORE_ONE 2
	GT_TMVP_DIRECT_STORE_ONE 3
	GT_TMVP_DIRECT_STORE_ONE 4
	GT_TMVP_DIRECT_STORE_ONE 5
	GT_TMVP_DIRECT_STORE_ONE 6
	GT_TMVP_DIRECT_STORE_ONE 7
.endm

.macro GT_TMVP_TRANSPOSE_LOAD_D8 basereg, dst0, dst1, dst2, dst3
	ldrh w13, [x15], #2
	add x14, \basereg, x13
	ldr d16, [x14]
	ldrh w13, [x15], #2
	add x14, \basereg, x13
	ldr d17, [x14]
	ldrh w13, [x15], #2
	add x14, \basereg, x13
	ldr d18, [x14]
	ldrh w13, [x15], #2
	add x14, \basereg, x13
	ldr d19, [x14]
	ldrh w13, [x15], #2
	add x14, \basereg, x13
	ldr d20, [x14]
	ldrh w13, [x15], #2
	add x14, \basereg, x13
	ldr d21, [x14]
	ldrh w13, [x15], #2
	add x14, \basereg, x13
	ldr d22, [x14]
	ldrh w13, [x15], #2
	add x14, \basereg, x13
	ldr d23, [x14]

	zip1 v24.4h, v16.4h, v17.4h
	zip2 v25.4h, v16.4h, v17.4h
	zip1 v26.4h, v18.4h, v19.4h
	zip2 v27.4h, v18.4h, v19.4h
	zip1 v28.4h, v20.4h, v21.4h
	zip2 v29.4h, v20.4h, v21.4h
	zip1 v30.4h, v22.4h, v23.4h
	zip2 v31.4h, v22.4h, v23.4h

	zip1 v16.2s, v24.2s, v26.2s
	zip2 v17.2s, v24.2s, v26.2s
	zip1 v18.2s, v25.2s, v27.2s
	zip2 v19.2s, v25.2s, v27.2s
	zip1 v20.2s, v28.2s, v30.2s
	zip2 v21.2s, v28.2s, v30.2s
	zip1 v22.2s, v29.2s, v31.2s
	zip2 v23.2s, v29.2s, v31.2s

	zip1 \dst0\().2d, v16.2d, v20.2d
	zip1 \dst1\().2d, v17.2d, v21.2d
	zip1 \dst2\().2d, v18.2d, v22.2d
	zip1 \dst3\().2d, v19.2d, v23.2d
.endm

.macro GT_TMVP_TRANSPOSE_STORE_D8
	zip1 v24.4h, v8.4h, v9.4h
	zip2 v25.4h, v8.4h, v9.4h
	zip1 v26.4h, v10.4h, v11.4h
	zip2 v27.4h, v10.4h, v11.4h

	zip1 v16.2s, v24.2s, v26.2s
	zip2 v17.2s, v24.2s, v26.2s
	zip1 v18.2s, v25.2s, v27.2s
	zip2 v19.2s, v25.2s, v27.2s

	ext v28.16b, v8.16b, v8.16b, #8
	ext v29.16b, v9.16b, v9.16b, #8
	ext v30.16b, v10.16b, v10.16b, #8
	ext v31.16b, v11.16b, v11.16b, #8

	zip1 v24.4h, v28.4h, v29.4h
	zip2 v25.4h, v28.4h, v29.4h
	zip1 v26.4h, v30.4h, v31.4h
	zip2 v27.4h, v30.4h, v31.4h

	zip1 v20.2s, v24.2s, v26.2s
	zip2 v21.2s, v24.2s, v26.2s
	zip1 v22.2s, v25.2s, v27.2s
	zip2 v23.2s, v25.2s, v27.2s

	ldrh w13, [x15], #2
	add x14, x11, x13
	str d16, [x14]
	ldrh w13, [x15], #2
	add x14, x11, x13
	str d17, [x14]
	ldrh w13, [x15], #2
	add x14, x11, x13
	str d18, [x14]
	ldrh w13, [x15], #2
	add x14, x11, x13
	str d19, [x14]
	ldrh w13, [x15], #2
	add x14, x11, x13
	str d20, [x14]
	ldrh w13, [x15], #2
	add x14, x11, x13
	str d21, [x14]
	ldrh w13, [x15], #2
	add x14, x11, x13
	str d22, [x14]
	ldrh w13, [x15], #2
	add x14, x11, x13
	str d23, [x14]
.endm

.macro GT_TMVP_BATCH_MUL_BODY
	smull   v12.4s, v5.4h, v11.4h
	smull2  v13.4s, v5.8h, v11.8h
	smull   v14.4s, v6.4h, v11.4h
	smull2  v15.4s, v6.8h, v11.8h
	smull   v16.4s, v7.4h, v11.4h
	smull2  v17.4s, v7.8h, v11.8h

	smlal   v12.4s, v6.4h, v10.4h
	smlal2  v13.4s, v6.8h, v10.8h
	smlal   v14.4s, v7.4h, v10.4h
	smlal2  v15.4s, v7.8h, v10.8h

	smlal   v12.4s, v7.4h, v9.4h
	smlal2  v13.4s, v7.8h, v9.8h

	uzp1    v20.8h, v16.8h, v17.8h
	uzp1    v19.8h, v14.8h, v15.8h
	uzp1    v18.8h, v12.8h, v13.8h

	mul     v20.8h, v20.8h, v0.h[2]
	mul     v19.8h, v19.8h, v0.h[2]
	mul     v18.8h, v18.8h, v0.h[2]

	smlal   v16.4s, v20.4h, v0.h[0]
	smlal2  v17.4s, v20.8h, v0.h[0]
	smlal   v14.4s, v19.4h, v0.h[0]
	smlal2  v15.4s, v19.8h, v0.h[0]
	smlal   v12.4s, v18.4h, v0.h[0]
	smlal2  v13.4s, v18.8h, v0.h[0]

	uzp2    v30.8h, v16.8h, v17.8h
	uzp2    v29.8h, v14.8h, v15.8h
	uzp2    v28.8h, v12.8h, v13.8h

	smull   v18.4s, v7.4h, v8.4h
	smull2  v19.4s, v7.8h, v8.8h
	smull   v16.4s, v30.4h, v1.4h
	smull2  v17.4s, v30.8h, v1.8h
	smull   v14.4s, v29.4h, v1.4h
	smull2  v15.4s, v29.8h, v1.8h
	smull   v12.4s, v28.4h, v1.4h
	smull2  v13.4s, v28.8h, v1.8h

	smlal   v18.4s, v4.4h, v11.4h
	smlal2  v19.4s, v4.8h, v11.8h
	smlal   v16.4s, v4.4h, v10.4h
	smlal2  v17.4s, v4.8h, v10.8h
	smlal   v14.4s, v4.4h, v9.4h
	smlal2  v15.4s, v4.8h, v9.8h
	smlal   v12.4s, v4.4h, v8.4h
	smlal2  v13.4s, v4.8h, v8.8h

	smlal   v18.4s, v5.4h, v10.4h
	smlal2  v19.4s, v5.8h, v10.8h
	smlal   v16.4s, v5.4h, v9.4h
	smlal2  v17.4s, v5.8h, v9.8h
	smlal   v14.4s, v5.4h, v8.4h
	smlal2  v15.4s, v5.8h, v8.8h

	smlal   v18.4s, v6.4h, v9.4h
	smlal2  v19.4s, v6.8h, v9.8h
	smlal   v16.4s, v6.4h, v8.4h
	smlal2  v17.4s, v6.8h, v8.8h

	uzp1    v23.8h, v18.8h, v19.8h
	uzp1    v22.8h, v16.8h, v17.8h
	uzp1    v21.8h, v14.8h, v15.8h
	uzp1    v20.8h, v12.8h, v13.8h

	mul     v23.8h, v23.8h, v0.h[2]
	mul     v22.8h, v22.8h, v0.h[2]
	mul     v21.8h, v21.8h, v0.h[2]
	mul     v20.8h, v20.8h, v0.h[2]

	smlal   v18.4s, v23.4h, v0.h[0]
	smlal   v16.4s, v22.4h, v0.h[0]
	smlal   v14.4s, v21.4h, v0.h[0]
	smlal   v12.4s, v20.4h, v0.h[0]

	smlal2  v19.4s, v23.8h, v0.h[0]
	smlal2  v17.4s, v22.8h, v0.h[0]
	smlal2  v15.4s, v21.8h, v0.h[0]
	smlal2  v13.4s, v20.8h, v0.h[0]

	uzp2    v7.8h, v18.8h, v19.8h
	uzp2    v6.8h, v16.8h, v17.8h
	uzp2    v5.8h, v14.8h, v15.8h
	uzp2    v4.8h, v12.8h, v13.8h

	smull   v18.4s, v7.4h, v0.h[3]
	smull2  v19.4s, v7.8h, v0.h[3]
	smull   v16.4s, v6.4h, v0.h[3]
	smull2  v17.4s, v6.8h, v0.h[3]
	smull   v14.4s, v5.4h, v0.h[3]
	smull2  v15.4s, v5.8h, v0.h[3]
	smull   v12.4s, v4.4h, v0.h[3]
	smull2  v13.4s, v4.8h, v0.h[3]

	uzp1    v23.8h, v18.8h, v19.8h
	uzp1    v22.8h, v16.8h, v17.8h
	uzp1    v21.8h, v14.8h, v15.8h
	uzp1    v20.8h, v12.8h, v13.8h

	mul     v23.8h, v23.8h, v0.h[2]
	mul     v22.8h, v22.8h, v0.h[2]
	mul     v21.8h, v21.8h, v0.h[2]
	mul     v20.8h, v20.8h, v0.h[2]

	smlal   v18.4s, v23.4h, v0.h[0]
	smlal2  v19.4s, v23.8h, v0.h[0]
	smlal   v16.4s, v22.4h, v0.h[0]
	smlal2  v17.4s, v22.8h, v0.h[0]
	smlal   v14.4s, v21.4h, v0.h[0]
	smlal2  v15.4s, v21.8h, v0.h[0]
	smlal   v12.4s, v20.4h, v0.h[0]
	smlal2  v13.4s, v20.8h, v0.h[0]

	uzp2    v11.8h, v18.8h, v19.8h
	uzp2    v10.8h, v16.8h, v17.8h
	uzp2    v9.8h, v14.8h, v15.8h
	uzp2    v8.8h, v12.8h, v13.8h
.endm

.macro GT_TMVP_BATCH_ADD_BODY
	smull   v16.4s, v5.4h, v11.4h
	smull2  v17.4s, v5.8h, v11.8h
	smull   v18.4s, v6.4h, v11.4h
	smull2  v19.4s, v6.8h, v11.8h
	smull   v20.4s, v7.4h, v11.4h
	smull2  v21.4s, v7.8h, v11.8h

	smlal   v16.4s, v6.4h, v10.4h
	smlal2  v17.4s, v6.8h, v10.8h
	smlal   v18.4s, v7.4h, v10.4h
	smlal2  v19.4s, v7.8h, v10.8h

	smlal   v16.4s, v7.4h, v9.4h
	smlal2  v17.4s, v7.8h, v9.8h

	uzp1    v24.8h, v20.8h, v21.8h
	uzp1    v23.8h, v18.8h, v19.8h
	uzp1    v22.8h, v16.8h, v17.8h

	mul     v24.8h, v24.8h, v0.h[2]
	mul     v23.8h, v23.8h, v0.h[2]
	mul     v22.8h, v22.8h, v0.h[2]

	smlal   v20.4s, v24.4h, v0.h[0]
	smlal2  v21.4s, v24.8h, v0.h[0]
	smlal   v18.4s, v23.4h, v0.h[0]
	smlal2  v19.4s, v23.8h, v0.h[0]
	smlal   v16.4s, v22.4h, v0.h[0]
	smlal2  v17.4s, v22.8h, v0.h[0]

	uzp2    v30.8h, v20.8h, v21.8h
	uzp2    v29.8h, v18.8h, v19.8h
	uzp2    v28.8h, v16.8h, v17.8h

	smull   v22.4s, v7.4h, v8.4h
	smull2  v23.4s, v7.8h, v8.8h
	smull   v20.4s, v30.4h, v1.4h
	smull2  v21.4s, v30.8h, v1.8h
	smull   v18.4s, v29.4h, v1.4h
	smull2  v19.4s, v29.8h, v1.8h
	smull   v16.4s, v28.4h, v1.4h
	smull2  v17.4s, v28.8h, v1.8h

	smlal   v22.4s, v4.4h, v11.4h
	smlal2  v23.4s, v4.8h, v11.8h
	smlal   v20.4s, v4.4h, v10.4h
	smlal2  v21.4s, v4.8h, v10.8h
	smlal   v18.4s, v4.4h, v9.4h
	smlal2  v19.4s, v4.8h, v9.8h
	smlal   v16.4s, v4.4h, v8.4h
	smlal2  v17.4s, v4.8h, v8.8h

	smlal   v22.4s, v5.4h, v10.4h
	smlal2  v23.4s, v5.8h, v10.8h
	smlal   v20.4s, v5.4h, v9.4h
	smlal2  v21.4s, v5.8h, v9.8h
	smlal   v18.4s, v5.4h, v8.4h
	smlal2  v19.4s, v5.8h, v8.8h

	smlal   v22.4s, v6.4h, v9.4h
	smlal2  v23.4s, v6.8h, v9.8h
	smlal   v20.4s, v6.4h, v8.4h
	smlal2  v21.4s, v6.8h, v8.8h

	uzp1    v24.8h, v16.8h, v17.8h
	uzp1    v25.8h, v18.8h, v19.8h
	uzp1    v26.8h, v20.8h, v21.8h
	uzp1    v27.8h, v22.8h, v23.8h

	mul     v24.8h, v24.8h, v0.h[2]
	mul     v25.8h, v25.8h, v0.h[2]
	mul     v26.8h, v26.8h, v0.h[2]
	mul     v27.8h, v27.8h, v0.h[2]

	smlal   v16.4s, v24.4h, v0.h[0]
	smlal2  v17.4s, v24.8h, v0.h[0]
	smlal   v18.4s, v25.4h, v0.h[0]
	smlal2  v19.4s, v25.8h, v0.h[0]
	smlal   v20.4s, v26.4h, v0.h[0]
	smlal2  v21.4s, v26.8h, v0.h[0]
	smlal   v22.4s, v27.4h, v0.h[0]
	smlal2  v23.4s, v27.8h, v0.h[0]

	uzp2    v4.8h, v16.8h, v17.8h
	uzp2    v5.8h, v18.8h, v19.8h
	uzp2    v6.8h, v20.8h, v21.8h
	uzp2    v7.8h, v22.8h, v23.8h

	smull   v16.4s, v4.4h, v0.h[3]
	smull2  v17.4s, v4.8h, v0.h[3]
	smull   v18.4s, v5.4h, v0.h[3]
	smull2  v19.4s, v5.8h, v0.h[3]
	smull   v20.4s, v6.4h, v0.h[3]
	smull2  v21.4s, v6.8h, v0.h[3]
	smull   v22.4s, v7.4h, v0.h[3]
	smull2  v23.4s, v7.8h, v0.h[3]

	smlal   v16.4s, v12.4h, v0.h[4]
	smlal2  v17.4s, v12.8h, v0.h[4]
	smlal   v18.4s, v13.4h, v0.h[4]
	smlal2  v19.4s, v13.8h, v0.h[4]
	smlal   v20.4s, v14.4h, v0.h[4]
	smlal2  v21.4s, v14.8h, v0.h[4]
	smlal   v22.4s, v15.4h, v0.h[4]
	smlal2  v23.4s, v15.8h, v0.h[4]

	uzp1    v24.8h, v16.8h, v17.8h
	uzp1    v25.8h, v18.8h, v19.8h
	uzp1    v26.8h, v20.8h, v21.8h
	uzp1    v27.8h, v22.8h, v23.8h

	mul     v24.8h, v24.8h, v0.h[2]
	mul     v25.8h, v25.8h, v0.h[2]
	mul     v26.8h, v26.8h, v0.h[2]
	mul     v27.8h, v27.8h, v0.h[2]

	smlal   v16.4s, v24.4h, v0.h[0]
	smlal2  v17.4s, v24.8h, v0.h[0]
	smlal   v18.4s, v25.4h, v0.h[0]
	smlal2  v19.4s, v25.8h, v0.h[0]
	smlal   v20.4s, v26.4h, v0.h[0]
	smlal2  v21.4s, v26.8h, v0.h[0]
	smlal   v22.4s, v27.4h, v0.h[0]
	smlal2  v23.4s, v27.8h, v0.h[0]

	uzp2    v8.8h, v16.8h, v17.8h
	uzp2    v9.8h, v18.8h, v19.8h
	uzp2    v10.8h, v20.8h, v21.8h
	uzp2    v11.8h, v22.8h, v23.8h
.endm

.global gt_tmvp_quartic_tmvp_experimental_asm
.global _gt_tmvp_quartic_tmvp_experimental_asm
.global gt_tmvp_quartic_tmvp_experimental_asm_fast
.global _gt_tmvp_quartic_tmvp_experimental_asm_fast
gt_tmvp_quartic_tmvp_experimental_asm:
_gt_tmvp_quartic_tmvp_experimental_asm:
	cbz x0, Lgt_tmvp_mul_invalid
	cbz x1, Lgt_tmvp_mul_invalid
	cbz x2, Lgt_tmvp_mul_invalid
	b Lgt_tmvp_mul_checked

gt_tmvp_quartic_tmvp_experimental_asm_fast:
_gt_tmvp_quartic_tmvp_experimental_asm_fast:
Lgt_tmvp_mul_checked:
	stp d8, d9, [sp, #-64]!
	stp d10, d11, [sp, #16]
	stp d12, d13, [sp, #32]
	stp d14, d15, [sp, #48]

	adr x12, Lgt_tmvp_base_consts
	ld1 {v0.8h}, [x12]
	adr x16, Lgt_tmvp_lambda_rowpack

	mov w4, #0
Lgt_tmvp_mul_branch_loop:
	mov x12, #768
	madd x7, x4, x12, x0
	madd x8, x4, x12, x1
	madd x14, x4, x12, x2

	mov w5, #0
Lgt_tmvp_mul_row_loop:
	add x11, x7, x5, lsl #8
	add x9, x8, x5, lsl #8
	add x10, x14, x5, lsl #8
	mov w6, #4
Lgt_tmvp_mul_k_loop:
	ldr q1, [x16], #16
	GT_TMVP_LOAD_AB x9, x10
	GT_TMVP_BATCH_MUL_BODY
	GT_TMVP_STORE_RESULT x11

	add x9, x9, #16
	add x10, x10, #16
	add x11, x11, #16
	subs w6, w6, #1
	b.ne Lgt_tmvp_mul_k_loop
	add w5, w5, #1
	cmp w5, #3
	b.lt Lgt_tmvp_mul_row_loop
	add w4, w4, #1
	cmp w4, #2
	b.lt Lgt_tmvp_mul_branch_loop

	mov w0, #GT_TMVP_STATUS_OK
	b Lgt_tmvp_mul_done

Lgt_tmvp_mul_invalid:
	mov w0, #GT_TMVP_STATUS_INVALID_ARGUMENT
	ret

Lgt_tmvp_mul_done:
	ldp d14, d15, [sp, #48]
	ldp d12, d13, [sp, #32]
	ldp d10, d11, [sp, #16]
	ldp d8, d9, [sp], #64
	ret

.global gt_tmvp_quartic_tmvp_add_experimental_asm
.global _gt_tmvp_quartic_tmvp_add_experimental_asm
.global gt_tmvp_quartic_tmvp_add_experimental_asm_fast
.global _gt_tmvp_quartic_tmvp_add_experimental_asm_fast
gt_tmvp_quartic_tmvp_add_experimental_asm:
_gt_tmvp_quartic_tmvp_add_experimental_asm:
	cbz x0, Lgt_tmvp_add_invalid
	cbz x1, Lgt_tmvp_add_invalid
	cbz x2, Lgt_tmvp_add_invalid
	cbz x3, Lgt_tmvp_add_invalid
	b Lgt_tmvp_add_checked

gt_tmvp_quartic_tmvp_add_experimental_asm_fast:
_gt_tmvp_quartic_tmvp_add_experimental_asm_fast:
Lgt_tmvp_add_checked:
	stp d8, d9, [sp, #-64]!
	stp d10, d11, [sp, #16]
	stp d12, d13, [sp, #32]
	stp d14, d15, [sp, #48]

	adr x12, Lgt_tmvp_base_consts
	ld1 {v0.8h}, [x12]
	adr x16, Lgt_tmvp_lambda_rowpack

	mov w4, #0
Lgt_tmvp_add_branch_loop:
	mov x12, #768
	madd x7, x4, x12, x0
	madd x8, x4, x12, x1
	madd x14, x4, x12, x2
	madd x15, x4, x12, x3

	mov w5, #0
Lgt_tmvp_add_row_loop:
	add x11, x7, x5, lsl #8
	add x9, x8, x5, lsl #8
	add x10, x14, x5, lsl #8
	add x12, x15, x5, lsl #8
	mov w6, #4
Lgt_tmvp_add_k_loop:
	ldr q1, [x16], #16
	GT_TMVP_LOAD_AB x9, x10
	ldr q12, [x12]
	ldr q13, [x12, #GT_TMVP_ROWPACK_LANE_BYTES]
	ldr q14, [x12, #(2 * GT_TMVP_ROWPACK_LANE_BYTES)]
	ldr q15, [x12, #(3 * GT_TMVP_ROWPACK_LANE_BYTES)]
	GT_TMVP_BATCH_ADD_BODY
	GT_TMVP_STORE_RESULT x11

	add x9, x9, #16
	add x10, x10, #16
	add x11, x11, #16
	add x12, x12, #16
	subs w6, w6, #1
	b.ne Lgt_tmvp_add_k_loop
	add w5, w5, #1
	cmp w5, #3
	b.lt Lgt_tmvp_add_row_loop
	add w4, w4, #1
	cmp w4, #2
	b.lt Lgt_tmvp_add_branch_loop

	mov w0, #GT_TMVP_STATUS_OK
	b Lgt_tmvp_add_done

Lgt_tmvp_add_invalid:
	mov w0, #GT_TMVP_STATUS_INVALID_ARGUMENT
	ret

Lgt_tmvp_add_done:
	ldp d14, d15, [sp, #48]
	ldp d12, d13, [sp, #32]
	ldp d10, d11, [sp, #16]
	ldp d8, d9, [sp], #64
	ret

	.global gt_tmvp_quartic_tmvp_experimental_asm_bound_inputs_fast
	.global _gt_tmvp_quartic_tmvp_experimental_asm_bound_inputs_fast
	gt_tmvp_quartic_tmvp_experimental_asm_bound_inputs_fast:
	_gt_tmvp_quartic_tmvp_experimental_asm_bound_inputs_fast:
		stp d8, d9, [sp, #-64]!
		stp d10, d11, [sp, #16]
		stp d12, d13, [sp, #32]
		stp d14, d15, [sp, #48]

		adr x12, Lgt_tmvp_base_consts
		ld1 {v0.8h}, [x12]
		adr x12, Lgt_tmvp_bound_consts
		ld1 {v2.8h}, [x12], #16
		ld1 {v3.8h}, [x12], #16
		ld1 {v31.8h}, [x12]
		adr x16, Lgt_tmvp_lambda_rowpack

		mov w4, #0
	Lgt_tmvp_bound_mul_branch_loop:
		mov x12, #768
		madd x7, x4, x12, x0
		madd x8, x4, x12, x1
		madd x14, x4, x12, x2

		mov w5, #0
	Lgt_tmvp_bound_mul_row_loop:
		add x11, x7, x5, lsl #8
		add x9, x8, x5, lsl #8
		add x10, x14, x5, lsl #8
		mov w6, #4
	Lgt_tmvp_bound_mul_k_loop:
		ldr q1, [x16], #16
		GT_TMVP_LOAD_AB x9, x10
		GT_TMVP_BOUND_AB
		GT_TMVP_BATCH_MUL_BODY
		GT_TMVP_STORE_RESULT x11

		add x9, x9, #16
		add x10, x10, #16
		add x11, x11, #16
		subs w6, w6, #1
		b.ne Lgt_tmvp_bound_mul_k_loop
		add w5, w5, #1
		cmp w5, #3
		b.lt Lgt_tmvp_bound_mul_row_loop
		add w4, w4, #1
		cmp w4, #2
		b.lt Lgt_tmvp_bound_mul_branch_loop

		mov w0, #GT_TMVP_STATUS_OK
		ldp d14, d15, [sp, #48]
		ldp d12, d13, [sp, #32]
		ldp d10, d11, [sp, #16]
		ldp d8, d9, [sp], #64
		ret

	.global gt_tmvp_quartic_tmvp_add_experimental_asm_bound_inputs_fast
	.global _gt_tmvp_quartic_tmvp_add_experimental_asm_bound_inputs_fast
	gt_tmvp_quartic_tmvp_add_experimental_asm_bound_inputs_fast:
	_gt_tmvp_quartic_tmvp_add_experimental_asm_bound_inputs_fast:
		stp d8, d9, [sp, #-64]!
		stp d10, d11, [sp, #16]
		stp d12, d13, [sp, #32]
		stp d14, d15, [sp, #48]

		adr x12, Lgt_tmvp_base_consts
		ld1 {v0.8h}, [x12]
		adr x12, Lgt_tmvp_bound_consts
		ld1 {v2.8h}, [x12], #16
		ld1 {v3.8h}, [x12], #16
		ld1 {v31.8h}, [x12]
		adr x16, Lgt_tmvp_lambda_rowpack

		mov w4, #0
	Lgt_tmvp_bound_add_branch_loop:
		mov x12, #768
		madd x7, x4, x12, x0
		madd x8, x4, x12, x1
		madd x14, x4, x12, x2
		madd x15, x4, x12, x3

		mov w5, #0
	Lgt_tmvp_bound_add_row_loop:
		add x11, x7, x5, lsl #8
		add x9, x8, x5, lsl #8
		add x10, x14, x5, lsl #8
		add x12, x15, x5, lsl #8
		mov w6, #4
	Lgt_tmvp_bound_add_k_loop:
		ldr q1, [x16], #16
		GT_TMVP_LOAD_AB x9, x10
		ldr q12, [x12]
		ldr q13, [x12, #GT_TMVP_ROWPACK_LANE_BYTES]
		ldr q14, [x12, #(2 * GT_TMVP_ROWPACK_LANE_BYTES)]
		ldr q15, [x12, #(3 * GT_TMVP_ROWPACK_LANE_BYTES)]
		GT_TMVP_BOUND_AB
		GT_TMVP_BOUND_C
		GT_TMVP_BATCH_ADD_BODY
		GT_TMVP_STORE_RESULT x11

		add x9, x9, #16
		add x10, x10, #16
		add x11, x11, #16
		add x12, x12, #16
		subs w6, w6, #1
		b.ne Lgt_tmvp_bound_add_k_loop
		add w5, w5, #1
		cmp w5, #3
		b.lt Lgt_tmvp_bound_add_row_loop
		add w4, w4, #1
		cmp w4, #2
		b.lt Lgt_tmvp_bound_add_branch_loop

		mov w0, #GT_TMVP_STATUS_OK
		ldp d14, d15, [sp, #48]
		ldp d12, d13, [sp, #32]
		ldp d10, d11, [sp, #16]
		ldp d8, d9, [sp], #64
		ret

	.global bench_gt_tmvp_fused_direct_mul_asm
	.global _bench_gt_tmvp_fused_direct_mul_asm
bench_gt_tmvp_fused_direct_mul_asm:
_bench_gt_tmvp_fused_direct_mul_asm:
	stp d8, d9, [sp, #-64]!
	stp d10, d11, [sp, #16]
	stp d12, d13, [sp, #32]
	stp d14, d15, [sp, #48]

	adr x14, Lgt_tmvp_base_consts
	ld1 {v0.8h}, [x14]
	adr x16, Lgt_tmvp_block_offsets
	adr x17, Lgt_tmvp_lambda_rowpack

	mov w4, #0
Lgt_tmvp_fused_mul_branch_loop:
	mov x8, #768
	mul x8, x8, x4
	add x9, x1, x8
	add x10, x2, x8
	add x11, x0, x8

	mov w5, #0
Lgt_tmvp_fused_mul_row_loop:
	mov w6, #0
Lgt_tmvp_fused_mul_batch_loop:
	lsl w8, w5, #2
	add w8, w8, w6
	add x15, x16, w8, uxtw #4
	mov x7, x15
	ldr q1, [x17], #16

	GT_TMVP_DIRECT_LOAD_AB
	GT_TMVP_BATCH_MUL_BODY
	mov x15, x7
	GT_TMVP_DIRECT_STORE_RESULT

	add w6, w6, #1
	cmp w6, #4
	b.lt Lgt_tmvp_fused_mul_batch_loop
	add w5, w5, #1
	cmp w5, #3
	b.lt Lgt_tmvp_fused_mul_row_loop
	add w4, w4, #1
	cmp w4, #2
	b.lt Lgt_tmvp_fused_mul_branch_loop

	ldp d14, d15, [sp, #48]
	ldp d12, d13, [sp, #32]
	ldp d10, d11, [sp, #16]
	ldp d8, d9, [sp], #64
	ret

.global bench_gt_tmvp_fused_direct_add_asm
.global _bench_gt_tmvp_fused_direct_add_asm
bench_gt_tmvp_fused_direct_add_asm:
_bench_gt_tmvp_fused_direct_add_asm:
	stp d8, d9, [sp, #-64]!
	stp d10, d11, [sp, #16]
	stp d12, d13, [sp, #32]
	stp d14, d15, [sp, #48]

	adr x14, Lgt_tmvp_base_consts
	ld1 {v0.8h}, [x14]
	adr x16, Lgt_tmvp_block_offsets
	adr x17, Lgt_tmvp_lambda_rowpack

	mov w4, #0
Lgt_tmvp_fused_add_branch_loop:
	mov x8, #768
	mul x8, x8, x4
	add x9, x1, x8
	add x10, x2, x8
	add x11, x0, x8
	add x12, x3, x8

	mov w5, #0
Lgt_tmvp_fused_add_row_loop:
	mov w6, #0
Lgt_tmvp_fused_add_batch_loop:
	lsl w8, w5, #2
	add w8, w8, w6
	add x15, x16, w8, uxtw #4
	mov x7, x15
	ldr q1, [x17], #16

	GT_TMVP_DIRECT_LOAD_ABC
	GT_TMVP_BATCH_ADD_BODY
	mov x15, x7
	GT_TMVP_DIRECT_STORE_RESULT

	add w6, w6, #1
	cmp w6, #4
	b.lt Lgt_tmvp_fused_add_batch_loop
	add w5, w5, #1
	cmp w5, #3
	b.lt Lgt_tmvp_fused_add_row_loop
	add w4, w4, #1
	cmp w4, #2
	b.lt Lgt_tmvp_fused_add_branch_loop

	ldp d14, d15, [sp, #48]
	ldp d12, d13, [sp, #32]
	ldp d10, d11, [sp, #16]
	ldp d8, d9, [sp], #64
	ret

.global bench_gt_tmvp_fused_transpose_mul_asm
.global _bench_gt_tmvp_fused_transpose_mul_asm
bench_gt_tmvp_fused_transpose_mul_asm:
_bench_gt_tmvp_fused_transpose_mul_asm:
	stp d8, d9, [sp, #-64]!
	stp d10, d11, [sp, #16]
	stp d12, d13, [sp, #32]
	stp d14, d15, [sp, #48]

	adr x14, Lgt_tmvp_base_consts
	ld1 {v0.8h}, [x14]
	adr x16, Lgt_tmvp_block_offsets
	adr x17, Lgt_tmvp_lambda_rowpack

	mov w4, #0
Lgt_tmvp_transpose_mul_branch_loop:
	mov x8, #768
	mul x8, x8, x4
	add x9, x1, x8
	add x10, x2, x8
	add x11, x0, x8

	mov w5, #0
Lgt_tmvp_transpose_mul_row_loop:
	mov w6, #0
Lgt_tmvp_transpose_mul_batch_loop:
	lsl w8, w5, #2
	add w8, w8, w6
	add x15, x16, w8, uxtw #4
	mov x7, x15
	ldr q1, [x17], #16

	GT_TMVP_TRANSPOSE_LOAD_D8 x9, v4, v5, v6, v7
	mov x15, x7
	GT_TMVP_TRANSPOSE_LOAD_D8 x10, v8, v9, v10, v11
	GT_TMVP_BATCH_MUL_BODY
	mov x15, x7
	GT_TMVP_TRANSPOSE_STORE_D8

	add w6, w6, #1
	cmp w6, #4
	b.lt Lgt_tmvp_transpose_mul_batch_loop
	add w5, w5, #1
	cmp w5, #3
	b.lt Lgt_tmvp_transpose_mul_row_loop
	add w4, w4, #1
	cmp w4, #2
	b.lt Lgt_tmvp_transpose_mul_branch_loop

	ldp d14, d15, [sp, #48]
	ldp d12, d13, [sp, #32]
	ldp d10, d11, [sp, #16]
	ldp d8, d9, [sp], #64
	ret

.global bench_gt_tmvp_fused_transpose_add_asm
.global _bench_gt_tmvp_fused_transpose_add_asm
bench_gt_tmvp_fused_transpose_add_asm:
_bench_gt_tmvp_fused_transpose_add_asm:
	stp d8, d9, [sp, #-64]!
	stp d10, d11, [sp, #16]
	stp d12, d13, [sp, #32]
	stp d14, d15, [sp, #48]

	adr x14, Lgt_tmvp_base_consts
	ld1 {v0.8h}, [x14]
	adr x16, Lgt_tmvp_block_offsets
	adr x17, Lgt_tmvp_lambda_rowpack

	mov w4, #0
Lgt_tmvp_transpose_add_branch_loop:
	mov x8, #768
	mul x8, x8, x4
	add x9, x1, x8
	add x10, x2, x8
	add x11, x0, x8
	add x12, x3, x8

	mov w5, #0
Lgt_tmvp_transpose_add_row_loop:
	mov w6, #0
Lgt_tmvp_transpose_add_batch_loop:
	lsl w8, w5, #2
	add w8, w8, w6
	add x15, x16, w8, uxtw #4
	mov x7, x15
	ldr q1, [x17], #16

	GT_TMVP_TRANSPOSE_LOAD_D8 x9, v4, v5, v6, v7
	mov x15, x7
	GT_TMVP_TRANSPOSE_LOAD_D8 x10, v8, v9, v10, v11
	mov x15, x7
	GT_TMVP_TRANSPOSE_LOAD_D8 x12, v12, v13, v14, v15
	GT_TMVP_BATCH_ADD_BODY
	mov x15, x7
	GT_TMVP_TRANSPOSE_STORE_D8

	add w6, w6, #1
	cmp w6, #4
	b.lt Lgt_tmvp_transpose_add_batch_loop
	add w5, w5, #1
	cmp w5, #3
	b.lt Lgt_tmvp_transpose_add_row_loop
	add w4, w4, #1
	cmp w4, #2
	b.lt Lgt_tmvp_transpose_add_branch_loop

	ldp d14, d15, [sp, #48]
	ldp d12, d13, [sp, #32]
	ldp d10, d11, [sp, #16]
	ldp d8, d9, [sp], #64
	ret

.align 4
Lgt_tmvp_block_offsets:
	/* row 0 */
	.hword 0, 24, 48, 72, 96, 120, 144, 168
	.hword 192, 216, 240, 264, 288, 312, 336, 360
	.hword 384, 408, 432, 456, 480, 504, 528, 552
	.hword 576, 600, 624, 648, 672, 696, 720, 744
	/* row 1 */
	.hword 256, 280, 304, 328, 352, 376, 400, 424
	.hword 448, 472, 496, 520, 544, 568, 592, 616
	.hword 640, 664, 688, 712, 736, 760, 16, 40
	.hword 64, 88, 112, 136, 160, 184, 208, 232
	/* row 2 */
	.hword 512, 536, 560, 584, 608, 632, 656, 680
	.hword 704, 728, 752, 8, 32, 56, 80, 104
	.hword 128, 152, 176, 200, 224, 248, 272, 296
	.hword 320, 344, 368, 392, 416, 440, 464, 488

.align 4
Lgt_tmvp_base_consts:
	.hword 0x0d81, 0x4bd4, 0xcd7f, 0x0363
	.hword 0xff6d, 0xf9dd, 0xc5d5, 0x0000

	.align 4
Lgt_tmvp_bound_consts:
	.hword 6144, 6144, 6144, 6144, 6144, 6144, 6144, 6144
	.hword -6144, -6144, -6144, -6144, -6144, -6144, -6144, -6144
	.hword 10371, 10371, 10371, 10371, 10371, 10371, 10371, 10371

	.align 4
Lgt_tmvp_lambda_rowpack:
	/* branch 0 */
	/* row 0, k32 00..07 */
	.hword   1655,  -1655,    183,   -183,  -1674,   1674,   -559,    559
	/* row 0, k32 08..15 */
	.hword   -397,    397,   1059,  -1059,   -223,    223,  -1138,   1138
	/* row 0, k32 16..23 */
	.hword    242,   -242,   1514,  -1514,    432,   -432,  -1640,   1640
	/* row 0, k32 24..31 */
	.hword    437,   -437,  -1723,   1723,   -277,    277,   -933,    933
	/* row 1, k32 00..07 */
	.hword   -443,    443,   -943,    943,    352,   -352,   -312,    312
	/* row 1, k32 08..15 */
	.hword    100,   -100,  -1660,   1660,  -1250,   1250,      8,     -8
	/* row 1, k32 16..23 */
	.hword   1341,  -1341,   1247,  -1247,  -1206,   1206,    -31,     31
	/* row 1, k32 24..31 */
	.hword  -1364,   1364,   1209,  -1209,   -235,    235,    444,   -444
	/* row 2, k32 00..07 */
	.hword  -1212,   1212,    760,   -760,   1322,  -1322,    871,   -871
	/* row 2, k32 08..15 */
	.hword    297,   -297,    601,   -601,   1473,  -1473,   1130,  -1130
	/* row 2, k32 16..23 */
	.hword  -1583,   1583,    696,   -696,    774,   -774,   1671,  -1671
	/* row 2, k32 24..31 */
	.hword    927,   -927,    514,   -514,    512,   -512,    489,   -489
	/* branch 1 */
	/* row 0, k32 00..07 */
	.hword    779,   -779,   1588,  -1588,  -1095,   1095,    892,   -892
	/* row 0, k32 08..15 */
	.hword   1221,  -1221,   -218,    218,    294,   -294,   -732,    732
	/* row 0, k32 16..23 */
	.hword     22,    -22,   1709,  -1709,   -275,    275,   1108,  -1108
	/* row 0, k32 24..31 */
	.hword    354,   -354,  -1728,   1728,   -968,    968,    858,   -858
	/* row 1, k32 00..07 */
	.hword    274,   -274,   -400,    400,     32,    -32,   1543,  -1543
	/* row 1, k32 08..15 */
	.hword  -1248,   1248,  -1408,   1408,  -1685,   1685,    315,   -315
	/* row 1, k32 16..23 */
	.hword   1379,  -1379,  -1458,   1458,  -1681,   1681,    940,   -940
	/* row 1, k32 24..31 */
	.hword   -124,    124,   1367,  -1367,   1550,  -1550,  -1531,   1531
	/* row 2, k32 00..07 */
	.hword  -1053,   1053,  -1188,   1188,   1063,  -1063,   1022,  -1022
	/* row 2, k32 08..15 */
	.hword     27,    -27,   1626,  -1626,   1391,  -1391,    417,   -417
	/* row 2, k32 16..23 */
	.hword  -1401,   1401,   -251,    251,  -1501,   1501,   1409,  -1409
	/* row 2, k32 24..31 */
	.hword   -230,    230,    361,   -361,   -582,    582,    673,   -673

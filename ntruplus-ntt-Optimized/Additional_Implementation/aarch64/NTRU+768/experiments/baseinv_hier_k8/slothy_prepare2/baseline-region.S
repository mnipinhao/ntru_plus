slothy_start_baseinv_prepare2_group_baseline:
	prepare_two_and_c01
	mov v10.16b, v1.16b
	mov v1.16b, v0.16b

	prepare_one
	fqmul_keep v11, v10, v4

	str q4, [x1], #16
	str q10, [x2], #16
	str q11, [x3], #16
	mov v0.16b, v1.16b
slothy_end_baseinv_prepare2_group_baseline:

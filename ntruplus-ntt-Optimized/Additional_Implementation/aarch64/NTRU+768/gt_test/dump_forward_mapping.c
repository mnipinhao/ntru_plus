#include <stdint.h>
#include <stdio.h>
#include <limits.h>

#if defined(__GNUC__) || defined(__clang__)
#define NTRUPLUS_UNUSED __attribute__((unused))
#else
#define NTRUPLUS_UNUSED
#endif

/*
 * Forward mapping dump helper.
 *
 * This debug tool includes ntt.c directly so the printed constants come from
 * the exact twist tables used by the C reference.  The output answers:
 *
 *   r[branch_start + 4*k + lane] is multiplied by which twist constant?
 *
 * It also prints the 96-point Good-Thomas input CRT coordinates used by
 * ntt96_goodthomas(), so the twist/gather path can be compared against a
 * future assembly load schedule.
 */
#include "../ntt.c"

static unsigned bitreverse5(unsigned x)
{
	unsigned r = 0;

	for (int i = 0; i < 5; i++)
	{
		r = (r << 1) | (x & 1U);
		x >>= 1;
	}

	return r;
}

static int modq(int32_t a)
{
	int r = a % NTRUPLUS_Q;

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}

	return r;
}

static int normal_from_mont(int16_t a)
{
	return modq(montgomery_reduce(a));
}

static int centered_modq(int32_t a)
{
	int r = modq(a);

	if (r > NTRUPLUS_Q / 2)
	{
		r -= NTRUPLUS_Q;
	}

	return r;
}

static int centered_normal_from_mont(int16_t a)
{
	return centered_modq(montgomery_reduce(a));
}

static int asm_precompute_from_normal(int c)
{
	/*
	 * sqrdmulh-compatible signed nearest integer for the Neon Barrett
	 * multiplication sequence:
	 *
	 *   sqrdmulh hi, a, p
	 *   mul      lo, a, c
	 *   mls      lo, hi, q
	 *
	 * p is nearest_integer(c * 2^15 / q).  Keep the negative case explicit;
	 * C casts or floating round() are too easy to make inconsistent with the
	 * assembly table.
	 */
	const int32_t scale = 1 << 15;
	const int64_t product = (int64_t)c * scale;

	if (product >= 0)
	{
		return (int)((product + NTRUPLUS_Q / 2) / NTRUPLUS_Q);
	}

	return -(int)((-product + NTRUPLUS_Q / 2) / NTRUPLUS_Q);
}

static int input_crt_n(int n3, int n32)
{
	return (64*n3 + 33*n32) % 96;
}

static void NTRUPLUS_UNUSED find_input_crt_coords(int n, int *out_n3, int *out_n32)
{
	for (int n3 = 0; n3 < 3; n3++)
	{
		for (int n32 = 0; n32 < 32; n32++)
		{
			if (input_crt_n(n3, n32) == n)
			{
				*out_n3 = n3;
				*out_n32 = n32;
				return;
			}
		}
	}

	*out_n3 = -1;
	*out_n32 = -1;
}

static int16_t dft3_twiddle_mont(int exp)
{
	static const int16_t powers[3] = {
		NTRUPLUS_R,
		GT96_OMEGA3,
		GT96_OMEGA3_SQ
	};

	return powers[exp % 3];
}

static int physical_pos_for_input_crt(int branch, int lane, int n3, int n32)
{
	const int branch_start = branch * (NTRUPLUS_N / 2);
	const int block = input_crt_n(n3, n32);

	return branch_start + 4*block + lane;
}

static void format_branch_lane_stream(char out[80], int branch, int lane)
{
	const int branch_start = branch * (NTRUPLUS_N / 2);

	snprintf(out,
	         80,
	         "Branch%d lane%d: r[%d,%d,%d,...,%d]",
	         branch,
	         lane,
	         branch_start + lane,
	         branch_start + lane + 4,
	         branch_start + lane + 8,
	         branch_start + 4*95 + lane);
}

static void format_dft3_offset_group(char out[128],
                                     int branch,
                                     int lane,
                                     int n3,
                                     int vector_group)
{
	int used = 0;

	out[0] = '\0';
	for (int i = 0; i < 8; i++)
	{
		const int n32 = 8*vector_group + i;
		const int pos = physical_pos_for_input_crt(branch, lane, n3, n32);

		used += snprintf(out + used,
		                 128 - used,
		                 "%sr%d",
		                 i == 0 ? "" : " ",
		                 pos);
	}
}

static const char *ntt32_reg_for_index(int index);

static const char *top_split_formula_for_branch(int branch)
{
	return branch == 0 ? "low_plus_zeta_high" : "low_plus_high_minus_zeta_high";
}

static const char *dft3_one_mul_role(int source_n3, int output_k3)
{
	if (output_k3 == 0)
	{
		return "x0_plus_x1_plus_x2";
	}

	if (output_k3 == 1)
	{
		switch (source_n3)
		{
		case 0:
			return "x0";
		case 1:
			return "plus_omega3_times_d";
		default:
			return "minus_x2_minus_omega3_times_d";
		}
	}

	switch (source_n3)
	{
	case 0:
		return "x0";
	case 1:
		return "minus_x1_minus_omega3_times_d";
	default:
		return "plus_omega3_times_d";
	}
}

static const char *dft3_input_name(int n3)
{
	static const char *names[3] = { "x0", "x1", "x2" };

	return names[n3];
}

static const char *branch_output_name(int branch);

static const char *dft3_output_name(int k3)
{
	static const char *names[3] = { "Y0", "Y1", "Y2" };

	return names[k3];
}

static const char *dft3_output_formula(int k3)
{
	static const char *formulas[3] = {
		"Y0=x0+x1+x2",
		"Y1=x0-x2+omega3*(x1-x2)",
		"Y2=x0-x1-omega3*(x1-x2)"
	};

	return formulas[k3];
}

static void format_gt_matrix_name(char out[32], int branch, int lane)
{
	snprintf(out, 32, "M%d=B%d_q%d", 4*branch + lane, branch, lane);
}

static void format_phase3_q_contents(char out[256], int k3, int k32)
{
	snprintf(out, 256,
	         "Q<w%02d_s0>=[M0_%s[%d]|M1_%s[%d]|M2_%s[%d]|M3_%s[%d]|"
	         "M4_%s[%d]|M5_%s[%d]|M6_%s[%d]|M7_%s[%d]]",
	         k32,
	         dft3_output_name(k3), k32,
	         dft3_output_name(k3), k32,
	         dft3_output_name(k3), k32,
	         dft3_output_name(k3), k32,
	         dft3_output_name(k3), k32,
	         dft3_output_name(k3), k32,
	         dft3_output_name(k3), k32,
	         dft3_output_name(k3), k32);
}

static void format_phase3_source(char out[128],
                                 int branch,
                                 int lane,
                                 int n3,
                                 int k32)
{
	const int block = input_crt_n(n3, k32);
	const int low = 4*block + lane;
	const int high = low + NTRUPLUS_N / 2;
	const int branch_pos = 4*block + lane;

	snprintf(out, 128,
	         "%s=%s[%d]*twist[%d]_from_a%d|a%d",
	         dft3_input_name(n3),
	         branch_output_name(branch),
	         branch_pos,
	         block,
	         low,
	         high);
}

static const char *chunk_role_name(int role)
{
	static const char *names[3] = { "A", "B", "C" };

	return names[role];
}

static int dft3_ld4_stage_coeff_offset(int branch,
                                       int group,
                                       int n3,
                                       int n32_lane,
                                       int quartic_lane)
{
	return (((branch * 4 + group) * 3 + n3) * 8 + n32_lane) * 4 +
		quartic_lane;
}

static int dft3_ld3_stage_coeff_offset(int branch,
                                       int quartic_lane,
                                       int group,
                                       int n32_lane,
                                       int n3)
{
	return (((branch * 4 + quartic_lane) * 4 + group) * 8 + n32_lane) * 3 +
		n3;
}

static void NTRUPLUS_UNUSED dump_gt_stage1_dft3_store_plan(void)
{
	FILE *fp = fopen("build/gt_stage1_dft3_store_plan.csv", "w");

	if (fp == NULL)
	{
		perror("build/gt_stage1_dft3_store_plan.csv");
		return;
	}

	fprintf(fp,
	        "stage1_order,branch,group,n3,n32,n32_lane,quartic_lane,"
	        "source_chunk_role,source_chunk,source_block_k,source_branch_pos,"
	        "source_after_top_split_pos,low_input_pos,high_input_pos,"
	        "top_zeta_mont,top_zeta_normal,top_split_formula,twist_table,"
	        "twist_index,twist_mont,twist_normal,operation,"
	        "ld4_load_chunk_low,ld4_load_chunk_high,ld4_vector_lane,"
	        "ld4_staging_expr,ld4_staging_coeff_offset,ld4_staging_byte_offset,"
	        "dft3_ld4_load_row,dft3_ld4_output_register,"
	        "ld3_staging_expr,ld3_staging_coeff_offset,ld3_staging_byte_offset,"
	        "dft3_ld3_load_group,dft3_ld3_output_register,notes\n");

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int16_t *twist = branch == 0 ? twist_branch0 : twist_branch1;
		const char *twist_name = branch == 0 ? "twist_branch0" : "twist_branch1";

		for (int group = 0; group < 4; group++)
		{
			for (int n3 = 0; n3 < 3; n3++)
			{
				for (int n32_lane = 0; n32_lane < 8; n32_lane++)
				{
					const int n32 = 8*group + n32_lane;
					const int source_block = input_crt_n(n3, n32);
					const int source_chunk = source_block / 8;
					const int chunk_role = (source_chunk - group) / 4;
					const int source_branch_pos = 4*source_block;

					for (int lane = 0; lane < 4; lane++)
					{
						const int source_pos = branch_start + source_branch_pos + lane;
						const int low_input_pos = source_branch_pos + lane;
						const int high_input_pos = low_input_pos + NTRUPLUS_N / 2;
						const int ld4_offset =
							dft3_ld4_stage_coeff_offset(branch, group, n3, n32_lane, lane);
						const int ld3_offset =
							dft3_ld3_stage_coeff_offset(branch, lane, group, n32_lane, n3);
						const int stage_order = ld4_offset;

						fprintf(fp,
						        "%d,%d,%d,%d,%d,%d,%d,"
						        "%s,%d,%d,%d,%d,%d,%d,"
						        "%d,%d,%s,%s,"
						        "%d,%d,%d,"
						        "top_split_then_twist_then_store_dft3_input,"
						        "a[%d..%d],a[%d..%d],%d,"
						        "tmp_ld4[branch%d][group%d][n3%d][n32_lane%d][q%d],"
						        "%d,%d,ld4_tmp_ld4_branch%d_group%d_n3%d,%s_q%d_vlane%d,"
						        "tmp_ld3[branch%d][q%d][group%d][n32_lane%d][n3%d],"
						        "%d,%d,ld3_tmp_ld3_branch%d_q%d_group%d,%s_vlane%d,"
						        "LD4_layout_is_recommended_for_four_quartic_lanes;LD3_layout_is_alternative_per_quartic_lane\n",
						        stage_order,
						        branch,
						        group,
						        n3,
						        n32,
						        n32_lane,
						        lane,
						        chunk_role_name(chunk_role),
						        source_chunk,
						        source_block,
						        source_branch_pos + lane,
						        source_pos,
						        low_input_pos,
						        high_input_pos,
						        NTRUPLUS_ZETA_TOP_SPLIT,
						        normal_from_mont(NTRUPLUS_ZETA_TOP_SPLIT),
						        top_split_formula_for_branch(branch),
						        twist_name,
						        source_block,
						        twist[source_block],
						        normal_from_mont(twist[source_block]),
						        32*source_chunk,
						        32*source_chunk + 31,
						        32*source_chunk + NTRUPLUS_N / 2,
						        32*source_chunk + NTRUPLUS_N / 2 + 31,
						        source_block & 7,
						        branch,
						        group,
						        n3,
						        n32_lane,
						        lane,
						        ld4_offset,
						        2*ld4_offset,
						        branch,
						        group,
						        n3,
						        dft3_input_name(n3),
						        lane,
						        n32_lane,
						        branch,
						        lane,
						        group,
						        n32_lane,
						        n3,
						        ld3_offset,
						        2*ld3_offset,
						        branch,
						        lane,
						        group,
						        dft3_input_name(n3),
						        n32_lane);
					}
				}
			}
		}
	}

	fclose(fp);
}

static void NTRUPLUS_UNUSED dump_gt_stage_top_split_plan(void)
{
	FILE *fp = fopen("build/gt_stage_top_split_plan.csv", "w");

	if (fp == NULL)
	{
		perror("build/gt_stage_top_split_plan.csv");
		return;
	}

	fprintf(fp,
	        "pair_i,low_input_pos,high_input_pos,top_zeta_mont,"
	        "top_zeta_normal,asm_loop_iter,asm_lane,asm_low_load_register,"
	        "asm_high_load_register,asm_temp_register,branch0_output_pos,"
	        "branch0_output_register,branch0_formula,branch1_output_pos,"
	        "branch1_output_register,branch1_formula,notes\n");

	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		const int chunk = i / 64;
		const int loop_iter = (i % 64) / 8;
		const int lane = i & 7;
		const int low_reg = 4 + chunk;
		const int high_reg = 10 + chunk;
		const int temp_reg = 16 + chunk;

		fprintf(fp,
		        "%d,%d,%d,%d,%d,%d,%d,v%d,v%d,v%d,%d,v%d,"
		        "t=fqmul_zeta_top_a[%d];r[%d]=a[%d]+t,%d,v%d,"
		        "t=fqmul_zeta_top_a[%d];r[%d]=a[%d]+a[%d]-t,"
		        "matches_original_ntt_s_level0_load_shape\n",
		        i,
		        i,
		        i + NTRUPLUS_N / 2,
		        NTRUPLUS_ZETA_TOP_SPLIT,
		        normal_from_mont(NTRUPLUS_ZETA_TOP_SPLIT),
		        loop_iter,
		        lane,
		        low_reg,
		        high_reg,
		        temp_reg,
		        i,
		        low_reg,
		        i + NTRUPLUS_N / 2,
		        i,
		        i,
		        i + NTRUPLUS_N / 2,
		        high_reg,
		        i + NTRUPLUS_N / 2,
		        i + NTRUPLUS_N / 2,
		        i,
		        i + NTRUPLUS_N / 2);
	}

	fclose(fp);
}

static void NTRUPLUS_UNUSED dump_gt_stage_twist_plan(void)
{
	FILE *fp = fopen("build/gt_stage_twist_plan.csv", "w");

	if (fp == NULL)
	{
		perror("build/gt_stage_twist_plan.csv");
		return;
	}

	fprintf(fp,
	        "branch,base_F,block_k,position_start,position_end,lane_count,"
	        "exponent,twist_table,twist_index,twist_mont,twist_normal,"
	        "operation,expanded_positions,notes\n");

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int base = branch == 0 ? 2 : 22;
		const int16_t *twist = branch == 0 ? twist_branch0 : twist_branch1;
		const char *twist_name = branch == 0 ? "twist_branch0" : "twist_branch1";

		for (int k = 0; k < 96; k++)
		{
			const int pos = branch_start + 4*k;

			fprintf(fp,
			        "%d,%d,%d,%d,%d,4,-%d,%s,%d,%d,%d,"
			        "r[%d..%d]=r[%d..%d]*%d^(-%d),"
			        "r[%d]|r[%d]|r[%d]|r[%d],"
			        "same_twist_for_four_quartic_lanes\n",
			        branch,
			        base,
			        k,
			        pos,
			        pos + 3,
			        k,
			        twist_name,
			        k,
			        twist[k],
			        normal_from_mont(twist[k]),
			        pos,
			        pos + 3,
			        pos,
			        pos + 3,
			        base,
			        k,
			        pos,
			        pos + 1,
			        pos + 2,
			        pos + 3);
		}
	}

	fclose(fp);
}

static void NTRUPLUS_UNUSED dump_gt_stage_dft3_plan(void)
{
	FILE *fp = fopen("build/gt_stage_dft3_plan.csv", "w");

	if (fp == NULL)
	{
		perror("build/gt_stage_dft3_plan.csv");
		return;
	}

	fprintf(fp,
	        "branch,quartic_lane,n32,vector_group,register_lane,"
	        "matrix_lane_stream,x0_offsets_8,x1_offsets_8,x2_offsets_8,"
	        "x0_pos,x0_block,x0_twist_mont,x0_twist_normal,"
	        "x1_pos,x1_block,x1_twist_mont,x1_twist_normal,"
	        "x2_pos,x2_block,x2_twist_mont,x2_twist_normal,"
	        "input_pack_registers,d_mont_constant,dft_y0_formula,"
	        "dft_y1_formula,dft_y2_formula,y0_row_k3,y1_row_k3,y2_row_k3,"
	        "notes\n");

	for (int branch = 0; branch < 2; branch++)
	{
		const int16_t *twist = branch == 0 ? twist_branch0 : twist_branch1;

		for (int lane = 0; lane < 4; lane++)
		{
			for (int n32 = 0; n32 < 32; n32++)
			{
				char matrix_lane_stream[80];
				char x0_offsets[128];
				char x1_offsets[128];
				char x2_offsets[128];
				const int x0_block = input_crt_n(0, n32);
				const int x1_block = input_crt_n(1, n32);
				const int x2_block = input_crt_n(2, n32);
				const int x0_pos = physical_pos_for_input_crt(branch, lane, 0, n32);
				const int x1_pos = physical_pos_for_input_crt(branch, lane, 1, n32);
				const int x2_pos = physical_pos_for_input_crt(branch, lane, 2, n32);
				const int vector_group = n32 / 8;

				format_branch_lane_stream(matrix_lane_stream, branch, lane);
				format_dft3_offset_group(x0_offsets, branch, lane, 0, vector_group);
				format_dft3_offset_group(x1_offsets, branch, lane, 1, vector_group);
				format_dft3_offset_group(x2_offsets, branch, lane, 2, vector_group);

				fprintf(fp,
				        "%d,%d,%d,%d,%d,"
				        "\"%s\",\"%s\",\"%s\",\"%s\","
				        "%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,"
				        "v4=x0_v5=x1_v6=x2,%d,"
				        "y0=x0+x1+x2,"
				        "y1=x0-x2+omega3*(x1-x2),"
				        "y2=x0-x1-omega3*(x1-x2),"
				        "0,1,2,one_multiply_dft3_column\n",
				        branch,
				        lane,
				        n32,
				        vector_group,
				        n32 & 7,
				        matrix_lane_stream,
				        x0_offsets,
				        x1_offsets,
				        x2_offsets,
				        x0_pos,
				        x0_block,
				        twist[x0_block],
				        normal_from_mont(twist[x0_block]),
				        x1_pos,
				        x1_block,
				        twist[x1_block],
				        normal_from_mont(twist[x1_block]),
				        x2_pos,
				        x2_block,
				        twist[x2_block],
				        normal_from_mont(twist[x2_block]),
				        GT96_OMEGA3);
			}
		}
	}

	fclose(fp);
}

static void dump_gt_stage_ntt32_input_plan(void)
{
	FILE *fp = fopen("build/gt_stage_ntt32_input_plan.csv", "w");

	if (fp == NULL)
	{
		perror("build/gt_stage_ntt32_input_plan.csv");
		return;
	}

	fprintf(fp,
	        "example_scope,gt_matrix,gt_matrix_lane,branch,quartic_lane,"
	        "phase3_row_k3,phase3_col_k32,phase3_value,phase3_formula,"
	        "phase3_q_register,phase3_q_lane,phase3_q_contents,"
	        "phase3_row_base_coeff_index,phase3_memory_index,"
	        "phase3_byte_offset,ntt32_load_instruction,"
	        "ntt32_load_byte_offset_from_row_base,ntt32_loaded_lane,"
	        "ntt32_work_index,bitrev_output_index,"
	        "x0_top_split_output_index,x0_block,x0_original_low_index,"
	        "x0_original_high_index,x0_source,"
	        "x1_top_split_output_index,x1_block,x1_original_low_index,"
	        "x1_original_high_index,x1_source,"
	        "x2_top_split_output_index,x2_block,x2_original_low_index,"
	        "x2_original_high_index,x2_source,"
	        "operation,notes\n");

	for (int branch = 0; branch < 2; branch++)
	{
		for (int lane = 0; lane < 4; lane++)
		{
			char matrix_name[32];
			const int packed_lane = 4*branch + lane;

			format_gt_matrix_name(matrix_name, branch, lane);

			for (int k3 = 0; k3 < 3; k3++)
			{
				for (int k32 = 0; k32 < 32; k32++)
				{
					const int work = k32;
					const int bitrev_out = (int)bitreverse5((unsigned)k32);
					const int pos0 = physical_pos_for_input_crt(branch, lane, 0, k32);
					const int pos1 = physical_pos_for_input_crt(branch, lane, 1, k32);
					const int pos2 = physical_pos_for_input_crt(branch, lane, 2, k32);
					const int block0 = input_crt_n(0, k32);
					const int block1 = input_crt_n(1, k32);
					const int block2 = input_crt_n(2, k32);
					const int low0 = 4*block0 + lane;
					const int low1 = 4*block1 + lane;
					const int low2 = 4*block2 + lane;
					const int high0 = low0 + NTRUPLUS_N / 2;
					const int high1 = low1 + NTRUPLUS_N / 2;
					const int high2 = low2 + NTRUPLUS_N / 2;
					const int phase3_row_base = k3 * 32 * 8;
					const int phase3_q_base = (k3 * 32 + k32) * 8;
					const int phase3_index = phase3_q_base + packed_lane;
					char q_contents[256];
					char source0[128];
					char source1[128];
					char source2[128];
					char load_instruction[96];
					char loaded_lane[48];
					char operation[128];
					const char *example =
						(branch == 0 && lane == 0 && k3 == 0) ?
						"first_matrix_first_row" : "all_matrices_all_rows";

					format_phase3_q_contents(q_contents, k3, k32);
					format_phase3_source(source0, branch, lane, 0, k32);
					format_phase3_source(source1, branch, lane, 1, k32);
					format_phase3_source(source2, branch, lane, 2, k32);
					snprintf(load_instruction, sizeof(load_instruction),
					         "ldr Q<w%02d_s0> [row_base #16*%d]",
					         work,
					         work);
					snprintf(loaded_lane, sizeof(loaded_lane),
					         "V<w%02d_s0>.h[%d]",
					         work,
					         packed_lane);
					snprintf(operation, sizeof(operation),
					         "%s=%s[%d]_goes_to_work[%d]_lane%d",
					         loaded_lane,
					         dft3_output_name(k3),
					         k32,
					         work,
					         packed_lane);

					fprintf(fp,
					        "%s,%s,%d,%d,%d,"
					        "%d,%d,%s,%s,"
					        "Q<w%02d_s0>,%d,%s,"
					        "%d,%d,%d,%s,"
					        "%d,%s,"
					        "%d,%d,"
					        "%d,%d,%d,%d,%s,"
					        "%d,%d,%d,%d,%s,"
					        "%d,%d,%d,%d,%s,"
					        "%s,"
					        "phase3_memory_is_row_major_k3_then_k32_with_8_packed_GT_matrices;ntt32_loads_one_Q_per_k32\n",
					        example,
					        matrix_name,
					        packed_lane,
					        branch,
					        lane,
					        k3,
					        k32,
					        dft3_output_name(k3),
					        dft3_output_formula(k3),
					        work,
					        packed_lane,
					        q_contents,
					        phase3_row_base,
					        phase3_index,
					        phase3_index * 2,
					        load_instruction,
					        work * 16,
					        loaded_lane,
					        work,
					        bitrev_out,
					        pos0,
					        block0,
					        low0,
					        high0,
					        source0,
					        pos1,
					        block1,
					        low1,
					        high1,
					        source1,
					        pos2,
					        block2,
					        low2,
					        high2,
					        source2,
					        operation);
				}
			}
		}
	}

	fclose(fp);
}

static void dump_gt_register_pack_plan(void)
{
	FILE *fp = fopen("build/gt_register_pack_plan.csv", "w");

	if (fp == NULL)
	{
		perror("build/gt_register_pack_plan.csv");
		return;
	}

	fprintf(fp,
	        "phase,branch,quartic_lane,vector_group,register,register_lane,"
	        "physical_pos,branch_pos,block_k,twist_index,input_n3,input_n32,"
	        "dft_output_k3,ntt32_stage,ntt32_len,ntt32_work_index,"
	        "ntt32_input_k32,ntt32_role,pair_lo_index,pair_hi_index,"
	        "twiddle_power,twiddle_mont,twiddle_normal,"
	        "source_pos_n3_0,source_pos_n3_1,source_pos_n3_2,"
	        "source_twist_n3_0,source_twist_n3_1,source_twist_n3_2,notes\n");

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int lane = 0; lane < 4; lane++)
		{
			for (int n32_base = 0; n32_base < 32; n32_base += 8)
			{
				const int vector_group = n32_base / 8;

				/*
				 * Proposed DFT3 input register pack:
				 *   v4 = mat[0][n32_base .. n32_base+7]
				 *   v5 = mat[1][n32_base .. n32_base+7]
				 *   v6 = mat[2][n32_base .. n32_base+7]
				 */
				for (int n3 = 0; n3 < 3; n3++)
				{
					for (int vlane = 0; vlane < 8; vlane++)
					{
						const int n32 = n32_base + vlane;
						const int block = input_crt_n(n3, n32);
						const int pos = branch_start + 4*block + lane;

						fprintf(fp,
						        "input_crt_pack,%d,%d,%d,v%d,%d,"
						        "%d,%d,%d,%d,%d,%d,"
						        "-1,-1,-1,-1,-1,source,-1,-1,"
						        "0,%d,%d,"
						        "-1,-1,-1,-1,-1,-1,"
						        "physical_source_then_twist_by_twist_index\n",
						        branch,
						        lane,
						        vector_group,
						        4 + n3,
						        vlane,
						        pos,
						        pos - branch_start,
						        block,
						        block,
						        n3,
						        n32,
						        NTRUPLUS_R,
						        normal_from_mont(NTRUPLUS_R));
					}
				}

				/*
				 * After one-multiply DFT3, the same three registers can be
				 * interpreted as k3 rows.  Each output lane is a linear
				 * combination of the three physical inputs listed below.
				 */
				for (int k3 = 0; k3 < 3; k3++)
				{
					for (int vlane = 0; vlane < 8; vlane++)
					{
						const int n32 = n32_base + vlane;
						const int pos0 = physical_pos_for_input_crt(branch, lane, 0, n32);
						const int pos1 = physical_pos_for_input_crt(branch, lane, 1, n32);
						const int pos2 = physical_pos_for_input_crt(branch, lane, 2, n32);
						const int tw0 = input_crt_n(0, n32);
						const int tw1 = input_crt_n(1, n32);
						const int tw2 = input_crt_n(2, n32);

						fprintf(fp,
						        "dft3_output_pack,%d,%d,%d,v%d,%d,"
						        "-1,-1,-1,-1,-1,%d,"
						        "%d,-1,-1,-1,-1,dft_output,-1,-1,"
						        "0,%d,%d,"
						        "%d,%d,%d,%d,%d,%d,"
						        "linear_combination_of_three_input_crt_sources\n",
						        branch,
						        lane,
						        vector_group,
						        4 + k3,
						        vlane,
						        n32,
						        k3,
						        NTRUPLUS_R,
						        normal_from_mont(NTRUPLUS_R),
						        pos0,
						        pos1,
						        pos2,
						        tw0,
						        tw1,
						        tw2);
					}
				}
			}

			for (int k3 = 0; k3 < 3; k3++)
			{
				/*
				 * Proposed 32-point row input pack for the CT kernel:
				 *   v4 = work[0..7], v5 = work[8..15],
				 *   v6 = work[16..23], v7 = work[24..31].
				 *
				 * work[k32] receives the DFT3 output at column k32.  The
				 * complete CT kernel leaves the row in bit-reversed
				 * frequency order:
				 *
				 *   out[bitreverse5(k32)] = NTT32(row)[k32].
				 */
				for (int work = 0; work < 32; work++)
				{
					const int input_k32 = work;
					const int reg = 4 + work / 8;
					const int vlane = work & 7;
					const int pos0 = physical_pos_for_input_crt(branch, lane, 0, input_k32);
					const int pos1 = physical_pos_for_input_crt(branch, lane, 1, input_k32);
					const int pos2 = physical_pos_for_input_crt(branch, lane, 2, input_k32);
					const int tw0 = input_crt_n(0, input_k32);
					const int tw1 = input_crt_n(1, input_k32);
					const int tw2 = input_crt_n(2, input_k32);

					fprintf(fp,
					        "ntt32_initial_natural_pack,%d,%d,%d,v%d,%d,"
					        "-1,-1,-1,-1,-1,%d,"
					        "%d,0,32,%d,%d,state,-1,-1,"
					        "0,%d,%d,"
					        "%d,%d,%d,%d,%d,%d,"
					        "natural_input_for_complete_ct_ntt32_bitrev_output\n",
					        branch,
					        lane,
					        work / 8,
					        reg,
					        vlane,
					        input_k32,
					        k3,
					        work,
					        input_k32,
					        NTRUPLUS_R,
					        normal_from_mont(NTRUPLUS_R),
					        pos0,
					        pos1,
					        pos2,
					        tw0,
					        tw1,
					        tw2);
				}

				for (unsigned stage = 1; stage <= 5; stage++)
				{
					const unsigned distance = 1U << (5 - stage);
					const unsigned len = distance * 2;

					for (unsigned start = 0; start < 32; start += len)
					{
						for (unsigned j = 0; j < distance; j++)
						{
							const unsigned lo = start + j;
							const unsigned hi = lo + distance;
							const unsigned power = ntt32_ct_twiddle_power(stage, lo);
							const int16_t twiddle = gt96_omega32_powers[power];
							const int lo_reg = 4 + (int)lo / 8;
							const int hi_reg = 4 + (int)hi / 8;

							fprintf(fp,
							        "ntt32_butterfly_operand,%d,%d,%d,v%d,%u,"
							        "-1,-1,-1,-1,-1,-1,"
							        "%d,%u,%u,%u,-1,lo,%u,%u,"
							        "%u,%d,%d,"
							        "-1,-1,-1,-1,-1,-1,"
							        "low_operand_for_ct_butterfly_t=fqmul_high_twiddle\n",
							        branch,
							        lane,
							        (int)lo / 8,
							        lo_reg,
							        lo & 7U,
							        k3,
							        stage,
							        len,
							        lo,
							        lo,
							        hi,
							        power,
							        twiddle,
							        normal_from_mont(twiddle));

							fprintf(fp,
							        "ntt32_butterfly_operand,%d,%d,%d,v%d,%u,"
							        "-1,-1,-1,-1,-1,-1,"
							        "%d,%u,%u,%u,-1,hi,%u,%u,"
							        "%u,%d,%d,"
							        "-1,-1,-1,-1,-1,-1,"
							        "ct_high_operand_is_multiplied_by_twiddle_then_low_minus_t\n",
							        branch,
							        lane,
							        (int)hi / 8,
							        hi_reg,
							        hi & 7U,
							        k3,
							        stage,
							        len,
							        hi,
							        lo,
							        hi,
							        power,
							        twiddle,
							        normal_from_mont(twiddle));
						}
					}
				}
			}
		}
	}

	fclose(fp);
}

/*
 * NEON planning view for one 32-point row.
 *
 * This is not a new mathematical mapping.  It assumes the natural-order row is
 * packed contiguously before the radix-2 CT kernel as:
 *
 *   v4 = work[0..7], v5 = work[8..15],
 *   v6 = work[16..23], v7 = work[24..31].
 *
 * The dump classifies each CT butterfly pair by register/lane shape.  That is
 * the useful signal for ASM planning: same-register pairs require a shuffle or
 * half-vector split, while cross-register same-lane pairs can be handled by
 * vector-wise butterfly instructions directly.
 */
static const char *ntt32_reg_for_index(int index)
{
	static const char *regs[4] = { "v4", "v5", "v6", "v7" };

	return regs[index / 8];
}

static void NTRUPLUS_UNUSED dump_full_fused_gt_plan(void)
{
	FILE *fp = fopen("build/full_fused_gt_plan.csv", "w");

	if (fp == NULL)
	{
		perror("build/full_fused_gt_plan.csv");
		return;
	}

	fprintf(fp,
	        "branch,quartic_lane,top_split_output_pos,top_split_branch_pos,"
	        "top_split_pair_index,top_split_low_input_pos,top_split_high_input_pos,"
	        "top_split_formula,source_block_k,source_n3,source_n32,"
	        "source_vector_group,source_input_register,source_input_register_lane,"
	        "twist_table,twist_index,twist_mont,twist_normal,"
	        "dft3_column,dft3_output_k3,dft3_factor_exp,dft3_factor_mont,"
	        "dft3_factor_normal,dft3_one_mul_role,source_pos_n3_0,"
	        "source_pos_n3_1,source_pos_n3_2,source_twist_n3_0,"
	        "source_twist_n3_1,source_twist_n3_2,ntt32_input_k32,"
	        "ntt32_input_work_index,ntt32_input_register,ntt32_input_register_lane,"
	        "ntt32_input_vector_group,ntt32_bitrev_output_index,"
	        "ntt32_bitrev_output_register,ntt32_bitrev_output_lane,notes\n");

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int16_t *twist = branch == 0 ? twist_branch0 : twist_branch1;
		const char *twist_name = branch == 0 ? "twist_branch0" : "twist_branch1";

		for (int lane = 0; lane < 4; lane++)
		{
			for (int source_n32 = 0; source_n32 < 32; source_n32++)
			{
				const int vector_group = source_n32 / 8;
				const int source_pos_n3_0 =
					physical_pos_for_input_crt(branch, lane, 0, source_n32);
				const int source_pos_n3_1 =
					physical_pos_for_input_crt(branch, lane, 1, source_n32);
				const int source_pos_n3_2 =
					physical_pos_for_input_crt(branch, lane, 2, source_n32);
				const int source_twist_n3_0 = input_crt_n(0, source_n32);
				const int source_twist_n3_1 = input_crt_n(1, source_n32);
				const int source_twist_n3_2 = input_crt_n(2, source_n32);

				for (int source_n3 = 0; source_n3 < 3; source_n3++)
				{
					const int block = input_crt_n(source_n3, source_n32);
					const int physical_pos = branch_start + 4*block + lane;
					const int branch_pos = physical_pos - branch_start;
					const int low_input_pos = branch_pos;
					const int high_input_pos = branch_pos + NTRUPLUS_N / 2;
					const int source_input_reg = 4 + source_n3;
					const int source_input_lane = source_n32 & 7;

					for (int output_k3 = 0; output_k3 < 3; output_k3++)
					{
						const int exp = (source_n3 * output_k3) % 3;
						const int16_t dft_factor = dft3_twiddle_mont(exp);
						const int work_index = source_n32;
						const int bitrev_out = (int)bitreverse5((unsigned)source_n32);
						const int ntt_reg_index = 4 + work_index / 8;
						const int ntt_lane = work_index & 7;

						fprintf(fp,
						        "%d,%d,%d,%d,%d,%d,%d,%s,"
						        "%d,%d,%d,%d,v%d,%d,%s,%d,%d,%d,"
						        "%d,%d,%d,%d,%d,%s,%d,%d,%d,%d,%d,%d,"
						        "%d,%d,%s,%d,%d,%d,%s,%d,"
						        "top_split_then_twist_then_dft3_contribution_then_complete_ntt32;bitrev_columns_are_physical_output_order\n",
						        branch,
						        lane,
						        physical_pos,
						        branch_pos,
						        branch_pos,
						        low_input_pos,
						        high_input_pos,
						        top_split_formula_for_branch(branch),
						        block,
						        source_n3,
						        source_n32,
						        vector_group,
						        source_input_reg,
						        source_input_lane,
						        twist_name,
						        block,
						        twist[block],
						        normal_from_mont(twist[block]),
						        source_n32,
						        output_k3,
						        exp,
						        dft_factor,
						        normal_from_mont(dft_factor),
						        dft3_one_mul_role(source_n3, output_k3),
						        source_pos_n3_0,
						        source_pos_n3_1,
						        source_pos_n3_2,
						        source_twist_n3_0,
						        source_twist_n3_1,
						        source_twist_n3_2,
						        source_n32,
						        work_index,
						        ntt32_reg_for_index(work_index),
						        ntt_lane,
						        ntt_reg_index - 4,
						        bitrev_out,
						        ntt32_reg_for_index(bitrev_out),
						        bitrev_out & 7);
					}
				}
			}
		}
	}

	fclose(fp);
}

static const char *ntt32_pair_shape(unsigned lo, unsigned hi)
{
	const unsigned lo_reg = lo / 8;
	const unsigned hi_reg = hi / 8;
	const unsigned lo_lane = lo & 7U;
	const unsigned hi_lane = hi & 7U;

	if (lo_reg != hi_reg && lo_lane == hi_lane)
	{
		return "cross_register_same_lane";
	}
	if (lo_reg == hi_reg && hi_lane == lo_lane + 1)
	{
		return "same_register_adjacent_lanes";
	}
	if (lo_reg == hi_reg && hi_lane == lo_lane + 2)
	{
		return "same_register_distance_2";
	}
	if (lo_reg == hi_reg && hi_lane == lo_lane + 4)
	{
		return "same_register_low_high_half";
	}

	return "irregular";
}

static const char *ntt32_shuffle_need(unsigned len)
{
	switch (len)
	{
	case 2:
		return "yes_even_odd_deinterleave";
	case 4:
		return "yes_lane_distance_2_shuffle";
	case 8:
		return "yes_half_vector_split";
	case 16:
	case 32:
		return "no_cross_register_same_lane";
	default:
		return "unknown";
	}
}

static const char *ntt32_vector_strategy(unsigned len)
{
	switch (len)
	{
	case 2:
		return "split_even_odd_lanes_per_register_then_reinterleave";
	case 4:
		return "group_lanes_0_1_vs_2_3_and_4_5_vs_6_7";
	case 8:
		return "split_each_register_into_low4_and_high4_halves";
	case 16:
		return "vector_butterflies_v4_vs_v5_and_v6_vs_v7";
	case 32:
		return "vector_butterflies_v4_vs_v6_and_v5_vs_v7";
	default:
		return "unknown";
	}
}

static void dump_ntt32_neon_plan(void)
{
	FILE *fp = fopen("build/ntt32_neon_plan.csv", "w");

	if (fp == NULL)
	{
		perror("build/ntt32_neon_plan.csv");
		return;
	}

	fprintf(fp,
	        "stage,len,step,start,j,lo_index,hi_index,lo_register,lo_lane,"
	        "hi_register,hi_lane,twiddle_power,twiddle_mont,twiddle_normal,"
	        "pair_shape,shuffle_need,vector_strategy,notes\n");

	for (unsigned stage = 1; stage <= 5; stage++)
	{
		const unsigned distance = 1U << (5 - stage);
		const unsigned len = distance * 2;
		const unsigned step = 32 / len;

		for (unsigned start = 0; start < 32; start += len)
		{
			for (unsigned j = 0; j < distance; j++)
			{
				const unsigned lo = start + j;
				const unsigned hi = lo + distance;
				const unsigned power = ntt32_ct_twiddle_power(stage, lo);
				const int16_t twiddle = gt96_omega32_powers[power];
				const char *notes = "ct_t_is_high_times_twiddle_low_plus_t_high_low_minus_t";

				if (power == 0)
				{
					notes = "ct_twiddle_is_montgomery_one_multiply_can_be_skipped";
				}

				fprintf(fp,
				        "%u,%u,%u,%u,%u,%u,%u,%s,%u,%s,%u,%u,%d,%d,"
				        "%s,%s,%s,%s\n",
				        stage,
				        len,
				        step,
				        start,
				        j,
				        lo,
				        hi,
				        ntt32_reg_for_index((int)lo),
				        lo & 7U,
				        ntt32_reg_for_index((int)hi),
				        hi & 7U,
				        power,
				        twiddle,
				        normal_from_mont(twiddle),
				        ntt32_pair_shape(lo, hi),
				        ntt32_shuffle_need(len),
				        ntt32_vector_strategy(len),
				        notes);
			}
		}
	}

	fclose(fp);
}

typedef struct
{
	int32_t min;
	int32_t max;
} bounds_t;

typedef struct
{
	const char *name;
	int reduce_dft_output;
	int reduce_ntt_input;
	int ntt_reduce_period;
} reduction_schedule_t;

static void bounds_init(bounds_t *b)
{
	b->min = INT_MAX;
	b->max = INT_MIN;
}

static void bounds_update(bounds_t *b, int32_t x)
{
	if (x < b->min)
	{
		b->min = x;
	}

	if (x > b->max)
	{
		b->max = x;
	}
}

static int exceeds_i16(const bounds_t *b)
{
	return b->min < INT16_MIN || b->max > INT16_MAX;
}

static int exceeds_centered_q(const bounds_t *b)
{
	const int centered_bound = NTRUPLUS_Q / 2;

	return b->min < -centered_bound || b->max > centered_bound;
}

static int32_t abs_i32(int32_t x)
{
	return x < 0 ? -x : x;
}

static int32_t max_abs_bound(const bounds_t *b)
{
	const int32_t lo = abs_i32(b->min);
	const int32_t hi = abs_i32(b->max);

	return lo > hi ? lo : hi;
}

static int ceil_div_i32(int32_t a, int32_t b)
{
	return (int)((a + b - 1) / b);
}

static int q_multiple_bound(const bounds_t *b)
{
	return ceil_div_i32(max_abs_bound(b), NTRUPLUS_Q);
}

static const char *range_class(const bounds_t *b)
{
	const int32_t max_abs = max_abs_bound(b);

	if (max_abs <= NTRUPLUS_Q / 2)
	{
		return "centered";
	}
	if (max_abs < NTRUPLUS_Q)
	{
		return "lt_1q";
	}
	if (max_abs < 2 * NTRUPLUS_Q)
	{
		return "lt_2q";
	}
	if (max_abs < 4 * NTRUPLUS_Q)
	{
		return "lt_4q";
	}
	if (max_abs < 8 * NTRUPLUS_Q)
	{
		return "lt_8q";
	}
	if (max_abs < 16 * NTRUPLUS_Q)
	{
		return "lt_16q";
	}

	return "ge_16q";
}

static int next_addsub_i16_safe(const bounds_t *b)
{
	const int32_t max_abs = max_abs_bound(b);

	return max_abs <= INT16_MAX / 2;
}

static int next_fqmul_montgomery_safe(const bounds_t *b)
{
	const int32_t max_abs = max_abs_bound(b);
	const int32_t max_mont_const_abs = NTRUPLUS_Q / 2;
	const int64_t product_bound = (int64_t)max_abs * max_mont_const_abs;
	const int64_t montgomery_input_bound = (int64_t)NTRUPLUS_Q * (1 << 15);

	return max_abs <= INT16_MAX && product_bound < montgomery_input_bound;
}

static bounds_t bounds_from_abs(int32_t bound)
{
	bounds_t b;

	b.min = -bound;
	b.max = bound;
	return b;
}

static int16_t centered_reduce_i32(int32_t a)
{
	int32_t r = a % NTRUPLUS_Q;

	if (r > NTRUPLUS_Q / 2)
	{
		r -= NTRUPLUS_Q;
	}
	else if (r < -NTRUPLUS_Q / 2)
	{
		r += NTRUPLUS_Q;
	}

	return (int16_t)r;
}

static int16_t trace_reduce_i32(int32_t a)
{
	if (a < INT16_MIN || a > INT16_MAX)
	{
		return centered_reduce_i32(a);
	}

	return barrett_reduce((int16_t)a);
}

static int32_t fqmul_wide(int32_t a, int16_t b)
{
	return montgomery_reduce(a * (int32_t)b);
}

static int should_reduce_stage(const reduction_schedule_t *schedule, int stage)
{
	if (schedule->ntt_reduce_period <= 0)
	{
		return stage == 5;
	}

	return (stage % schedule->ntt_reduce_period) == 0 || stage == 5;
}

static void trace_report(FILE *fp,
                         const char *case_name,
                         const char *schedule_name,
                         const char *phase,
                         int branch,
                         int lane,
                         int row_k3,
                         int stage,
                         unsigned len,
                         const char *policy,
                         bounds_t bounds)
{
	fprintf(fp,
	        "%s,%s,%s,%d,%d,%d,%d,%u,%s,%d,%d,%d,%d,%d,%d,%s,%d,%d\n",
	        case_name,
	        schedule_name,
	        phase,
	        branch,
	        lane,
	        row_k3,
	        stage,
	        len,
	        policy,
	        bounds.min,
	        bounds.max,
	        max_abs_bound(&bounds),
	        q_multiple_bound(&bounds),
	        exceeds_centered_q(&bounds),
	        exceeds_i16(&bounds),
	        range_class(&bounds),
	        next_addsub_i16_safe(&bounds),
	        next_fqmul_montgomery_safe(&bounds));
}

static uint32_t xorshift32(uint32_t *state)
{
	uint32_t x = *state;

	x ^= x << 13;
	x ^= x >> 17;
	x ^= x << 5;
	*state = x;
	return x;
}

static void fill_trace_case(const char *case_name, int16_t a[NTRUPLUS_N])
{
	if (case_name[0] == 'z')
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a[i] = 0;
		}
	}
	else if (case_name[0] == 'p')
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a[i] = NTRUPLUS_Q / 2;
		}
	}
	else if (case_name[0] == 'n')
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a[i] = -(NTRUPLUS_Q / 2);
		}
	}
	else if (case_name[0] == 'a')
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a[i] = (i & 1) ? -(NTRUPLUS_Q / 2) : NTRUPLUS_Q / 2;
		}
	}
	else if (case_name[0] == 'r' && case_name[1] == 'a')
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a[i] = (int16_t)(((i * 37 + i / 7) % NTRUPLUS_Q) - NTRUPLUS_Q / 2);
		}
	}
	else if (case_name[0] == 'r')
	{
		uint32_t seed = 0x12345678U;

		for (const char *p = case_name; *p != '\0'; p++)
		{
			seed = seed * 33U + (unsigned char)*p;
		}

		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			const uint32_t x = xorshift32(&seed);

			a[i] = (int16_t)((int)(x % (2U * NTRUPLUS_Q)) - NTRUPLUS_Q);
		}
	}
	else
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a[i] = 0;
		}
	}
}

static void trace_reduction_schedule(FILE *fp,
                                     const char *case_name,
                                     const int16_t a[NTRUPLUS_N],
                                     const reduction_schedule_t *schedule)
{
	int32_t branch_coeffs[NTRUPLUS_N];

	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		const int32_t t1 = fqmul(NTRUPLUS_ZETA_TOP_SPLIT,
		                         a[i + NTRUPLUS_N / 2]);

		branch_coeffs[i + NTRUPLUS_N / 2] = a[i] + a[i + NTRUPLUS_N / 2] - t1;
		branch_coeffs[i] = a[i] + t1;
	}

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int16_t *twist = branch == 0 ? twist_branch0 : twist_branch1;
		bounds_t top_bounds;

		bounds_init(&top_bounds);
		for (int i = 0; i < NTRUPLUS_N / 2; i++)
		{
			bounds_update(&top_bounds, branch_coeffs[branch_start + i]);
		}
		trace_report(fp, case_name, schedule->name, "top_split_raw",
		             branch, -1, -1, -1, 0, "no_reduce", top_bounds);

		for (int k = 0; k < 96; k++)
		{
			for (int lane = 0; lane < 4; lane++)
			{
				const int pos = branch_start + 4*k + lane;

				branch_coeffs[pos] = fqmul_wide(branch_coeffs[pos], twist[k]);
			}
		}

		for (int lane = 0; lane < 4; lane++)
		{
			int32_t mat[3][32];
			bounds_t twist_bounds;

			bounds_init(&twist_bounds);
			for (int k = 0; k < 96; k++)
			{
				bounds_update(&twist_bounds,
				              branch_coeffs[branch_start + 4*k + lane]);
			}
			trace_report(fp, case_name, schedule->name, "after_twist",
			             branch, lane, -1, -1, 0, "fqmul", twist_bounds);

			for (int n3 = 0; n3 < 3; n3++)
			{
				for (int n32 = 0; n32 < 32; n32++)
				{
					const int n = input_crt_n(n3, n32);

					mat[n3][n32] = branch_coeffs[branch_start + 4*n + lane];
				}
			}

			{
				bounds_t input_bounds;
				bounds_t d_raw_bounds;
				bounds_t t_bounds;
				bounds_t y_raw_bounds;
				bounds_t y_stored_bounds;

				bounds_init(&input_bounds);
				bounds_init(&d_raw_bounds);
				bounds_init(&t_bounds);
				bounds_init(&y_raw_bounds);
				bounds_init(&y_stored_bounds);

				for (int n3 = 0; n3 < 3; n3++)
				{
					for (int n32 = 0; n32 < 32; n32++)
					{
						bounds_update(&input_bounds, mat[n3][n32]);
					}
				}

				for (int n32 = 0; n32 < 32; n32++)
				{
					const int32_t x0 = mat[0][n32];
					const int32_t x1 = mat[1][n32];
					const int32_t x2 = mat[2][n32];
					const int32_t d_raw = x1 - x2;
					const int32_t d = trace_reduce_i32(d_raw);
					const int32_t t = fqmul_wide(d, GT96_OMEGA3);
					const int32_t y_raw[3] = {
						x0 + x1 + x2,
						x0 - x2 + t,
						x0 - x1 - t
					};

					bounds_update(&d_raw_bounds, d_raw);
					bounds_update(&t_bounds, t);

					for (int k3 = 0; k3 < 3; k3++)
					{
						bounds_update(&y_raw_bounds, y_raw[k3]);
						mat[k3][n32] = schedule->reduce_dft_output ?
							trace_reduce_i32(y_raw[k3]) :
							y_raw[k3];
						bounds_update(&y_stored_bounds, mat[k3][n32]);
					}
				}

				trace_report(fp, case_name, schedule->name, "gt_input_mat",
				             branch, lane, -1, -1, 0, "after_twist_gather",
				             input_bounds);
				trace_report(fp, case_name, schedule->name, "dft3_d_raw",
				             branch, lane, -1, -1, 0, "before_d_reduce",
				             d_raw_bounds);
				trace_report(fp, case_name, schedule->name, "dft3_t",
				             branch, lane, -1, -1, 0, "fqmul_omega3",
				             t_bounds);
				trace_report(fp, case_name, schedule->name, "dft3_y_raw",
				             branch, lane, -1, -1, 0, "before_optional_reduce",
				             y_raw_bounds);
				trace_report(fp, case_name, schedule->name, "dft3_y_stored",
				             branch, lane, -1, -1, 0,
				             schedule->reduce_dft_output ? "reduced" : "lazy",
				             y_stored_bounds);
			}

			for (int k3 = 0; k3 < 3; k3++)
			{
				int32_t row[32];
				bounds_t ntt_input_bounds;

				bounds_init(&ntt_input_bounds);
				for (unsigned i = 0; i < 32; i++)
				{
					row[i] = schedule->reduce_ntt_input ?
						trace_reduce_i32(mat[k3][i]) :
						mat[k3][i];
				}

				for (int i = 0; i < 32; i++)
				{
					bounds_update(&ntt_input_bounds, row[i]);
				}
				trace_report(fp, case_name, schedule->name, "ntt32_natural_input",
				             branch, lane, k3, 0, 1,
				             schedule->reduce_ntt_input ? "reduced" : "lazy",
				             ntt_input_bounds);

				for (unsigned stage = 1; stage <= 5; stage++)
				{
					const unsigned distance = 1U << (5 - stage);
					const unsigned len = distance * 2;
					const int reduce_stage = should_reduce_stage(schedule, (int)stage);
					bounds_t input_bounds;
					bounds_t fqmul_bounds;
					bounds_t raw_bounds;
					bounds_t stored_bounds;

					bounds_init(&input_bounds);
					bounds_init(&fqmul_bounds);
					bounds_init(&raw_bounds);
					bounds_init(&stored_bounds);

					for (int i = 0; i < 32; i++)
					{
						bounds_update(&input_bounds, row[i]);
					}

					for (unsigned start = 0; start < 32; start += len)
					{
						for (unsigned j = 0; j < distance; j++)
						{
							const unsigned lo = start + j;
							const unsigned hi = lo + distance;
							const unsigned power = ntt32_ct_twiddle_power(stage, lo);
							const int32_t u = row[lo];
							const int32_t v = row[hi];
							const int32_t t =
								fqmul_wide(v, gt96_omega32_powers[power]);
							const int32_t sum = u + t;
							const int32_t diff = u - t;

							bounds_update(&fqmul_bounds, t);
							bounds_update(&raw_bounds, sum);
							bounds_update(&raw_bounds, diff);

							row[lo] = reduce_stage ? trace_reduce_i32(sum) : sum;
							row[hi] = reduce_stage ? trace_reduce_i32(diff) : diff;
						}
					}

					for (int i = 0; i < 32; i++)
					{
						bounds_update(&stored_bounds, row[i]);
					}

					trace_report(fp, case_name, schedule->name, "ntt32_stage_input",
					             branch, lane, k3, stage, len, "before_butterfly",
					             input_bounds);
					trace_report(fp, case_name, schedule->name, "ntt32_stage_fqmul",
					             branch, lane, k3, (int)stage, len,
					             "ct_t_high_times_twiddle",
					             fqmul_bounds);
					trace_report(fp, case_name, schedule->name, "ntt32_stage_raw",
					             branch, lane, k3, stage, len, "before_optional_reduce",
					             raw_bounds);
					trace_report(fp, case_name, schedule->name, "ntt32_stage_stored",
					             branch, lane, k3, stage, len,
					             reduce_stage ? "reduced" : "lazy",
					             stored_bounds);
				}
			}
		}
	}
}

static void NTRUPLUS_UNUSED dump_reduction_bound_trace(void)
{
	static const char *cases[] = {
		"zero",
		"positive_half_q",
		"negative_half_q",
		"alternating_half_q",
		"ramp",
		"random_0",
		"random_1",
		"random_2"
	};
	static const reduction_schedule_t schedules[] = {
		{ "current_ref", 1, 1, 1 },
		{ "defer_dft_to_ntt_input", 0, 1, 1 },
		{ "defer_dft_no_ntt_input_reduce", 0, 0, 1 },
		{ "ntt_reduce_every_2_stages", 1, 1, 2 },
		{ "ntt_reduce_final_only", 1, 1, 0 },
	};
	FILE *fp = fopen("build/reduction_bound_trace.csv", "w");

	if (fp == NULL)
	{
		perror("build/reduction_bound_trace.csv");
		return;
	}

	fprintf(fp,
	        "case,schedule,phase,branch,lane,row_k3,stage,len,policy,"
	        "min_value,max_value,max_abs,ceil_abs_over_q,"
	        "exceeds_centered_q,exceeds_int16,range_class,"
	        "next_addsub_i16_safe,next_fqmul_montgomery_safe\n");

	for (unsigned c = 0; c < sizeof(cases) / sizeof(cases[0]); c++)
	{
		int16_t a[NTRUPLUS_N];

		fill_trace_case(cases[c], a);

		for (unsigned s = 0; s < sizeof(schedules) / sizeof(schedules[0]); s++)
		{
			trace_reduction_schedule(fp, cases[c], a, &schedules[s]);
		}
	}

	fclose(fp);
}

static void static_bound_report(FILE *fp,
                                const char *input_model,
                                const char *schedule_name,
                                const char *phase,
                                int stage,
                                unsigned len,
                                const char *policy,
                                int32_t input_bound,
                                int32_t fqmul_input_bound,
                                int32_t output_bound,
                                const char *notes)
{
	const bounds_t out = bounds_from_abs(output_bound);
	const bounds_t fqmul_in = bounds_from_abs(fqmul_input_bound);

	fprintf(fp,
	        "%s,%s,%s,%d,%u,%s,%d,%d,%d,%d,%d,%d,%d,%s,%d,%d,%s\n",
	        input_model,
	        schedule_name,
	        phase,
	        stage,
	        len,
	        policy,
	        input_bound,
	        fqmul_input_bound,
	        output_bound,
	        max_abs_bound(&out),
	        q_multiple_bound(&out),
	        exceeds_centered_q(&out),
	        exceeds_i16(&out),
	        range_class(&out),
	        next_addsub_i16_safe(&out),
	        next_fqmul_montgomery_safe(&fqmul_in),
	        notes);
}

static void NTRUPLUS_UNUSED dump_reduction_static_bounds(void)
{
	static const reduction_schedule_t schedules[] = {
		{ "current_ref", 1, 1, 1 },
		{ "defer_dft_to_ntt_input", 0, 1, 1 },
		{ "defer_dft_no_ntt_input_reduce", 0, 0, 1 },
		{ "ntt_reduce_every_2_stages", 1, 1, 2 },
		{ "ntt_reduce_final_only", 1, 1, 0 },
	};
	static const struct
	{
		const char *name;
		int32_t input_bound;
	} input_models[] = {
		{ "centered_input_abs_le_q_over_2", NTRUPLUS_Q / 2 },
		{ "signed_modq_input_abs_lt_q", NTRUPLUS_Q - 1 },
	};
	FILE *fp = fopen("build/reduction_static_bounds.csv", "w");

	if (fp == NULL)
	{
		perror("build/reduction_static_bounds.csv");
		return;
	}

	fprintf(fp,
	        "input_model,schedule,phase,stage,len,policy,"
	        "input_bound_abs,fqmul_input_bound_abs,output_bound_abs,"
	        "max_abs,ceil_abs_over_q,exceeds_centered_q,exceeds_int16,"
	        "range_class,next_addsub_i16_safe,next_fqmul_montgomery_safe,"
	        "notes\n");

	for (unsigned m = 0; m < sizeof(input_models) / sizeof(input_models[0]); m++)
	{
		const int32_t in = input_models[m].input_bound;
		const int32_t fqmul_out = NTRUPLUS_Q - 1;
		const int32_t centered = NTRUPLUS_Q / 2;
		const int32_t top_branch0 = in + fqmul_out;
		const int32_t top_branch1 = 2*in + fqmul_out;
		const int32_t top_bound = top_branch0 > top_branch1 ?
			top_branch0 : top_branch1;
		const int32_t twist_bound = fqmul_out;
		const int32_t dft_d_raw_bound = 2*twist_bound;
		const int32_t dft_t_bound = fqmul_out;
		const int32_t dft_y_raw_bound = 3*twist_bound;

		for (unsigned s = 0; s < sizeof(schedules) / sizeof(schedules[0]); s++)
		{
			const reduction_schedule_t *schedule = &schedules[s];
			int32_t dft_stored_bound;
			int32_t row_bound;

			static_bound_report(fp,
			                    input_models[m].name,
			                    schedule->name,
			                    "top_split_raw",
			                    -1,
			                    0,
			                    "no_reduce",
			                    in,
			                    in,
			                    top_bound,
			                    "r0=a0+t1_and_r1=a0+a1-t1");
			static_bound_report(fp,
			                    input_models[m].name,
			                    schedule->name,
			                    "after_twist",
			                    -1,
			                    0,
			                    "fqmul",
			                    top_bound,
			                    top_bound,
			                    twist_bound,
			                    "twist_fqmul_reduces_to_montgomery_output_range");
			static_bound_report(fp,
			                    input_models[m].name,
			                    schedule->name,
			                    "dft3_d_raw",
			                    -1,
			                    0,
			                    "before_d_reduce",
			                    twist_bound,
			                    twist_bound,
			                    dft_d_raw_bound,
			                    "x1-x2_before_barrett_reduce");
			static_bound_report(fp,
			                    input_models[m].name,
			                    schedule->name,
			                    "dft3_t",
			                    -1,
			                    0,
			                    "fqmul_omega3",
			                    centered,
			                    centered,
			                    dft_t_bound,
			                    "d_is_centered_before_fqmul");
			static_bound_report(fp,
			                    input_models[m].name,
			                    schedule->name,
			                    "dft3_y_raw",
			                    -1,
			                    0,
			                    "before_optional_reduce",
			                    twist_bound,
			                    twist_bound,
			                    dft_y_raw_bound,
			                    "x0+x1+x2_or_x0-xi+t");

			dft_stored_bound = schedule->reduce_dft_output ?
				centered : dft_y_raw_bound;
			static_bound_report(fp,
			                    input_models[m].name,
			                    schedule->name,
			                    "dft3_y_stored",
			                    -1,
			                    0,
			                    schedule->reduce_dft_output ? "reduced" : "lazy",
			                    dft_y_raw_bound,
			                    dft_y_raw_bound,
			                    dft_stored_bound,
			                    "input_to_ct_ntt32_before_optional_reduce");

			row_bound = schedule->reduce_ntt_input ? centered : dft_stored_bound;
			static_bound_report(fp,
			                    input_models[m].name,
			                    schedule->name,
			                    "ntt32_natural_input",
			                    0,
			                    1,
			                    schedule->reduce_ntt_input ? "reduced" : "lazy",
			                    dft_stored_bound,
			                    dft_stored_bound,
			                    row_bound,
			                    "work_natural_input_bound");

			for (unsigned stage = 1; stage <= 5; stage++)
			{
				const unsigned distance = 1U << (5 - stage);
				const unsigned len = distance * 2;
				const int reduce_stage = should_reduce_stage(schedule, (int)stage);
				const int32_t raw_bound = row_bound + fqmul_out;
				const int32_t stored_bound = reduce_stage ? centered : raw_bound;

				static_bound_report(fp,
				                    input_models[m].name,
				                    schedule->name,
				                    "ntt32_stage_raw",
				                    (int)stage,
				                    len,
				                    "before_optional_reduce",
				                    row_bound,
				                    row_bound,
				                    raw_bound,
				                    "ct_outputs_are_low_plus_t_and_low_minus_t");
				static_bound_report(fp,
				                    input_models[m].name,
				                    schedule->name,
				                    "ntt32_stage_stored",
				                    (int)stage,
				                    len,
				                    reduce_stage ? "reduced" : "lazy",
				                    raw_bound,
				                    raw_bound,
				                    stored_bound,
				                    "stored_after_stage");

				row_bound = stored_bound;
			}
		}
	}

	fclose(fp);
}

static void NTRUPLUS_UNUSED dump_dft3_twiddle_schedule(void)
{
	FILE *fp = fopen("build/dft3_twiddle_schedule.csv", "w");

	if (fp == NULL)
	{
		perror("build/dft3_twiddle_schedule.csv");
		return;
	}

	fprintf(fp, "input_crt_n3,input_crt_n32,gt_in_index,output_k3,dft_twiddle_exp,dft_twiddle_mont,dft_twiddle_normal\n");

	for (int n32 = 0; n32 < 32; n32++)
	{
		for (int n3 = 0; n3 < 3; n3++)
		{
			const int in_index = input_crt_n(n3, n32);

			for (int k3 = 0; k3 < 3; k3++)
			{
				const int exp = (n3 * k3) % 3;
				const int16_t twiddle = dft3_twiddle_mont(exp);

				fprintf(fp, "%d,%d,%d,%d,%d,%d,%d\n",
				        n3,
				        n32,
				        in_index,
				        k3,
				        exp,
				        twiddle,
				        normal_from_mont(twiddle));
			}
		}
	}

	fclose(fp);
}

static void dump_ntt32_twiddle_schedule(void)
{
	FILE *fp = fopen("build/ntt32_twiddle_schedule.csv", "w");

	if (fp == NULL)
	{
		perror("build/ntt32_twiddle_schedule.csv");
		return;
	}

	fprintf(fp, "row_k3,stage,len,start,j,lo_index,hi_index,twiddle_power,twiddle_mont,twiddle_normal,algorithm,notes\n");

	for (int row_k3 = 0; row_k3 < 3; row_k3++)
	{
		for (unsigned stage = 1; stage <= 5; stage++)
		{
			const unsigned distance = 1U << (5 - stage);
			const unsigned len = distance * 2;
			for (unsigned start = 0; start < 32; start += len)
			{
				for (unsigned j = 0; j < distance; j++)
				{
					const unsigned lo = start + j;
					const unsigned hi = lo + distance;
					const unsigned power = ntt32_ct_twiddle_power(stage, lo);
					const int16_t twiddle = gt96_omega32_powers[power];

					fprintf(fp, "%d,%u,%u,%u,%u,%u,%u,%u,%d,%d,complete_ct_bitrev_output,ct_t_is_high_times_twiddle_low_plus_t_high_low_minus_t\n",
					        row_k3,
					        stage,
					        len,
					        start,
					        j,
					        lo,
					        hi,
					        power,
					        twiddle,
					        normal_from_mont(twiddle));
				}
			}
		}
	}

	fclose(fp);
}

static void dump_gt_rowbitrev_basemul_table(void)
{
	FILE *fp = fopen("build/gt_rowbitrev_basemul_table.csv", "w");

	if (fp == NULL)
	{
		perror("build/gt_rowbitrev_basemul_table.csv");
		return;
	}

	fprintf(fp,
	        "branch,physical_j,position_start,position_end,k3,k32_bitrev_order,"
	        "logical_k32,logical_j,lambda_table,lambda_mont,lambda_normal,"
	        "asm_zeta_vector_index,asm_zeta_vector_lane,operation,notes\n");

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4*physical_j;
			const int k3 = (2*physical_j) % 3;
			const int k32_bitrev_order = (11*physical_j) & 31;
			const int logical_k32 = (int)bitreverse5((unsigned)k32_bitrev_order);
			const int logical_j =
				(int)gt96_output_crt_index((unsigned)k3, (unsigned)logical_k32);
			const int asm_vector = branch * 12 + physical_j / 8;
			const int asm_lane = physical_j & 7;

			fprintf(fp,
			        "%d,%d,%d,%d,%d,%d,%d,%d,"
			        "gt_rowbitrev_lambda[%d][%d],%d,%d,%d,%d,"
			        "direct_quartic_basemul_or_baseinv,"
			        "complete_rowbitrev_block_uses_physical_order_lambda\n",
			        branch,
			        physical_j,
			        pos,
			        pos + 3,
			        k3,
			        k32_bitrev_order,
			        logical_k32,
			        logical_j,
			        branch,
			        physical_j,
			        gt_rowbitrev_lambda[branch][physical_j],
			        normal_from_mont(gt_rowbitrev_lambda[branch][physical_j]),
			        asm_vector,
			        asm_lane);
		}
	}

	fclose(fp);
}

static const char *blockpair_register_for_block(int group, int half, int block)
{
	static const char *role0_regs[4] = { "v22", "v23", "v24", "v25" };
	static const char *role1_regs[4] = { "v26", "v27", "v28", "v29" };
	static const char *role2_regs[4] = { "v30", "v31", "v4", "v5" };
	const int base = 8*group + 4*half;

	if (block >= base && block < base + 4)
	{
		return role0_regs[block - base];
	}
	if (block >= 32 + base && block < 32 + base + 4)
	{
		return role1_regs[block - (32 + base)];
	}
	if (block >= 64 + base && block < 64 + base + 4)
	{
		return role2_regs[block - (64 + base)];
	}

	return "out_of_tile";
}

static void format_blockpair_source_vector(char out[160], int block)
{
	const int p = 4*block;

	snprintf(out, 160,
	         "a%d|a%d|a%d|a%d|a%d|a%d|a%d|a%d",
	         p + 0,
	         p + 1,
	         p + 2,
	         p + 3,
	         p + NTRUPLUS_N / 2 + 0,
	         p + NTRUPLUS_N / 2 + 1,
	         p + NTRUPLUS_N / 2 + 2,
	         p + NTRUPLUS_N / 2 + 3);
}

static void format_blockpair_value_vector(char out[192], int block)
{
	const int p = 4*block;

	snprintf(out, 192,
	         "B0[%d]|B0[%d]|B0[%d]|B0[%d]|B1[%d]|B1[%d]|B1[%d]|B1[%d]",
	         p + 0,
	         p + 1,
	         p + 2,
	         p + 3,
	         p + 0,
	         p + 1,
	         p + 2,
	         p + 3);
}

static void format_twist_blockpair_vector(char out[192], int branch0_value, int branch1_value)
{
	snprintf(out, 192,
	         "%d|%d|%d|%d|%d|%d|%d|%d",
	         branch0_value,
	         branch0_value,
	         branch0_value,
	         branch0_value,
	         branch1_value,
	         branch1_value,
	         branch1_value,
	         branch1_value);
}

static void dump_gt_blockpair_phase2_plan(void)
{
	FILE *fp = fopen("build/gt_blockpair_phase2_plan.csv", "w");

	if (fp == NULL)
	{
		perror("build/gt_blockpair_phase2_plan.csv");
		return;
	}

	fprintf(fp,
	        "group,half,n32,store_col,dft3_input,source_n3,packed_register,"
	        "packed_name,twisted_name,block_k,source_positions,value_vector,"
	        "branch0_twist_mont,branch1_twist_mont,"
	        "branch0_twist_asm_multiplier,branch1_twist_asm_multiplier,"
	        "branch0_twist_precompute,branch1_twist_precompute,"
	        "twist_vector_normal,twist_vector_precompute,twist_operation,"
	        "st3_register_order,next_ld3_result,notes\n");

	for (int group = 0; group < 4; group++)
	{
		for (int half = 0; half < 2; half++)
		{
			for (int col = 0; col < 4; col++)
			{
				const int n32 = 8*group + 4*half + col;
				const int blocks[3] = {
					input_crt_n(0, n32),
					input_crt_n(1, n32),
					input_crt_n(2, n32)
				};
				const char *regs[3] = {
					blockpair_register_for_block(group, half, blocks[0]),
					blockpair_register_for_block(group, half, blocks[1]),
					blockpair_register_for_block(group, half, blocks[2])
				};
				char st3_order[96];
				char next_ld3[96];

				snprintf(st3_order, sizeof(st3_order),
				         "st3_{%s.8h|%s.8h|%s.8h}_[dst_g%d_h%d_col%d]",
				         regs[0],
				         regs[1],
				         regs[2],
				         group,
				         half,
				         col);
				snprintf(next_ld3, sizeof(next_ld3),
				         "ld3_returns_x0=%s_x1=%s_x2=%s",
				         regs[0],
				         regs[1],
				         regs[2]);

				for (int n3 = 0; n3 < 3; n3++)
				{
					const int block = blocks[n3];
					const char *reg = regs[n3];
					const int16_t mont0 = twist_branch0[block];
					const int16_t mont1 = twist_branch1[block];
					const int normal0 = centered_normal_from_mont(mont0);
					const int normal1 = centered_normal_from_mont(mont1);
					const int pre0 = asm_precompute_from_normal(normal0);
					const int pre1 = asm_precompute_from_normal(normal1);
					char source_vector[160];
					char value_vector[192];
					char twist_normal_vector[192];
					char twist_precompute_vector[192];

					format_blockpair_source_vector(source_vector, block);
					format_blockpair_value_vector(value_vector, block);
					format_twist_blockpair_vector(twist_normal_vector, normal0, normal1);
					format_twist_blockpair_vector(twist_precompute_vector, pre0, pre1);

					fprintf(fp,
					        "%d,%d,%d,%d,%s,%d,%s,"
					        "P%d,PT%d,%d,%s,%s,"
					        "%d,%d,%d,%d,%d,%d,%s,%s,"
					        "PT%d=fqmul(P%d,TW%d),%s,%s,"
					        "blockpair_shape_after_zip;TW=[tw0x4|tw1x4];TP=[pre0x4|pre1x4]\n",
					        group,
					        half,
					        n32,
					        col,
					        dft3_input_name(n3),
					        n3,
					        reg,
					        block,
					        block,
					        block,
					        source_vector,
					        value_vector,
					        mont0,
					        mont1,
					        normal0,
					        normal1,
					        pre0,
					        pre1,
					        twist_normal_vector,
					        twist_precompute_vector,
					        block,
					        block,
					        block,
					        st3_order,
					        next_ld3);
				}
			}
		}
	}

	fclose(fp);
}

static void format_twist_pair_vector(char out[192], int first, int second)
{
	snprintf(out, 192,
	         "%d|%d|%d|%d|%d|%d|%d|%d",
	         first,
	         first,
	         first,
	         first,
	         second,
	         second,
	         second,
	         second);
}

static void format_compact_pair(char out[96], int first_mul, int second_mul,
                                int first_pre, int second_pre)
{
	snprintf(out, 96,
	         "%d|%d|%d|%d",
	         first_mul,
	         second_mul,
	         first_pre,
	         second_pre);
}

static const char *branch_output_name(int branch)
{
	return branch == 0 ? "B0" : "B1";
}

static const char *twist_table_name_for_branch(int branch)
{
	return branch == 0 ? "twist_branch0" : "twist_branch1";
}

static const int16_t *twist_table_for_branch(int branch)
{
	return branch == 0 ? twist_branch0 : twist_branch1;
}

static int twist_before_zip_register(int branch, int chunk_role, int pair)
{
	const int base = branch == 0 ? 4 : 10;

	return base + 2*chunk_role + pair;
}

static unsigned hword_hex(int value)
{
	return (unsigned)((uint16_t)(int16_t)value);
}

static void emit_asm_hword_vector(FILE *fp, int first, int second)
{
	fprintf(fp,
	        "    .hword 0x%04x, 0x%04x, 0x%04x, 0x%04x, "
	        "0x%04x, 0x%04x, 0x%04x, 0x%04x\n",
	        hword_hex(first),
	        hword_hex(first),
	        hword_hex(first),
	        hword_hex(first),
	        hword_hex(second),
	        hword_hex(second),
	        hword_hex(second),
	        hword_hex(second));
}

static void dump_gt_twist_before_zip_table(void)
{
	FILE *csv = fopen("build/gt_twist_before_zip_table.csv", "w");
	FILE *asm_table = fopen("build/gt_twist_before_zip_table.s", "w");

	if (csv == NULL)
	{
		perror("build/gt_twist_before_zip_table.csv");
	}
	if (asm_table == NULL)
	{
		perror("build/gt_twist_before_zip_table.s");
	}
	if (csv == NULL || asm_table == NULL)
	{
		if (csv != NULL)
		{
			fclose(csv);
		}
		if (asm_table != NULL)
		{
			fclose(asm_table);
		}
		return;
	}

	fprintf(csv,
	        "loop,group,half,branch,branch_output,top_split_output_register,"
	        "coeff_start,coeff_end,block0,block1,twist_table,"
	        "twist_index0,twist_index1,twist_mont0,twist_mont1,"
	        "twist_asm_multiplier0,twist_asm_multiplier1,"
	        "twist_precompute0,twist_precompute1,"
	        "twist_multiplier_vector,twist_precompute_vector,"
	        "semi_expanded_multiplier_hword,semi_expanded_precompute_hword,"
	        "compact_hword,operation,notes\n");

	fprintf(asm_table,
	        "/* Auto-generated by gt_test/dump_forward_mapping.c.\n"
	        " * Twist-before-zip table for the current block-pair schedule.\n"
	        " * Order: loop 0..7; inside each loop B1 v10..v15, then B0 v4..v9.\n"
	        " * semi_expanded entries are consumed as multiplier vector then precompute vector.\n"
	        " * compact entries are: m[k0], m[k1], pre[k0], pre[k1].\n"
	        " * Values are emitted as unsigned 16-bit hex two's-complement hwords.\n"
	        " */\n\n"
	        ".align 4\n"
	        "gt_twist_before_zip_semi_expanded:\n");

	for (int loop = 0; loop < 8; loop++)
	{
		const int group = loop / 2;
		const int half = loop & 1;
		const int base = 8*group + 4*half;

		for (int branch_order = 0; branch_order < 2; branch_order++)
		{
			const int branch = branch_order == 0 ? 1 : 0;
			const int16_t *twist = twist_table_for_branch(branch);

			for (int chunk_role = 0; chunk_role < 3; chunk_role++)
			{
				for (int pair = 0; pair < 2; pair++)
				{
					const int block0 = 32*chunk_role + base + 2*pair;
					const int block1 = block0 + 1;
					const int coeff_start = 4*block0;
					const int coeff_end = coeff_start + 7;
					const int reg = twist_before_zip_register(branch, chunk_role, pair);
					const int mont0 = twist[block0];
					const int mont1 = twist[block1];
					const int normal0 = centered_normal_from_mont(twist[block0]);
					const int normal1 = centered_normal_from_mont(twist[block1]);
					const int pre0 = asm_precompute_from_normal(normal0);
					const int pre1 = asm_precompute_from_normal(normal1);
					char mul_vector[192];
					char pre_vector[192];
					char compact[96];

					format_twist_pair_vector(mul_vector, normal0, normal1);
					format_twist_pair_vector(pre_vector, pre0, pre1);
					format_compact_pair(compact, normal0, normal1, pre0, pre1);

					fprintf(csv,
					        "%d,%d,%d,%d,%s,v%d,"
					        "%d,%d,%d,%d,%s,"
					        "%d,%d,%d,%d,%d,%d,%d,%d,"
					        "%s,%s,%s,%s,%s,"
					        "fqmul_%s[%d..%d]_by_twist_%s_k%d_k%d,"
					        "twist_before_zip;vector_shape=[k0x4|k1x4]\n",
					        loop,
					        group,
					        half,
					        branch,
					        branch_output_name(branch),
					        reg,
					        coeff_start,
					        coeff_end,
					        block0,
					        block1,
					        twist_table_name_for_branch(branch),
					        block0,
					        block1,
					        mont0,
					        mont1,
					        normal0,
					        normal1,
					        pre0,
					        pre1,
					        mul_vector,
					        pre_vector,
					        mul_vector,
					        pre_vector,
					        compact,
					        branch_output_name(branch),
					        coeff_start,
					        coeff_end,
					        twist_table_name_for_branch(branch),
					        block0,
					        block1);

					fprintf(asm_table,
					        "    // loop %d group=%d half=%d %s v%d coeff %s[%d..%d], blocks k=%d,%d\n",
					        loop,
					        group,
					        half,
					        branch_output_name(branch),
					        reg,
					        branch_output_name(branch),
					        coeff_start,
					        coeff_end,
					        block0,
					        block1);
					emit_asm_hword_vector(asm_table, normal0, normal1);
					emit_asm_hword_vector(asm_table, pre0, pre1);
				}
			}
		}
	}

	fprintf(asm_table,
	        "\n.align 4\n"
	        "gt_twist_before_zip_compact:\n");

	for (int loop = 0; loop < 8; loop++)
	{
		const int group = loop / 2;
		const int half = loop & 1;
		const int base = 8*group + 4*half;

		for (int branch_order = 0; branch_order < 2; branch_order++)
		{
			const int branch = branch_order == 0 ? 1 : 0;
			const int16_t *twist = twist_table_for_branch(branch);

			for (int chunk_role = 0; chunk_role < 3; chunk_role++)
			{
				for (int pair = 0; pair < 2; pair++)
				{
					const int block0 = 32*chunk_role + base + 2*pair;
					const int block1 = block0 + 1;
					const int coeff_start = 4*block0;
					const int coeff_end = coeff_start + 7;
					const int reg = twist_before_zip_register(branch, chunk_role, pair);
					const int normal0 = centered_normal_from_mont(twist[block0]);
					const int normal1 = centered_normal_from_mont(twist[block1]);
					const int pre0 = asm_precompute_from_normal(normal0);
					const int pre1 = asm_precompute_from_normal(normal1);

					fprintf(asm_table,
					        "    // loop %d group=%d half=%d %s v%d coeff %s[%d..%d], blocks k=%d,%d\n"
					        "    .hword 0x%04x, 0x%04x, 0x%04x, 0x%04x\n",
					        loop,
					        group,
					        half,
					        branch_output_name(branch),
					        reg,
					        branch_output_name(branch),
					        coeff_start,
					        coeff_end,
					        block0,
					        block1,
					        hword_hex(normal0),
					        hword_hex(normal1),
					        hword_hex(pre0),
					        hword_hex(pre1));
				}
			}
		}
	}

	fclose(csv);
	fclose(asm_table);
}

int main(void)
{
	/*
	 * Keep only the dumps that are useful for the current complete
	 * row-bitrev Good-Thomas + ASM work:
	 *
	 * - gt_blockpair_phase2_plan feeds the interactive phase123 viewer.
	 * - gt_twist_before_zip_table gives the current twist/precompute order.
	 * - gt_stage_ntt32_input_plan, ntt32_* and gt_register_pack_plan describe
	 *   the row input and complete 32-point CT kernel shape.
	 * - gt_rowbitrev_basemul_table describes physical-order lambda layout.
	 */
	dump_gt_blockpair_phase2_plan();
	dump_gt_twist_before_zip_table();
	dump_gt_stage_ntt32_input_plan();
	dump_ntt32_twiddle_schedule();
	dump_ntt32_neon_plan();
	dump_gt_register_pack_plan();
	dump_gt_rowbitrev_basemul_table();

	return 0;
}

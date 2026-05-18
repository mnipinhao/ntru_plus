#include <stdint.h>
#include <stdio.h>
#include <limits.h>

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

static int input_crt_n(int n3, int n32)
{
	return (64*n3 + 33*n32) % 96;
}

static void find_input_crt_coords(int n, int *out_n3, int *out_n32)
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
				 * Proposed 32-point row input pack after bitreverse:
				 *   v4 = work[0..7], v5 = work[8..15],
				 *   v6 = work[16..23], v7 = work[24..31].
				 *
				 * work[bitreverse5(k32)] receives the DFT3 output at
				 * column k32.
				 */
				for (int work = 0; work < 32; work++)
				{
					const int input_k32 = (int)bitreverse5((unsigned)work);
					const int reg = 4 + work / 8;
					const int vlane = work & 7;
					const int pos0 = physical_pos_for_input_crt(branch, lane, 0, input_k32);
					const int pos1 = physical_pos_for_input_crt(branch, lane, 1, input_k32);
					const int pos2 = physical_pos_for_input_crt(branch, lane, 2, input_k32);
					const int tw0 = input_crt_n(0, input_k32);
					const int tw1 = input_crt_n(1, input_k32);
					const int tw2 = input_crt_n(2, input_k32);

					fprintf(fp,
					        "ntt32_initial_bitreversed_pack,%d,%d,%d,v%d,%d,"
					        "-1,-1,-1,-1,-1,%d,"
					        "%d,0,1,%d,%d,state,-1,-1,"
					        "0,%d,%d,"
					        "%d,%d,%d,%d,%d,%d,"
					        "work_index_is_bitreversed_k32\n",
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

				int stage = 0;

				for (unsigned len = 2; len <= 32; len <<= 1)
				{
					const unsigned step = 32 / len;

					stage++;

					for (unsigned start = 0; start < 32; start += len)
					{
						for (unsigned j = 0; j < len / 2; j++)
						{
							const unsigned lo = start + j;
							const unsigned hi = lo + len / 2;
							const unsigned power = step * j;
							const int16_t twiddle = gt96_omega32_powers[power];
							const int lo_reg = 4 + (int)lo / 8;
							const int hi_reg = 4 + (int)hi / 8;

							fprintf(fp,
							        "ntt32_butterfly_operand,%d,%d,%d,v%d,%u,"
							        "-1,-1,-1,-1,-1,-1,"
							        "%d,%d,%u,%u,-1,lo,%u,%u,"
							        "%u,%d,%d,"
							        "-1,-1,-1,-1,-1,-1,"
							        "low_operand_before_stage_butterfly\n",
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
							        "%d,%d,%u,%u,-1,hi,%u,%u,"
							        "%u,%d,%d,"
							        "-1,-1,-1,-1,-1,-1,"
							        "high_operand_multiplied_by_stage_twiddle\n",
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
 * This is not a new mathematical mapping.  It assumes the bitreversed row is
 * packed contiguously as:
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

	int stage = 0;

	for (unsigned len = 2; len <= 32; len <<= 1)
	{
		const unsigned step = 32 / len;

		stage++;

		for (unsigned start = 0; start < 32; start += len)
		{
			for (unsigned j = 0; j < len / 2; j++)
			{
				const unsigned lo = start + j;
				const unsigned hi = lo + len / 2;
				const unsigned power = step * j;
				const int16_t twiddle = gt96_omega32_powers[power];
				const char *notes = "high_operand_multiplied_by_twiddle";

				if (power == 0)
				{
					notes = "twiddle_is_montgomery_one_multiply_can_be_skipped";
				}

				fprintf(fp,
				        "%d,%u,%u,%u,%u,%u,%u,%s,%u,%s,%u,%u,%d,%d,"
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
				bounds_t bitrev_bounds;

				bounds_init(&bitrev_bounds);
				for (unsigned i = 0; i < 32; i++)
				{
					const unsigned br = bitreverse5(i);

					row[br] = schedule->reduce_ntt_input ?
						trace_reduce_i32(mat[k3][i]) :
						mat[k3][i];
				}

				for (int i = 0; i < 32; i++)
				{
					bounds_update(&bitrev_bounds, row[i]);
				}
				trace_report(fp, case_name, schedule->name, "ntt32_bitreverse_input",
				             branch, lane, k3, 0, 1,
				             schedule->reduce_ntt_input ? "reduced" : "lazy",
				             bitrev_bounds);

				int stage = 0;

				for (unsigned len = 2; len <= 32; len <<= 1)
				{
					const unsigned step = 32 / len;
					const int reduce_stage = should_reduce_stage(schedule, stage + 1);
					bounds_t input_bounds;
					bounds_t fqmul_bounds;
					bounds_t raw_bounds;
					bounds_t stored_bounds;

					stage++;
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
						int16_t w = NTRUPLUS_R;

						for (unsigned j = 0; j < len / 2; j++)
						{
							const unsigned lo = start + j;
							const unsigned hi = lo + len / 2;
							const int32_t u = row[lo];
							const int32_t v = fqmul_wide(row[hi], w);
							const int32_t sum = u + v;
							const int32_t diff = u - v;

							bounds_update(&fqmul_bounds, v);
							bounds_update(&raw_bounds, sum);
							bounds_update(&raw_bounds, diff);

							row[lo] = reduce_stage ? trace_reduce_i32(sum) : sum;
							row[hi] = reduce_stage ? trace_reduce_i32(diff) : diff;
							w = fqmul(w, gt96_omega32_powers[step]);
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
					             branch, lane, k3, stage, len, "montgomery_output",
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

static void dump_reduction_bound_trace(void)
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

static void dump_reduction_static_bounds(void)
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
			int stage = 0;

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
			                    "input_to_ntt32_before_optional_bitreverse_reduce");

			row_bound = schedule->reduce_ntt_input ? centered : dft_stored_bound;
			static_bound_report(fp,
			                    input_models[m].name,
			                    schedule->name,
			                    "ntt32_bitreverse_input",
			                    0,
			                    1,
			                    schedule->reduce_ntt_input ? "reduced" : "lazy",
			                    dft_stored_bound,
			                    dft_stored_bound,
			                    row_bound,
			                    "work_bitreverse_input_bound");

			for (unsigned len = 2; len <= 32; len <<= 1)
			{
				const int reduce_stage = should_reduce_stage(schedule, stage + 1);
				const int32_t raw_bound = row_bound + fqmul_out;
				const int32_t stored_bound = reduce_stage ? centered : raw_bound;

				stage++;
				static_bound_report(fp,
				                    input_models[m].name,
				                    schedule->name,
				                    "ntt32_stage_raw",
				                    stage,
				                    len,
				                    "before_optional_reduce",
				                    row_bound,
				                    row_bound,
				                    raw_bound,
				                    "u_plus_or_minus_fqmul(high_twiddle)");
				static_bound_report(fp,
				                    input_models[m].name,
				                    schedule->name,
				                    "ntt32_stage_stored",
				                    stage,
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

static void dump_dft3_twiddle_schedule(void)
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

	fprintf(fp, "row_k3,stage,len,start,j,lo_index,hi_index,twiddle_power,twiddle_mont,twiddle_normal\n");

	for (int row_k3 = 0; row_k3 < 3; row_k3++)
	{
		int stage = 0;

		for (unsigned len = 2; len <= 32; len <<= 1)
		{
			const unsigned step = 32 / len;

			stage++;

			for (unsigned start = 0; start < 32; start += len)
			{
				for (unsigned j = 0; j < len / 2; j++)
				{
					const unsigned lo = start + j;
					const unsigned hi = lo + len / 2;
					const unsigned power = step * j;
					const int16_t twiddle = gt96_omega32_powers[power];

					fprintf(fp, "%d,%d,%u,%u,%u,%u,%u,%u,%d,%d\n",
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

int main(void)
{
	dump_dft3_twiddle_schedule();
	dump_ntt32_twiddle_schedule();
	dump_ntt32_neon_plan();
	dump_gt_register_pack_plan();
	dump_reduction_bound_trace();
	dump_reduction_static_bounds();

	printf("physical_pos,branch,branch_pos,block_k,lane,twist_table,twist_index,twist_mont,twist_normal,gt_in_index,input_crt_n3,input_crt_n32,dft_to_k3_0_exp,dft_to_k3_0_mont,dft_to_k3_0_normal,dft_to_k3_1_exp,dft_to_k3_1_mont,dft_to_k3_1_normal,dft_to_k3_2_exp,dft_to_k3_2_mont,dft_to_k3_2_normal\n");

	for (int pos = 0; pos < NTRUPLUS_N; pos++)
	{
		const int branch = pos / (NTRUPLUS_N / 2);
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int branch_pos = pos - branch_start;
		const int block = branch_pos / 4;
		const int lane = branch_pos & 3;
		const int16_t *twist = branch == 0 ? twist_branch0 : twist_branch1;
		const char *twist_name = branch == 0 ? "twist_branch0" : "twist_branch1";
		int n3;
		int n32;

		find_input_crt_coords(block, &n3, &n32);

		printf("%d,%d,%d,%d,%d,%s,%d,%d,%d,%d,%d,%d",
		       pos,
		       branch,
		       branch_pos,
		       block,
		       lane,
		       twist_name,
		       block,
		       twist[block],
		       normal_from_mont(twist[block]),
		       block,
		       n3,
		       n32);

		for (int k3 = 0; k3 < 3; k3++)
		{
			const int exp = (n3 * k3) % 3;
			const int16_t twiddle = dft3_twiddle_mont(exp);

			printf(",%d,%d,%d",
			       exp,
			       twiddle,
			       normal_from_mont(twiddle));
		}

		printf("\n");
	}

	return 0;
}

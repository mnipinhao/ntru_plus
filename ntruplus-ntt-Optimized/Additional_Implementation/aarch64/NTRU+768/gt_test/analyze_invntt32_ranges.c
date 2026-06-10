#include <stdint.h>
#include <stdio.h>
#include <string.h>

/*
 * Range analyzer for the production inverse row NTT32.
 *
 * This deliberately models the assembly operations rather than abstract
 * modular arithmetic:
 *   - q = 3457,
 *   - sqrdmulh/mul/mls normal-form fqmul,
 *   - sqdmulh/srshr/mls Barrett reduction,
 *   - signed 16-bit lane add/sub wrap behavior,
 *   - the exact inverse row stage order used by asm/slothy/invntt_opt.s.
 *
 * Inputs are valid rows produced by ntt_gt_rowbitrevlayout() from patterns,
 * impulses, random inputs, and lazy-edge inputs.  They are not arbitrary
 * int16 values.  The row_end_reduce_only variant matches the production
 * lazy row policy: leave all row butterflies unreduced, then run the actual
 * Barrett row-end reduction over all 32 natural-order row vectors before
 * post-row DFT3/untwist/merge.
 */
#define NTRUPLUS_NTT_REFERENCE_TEST
#include "../ntt.c"

#define RANDOM_CASES 512
#define STAGES 6

enum variant {
	VAR_BASELINE,
	VAR_SKIP_STAGE1,
	VAR_SKIP_STAGE2,
	VAR_SKIP_STAGE3,
	VAR_STAGE123_END,
	VAR_STAGE45_END,
	VAR_STAGE_ENDS,
	VAR_ROW_END,
	VAR_REDUCE_LO_ONLY,
	VAR_REDUCE_HI_ONLY,
	VAR_COUNT
};

struct range {
	int min;
	int max;
};

struct stats {
	struct range stage[STAGES];
	int rows;
	int reductions;
	int fqmuls;
	int addsub_wraps;
	int mismatches;
	int exact_mismatches;
	int max_raw_addsub;
	int max_abs_before_reduce;
	int max_abs_fqmul_input;
};

static const char *variant_name(enum variant variant)
{
	switch (variant)
	{
	case VAR_BASELINE: return "baseline";
	case VAR_SKIP_STAGE1: return "skip_stage1_reductions";
	case VAR_SKIP_STAGE2: return "skip_stage2_reductions";
	case VAR_SKIP_STAGE3: return "skip_stage3_reductions";
	case VAR_STAGE123_END: return "stage123_end_reduce";
	case VAR_STAGE45_END: return "stage45_end_reduce";
	case VAR_STAGE_ENDS: return "stage123_stage45_end_reduce";
	case VAR_ROW_END: return "row_end_reduce_only";
	case VAR_REDUCE_LO_ONLY: return "reduce_lo_only";
	case VAR_REDUCE_HI_ONLY: return "reduce_hi_only";
	default: return "unknown";
	}
}

static int abs_i(int x)
{
	return x < 0 ? -x : x;
}

static int modq_i(int64_t a)
{
	int r = (int)(a % NTRUPLUS_Q);

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}

	return r;
}

static int equal_modq_i(int16_t a, int16_t b)
{
	return modq_i((int)a - (int)b) == 0;
}

static int16_t wrap16(int32_t x)
{
	return (int16_t)(uint16_t)x;
}

static int64_t arshift(int64_t x, unsigned shift)
{
	if (x >= 0)
	{
		return x >> shift;
	}

	return -(((-x) + ((INT64_C(1) << shift) - 1)) >> shift);
}

static int16_t sat16(int64_t x)
{
	if (x > 32767)
	{
		return 32767;
	}

	if (x < -32768)
	{
		return -32768;
	}

	return (int16_t)x;
}

static int16_t sqrdmulh_s16(int16_t a, int16_t b)
{
	const int64_t doubled = INT64_C(2) * a * b;
	const int64_t rounded = arshift(doubled + (INT64_C(1) << 15), 16);

	return sat16(rounded);
}

static int16_t sqdmulh_s16(int16_t a, int16_t b)
{
	const int64_t doubled = INT64_C(2) * a * b;

	return sat16(arshift(doubled, 16));
}

static int16_t srshr_s16(int16_t a, unsigned shift)
{
	return (int16_t)arshift((int64_t)a + (INT64_C(1) << (shift - 1)), shift);
}

static void range_init(struct range *r)
{
	r->min = 32767;
	r->max = -32768;
}

static void range_add(struct range *r, int x)
{
	if (x < r->min)
	{
		r->min = x;
	}

	if (x > r->max)
	{
		r->max = x;
	}
}

static void stats_init(struct stats *stats)
{
	memset(stats, 0, sizeof(*stats));

	for (int i = 0; i < STAGES; i++)
	{
		range_init(&stats->stage[i]);
	}
}

static void record_stage(struct stats *stats, int stage, const int16_t a[32])
{
	for (int i = 0; i < 32; i++)
	{
		range_add(&stats->stage[stage], a[i]);
	}
}

static void record_stage_range(struct stats *stats, int stage,
                               const int16_t a[32], int start, int len)
{
	for (int i = 0; i < len; i++)
	{
		range_add(&stats->stage[stage], a[start + i]);
	}
}

static void record_stage_4(struct stats *stats, int stage, const int16_t a[32],
                           int i0, int i1, int i2, int i3)
{
	range_add(&stats->stage[stage], a[i0]);
	range_add(&stats->stage[stage], a[i1]);
	range_add(&stats->stage[stage], a[i2]);
	range_add(&stats->stage[stage], a[i3]);
}

static int16_t asm_fqmul(int16_t a, int16_t mul, int16_t pre,
                         struct stats *stats)
{
	const int abs_a = abs_i(a);
	int16_t qhat;
	int16_t prod;

	if (abs_a > stats->max_abs_fqmul_input)
	{
		stats->max_abs_fqmul_input = abs_a;
	}

	stats->fqmuls++;
	qhat = sqrdmulh_s16(a, pre);
	prod = wrap16((int32_t)a * mul);
	prod = wrap16((int32_t)prod - (int32_t)qhat * NTRUPLUS_Q);
	return prod;
}

static int16_t asm_barrett(int16_t a, struct stats *stats)
{
	int16_t t;
	const int abs_a = abs_i(a);

	if (abs_a > stats->max_abs_before_reduce)
	{
		stats->max_abs_before_reduce = abs_a;
	}

	stats->reductions++;
	t = sqdmulh_s16(a, 19412);
	t = srshr_s16(t, 11);
	return wrap16((int32_t)a - (int32_t)t * NTRUPLUS_Q);
}

static int16_t add16_checked(int16_t a, int16_t b, struct stats *stats)
{
	const int32_t raw = (int32_t)a + b;

	if (abs_i(raw) > stats->max_raw_addsub)
	{
		stats->max_raw_addsub = abs_i(raw);
	}

	if (raw < -32768 || raw > 32767)
	{
		stats->addsub_wraps++;
	}

	return wrap16(raw);
}

static int16_t sub16_checked(int16_t a, int16_t b, struct stats *stats)
{
	const int32_t raw = (int32_t)a - b;

	if (abs_i(raw) > stats->max_raw_addsub)
	{
		stats->max_raw_addsub = abs_i(raw);
	}

	if (raw < -32768 || raw > 32767)
	{
		stats->addsub_wraps++;
	}

	return wrap16(raw);
}

static int reduce_after_butterfly(enum variant variant, int stage)
{
	if (variant == VAR_SKIP_STAGE1 && stage == 1)
	{
		return 0;
	}

	if (variant == VAR_SKIP_STAGE2 && stage == 2)
	{
		return 0;
	}

	if (variant == VAR_SKIP_STAGE3 && stage == 3)
	{
		return 0;
	}

	if (variant == VAR_STAGE123_END && stage <= 3)
	{
		return 0;
	}

	if (variant == VAR_STAGE45_END && stage >= 4)
	{
		return 0;
	}

	if (variant == VAR_STAGE_ENDS)
	{
		return 0;
	}

	if (variant == VAR_ROW_END)
	{
		return 0;
	}

	return 1;
}

static void maybe_reduce_pair(enum variant variant, int stage,
                              int16_t *lo, int16_t *hi, struct stats *stats)
{
	if (!reduce_after_butterfly(variant, stage))
	{
		return;
	}

	if (variant == VAR_REDUCE_HI_ONLY)
	{
		*hi = asm_barrett(*hi, stats);
		return;
	}

	if (variant == VAR_REDUCE_LO_ONLY)
	{
		*lo = asm_barrett(*lo, stats);
		return;
	}

	*lo = asm_barrett(*lo, stats);
	*hi = asm_barrett(*hi, stats);
}

static void reduce_range(int16_t a[32], int start, int len, struct stats *stats)
{
	for (int i = 0; i < len; i++)
	{
		a[start + i] = asm_barrett(a[start + i], stats);
	}
}

static void butterfly(int16_t a[32], int lo, int hi, int stage,
                      int16_t mul, int16_t pre, enum variant variant,
                      struct stats *stats)
{
	const int16_t old_lo = a[lo];
	const int16_t prod = asm_fqmul(a[hi], mul, pre, stats);

	a[lo] = add16_checked(a[lo], prod, stats);
	a[hi] = sub16_checked(old_lo, prod, stats);
	maybe_reduce_pair(variant, stage, &a[lo], &a[hi], stats);
}

static void invntt32_asm_model(int16_t out[32], const int16_t in[32],
                               enum variant variant, struct stats *stats)
{
	static const int16_t stage123_mul[5] = { 1, 708, 1521, 708, -1716 };
	static const int16_t stage123_pre[5] = { 9, 6711, 14417, 6711, -16266 };
	static const int16_t stage45_mul[8][3] = {
		{ 1, 1, 708 },
		{ -39, -436, -1015 },
		{ 1521, -39, 44 },
		{ -550, -281, 1558 },
		{ 708, 1521, -1716 },
		{ 44, 588, 1464 },
		{ -1716, -550, 1241 },
		{ 1241, 1267, 1673 },
	};
	static const int16_t stage45_pre[8][3] = {
		{ 9, 9, 6711 },
		{ -370, -4133, -9621 },
		{ 14417, -370, 417 },
		{ -5213, -2664, 14768 },
		{ 6711, 14417, -16266 },
		{ 417, 5573, 13877 },
		{ -16266, -5213, 11763 },
		{ 11763, 12010, 15858 },
	};

	memcpy(out, in, 32 * sizeof(out[0]));
	stats->rows++;
	record_stage(stats, 0, out);

	for (int base = 0; base < 32; base += 8)
	{
		butterfly(out, base + 0, base + 1, 1, stage123_mul[0], stage123_pre[0], variant, stats);
		butterfly(out, base + 2, base + 3, 1, stage123_mul[0], stage123_pre[0], variant, stats);
		butterfly(out, base + 4, base + 5, 1, stage123_mul[0], stage123_pre[0], variant, stats);
		butterfly(out, base + 6, base + 7, 1, stage123_mul[0], stage123_pre[0], variant, stats);
		record_stage_range(stats, 1, out, base, 8);

		butterfly(out, base + 0, base + 2, 2, stage123_mul[0], stage123_pre[0], variant, stats);
		butterfly(out, base + 1, base + 3, 2, stage123_mul[1], stage123_pre[1], variant, stats);
		butterfly(out, base + 4, base + 6, 2, stage123_mul[0], stage123_pre[0], variant, stats);
		butterfly(out, base + 5, base + 7, 2, stage123_mul[1], stage123_pre[1], variant, stats);
		record_stage_range(stats, 2, out, base, 8);

		butterfly(out, base + 0, base + 4, 3, stage123_mul[0], stage123_pre[0], variant, stats);
		butterfly(out, base + 1, base + 5, 3, stage123_mul[2], stage123_pre[2], variant, stats);
		butterfly(out, base + 2, base + 6, 3, stage123_mul[3], stage123_pre[3], variant, stats);
		butterfly(out, base + 3, base + 7, 3, stage123_mul[4], stage123_pre[4], variant, stats);

		if (variant == VAR_STAGE123_END || variant == VAR_STAGE_ENDS)
		{
			reduce_range(out, base, 8, stats);
		}

		record_stage_range(stats, 3, out, base, 8);
	}

	for (int j = 0; j < 8; j++)
	{
		butterfly(out, j, j + 8, 4, stage45_mul[j][0], stage45_pre[j][0], variant, stats);
		butterfly(out, j + 16, j + 24, 4, stage45_mul[j][0], stage45_pre[j][0], variant, stats);
		record_stage_4(stats, 4, out, j, j + 8, j + 16, j + 24);

		butterfly(out, j, j + 16, 5, stage45_mul[j][1], stage45_pre[j][1], variant, stats);
		butterfly(out, j + 8, j + 24, 5, stage45_mul[j][2], stage45_pre[j][2], variant, stats);

		if (variant == VAR_STAGE45_END || variant == VAR_STAGE_ENDS)
		{
			out[j] = asm_barrett(out[j], stats);
			out[j + 8] = asm_barrett(out[j + 8], stats);
			out[j + 16] = asm_barrett(out[j + 16], stats);
			out[j + 24] = asm_barrett(out[j + 24], stats);
		}

		record_stage_4(stats, 5, out, j, j + 8, j + 16, j + 24);
	}

	if (variant == VAR_ROW_END)
	{
		reduce_range(out, 0, 32, stats);
		record_stage(stats, 5, out);
	}
}

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static void fill_zero(int16_t a[NTRUPLUS_N])
{
	memset(a, 0, NTRUPLUS_N * sizeof(a[0]));
}

static void fill_pattern(int16_t a[NTRUPLUS_N], int pattern, uint32_t seed)
{
	static const int lazy_vals[] = {
		0, 1, -1,
		NTRUPLUS_Q - 1, -(NTRUPLUS_Q - 1),
		2 * (NTRUPLUS_Q - 1), -2 * (NTRUPLUS_Q - 1),
		3 * (NTRUPLUS_Q - 1), -3 * (NTRUPLUS_Q - 1),
		4 * (NTRUPLUS_Q - 1), -4 * (NTRUPLUS_Q - 1)
	};

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		switch (pattern)
		{
		case 0:
			a[i] = 0;
			break;
		case 1:
			a[i] = 1;
			break;
		case 2:
			a[i] = (i & 1) ? -1 : 1;
			break;
		case 3:
			a[i] = (i & 1) ? -(NTRUPLUS_Q / 2) : (NTRUPLUS_Q / 2);
			break;
		case 4:
			a[i] = (int16_t)lazy_vals[i % (int)(sizeof(lazy_vals) / sizeof(lazy_vals[0]))];
			break;
		default:
			a[i] = (int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
			break;
		}
	}
}

static void gather_rows(int16_t rows[3][32][8], const int16_t in[NTRUPLUS_N])
{
	for (int k3 = 0; k3 < 3; k3++)
	{
		for (int k32_br = 0; k32_br < 32; k32_br++)
		{
			const int physical_j = (32*k3 + 3*k32_br) % 96;

			for (int lane = 0; lane < 4; lane++)
			{
				rows[k3][k32_br][lane] = in[4*physical_j + lane];
				rows[k3][k32_br][4 + lane] =
					in[NTRUPLUS_N/2 + 4*physical_j + lane];
			}
		}
	}
}

static void analyze_frequency_input(const int16_t freq[NTRUPLUS_N],
                                    struct stats stats[VAR_COUNT])
{
	int16_t rows[3][32][8];

	gather_rows(rows, freq);

	for (int k3 = 0; k3 < 3; k3++)
	{
		for (int lane = 0; lane < 8; lane++)
		{
			int16_t in[32];
			int16_t baseline[32];

			for (int k32 = 0; k32 < 32; k32++)
			{
				in[k32] = rows[k3][k32][lane];
			}

			invntt32_asm_model(baseline, in, VAR_BASELINE, &stats[VAR_BASELINE]);

			for (int variant = 1; variant < VAR_COUNT; variant++)
			{
				int16_t got[32];

				invntt32_asm_model(got, in, (enum variant)variant, &stats[variant]);

				for (int i = 0; i < 32; i++)
				{
					if (!equal_modq_i(got[i], baseline[i]))
					{
						stats[variant].mismatches++;
					}

					if (got[i] != baseline[i])
					{
						stats[variant].exact_mismatches++;
					}
				}
			}
		}
	}
}

static void analyze_time_input(const int16_t input[NTRUPLUS_N],
                               struct stats stats[VAR_COUNT])
{
	int16_t freq[NTRUPLUS_N];

	ntt_gt_rowbitrevlayout(freq, input);
	analyze_frequency_input(freq, stats);
}

int main(void)
{
	struct stats stats[VAR_COUNT];
	int16_t a[NTRUPLUS_N];

	for (int variant = 0; variant < VAR_COUNT; variant++)
	{
		stats_init(&stats[variant]);
	}

	for (int pattern = 0; pattern < 6; pattern++)
	{
		fill_pattern(a, pattern, 0x12345678u + (uint32_t)pattern);
		analyze_time_input(a, stats);
	}

	for (int pos = 0; pos < NTRUPLUS_N; pos++)
	{
		fill_zero(a);
		a[pos] = 1;
		analyze_time_input(a, stats);
	}

	for (uint32_t seed = 0; seed < RANDOM_CASES; seed++)
	{
		fill_pattern(a, 5, 0x9e3779b9u + seed);
		analyze_time_input(a, stats);
	}

	printf("inverse row NTT32 ASM range analyzer: real forward-produced row inputs\n");
	printf("cases: patterns=6 impulses=768 random=%d\n", RANDOM_CASES);
	printf("variant rows reductions reductions_per_row fqmuls fqmuls_per_row "
	       "wraps max_raw_addsub max_abs_fqmul_input "
	       "max_abs_before_reduce mismatches exact_mismatches "
	       "stage0 stage1 stage2 stage3 stage4 stage5\n");

	for (int variant = 0; variant < VAR_COUNT; variant++)
	{
		printf("%s %d %d %.2f %d %.2f %d %d %d %d %d %d",
		       variant_name((enum variant)variant),
		       stats[variant].rows,
		       stats[variant].reductions,
		       stats[variant].rows == 0 ? 0.0 :
		           (double)stats[variant].reductions / stats[variant].rows,
		       stats[variant].fqmuls,
		       stats[variant].rows == 0 ? 0.0 :
		           (double)stats[variant].fqmuls / stats[variant].rows,
		       stats[variant].addsub_wraps,
		       stats[variant].max_raw_addsub,
		       stats[variant].max_abs_fqmul_input,
		       stats[variant].max_abs_before_reduce,
		       stats[variant].mismatches,
		       stats[variant].exact_mismatches);

		for (int stage = 0; stage < STAGES; stage++)
		{
			printf(" [%d,%d]", stats[variant].stage[stage].min,
			       stats[variant].stage[stage].max);
		}

		printf("\n");
	}

	if (stats[VAR_ROW_END].rows == 0)
	{
		fprintf(stderr, "row_end_reduce_only analyzer did not process rows\n");
		return 1;
	}

	if (stats[VAR_ROW_END].addsub_wraps != 0)
	{
		fprintf(stderr, "row_end_reduce_only observed signed int16 wraps: %d\n",
		        stats[VAR_ROW_END].addsub_wraps);
		return 1;
	}

	if (stats[VAR_ROW_END].mismatches != 0 ||
	    stats[VAR_ROW_END].exact_mismatches != 0)
	{
		fprintf(stderr,
		        "row_end_reduce_only mismatch: modq=%d exact=%d\n",
		        stats[VAR_ROW_END].mismatches,
		        stats[VAR_ROW_END].exact_mismatches);
		return 1;
	}

	if (stats[VAR_ROW_END].max_abs_before_reduce > 10000)
	{
		fprintf(stderr,
		        "row_end_reduce_only bound too high: max_abs_before_reduce=%d\n",
		        stats[VAR_ROW_END].max_abs_before_reduce);
		return 1;
	}

	printf("row_end_reduce_only contract check ok: max_abs_before_reduce=%d\n",
	       stats[VAR_ROW_END].max_abs_before_reduce);

	return 0;
}

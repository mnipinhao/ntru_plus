#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"

#define NTRUPLUS_NTT_REFERENCE_TEST
#include "../ntt.c"

#define GT_BRANCHES 2
#define GT_BRANCH_N (NTRUPLUS_N / GT_BRANCHES)
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_QUARTIC_LANES 4
#define RANDOM_TESTS 96

enum rowkernel_variant {
	ROWKERNEL_CURRENT,
	ROWKERNEL_NO_ENTRY,
	ROWKERNEL_NO_END,
	ROWKERNEL_NO_ENTRY_NO_END,
	ROWKERNEL_VARIANTS
};

enum row_stage {
	ROW_STAGE_INPUT,
	ROW_STAGE_AFTER_ENTRY,
	ROW_STAGE_AFTER_STAGE1,
	ROW_STAGE_AFTER_STAGE2,
	ROW_STAGE_AFTER_STAGE3,
	ROW_STAGE_AFTER_STAGE4,
	ROW_STAGE_AFTER_STAGE5,
	ROW_STAGE_AFTER_END,
	ROW_STAGE_COUNT
};

struct range_stat {
	int min;
	int max;
	int max_abs;
};

struct stage_stats {
	struct range_stat stage[ROW_STAGE_COUNT];
};

struct interval {
	int lo;
	int hi;
	int wraps_possible;
};

static const char *const variant_names[ROWKERNEL_VARIANTS] = {
	"current",
	"no_entry",
	"no_end",
	"no_entry_no_end",
};

static const char *const stage_names[ROW_STAGE_COUNT] = {
	"input",
	"after_entry",
	"after_stage1",
	"after_stage2",
	"after_stage3",
	"after_stage4",
	"after_stage5",
	"after_end",
};

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

static void range_init(struct range_stat *st)
{
	st->min = 32767;
	st->max = -32768;
	st->max_abs = 0;
}

static void stage_stats_init(struct stage_stats *stats)
{
	for (int i = 0; i < ROW_STAGE_COUNT; i++)
	{
		range_init(&stats->stage[i]);
	}
}

static int abs_i(int x)
{
	return x < 0 ? -x : x;
}

static void range_update(struct range_stat *st, int x)
{
	const int ax = abs_i(x);

	if (x < st->min)
	{
		st->min = x;
	}
	if (x > st->max)
	{
		st->max = x;
	}
	if (ax > st->max_abs)
	{
		st->max_abs = ax;
	}
}

static void range_update_vec(struct range_stat *st, const int16_t *a, int n)
{
	for (int i = 0; i < n; i++)
	{
		range_update(st, a[i]);
	}
}

static void stage_update(struct stage_stats *stats, enum row_stage stage,
                         const int16_t row[GT_ROW_N])
{
	if (stats != NULL)
	{
		range_update_vec(&stats->stage[stage], row, GT_ROW_N);
	}
}

static int modq_i64(int64_t a)
{
	int r = (int)(a % NTRUPLUS_Q);

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}

	return r;
}

static int centered_modq_i64(int64_t a)
{
	int r = modq_i64(a);

	if (r > NTRUPLUS_Q / 2)
	{
		r -= NTRUPLUS_Q;
	}

	return r;
}

static int equal_modq_i16(int16_t a, int16_t b)
{
	return modq_i64((int)a - (int)b) == 0;
}

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static int64_t arshift_i64(int64_t x, unsigned shift)
{
	if (x >= 0)
	{
		return x >> shift;
	}

	return -(((-x) + ((INT64_C(1) << shift) - 1)) >> shift);
}

static int16_t wrap16(int32_t x)
{
	return (int16_t)(uint16_t)x;
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
	const int64_t rounded = arshift_i64(doubled + (INT64_C(1) << 15), 16);

	return sat16(rounded);
}

static int16_t sqdmulh_s16(int16_t a, int16_t b)
{
	return sat16(arshift_i64(INT64_C(2) * a * b, 16));
}

static int16_t srshr_s16(int16_t a, unsigned shift)
{
	return (int16_t)arshift_i64((int64_t)a + (INT64_C(1) << (shift - 1)),
	                            shift);
}

static int16_t row_fqmul(int16_t a, int16_t mul, int16_t pre)
{
	const int16_t qhat = sqrdmulh_s16(a, pre);
	int16_t prod = wrap16((int32_t)a * mul);

	prod = wrap16((int32_t)prod - (int32_t)qhat * NTRUPLUS_Q);
	return prod;
}

static int16_t row_barrett(int16_t a)
{
	int16_t t = sqdmulh_s16(a, 19412);

	t = srshr_s16(t, 11);
	return wrap16((int32_t)a - (int32_t)t * NTRUPLUS_Q);
}

static void row_butterfly(int16_t a[GT_ROW_N], int lo, int hi,
                          int16_t mul, int16_t pre)
{
	const int16_t old_lo = a[lo];
	const int16_t prod = row_fqmul(a[hi], mul, pre);

	a[lo] = wrap16((int32_t)a[lo] + prod);
	a[hi] = wrap16((int32_t)old_lo - prod);
}

static void rowkernel_apply(int16_t out[GT_ROW_N], const int16_t in[GT_ROW_N],
                            enum rowkernel_variant variant,
                            struct stage_stats *stats)
{
	const int do_entry =
		variant == ROWKERNEL_CURRENT || variant == ROWKERNEL_NO_END;
	const int do_end =
		variant == ROWKERNEL_CURRENT || variant == ROWKERNEL_NO_ENTRY;

	memcpy(out, in, GT_ROW_N * sizeof(out[0]));
	stage_update(stats, ROW_STAGE_INPUT, out);

	if (do_entry)
	{
		for (int i = 0; i < GT_ROW_N; i++)
		{
			out[i] = row_barrett(out[i]);
		}
	}
	stage_update(stats, ROW_STAGE_AFTER_ENTRY, out);

	for (int base = 0; base < GT_ROW_N; base += 8)
	{
		row_butterfly(out, base + 0, base + 1,
		              stage123_mul[0], stage123_pre[0]);
		row_butterfly(out, base + 2, base + 3,
		              stage123_mul[0], stage123_pre[0]);
		row_butterfly(out, base + 4, base + 5,
		              stage123_mul[0], stage123_pre[0]);
		row_butterfly(out, base + 6, base + 7,
		              stage123_mul[0], stage123_pre[0]);
	}
	stage_update(stats, ROW_STAGE_AFTER_STAGE1, out);

	for (int base = 0; base < GT_ROW_N; base += 8)
	{
		row_butterfly(out, base + 0, base + 2,
		              stage123_mul[0], stage123_pre[0]);
		row_butterfly(out, base + 1, base + 3,
		              stage123_mul[1], stage123_pre[1]);
		row_butterfly(out, base + 4, base + 6,
		              stage123_mul[0], stage123_pre[0]);
		row_butterfly(out, base + 5, base + 7,
		              stage123_mul[1], stage123_pre[1]);
	}
	stage_update(stats, ROW_STAGE_AFTER_STAGE2, out);

	for (int base = 0; base < GT_ROW_N; base += 8)
	{
		row_butterfly(out, base + 0, base + 4,
		              stage123_mul[0], stage123_pre[0]);
		row_butterfly(out, base + 1, base + 5,
		              stage123_mul[2], stage123_pre[2]);
		row_butterfly(out, base + 2, base + 6,
		              stage123_mul[3], stage123_pre[3]);
		row_butterfly(out, base + 3, base + 7,
		              stage123_mul[4], stage123_pre[4]);
	}
	stage_update(stats, ROW_STAGE_AFTER_STAGE3, out);

	for (int j = 0; j < 8; j++)
	{
		row_butterfly(out, j, j + 8,
		              stage45_mul[j][0], stage45_pre[j][0]);
		row_butterfly(out, j + 16, j + 24,
		              stage45_mul[j][0], stage45_pre[j][0]);
	}
	stage_update(stats, ROW_STAGE_AFTER_STAGE4, out);

	for (int j = 0; j < 8; j++)
	{
		row_butterfly(out, j, j + 16,
		              stage45_mul[j][1], stage45_pre[j][1]);
		row_butterfly(out, j + 8, j + 24,
		              stage45_mul[j][2], stage45_pre[j][2]);
	}
	stage_update(stats, ROW_STAGE_AFTER_STAGE5, out);

	if (do_end)
	{
		for (int i = 0; i < GT_ROW_N; i++)
		{
			out[i] = row_barrett(out[i]);
		}
	}
	stage_update(stats, ROW_STAGE_AFTER_END, out);
}

static int block_index(int branch, int physical_j, int lane)
{
	return branch * GT_BRANCH_N + GT_QUARTIC_LANES * physical_j + lane;
}

static int physical_j_from_row_k32(int row, int k32)
{
	return (GT_ROW_N * row + GT_ROWS * k32) % (GT_ROWS * GT_ROW_N);
}

static int row_from_physical_j(int physical_j)
{
	return (2 * (physical_j % GT_ROWS)) % GT_ROWS;
}

static int k32_from_physical_j(int physical_j)
{
	const int row = row_from_physical_j(physical_j);

	for (int k32 = 0; k32 < GT_ROW_N; k32++)
	{
		if (physical_j_from_row_k32(row, k32) == physical_j)
		{
			return k32;
		}
	}

	return -1;
}

static int rowpack_index(int branch, int row, int lane, int k32)
{
	return branch * GT_BRANCH_N +
	       row * (GT_QUARTIC_LANES * GT_ROW_N) +
	       lane * GT_ROW_N + k32;
}

static void block_to_rowpack(int16_t rowpack[NTRUPLUS_N],
                             const int16_t block[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int physical_j = 0; physical_j < GT_ROWS * GT_ROW_N;
		     physical_j++)
		{
			const int row = row_from_physical_j(physical_j);
			const int k32 = k32_from_physical_j(physical_j);

			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				rowpack[rowpack_index(branch, row, lane, k32)] =
					block[block_index(branch, physical_j, lane)];
			}
		}
	}
}

static void rowpack_to_block(int16_t block[NTRUPLUS_N],
                             const int16_t rowpack[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int physical_j = 0; physical_j < GT_ROWS * GT_ROW_N;
		     physical_j++)
		{
			const int row = row_from_physical_j(physical_j);
			const int k32 = k32_from_physical_j(physical_j);

			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				block[block_index(branch, physical_j, lane)] =
					rowpack[rowpack_index(branch, row, lane, k32)];
			}
		}
	}
}

static void basemul_rowpack_scalar(int16_t r[NTRUPLUS_N],
                                   const int16_t a[NTRUPLUS_N],
                                   const int16_t b[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				int16_t aa[GT_QUARTIC_LANES];
				int16_t bb[GT_QUARTIC_LANES];
				int16_t rr[GT_QUARTIC_LANES];
				const int physical_j = physical_j_from_row_k32(row, k32);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					aa[lane] = a[rowpack_index(branch, row, lane, k32)];
					bb[lane] = b[rowpack_index(branch, row, lane, k32)];
				}

				basemul(rr, aa, bb, gt_rowbitrev_lambda[branch][physical_j]);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					r[rowpack_index(branch, row, lane, k32)] = rr[lane];
				}
			}
		}
	}
}

static void basemul_add_rowpack_scalar(int16_t r[NTRUPLUS_N],
                                       const int16_t a[NTRUPLUS_N],
                                       const int16_t b[NTRUPLUS_N],
                                       const int16_t c[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				int16_t aa[GT_QUARTIC_LANES];
				int16_t bb[GT_QUARTIC_LANES];
				int16_t cc[GT_QUARTIC_LANES];
				int16_t rr[GT_QUARTIC_LANES];
				const int physical_j = physical_j_from_row_k32(row, k32);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					aa[lane] = a[rowpack_index(branch, row, lane, k32)];
					bb[lane] = b[rowpack_index(branch, row, lane, k32)];
					cc[lane] = c[rowpack_index(branch, row, lane, k32)];
				}

				basemul_add(rr, aa, bb, cc,
				            gt_rowbitrev_lambda[branch][physical_j]);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					r[rowpack_index(branch, row, lane, k32)] = rr[lane];
				}
			}
		}
	}
}

static void fill_pattern(int16_t a[NTRUPLUS_N], unsigned pattern,
                         uint32_t seed)
{
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
			a[i] = (i & 3) == 0 ? NTRUPLUS_Q - 1 :
			       (i & 3) == 1 ? -(NTRUPLUS_Q - 1) :
			       (i & 3) == 2 ? NTRUPLUS_Q / 2 : -(NTRUPLUS_Q / 2);
			break;
		default:
			a[i] =
				(int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
				          NTRUPLUS_Q);
			break;
		}
	}
}

static int compare_modq_poly(const char *label,
                             const int16_t got[NTRUPLUS_N],
                             const int16_t want[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq_i16(got[i], want[i]))
		{
			fprintf(stderr,
			        "%s mismatch at %d: got %d want %d\n",
			        label,
			        i,
			        got[i],
			        want[i]);
			return 0;
		}
	}

	return 1;
}

static void rowpack_apply_rowkernels(int16_t work[NTRUPLUS_N],
                                     enum rowkernel_variant variant,
                                     struct stage_stats *stats)
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				int16_t out[GT_ROW_N];
				int16_t *plane = &work[rowpack_index(branch, row, lane, 0)];

				rowkernel_apply(out, plane, variant, stats);
				memcpy(plane, out, GT_ROW_N * sizeof(out[0]));
			}
		}
	}
}

static void rowpack_postmerge_from_rows(int16_t r[NTRUPLUS_N],
                                        const int16_t work[NTRUPLUS_N])
{
	int16_t branches[NTRUPLUS_N];

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_BRANCH_N;
		const int16_t *untwist =
			branch == 0 ? untwist_branch0 : untwist_branch1;

		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			int16_t mat[GT_ROWS][GT_ROW_N];

			for (int row = 0; row < GT_ROWS; row++)
			{
				for (int k32 = 0; k32 < GT_ROW_N; k32++)
				{
					mat[row][k32] =
						work[rowpack_index(branch, row, lane, k32)];
				}
			}

			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				dft3_inverse(&mat[0][k32], &mat[1][k32], &mat[2][k32]);
			}

			for (int n3 = 0; n3 < GT_ROWS; n3++)
			{
				for (int n32 = 0; n32 < GT_ROW_N; n32++)
				{
					const int n = (64 * n3 + 33 * n32) %
					              (GT_ROWS * GT_ROW_N);

					branches[branch_start + GT_QUARTIC_LANES * n + lane] =
						fqmul(mat[n3][n32], untwist[n]);
				}
			}
		}
	}

	for (int i = 0; i < GT_BRANCH_N; i++)
	{
		const int16_t t1 = branches[i] + branches[i + GT_BRANCH_N];
		const int16_t t2 =
			fqmul(NTRUPLUS_ZMINUSZ5INV,
			      branches[i] - branches[i + GT_BRANCH_N]);

		r[i] = fqmul(NTRUPLUS_NINV, t1 - t2);
		r[i + GT_BRANCH_N] = fqmul(NTRUPLUS_2NINV, t2);
	}
}

static void rowpack_invntt_variant(int16_t r[NTRUPLUS_N],
                                   const int16_t a[NTRUPLUS_N],
                                   enum rowkernel_variant variant,
                                   struct stage_stats *stats)
{
	int16_t work[NTRUPLUS_N];

	memcpy(work, a, sizeof(work));
	rowpack_apply_rowkernels(work, variant, stats);
	rowpack_postmerge_from_rows(r, work);
}

static void schoolbook_mul_reference(int16_t r[NTRUPLUS_N],
                                     const int16_t a[NTRUPLUS_N],
                                     const int16_t b[NTRUPLUS_N])
{
	int64_t tmp[2 * NTRUPLUS_N - 1];

	memset(tmp, 0, sizeof(tmp));

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		for (int j = 0; j < NTRUPLUS_N; j++)
		{
			tmp[i + j] += (int64_t)a[i] * b[j];
		}
	}

	for (int i = 2 * NTRUPLUS_N - 2; i >= NTRUPLUS_N; i--)
	{
		const int64_t c = tmp[i];

		tmp[i - NTRUPLUS_N / 2] += c;
		tmp[i - NTRUPLUS_N] -= c;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r[i] = (int16_t)centered_modq_i64(tmp[i]);
	}
}

static void prepare_rowpack_ntt(int16_t out[NTRUPLUS_N],
                                const int16_t natural[NTRUPLUS_N])
{
	int16_t block[NTRUPLUS_N];

	ntt_gt_rowbitrevlayout(block, natural);
	block_to_rowpack(out, block);
}

static int compare_rowkernel_rows(const char *label,
                                  const int16_t input[NTRUPLUS_N],
                                  enum rowkernel_variant variant)
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				int16_t current[GT_ROW_N];
				int16_t candidate[GT_ROW_N];
				const int16_t *plane =
					&input[rowpack_index(branch, row, lane, 0)];

				rowkernel_apply(current, plane, ROWKERNEL_CURRENT, NULL);
				rowkernel_apply(candidate, plane, variant, NULL);

				for (int k32 = 0; k32 < GT_ROW_N; k32++)
				{
					if (!equal_modq_i16(candidate[k32], current[k32]))
					{
						fprintf(stderr,
						        "%s row mismatch variant=%s branch=%d row=%d lane=%d k32=%d input=%d got=%d want=%d\n",
						        label,
						        variant_names[variant],
						        branch,
						        row,
						        lane,
						        k32,
						        plane[k32],
						        candidate[k32],
						        current[k32]);
						return 0;
					}
				}
			}
		}
	}

	return 1;
}

static void print_range_line(const char *label, const struct range_stat *st)
{
	printf("%s min=%d max=%d max_abs=%d\n",
	       label,
	       st->min,
	       st->max,
	       st->max_abs);
}

static void print_stage_stats(const char *path, const struct stage_stats *stats)
{
	for (int i = 0; i < ROW_STAGE_COUNT; i++)
	{
		char label[128];

		snprintf(label, sizeof(label), "%s_%s", path, stage_names[i]);
		print_range_line(label, &stats->stage[i]);
	}
}

static struct interval interval_from_range(int lo, int hi)
{
	struct interval out = { lo, hi, 0 };

	return out;
}

static void interval_note_wrap(struct interval *a)
{
	if (a->lo < -32768 || a->hi > 32767)
	{
		a->wraps_possible = 1;
	}
}

static struct interval fqmul_interval(struct interval in,
                                      const int16_t *mul,
                                      const int16_t *pre,
                                      int count)
{
	struct interval out = { 32767, -32768, in.wraps_possible };
	const int lo = in.lo < -32768 ? -32768 : in.lo;
	const int hi = in.hi > 32767 ? 32767 : in.hi;

	for (int x = lo; x <= hi; x++)
	{
		for (int i = 0; i < count; i++)
		{
			const int y = row_fqmul((int16_t)x, mul[i], pre[i]);

			if (y < out.lo)
			{
				out.lo = y;
			}
			if (y > out.hi)
			{
				out.hi = y;
			}
		}
	}

	return out;
}

static struct interval butterfly_interval(struct interval in,
                                          const int16_t *mul,
                                          const int16_t *pre,
                                          int count)
{
	const struct interval prod = fqmul_interval(in, mul, pre, count);
	struct interval out;

	out.lo = in.lo + prod.lo;
	out.hi = in.hi + prod.hi;
	if (in.lo - prod.hi < out.lo)
	{
		out.lo = in.lo - prod.hi;
	}
	if (in.hi - prod.lo > out.hi)
	{
		out.hi = in.hi - prod.lo;
	}
	out.wraps_possible = in.wraps_possible || prod.wraps_possible;
	interval_note_wrap(&out);

	return out;
}

static void print_interval_line(const char *label, struct interval a)
{
	printf("%s lo=%d hi=%d max_abs=%d wraps_possible=%d\n",
	       label,
	       a.lo,
	       a.hi,
	       abs_i(a.lo) > abs_i(a.hi) ? abs_i(a.lo) : abs_i(a.hi),
	       a.wraps_possible);
}

static void print_no_entry_no_end_interval_proof(const char *label,
                                                 int input_lo,
                                                 int input_hi)
{
	static const int16_t stage1_mul[] = { 1 };
	static const int16_t stage1_pre[] = { 9 };
	static const int16_t stage2_mul[] = { 1, 708 };
	static const int16_t stage2_pre[] = { 9, 6711 };
	static const int16_t stage3_mul[] = { 1, 1521, 708, -1716 };
	static const int16_t stage3_pre[] = { 9, 14417, 6711, -16266 };
	static const int16_t stage4_mul[] = {
		1, -39, 1521, -550, 708, 44, -1716, 1241,
	};
	static const int16_t stage4_pre[] = {
		9, -370, 14417, -5213, 6711, 417, -16266, 11763,
	};
	static const int16_t stage5_mul[] = {
		1, -436, -39, -281, 1521, 588, -550, 1267,
		708, -1015, 44, 1558, -1716, 1464, 1241, 1673,
	};
	static const int16_t stage5_pre[] = {
		9, -4133, -370, -2664, 14417, 5573, -5213, 12010,
		6711, -9621, 417, 14768, -16266, 13877, 11763, 15858,
	};
	struct interval a = interval_from_range(input_lo, input_hi);
	char line[160];

	snprintf(line, sizeof(line), "interval_%s_input", label);
	print_interval_line(line, a);
	a = butterfly_interval(a, stage1_mul, stage1_pre, 1);
	snprintf(line, sizeof(line), "interval_%s_after_stage1", label);
	print_interval_line(line, a);
	a = butterfly_interval(a, stage2_mul, stage2_pre, 2);
	snprintf(line, sizeof(line), "interval_%s_after_stage2", label);
	print_interval_line(line, a);
	a = butterfly_interval(a, stage3_mul, stage3_pre, 4);
	snprintf(line, sizeof(line), "interval_%s_after_stage3", label);
	print_interval_line(line, a);
	a = butterfly_interval(a, stage4_mul, stage4_pre, 8);
	snprintf(line, sizeof(line), "interval_%s_after_stage4", label);
	print_interval_line(line, a);
	a = butterfly_interval(a, stage5_mul, stage5_pre, 16);
	snprintf(line, sizeof(line), "interval_%s_after_stage5", label);
	print_interval_line(line, a);
}

static int check_path_case(const char *path_label,
                           const int16_t a[NTRUPLUS_N],
                           const int16_t b[NTRUPLUS_N],
                           const int16_t c[NTRUPLUS_N],
                           int is_add,
                           struct range_stat *basemul_range,
                           struct stage_stats variant_stats[ROWKERNEL_VARIANTS])
{
	int16_t want[NTRUPLUS_N];
	int16_t ntt_a[NTRUPLUS_N];
	int16_t ntt_b[NTRUPLUS_N];
	int16_t ntt_c[NTRUPLUS_N];
	int16_t rowpack_out[NTRUPLUS_N];
	int16_t got_current[NTRUPLUS_N];
	int16_t got_variant[NTRUPLUS_N];

	schoolbook_mul_reference(want, a, b);
	if (is_add)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			want[i] = (int16_t)centered_modq_i64((int64_t)want[i] + c[i]);
		}
	}

	prepare_rowpack_ntt(ntt_a, a);
	prepare_rowpack_ntt(ntt_b, b);
	if (is_add)
	{
		prepare_rowpack_ntt(ntt_c, c);
		basemul_add_rowpack_scalar(rowpack_out, ntt_a, ntt_b, ntt_c);
	}
	else
	{
		basemul_rowpack_scalar(rowpack_out, ntt_a, ntt_b);
	}

	range_update_vec(basemul_range, rowpack_out, NTRUPLUS_N);
	rowpack_invntt_variant(got_current, rowpack_out,
	                       ROWKERNEL_CURRENT,
	                       &variant_stats[ROWKERNEL_CURRENT]);

	if (!compare_modq_poly(path_label, got_current, want))
	{
		return 0;
	}

	for (int v = ROWKERNEL_NO_ENTRY; v < ROWKERNEL_VARIANTS; v++)
	{
		if (!compare_rowkernel_rows(path_label, rowpack_out,
		                            (enum rowkernel_variant)v))
		{
			return 0;
		}

		rowpack_invntt_variant(got_variant, rowpack_out,
		                       (enum rowkernel_variant)v,
		                       &variant_stats[v]);
		if (!compare_modq_poly(path_label, got_variant, got_current))
		{
			return 0;
		}
		if (!compare_modq_poly(path_label, got_variant, want))
		{
			return 0;
		}
	}

	return 1;
}

static int run_path_suite(const char *path_label, int is_add)
{
	int16_t a[NTRUPLUS_N];
	int16_t b[NTRUPLUS_N];
	int16_t c[NTRUPLUS_N];
	struct range_stat basemul_range;
	struct stage_stats variant_stats[ROWKERNEL_VARIANTS];

	range_init(&basemul_range);
	for (int v = 0; v < ROWKERNEL_VARIANTS; v++)
	{
		stage_stats_init(&variant_stats[v]);
	}

	for (unsigned pattern = 0; pattern < 5; pattern++)
	{
		fill_pattern(a, pattern, 0x243f6a88u + pattern);
		fill_pattern(b, pattern ^ 3U, 0x85a308d3u + pattern);
		fill_pattern(c, pattern ^ 1U, 0x13198a2eu + pattern);

		if (!check_path_case(path_label, a, b, c, is_add,
		                     &basemul_range, variant_stats))
		{
			return 0;
		}
	}

	for (int t = 0; t < RANDOM_TESTS; t++)
	{
		fill_pattern(a, 5, 0x6a09e667u + (uint32_t)t);
		fill_pattern(b, 5, 0xbb67ae85u + (uint32_t)(3 * t));
		fill_pattern(c, 5, 0x3c6ef372u + (uint32_t)(5 * t));

		if (!check_path_case(path_label, a, b, c, is_add,
		                     &basemul_range, variant_stats))
		{
			return 0;
		}
	}

	printf("path=%s randomized_adversarial_cases=%d correctness=ok\n",
	       path_label,
	       RANDOM_TESTS + 5);
	print_range_line(is_add ? "rowpack_basemul_add_out" :
	                 "rowpack_basemul_out",
	                 &basemul_range);
	print_no_entry_no_end_interval_proof(path_label,
	                                     basemul_range.min,
	                                     basemul_range.max);

	for (int v = 0; v < ROWKERNEL_VARIANTS; v++)
	{
		print_stage_stats(variant_names[v], &variant_stats[v]);
	}

	return 1;
}

static void interval_probe_for_range(const char *label, int lo, int hi)
{
	struct range_stat input;
	struct stage_stats stats;
	int16_t row[GT_ROW_N];
	int16_t out[GT_ROW_N];

	range_init(&input);
	stage_stats_init(&stats);

	for (int i = 0; i < GT_ROW_N; i++)
	{
		row[i] = (int16_t)((i & 1) ? lo : hi);
		range_update(&input, row[i]);
	}

	rowkernel_apply(out, row, ROWKERNEL_NO_ENTRY_NO_END, &stats);

	printf("adversarial_interval_probe label=%s lo=%d hi=%d\n", label, lo, hi);
	print_range_line("adversarial_input", &input);
	print_stage_stats("adversarial_no_entry_no_end", &stats);
}

int main(void)
{
	if (!run_path_suite("product", 0))
	{
		return 1;
	}
	if (!run_path_suite("product_add", 1))
	{
		return 1;
	}

	interval_probe_for_range("canonical", -(NTRUPLUS_Q / 2), NTRUPLUS_Q / 2);
	interval_probe_for_range("montgomery_raw", -(NTRUPLUS_Q - 1),
	                         NTRUPLUS_Q - 1);

	printf("rowpack no-entry/no-end lazy reduction contract: ok\n");
	return 0;
}

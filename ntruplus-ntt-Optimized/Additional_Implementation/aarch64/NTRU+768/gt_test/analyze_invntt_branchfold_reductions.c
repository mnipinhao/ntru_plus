#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "params.h"

#include "../ntt.c"

#define RANDOM_TESTS 128

enum variant {
	VAR_REDUCE_BOTH = 0,
	VAR_SKIP_LOW,
	VAR_SKIP_HIGH,
	VAR_SKIP_BOTH,
	VAR_COUNT
};

struct stats {
	const char *name;
	long long coeffs;
	long long exact_mismatch;
	long long modq_mismatch;
	long long mod3_mismatch;
	long long delta_0;
	long long delta_q;
	long long delta_neg_q;
	long long delta_2q;
	long long delta_neg_2q;
	long long delta_other;
	int min_out;
	int max_out;
	int min_before_reduce;
	int max_before_reduce;
};

static struct stats reduce_both_vs_exact;

static int centered(int x)
{
	x %= NTRUPLUS_Q;
	if (x < 0)
	{
		x += NTRUPLUS_Q;
	}
	if (x > NTRUPLUS_Q / 2)
	{
		x -= NTRUPLUS_Q;
	}
	return x;
}

static int modq_i(int x)
{
	x %= NTRUPLUS_Q;
	if (x < 0)
	{
		x += NTRUPLUS_Q;
	}
	return x;
}

static int mod3_i(int x)
{
	x %= 3;
	if (x < 0)
	{
		x += 3;
	}
	return x;
}

static int pow_mod(int a, int e)
{
	int64_t r = 1;
	int64_t b = modq_i(a);

	while (e > 0)
	{
		if (e & 1)
		{
			r = (r * b) % NTRUPLUS_Q;
		}
		b = (b * b) % NTRUPLUS_Q;
		e >>= 1;
	}

	return (int)r;
}

static int inv_mod(int a)
{
	return pow_mod(a, NTRUPLUS_Q - 2);
}

static int precompute(int m)
{
	const int64_t num = (int64_t)m * (1 << 15);

	if (num >= 0)
	{
		return (int)((num + NTRUPLUS_Q / 2) / NTRUPLUS_Q);
	}
	return -(int)((-num + NTRUPLUS_Q / 2) / NTRUPLUS_Q);
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

static int16_t asm_fqmul(int16_t a, int16_t mul, int16_t pre)
{
	const int16_t qhat = sqrdmulh_s16(a, pre);
	int16_t prod = wrap16((int32_t)a * mul);

	prod = wrap16((int32_t)prod - (int32_t)qhat * NTRUPLUS_Q);
	return prod;
}

static int16_t asm_barrett(int16_t a)
{
	int16_t t = sqdmulh_s16(a, 19412);

	t = srshr_s16(t, 11);
	return wrap16((int32_t)a - (int32_t)t * NTRUPLUS_Q);
}

static int16_t add16(int16_t a, int16_t b)
{
	return wrap16((int32_t)a + b);
}

static int16_t sub16(int16_t a, int16_t b)
{
	return wrap16((int32_t)a - b);
}

static void stats_init(struct stats stats[VAR_COUNT])
{
	static const char *names[VAR_COUNT] = {
		"reduce_both",
		"skip_low",
		"skip_high",
		"skip_both",
	};

	memset(stats, 0, sizeof(struct stats) * VAR_COUNT);
	for (int i = 0; i < VAR_COUNT; i++)
	{
		stats[i].name = names[i];
		stats[i].min_out = 32767;
		stats[i].max_out = -32768;
		stats[i].min_before_reduce = 32767;
		stats[i].max_before_reduce = -32768;
	}
}

static void stats_init_one(struct stats *stats, const char *name)
{
	memset(stats, 0, sizeof(*stats));
	stats->name = name;
	stats->min_out = 32767;
	stats->max_out = -32768;
	stats->min_before_reduce = 32767;
	stats->max_before_reduce = -32768;
}

static void range_add(int *min, int *max, int x)
{
	if (x < *min)
	{
		*min = x;
	}
	if (x > *max)
	{
		*max = x;
	}
}

static void fill_pattern(int16_t a[NTRUPLUS_N], const char *name, uint32_t seed)
{
	if (strcmp(name, "zero") == 0)
	{
		memset(a, 0, sizeof(int16_t) * NTRUPLUS_N);
		return;
	}

	if (strcmp(name, "one") == 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a[i] = 1;
		}
		return;
	}

	if (strcmp(name, "alternating_pm1") == 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a[i] = (i & 1) ? -1 : 1;
		}
		return;
	}

	if (strcmp(name, "centered_edges") == 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a[i] = (i & 1) ? -(NTRUPLUS_Q / 2) : (NTRUPLUS_Q / 2);
		}
		return;
	}

	if (strcmp(name, "lazy_edges") == 0)
	{
		static const int vals[] = {
			0, 1, -1,
			NTRUPLUS_Q - 1, -(NTRUPLUS_Q - 1),
			2 * (NTRUPLUS_Q - 1), -2 * (NTRUPLUS_Q - 1),
			3 * (NTRUPLUS_Q - 1), -3 * (NTRUPLUS_Q - 1),
		};

		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a[i] = (int16_t)vals[i % (int)(sizeof(vals) / sizeof(vals[0]))];
		}
		return;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		seed = seed * 1664525u + 1013904223u;
		a[i] = (int16_t)((int)(seed % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
	}
}

static void fill_impulse(int16_t a[NTRUPLUS_N], int pos, int16_t value)
{
	memset(a, 0, sizeof(int16_t) * NTRUPLUS_N);
	a[pos] = value;
}

static void row_outputs(int16_t rows[2][4][3][32], const int16_t freq[NTRUPLUS_N])
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int lane = 0; lane < 4; lane++)
		{
			int16_t mat[3][32];

			for (int j = 0; j < 96; j++)
			{
				const int k3 = (2 * j) % 3;
				const int k32_br = (11 * j) & 31;
				mat[k3][k32_br] =
					barrett_reduce(freq[branch_start + 4*j + lane]);
			}

			for (int k3 = 0; k3 < 3; k3++)
			{
				int16_t row[32];

				intt32_radix2_dit(row, mat[k3]);
				for (int k32 = 0; k32 < 32; k32++)
				{
					rows[branch][lane][k3][k32] = row[k32];
				}
			}
		}
	}
}

static void branchfold_variant(int16_t out[NTRUPLUS_N], const int16_t freq[NTRUPLUS_N],
                               enum variant variant, struct stats *stats)
{
	int16_t rows[2][4][3][32];
	const int inv192 = centered(inv_mod(192));
	const int inv96 = centered(inv_mod(96));
	const int z = 1634;
	const int low0_base = centered((1 - z) * inv192);
	const int low1_base = centered((1 + z) * inv192);
	const int high0_base = centered(z * inv96);
	const int high1_base = centered(-z * inv96);

	row_outputs(rows, freq);

	for (int k32 = 0; k32 < 32; k32++)
	{
		const int ks[3] = {
			(33 * k32) % 96,
			(33 * k32 + 64) % 96,
			(33 * k32 + 32) % 96,
		};

		for (int n3 = 0; n3 < 3; n3++)
		{
			const int k = ks[n3];
			const int f0 = centered(pow_mod(2, k));
			const int f1 = centered(pow_mod(22, k));
			const int low0 = centered(f0 * low0_base);
			const int low1 = centered(f1 * low1_base);
			const int high0 = centered(f0 * high0_base);
			const int high1 = centered(f1 * high1_base);
			const int low0_pre = precompute(low0);
			const int low1_pre = precompute(low1);
			const int high0_pre = precompute(high0);
			const int high1_pre = precompute(high1);

			for (int lane = 0; lane < 4; lane++)
			{
				int16_t dft[2];
				int16_t outlo;
				int16_t outhi;

				for (int branch = 0; branch < 2; branch++)
				{
					const int16_t r0 = rows[branch][lane][0][k32];
					const int16_t r1 = rows[branch][lane][1][k32];
					const int16_t r2 = rows[branch][lane][2][k32];
					const int16_t diff21 = sub16(r2, r1);
					const int16_t t = asm_fqmul(diff21, -723, -6853);

					if (n3 == 0)
					{
						dft[branch] = add16(add16(r0, r1), r2);
					}
					else if (n3 == 1)
					{
						dft[branch] = add16(sub16(r0, r1), t);
					}
					else
					{
						dft[branch] = sub16(sub16(r0, r2), t);
					}
				}

				outlo = add16(asm_fqmul(dft[0], low0, low0_pre),
				              asm_fqmul(dft[1], low1, low1_pre));
				outhi = add16(asm_fqmul(dft[0], high0, high0_pre),
				              asm_fqmul(dft[1], high1, high1_pre));

				range_add(&stats->min_before_reduce,
				          &stats->max_before_reduce, outlo);
				range_add(&stats->min_before_reduce,
				          &stats->max_before_reduce, outhi);

				if (variant != VAR_SKIP_LOW && variant != VAR_SKIP_BOTH)
				{
					outlo = asm_barrett(outlo);
				}
				if (variant != VAR_SKIP_HIGH && variant != VAR_SKIP_BOTH)
				{
					outhi = asm_barrett(outhi);
				}

				out[4*k + lane] = outlo;
				out[NTRUPLUS_N / 2 + 4*k + lane] = outhi;
			}
		}
	}
}

static void update_stats(struct stats *stats, const int16_t got[NTRUPLUS_N],
                         const int16_t want[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		const int delta = (int)got[i] - (int)want[i];

		stats->coeffs++;
		range_add(&stats->min_out, &stats->max_out, got[i]);
		if (got[i] != want[i])
		{
			stats->exact_mismatch++;
		}
		if (modq_i(delta) != 0)
		{
			stats->modq_mismatch++;
		}
		if (mod3_i(got[i]) != mod3_i(want[i]))
		{
			stats->mod3_mismatch++;
		}

		if (delta == 0)
		{
			stats->delta_0++;
		}
		else if (delta == NTRUPLUS_Q)
		{
			stats->delta_q++;
		}
		else if (delta == -NTRUPLUS_Q)
		{
			stats->delta_neg_q++;
		}
		else if (delta == 2 * NTRUPLUS_Q)
		{
			stats->delta_2q++;
		}
		else if (delta == -2 * NTRUPLUS_Q)
		{
			stats->delta_neg_2q++;
		}
		else
		{
			stats->delta_other++;
		}
	}
}

static void run_case(struct stats stats[VAR_COUNT], const int16_t input[NTRUPLUS_N])
{
	int16_t freq[NTRUPLUS_N];
	int16_t exact[NTRUPLUS_N];
	int16_t baseline[NTRUPLUS_N];
	int16_t got[NTRUPLUS_N];
	struct stats scratch[VAR_COUNT];

	ntt_gt_rowbitrevlayout(freq, input);
	invntt_gt_rowbitrevlayout_exact(exact, freq);
	stats_init(scratch);
	branchfold_variant(baseline, freq, VAR_REDUCE_BOTH,
	                   &scratch[VAR_REDUCE_BOTH]);
	update_stats(&reduce_both_vs_exact, baseline, exact);

	for (int v = 0; v < VAR_COUNT; v++)
	{
		branchfold_variant(got, freq, (enum variant)v, &stats[v]);
		update_stats(&stats[v], got, baseline);
	}
}

int main(void)
{
	static const char *patterns[] = {
		"zero", "one", "alternating_pm1", "centered_edges", "lazy_edges",
		"random",
	};
	struct stats stats[VAR_COUNT];
	int16_t input[NTRUPLUS_N];
	int cases = 0;

	stats_init(stats);
	stats_init_one(&reduce_both_vs_exact, "reduce_both_vs_exact");

	for (unsigned i = 0; i < sizeof(patterns) / sizeof(patterns[0]); i++)
	{
		fill_pattern(input, patterns[i], 0x12345678u + i);
		run_case(stats, input);
		cases++;
	}

	for (int t = 0; t < RANDOM_TESTS; t++)
	{
		fill_pattern(input, "random", 0x9e3779b9u + (uint32_t)t);
		run_case(stats, input);
		cases++;
	}

	for (int pos = 0; pos < NTRUPLUS_N; pos++)
	{
		fill_impulse(input, pos, (int16_t)(1 + (pos % 7)));
		run_case(stats, input);
		cases++;
	}

	printf("branchfold final-output reduction analyzer: cases=%d coeffs_per_variant=%lld\n",
	       cases, stats[0].coeffs);
	printf("comparison baseline: branchfold reduce_both model\n");
	printf("reduce_both_vs_exact %lld %lld %lld %lld %lld %lld %lld %lld %lld [%d,%d]\n",
	       reduce_both_vs_exact.exact_mismatch,
	       reduce_both_vs_exact.modq_mismatch,
	       reduce_both_vs_exact.mod3_mismatch,
	       reduce_both_vs_exact.delta_0,
	       reduce_both_vs_exact.delta_q,
	       reduce_both_vs_exact.delta_neg_q,
	       reduce_both_vs_exact.delta_2q,
	       reduce_both_vs_exact.delta_neg_2q,
	       reduce_both_vs_exact.delta_other,
	       reduce_both_vs_exact.min_out,
	       reduce_both_vs_exact.max_out);
	printf("variant exact_mismatch_vs_reduce_both modq_mismatch mod3_mismatch delta0 +q -q +2q -2q other out_range before_reduce_range\n");
	for (int v = 0; v < VAR_COUNT; v++)
	{
		printf("%s %lld %lld %lld %lld %lld %lld %lld %lld %lld [%d,%d] [%d,%d]\n",
		       stats[v].name,
		       stats[v].exact_mismatch,
		       stats[v].modq_mismatch,
		       stats[v].mod3_mismatch,
		       stats[v].delta_0,
		       stats[v].delta_q,
		       stats[v].delta_neg_q,
		       stats[v].delta_2q,
		       stats[v].delta_neg_2q,
		       stats[v].delta_other,
		       stats[v].min_out,
		       stats[v].max_out,
		       stats[v].min_before_reduce,
		       stats[v].max_before_reduce);
	}

	if (stats[VAR_REDUCE_BOTH].exact_mismatch != 0 ||
	    stats[VAR_REDUCE_BOTH].modq_mismatch != 0)
	{
		fprintf(stderr, "reduce_both baseline self-comparison failed\n");
		return 1;
	}

	return 0;
}

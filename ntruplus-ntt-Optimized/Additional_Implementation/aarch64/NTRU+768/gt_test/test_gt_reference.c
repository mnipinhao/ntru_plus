#include <stdint.h>
#include <stdio.h>

/*
 * Debug-only harness. Include ntt.c directly so this file checks the same
 * static Montgomery helpers, twist/untwist tables, and Good-Thomas kernels
 * used by the implementation.
 */
#define NTRUPLUS_NTT_REFERENCE_TEST
#include "../ntt.c"

#define TEST_VECTORS 8
#define OMEGA96_NORMAL 675

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

static int modq(int64_t a)
{
	int r = a % NTRUPLUS_Q;

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}

	return r;
}

static int field_mul(int a, int b)
{
	return (int)(((int64_t)modq(a) * modq(b)) % NTRUPLUS_Q);
}

static int field_pow(int a, int e)
{
	int r = 1;
	int b = modq(a);

	while (e > 0)
	{
		if (e & 1)
		{
			r = field_mul(r, b);
		}

		b = field_mul(b, b);
		e >>= 1;
	}

	return r;
}

static int field_inv(int a)
{
	return field_pow(a, NTRUPLUS_Q - 2);
}

static int16_t to_mont(int a)
{
	return montgomery_reduce((int32_t)modq(a) * NTRUPLUS_RSQ);
}

static int normal_from_mont(int16_t a)
{
	return modq(montgomery_reduce(a));
}

static int centered_normal_from_mont(int16_t a)
{
	int r = normal_from_mont(a);

	if (r > NTRUPLUS_Q / 2)
	{
		r -= NTRUPLUS_Q;
	}

	return r;
}

static int equal_modq(int16_t a, int16_t b)
{
	return modq(a - b) == 0;
}

static void fill_input(int16_t a[NTRUPLUS_N], uint32_t seed)
{
	uint32_t s = seed + 1;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		s = s * 1664525u + 1013904223u;
		a[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
	}
}

static int coeff_match_count(const int16_t a[NTRUPLUS_N],
                             const int16_t b[NTRUPLUS_N])
{
	int count = 0;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		count += equal_modq(a[i], b[i]);
	}

	return count;
}

static int coeff32_match_count(const int16_t a[32], const int16_t b[32])
{
	int count = 0;

	for (int i = 0; i < 32; i++)
	{
		count += equal_modq(a[i], b[i]);
	}

	return count;
}

static int check_inverse_scaling_constants(void)
{
	int ok = 1;

	ok &= centered_normal_from_mont(NTRUPLUS_NINV) == -18;
	ok &= centered_normal_from_mont(NTRUPLUS_2NINV) == -36;
	ok &= centered_normal_from_mont(NTRUPLUS_ZMINUSZ5INV) == 1634;

	if (!ok)
	{
		printf("inverse scaling constant check failed: "
		       "1/192=%d 1/96=%d zminusz5inv=%d\n",
		       centered_normal_from_mont(NTRUPLUS_NINV),
		       centered_normal_from_mont(NTRUPLUS_2NINV),
		       centered_normal_from_mont(NTRUPLUS_ZMINUSZ5INV));
		return 0;
	}

	printf("inverse scaling constants: ok (1/192=-18, 1/96=-36, zminusz5inv=1634)\n");
	return 1;
}

static void split_layer_reference(int16_t r[NTRUPLUS_N],
                                  const int16_t a[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		const int16_t t1 = fqmul(NTRUPLUS_ZETA_TOP_SPLIT,
		                         a[i + NTRUPLUS_N / 2]);

		r[i + NTRUPLUS_N / 2] = a[i] + a[i + NTRUPLUS_N / 2] - t1;
		r[i                 ] = a[i]                         + t1;
	}
}

static void direct_ntt32(int16_t out[32], const int16_t in[32])
{
	for (int j = 0; j < 32; j++)
	{
		const int omega32 = field_pow(OMEGA96_NORMAL, 3);
		const int alpha = field_pow(omega32, j);
		int power = 1;
		int acc = 0;

		for (int k = 0; k < 32; k++)
		{
			acc = (acc + field_mul(in[k], power)) % NTRUPLUS_Q;
			power = field_mul(power, alpha);
		}

		out[j] = (int16_t)acc;
	}
}

static void direct_ntt96(int16_t out[96], const int16_t in[96])
{
	for (int j = 0; j < 96; j++)
	{
		const int alpha = field_pow(OMEGA96_NORMAL, j);
		int power = 1;
		int acc = 0;

		for (int k = 0; k < 96; k++)
		{
			acc = (acc + field_mul(in[k], power)) % NTRUPLUS_Q;
			power = field_mul(power, alpha);
		}

		out[j] = (int16_t)acc;
	}
}

static unsigned rowbitrev_logical_index(unsigned physical_j)
{
	const unsigned k3 = (2 * physical_j) % 3;
	const unsigned k32_br = (11 * physical_j) & 31U;
	const unsigned logical_k32 = bitreverse5(k32_br);

	return gt96_output_crt_index(k3, logical_k32);
}

static void direct_gt_rowbitrev(int16_t out[NTRUPLUS_N],
                                const int16_t a[NTRUPLUS_N],
                                const int factors[2])
{
	int16_t split[NTRUPLUS_N];

	split_layer_reference(split, a);

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int twist_step = field_inv(factors[branch]);
		int twist_power = 1;

		for (int k = 0; k < 96; k++)
		{
			const int16_t twist = to_mont(twist_power);

			for (int lane = 0; lane < 4; lane++)
			{
				split[branch_start + 4*k + lane] =
					fqmul(split[branch_start + 4*k + lane], twist);
			}

			twist_power = field_mul(twist_power, twist_step);
		}

		for (int lane = 0; lane < 4; lane++)
		{
			int16_t in[96];
			int16_t direct[96];

			for (int k = 0; k < 96; k++)
			{
				in[k] = split[branch_start + 4*k + lane];
			}

			direct_ntt96(direct, in);

			for (int physical_j = 0; physical_j < 96; physical_j++)
			{
				const unsigned logical_j =
					rowbitrev_logical_index((unsigned)physical_j);

				out[branch_start + 4*physical_j + lane] = direct[logical_j];
			}
		}
	}
}

static int check_twist_tables(void)
{
	const int f0 = normal_from_mont(untwist_branch0[1]);
	const int f1 = normal_from_mont(untwist_branch1[1]);
	const int f0_inv = field_inv(f0);
	const int f1_inv = field_inv(f1);
	int f0_power = 1;
	int f1_power = 1;
	int f0_inv_power = 1;
	int f1_inv_power = 1;

	for (int i = 0; i < 96; i++)
	{
		if (normal_from_mont(untwist_branch0[i]) != f0_power ||
		    normal_from_mont(untwist_branch1[i]) != f1_power ||
		    normal_from_mont(twist_branch0[i]) != f0_inv_power ||
		    normal_from_mont(twist_branch1[i]) != f1_inv_power ||
		    !equal_modq(fqmul(untwist_branch0[i], twist_branch0[i]), NTRUPLUS_R) ||
		    !equal_modq(fqmul(untwist_branch1[i], twist_branch1[i]), NTRUPLUS_R))
		{
			printf("twist/untwist table check failed at i=%d\n", i);
			return 0;
		}

		f0_power = field_mul(f0_power, f0);
		f1_power = field_mul(f1_power, f1);
		f0_inv_power = field_mul(f0_inv_power, f0_inv);
		f1_inv_power = field_mul(f1_inv_power, f1_inv);
	}

	printf("twist/untwist table check: ok (F0=%d, F1=%d)\n", f0, f1);
	return 1;
}

static int check_gt_rowbitrev_lambda_table(const int factors[2])
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int factor_inv = field_inv(factors[branch]);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const unsigned logical_j =
				rowbitrev_logical_index((unsigned)physical_j);
			const int expected =
				field_mul(field_pow(OMEGA96_NORMAL, (int)logical_j), factor_inv);
			const int actual =
				normal_from_mont(gt_rowbitrev_lambda[branch][physical_j]);

			if (actual != expected)
			{
				printf("gt_rowbitrev_lambda mismatch: branch=%d physical_j=%d "
				       "logical_j=%u actual_normal=%d expected_normal=%d\n",
				       branch, physical_j, logical_j, actual, expected);
				return 0;
			}
		}
	}

	printf("gt_rowbitrev_lambda physical-order table check: ok\n");
	return 1;
}

static int check_ntt32_radix2_ct_bitrev(void)
{
	int min_matches = 32;
	int16_t in[32];
	int16_t direct[32];
	int16_t rowbitrev[32];
	int16_t expected_bitrev[32];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		uint32_t s = 0xd1b54a35u ^ seed;

		for (int i = 0; i < 32; i++)
		{
			s = s * 1664525u + 1013904223u;
			in[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
		}

		direct_ntt32(direct, in);
		ntt32_radix2_ct_bitrev(rowbitrev, in);

		for (int k = 0; k < 32; k++)
		{
			expected_bitrev[bitreverse5((unsigned)k)] = direct[k];
		}

		const int matches = coeff32_match_count(expected_bitrev, rowbitrev);
		if (matches < min_matches)
		{
			min_matches = matches;
		}
	}

	printf("ntt32_radix2_ct_bitrev complete row-bitrev check: %d/32 minimum coefficient match\n",
	       min_matches);
	return min_matches == 32;
}

static int check_ntt96_goodthomas(void)
{
	int min_matches = 96;
	int16_t in[96];
	int16_t direct[96];
	int16_t gt[96];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		uint32_t s = 0x9e3779b9u ^ seed;

		for (int i = 0; i < 96; i++)
		{
			s = s * 1664525u + 1013904223u;
			in[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
		}

		direct_ntt96(direct, in);
		ntt96_goodthomas(gt, in);

		int matches = 0;
		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const unsigned logical_j =
				rowbitrev_logical_index((unsigned)physical_j);

			matches += equal_modq(gt[physical_j], direct[logical_j]);
		}
		if (matches < min_matches)
		{
			min_matches = matches;
		}
	}

	printf("ntt96_goodthomas complete row-bitrev check: %d/96 minimum coefficient match\n",
	       min_matches);
	return min_matches == 96;
}

static int check_intt32_radix2_dit(void)
{
	int min_roundtrip = 32;
	int16_t in[32];
	int16_t freq[32];
	int16_t fast[32];
	int16_t scaled[32];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		uint32_t s = 0x165667b1u ^ seed;
		int matches = 0;

		for (int i = 0; i < 32; i++)
		{
			s = s * 1664525u + 1013904223u;
			in[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
		}

		for (int i = 0; i < 32; i++)
		{
			scaled[i] = (int16_t)field_mul(in[i], 32);
		}

		ntt32_radix2_ct_bitrev(freq, in);
		intt32_radix2_dit(fast, freq);
		matches = coeff32_match_count(scaled, fast);
		if (matches < min_roundtrip)
		{
			min_roundtrip = matches;
		}
	}

	printf("intt32_radix2_dit roundtrip: %d/32 after 32 scaling\n",
	       min_roundtrip);
	return min_roundtrip == 32;
}

static int check_invntt96_goodthomas(void)
{
	int min_matches = 96;
	int16_t in[96];
	int16_t freq[96];
	int16_t inv[96];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		uint32_t s = 0xc2b2ae35u ^ seed;
		int matches = 0;

		for (int i = 0; i < 96; i++)
		{
			s = s * 1664525u + 1013904223u;
			in[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
		}

		ntt96_goodthomas(freq, in);
		invntt96_goodthomas(inv, freq);

		for (int i = 0; i < 96; i++)
		{
			matches += equal_modq(inv[i], field_mul(in[i], 96));
		}

		if (matches < min_matches)
		{
			min_matches = matches;
		}
	}

	printf("invntt96_goodthomas check: %d/96 minimum coefficient match after 96 scaling\n",
	       min_matches);
	return min_matches == 96;
}

static int check_invntt96_goodthomas_rowfirst(void)
{
	int min_scaled_matches = 96;
	int min_legacy_matches = 96;
	int16_t in[96];
	int16_t freq[96];
	int16_t legacy[96];
	int16_t rowfirst[96];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		uint32_t s = 0x85ebca6bu ^ seed;
		int scaled_matches = 0;
		int legacy_matches = 0;
		int unscaled_matches = 0;
		int scaled192_matches = 0;

		for (int i = 0; i < 96; i++)
		{
			s = s * 1664525u + 1013904223u;
			in[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
		}

		ntt96_goodthomas(freq, in);
		invntt96_goodthomas(legacy, freq);
		invntt96_goodthomas_rowfirst(rowfirst, freq);

		for (int i = 0; i < 96; i++)
		{
			scaled_matches += equal_modq(rowfirst[i], field_mul(in[i], 96));
			legacy_matches += equal_modq(rowfirst[i], legacy[i]);
			unscaled_matches += equal_modq(rowfirst[i], in[i]);
			scaled192_matches += equal_modq(rowfirst[i], field_mul(in[i], 192));
		}

		if (scaled_matches < min_scaled_matches)
		{
			min_scaled_matches = scaled_matches;
		}
		if (legacy_matches < min_legacy_matches)
		{
			min_legacy_matches = legacy_matches;
		}
		if (unscaled_matches == 96 || scaled192_matches == 96)
		{
			printf("invntt96 row-first scaling regression: seed=%u "
			       "unscaled=%d scaled192=%d\n",
			       seed, unscaled_matches, scaled192_matches);
			return 0;
		}
	}

	printf("invntt96 row-first check: scaled %d/96, legacy-equivalent %d/96\n",
	       min_scaled_matches, min_legacy_matches);
	return min_scaled_matches == 96 && min_legacy_matches == 96;
}

static int check_full_ntt_gt_rowbitrev_direct(const int factors[2])
{
	int min_vs_direct = NTRUPLUS_N;
	int min_public = NTRUPLUS_N;
	int16_t a[NTRUPLUS_N];
	int16_t direct[NTRUPLUS_N];
	int16_t gt[NTRUPLUS_N];
	int16_t public_ntt[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		fill_input(a, seed);
		direct_gt_rowbitrev(direct, a, factors);

		ntt_gt_rowbitrevlayout(gt, a);
		ntt(public_ntt, a);

		int matches = coeff_match_count(direct, gt);
		if (matches < min_vs_direct)
		{
			min_vs_direct = matches;
		}

		matches = coeff_match_count(gt, public_ntt);
		if (matches < min_public)
		{
			min_public = matches;
		}
	}

	printf("full ntt GT-row-bitrev layout: vs direct %d/768, public ntt %d/768\n",
	       min_vs_direct, min_public);
	return min_vs_direct == NTRUPLUS_N && min_public == NTRUPLUS_N;
}

static int check_invntt_gt_rowbitrevlayout_roundtrip(void)
{
	int min_gt = NTRUPLUS_N;
	int min_public = NTRUPLUS_N;
	int16_t a[NTRUPLUS_N];
	int16_t gt_ntt[NTRUPLUS_N];
	int16_t public_ntt[NTRUPLUS_N];
	int16_t round[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		fill_input(a, seed);

		ntt_gt_rowbitrevlayout(gt_ntt, a);
		invntt_gt_rowbitrevlayout(round, gt_ntt);
		int matches = coeff_match_count(a, round);
		if (matches < min_gt)
		{
			min_gt = matches;
		}

		ntt(public_ntt, a);
		invntt(round, public_ntt);
		matches = coeff_match_count(a, round);
		if (matches < min_public)
		{
			min_public = matches;
		}
	}

	printf("invntt_gt_rowbitrevlayout roundtrip: direct %d/768, public ntt/invntt %d/768\n",
	       min_gt, min_public);
	return min_gt == NTRUPLUS_N && min_public == NTRUPLUS_N;
}

static int check_invntt_gt_rowbitrevlayout_impulses(void)
{
	int16_t a[NTRUPLUS_N];
	int16_t freq[NTRUPLUS_N];
	int16_t round[NTRUPLUS_N];

	for (int pos = 0; pos < NTRUPLUS_N; pos++)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a[i] = 0;
		}
		a[pos] = 1;

		ntt_gt_rowbitrevlayout(freq, a);
		invntt_gt_rowbitrevlayout_exact(round, freq);

		const int matches = coeff_match_count(a, round);
		if (matches != NTRUPLUS_N)
		{
			printf("invntt exact impulse roundtrip mismatch: pos=%d matches=%d/768\n",
			       pos, matches);
			return 0;
		}
		if (equal_modq(round[pos], 96) || equal_modq(round[pos], 192))
		{
			printf("invntt exact impulse scaling regression: pos=%d value=%d\n",
			       pos, round[pos]);
			return 0;
		}
	}

	printf("invntt exact impulse roundtrip: ok (768/768 positions)\n");
	return 1;
}

static int check_invntt_gt_rowbitrevlayout_random_extended(void)
{
	int min_matches = NTRUPLUS_N;
	int16_t a[NTRUPLUS_N];
	int16_t freq[NTRUPLUS_N];
	int16_t round[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < 32; seed++)
	{
		fill_input(a, 0x7f4a7c15u ^ seed);
		ntt_gt_rowbitrevlayout(freq, a);
		invntt_gt_rowbitrevlayout_exact(round, freq);

		const int matches = coeff_match_count(a, round);
		if (matches < min_matches)
		{
			min_matches = matches;
		}
	}

	printf("invntt exact random roundtrip: %d/768 minimum coefficient match\n",
	       min_matches);
	return min_matches == NTRUPLUS_N;
}

static void fill_lazy_edge_input(int16_t a[NTRUPLUS_N], int pattern)
{
	static const int16_t values[] = {
		NTRUPLUS_Q - 1,
		-(NTRUPLUS_Q - 1),
		3 * (NTRUPLUS_Q - 1),
		-3 * (NTRUPLUS_Q - 1),
		4 * (NTRUPLUS_Q - 1),
		-4 * (NTRUPLUS_Q - 1),
	};

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		a[i] = values[(i + pattern) % (int)(sizeof(values) / sizeof(values[0]))];
	}
}

static int check_invntt_gt_rowbitrevlayout_lazy_edges(void)
{
	int min_matches = NTRUPLUS_N;
	int16_t a[NTRUPLUS_N];
	int16_t freq[NTRUPLUS_N];
	int16_t round[NTRUPLUS_N];

	for (int pattern = 0; pattern < 6; pattern++)
	{
		fill_lazy_edge_input(a, pattern);
		ntt_gt_rowbitrevlayout(freq, a);
		invntt_gt_rowbitrevlayout_exact(round, freq);

		const int matches = coeff_match_count(a, round);
		if (matches < min_matches)
		{
			min_matches = matches;
		}
	}

	printf("invntt exact lazy-edge roundtrip: %d/768 minimum coefficient match\n",
	       min_matches);
	return min_matches == NTRUPLUS_N;
}

static void schoolbook_mul_reference(int16_t r[NTRUPLUS_N],
                                     const int16_t a[NTRUPLUS_N],
                                     const int16_t b[NTRUPLUS_N])
{
	int64_t tmp[2*NTRUPLUS_N - 1];

	for (int i = 0; i < 2*NTRUPLUS_N - 1; i++)
	{
		tmp[i] = 0;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		for (int j = 0; j < NTRUPLUS_N; j++)
		{
			tmp[i + j] += (int64_t)a[i] * b[j];
		}
	}

	/* NTRU+768 works modulo X^768 - X^384 + 1, so X^768 = X^384 - 1. */
	for (int i = 2*NTRUPLUS_N - 2; i >= NTRUPLUS_N; i--)
	{
		const int64_t c = tmp[i];

		tmp[i - NTRUPLUS_N/2] += c;
		tmp[i - NTRUPLUS_N] -= c;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r[i] = (int16_t)modq(tmp[i]);
	}
}

static void rowbitrev_basemul_reference(int16_t r[NTRUPLUS_N],
                                        const int16_t a[NTRUPLUS_N],
                                        const int16_t b[NTRUPLUS_N])
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4*physical_j;

			basemul(r + pos, a + pos, b + pos,
			        gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
}

static int rowbitrev_baseinv_reference(int16_t r[NTRUPLUS_N],
                                       const int16_t a[NTRUPLUS_N])
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4*physical_j;

			if (baseinv(r + pos, a + pos,
			            gt_rowbitrev_lambda[branch][physical_j]))
			{
				for (int i = 0; i < NTRUPLUS_N; i++)
				{
					r[i] = 0;
				}

				return 1;
			}
		}
	}

	return 0;
}

static int check_gt_rowbitrev_multiplication(void)
{
	int min_vs_schoolbook = NTRUPLUS_N;
	int16_t a[NTRUPLUS_N];
	int16_t b[NTRUPLUS_N];
	int16_t schoolbook[NTRUPLUS_N];
	int16_t natural_a[NTRUPLUS_N];
	int16_t natural_b[NTRUPLUS_N];
	int16_t natural_c[NTRUPLUS_N];
	int16_t natural_round[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		fill_input(a, seed);
		fill_input(b, seed + 0x100u);
		schoolbook_mul_reference(schoolbook, a, b);

		ntt_gt_rowbitrevlayout(natural_a, a);
		ntt_gt_rowbitrevlayout(natural_b, b);
		rowbitrev_basemul_reference(natural_c, natural_a, natural_b);
		invntt_gt_rowbitrevlayout(natural_round, natural_c);

		const int matches = coeff_match_count(schoolbook, natural_round);
		if (matches < min_vs_schoolbook)
		{
			min_vs_schoolbook = matches;
		}
	}

	printf("GT-row-bitrev multiplication: vs schoolbook %d/768\n",
	       min_vs_schoolbook);
	return min_vs_schoolbook == NTRUPLUS_N;
}

static int check_gt_rowbitrev_basemul_add(void)
{
	for (int branch = 0; branch < 2; branch++)
	{
		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int16_t zeta = gt_rowbitrev_lambda[branch][physical_j];
			int16_t a[4];
			int16_t b[4];
			int16_t c[4];
			int16_t prod[4];
			int16_t add[4];
			uint32_t s = (uint32_t)(0xc2b2ae35u + 389u * branch +
			                         17u * physical_j);

			for (int lane = 0; lane < 4; lane++)
			{
				s = s * 1664525u + 1013904223u;
				a[lane] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
				s = s * 1664525u + 1013904223u;
				b[lane] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
				s = s * 1664525u + 1013904223u;
				c[lane] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
			}

			basemul(prod, a, b, zeta);
			basemul_add(add, a, b, c, zeta);

			for (int lane = 0; lane < 4; lane++)
			{
				if (!equal_modq(add[lane], prod[lane] + c[lane]))
				{
					printf("rowbitrev basemul_add mismatch: branch=%d physical_j=%d lane=%d\n",
					       branch, physical_j, lane);
					return 0;
				}
			}
		}
	}

	printf("GT-row-bitrev basemul_add check: ok\n");
	return 1;
}

static int check_gt_rowbitrev_baseinv(void)
{
	int checked = 0;

	for (int branch = 0; branch < 2; branch++)
	{
		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int16_t zeta = gt_rowbitrev_lambda[branch][physical_j];
			int16_t a[4];
			int16_t inv[4];
			int16_t prod[4];
			uint32_t s = (uint32_t)(0x85ebca6bu + 307u * branch +
			                         11u * physical_j);

			for (int lane = 0; lane < 4; lane++)
			{
				s = s * 1664525u + 1013904223u;
				a[lane] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
			}

			if (baseinv(inv, a, zeta))
			{
				continue;
			}

			basemul(prod, a, inv, zeta);

			if (!equal_modq(prod[0], 1) ||
			    !equal_modq(prod[1], 0) ||
			    !equal_modq(prod[2], 0) ||
			    !equal_modq(prod[3], 0))
			{
				printf("rowbitrev baseinv mismatch: branch=%d physical_j=%d\n",
				       branch, physical_j);
				return 0;
			}

			checked++;
		}
	}

	printf("GT-row-bitrev baseinv check: %d invertible blocks checked\n",
	       checked);
	return checked > 0;
}

static int check_gt_rowbitrev_poly_baseinv_identity(void)
{
	int16_t a[NTRUPLUS_N] = {0};
	int16_t inv[NTRUPLUS_N];
	int16_t prod[NTRUPLUS_N];

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4*physical_j;

			a[pos] = 1;
		}
	}

	if (rowbitrev_baseinv_reference(inv, a))
	{
		printf("GT-row-bitrev polynomial baseinv identity unexpectedly failed\n");
		return 0;
	}

	rowbitrev_basemul_reference(prod, a, inv);

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq(prod[i], a[i]))
		{
			printf("GT-row-bitrev polynomial baseinv identity mismatch: i=%d\n", i);
			return 0;
		}
	}

	printf("GT-row-bitrev polynomial baseinv identity check: ok\n");
	return 1;
}

int main(void)
{
	const int f0 = normal_from_mont(untwist_branch0[1]);
	const int f1 = normal_from_mont(untwist_branch1[1]);
	const int branch_factors[2] = {f0, f1};
	int ok = 1;

	ok &= check_inverse_scaling_constants();
	ok &= check_twist_tables();
	ok &= check_gt_rowbitrev_lambda_table(branch_factors);
	ok &= check_ntt32_radix2_ct_bitrev();
	ok &= check_ntt96_goodthomas();
	ok &= check_intt32_radix2_dit();
	ok &= check_invntt96_goodthomas();
	ok &= check_invntt96_goodthomas_rowfirst();
	ok &= check_full_ntt_gt_rowbitrev_direct(branch_factors);
	ok &= check_invntt_gt_rowbitrevlayout_roundtrip();
	ok &= check_invntt_gt_rowbitrevlayout_impulses();
	ok &= check_invntt_gt_rowbitrevlayout_random_extended();
	ok &= check_invntt_gt_rowbitrevlayout_lazy_edges();
	ok &= check_gt_rowbitrev_multiplication();
	ok &= check_gt_rowbitrev_basemul_add();
	ok &= check_gt_rowbitrev_baseinv();
	ok &= check_gt_rowbitrev_poly_baseinv_identity();

	return ok ? 0 : 1;
}

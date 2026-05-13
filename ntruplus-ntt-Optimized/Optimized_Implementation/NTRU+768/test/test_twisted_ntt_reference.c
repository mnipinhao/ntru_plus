#include <stdint.h>
#include <stdio.h>

/*
 * Debug-only harness. Include ntt.c directly so this file checks the same
 * static Montgomery helpers and twist tables used by the implementation.
 */
#define NTRUPLUS_NTT_REFERENCE_TEST
#include "../ntt.c"

#define TEST_VECTORS 8

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

static int lambda_for_block(int branch, int block)
{
	int lambda = normal_from_mont(zetas[96 + 48*branch + block/2]);

	if (block & 1)
	{
		lambda = modq(-lambda);
	}

	return lambda;
}

static void split_layer_reference(int16_t r[NTRUPLUS_N],
                                  const int16_t a[NTRUPLUS_N])
{
	int16_t t1;
	int16_t zeta1 = zetas[1];

	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		t1 = fqmul(zeta1, a[i + NTRUPLUS_N / 2]);

		r[i + NTRUPLUS_N / 2] = a[i] + a[i + NTRUPLUS_N / 2] - t1;
		r[i                 ] = a[i]                         + t1;
	}
}

static void original_ntt_reference(int16_t r[NTRUPLUS_N],
                                   const int16_t a[NTRUPLUS_N])
{
	int16_t t1, t2, t3;
	int16_t zeta1, zeta2;
	int k = 1;

	zeta1 = zetas[k++];

	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		t1 = fqmul(zeta1, a[i + NTRUPLUS_N / 2]);

		r[i + NTRUPLUS_N / 2] = a[i] + a[i + NTRUPLUS_N / 2] - t1;
		r[i                 ] = a[i]                         + t1;
	}

	for (int start = 0; start < NTRUPLUS_N; start += 384)
	{
		zeta1 = zetas[k++];
		zeta2 = zetas[k++];

		for (int i = start; i < start + 128; i++)
		{
			t1 = fqmul(zeta1, r[i + 128]);
			t2 = fqmul(zeta2, r[i + 256]);
			t3 = fqmul(NTRUPLUS_OMEGA, t1 - t2);

			r[i + 256] = r[i] - t1 - t3;
			r[i + 128] = r[i] - t2 + t3;
			r[i      ] = r[i] + t1 + t2;
		}
	}

	for (int step = 64; step >= 4; step >>= 1)
	{
		for (int start = 0; start < NTRUPLUS_N; start += (step << 1))
		{
			zeta1 = zetas[k++];

			for (int i = start; i < start + step; i++)
			{
				t1 = fqmul(zeta1, r[i + step]);

				r[i + step] = barrett_reduce(r[i] - t1);
				r[i       ] = barrett_reduce(r[i] + t1);
			}
		}
	}
}

static void slow_eval_original_order(int16_t out[NTRUPLUS_N],
                                     const int16_t split[NTRUPLUS_N])
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int block = 0; block < 96; block++)
		{
			const int lambda = lambda_for_block(branch, block);

			for (int r = 0; r < 4; r++)
			{
				int power = 1;
				int acc = 0;

				for (int k = 0; k < 96; k++)
				{
					acc = (acc + field_mul(split[branch_start + 4*k + r], power)) % NTRUPLUS_Q;
					power = field_mul(power, lambda);
				}

				out[branch_start + 4*block + r] = (int16_t)acc;
			}
		}
	}
}

static void slow_eval_twisted(int16_t out[NTRUPLUS_N],
                              const int16_t a[NTRUPLUS_N],
                              const int factors[2],
                              int inverse_twist,
                              int inverse_alpha)
{
	int16_t split[NTRUPLUS_N];

	split_layer_reference(split, a);

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int factor = factors[branch];
		const int twist_step = inverse_twist ? field_inv(factor) : factor;
		const int alpha_scale = inverse_alpha ? field_inv(factor) : factor;
		int twist_power = 1;

		for (int k = 0; k < 96; k++)
		{
			const int16_t twist = to_mont(twist_power);

			for (int r = 0; r < 4; r++)
			{
				split[branch_start + 4*k + r] =
					fqmul(split[branch_start + 4*k + r], twist);
			}

			twist_power = field_mul(twist_power, twist_step);
		}

		for (int block = 0; block < 96; block++)
		{
			const int alpha = field_mul(lambda_for_block(branch, block), alpha_scale);

			for (int r = 0; r < 4; r++)
			{
				int power = 1;
				int acc = 0;

				for (int k = 0; k < 96; k++)
				{
					acc = (acc + field_mul(split[branch_start + 4*k + r], power)) % NTRUPLUS_Q;
					power = field_mul(power, alpha);
				}

				out[branch_start + 4*block + r] = (int16_t)acc;
			}
		}
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

static int block_equal(const int16_t a[NTRUPLUS_N], int aoff,
                       const int16_t b[NTRUPLUS_N], int boff)
{
	for (int r = 0; r < 4; r++)
	{
		if (!equal_modq(a[aoff + r], b[boff + r]))
		{
			return 0;
		}
	}

	return 1;
}

static int same_position_block_count(const int16_t a[NTRUPLUS_N],
                                     const int16_t b[NTRUPLUS_N])
{
	int count = 0;

	for (int block = 0; block < NTRUPLUS_N / 4; block++)
	{
		count += block_equal(a, 4*block, b, 4*block);
	}

	return count;
}

static int permuted_branch_block_count(const int16_t a[NTRUPLUS_N],
                                       const int16_t b[NTRUPLUS_N],
                                       int branch)
{
	int used[96] = {0};
	int count = 0;
	const int branch_start = branch * (NTRUPLUS_N / 2);

	for (int i = 0; i < 96; i++)
	{
		for (int j = 0; j < 96; j++)
		{
			if (!used[j] &&
			    block_equal(a, branch_start + 4*i, b, branch_start + 4*j))
			{
				used[j] = 1;
				count++;
				break;
			}
		}
	}

	return count;
}

static int alpha_is_cyclic(const int factors[2], int inverse_alpha)
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int scale = inverse_alpha ? field_inv(factors[branch]) : factors[branch];

		for (int block = 0; block < 96; block++)
		{
			const int alpha = field_mul(lambda_for_block(branch, block), scale);

			if (field_pow(alpha, 96) != 1)
			{
				return 0;
			}
		}
	}

	return 1;
}

static int alpha_for_block(int branch, int block, int factor)
{
	return field_mul(lambda_for_block(branch, block), factor);
}

static int is_primitive_96_root(int a)
{
	return field_pow(a, 96) == 1 &&
	       field_pow(a, 48) != 1 &&
	       field_pow(a, 32) != 1;
}

static int primitive_96_root_for_branch(int branch, int factor)
{
	for (int block = 0; block < 96; block++)
	{
		const int alpha = alpha_for_block(branch, block, factor);

		if (is_primitive_96_root(alpha))
		{
			return alpha;
		}
	}

	return 0;
}

static int exponent_for_root(int omega, int alpha)
{
	int power = 1;

	for (int e = 0; e < 96; e++)
	{
		if (power == alpha)
		{
			return e;
		}

		power = field_mul(power, omega);
	}

	return -1;
}

static int build_branch_exponents(int exponents[96], int branch, int factor, int omega)
{
	for (int block = 0; block < 96; block++)
	{
		const int alpha = alpha_for_block(branch, block, factor);

		exponents[block] = exponent_for_root(omega, alpha);
		if (exponents[block] < 0)
		{
			return 0;
		}
	}

	return 1;
}

static void slow_ntt96_direct(int16_t out[96], const int16_t in[96], int omega)
{
	for (int e = 0; e < 96; e++)
	{
		const int alpha = field_pow(omega, e);
		int power = 1;
		int acc = 0;

		for (int k = 0; k < 96; k++)
		{
			acc = (acc + field_mul(in[k], power)) % NTRUPLUS_Q;
			power = field_mul(power, alpha);
		}

		out[e] = (int16_t)acc;
	}
}

static void ntt96_cyclic_mixedradix(int16_t out[96], const int16_t in[96], int omega)
{
	int inner[3][32];
	const int omega32 = field_pow(omega, 32);
	const int omega3 = field_pow(omega, 3);

	for (int m1 = 0; m1 < 3; m1++)
	{
		const int inner_root = field_pow(omega32, m1);

		for (int n2 = 0; n2 < 32; n2++)
		{
			int power = 1;
			int acc = 0;

			for (int n1 = 0; n1 < 3; n1++)
			{
				acc = (acc + field_mul(in[n2 + 32*n1], power)) % NTRUPLUS_Q;
				power = field_mul(power, inner_root);
			}

			inner[m1][n2] = field_mul(acc, field_pow(omega, m1*n2));
		}
	}

	for (int m1 = 0; m1 < 3; m1++)
	{
		for (int m2 = 0; m2 < 32; m2++)
		{
			const int outer_root = field_pow(omega3, m2);
			int power = 1;
			int acc = 0;

			for (int n2 = 0; n2 < 32; n2++)
			{
				acc = (acc + field_mul(inner[m1][n2], power)) % NTRUPLUS_Q;
				power = field_mul(power, outer_root);
			}

			out[m1 + 3*m2] = (int16_t)acc;
		}
	}
}

static void full_twisted_mixedradix(int16_t out[NTRUPLUS_N],
                                    const int16_t a[NTRUPLUS_N],
                                    const int factors[2])
{
	int16_t split[NTRUPLUS_N];

	split_layer_reference(split, a);

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int factor = factors[branch];
		const int twist_step = field_inv(factor);
		const int omega = primitive_96_root_for_branch(branch, factor);
		int exponents[96];
		int twist_power = 1;

		if (omega == 0 || !build_branch_exponents(exponents, branch, factor, omega))
		{
			for (int i = 0; i < NTRUPLUS_N; i++)
			{
				out[i] = 1;
			}
			return;
		}

		for (int k = 0; k < 96; k++)
		{
			const int16_t twist = to_mont(twist_power);

			for (int r = 0; r < 4; r++)
			{
				split[branch_start + 4*k + r] =
					fqmul(split[branch_start + 4*k + r], twist);
			}

			twist_power = field_mul(twist_power, twist_step);
		}

		for (int r = 0; r < 4; r++)
		{
			int16_t seq[96];
			int16_t natural[96];

			for (int k = 0; k < 96; k++)
			{
				seq[k] = split[branch_start + 4*k + r];
			}

			ntt96_cyclic_mixedradix(natural, seq, omega);

			for (int block = 0; block < 96; block++)
			{
				out[branch_start + 4*block + r] = natural[exponents[block]];
			}
		}
	}
}

static int check_twist_tables(void)
{
	const int f0 = normal_from_mont(tw_branch0[1]);
	const int f1 = normal_from_mont(tw_branch1[1]);
	const int f0_inv = field_inv(f0);
	const int f1_inv = field_inv(f1);
	int f0_power = 1;
	int f1_power = 1;
	int f0_inv_power = 1;
	int f1_inv_power = 1;

	for (int i = 0; i < 96; i++)
	{
		if (normal_from_mont(tw_branch0[i]) != f0_power ||
		    normal_from_mont(tw_branch1[i]) != f1_power ||
		    normal_from_mont(tw_branch0_inv[i]) != f0_inv_power ||
		    normal_from_mont(tw_branch1_inv[i]) != f1_inv_power ||
		    !equal_modq(fqmul(tw_branch0[i], tw_branch0_inv[i]), NTRUPLUS_R) ||
		    !equal_modq(fqmul(tw_branch1[i], tw_branch1_inv[i]), NTRUPLUS_R))
		{
			printf("twist table check failed at i=%d\n", i);
			return 0;
		}

		f0_power = field_mul(f0_power, f0);
		f1_power = field_mul(f1_power, f1);
		f0_inv_power = field_mul(f0_inv_power, f0_inv);
		f1_inv_power = field_mul(f1_inv_power, f1_inv);
	}

	printf("twist table check: ok (F0=%d, F1=%d)\n", f0, f1);
	return 1;
}

static int check_original_direct_eval(void)
{
	int16_t a[NTRUPLUS_N];
	int16_t split[NTRUPLUS_N];
	int16_t ref[NTRUPLUS_N];
	int16_t slow[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		fill_input(a, seed);
		split_layer_reference(split, a);
		original_ntt_reference(ref, a);
		slow_eval_original_order(slow, split);

		if (coeff_match_count(ref, slow) != NTRUPLUS_N)
		{
			printf("original direct-evaluation check failed at seed=%u\n", seed);
			return 0;
		}
	}

	printf("original direct-evaluation check: ok\n");
	return 1;
}

static int coeff96_match_count(const int16_t a[96], const int16_t b[96])
{
	int count = 0;

	for (int i = 0; i < 96; i++)
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

static int check_ntt96_cyclic_mixedradix(void)
{
	int min_matches = 96;
	int16_t in[96];
	int16_t slow[96];
	int16_t mixed[96];
	const int f0 = normal_from_mont(tw_branch0[1]);
	const int f1 = normal_from_mont(tw_branch1[1]);
	const int omegas[2] = {
		primitive_96_root_for_branch(0, f0),
		primitive_96_root_for_branch(1, f1)
	};

	for (int root = 0; root < 2; root++)
	{
		if (omegas[root] == 0)
		{
			printf("ntt96 mixed-radix check failed: missing primitive root %d\n", root);
			return 0;
		}

		for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
		{
			uint32_t s = 0x9e3779b9u ^ (seed + 17u * (uint32_t)root);

			for (int i = 0; i < 96; i++)
			{
				s = s * 1664525u + 1013904223u;
				in[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
			}

			slow_ntt96_direct(slow, in, omegas[root]);
			ntt96_cyclic_mixedradix(mixed, in, omegas[root]);

			const int matches = coeff96_match_count(slow, mixed);
			if (matches < min_matches)
			{
				min_matches = matches;
			}
		}
	}

	printf("ntt96_cyclic_mixedradix check: %d/96 minimum coefficient match\n",
	       min_matches);
	return min_matches == 96;
}

static int check_ntt96_goodthomas(void)
{
	int min_vs_slow = 96;
	int min_vs_mixed = 96;
	int16_t in[96];
	int16_t slow[96];
	int16_t mixed[96];
	int16_t gt[96];
	const int f1 = normal_from_mont(tw_branch1[1]);
	const int omega = primitive_96_root_for_branch(1, f1);

	if (omega == 0)
	{
		printf("ntt96 Good-Thomas check failed: missing canonical primitive root\n");
		return 0;
	}

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		uint32_t s = 0x85ebca6bu ^ seed;
		int matches;

		for (int i = 0; i < 96; i++)
		{
			s = s * 1664525u + 1013904223u;
			in[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
		}

		slow_ntt96_direct(slow, in, omega);
		ntt96_cyclic_mixedradix(mixed, in, omega);
		ntt96_goodthomas(gt, in);

		matches = coeff96_match_count(slow, gt);
		if (matches < min_vs_slow)
		{
			min_vs_slow = matches;
		}

		matches = coeff96_match_count(mixed, gt);
		if (matches < min_vs_mixed)
		{
			min_vs_mixed = matches;
		}
	}

	printf("ntt96_goodthomas check: vs slow %d/96, vs mixed-radix %d/96\n",
	       min_vs_slow, min_vs_mixed);
	return min_vs_slow == 96 && min_vs_mixed == 96;
}

static int check_intt32_radix2(void)
{
	int min_vs_slow = 32;
	int min_roundtrip = 32;
	int16_t in[32];
	int16_t freq[32];
	int16_t slow[32];
	int16_t fast[32];
	int16_t scaled[32];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		uint32_t s = 0x27d4eb2du ^ seed;
		int matches = 0;

		for (int i = 0; i < 32; i++)
		{
			s = s * 1664525u + 1013904223u;
			freq[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
		}

		intt32_slow(slow, freq);
		intt32_radix2(fast, freq);
		matches = coeff32_match_count(slow, fast);
		if (matches < min_vs_slow)
		{
			min_vs_slow = matches;
		}

		s = 0x165667b1u ^ seed;
		for (int i = 0; i < 32; i++)
		{
			s = s * 1664525u + 1013904223u;
			in[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
		}

		ntt32_radix2(freq, in);
		intt32_radix2(fast, freq);
		for (int i = 0; i < 32; i++)
		{
			scaled[i] = (int16_t)field_mul(in[i], 32);
		}

		matches = coeff32_match_count(scaled, fast);
		if (matches < min_roundtrip)
		{
			min_roundtrip = matches;
		}
	}

	printf("intt32_radix2 check: vs slow %d/32, roundtrip %d/32 after 32 scaling\n",
	       min_vs_slow, min_roundtrip);
	return min_vs_slow == 32 && min_roundtrip == 32;
}

static int check_invntt96_goodthomas_fast_vs_slow(void)
{
	int min_matches = 96;
	int16_t freq[96];
	int16_t slow[96];
	int16_t fast[96];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		uint32_t s = 0x94d049bbu ^ seed;
		int matches;

		for (int i = 0; i < 96; i++)
		{
			s = s * 1664525u + 1013904223u;
			freq[i] = (int16_t)((int)(s % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
		}

		invntt96_goodthomas_slow(slow, freq);
		invntt96_goodthomas(fast, freq);
		matches = coeff96_match_count(slow, fast);
		if (matches < min_matches)
		{
			min_matches = matches;
		}
	}

	printf("invntt96_goodthomas fast-vs-slow check: %d/96 minimum coefficient match\n",
	       min_matches);
	return min_matches == 96;
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

static int check_full_twisted_mixedradix(const int factors[2])
{
	int min_vs_slow = NTRUPLUS_N;
	int min_vs_ref = NTRUPLUS_N;
	int min_blocks = NTRUPLUS_N / 4;
	int16_t a[NTRUPLUS_N];
	int16_t slow[NTRUPLUS_N];
	int16_t mixed[NTRUPLUS_N];
	int16_t ref[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		int matches;

		fill_input(a, seed);
		slow_eval_twisted(slow, a, factors, 1, 0);
		full_twisted_mixedradix(mixed, a, factors);
		original_ntt_reference(ref, a);

		matches = coeff_match_count(slow, mixed);
		if (matches < min_vs_slow)
		{
			min_vs_slow = matches;
		}

		matches = coeff_match_count(ref, mixed);
		if (matches < min_vs_ref)
		{
			min_vs_ref = matches;
		}

		matches = same_position_block_count(ref, mixed);
		if (matches < min_blocks)
		{
			min_blocks = matches;
		}
	}

	printf("full twisted mixed-radix: vs slow %d/768, vs original %d/768, same blocks %d/192\n",
	       min_vs_slow, min_vs_ref, min_blocks);
	return min_vs_slow == NTRUPLUS_N &&
	       min_vs_ref == NTRUPLUS_N &&
	       min_blocks == NTRUPLUS_N / 4;
}

static int check_full_ntt_goodthomas(const int factors[2])
{
	int min_vs_mixed = NTRUPLUS_N;
	int min_vs_ref = NTRUPLUS_N;
	int min_blocks = NTRUPLUS_N / 4;
	int16_t a[NTRUPLUS_N];
	int16_t mixed[NTRUPLUS_N];
	int16_t gt[NTRUPLUS_N];
	int16_t ref[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		int matches;

		fill_input(a, seed);
		full_twisted_mixedradix(mixed, a, factors);
		original_ntt_reference(ref, a);
		ntt_gt_oldlayout(gt, a);

		matches = coeff_match_count(mixed, gt);
		if (matches < min_vs_mixed)
		{
			min_vs_mixed = matches;
		}

		matches = coeff_match_count(ref, gt);
		if (matches < min_vs_ref)
		{
			min_vs_ref = matches;
		}

		matches = same_position_block_count(ref, gt);
		if (matches < min_blocks)
		{
			min_blocks = matches;
		}
	}

	printf("full ntt Good-Thomas old-layout: vs mixed-radix %d/768, vs original %d/768, same blocks %d/192\n",
	       min_vs_mixed, min_vs_ref, min_blocks);
	return min_vs_mixed == NTRUPLUS_N &&
	       min_vs_ref == NTRUPLUS_N &&
	       min_blocks == NTRUPLUS_N / 4;
}

static int check_full_ntt_gt_natural_layout(const int factors[2])
{
	int min_permuted = NTRUPLUS_N;
	int min_public = NTRUPLUS_N;
	int16_t a[NTRUPLUS_N];
	int16_t old_layout[NTRUPLUS_N];
	int16_t natural[NTRUPLUS_N];
	int16_t public_ntt[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		int permuted = 0;
		int matches;

		fill_input(a, seed);
		full_twisted_mixedradix(old_layout, a, factors);
		ntt_gt_naturallayout(natural, a);
		ntt(public_ntt, a);

		for (int branch = 0; branch < 2; branch++)
		{
			const int branch_start = branch * (NTRUPLUS_N / 2);

			for (int block = 0; block < 96; block++)
			{
				const int j = gt96_branch_exponents[branch][block];

				for (int lane = 0; lane < 4; lane++)
				{
					permuted += equal_modq(old_layout[branch_start + 4*block + lane],
					                       natural[branch_start + 4*j + lane]);
				}
			}
		}

		if (permuted < min_permuted)
		{
			min_permuted = permuted;
		}

		matches = coeff_match_count(natural, public_ntt);
		if (matches < min_public)
		{
			min_public = matches;
		}
	}

	printf("full ntt GT-natural layout: old-layout permutation %d/768, public ntt %d/768\n",
	       min_permuted, min_public);
	return min_permuted == NTRUPLUS_N && min_public == NTRUPLUS_N;
}

static int check_invntt_gt_oldlayout_roundtrip(void)
{
	int min_gt = NTRUPLUS_N;
	int min_old = NTRUPLUS_N;
	int16_t a[NTRUPLUS_N];
	int16_t gt_ntt[NTRUPLUS_N];
	int16_t old_ntt[NTRUPLUS_N];
	int16_t round[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		int matches;

		fill_input(a, seed);

		ntt_gt_oldlayout(gt_ntt, a);
		invntt_gt_oldlayout(round, gt_ntt);
		matches = coeff_match_count(a, round);
		if (matches < min_gt)
		{
			min_gt = matches;
		}

		original_ntt_reference(old_ntt, a);
		invntt_gt_oldlayout(round, old_ntt);
		matches = coeff_match_count(a, round);
		if (matches < min_old)
		{
			min_old = matches;
		}
	}

	printf("invntt_gt_oldlayout roundtrip: from gt old-layout %d/768, from old ntt %d/768\n",
	       min_gt, min_old);
	return min_gt == NTRUPLUS_N && min_old == NTRUPLUS_N;
}

static int check_invntt_gt_naturallayout_roundtrip(void)
{
	int min_gt = NTRUPLUS_N;
	int min_public = NTRUPLUS_N;
	int16_t a[NTRUPLUS_N];
	int16_t gt_ntt[NTRUPLUS_N];
	int16_t public_ntt[NTRUPLUS_N];
	int16_t round[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		int matches;

		fill_input(a, seed);

		ntt_gt_naturallayout(gt_ntt, a);
		invntt_gt_naturallayout(round, gt_ntt);
		matches = coeff_match_count(a, round);
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

	printf("invntt_gt_naturallayout roundtrip: direct %d/768, public ntt/invntt %d/768\n",
	       min_gt, min_public);
	return min_gt == NTRUPLUS_N && min_public == NTRUPLUS_N;
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

static void oldlayout_basemul_reference(int16_t r[NTRUPLUS_N],
                                        const int16_t a[NTRUPLUS_N],
                                        const int16_t b[NTRUPLUS_N])
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int zeta_base = 96 + 48 * branch;

		for (int pair = 0; pair < 48; pair++)
		{
			const int16_t zeta = zetas[zeta_base + pair];
			const int block_plus = branch_start + 8*pair;
			const int block_minus = block_plus + 4;

			basemul(r + block_plus, a + block_plus, b + block_plus, zeta);
			basemul(r + block_minus, a + block_minus, b + block_minus, -zeta);
		}
	}
}

static void naturallayout_basemul_reference(int16_t r[NTRUPLUS_N],
                                            const int16_t a[NTRUPLUS_N],
                                            const int16_t b[NTRUPLUS_N])
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int j = 0; j < 96; j++)
		{
			const int pos = branch_start + 4*j;

			basemul(r + pos, a + pos, b + pos, gt_lambda[branch][j]);
		}
	}
}

static int check_gt_natural_multiplication(void)
{
	int min_vs_old = NTRUPLUS_N;
	int min_vs_schoolbook = NTRUPLUS_N;
	int16_t a[NTRUPLUS_N];
	int16_t b[NTRUPLUS_N];
	int16_t schoolbook[NTRUPLUS_N];
	int16_t old_a[NTRUPLUS_N];
	int16_t old_b[NTRUPLUS_N];
	int16_t old_c[NTRUPLUS_N];
	int16_t old_round[NTRUPLUS_N];
	int16_t natural_a[NTRUPLUS_N];
	int16_t natural_b[NTRUPLUS_N];
	int16_t natural_c[NTRUPLUS_N];
	int16_t natural_round[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		int matches;

		fill_input(a, seed);
		fill_input(b, seed + 0x100u);
		schoolbook_mul_reference(schoolbook, a, b);

		ntt_gt_oldlayout(old_a, a);
		ntt_gt_oldlayout(old_b, b);
		oldlayout_basemul_reference(old_c, old_a, old_b);
		invntt_gt_oldlayout(old_round, old_c);

		ntt_gt_naturallayout(natural_a, a);
		ntt_gt_naturallayout(natural_b, b);
		naturallayout_basemul_reference(natural_c, natural_a, natural_b);
		invntt_gt_naturallayout(natural_round, natural_c);

		matches = coeff_match_count(old_round, natural_round);
		if (matches < min_vs_old)
		{
			min_vs_old = matches;
		}

		matches = coeff_match_count(schoolbook, natural_round);
		if (matches < min_vs_schoolbook)
		{
			min_vs_schoolbook = matches;
		}
	}

	printf("GT-natural multiplication: vs old-layout reference %d/768, vs schoolbook %d/768\n",
	       min_vs_old, min_vs_schoolbook);
	return min_vs_old == NTRUPLUS_N && min_vs_schoolbook == NTRUPLUS_N;
}

static int report_mode(const char *name,
                       const int factors[2],
                       int inverse_twist,
                       int inverse_alpha)
{
	int min_coeff = NTRUPLUS_N;
	int min_same_blocks = NTRUPLUS_N / 4;
	int min_permuted_blocks = NTRUPLUS_N / 4;
	int16_t a[NTRUPLUS_N];
	int16_t ref[NTRUPLUS_N];
	int16_t twisted[NTRUPLUS_N];

	for (uint32_t seed = 0; seed < TEST_VECTORS; seed++)
	{
		int coeffs;
		int same_blocks;
		int permuted_blocks;

		fill_input(a, seed);
		original_ntt_reference(ref, a);
		slow_eval_twisted(twisted, a, factors, inverse_twist, inverse_alpha);

		coeffs = coeff_match_count(ref, twisted);
		same_blocks = same_position_block_count(ref, twisted);
		permuted_blocks =
			permuted_branch_block_count(ref, twisted, 0) +
			permuted_branch_block_count(ref, twisted, 1);

		if (coeffs < min_coeff)
		{
			min_coeff = coeffs;
		}
		if (same_blocks < min_same_blocks)
		{
			min_same_blocks = same_blocks;
		}
		if (permuted_blocks < min_permuted_blocks)
		{
			min_permuted_blocks = permuted_blocks;
		}
	}

	printf("%-58s coeff %3d/%d, same blocks %3d/%d, permuted blocks %3d/%d, alpha^96=1: %s\n",
	       name,
	       min_coeff, NTRUPLUS_N,
	       min_same_blocks, NTRUPLUS_N / 4,
	       min_permuted_blocks, NTRUPLUS_N / 4,
	       alpha_is_cyclic(factors, inverse_alpha) ? "yes" : "no");

	return min_coeff == NTRUPLUS_N;
}

int main(void)
{
	const int f0 = normal_from_mont(tw_branch0[1]);
	const int f1 = normal_from_mont(tw_branch1[1]);
	const int branch_factors[2] = {f0, f1};
	int ok = 1;
	int cyclic_inverse_exact;

	ok &= check_twist_tables();
	ok &= check_original_direct_eval();
	ok &= check_ntt96_cyclic_mixedradix();
	ok &= check_ntt96_goodthomas();
	ok &= check_intt32_radix2();
	ok &= check_invntt96_goodthomas_fast_vs_slow();
	ok &= check_invntt96_goodthomas();

	printf("branch 0 lambda^96=%d, branch 1 lambda^96=%d, F0^96=%d, F1^96=%d\n",
	       field_pow(lambda_for_block(0, 0), 96),
	       field_pow(lambda_for_block(1, 0), 96),
	       field_pow(f0, 96),
	       field_pow(f1, 96));

	cyclic_inverse_exact = report_mode("inverse twist: branch=(F0,F1), twist F^-k, alpha=F*lambda",
	                                   branch_factors, 1, 0);
	(void)report_mode("wrong alpha: branch=(F0,F1), twist F^-k, alpha=lambda/F",
	                  branch_factors, 1, 1);
	(void)report_mode("equivalent positive twist: branch=(F0,F1), twist F^k, alpha=lambda/F",
	                  branch_factors, 0, 1);

	ok &= check_full_twisted_mixedradix(branch_factors);
	ok &= check_full_ntt_goodthomas(branch_factors);
	ok &= check_full_ntt_gt_natural_layout(branch_factors);
	ok &= check_invntt_gt_oldlayout_roundtrip();
	ok &= check_invntt_gt_naturallayout_roundtrip();
	ok &= check_gt_natural_multiplication();

	if (!cyclic_inverse_exact)
	{
		ok = 0;
	}

	return ok ? 0 : 1;
}

#include <stdint.h>
#include <stdio.h>

/*
 * Layout dump helper. Include ntt.c directly so this debug tool uses the same
 * static Montgomery helpers, twist tables, and Good-Thomas scatter tables as
 * the implementation under inspection.
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

static int normal_from_mont(int16_t a)
{
	return modq(montgomery_reduce(a));
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

static int lambda_for_block(int branch, int block)
{
	int lambda = normal_from_mont(zetas[96 + 48*branch + block/2]);

	if (block & 1)
	{
		lambda = modq(-lambda);
	}

	return lambda;
}

static int zeta_base_for_branch(int branch)
{
	return branch == 0 ? 96 : 144;
}

static int zeta_idx_for_block(int branch, int local_block)
{
	return zeta_base_for_branch(branch) + local_block / 2;
}

static char zeta_sign_for_block(int local_block)
{
	return (local_block & 1) ? '-' : '+';
}

static int verify_basemul_zeta_layout(void)
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = (NTRUPLUS_N / 2) * branch;
		const int expected_base = branch == 0 ? 96 : 144;

		for (int local_block = 0; local_block < 96; local_block++)
		{
			const int pos = branch_start + 4*local_block;
			const int expected_zeta_idx = expected_base + local_block / 2;
			const char expected_sign = (local_block & 1) ? '-' : '+';

			if (zeta_idx_for_block(branch, local_block) != expected_zeta_idx ||
			    zeta_sign_for_block(local_block) != expected_sign ||
			    pos / 8 + 96 != expected_zeta_idx)
			{
				fprintf(stderr,
				        "basemul/baseinv zeta layout mismatch: branch=%d block=%d pos=%d\n",
				        branch, local_block, pos);
				return 0;
			}
		}
	}

	return 1;
}

static void dump_basemul_zeta_row(int branch, int local_block)
{
	const int branch_start = (NTRUPLUS_N / 2) * branch;
	const int pos = branch_start + 4*local_block;

	printf("%6d | %11d | %3d..%-3d | %8d | %4c\n",
	       branch,
	       local_block,
	       pos,
	       pos + 3,
	       zeta_idx_for_block(branch, local_block),
	       zeta_sign_for_block(local_block));
}

static void dump_basemul_zeta_layout(void)
{
	const int sample_blocks[] = {0, 1, 2, 3, 94, 95};

	printf("\n# old-compatible basemul/baseinv quartic block to zetas[] layout\n");
	printf("branch | local_block | positions | zeta_idx | sign\n");
	printf("-------+-------------+-----------+----------+-----\n");

	for (int branch = 0; branch < 2; branch++)
	{
		for (size_t i = 0; i < sizeof(sample_blocks) / sizeof(sample_blocks[0]); i++)
		{
			dump_basemul_zeta_row(branch, sample_blocks[i]);
		}
	}
}

static void gen_expected_gt_lambda_table(int16_t table[2][96])
{
	for (int branch = 0; branch < 2; branch++)
	{
		for (int local_block = 0; local_block < 96; local_block++)
		{
			const int j = gt96_branch_exponents[branch][local_block];
			const int16_t zeta = zetas[zeta_idx_for_block(branch, local_block)];

			table[branch][j] = zeta_sign_for_block(local_block) == '+' ? zeta : -zeta;
		}
	}
}

static void dump_gt_natural_lambda_row(int branch, int j)
{
	const int branch_start = (NTRUPLUS_N / 2) * branch;
	const int pos = branch_start + 4*j;

	printf("%6d | %7d | %3d..%-3d | %11d | %13d\n",
	       branch,
	       j,
	       pos,
	       pos + 3,
	       gt_lambda[branch][j],
	       normal_from_mont(gt_lambda[branch][j]));
}

static void dump_gt_natural_lambda_layout(void)
{
	const int sample_blocks[] = {0, 1, 2, 3, 94, 95};

	printf("\n# GT-natural quartic block to lambda layout\n");
	printf("branch | block j | positions | lambda_mont | lambda_normal\n");
	printf("-------+---------+-----------+-------------+--------------\n");

	for (int branch = 0; branch < 2; branch++)
	{
		for (size_t i = 0; i < sizeof(sample_blocks) / sizeof(sample_blocks[0]); i++)
		{
			dump_gt_natural_lambda_row(branch, sample_blocks[i]);
		}
	}
}

static int verify_gt_lambda_formula(int omega96, const int factors[2])
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int factor_inv = field_inv(factors[branch]);

		for (int j = 0; j < 96; j++)
		{
			const int expected = field_mul(field_pow(omega96, j), factor_inv);
			const int actual = normal_from_mont(gt_lambda[branch][j]);

			if (actual != expected)
			{
				fprintf(stderr,
				        "GT lambda formula mismatch: branch=%d j=%d actual=%d expected=%d\n",
				        branch, j, actual, expected);
				return 0;
			}
		}
	}

	return 1;
}

static int dump_gt_lambda_table_comparison(void)
{
	int16_t expected_gt_lambda[2][96];
	int ok = 1;

	gen_expected_gt_lambda_table(expected_gt_lambda);

	printf("\n# old-compatible block order vs GT-natural lambda table\n");
	printf("branch | old_block | logical j | old zeta | gt_lambda[j] | match\n");
	printf("-------+-----------+-----------+----------+--------------+------\n");

	for (int branch = 0; branch < 2; branch++)
	{
		for (int local_block = 0; local_block < 96; local_block++)
		{
			const int j = gt96_branch_exponents[branch][local_block];
			const int16_t zeta = zetas[zeta_idx_for_block(branch, local_block)];
			const int16_t old_zeta = zeta_sign_for_block(local_block) == '+' ? zeta : -zeta;
			const int match = old_zeta == gt_lambda[branch][j] &&
			                  old_zeta == expected_gt_lambda[branch][j];

			if (!match)
			{
				ok = 0;
			}

			printf("%6d | %9d | %9d | %8d | %12d | %s\n",
			       branch,
			       local_block,
			       j,
			       old_zeta,
			       gt_lambda[branch][j],
			       match ? "yes" : "NO");
		}
	}

	printf("# GT-natural lambda table comparison: %s\n", ok ? "ok" : "mismatch");
	return ok;
}

int main(void)
{
	const int factors[2] = {
		normal_from_mont(tw_branch0[1]),
		normal_from_mont(tw_branch1[1])
	};
	const int omega96 = field_mul(lambda_for_block(1, 0), factors[1]);
	int ok = 1;

	printf("# alpha_j and lambda_j are normal representatives in [0,%d).\n",
	       NTRUPLUS_Q);
	printf("# omega96=%d, F0=%d, F1=%d\n", omega96, factors[0], factors[1]);
	printf("physical pos | branch | lane r | logical j | alpha_j | lambda_j | basemul-table-index\n");
	printf("-------------+--------+--------+-----------+---------+----------+--------------------\n");

	for (int pos = 0; pos < NTRUPLUS_N; pos++)
	{
		const int branch = pos / (NTRUPLUS_N / 2);
		const int branch_pos = pos - branch * (NTRUPLUS_N / 2);
		const int block = branch_pos / 4;
		const int lane = pos & 3;
		const int lambda = lambda_for_block(branch, block);
		const int alpha = field_mul(lambda, factors[branch]);
		const int logical_j = exponent_for_root(omega96, alpha);
		const int table_index = zeta_idx_for_block(branch, block);
		const char table_sign = zeta_sign_for_block(block);

		if (logical_j != gt96_branch_exponents[branch][block])
		{
			ok = 0;
		}

		printf("%12d | %6d | %6d | %9d | %7d | %8d | %c zetas[%3d]\n",
		       pos,
		       branch,
		       lane,
		       logical_j,
		       alpha,
		       lambda,
		       table_sign,
		       table_index);
	}

	if (!verify_basemul_zeta_layout())
	{
		ok = 0;
	}
	if (!verify_gt_lambda_formula(omega96, factors))
	{
		ok = 0;
	}

	dump_basemul_zeta_layout();
	dump_gt_natural_lambda_layout();
	if (!dump_gt_lambda_table_comparison())
	{
		ok = 0;
	}

	if (!ok)
	{
		fprintf(stderr, "layout dump mismatch: computed layout differs from implementation tables\n");
		return 1;
	}

	return 0;
}

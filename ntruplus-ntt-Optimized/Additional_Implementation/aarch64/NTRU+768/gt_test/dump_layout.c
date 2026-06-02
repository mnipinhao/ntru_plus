#include <stdint.h>
#include <stdio.h>

/*
 * Layout dump helper. Include ntt.c directly so this debug tool uses the same
 * static Montgomery helpers, twist/untwist tables, and lambda table as the
 * implementation under inspection.
 */
#include "../ntt.c"

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

static unsigned rowbitrev_logical_index(unsigned physical_j)
{
	const unsigned k3 = (2 * physical_j) % 3;
	const unsigned k32_br = (11 * physical_j) & 31U;
	const unsigned logical_k32 = bitreverse5(k32_br);

	return gt96_output_crt_index(k3, logical_k32);
}

static void dump_gt_rowbitrev_lambda_row(int branch, int physical_j)
{
	const int branch_start = (NTRUPLUS_N / 2) * branch;
	const int k3 = (2 * physical_j) % 3;
	const int k32_br = (11 * physical_j) & 31;
	const int logical_k32 = (int)bitreverse5((unsigned)k32_br);
	const int logical_j = (int)rowbitrev_logical_index((unsigned)physical_j);
	const int pos = branch_start + 4*physical_j;

	printf("%6d | %14d | %2d | %6d | %11d | %9d | %3d..%-3d | %11d | %13d\n",
	       branch,
	       physical_j,
	       k3,
	       k32_br,
	       logical_k32,
	       logical_j,
	       pos,
	       pos + 3,
	       gt_rowbitrev_lambda[branch][physical_j],
	       normal_from_mont(gt_rowbitrev_lambda[branch][physical_j]));
}

static void dump_gt_rowbitrev_lambda_layout(void)
{
	const int sample_blocks[] = {0, 1, 2, 3, 94, 95};

	printf("\n# GT row-bitrev quartic block to lambda layout\n");
	printf("branch | physical block | k3 | k32_br | logical_k32 | logical j | positions | lambda_mont | lambda_normal\n");
	printf("-------+----------------+----+--------+-------------+-----------+-----------+-------------+--------------\n");

	for (int branch = 0; branch < 2; branch++)
	{
		for (size_t i = 0; i < sizeof(sample_blocks) / sizeof(sample_blocks[0]); i++)
		{
			dump_gt_rowbitrev_lambda_row(branch, sample_blocks[i]);
		}
	}
}

static int verify_gt_rowbitrev_lambda_table(const int factors[2])
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int factor_inv = field_inv(factors[branch]);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int logical_j =
				(int)rowbitrev_logical_index((unsigned)physical_j);
			const int expected =
				field_mul(field_pow(OMEGA96_NORMAL, logical_j), factor_inv);
			const int actual =
				normal_from_mont(gt_rowbitrev_lambda[branch][physical_j]);

			if (actual != expected)
			{
				fprintf(stderr,
				        "GT row-bitrev lambda mismatch: branch=%d physical_j=%d logical_j=%d actual=%d expected=%d\n",
				        branch, physical_j, logical_j, actual, expected);
				return 0;
			}
		}
	}

	return 1;
}

int main(void)
{
	const int factors[2] = {
		normal_from_mont(untwist_branch0[1]),
		normal_from_mont(untwist_branch1[1])
	};
	int ok = 1;

	printf("# GT row-bitrev layout.\n");
	printf("# alpha_j and lambda_j are normal representatives in [0,%d).\n",
	       NTRUPLUS_Q);
	printf("# omega96=%d, F0=%d, F1=%d\n",
	       OMEGA96_NORMAL, factors[0], factors[1]);
	printf("physical pos | branch | lane r | physical block | k3 | k32_br | logical_k32 | logical j | alpha_j | lambda_j | table index\n");
	printf("-------------+--------+--------+----------------+----+--------+-------------+-----------+---------+----------+------------\n");

	for (int pos = 0; pos < NTRUPLUS_N; pos++)
	{
		const int branch = pos / (NTRUPLUS_N / 2);
		const int branch_pos = pos - branch * (NTRUPLUS_N / 2);
		const int physical_j = branch_pos / 4;
		const int k3 = (2 * physical_j) % 3;
		const int k32_br = (11 * physical_j) & 31;
		const int logical_k32 = (int)bitreverse5((unsigned)k32_br);
		const int logical_j =
			(int)rowbitrev_logical_index((unsigned)physical_j);
		const int lane = pos & 3;
		const int lambda = normal_from_mont(gt_rowbitrev_lambda[branch][physical_j]);
		const int alpha = field_mul(lambda, factors[branch]);
		const int expected_alpha = field_pow(OMEGA96_NORMAL, logical_j);

		if (alpha != expected_alpha)
		{
			ok = 0;
		}

		printf("%12d | %6d | %6d | %14d | %2d | %6d | %11d | %9d | %7d | %8d | gt_rowbitrev_lambda[%d][%2d]\n",
		       pos,
		       branch,
		       lane,
		       physical_j,
		       k3,
		       k32_br,
		       logical_k32,
		       logical_j,
		       alpha,
		       lambda,
		       branch,
		       physical_j);
	}

	if (!verify_gt_rowbitrev_lambda_table(factors))
	{
		ok = 0;
	}

	dump_gt_rowbitrev_lambda_layout();

	if (!ok)
	{
		fprintf(stderr, "layout dump mismatch: computed layout differs from row-bitrev tables\n");
		return 1;
	}

	return 0;
}

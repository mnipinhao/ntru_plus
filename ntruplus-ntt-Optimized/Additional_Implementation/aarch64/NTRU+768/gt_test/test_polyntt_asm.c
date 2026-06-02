#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "ntt.h"
#include "poly.h"

#define RANDOM_TESTS 8

#ifndef POLYNTT_ASM_ALLOW_LAZY
#define POLYNTT_ASM_ALLOW_LAZY 0
#endif

#ifndef POLYNTT_ASM_STAGE1_ZIP
#define POLYNTT_ASM_STAGE1_ZIP 0
#endif

#ifndef POLYNTT_ASM_STAGE2_DFT3
#define POLYNTT_ASM_STAGE2_DFT3 0
#endif

#ifndef POLYNTT_ASM_DUMP_STAGE2_MEMORY
#define POLYNTT_ASM_DUMP_STAGE2_MEMORY 0
#endif

#define POLYNTT_ASM_PARTIAL (POLYNTT_ASM_STAGE1_ZIP || POLYNTT_ASM_STAGE2_DFT3)
#define POLYNTT_ASM_OUTPUT_NOT_POINTWISE POLYNTT_ASM_PARTIAL

/*
 * Link this harness with exactly one poly_ntt() implementation, normally
 * asm/my_ntt.s.  The golden output comes from the C Good-Thomas reference in
 * ntt.c, so this test does not depend on production poly.c or asm/ntt.s.
 *
 * Default policy is strict exact matching to catch permutation and reduction
 * shape errors early.  The current C reference emits complete row-bitrev
 * forward output; basemul/baseinv can use gt_rowbitrev_lambda[] in physical
 * memory order.  For an intentionally lazy-reduced ASM kernel, build with
 * -DPOLYNTT_ASM_ALLOW_LAZY=1 to accept mod-q equality.
 */

static int modq(int64_t a)
{
	int r = (int)(a % NTRUPLUS_Q);

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}

	return r;
}

static int equal_modq(int16_t a, int16_t b)
{
	return modq((int)a - (int)b) == 0;
}

static void fill_zero(poly *a)
{
	memset(a->coeffs, 0, sizeof(a->coeffs));
}

static void fill_pattern(poly *a, const char *name, uint32_t seed)
{
	if (strcmp(name, "zero") == 0)
	{
		fill_zero(a);
		return;
	}

	if (strcmp(name, "one") == 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a->coeffs[i] = 1;
		}
		return;
	}

	if (strcmp(name, "alternating_pm1") == 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a->coeffs[i] = (i & 1) ? -1 : 1;
		}
		return;
	}

	if (strcmp(name, "centered_edges") == 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a->coeffs[i] = (i & 1) ? -(NTRUPLUS_Q / 2) : (NTRUPLUS_Q / 2);
		}
		return;
	}

	if (strcmp(name, "ramp") == 0)
	{
		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			a->coeffs[i] = (int16_t)((i % NTRUPLUS_Q) - NTRUPLUS_Q / 2);
		}
		return;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		seed = seed * 1664525u + 1013904223u;
		a->coeffs[i] = (int16_t)((int)(seed % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
	}
}

static void fill_impulse(poly *a, int pos, int16_t value)
{
	fill_zero(a);
	a->coeffs[pos] = value;
}

#if POLYNTT_ASM_PARTIAL
static int mul_modq(int a, int b)
{
	return modq((int64_t)a * b);
}

static int pow_modq(int base, int exp)
{
	int acc = 1;
	int x = modq(base);

	while (exp > 0)
	{
		if (exp & 1)
		{
			acc = mul_modq(acc, x);
		}
		x = mul_modq(x, x);
		exp >>= 1;
	}

	return acc;
}

static int inv_modq(int a)
{
	/* q is prime, so a^{-1} = a^{q-2}. */
	return pow_modq(a, NTRUPLUS_Q - 2);
}

static int twist_normal(int branch, int block)
{
	const int f = branch == 0 ? 2 : 22;

	return pow_modq(inv_modq(f), block);
}

#if POLYNTT_ASM_STAGE1_ZIP
static void store_stage1_pack(poly *r,
                              int *outpos,
                              const int b0[384],
                              const int b1[384],
                              int block)
{
	const int tw0 = twist_normal(0, block);
	const int tw1 = twist_normal(1, block);

	for (int lane = 0; lane < 4; lane++)
	{
		r->coeffs[(*outpos)++] = (int16_t)mul_modq(b0[4*block + lane], tw0);
	}

	for (int lane = 0; lane < 4; lane++)
	{
		r->coeffs[(*outpos)++] = (int16_t)mul_modq(b1[4*block + lane], tw1);
	}
}

static void reference_stage1_dft3_input(poly *r, const poly *a)
{
	int b0[384];
	int b1[384];
	int outpos = 0;

	/* my_ntt.s uses the Neon Barrett multiplier form.  This reference keeps
	 * only the mathematical residue: top_zeta_mont = -1033 corresponds to
	 * the normal field multiplier -722.
	 */
	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		const int low = a->coeffs[i];
		const int high = a->coeffs[i + NTRUPLUS_N / 2];
		const int t = mul_modq(high, -722);

		b0[i] = modq(low + t);
		b1[i] = modq(low + high - t);
	}

	for (int loop = 0; loop < 8; loop++)
	{
		const int a_base = 4 * loop;
		const int b_base = 32 + 4 * loop;
		const int c_base = 64 + 4 * loop;
		const int order[12] = {
			a_base + 0, c_base + 0, b_base + 0,
			b_base + 1, a_base + 1, c_base + 1,
			c_base + 2, b_base + 2, a_base + 2,
			a_base + 3, c_base + 3, b_base + 3
		};

		for (int i = 0; i < 12; i++)
		{
			store_stage1_pack(r, &outpos, b0, b1, order[i]);
		}
	}
}
#endif

#if POLYNTT_ASM_STAGE2_DFT3
static int stage1_value(const int b0[384],
                        const int b1[384],
                        int branch,
                        int block,
                        int lane)
{
	const int *b = branch == 0 ? b0 : b1;

	return mul_modq(b[4*block + lane], twist_normal(branch, block));
}

static void store_stage2_dft3_column(poly *r,
                                     const int b0[384],
                                     const int b1[384],
                                     int n32,
                                     int x0_block,
                                     int x1_block,
                                     int x2_block)
{
	for (int branch = 0; branch < 2; branch++)
	{
		for (int lane = 0; lane < 4; lane++)
		{
			const int x0 = stage1_value(b0, b1, branch, x0_block, lane);
			const int x1 = stage1_value(b0, b1, branch, x1_block, lane);
			const int x2 = stage1_value(b0, b1, branch, x2_block, lane);
			const int d = x1 - x2;
			const int t = mul_modq(d, -723);
			const int packed_lane = 4*branch + lane;

			r->coeffs[(0*32 + n32)*8 + packed_lane] =
				(int16_t)modq(x0 + x1 + x2);
			r->coeffs[(1*32 + n32)*8 + packed_lane] =
				(int16_t)modq(x0 - x2 + t);
			r->coeffs[(2*32 + n32)*8 + packed_lane] =
				(int16_t)modq(x0 - x1 - t);
		}
	}
}

static void reference_stage2_dft3_output(poly *r, const poly *a)
{
	int b0[384];
	int b1[384];

	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		const int low = a->coeffs[i];
		const int high = a->coeffs[i + NTRUPLUS_N / 2];
		const int t = mul_modq(high, -722);

		b0[i] = modq(low + t);
		b1[i] = modq(low + high - t);
	}

	for (int loop = 0; loop < 8; loop++)
	{
		const int a_base = 4 * loop;
		const int b_base = 32 + 4 * loop;
		const int c_base = 64 + 4 * loop;

		store_stage2_dft3_column(r, b0, b1, a_base + 0,
		                         a_base + 0, c_base + 0, b_base + 0);
		store_stage2_dft3_column(r, b0, b1, a_base + 1,
		                         b_base + 1, a_base + 1, c_base + 1);
		store_stage2_dft3_column(r, b0, b1, a_base + 2,
		                         c_base + 2, b_base + 2, a_base + 2);
		store_stage2_dft3_column(r, b0, b1, a_base + 3,
	                         a_base + 3, c_base + 3, b_base + 3);
	}
}
#endif
#endif

static void reference_poly_ntt(poly *r, const poly *a)
{
#if POLYNTT_ASM_STAGE2_DFT3
	reference_stage2_dft3_output(r, a);
#elif POLYNTT_ASM_STAGE1_ZIP
	reference_stage1_dft3_input(r, a);
#else
	ntt_gt_rowbitrevlayout(r->coeffs, a->coeffs);
#endif
}

static int compare_poly(const char *label, const poly *asm_out, const poly *ref)
{
	int exact_matches = 0;
	int mod_matches = 0;
	int printed = 0;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		const int exact = asm_out->coeffs[i] == ref->coeffs[i];
		const int mod = equal_modq(asm_out->coeffs[i], ref->coeffs[i]);

		exact_matches += exact;
		mod_matches += mod;

		if (!mod && printed < 8)
		{
			printf("  mismatch %-24s i=%3d asm=%7d ref=%7d diff_mod_q=%4d\n",
			       label,
			       i,
			       asm_out->coeffs[i],
			       ref->coeffs[i],
			       modq((int)asm_out->coeffs[i] - (int)ref->coeffs[i]));
			printed++;
		}
	}

	printf("%-28s exact %3d/768, mod-q %3d/768\n",
	       label, exact_matches, mod_matches);

#if POLYNTT_ASM_PARTIAL
	return mod_matches == NTRUPLUS_N;
#elif POLYNTT_ASM_ALLOW_LAZY
	return mod_matches == NTRUPLUS_N;
#else
	return exact_matches == NTRUPLUS_N;
#endif
}

static int compare_to_reference_case(const char *label, const poly *input)
{
	poly ref;
	poly asm_out;

	reference_poly_ntt(&ref, input);
	poly_ntt(&asm_out, input);

	return compare_poly(label, &asm_out, &ref);
}

#if POLYNTT_ASM_DUMP_STAGE2_MEMORY
static void stage2_source_blocks(int n32, int *x0, int *x1, int *x2)
{
	const int loop = n32 / 4;
	const int col = n32 % 4;
	const int a_base = 4 * loop;
	const int b_base = 32 + 4 * loop;
	const int c_base = 64 + 4 * loop;

	switch (col)
	{
	case 0:
		*x0 = a_base + 0;
		*x1 = c_base + 0;
		*x2 = b_base + 0;
		break;
	case 1:
		*x0 = b_base + 1;
		*x1 = a_base + 1;
		*x2 = c_base + 1;
		break;
	case 2:
		*x0 = c_base + 2;
		*x1 = b_base + 2;
		*x2 = a_base + 2;
		break;
	default:
		*x0 = a_base + 3;
		*x1 = c_base + 3;
		*x2 = b_base + 3;
		break;
	}
}

static void dump_stage2_memory(void)
{
	poly input;
	poly asm_out;

	fill_pattern(&input, "ramp", 0);
	poly_ntt(&asm_out, &input);

	printf("stage2 DFT3 row-major memory dump, input=ramp\n");
	printf("memory layout: coeff[(row_k3*32 + n32)*8 + lane]\n");
	printf("lane 0..3 = branch0 quartic lane0..3, lane 4..7 = branch1 quartic lane0..3\n");

	for (int row = 0; row < 3; row++)
	{
		printf("\nrow_k3=%d\n", row);
		for (int n32 = 0; n32 < 32; n32++)
		{
			int x0;
			int x1;
			int x2;
			const int coeff_offset = (row * 32 + n32) * 8;
			const int byte_offset = coeff_offset * (int)sizeof(int16_t);

			stage2_source_blocks(n32, &x0, &x1, &x2);

			printf("  n32=%2d loop=%d col=%d off=%3d byte=%4d "
			       "src_blocks(x0,x1,x2)=(%2d,%2d,%2d) "
			       "lanes=[%6d %6d %6d %6d | %6d %6d %6d %6d]\n",
			       n32,
			       n32 / 4,
			       n32 % 4,
			       coeff_offset,
			       byte_offset,
			       x0,
			       x1,
			       x2,
			       asm_out.coeffs[coeff_offset + 0],
			       asm_out.coeffs[coeff_offset + 1],
			       asm_out.coeffs[coeff_offset + 2],
			       asm_out.coeffs[coeff_offset + 3],
			       asm_out.coeffs[coeff_offset + 4],
			       asm_out.coeffs[coeff_offset + 5],
			       asm_out.coeffs[coeff_offset + 6],
			       asm_out.coeffs[coeff_offset + 7]);
		}
	}
}
#endif

static int check_reference_differential(void)
{
	static const char *patterns[] = {
		"zero",
		"one",
		"alternating_pm1",
		"centered_edges",
		"ramp"
	};
	static const int impulse_positions[] = {
		0, 1, 2, 3, 4, 31, 32, 33,
		127, 128, 255, 256, 383, 384, 511, 512, 767
	};
	poly input;
	char label[64];
	int ok = 1;

	for (unsigned i = 0; i < sizeof(patterns) / sizeof(patterns[0]); i++)
	{
		fill_pattern(&input, patterns[i], 0);
		ok &= compare_to_reference_case(patterns[i], &input);
	}

	for (unsigned i = 0; i < sizeof(impulse_positions) / sizeof(impulse_positions[0]); i++)
	{
		fill_impulse(&input, impulse_positions[i], 1);
		snprintf(label, sizeof(label), "impulse_%03d", impulse_positions[i]);
		ok &= compare_to_reference_case(label, &input);
	}

	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		fill_pattern(&input, "random", 0x9e3779b9u ^ seed);
		snprintf(label, sizeof(label), "random_%u", seed);
		ok &= compare_to_reference_case(label, &input);
	}

	return ok;
}

#if !POLYNTT_ASM_OUTPUT_NOT_POINTWISE
static int check_roundtrip(void)
{
	poly input;
	poly freq;
	poly round;
	int min_matches = NTRUPLUS_N;

	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		int matches = 0;

		fill_pattern(&input, "random", 0x243f6a88u ^ seed);
		poly_ntt(&freq, &input);
		invntt_gt_rowbitrevlayout(round.coeffs, freq.coeffs);

		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			matches += equal_modq(round.coeffs[i], input.coeffs[i]);
		}

		if (matches < min_matches)
		{
			min_matches = matches;
		}
	}

	printf("%-28s mod-q %3d/768\n", "roundtrip", min_matches);
	return min_matches == NTRUPLUS_N;
}

static void rowbitrev_basemul_reference(poly *r, const poly *a, const poly *b)
{
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);

		for (int physical_j = 0; physical_j < 96; physical_j++)
		{
			const int pos = branch_start + 4*physical_j;

			basemul(r->coeffs + pos,
			        a->coeffs + pos,
			        b->coeffs + pos,
			        gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
}

static void schoolbook_mul_reference(poly *r, const poly *a, const poly *b)
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
			tmp[i + j] += (int64_t)a->coeffs[i] * b->coeffs[j];
		}
	}

	/* NTRU+768 ring: X^768 = X^384 - 1. */
	for (int i = 2*NTRUPLUS_N - 2; i >= NTRUPLUS_N; i--)
	{
		const int64_t c = tmp[i];

		tmp[i - NTRUPLUS_N / 2] += c;
		tmp[i - NTRUPLUS_N] -= c;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r->coeffs[i] = (int16_t)modq(tmp[i]);
	}
}

static int check_multiplication(void)
{
	poly a;
	poly b;
	poly A;
	poly B;
	poly C;
	poly product;
	poly schoolbook;
	int min_matches = NTRUPLUS_N;

	for (uint32_t seed = 0; seed < RANDOM_TESTS; seed++)
	{
		int matches = 0;

		fill_pattern(&a, "random", 0xa4093822u ^ seed);
		fill_pattern(&b, "random", 0x299f31d0u ^ seed);
		schoolbook_mul_reference(&schoolbook, &a, &b);

		poly_ntt(&A, &a);
		poly_ntt(&B, &b);
		rowbitrev_basemul_reference(&C, &A, &B);
		invntt_gt_rowbitrevlayout(product.coeffs, C.coeffs);

		for (int i = 0; i < NTRUPLUS_N; i++)
		{
			matches += equal_modq(product.coeffs[i], schoolbook.coeffs[i]);
		}

		if (matches < min_matches)
		{
			min_matches = matches;
		}
	}

	printf("%-28s mod-q %3d/768\n", "multiplication", min_matches);
	return min_matches == NTRUPLUS_N;
}
#endif

int main(void)
{
	int ok = 1;

#if POLYNTT_ASM_DUMP_STAGE2_MEMORY
	dump_stage2_memory();
	return 0;
#endif

	printf("polyntt ASM test policy: %s\n",
#if POLYNTT_ASM_STAGE1_ZIP
	       "stage1 top-split/twist/DFT3-input layout, mod-q equality");
#elif POLYNTT_ASM_STAGE2_DFT3
	       "stage2 DFT3 row-major NTT32 input layout, mod-q equality");
#else
		       POLYNTT_ASM_ALLOW_LAZY ? "mod-q equality accepts lazy reduction"
		                              : "strict exact complete row-bitrev output equality");
#endif

	ok &= check_reference_differential();
#if !POLYNTT_ASM_OUTPUT_NOT_POINTWISE
	ok &= check_roundtrip();
	ok &= check_multiplication();
#endif

	return ok ? 0 : 1;
}

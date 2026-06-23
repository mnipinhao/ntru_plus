#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "gt_tmvp_quartic_tmvp_experimental.h"
#include "ntt.h"
#include "params.h"
#include "poly.h"

#if !defined(GT_TMVP_ENABLE_CANDIDATE_A_BATCH8_KEM)
#error "poly_gt_tmvp_candidate_a_batch8_kem.c requires GT_TMVP_ENABLE_CANDIDATE_A_BATCH8_KEM"
#endif

#if !defined(__aarch64__)
#error "Candidate A batch8 KEM path requires AArch64 assembly"
#endif

#if NTRUPLUS_N != 768
#error "Candidate A batch8 KEM path is specialized for NTRU+768"
#endif

/*
 * Pull in the scalar GT reference transform helpers in this translation unit.
 * Candidate A needs the incomplete stage4 boundary, while baseinv still needs
 * the complete GT NTT internally to compute natural-domain inverses.
 */
#include "ntt.c"

#define GT_BRANCHES 2
#define GT_BRANCH_N (NTRUPLUS_N / GT_BRANCHES)
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_QUARTIC_LANES 4
#define GT_VECTOR_LANES 8

extern void ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end(
	int16_t *row_plane, const int16_t *consts);
extern const int16_t
	ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end_consts[];

extern void ntruplus768_invntt32_rowpack_postmerge_branchfold_asm(
	int16_t *r, const int16_t *work, const int16_t *low_mont,
	const int16_t *high_mont);

static int16_t g_postfold_low_mont[GT_ROWS * GT_ROW_N][GT_VECTOR_LANES]
                                  __attribute__((aligned(16)));
static int16_t g_postfold_high_mont[GT_ROWS * GT_ROW_N][GT_VECTOR_LANES]
                                   __attribute__((aligned(16)));
static int g_postfold_consts_ready;

static inline int16_t crepmod3(int16_t a)
{
	int16_t t;
	const int16_t v = ((1 << 15) + 3 / 2) / 3;

	a += (a >> 15) & NTRUPLUS_Q;
	a -= (NTRUPLUS_Q + 1) / 2;
	a += (a >> 15) & NTRUPLUS_Q;
	a -= (NTRUPLUS_Q - 1) / 2;

	t = ((int32_t)v * a + (1 << 14)) >> 15;
	t *= 3;
	return a - t;
}

static void poly_zero_coeffs(poly *r)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r->coeffs[i] = 0;
	}
}

static int rowpack_index(int branch, int row, int lane, int k32)
{
	return branch * GT_BRANCH_N +
	       row * (GT_QUARTIC_LANES * GT_ROW_N) +
	       lane * GT_ROW_N + k32;
}

static int centered_modq(int64_t x)
{
	int r = (int)(x % NTRUPLUS_Q);

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}
	if (r > NTRUPLUS_Q / 2)
	{
		r -= NTRUPLUS_Q;
	}
	return r;
}

static void ntt32_radix2_ct_bitrev_stage4(int16_t out[GT_ROW_N],
                                          const int16_t in[GT_ROW_N])
{
	for (unsigned i = 0; i < GT_ROW_N; i++)
	{
		out[i] = barrett_reduce(in[i]);
	}

	for (unsigned stage = 1; stage <= 4; stage++)
	{
		const unsigned distance = 1U << (5 - stage);

		for (unsigned lo = 0; lo < GT_ROW_N; lo++)
		{
			if ((lo & distance) != 0)
			{
				continue;
			}

			const unsigned hi = lo + distance;
			const unsigned power = ntt32_ct_twiddle_power(stage, lo);
			const int16_t u = out[lo];
			const int16_t t = fqmul(out[hi], gt96_omega32_powers[power]);

			out[lo] = barrett_reduce(u + t);
			out[hi] = barrett_reduce(u - t);
		}
	}
}

static void ntt_gt_rowpack_soa_stage4_source(
	int16_t r[NTRUPLUS_N],
	const int16_t a[NTRUPLUS_N])
{
	int16_t work[NTRUPLUS_N];

	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		const int16_t t1 =
			fqmul(NTRUPLUS_ZETA_TOP_SPLIT, a[i + NTRUPLUS_N / 2]);

		work[i + NTRUPLUS_N / 2] =
			a[i] + a[i + NTRUPLUS_N / 2] - t1;
		work[i] = a[i] + t1;
	}

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_BRANCH_N;
		const int16_t *twist =
			branch == 0 ? twist_branch0 : twist_branch1;

		for (int i = 0; i < GT_ROWS * GT_ROW_N; i++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				work[branch_start + GT_QUARTIC_LANES * i + lane] =
					fqmul(work[branch_start + GT_QUARTIC_LANES * i + lane],
					      twist[i]);
			}
		}

		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			int16_t mat[GT_ROWS][GT_ROW_N];

			for (int n3 = 0; n3 < GT_ROWS; n3++)
			{
				for (int n32 = 0; n32 < GT_ROW_N; n32++)
				{
					const int n =
						(64 * n3 + 33 * n32) %
						(GT_ROWS * GT_ROW_N);

					mat[n3][n32] =
						work[branch_start +
						     GT_QUARTIC_LANES * n + lane];
				}
			}

			for (int n32 = 0; n32 < GT_ROW_N; n32++)
			{
				dft3_forward(&mat[0][n32], &mat[1][n32],
				             &mat[2][n32]);
			}

			for (int row = 0; row < GT_ROWS; row++)
			{
				int16_t row_stage4[GT_ROW_N];

				ntt32_radix2_ct_bitrev_stage4(row_stage4, mat[row]);
				for (int k32 = 0; k32 < GT_ROW_N; k32++)
				{
					r[rowpack_index(branch, row, lane, k32)] =
						row_stage4[k32];
				}
			}
		}
	}
}

static int normal_from_mont_centered(int16_t a)
{
	return centered_modq(montgomery_reduce(a));
}

static int16_t mont_from_normal_centered(int normal)
{
	return (int16_t)centered_modq(fqmul((int16_t)centered_modq(normal),
	                                    NTRUPLUS_RSQ));
}

static void init_rowpack_postfold_consts(void)
{
	const int z = normal_from_mont_centered(NTRUPLUS_ZMINUSZ5INV);
	const int inv192 = normal_from_mont_centered(NTRUPLUS_NINV);
	const int inv96 = normal_from_mont_centered(NTRUPLUS_2NINV);

	if (g_postfold_consts_ready)
	{
		return;
	}

	for (int n = 0; n < GT_ROWS * GT_ROW_N; n++)
	{
		const int f0 = normal_from_mont_centered(untwist_branch0[n]);
		const int f1 = normal_from_mont_centered(untwist_branch1[n]);
		const int low0 = centered_modq((int64_t)f0 * (1 - z) * inv192);
		const int low1 = centered_modq((int64_t)f1 * (1 + z) * inv192);
		const int high0 = centered_modq((int64_t)f0 * z * inv96);
		const int high1 = centered_modq(-(int64_t)f1 * z * inv96);

		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			g_postfold_low_mont[n][lane] =
				mont_from_normal_centered(low0);
			g_postfold_low_mont[n][GT_QUARTIC_LANES + lane] =
				mont_from_normal_centered(low1);
			g_postfold_high_mont[n][lane] =
				mont_from_normal_centered(high0);
			g_postfold_high_mont[n][GT_QUARTIC_LANES + lane] =
				mont_from_normal_centered(high1);
		}
	}

	g_postfold_consts_ready = 1;
}

static void apply_rowkernel_stage2_to5_asm(
	int16_t r[NTRUPLUS_N],
	const int16_t a[NTRUPLUS_N])
{
	memcpy(r, a, NTRUPLUS_N * sizeof(r[0]));

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				const int pos = rowpack_index(branch, row, lane, 0);

				ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end(
					&r[pos],
					ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end_consts);
			}
		}
	}
}

static void candidate_a_batch8_muladd_natural(poly *r, const poly *a,
                                              const poly *b, const poly *c)
{
	int16_t a_stage4[NTRUPLUS_N];
	int16_t b_stage4[NTRUPLUS_N];
	int16_t c_stage4[NTRUPLUS_N];
	int16_t tmvp_stage1[NTRUPLUS_N];
	int16_t rows[NTRUPLUS_N];
	int status;

	ntt_gt_rowpack_soa_stage4_source(a_stage4, a->coeffs);
	ntt_gt_rowpack_soa_stage4_source(b_stage4, b->coeffs);
	if (c != NULL)
	{
		ntt_gt_rowpack_soa_stage4_source(c_stage4, c->coeffs);
		status = gt_tmvp_quartic_tmvp_add_incomplete_candidate_a_asm(
			tmvp_stage1, a_stage4, b_stage4, c_stage4);
	}
	else
	{
		status = gt_tmvp_quartic_tmvp_incomplete_candidate_a_asm(
			tmvp_stage1, a_stage4, b_stage4);
	}

	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		poly_zero_coeffs(r);
		return;
	}

	init_rowpack_postfold_consts();
	apply_rowkernel_stage2_to5_asm(rows, tmvp_stage1);
	ntruplus768_invntt32_rowpack_postmerge_branchfold_asm(
		r->coeffs, rows, &g_postfold_low_mont[0][0],
		&g_postfold_high_mont[0][0]);
}

void poly_tobytes(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a)
{
	int16_t t[2];

	for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
	{
		t[0] = a->coeffs[2 * i];
		t[0] += (t[0] >> 15) & NTRUPLUS_Q;
		t[1] = a->coeffs[2 * i + 1];
		t[1] += (t[1] >> 15) & NTRUPLUS_Q;

		r[3 * i + 0] = (uint8_t)(t[0] >> 0);
		r[3 * i + 1] = (uint8_t)((t[0] >> 8) | (t[1] << 4));
		r[3 * i + 2] = (uint8_t)(t[1] >> 4);
	}
}

void poly_frombytes(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES])
{
	for (size_t i = 0; i < NTRUPLUS_N / 2; i++)
	{
		r->coeffs[2 * i] =
			((a[3 * i + 0] >> 0) | ((uint16_t)a[3 * i + 1] << 8)) & 0xFFF;
		r->coeffs[2 * i + 1] =
			((a[3 * i + 1] >> 4) | ((uint16_t)a[3 * i + 2] << 4)) & 0xFFF;
	}
}

void poly_cbd1(poly *r, const uint8_t buf[NTRUPLUS_N / 4])
{
	uint8_t t1;
	uint8_t t2;

	for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
	{
		t1 = buf[i];
		t2 = buf[i + NTRUPLUS_N / 8];

		for (size_t j = 0; j < 8; j++)
		{
			r->coeffs[8 * i + j] = (int16_t)((t1 & 0x1) - (t2 & 0x1));

			t1 >>= 1;
			t2 >>= 1;
		}
	}
}

void poly_sotp_encode(poly *r, const uint8_t msg[NTRUPLUS_N / 8],
                      const uint8_t buf[NTRUPLUS_N / 4])
{
	uint8_t tmp[NTRUPLUS_N / 4];

	for (int i = 0; i < NTRUPLUS_N / 8; i++)
	{
		tmp[i] = buf[i] ^ msg[i];
	}

	for (int i = NTRUPLUS_N / 8; i < NTRUPLUS_N / 4; i++)
	{
		tmp[i] = buf[i];
	}

	poly_cbd1(r, tmp);
}

int poly_sotp_decode(uint8_t msg[NTRUPLUS_N / 8], const poly *a,
                     const uint8_t buf[NTRUPLUS_N / 4])
{
	uint8_t t1;
	uint8_t t2;
	uint8_t t3;
	uint16_t t4;
	uint32_t ret = 0;
	uint8_t mask;

	for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
	{
		t1 = buf[i];
		t2 = buf[i + NTRUPLUS_N / 8];
		t3 = 0;

		for (size_t j = 0; j < 8; j++)
		{
			t4 = t2 & 0x1;
			t4 += (uint16_t)a->coeffs[8 * i + j];
			ret |= t4;
			t4 = (t4 ^ t1) & 0x1;
			t3 ^= (uint8_t)(t4 << j);

			t1 >>= 1;
			t2 >>= 1;
		}

		msg[i] = t3;
	}

	ret = ret >> 1;
	ret = (-(uint32_t)ret) >> 31;
	mask = (uint8_t)(ret - 1);

	for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
	{
		msg[i] &= mask;
	}

	return (int)ret;
}

void poly_ntt(poly *r, const poly *a)
{
	if (r != a)
	{
		memcpy(r->coeffs, a->coeffs, sizeof(r->coeffs));
	}
}

void poly_invntt(poly *r, const poly *a)
{
	if (r != a)
	{
		memcpy(r->coeffs, a->coeffs, sizeof(r->coeffs));
	}
}

int poly_baseinv(poly *r, const poly *a)
{
	poly freq;
	poly inv_freq;

	ntt(freq.coeffs, a->coeffs);

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_BRANCH_N;

		for (int physical_j = 0; physical_j < GT_ROWS * GT_ROW_N;
		     physical_j++)
		{
			const int pos = branch_start + GT_QUARTIC_LANES * physical_j;

			if (baseinv(inv_freq.coeffs + pos, freq.coeffs + pos,
			            gt_rowbitrev_lambda[branch][physical_j]))
			{
				poly_zero_coeffs(r);
				return 1;
			}
		}
	}

	invntt(r->coeffs, inv_freq.coeffs);
	return 0;
}

void poly_basemul(poly *r, const poly *a, const poly *b)
{
	candidate_a_batch8_muladd_natural(r, a, b, NULL);
}

void poly_basemul_add(poly *r, const poly *a, const poly *b, const poly *c)
{
	candidate_a_batch8_muladd_natural(r, a, b, c);
}

void poly_sub(poly *r, const poly *a, const poly *b)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r->coeffs[i] = a->coeffs[i] - b->coeffs[i];
	}
}

void poly_triple(poly *r, const poly *a)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r->coeffs[i] = 3 * a->coeffs[i];
	}
}

void poly_crepmod3(poly *r, const poly *a)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r->coeffs[i] = crepmod3(a->coeffs[i]);
	}
}

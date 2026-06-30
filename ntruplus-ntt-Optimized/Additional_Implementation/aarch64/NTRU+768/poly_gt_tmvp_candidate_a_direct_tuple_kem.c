#include <stddef.h>
#include <stdint.h>

#include "ntt.h"
#include "params.h"
#include "poly.h"

#if !defined(GT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_KEM)
#error "poly_gt_tmvp_candidate_a_direct_tuple_kem.c requires GT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_KEM"
#endif

#if defined(GT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM) && \
	!defined(__aarch64__)
#error "GT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM requires AArch64"
#endif

#if NTRUPLUS_N != 768
#error "Candidate A direct tuple KEM path is specialized for NTRU+768"
#endif

#define GT_TMVP_BRANCHES 2
#define GT_TMVP_BRANCH_N (NTRUPLUS_N / GT_TMVP_BRANCHES)
#define GT_TMVP_BLOCKS_PER_BRANCH 96
#define GT_TMVP_ROWS 3
#define GT_TMVP_ROW_N 32
#define GT_TMVP_QUARTIC_LANES 4

#if defined(GT_TMVP_USE_DIRECT_TUPLE_NTT_ASM)
void gt_candidate_a_direct_tuple_poly_ntt(poly *r, const poly *a);
#endif

#if defined(GT_TMVP_USE_BLOCK_MAJOR_INVNTT_ASM)
void gt_block_major_poly_invntt(poly *r, const poly *a);
#endif

#if defined(GT_TMVP_USE_TUPLE_INVNTT_ASM)
void gt_tuple_poly_invntt(poly *r, const poly *a);
#endif

#if defined(GT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM)
void candidate_a_direct_tuple_basemul_asm_fast(poly *r, const poly *a,
                                               const poly *b);
void candidate_a_direct_tuple_basemul_add_asm_fast(poly *r, const poly *a,
                                                   const poly *b,
                                                   const poly *c);
#endif

#if defined(GT_TMVP_USE_BATCH_BASEINV)
int poly_baseinv_gt_tuple_batch(poly *r, const poly *a);
#endif

static void poly_zero_coeffs(poly *r)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r->coeffs[i] = 0;
	}
}

static int block_major_index(int branch, int physical_j, int lane)
{
	return branch * GT_TMVP_BRANCH_N +
	       GT_TMVP_QUARTIC_LANES * physical_j + lane;
}

static int tuple_index(int branch, int row, int k32, int lane)
{
	return branch * GT_TMVP_BRANCH_N +
	       row * (GT_TMVP_ROW_N * GT_TMVP_QUARTIC_LANES) +
	       GT_TMVP_QUARTIC_LANES * k32 + lane;
}

static int tuple_physical_j(int row, int k32)
{
	return (GT_TMVP_ROW_N * row + GT_TMVP_ROWS * k32) %
	       GT_TMVP_BLOCKS_PER_BRANCH;
}

static void block_major_to_tuple(int16_t tuple[NTRUPLUS_N],
                                 const int16_t block_major[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_TMVP_ROW_N; k32++)
			{
				const int physical_j = tuple_physical_j(row, k32);

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int tuple_idx =
						tuple_index(branch, row, k32, lane);
					const int block_idx =
						block_major_index(branch, physical_j, lane);

					tuple[tuple_idx] = block_major[block_idx];
				}
			}
		}
	}
}

static void tuple_to_block_major(int16_t block_major[NTRUPLUS_N],
                                 const int16_t tuple[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_TMVP_ROW_N; k32++)
			{
				const int physical_j = tuple_physical_j(row, k32);

				for (int lane = 0; lane < GT_TMVP_QUARTIC_LANES; lane++)
				{
					const int tuple_idx =
						tuple_index(branch, row, k32, lane);
					const int block_idx =
						block_major_index(branch, physical_j, lane);

					block_major[block_idx] = tuple[tuple_idx];
				}
			}
		}
	}
}

#if !defined(GT_TMVP_USE_STOCK_SUPPORT_ASM)
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
#endif

void poly_ntt(poly *r, const poly *a)
{
#if defined(GT_TMVP_USE_DIRECT_TUPLE_NTT_ASM)
	gt_candidate_a_direct_tuple_poly_ntt(r, a);
#else
	int16_t block_major[NTRUPLUS_N];

	ntt(block_major, a->coeffs);
	block_major_to_tuple(r->coeffs, block_major);
#endif
}

void poly_invntt(poly *r, const poly *a)
{
#if defined(GT_TMVP_USE_TUPLE_INVNTT_ASM)
	gt_tuple_poly_invntt(r, a);
#elif defined(GT_TMVP_USE_BLOCK_MAJOR_INVNTT_ASM)
	poly block_major;

	tuple_to_block_major(block_major.coeffs, a->coeffs);
	gt_block_major_poly_invntt(r, &block_major);
#else
	int16_t block_major[NTRUPLUS_N];

	tuple_to_block_major(block_major, a->coeffs);
	invntt(r->coeffs, block_major);
#endif
}

int poly_baseinv(poly *r, const poly *a)
{
#if defined(GT_TMVP_USE_BATCH_BASEINV)
	return poly_baseinv_gt_tuple_batch(r, a);
#else
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_TMVP_ROW_N; k32++)
			{
				const int pos = tuple_index(branch, row, k32, 0);
				const int physical_j = tuple_physical_j(row, k32);

				if (baseinv(r->coeffs + pos, a->coeffs + pos,
				            gt_rowbitrev_lambda[branch][physical_j]) != 0)
				{
					poly_zero_coeffs(r);
					return 1;
				}
			}
		}
	}

	return 0;
#endif
}

static void tuple_basemul_c(poly *r, const poly *a, const poly *b)
{
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_TMVP_ROW_N; k32++)
			{
				const int pos = tuple_index(branch, row, k32, 0);
				const int physical_j = tuple_physical_j(row, k32);

				basemul(r->coeffs + pos, a->coeffs + pos, b->coeffs + pos,
				        gt_rowbitrev_lambda[branch][physical_j]);
			}
		}
	}
}

static void tuple_basemul_add_c(poly *r, const poly *a, const poly *b,
                                const poly *c)
{
	for (int branch = 0; branch < GT_TMVP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_TMVP_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_TMVP_ROW_N; k32++)
			{
				const int pos = tuple_index(branch, row, k32, 0);
				const int physical_j = tuple_physical_j(row, k32);

				basemul_add(r->coeffs + pos, a->coeffs + pos, b->coeffs + pos,
				            c->coeffs + pos,
				            gt_rowbitrev_lambda[branch][physical_j]);
			}
		}
	}
}

void poly_basemul(poly *r, const poly *a, const poly *b)
{
#if defined(GT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM)
	candidate_a_direct_tuple_basemul_asm_fast(r, a, b);
#else
	tuple_basemul_c(r, a, b);
#endif
}

void poly_basemul_add(poly *r, const poly *a, const poly *b, const poly *c)
{
#if defined(GT_TMVP_ENABLE_CANDIDATE_A_DIRECT_TUPLE_BASEMUL_ASM)
	candidate_a_direct_tuple_basemul_add_asm_fast(r, a, b, c);
#else
	tuple_basemul_add_c(r, a, b, c);
#endif
}

#if !defined(GT_TMVP_USE_STOCK_SUPPORT_ASM)
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
#endif

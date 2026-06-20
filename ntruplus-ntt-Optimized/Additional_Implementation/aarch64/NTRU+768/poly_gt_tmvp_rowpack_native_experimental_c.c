#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "gt_tmvp_quartic_tmvp_experimental.h"
#include "params.h"
#include "poly.h"

#if !defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C) && \
	!defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM)
#error "poly_gt_tmvp_rowpack_native_experimental_c.c requires an experimental GT TMVP backend"
#endif

#if defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM) && \
	!defined(__aarch64__)
#error "GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM requires AArch64"
#endif

#if defined(GT_TMVP_ROWPACK_NATIVE_AARCH64_FULL_PIPELINE) && \
	!defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM)
#error "GT_TMVP_ROWPACK_NATIVE_AARCH64_FULL_PIPELINE requires the ASM TMVP backend"
#endif

#if defined(GT_TMVP_ROWPACK_NATIVE_AARCH64_FULL_PIPELINE) && \
	!defined(__aarch64__)
#error "GT_TMVP_ROWPACK_NATIVE_AARCH64_FULL_PIPELINE requires AArch64"
#endif

#if NTRUPLUS_N != 768
#error "poly_gt_tmvp_rowpack_native_experimental_c.c is specialized for NTRU+768"
#endif

/*
 * This is an opt-in experiment: include the scalar reference NTT internals so
 * the wrapper can produce and consume rowpack directly without touching the
 * production poly/NTT ABI.
 */
#include "ntt.c"

#define GT_RP_BRANCHES 2
#define GT_RP_BRANCH_N (NTRUPLUS_N / GT_RP_BRANCHES)
#define GT_RP_ROWS 3
#define GT_RP_ROW_N 32
#define GT_RP_QUARTIC_LANES 4
#define GT_RP_VECTOR_LANES 8

#if defined(GT_TMVP_ROWPACK_NATIVE_AARCH64_FULL_PIPELINE)
void ntruplus768_invntt32_rowpack_soa_row(int16_t *row_plane,
                                          const int16_t *consts);
extern const int16_t ntruplus768_invntt32_rowpack_soa_row_consts[];
void ntruplus768_invntt32_rowpack_postmerge_branchfold_asm(
	int16_t *r, const int16_t *work, const int16_t *low_mont,
	const int16_t *high_mont);

static int16_t gt_rp_postfold_low_mont[GT_RP_ROWS * GT_RP_ROW_N]
                                      [GT_RP_VECTOR_LANES]
	__attribute__((aligned(16)));
static int16_t gt_rp_postfold_high_mont[GT_RP_ROWS * GT_RP_ROW_N]
                                       [GT_RP_VECTOR_LANES]
	__attribute__((aligned(16)));
static int gt_rp_postfold_consts_ready;
#endif

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

static int rowpack_index(int branch, int row, int lane, int k32)
{
	return branch * GT_RP_BRANCH_N +
	       row * (GT_RP_QUARTIC_LANES * GT_RP_ROW_N) +
	       lane * GT_RP_ROW_N + k32;
}

static int physical_j_from_row_k32(int row, int k32)
{
	return (GT_RP_ROW_N * row + GT_RP_ROWS * k32) %
	       (GT_RP_ROWS * GT_RP_ROW_N);
}

#if defined(GT_TMVP_ROWPACK_NATIVE_AARCH64_FULL_PIPELINE)
static int centered_modq_i64(int64_t a)
{
	int r = (int)(a % NTRUPLUS_Q);

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

static int normal_from_mont_centered(int16_t a)
{
	return centered_modq_i64(montgomery_reduce(a));
}

static int16_t mont_from_normal_centered(int normal)
{
	return (int16_t)centered_modq_i64(
		fqmul((int16_t)centered_modq_i64(normal), NTRUPLUS_RSQ));
}

static void gt_rp_init_postfold_consts(void)
{
	const int z = normal_from_mont_centered(NTRUPLUS_ZMINUSZ5INV);
	const int inv192 = normal_from_mont_centered(NTRUPLUS_NINV);
	const int inv96 = normal_from_mont_centered(NTRUPLUS_2NINV);

	if (gt_rp_postfold_consts_ready)
	{
		return;
	}

	for (int n = 0; n < GT_RP_ROWS * GT_RP_ROW_N; n++)
	{
		const int f0 = normal_from_mont_centered(untwist_branch0[n]);
		const int f1 = normal_from_mont_centered(untwist_branch1[n]);
		const int low0 = centered_modq_i64((int64_t)f0 * (1 - z) * inv192);
		const int low1 = centered_modq_i64((int64_t)f1 * (1 + z) * inv192);
		const int high0 = centered_modq_i64((int64_t)f0 * z * inv96);
		const int high1 = centered_modq_i64(-(int64_t)f1 * z * inv96);

		for (int lane = 0; lane < GT_RP_QUARTIC_LANES; lane++)
		{
			gt_rp_postfold_low_mont[n][lane] =
				mont_from_normal_centered(low0);
			gt_rp_postfold_low_mont[n][GT_RP_QUARTIC_LANES + lane] =
				mont_from_normal_centered(low1);
			gt_rp_postfold_high_mont[n][lane] =
				mont_from_normal_centered(high0);
			gt_rp_postfold_high_mont[n][GT_RP_QUARTIC_LANES + lane] =
				mont_from_normal_centered(high1);
		}
	}

	gt_rp_postfold_consts_ready = 1;
}

static void gt_rp_apply_no_entry_no_end_rowkernels(int16_t work[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_RP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_RP_ROWS; row++)
		{
			for (int lane = 0; lane < GT_RP_QUARTIC_LANES; lane++)
			{
				ntruplus768_invntt32_rowpack_soa_row(
					&work[rowpack_index(branch, row, lane, 0)],
					ntruplus768_invntt32_rowpack_soa_row_consts);
			}
		}
	}
}
#endif

static void poly_zero_coeffs(poly *r)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r->coeffs[i] = 0;
	}
}

static int gt_tmvp_backend_mul(int16_t r[NTRUPLUS_N],
                               const int16_t a[NTRUPLUS_N],
                               const int16_t b[NTRUPLUS_N])
{
#if defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM)
	return gt_tmvp_quartic_tmvp_experimental_asm_fast(r, a, b);
#else
	return gt_tmvp_quartic_tmvp_experimental_c(r, a, b);
#endif
}

static int gt_tmvp_backend_add(int16_t r[NTRUPLUS_N],
                               const int16_t a[NTRUPLUS_N],
                               const int16_t b[NTRUPLUS_N],
                               const int16_t c[NTRUPLUS_N])
{
#if defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM)
	return gt_tmvp_quartic_tmvp_add_experimental_asm_fast(r, a, b, c);
#else
	return gt_tmvp_quartic_tmvp_add_experimental_c(r, a, b, c);
#endif
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

#if !defined(GT_TMVP_ROWPACK_NATIVE_AARCH64_FULL_PIPELINE)
void poly_ntt(poly *r, const poly *a)
{
	int16_t work[NTRUPLUS_N];
	int16_t t1;

	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		t1 = fqmul(NTRUPLUS_ZETA_TOP_SPLIT, a->coeffs[i + NTRUPLUS_N / 2]);

		work[i + NTRUPLUS_N / 2] =
			a->coeffs[i] + a->coeffs[i + NTRUPLUS_N / 2] - t1;
		work[i] = a->coeffs[i] + t1;
	}

	for (int branch = 0; branch < GT_RP_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_RP_BRANCH_N;
		const int16_t *twist =
			branch == 0 ? twist_branch0 : twist_branch1;

		for (int i = 0; i < GT_RP_ROWS * GT_RP_ROW_N; i++)
		{
			for (int lane = 0; lane < GT_RP_QUARTIC_LANES; lane++)
			{
				work[branch_start + GT_RP_QUARTIC_LANES * i + lane] =
					fqmul(work[branch_start +
					           GT_RP_QUARTIC_LANES * i + lane],
					      twist[i]);
			}
		}

		for (int lane = 0; lane < GT_RP_QUARTIC_LANES; lane++)
		{
			int16_t in[GT_RP_ROWS * GT_RP_ROW_N];
			int16_t out[GT_RP_ROWS * GT_RP_ROW_N];

			for (int i = 0; i < GT_RP_ROWS * GT_RP_ROW_N; i++)
			{
				in[i] =
					work[branch_start + GT_RP_QUARTIC_LANES * i + lane];
			}

			ntt96_goodthomas(out, in);

			for (int row = 0; row < GT_RP_ROWS; row++)
			{
				for (int k32 = 0; k32 < GT_RP_ROW_N; k32++)
				{
					const int physical_j =
						physical_j_from_row_k32(row, k32);

					r->coeffs[rowpack_index(branch, row, lane, k32)] =
						out[physical_j];
				}
			}
		}
	}
}
#endif

void poly_invntt(poly *r, const poly *a)
{
#if defined(GT_TMVP_ROWPACK_NATIVE_AARCH64_FULL_PIPELINE)
	int16_t work[NTRUPLUS_N];

	memcpy(work, a->coeffs, sizeof(work));
	gt_rp_apply_no_entry_no_end_rowkernels(work);
	gt_rp_init_postfold_consts();
	ntruplus768_invntt32_rowpack_postmerge_branchfold_asm(
		r->coeffs, work, &gt_rp_postfold_low_mont[0][0],
		&gt_rp_postfold_high_mont[0][0]);
#else
	int16_t branches[NTRUPLUS_N];
	int16_t t1;
	int16_t t2;

	for (int branch = 0; branch < GT_RP_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_RP_BRANCH_N;
		const int16_t *untwist =
			branch == 0 ? untwist_branch0 : untwist_branch1;

		for (int lane = 0; lane < GT_RP_QUARTIC_LANES; lane++)
		{
			int16_t rowbitrev_freq[GT_RP_ROWS * GT_RP_ROW_N];
			int16_t coeffs[GT_RP_ROWS * GT_RP_ROW_N];

			for (int row = 0; row < GT_RP_ROWS; row++)
			{
				for (int k32 = 0; k32 < GT_RP_ROW_N; k32++)
				{
					const int physical_j =
						physical_j_from_row_k32(row, k32);

					rowbitrev_freq[physical_j] =
						a->coeffs[rowpack_index(branch, row, lane, k32)];
				}
			}

			invntt96_goodthomas_rowfirst(coeffs, rowbitrev_freq);

			for (int i = 0; i < GT_RP_ROWS * GT_RP_ROW_N; i++)
			{
				branches[branch_start + GT_RP_QUARTIC_LANES * i + lane] =
					fqmul(coeffs[i], untwist[i]);
			}
		}
	}

	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		t1 = branches[i] + branches[i + NTRUPLUS_N / 2];
		t2 = fqmul(NTRUPLUS_ZMINUSZ5INV,
		           branches[i] - branches[i + NTRUPLUS_N / 2]);

		r->coeffs[i] = fqmul(NTRUPLUS_NINV, t1 - t2);
		r->coeffs[i + NTRUPLUS_N / 2] = fqmul(NTRUPLUS_2NINV, t2);
	}
#endif
}

int poly_baseinv(poly *r, const poly *a)
{
	for (int branch = 0; branch < GT_RP_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_RP_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_RP_ROW_N; k32++)
			{
				int16_t aa[GT_RP_QUARTIC_LANES];
				int16_t rr[GT_RP_QUARTIC_LANES];
				const int physical_j =
					physical_j_from_row_k32(row, k32);

				for (int lane = 0; lane < GT_RP_QUARTIC_LANES; lane++)
				{
					aa[lane] =
						a->coeffs[rowpack_index(branch, row, lane, k32)];
				}

				if (baseinv(rr, aa, gt_rowbitrev_lambda[branch][physical_j]) != 0)
				{
					poly_zero_coeffs(r);
					return 1;
				}

				for (int lane = 0; lane < GT_RP_QUARTIC_LANES; lane++)
				{
					r->coeffs[rowpack_index(branch, row, lane, k32)] =
						rr[lane];
				}
			}
		}
	}

	return 0;
}

void poly_basemul(poly *r, const poly *a, const poly *b)
{
	if (gt_tmvp_backend_mul(r->coeffs, a->coeffs, b->coeffs) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		poly_zero_coeffs(r);
	}
}

void poly_basemul_add(poly *r, const poly *a, const poly *b, const poly *c)
{
	if (gt_tmvp_backend_add(r->coeffs, a->coeffs, b->coeffs, c->coeffs) !=
	    GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		poly_zero_coeffs(r);
	}
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

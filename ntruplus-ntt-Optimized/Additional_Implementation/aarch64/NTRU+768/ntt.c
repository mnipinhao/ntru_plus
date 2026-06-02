#include <stdint.h>
#include "params.h"
#include "ntt.h"

#if defined(__GNUC__) || defined(__clang__)
#define NTRUPLUS_UNUSED __attribute__((unused))
#else
#define NTRUPLUS_UNUSED
#endif

#define NTRUPLUS_R            -147 // R = 2^16 mod q
#define NTRUPLUS_RINV         -682 // (R)^(-1) mod q
#define NTRUPLUS_RSQ           867 // (R^2) mod q
#define NTRUPLUS_HALF         1655 // (1/2 * R) mod q
#define NTRUPLUS_QINV        12929 // (q)^(-1) mod (2^16)

#define NTRUPLUS_OMEGA        -886 // (omega * R) mod q
#define NTRUPLUS_ZMINUSZ5INV -1665 // (z - z^5)^(-1) * R mod q
                                   // where z = zeta^((n/d)/6)
#define NTRUPLUS_ZETA_TOP_SPLIT -1033 // top split constant in Montgomery form

#define GT96_OMEGA3     NTRUPLUS_OMEGA // (omega96^32 * R) mod q
#define GT96_OMEGA3_SQ        1033 // (omega96^64 * R) mod q

#define NTRUPLUS_NINV         -811 // (n/d)^(-1) * R mod q
#define NTRUPLUS_2NINV       -1622 // 2 * (n/d)^(-1) * R mod q

/*
 * Branch twist/untwist tables in Montgomery form.
 *
 *   twist_branch*   : F_b^{-k} * R, used by forward ntt()
 *   untwist_branch* : F_b^k * R, used by inverse ntt()
 *
 * After the first split, branch b is r[b*384 .. b*384+383].  For each
 * branch polynomial A_b(y) = sum_k a_{4k+r} y^k, the forward twist uses
 * a_{4k+r} -> a_{4k+r} * F_b^{-k}.  The matching reference evaluation is
 * at alpha = F_b * lambda, since
 *
 *   sum_k a_k F_b^{-k} alpha^k = A_b(alpha / F_b).
 *
 * The factors are chosen so alpha^96 = 1 for the 96-point cyclic NTT:
 *   branch 0: F_0 = 2
 *   branch 1: F_1 = 22
 */
static const int16_t twist_branch0[96] = {
	-147,   1655,   -901,   1278,    639,  -1409,   1024,    512,
	 256,    128,     64,     32,     16,      8,      4,      2,
	   1,  -1728,   -864,   -432,   -216,   -108,    -54,    -27,
	1715,   -871,   1293,  -1082,   -541,   1458,    729,  -1364,
	-682,   -341,   1558,    779,  -1339,   1059,  -1199,   1129,
   -1164,   -582,   -291,   1583,   -937,   1260,    630,    315,
   -1571,    943,  -1257,   1100,    550,    275,  -1591,    933,
   -1262,   -631,   1413,  -1022,   -511,   1473,   -992,   -496,
	-248,   -124,    -62,    -31,   1713,   -872,   -436,   -218,
	-109,   1674,    837,  -1310,   -655,   1401,  -1028,   -514,
	-257,   1600,    800,    400,    200,    100,     50,     25,
   -1716,   -858,   -429,   1514,    757,  -1350,   -675,   1391,
};
static const int16_t twist_branch1[96] = {
	-147,    779,   -436,    923,  -1058,   1209,  -1045,   1681,
	-395,   1082,    992,  -1212,   1202,   1626,   1331,  -1668,
	 867,   -432,  -1591,   -858,    -39,  -1416,   1507,  -1660,
	-704,    -32,   -630,  -1600,   -387,   -489,   1392,   -251,
	 460,   1278,  -1199,   1674,  -1181,    732,   -281,  -1427,
	-222,   1247,   -729,    124,   1577,   -714,   -661,  -1130,
	1520,  -1188,    -54,   -631,    757,   -437,   -177,  -1108,
	1521,    -88,     -4,   -943,   -200,   1248,    371,    174,
	1265,  -1671,   1024,   -582,   -655,  -1444,  -1637,    397,
	1118,   -892,    588,    341,  -1713,   -235,    775,  -1379,
	 723,    190,   1580,   -871,   -511,   1391,  -1351,    410,
	1590,   -242,    -11,   1728,   -550,    -25,    156,  -1250,
};
static const int16_t untwist_branch0[96] = {
	-147,   -294,   -588,  -1176,   1105,  -1247,    963,  -1531,
	 395,    790,   1580,   -297,   -594,  -1188,   1081,  -1295,
	 867,  -1723,     11,     22,     44,     88,    176,    352,
	 704,   1408,   -641,  -1282,    893,  -1671,    115,    230,
	 460,    920,  -1617,    223,    446,    892,  -1673,    111,
	 222,    444,    888,  -1681,     95,    190,    380,    760,
	1520,   -417,   -834,  -1668,    121,    242,    484,    968,
   -1521,    415,    830,   1660,   -137,   -274,   -548,  -1096,
	1265,   -927,   1603,   -251,   -502,  -1004,   1449,   -559,
   -1118,   1221,  -1015,   1427,   -603,  -1206,   1045,  -1367,
	 723,   1446,   -565,  -1130,   1197,  -1063,   1331,   -795,
   -1590,    277,    554,   1108,  -1241,    975,  -1507,    443,
};
static const int16_t untwist_branch1[96] = {
	-147,    223,   1449,    765,   -455,    361,   1028,  -1583,
	-256,   1282,    548,   1685,   -957,   -312,     50,   1100,
	   1,     22,    484,    277,   -820,   -755,    675,   1022,
   -1715,    297,   -380,  -1446,   -699,  -1550,    470,    -31,
	-682,  -1176,  -1673,   1221,   -794,   -183,   -569,   1310,
	1164,   1409,   -115,    927,   -348,   -742,    961,    400,
   -1571,      8,    176,    415,  -1241,    354,    874,  -1514,
	1262,    108,  -1081,    417,  -1197,   1322,   1428,    303,
	-248,   1458,    963,    444,   -603,    562,  -1464,  -1095,
	 109,  -1059,    901,   -920,    502,    673,    978,    774,
	-257,   1260,     64,   1408,   -137,    443,   -625,     78,
	1716,   -275,    864,   1723,   -121,    795,    205,   1053,
};

/*
 * Good-Thomas reference constants for the cyclic 96-point NTT.
 *
 * The canonical primitive 96th root is omega96 = 675 in normal form.  This
 * root is branch 1 block 0 after applying the verified F_b scaling, and every
 * alpha = F_b * lambda used by the two branches is a power of it.  The tables
 * below are in Montgomery form when they are used by fqmul().
 *
 * TODO: it can only use one table, because omega32_inv_powers is the reverse of omega32_powers. So if you want to use inv_powers you can read gt96_omega32_powers[32] backwards.
 */
static const int16_t gt96_omega32_powers[32] = {
	 -147,    484,   -794,    874,    109,    864,   -446,   -554,
	  366,   -429,  -1339,     11,  -1118,    177,   1181,   1591,
	  147,   -484,    794,   -874,   -109,   -864,    446,    554,
	 -366,    429,   1339,    -11,   1118,   -177,  -1181,  -1591,
};

static const int16_t gt96_omega32_inv_powers[32] = {
	 -147,  -1591,  -1181,   -177,   1118,    -11,   1339,    429,
	 -366,    554,    446,   -864,   -109,   -874,    794,   -484,
	  147,   1591,   1181,    177,  -1118,     11,  -1339,   -429,
	  366,   -554,   -446,    864,    109,    874,   -794,    484,
};

/*
 * Good-Thomas quartic folding constants in centered signed Montgomery form.
 *
 * The table is indexed by logical Good-Thomas output j.  In row-bitrev
 * physical layout, recover the logical index with
 * gt96_rowbitrev_logical_index(physical_j) before using this table.  The
 * quartic block is interpreted in Z_q[X] / (X^4 - lambda_j), where
 *   branch 0: lambda_j = omega96^j / 2
 *   branch 1: lambda_j = omega96^j / 22
 * and omega96 = 675.  These constants are not butterfly twiddles; they are
 * the per-block zeta values passed to basemul()/baseinv().
 *
 * TODO: it can store half like gt_lambda[2][48], because lambda_j is symmetric.
 */
const int16_t gt_lambda[2][96] = {
	{
		 1655,    514,   1250,    242,    871,    235,   -397,   1671,
		  943,    437,   1130,  -1247,  -1674,    489,   1660,    432,
		 1212,  -1209,   -223,   1583,    312,   -277,   -297,     31,
		  183,   -927,     -8,   1514,  -1322,   -444,   1059,   -774,
		 -443,  -1723,  -1473,   1341,   -559,   -512,    100,  -1640,
		 -760,  -1364,  -1138,   -696,    352,   -933,   -601,  -1206,
		-1655,   -514,  -1250,   -242,   -871,   -235,    397,  -1671,
		 -943,   -437,  -1130,   1247,   1674,   -489,  -1660,   -432,
		-1212,   1209,    223,  -1583,   -312,    277,    297,    -31,
		 -183,    927,      8,  -1514,   1322,    444,  -1059,    774,
		  443,   1723,   1473,  -1341,    559,    512,   -100,   1640,
		  760,   1364,   1138,    696,   -352,    933,    601,   1206
	},
	{
		  779,    361,   1685,     22,   1022,  -1550,   1221,   1409,
		  400,    354,    417,   1458,  -1095,    673,   1408,   -275,
		 1053,  -1367,    294,   1401,  -1543,   -968,    -27,   -940,
		 1588,    230,   -315,   1709,  -1063,   1531,   -218,   1501,
		  274,  -1728,  -1391,   1379,    892,    582,  -1248,   1108,
		 1188,   -124,   -732,    251,     32,    858,  -1626,  -1681,
		 -779,   -361,  -1685,    -22,  -1022,   1550,  -1221,  -1409,
		 -400,   -354,   -417,  -1458,   1095,   -673,  -1408,    275,
		-1053,   1367,   -294,  -1401,   1543,    968,     27,    940,
		-1588,   -230,    315,  -1709,   1063,  -1531,    218,  -1501,
		 -274,   1728,   1391,  -1379,   -892,   -582,   1248,  -1108,
		-1188,    124,    732,   -251,    -32,   -858,   1626,   1681
	}
};

/*
 * The same quartic folding constants, repacked in physical row-bitrev block
 * order.
 *
 * Forward NTT output is not GT-natural: physical block j stores logical index
 * gt96_rowbitrev_logical_index(j).  For C reference loops and future ASM table
 * packing, this table makes the basemul/baseinv zeta lookup match memory order:
 *
 *   gt_rowbitrev_lambda[branch][physical_j]
 *     = gt_lambda[branch][gt96_rowbitrev_logical_index(physical_j)]
 *
 * This table is still a lambda/zeta table for X^4 - lambda.  It is not a
 * butterfly twiddle table.
 */
const int16_t gt_rowbitrev_lambda[2][96] = {
	{
		  1655,   -601,    -31,  -1655,   1473,     31,    183,  -1473,
		 -1364,   -183,   1130,   1364,  -1674,  -1130,   1209,   1674,
		 -1583,  -1209,   -559,   1583,   -235,    559,    696,    235,
		  -397,   -696,    444,    397,    774,   -444,   1059,   -774,
		  -443,  -1059,   1671,    443,   -223,  -1671,   -943,    223,
		   927,    943,  -1138,   -927,    352,   1138,    514,   -352,
		   242,   -514,   -312,   -242,    512,    312,   1514,   -512,
		   100,  -1514,    489,   -100,    432,   -489,  -1660,   -432,
		 -1212,   1660,  -1640,   1212,  -1250,   1640,    760,   1250,
		   437,   -760,      8,   -437,   1322,     -8,  -1723,  -1322,
		  1341,   1723,    871,  -1341,   -277,   -871,   1247,    277,
		   297,  -1247,   -933,   -297,  -1206,    933,    601,   1206
	},
	{
		   779,  -1626,    940,   -779,   1391,   -940,   1588,  -1391,
		  -124,  -1588,    417,    124,  -1095,   -417,   1367,   1095,
		 -1401,  -1367,    892,   1401,   1550,   -892,   -251,  -1550,
		  1221,    251,  -1531,  -1221,  -1501,   1531,   -218,   1501,
		   274,    218,   1409,   -274,    294,  -1409,   -400,   -294,
		  -230,    400,   -732,    230,     32,    732,    361,    -32,
		    22,   -361,   1543,    -22,   -582,  -1543,   1709,    582,
		 -1248,  -1709,    673,   1248,   -275,   -673,  -1408,    275,
		 -1053,   1408,   1108,   1053,  -1685,  -1108,  -1188,   1685,
		   354,   1188,    315,   -354,   1063,   -315,  -1728,  -1063,
		  1379,   1728,   1022,  -1379,   -968,  -1022,  -1458,    968,
		    27,   1458,    858,    -27,  -1681,   -858,   1626,   1681
	}
};
/*************************************************
* Name:        montgomery_reduce
*
* Description: Montgomery reduction; given a 32-bit integer a, computes
*              a 16-bit integer congruent to a * R^-1 mod q,
*              where R = 2^16.
*
* Arguments:   - int32_t a: input integer to be reduced;
*                           must lie in {-q*2^15, ..., q*2^15-1}
*
* Returns:     an integer in {-q+1, ..., q-1} congruent to
*              a * R^-1 mod q.
**************************************************/
static inline int16_t montgomery_reduce(int32_t a)
{
	int16_t t;

	t = (int16_t)a * NTRUPLUS_QINV;
	t = (a - (int32_t)t * NTRUPLUS_Q) >> 16;
	return t;
}

/*************************************************
* Name:        barrett_reduce
*
* Description: Barrett reduction; given a 16-bit integer a, computes a
*              centered representative congruent to a mod q in
*              {-(q+1)/2, ..., (q+1)/2}.
*
* Arguments:   - int16_t a: input integer to be reduced
*
* Returns:     integer in {-(q+1)/2, ..., (q+1)/2} congruent to a mod q.
**************************************************/
static inline int16_t barrett_reduce(int16_t a)
{
	int16_t t;
	const int16_t v = ((1<<26) + NTRUPLUS_Q/2) / NTRUPLUS_Q;

	t  = ((int32_t)v*a + (1<<25)) >> 26;
	t *= NTRUPLUS_Q;
	return a - t;
}

/*************************************************
* Name:        fqmul
*
* Description: Multiplication followed by Montgomery reduction.
*
* Arguments:   - int16_t a: first factor
*              - int16_t b: second factor
*
* Returns:     16-bit integer congruent to a*b*R^-1 mod q.
**************************************************/
static inline int16_t fqmul(int16_t a, int16_t b)
{
    return montgomery_reduce((int32_t)a * b);
}

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

static unsigned gt96_output_crt_index(unsigned k3, unsigned k32)
{
	return (32*k3 + 3*k32) % 96;
}

static unsigned gt96_output_crt_k3(unsigned j)
{
	return (2*j) % 3;
}

static unsigned gt96_output_crt_k32(unsigned j)
{
	return (11*j) & 31U;
}

static unsigned NTRUPLUS_UNUSED gt96_rowbitrev_logical_index(unsigned physical_j)
{
	/*
	 * Row-bitrev layout keeps the Good-Thomas output CRT scatter, but the
	 * 32-point row coordinate is stored in bit-reversed order:
	 *
	 *   physical coordinate: (k3, k32_br)
	 *   logical coordinate : (k3, bitreverse5(k32_br))
	 *
	 * Therefore a physical quartic block does not directly use
	 * gt_lambda[branch][physical_j].  Basemul/baseinv must first recover the
	 * logical GT index stored at that physical block.
	 */
	const unsigned k3 = gt96_output_crt_k3(physical_j);
	const unsigned k32_br = gt96_output_crt_k32(physical_j);
	const unsigned k32 = bitreverse5(k32_br);

	return gt96_output_crt_index(k3, k32);
}

static void ntt32_radix2_dif_incomplete(int16_t out[32], const int16_t in[32])
{
	/*
	 * Incomplete forward cyclic 32-point NTT using radix-2
	 * decimation-in-frequency.
	 *
	 * This consumes natural-order input and runs only:
	 *
	 *   len = 32, 16, 8, 4
	 *
	 * The final len=2 DIF butterflies are intentionally skipped.  Therefore
	 * out[] is the pre-final-layer state, not full bit-reversed NTT32 output.
	 * Adjacent pairs (2*m, 2*m+1) still contain the missing two-point layer.
	 * The matching basemul/baseinv helpers operate on those pairs directly.
	 */
	for (unsigned i = 0; i < 32; i++)
	{
		out[i] = barrett_reduce(in[i]);
	}

	for (unsigned len = 32; len >= 4; len >>= 1)
	{
		const int16_t root = gt96_omega32_powers[32 / len];

		for (unsigned start = 0; start < 32; start += len)
		{
			int16_t w = NTRUPLUS_R;

			for (unsigned j = 0; j < len / 2; j++)
			{
				const int16_t u = out[start + j];
				const int16_t v = out[start + j + len / 2];
				const int16_t diff = barrett_reduce(u - v);

				out[start + j] = barrett_reduce(u + v);
				out[start + j + len / 2] = fqmul(diff, w);
				w = fqmul(w, root);
			}
		}
	}
}

static void NTRUPLUS_UNUSED intt32_radix2_bitrevin(int16_t out[32], const int16_t in[32])
{
	/*
	 * Unnormalized inverse cyclic 32-point NTT for the complete bit-reversed
	 * 32-point representation.
	 *
	 * Input is already in bit-reversed frequency order:
	 *   in[bitreverse5(k)] = F[k]
	 *
	 * The increasing-len inverse radix-2 DIT butterflies normally start from
	 * bit-reversed frequency input, so no extra input permutation is needed.
	 * The output is natural-order time-domain data and is scaled by 32.
	 *
	 * This is kept as an oracle for the complete representation.  The
	 * incomplete path uses intt32_radix2_incomplete() instead.
	 */
	for (unsigned i = 0; i < 32; i++)
	{
		out[i] = barrett_reduce(in[i]);
	}

	for (unsigned len = 2; len <= 32; len <<= 1)
	{
		const int16_t root = gt96_omega32_inv_powers[32 / len];

		for (unsigned start = 0; start < 32; start += len)
		{
			int16_t w = NTRUPLUS_R;

			for (unsigned j = 0; j < len / 2; j++)
			{
				const int16_t u = out[start + j];
				const int16_t v = fqmul(out[start + j + len / 2], w);

				out[start + j] = barrett_reduce(u + v);
				out[start + j + len / 2] = barrett_reduce(u - v);
				w = fqmul(w, root);
			}
		}
	}
}

static void intt32_radix2_incomplete(int16_t out[32], const int16_t in[32])
{
	/*
	 * Inverse row kernel for ntt32_radix2_dif_incomplete().
	 *
	 * The skipped forward len=2 layer would map each adjacent pair
	 *   (u, v) -> (u + v, u - v).
	 * The complete inverse DIT kernel would immediately apply the same
	 * two-point butterfly and produce (2u, 2v), then continue with len=4.
	 *
	 * To consume the incomplete representation directly, start the inverse at
	 * len=4 and multiply the final row by 2.  This keeps the row scaling equal
	 * to the complete 32-point inverse:
	 *
	 *   intt32_radix2_incomplete(ntt32_radix2_dif_incomplete(x)) = 32*x.
	 */
	for (unsigned i = 0; i < 32; i++)
	{
		out[i] = barrett_reduce(in[i]);
	}

	for (unsigned len = 4; len <= 32; len <<= 1)
	{
		const int16_t root = gt96_omega32_inv_powers[32 / len];

		for (unsigned start = 0; start < 32; start += len)
		{
			int16_t w = NTRUPLUS_R;

			for (unsigned j = 0; j < len / 2; j++)
			{
				const int16_t u = out[start + j];
				const int16_t v = fqmul(out[start + j + len / 2], w);

				out[start + j] = barrett_reduce(u + v);
				out[start + j + len / 2] = barrett_reduce(u - v);
				w = fqmul(w, root);
			}
		}
	}

	for (unsigned i = 0; i < 32; i++)
	{
		out[i] = barrett_reduce(out[i] + out[i]);
	}
}

static void dft3_forward(int16_t *a0, int16_t *a1, int16_t *a2)
{
	const int16_t x0 = *a0;
	const int16_t x1 = *a1;
	const int16_t x2 = *a2;
	const int16_t d = barrett_reduce(x1 - x2);
	const int16_t t = fqmul(d, GT96_OMEGA3);
	const int16_t y0 = barrett_reduce(x0 + x1 + x2);

	/*
	 * Since 1 + omega3 + omega3^2 = 0:
	 *   y1 = x0 + omega3*x1 + omega3^2*x2
	 *      = x0 - x2 + omega3*(x1 - x2)
	 *   y2 = x0 + omega3^2*x1 + omega3*x2
	 *      = x0 - x1 - omega3*(x1 - x2)
	 *
	 * This keeps the same unnormalized 3-point DFT while using one
	 * Montgomery multiplication per lane instead of four.
	 */
	const int16_t y1 = barrett_reduce(x0 - x2 + t);
	const int16_t y2 = barrett_reduce(x0 - x1 - t);

	*a0 = y0;
	*a1 = y1;
	*a2 = y2;
}

static void ntt96_goodthomas_core(int16_t mat[3][32])
{
	/*
	 * The 96-point transform separates into a 3-point transform on the
	 * n3 dimension and a 32-point transform on the n32 dimension:
	 *
	 *   omega96^((64*n3 + 33*n32) * (32*k3 + 3*k32))
	 *     = omega96^(32*n3*k3) * omega96^(3*n32*k32).
	 *
	 * These two dimensions commute.  Do the 3-point DFT first so the
	 * reference follows the schedule intended for the AArch64 path.
	 */
	for (int n32 = 0; n32 < 32; n32++)
	{
		dft3_forward(&mat[0][n32], &mat[1][n32], &mat[2][n32]);
	}

	for (int k3 = 0; k3 < 3; k3++)
	{
		int16_t row[32];

		ntt32_radix2_dif_incomplete(row, mat[k3]);

		for (int k32 = 0; k32 < 32; k32++)
		{
			/*
			 * Keep the local 32-point row in the incomplete DIF state.
			 * Unlike the previous complete row-bitrev path, this is not
			 * a finished point-value NTT row:
			 *
			 *   stages done    : len=32,16,8,4
			 *   stage skipped  : len=2
			 *
			 * The adjacent k32 pairs still contain one unresolved radix-2
			 * layer.  The matching incomplete basemul/baseinv helpers
			 * operate on those pairs, and the inverse row kernel consumes
			 * this state directly.
			 */
			mat[k3][k32] = row[k32];
		}
	}
}

static void ntt96_goodthomas(int16_t out[96], const int16_t in[96])
{
	int16_t mat[3][32];

	for (int n3 = 0; n3 < 3; n3++)
	{
		for (int n32 = 0; n32 < 32; n32++)
		{
			const int n = (64*n3 + 33*n32) % 96;
			mat[n3][n32] = in[n];
		}
	}

	ntt96_goodthomas_core(mat);

	for (int k3 = 0; k3 < 3; k3++)
	{
		for (int k32 = 0; k32 < 32; k32++)
		{
			const int k = gt96_output_crt_index((unsigned)k3, (unsigned)k32);
			out[k] = mat[k3][k32];
		}
	}
}

static void dft3_inverse(int16_t *a0, int16_t *a1, int16_t *a2)
{
	const int16_t y0 = *a0;
	const int16_t y1 = *a1;
	const int16_t y2 = *a2;
	const int16_t d = barrett_reduce(y2 - y1);
	const int16_t t = fqmul(d, GT96_OMEGA3);
	const int16_t x0 = barrett_reduce(y0 + y1 + y2);

	/*
	 * Inverse 3-point DFT is also unnormalized.  Using omega3^2=-1-omega3:
	 *   x1 = y0 + omega3^2*y1 + omega3*y2
	 *      = y0 - y1 + omega3*(y2 - y1)
	 *   x2 = y0 + omega3*y1 + omega3^2*y2
	 *      = y0 - y2 - omega3*(y2 - y1)
	 */
	const int16_t x1 = barrett_reduce(y0 - y1 + t);
	const int16_t x2 = barrett_reduce(y0 - y2 - t);

	*a0 = x0;
	*a1 = x1;
	*a2 = x2;
}

static void invntt96_goodthomas(int16_t out[96], const int16_t in[96])
{
	int16_t mat[3][32];

	for (int k3 = 0; k3 < 3; k3++)
	{
		for (int k32 = 0; k32 < 32; k32++)
		{
			const int k = gt96_output_crt_index((unsigned)k3, (unsigned)k32);
			mat[k3][k32] = in[k];
		}
	}

	for (int k32 = 0; k32 < 32; k32++)
	{
		dft3_inverse(&mat[0][k32], &mat[1][k32], &mat[2][k32]);
	}

	for (int n3 = 0; n3 < 3; n3++)
	{
		int16_t row[32];

		/* Consume the incomplete pre-len2 row directly. */
		intt32_radix2_incomplete(row, mat[n3]);

		for (int n32 = 0; n32 < 32; n32++)
		{
			mat[n3][n32] = row[n32];
		}
	}

	for (int n3 = 0; n3 < 3; n3++)
	{
		for (int n32 = 0; n32 < 32; n32++)
		{
			const int n = (64*n3 + 33*n32) % 96;
			out[n] = mat[n3][n32];
		}
	}
}

/*************************************************
* Name:        fqinv
*
* Description: Computes the multiplicative inverse of a value in the
*              finite field Z_q.
*
* Arguments:   - int16_t a: input value a mod q
*
* Returns:     16-bit integer congruent to a^{-1} mod q.
**************************************************/
static inline int16_t fqinv(int16_t a)
{
	int16_t t1, t2, t3;

	t1 = fqmul(a, a);    // 10
	t2 = fqmul(t1, t1);  // 100
	t2 = fqmul(t2, t2);  // 1000
	t3 = fqmul(t2, t2);  // 10000

	t1 = fqmul(t1, t2);  // 1010

	t2 = fqmul(t1, t3);  // 11010
	t2 = fqmul(t2, t2);  // 110100
	t2 = fqmul(t2, a);   // 110101

	t1 = fqmul(t1, t2);  // 111111

	t2 = fqmul(t2, t2);  // 1101010
	t2 = fqmul(t2, t2);  // 11010100
	t2 = fqmul(t2, t2);  // 110101000
	t2 = fqmul(t2, t2);  // 1101010000
	t2 = fqmul(t2, t2);  // 11010100000
	t2 = fqmul(t2, t2);  // 110101000000
	t2 = fqmul(t2, t1);  // 110101111111

	t2 = fqmul(NTRUPLUS_RINV, t2);

	return t2;
}

/*************************************************
* Name:        ntt_gt_rowbitrevlayout
*
* Description: Number-theoretic transform (NTT) in R_q using the
*              Good-Thomas row-bitrev block-major layout.  Physical block
*              j stores the logical 96-point Good-Thomas output recovered by
*              gt96_rowbitrev_logical_index(j), and each block represents an
*              element of Zq[X]/(X^4 - gt_lambda[branch][logical_j]).
*
* Arguments:   - int16_t r[NTRUPLUS_N]: pointer to output vector in
*                                       GT row-bitrev NTT representation
*              - const int16_t a[NTRUPLUS_N]: pointer to input vector of
*                                            coefficients of a in R_q
*
* Returns:     none.
**************************************************/
void ntt_gt_rowbitrevlayout(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N])
{
	int16_t t1;

	/* Step 1: split the 768-coefficient polynomial into two 384-coefficient
	 * branches.
	 */
	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		t1 = fqmul(NTRUPLUS_ZETA_TOP_SPLIT, a[i + NTRUPLUS_N / 2]);

		r[i + NTRUPLUS_N / 2] = a[i] + a[i + NTRUPLUS_N / 2] - t1;
		r[i                 ] = a[i]                         + t1;
	}

	/*
	 * Good-Thomas reference path for the verified twisted formulation.
	 * Each branch is twisted into a cyclic length-96 problem on four
	 * stride-4 streams, transformed through an explicit in[96]/out[96]
	 * 96-point kernel, then stored in row-bitrev block-major layout.
	 */
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int16_t *twist = branch == 0 ? twist_branch0 : twist_branch1;

		/* Step 2: twist each branch by F_b^{-k}.  After this twist, each
		 * stride-4 lane becomes a cyclic 96-point NTT problem.
		 */
		for (int i = 0; i < 96; i++)
		{
			for (int j = 0; j < 4; j++)
			{
				r[branch_start + 4*i + j] =
					fqmul(r[branch_start + 4*i + j], twist[i]);
			}
		}

		/* Step 3: run the Good-Thomas 96-point NTT independently on the
		 * four lanes A_0(y), A_1(y), A_2(y), A_3(y), where y = x^4.
		 */
		for (int lane = 0; lane < 4; lane++)
		{
			int16_t in[96];
			int16_t out[96];

			/* Gather one stride-4 lane into a contiguous input for the
			 * 96-point Good-Thomas kernel.  This is intentionally
			 * explicit so the future assembly routine has a simple
			 * in/out reference boundary.
			 */
			for (int i = 0; i < 96; i++)
			{
				in[i] = r[branch_start + 4*i + lane];
			}

			ntt96_goodthomas(out, in);

			/*
			 * Row-bitrev layout:
			 * out[j] is already the value for physical block j; the
			 * logical GT index stored there is
			 * gt96_rowbitrev_logical_index(j).  The output remains
			 * block-major: block j is four consecutive lanes at
			 * branch_start + 4*j.
			 */
			for (int j = 0; j < 96; j++)
			{
				r[branch_start + 4*j + lane] = out[j];
			}
		}
	}
}

void ntt(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N])
{
	ntt_gt_rowbitrevlayout(r, a);
}

/*************************************************
* Name:        invntt_gt_rowbitrevlayout
*
 * Description: Inverse for the incomplete row-bitrev NTT-domain layout.
 *              Each 32-point row is stored before the final len=2 DIF layer.
 *              The inverse row kernel consumes that representation directly,
 *              starts at inverse len=4, and restores the same 96x branch
 *              scaling as the complete inverse path.
*
* Arguments:   - int16_t r[NTRUPLUS_N]: pointer to output vector
*              - const int16_t a[NTRUPLUS_N]: pointer to input vector in
*                                            GT row-bitrev NTT layout
*
* Returns:     none.
**************************************************/
void invntt_gt_rowbitrevlayout(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N])
{
	int16_t branches[NTRUPLUS_N];
	int16_t t1, t2;

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int16_t *untwist = branch == 0 ? untwist_branch0 : untwist_branch1;

		for (int lane = 0; lane < 4; lane++)
		{
			int16_t rowbitrev_freq[96];
			int16_t coeffs[96];

			/*
			 * Incomplete row-bitrev frequency layout: physical block j
			 * is gathered directly.  This is not GT-natural order, and
			 * adjacent k32 pairs still represent the state before the
			 * skipped len=2 layer.
			 */
			for (int j = 0; j < 96; j++)
			{
				rowbitrev_freq[j] = a[branch_start + 4*j + lane];
			}

			/* The inverse is intentionally unnormalized.  Its output is
			 * 96 times the twisted branch coefficients.
			 */
			invntt96_goodthomas(coeffs, rowbitrev_freq);

			/* Forward used F_b^{-k}; multiply by F_b^k to untwist. */
			for (int i = 0; i < 96; i++)
			{
				branches[branch_start + 4*i + lane] =
					fqmul(coeffs[i], untwist[i]);
			}
		}
	}

	/* Merge the two 384-coefficient branches.  At this point each branch is
	 * scaled by 96, so the original final constants NINV=1/192 and
	 * 2NINV=1/96 recover the coefficient representation.
	 */
	for (int i = 0; i < NTRUPLUS_N/2; i++)
	{
		t1 = branches[i] + branches[i + NTRUPLUS_N/2];
		t2 = fqmul(NTRUPLUS_ZMINUSZ5INV, branches[i] - branches[i + NTRUPLUS_N/2]);

		r[i               ] = fqmul(NTRUPLUS_NINV, t1 - t2);
		r[i + NTRUPLUS_N/2] = fqmul(NTRUPLUS_2NINV, t2);
	}
}

void invntt(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N])
{
	invntt_gt_rowbitrevlayout(r, a);
}

/*************************************************
* Name:        baseinv
*
* Description: Inversion of a polynomial in Zq[X]/(X^4 - zeta), used as
*              a building block for inversion of elements in R_q in the
*              NTT domain.
*
* Arguments:   - int16_t r[4]:        pointer to the output polynomial
*              - const int16_t a[4]:  pointer to the input polynomial
*              - const int16_t zeta:  parameter defining X^4 - zeta
*
* Returns:     0 if a is invertible, 1 otherwise.
**************************************************/
int baseinv(int16_t r[4], const int16_t a[4], const int16_t zeta)
{
	int16_t t0, t1, t2, t3;

	t0 = montgomery_reduce(a[2]*a[2] - 2*a[1]*a[3]);            // R^-1
	t1 = montgomery_reduce(a[3]*a[3]);                          // R^-1
	t0 = montgomery_reduce(a[0]*a[0] + t0*zeta);                // R^-1
	t1 = montgomery_reduce(a[1]*a[1] + t1*zeta - 2*a[0]*a[2]);  // R^-1
	t2 = montgomery_reduce(t1*zeta);                            // R^-1

	t3 = montgomery_reduce(t0*t0 - t1*t2);  // R^-3

	if (t3 == 0) return 1;

	r[0] = montgomery_reduce(a[0]*t0 + a[2]*t2); // R^-2
	r[1] = montgomery_reduce(a[3]*t2 + a[1]*t0); // R^-2
	r[2] = montgomery_reduce(a[2]*t0 + a[0]*t1); // R^-2
	r[3] = montgomery_reduce(a[1]*t1 + a[3]*t0); // R^-2

	t3 = fqinv(t3); // R^5

	r[0] =  montgomery_reduce(r[0]*t3); // R^0
	r[1] = -montgomery_reduce(r[1]*t3); // R^0
	r[2] =  montgomery_reduce(r[2]*t3); // R^0
	r[3] = -montgomery_reduce(r[3]*t3); // R^0

	return 0;
}

/*************************************************
* Name:        basemul
*
* Description: Multiplication of polynomials in Zq[X]/(X^4 - zeta),
*              used for multiplication of elements in R_q in the NTT domain.
*
* Arguments:   - int16_t r[4]:        pointer to the output polynomial
*              - const int16_t a[4]:  pointer to the first factor
*              - const int16_t b[4]:  pointer to the second factor
*              - const int16_t zeta:  parameter defining X^4 - zeta
*
* Returns:     none.
**************************************************/
void basemul(int16_t r[4], const int16_t a[4], const int16_t b[4], const int16_t zeta)
{
	r[0] = montgomery_reduce(a[1]*b[3]+a[2]*b[2]+a[3]*b[1]); // R^-1
	r[1] = montgomery_reduce(a[2]*b[3]+a[3]*b[2]);           // R^-1
	r[2] = montgomery_reduce(a[3]*b[3]);                     // R^-1

	r[0] = montgomery_reduce(r[0]*zeta+a[0]*b[0]);  				   // R^-1
	r[1] = montgomery_reduce(r[1]*zeta+a[0]*b[1]+a[1]*b[0]); 		   // R^-1
	r[2] = montgomery_reduce(r[2]*zeta+a[0]*b[2]+a[1]*b[1]+a[2]*b[0]); // R^-1
	r[3] = montgomery_reduce(a[0]*b[3]+a[1]*b[2]+a[2]*b[1]+a[3]*b[0]); // R^-1

	r[0] = montgomery_reduce(r[0]*NTRUPLUS_RSQ); // R^0
	r[1] = montgomery_reduce(r[1]*NTRUPLUS_RSQ); // R^0
	r[2] = montgomery_reduce(r[2]*NTRUPLUS_RSQ); // R^0
	r[3] = montgomery_reduce(r[3]*NTRUPLUS_RSQ); // R^0
}

/*************************************************
* Name:        basemul_add
*
* Description: Multiplication then addition of polynomials in
*              Zq[X]/(X^4 - zeta), used for multiplication of
*              elements in R_q in the NTT domain.
*
* Arguments:   - int16_t r[4]:        pointer to the output polynomial
*              - const int16_t a[4]:  pointer to the first factor
*              - const int16_t b[4]:  pointer to the second factor
*              - const int16_t c[4]:  pointer to the third factor
*              - const int16_t zeta:  parameter defining X^4 - zeta
*
* Returns:     none.
**************************************************/
void basemul_add(int16_t r[4], const int16_t a[4], const int16_t b[4], const int16_t c[4], const int16_t zeta)
{
	r[0] = montgomery_reduce(a[1]*b[3]+a[2]*b[2]+a[3]*b[1]); // R^-1
	r[1] = montgomery_reduce(a[2]*b[3]+a[3]*b[2]);           // R^-1
	r[2] = montgomery_reduce(a[3]*b[3]);                     // R^-1

	r[0] = montgomery_reduce(r[0]*zeta+a[0]*b[0]);  				   // R^-1
	r[1] = montgomery_reduce(r[1]*zeta+a[0]*b[1]+a[1]*b[0]); 		   // R^-1
	r[2] = montgomery_reduce(r[2]*zeta+a[0]*b[2]+a[1]*b[1]+a[2]*b[0]); // R^-1
	r[3] = montgomery_reduce(a[0]*b[3]+a[1]*b[2]+a[2]*b[1]+a[3]*b[0]); // R^-1

	r[0] = montgomery_reduce(c[0]*NTRUPLUS_R + r[0]*NTRUPLUS_RSQ); // R^0
	r[1] = montgomery_reduce(c[1]*NTRUPLUS_R + r[1]*NTRUPLUS_RSQ); // R^0
	r[2] = montgomery_reduce(c[2]*NTRUPLUS_R + r[2]*NTRUPLUS_RSQ); // R^0
	r[3] = montgomery_reduce(c[3]*NTRUPLUS_R + r[3]*NTRUPLUS_RSQ); // R^0
}

static void incomplete_pair_complete(int16_t plus[4], int16_t minus[4],
                                     const int16_t lo[4], const int16_t hi[4])
{
	/*
	 * Complete the skipped len=2 DIF layer for one adjacent k32 pair:
	 *
	 *   plus  = lo + hi
	 *   minus = lo - hi
	 *
	 * plus/minus are the two complete point-value quartic blocks that would
	 * have been produced by a full row-bitrev NTT32.
	 */
	for (int lane = 0; lane < 4; lane++)
	{
		plus[lane] = barrett_reduce(lo[lane] + hi[lane]);
		minus[lane] = barrett_reduce(lo[lane] - hi[lane]);
	}
}

static void incomplete_pair_uncomplete(int16_t lo[4], int16_t hi[4],
                                       const int16_t plus[4],
                                       const int16_t minus[4])
{
	/*
	 * Inverse of the skipped len=2 layer:
	 *
	 *   lo = (plus + minus) / 2
	 *   hi = (plus - minus) / 2
	 *
	 * NTRUPLUS_HALF is 1/2 in Montgomery form, so fqmul() performs the
	 * division by 2 modulo q.
	 */
	for (int lane = 0; lane < 4; lane++)
	{
		lo[lane] = fqmul(barrett_reduce(plus[lane] + minus[lane]),
		                 NTRUPLUS_HALF);
		hi[lane] = fqmul(barrett_reduce(plus[lane] - minus[lane]),
		                 NTRUPLUS_HALF);
	}
}

void basemul_incomplete_pair(int16_t r_lo[4], int16_t r_hi[4],
                             const int16_t a_lo[4], const int16_t a_hi[4],
                             const int16_t b_lo[4], const int16_t b_hi[4],
                             const int16_t zeta_lo,
                             const int16_t zeta_hi)
{
	int16_t a_plus[4], a_minus[4];
	int16_t b_plus[4], b_minus[4];
	int16_t r_plus[4], r_minus[4];

	incomplete_pair_complete(a_plus, a_minus, a_lo, a_hi);
	incomplete_pair_complete(b_plus, b_minus, b_lo, b_hi);

	basemul(r_plus, a_plus, b_plus, zeta_lo);
	basemul(r_minus, a_minus, b_minus, zeta_hi);

	incomplete_pair_uncomplete(r_lo, r_hi, r_plus, r_minus);
}

void basemul_add_incomplete_pair(int16_t r_lo[4], int16_t r_hi[4],
                                 const int16_t a_lo[4], const int16_t a_hi[4],
                                 const int16_t b_lo[4], const int16_t b_hi[4],
                                 const int16_t c_lo[4], const int16_t c_hi[4],
                                 const int16_t zeta_lo,
                                 const int16_t zeta_hi)
{
	int16_t product_lo[4];
	int16_t product_hi[4];

	basemul_incomplete_pair(product_lo, product_hi,
	                        a_lo, a_hi,
	                        b_lo, b_hi,
	                        zeta_lo, zeta_hi);

	for (int lane = 0; lane < 4; lane++)
	{
		r_lo[lane] = barrett_reduce(product_lo[lane] + c_lo[lane]);
		r_hi[lane] = barrett_reduce(product_hi[lane] + c_hi[lane]);
	}
}

int baseinv_incomplete_pair(int16_t r_lo[4], int16_t r_hi[4],
                            const int16_t a_lo[4], const int16_t a_hi[4],
                            const int16_t zeta_lo,
                            const int16_t zeta_hi)
{
	int16_t a_plus[4], a_minus[4];
	int16_t inv_plus[4], inv_minus[4];

	incomplete_pair_complete(a_plus, a_minus, a_lo, a_hi);

	if (baseinv(inv_plus, a_plus, zeta_lo))
	{
		return 1;
	}
	if (baseinv(inv_minus, a_minus, zeta_hi))
	{
		return 1;
	}

	incomplete_pair_uncomplete(r_lo, r_hi, inv_plus, inv_minus);
	return 0;
}

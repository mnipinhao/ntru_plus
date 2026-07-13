#include <stdint.h>
#include "params.h"
#include "ntt.h"

#define NTRUPLUS_R            -147 // R = 2^16 mod q
#define NTRUPLUS_RINV         -682 // (R)^(-1) mod q
#define NTRUPLUS_RSQ           867 // (R^2) mod q
#define NTRUPLUS_QINV        12929 // (q)^(-1) mod (2^16)

#define NTRUPLUS_OMEGA        -886 // (omega * R) mod q
#define NTRUPLUS_ZMINUSZ5INV -1665 // (z - z^5)^(-1) * R mod q
                                   // where z = zeta^((n/d)/6)

#define GT96_OMEGA3     NTRUPLUS_OMEGA // (omega96^32 * R) mod q
#define GT96_OMEGA3_SQ        1033 // (omega96^64 * R) mod q

#define NTRUPLUS_NINV         -811 // (n/d)^(-1) * R mod q
#define NTRUPLUS_2NINV       -1622 // 2 * (n/d)^(-1) * R mod q

// zetas: Montgomery-form twiddle factors
const int16_t zetas[192] = {
	 -147, -1033,  -682,  -248,  -708,   682,     1,  -722,
	 -723,  -257, -1124,  -867,  -256,  1484,  1262, -1590,
	 1611,   222,  1164, -1346,  1716, -1521,  -357,   395,
	 -455,   639,   502,   655,  -699,   541,    95, -1577,
	-1241,   550,   -44,    39,  -820,  -216,  -121,  -757,
	 -348,   937,   893,   387,  -603,  1713, -1105,  1058,
	 1449,   837,   901,  1637,  -569, -1617, -1530,  1199,
	   50,  -830,  -625,     4,   176,  -156,  1257, -1507,
	 -380,  -606,  1293,   661,  1428, -1580,  -565,  -992,
	  548,  -800,    64,  -371,   961,   641,    87,   630,
	  675,  -834,   205,    54, -1081,  1351,  1413, -1331,
	-1673, -1267, -1558,   281, -1464,  -588,  1015,   436,
	  223,  1138, -1059,  -397,  -183,  1655,   559, -1674,
	  277,   933,  1723,   437, -1514,   242,  1640,   432,
	-1583,   696,   774,  1671,   927,   514,   512,   489,
	  297,   601,  1473,  1130,  1322,   871,   760,  1212,
	 -312,  -352,   443,   943,     8,  1250,  -100,  1660,
	  -31,  1206, -1341, -1247,   444,   235,  1364, -1209,
	  361,   230,   673,   582,  1409,  1501,  1401,   251,
	 1022, -1063,  1053,  1188,   417, -1391,   -27, -1626,
	 1685,  -315,  1408, -1248,   400,   274, -1543,    32,
	-1550,  1531, -1367,  -124,  1458,  1379,  -940, -1681,
	   22,  1709,  -275,  1108,   354, -1728,  -968,   858,
	 1221,  -218,   294,  -732, -1095,   892,  1588,  -779
};

/*
 * Branch twist tables in Montgomery form.
 *
 * After the first split, branch b is r[b*384 .. b*384+383].  For each
 * branch polynomial A_b(y) = sum_k a_{4k+r} y^k, the inverse twist uses
 * a_{4k+r} -> a_{4k+r} * F_b^{-k}.  The matching reference evaluation is
 * at alpha = F_b * lambda, since
 *
 *   sum_k a_k F_b^{-k} alpha^k = A_b(alpha / F_b).
 *
 * The factors are chosen so alpha^96 = 1 for the 96-point cyclic NTT:
 *   branch 0: F_0 = 2
 *   branch 1: F_1 = 22
 */
static const int16_t tw_branch0_inv[96] = {
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
static const int16_t tw_branch1_inv[96] = {
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
static const int16_t tw_branch0[96] = {
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
static const int16_t tw_branch1[96] = {
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

static const uint8_t gt96_branch_exponents[2][96] = {
	{
		66, 18, 90, 42, 78, 30,  6, 54, 72, 24,  0, 48, 84, 36, 12, 60,
		69, 21, 93, 45, 81, 33,  9, 57, 75, 27,  3, 51, 87, 39, 15, 63,
		67, 19, 91, 43, 79, 31,  7, 55, 73, 25,  1, 49, 85, 37, 13, 61,
		70, 22, 94, 46, 82, 34, 10, 58, 76, 28,  4, 52, 88, 40, 16, 64,
		68, 20, 92, 44, 80, 32,  8, 56, 74, 26,  2, 50, 86, 38, 14, 62,
		71, 23, 95, 47, 83, 35, 11, 59, 77, 29,  5, 53, 89, 41, 17, 65,
	},
	{
		 1, 49, 25, 73, 13, 61, 37, 85,  7, 55, 31, 79, 19, 67, 43, 91,
		 4, 52, 28, 76, 16, 64, 40, 88, 10, 58, 34, 82, 22, 70, 46, 94,
		 2, 50, 26, 74, 14, 62, 38, 86,  8, 56, 32, 80, 20, 68, 44, 92,
		 5, 53, 29, 77, 17, 65, 41, 89, 11, 59, 35, 83, 23, 71, 47, 95,
		 3, 51, 27, 75, 15, 63, 39, 87,  9, 57, 33, 81, 21, 69, 45, 93,
		 6, 54, 30, 78, 18, 66, 42, 90, 12, 60, 36, 84, 24, 72, 48,  0,
	},
};

/*
 * GT-natural quartic folding constants in centered signed Montgomery form.
 *
 * In GT-natural layout, physical block j stores logical Good-Thomas output
 * j.  The quartic block is interpreted in Z_q[X] / (X^4 - lambda_j), where
 *   branch 0: lambda_j = omega96^j / 2
 *   branch 1: lambda_j = omega96^j / 22
 * and omega96 = 675.  These constants are not butterfly twiddles; they are
 * the per-block zeta values passed to basemul()/baseinv().
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

static void ntt32_radix2(int16_t out[32], const int16_t in[32])
{
	for (unsigned i = 0; i < 32; i++)
	{
		out[bitreverse5(i)] = barrett_reduce(in[i]);
	}

	for (unsigned len = 2; len <= 32; len <<= 1)
	{
		const int16_t root = gt96_omega32_powers[32 / len];

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

static void intt32_radix2(int16_t out[32], const int16_t in[32])
{
	/*
	 * Unnormalized inverse cyclic 32-point NTT with the same radix-2 shape
	 * as ntt32_radix2().  The root is omega32^{-1}, where
	 * omega32 = omega96^3.  Because this is unnormalized,
	 * intt32_radix2(ntt32_radix2(x)) = 32*x.
	 */
	for (unsigned i = 0; i < 32; i++)
	{
		out[bitreverse5(i)] = barrett_reduce(in[i]);
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

static void dft3_forward(int16_t *a0, int16_t *a1, int16_t *a2)
{
	const int16_t x0 = *a0;
	const int16_t x1 = *a1;
	const int16_t x2 = *a2;
	const int16_t y0 = barrett_reduce(x0 + x1 + x2);
	const int16_t y1 = barrett_reduce(x0 +
	                                  fqmul(x1, GT96_OMEGA3) +
	                                  fqmul(x2, GT96_OMEGA3_SQ));
	const int16_t y2 = barrett_reduce(x0 +
	                                  fqmul(x1, GT96_OMEGA3_SQ) +
	                                  fqmul(x2, GT96_OMEGA3));

	*a0 = y0;
	*a1 = y1;
	*a2 = y2;
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

	for (int n3 = 0; n3 < 3; n3++)
	{
		int16_t row[32];

		ntt32_radix2(row, mat[n3]);

		for (int k32 = 0; k32 < 32; k32++)
		{
			mat[n3][k32] = row[k32];
		}
	}

	for (int k32 = 0; k32 < 32; k32++)
	{
		dft3_forward(&mat[0][k32], &mat[1][k32], &mat[2][k32]);
	}

	for (int k3 = 0; k3 < 3; k3++)
	{
		for (int k32 = 0; k32 < 32; k32++)
		{
			const int k = (32*k3 + 3*k32) % 96;
			out[k] = mat[k3][k32];
		}
	}
}

#ifdef NTRUPLUS_NTT_REFERENCE_TEST
static void intt32_slow(int16_t out[32], const int16_t in[32])
{
	for (int n = 0; n < 32; n++)
	{
		int16_t acc = 0;

		for (int k = 0; k < 32; k++)
		{
			const int e = (n * k) & 31;
			const int inv_e = (32 - e) & 31;

			acc = barrett_reduce(acc +
			                     fqmul(in[k], gt96_omega32_powers[inv_e]));
		}

		out[n] = acc;
	}
}
#endif

static void dft3_inverse(int16_t *a0, int16_t *a1, int16_t *a2)
{
	const int16_t y0 = *a0;
	const int16_t y1 = *a1;
	const int16_t y2 = *a2;
	const int16_t x0 = barrett_reduce(y0 + y1 + y2);
	const int16_t x1 = barrett_reduce(y0 +
	                                  fqmul(y1, GT96_OMEGA3_SQ) +
	                                  fqmul(y2, GT96_OMEGA3));
	const int16_t x2 = barrett_reduce(y0 +
	                                  fqmul(y1, GT96_OMEGA3) +
	                                  fqmul(y2, GT96_OMEGA3_SQ));

	*a0 = x0;
	*a1 = x1;
	*a2 = x2;
}

#ifdef NTRUPLUS_NTT_REFERENCE_TEST
static void invntt96_goodthomas_slow(int16_t out[96], const int16_t in[96])
{
	int16_t mat[3][32];

	for (int k3 = 0; k3 < 3; k3++)
	{
		for (int k32 = 0; k32 < 32; k32++)
		{
			const int k = (32*k3 + 3*k32) % 96;
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

		intt32_slow(row, mat[n3]);

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
#endif

static void invntt96_goodthomas(int16_t out[96], const int16_t in[96])
{
	int16_t mat[3][32];

	for (int k3 = 0; k3 < 3; k3++)
	{
		for (int k32 = 0; k32 < 32; k32++)
		{
			const int k = (32*k3 + 3*k32) % 96;
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

		intt32_radix2(row, mat[n3]);

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
* Name:        ntt_gt_layout
*
* Description: Number-theoretic transform (NTT) in R_q. Transforms the
*              coefficient representation of a into a representation
*              where each block of 4 coefficients corresponds to an
*              element of Zq[X]/(X^4 - zeta_i).
*
* Arguments:   - int16_t r[NTRUPLUS_N]: pointer to output vector; NTT
*                                       representation of a in the
*                                       product ring Zq[X]/(X^4 - zeta_i)
*              - const int16_t a[NTRUPLUS_N]: pointer to input vector of
*                                            coefficients of a in R_q
*
* Returns:     none.
**************************************************/
static void ntt_gt_layout(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N],
                          int natural_layout)
{
	int16_t t1;
	int16_t zeta1;

	zeta1 = zetas[1];

	/* Step 1: split the 768-coefficient polynomial into two 384-coefficient
	 * branches.  This is the same top-level split used by the original NTT.
	 */
	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		t1 = fqmul(zeta1, a[i + NTRUPLUS_N / 2]);

		r[i + NTRUPLUS_N / 2] = a[i] + a[i + NTRUPLUS_N / 2] - t1;
		r[i                 ] = a[i]                         + t1;
	}

	/*
	 * Good-Thomas reference path for the verified twisted formulation:
	 * each branch is twisted into a cyclic length-96 problem on four
	 * stride-4 streams, transformed, then stored in the block-major layout
	 * selected by the caller.
	 */
	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int16_t *tw_inv = branch == 0 ? tw_branch0_inv : tw_branch1_inv;
		const uint8_t *exponents = gt96_branch_exponents[branch];

		/* Step 2: twist each branch by F_b^{-k}.  After this twist, each
		 * stride-4 lane becomes a cyclic 96-point NTT problem.
		 */
		for (int i = 0; i < 96; i++)
		{
			for (int j = 0; j < 4; j++)
			{
				r[branch_start + 4*i + j] = fqmul(r[branch_start + 4*i + j], tw_inv[i]);
			}
		}

		/* Step 3: run the Good-Thomas 96-point NTT independently on the
		 * four lanes A_0(y), A_1(y), A_2(y), A_3(y), where y = x^4.
		 */
		for (int lane = 0; lane < 4; lane++)
		{
			int16_t in[96];
			int16_t out[96];

			/* Gather one stride-4 lane into a contiguous 96-coefficient
			 * input for ntt96_goodthomas().
			 */
			for (int i = 0; i < 96; i++)
			{
				in[i] = r[branch_start + 4*i + lane];
			}

			ntt96_goodthomas(out, in);

			if (natural_layout)
			{
				/*
				 * GT-natural layout:
				 * physical block j stores logical 96-point
				 * Good-Thomas output out[j].  The output remains
				 * block-major: block j is four consecutive lanes
				 * at branch_start + 4*j.
				 */
				for (int j = 0; j < 96; j++)
				{
					r[branch_start + 4*j + lane] = out[j];
				}
			}
			else
			{
				/* Old-compatible layout:
				 * physical block b stores logical output
				 * out[gt96_branch_exponents[branch][b]].
				 */
				for (int block = 0; block < 96; block++)
				{
					r[branch_start + 4*block + lane] = out[exponents[block]];
				}
			}
		}
	}
}

void ntt_gt_oldlayout(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N])
{
	ntt_gt_layout(r, a, 0);
}

void ntt_gt_naturallayout(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N])
{
	ntt_gt_layout(r, a, 1);
}

void ntt(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N])
{
	ntt_gt_oldlayout(r, a);
}

/*************************************************
* Name:        invntt_oldlayout_reference
*
* Description: Original inverse NTT for the old-compatible NTT-domain block
*              order.  Kept as a reference while the public invntt() uses the
*              GT-natural inverse path.
*
* Arguments:   - int16_t r[NTRUPLUS_N]: pointer to output vector; coefficient
*                                       representation of a in R_q
*              - const int16_t a[NTRUPLUS_N]: pointer to input vector in NTT
*                                            representation in the product
*                                            ring Zq[X]/(X^4 - zeta_i)
*
* Returns:     none.
**************************************************/
void invntt_oldlayout_reference(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N])
{
	int16_t t1, t2, t3;
	int16_t zeta1, zeta2;
	int k = 191;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r[i] = a[i];
	}

	for (int step = 4; step <= 64; step <<= 1)
	{
		for (int start = 0; start < NTRUPLUS_N; start += (step << 1))
		{
			zeta1 = zetas[k--];

			for (int i = start; i < start + step; i++)
			{
				t1 = r[i + step];

				r[i + step] = fqmul(zeta1, t1 - r[i]);
				r[i       ] = barrett_reduce(r[i] + t1);
			}
		}
	}

	for (int start = 0; start < NTRUPLUS_N; start += 384)
	{
		zeta2 = zetas[k--];
		zeta1 = zetas[k--];

		for (int i = start; i < start + 128; i++)
		{
			t1 = fqmul(NTRUPLUS_OMEGA, r[i + 128] - r[i]);
			t2 = fqmul(zeta1, r[i + 256] - r[i]       + t1);
			t3 = fqmul(zeta2, r[i + 256] - r[i + 128] - t1);
			
			r[i      ] = r[i] + r[i + 128] + r[i + 256];
			r[i + 128] = t2;			
			r[i + 256] = t3;
		}
	}

	for (int i = 0; i < NTRUPLUS_N/2; i++)
	{
		t1 = r[i] + r[i + NTRUPLUS_N/2];
		t2 = fqmul(NTRUPLUS_ZMINUSZ5INV, r[i] - r[i + NTRUPLUS_N/2]);

		r[i               ] = fqmul(NTRUPLUS_NINV, t1 - t2);
		r[i + NTRUPLUS_N/2] = fqmul(NTRUPLUS_2NINV, t2);	
	}
}

/*************************************************
* Name:        invntt_gt_oldlayout
*
* Description: Debug/reference inverse for the Good-Thomas forward path while
*              consuming the old-compatible NTT-domain block-major layout.
*              It reverses the ntt_gt_oldlayout() scatter, applies an
*              unnormalized inverse 96-point Good-Thomas transform per lane,
*              untwists each branch, then
*              performs the original two-branch merge.
*
* Arguments:   - int16_t r[NTRUPLUS_N]: pointer to output vector
*              - const int16_t a[NTRUPLUS_N]: pointer to input vector in
*                                            old-compatible NTT layout
*
* Returns:     none.
**************************************************/
void invntt_gt_oldlayout(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N])
{
	int16_t branches[NTRUPLUS_N];
	int16_t t1, t2;

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int16_t *tw = branch == 0 ? tw_branch0 : tw_branch1;
		const uint8_t *exponents = gt96_branch_exponents[branch];

		for (int lane = 0; lane < 4; lane++)
		{
			int16_t natural[96];
			int16_t coeffs[96];

			/* Undo the old-compatible scatter:
			 * physical block -> canonical Good-Thomas logical j.
			 */
			for (int block = 0; block < 96; block++)
			{
				natural[exponents[block]] =
					a[branch_start + 4*block + lane];
			}

			/* The inverse is intentionally unnormalized.  Its output is
			 * 96 times the twisted branch coefficients.
			 */
			invntt96_goodthomas(coeffs, natural);

			/* Forward used F_b^{-k}; multiply by F_b^k to untwist. */
			for (int i = 0; i < 96; i++)
			{
				branches[branch_start + 4*i + lane] =
					fqmul(coeffs[i], tw[i]);
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

/*************************************************
* Name:        invntt_gt_naturallayout
*
* Description: Inverse for the GT-natural NTT-domain layout.  Physical block
*              j is already logical Good-Thomas output j, so the inverse
*              gathers each lane directly and does not undo exponents[].
*
* Arguments:   - int16_t r[NTRUPLUS_N]: pointer to output vector
*              - const int16_t a[NTRUPLUS_N]: pointer to input vector in
*                                            GT-natural NTT layout
*
* Returns:     none.
**************************************************/
void invntt_gt_naturallayout(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N])
{
	int16_t branches[NTRUPLUS_N];
	int16_t t1, t2;

	for (int branch = 0; branch < 2; branch++)
	{
		const int branch_start = branch * (NTRUPLUS_N / 2);
		const int16_t *tw = branch == 0 ? tw_branch0 : tw_branch1;

		for (int lane = 0; lane < 4; lane++)
		{
			int16_t natural[96];
			int16_t coeffs[96];

			/*
			 * GT-natural layout:
			 * physical block j is logical Good-Thomas index j.
			 * Each quartic block remains block-major, so this lane is
			 * gathered from branch_start + 4*j + lane.
			 */
			for (int j = 0; j < 96; j++)
			{
				natural[j] = a[branch_start + 4*j + lane];
			}

			/* The inverse is intentionally unnormalized.  Its output is
			 * 96 times the twisted branch coefficients.
			 */
			invntt96_goodthomas(coeffs, natural);

			/* Forward used F_b^{-k}; multiply by F_b^k to untwist. */
			for (int i = 0; i < 96; i++)
			{
				branches[branch_start + 4*i + lane] =
					fqmul(coeffs[i], tw[i]);
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
	invntt_gt_oldlayout(r, a);
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

/*
 * Candidate A direct-tuple complete NTT-domain basemul.
 *
 * This reuses the production GT ld4/st4 quartic arithmetic, but remaps the
 * public symbols and lambda table.  Define
 * CANDIDATE_A_DIRECT_TUPLE_BASEMUL_USE_OPT to include the promoted
 * Slothy-scheduled base_gt.opt.s body; otherwise the portable macro source
 * base_gt.S is used.  The memory representation is:
 *
 *   index = branch*384 + row*128 + 4*k32 + lane
 *
 * The loop body is therefore still 24 contiguous 64-byte tuple blocks:
 *
 *   2 branches * 3 rows * 4 kblocks = 24
 */

#define poly_basemul candidate_a_direct_tuple_basemul_asm_fast
#define _poly_basemul _candidate_a_direct_tuple_basemul_asm_fast
#define poly_basemul_add candidate_a_direct_tuple_basemul_add_asm_fast
#define _poly_basemul_add _candidate_a_direct_tuple_basemul_add_asm_fast
#define gt_rowbitrev_lambda candidate_a_direct_tuple_lambda

#if defined(CANDIDATE_A_DIRECT_TUPLE_BASEMUL_USE_OPT)
#include "asm/base_gt.opt.s"
#else
#include "asm/base_gt.S"
#endif

	.align 4
	.global candidate_a_direct_tuple_lambda
	.global _candidate_a_direct_tuple_lambda
candidate_a_direct_tuple_lambda:
_candidate_a_direct_tuple_lambda:
	/* branch 0 */
	/* row 0, k32 00..07 */
	.hword   1655,  -1655,    183,   -183,  -1674,   1674,   -559,    559
	/* row 0, k32 08..15 */
	.hword   -397,    397,   1059,  -1059,   -223,    223,  -1138,   1138
	/* row 0, k32 16..23 */
	.hword    242,   -242,   1514,  -1514,    432,   -432,  -1640,   1640
	/* row 0, k32 24..31 */
	.hword    437,   -437,  -1723,   1723,   -277,    277,   -933,    933
	/* row 1, k32 00..07 */
	.hword   -443,    443,   -943,    943,    352,   -352,   -312,    312
	/* row 1, k32 08..15 */
	.hword    100,   -100,  -1660,   1660,  -1250,   1250,      8,     -8
	/* row 1, k32 16..23 */
	.hword   1341,  -1341,   1247,  -1247,  -1206,   1206,    -31,     31
	/* row 1, k32 24..31 */
	.hword  -1364,   1364,   1209,  -1209,   -235,    235,    444,   -444
	/* row 2, k32 00..07 */
	.hword  -1212,   1212,    760,   -760,   1322,  -1322,    871,   -871
	/* row 2, k32 08..15 */
	.hword    297,   -297,    601,   -601,   1473,  -1473,   1130,  -1130
	/* row 2, k32 16..23 */
	.hword  -1583,   1583,    696,   -696,    774,   -774,   1671,  -1671
	/* row 2, k32 24..31 */
	.hword    927,   -927,    514,   -514,    512,   -512,    489,   -489
	/* branch 1 */
	/* row 0, k32 00..07 */
	.hword    779,   -779,   1588,  -1588,  -1095,   1095,    892,   -892
	/* row 0, k32 08..15 */
	.hword   1221,  -1221,   -218,    218,    294,   -294,   -732,    732
	/* row 0, k32 16..23 */
	.hword     22,    -22,   1709,  -1709,   -275,    275,   1108,  -1108
	/* row 0, k32 24..31 */
	.hword    354,   -354,  -1728,   1728,   -968,    968,    858,   -858
	/* row 1, k32 00..07 */
	.hword    274,   -274,   -400,    400,     32,    -32,   1543,  -1543
	/* row 1, k32 08..15 */
	.hword  -1248,   1248,  -1408,   1408,  -1685,   1685,    315,   -315
	/* row 1, k32 16..23 */
	.hword   1379,  -1379,  -1458,   1458,  -1681,   1681,    940,   -940
	/* row 1, k32 24..31 */
	.hword   -124,    124,   1367,  -1367,   1550,  -1550,  -1531,   1531
	/* row 2, k32 00..07 */
	.hword  -1053,   1053,  -1188,   1188,   1063,  -1063,   1022,  -1022
	/* row 2, k32 08..15 */
	.hword     27,    -27,   1626,  -1626,   1391,  -1391,    417,   -417
	/* row 2, k32 16..23 */
	.hword  -1401,   1401,   -251,    251,  -1501,   1501,   1409,  -1409
	/* row 2, k32 24..31 */
	.hword   -230,    230,    361,   -361,   -582,    582,    673,   -673

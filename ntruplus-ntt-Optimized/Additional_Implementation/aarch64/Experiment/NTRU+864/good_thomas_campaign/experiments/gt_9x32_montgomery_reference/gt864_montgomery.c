#include "gt864_montgomery.h"

#include <assert.h>
#include <stddef.h>
#include <stdint.h>

/*
 * This file is the readable Montgomery-aware Good-Thomas reference for
 *
 *   R_q = Z_3457[x] / (x^864 - x^432 + 1).
 *
 * Put y = x^3.  Each input polynomial is written as
 *
 *   A(x) = A_0(y) + x A_1(y) + x^2 A_2(y),
 *
 * where every A_b has 288 coefficients modulo
 *
 *   P(y) = y^288 - y^144 + 1 = Q(y^9),
 *   Q(z) = z^32 - z^16 + 1.
 *
 * Splitting the coefficient index m = s + 9t gives
 *
 *   A_b(y) = sum_{s=0}^8 y^s B_{b,s}(y^9),
 *   B_{b,s}(z) = sum_{t=0}^31 a[3(s+9t)+b] z^t.
 *
 * The reference therefore evaluates 3 * 9 polynomials B_{b,s} at 32
 * public column points, then evaluates the nine residues at nine public row
 * points.  It deliberately uses direct Horner evaluation and an inverse
 * Vandermonde matrix.  Those choices make the mathematics visible; they are
 * not the future optimized 32-point algorithm.
 *
 * Representation contract
 * -----------------------
 * Coefficients remain normal R^0 field representatives.  Only public roots,
 * inverse factors, and Vandermonde coefficients are encoded as c*R mod q.
 * Thus fqmul_public(a, cR) returns ac in the normal R^0 domain.  This matches
 * the scale convention in Reference_Implementation/NTRU+864/ntt.c.
 */

#define GT864_POINTS          (GT864_N / GT864_LEAF_DEGREE)

#define NTRUPLUS_R            -147 /* R = 2^16 mod q */
#define NTRUPLUS_RSQ           867 /* R^2 mod q */
#define NTRUPLUS_QINV        12929 /* q^-1 mod 2^16 */

#define GT864_ETA              1520 /* primitive ninth root */

extern const int16_t zetas[GT864_POINTS];

/*
 * Compile-time Montgomery root tables, analogous to zetas[] in the current
 * scalar NTRU+864 reference.  They are generated from
 *
 *   lambda[column] = 2401^k,  0 <= k < 96 and k mod 6 in {1, 5},
 *   z[column]      = lambda[column]^9,
 *   root[row][col] = lambda[column] * 1520^row,
 *
 * and every entry below is the centered representative of value * R mod q.
 * The row-zero root is lambda itself, so no duplicate lambda table is kept.
 * These Montgomery-form tables avoid rebuilding the public grid and
 * re-encoding its entries on every transform call.
 */
static const int16_t gt864_z_mont[GT864_COLUMNS] = {
      -888,  -1028,    963,  -1548,   -729,    978,    -62,   1392,
      -470,  -1603,   -775,    115,   1039,  -1024,  -1045,   -291,
       888,   1028,   -963,   1548,    729,   -978,     62,  -1392,
       470,   1603,    775,   -115,  -1039,   1024,   1045,    291,
};

static const int16_t gt864_roots_mont[GT864_ROWS][GT864_COLUMNS] = {
    {
          -333,    365,    917,   -403,   -179,   1089,   1230,     -9,
          -553,  -1657,    -24,   -472,   1343,   1061,   1046,  -1323,
          1677,  -1589,    -71,   -244,    372,    402,   1654,   -889,
          1072,   1493,    -66,  -1298,   -628,    325,   1148,    683,
    },
    {
         -1438,   1680,    669,   -671,   1023,   -623,   -637,    148,
          -509,   1513,   1547,   1616,  -1727,  -1699,   -300,   1014,
          1231,   1163,   -753,   -981,  -1508,   -849,    841,    407,
          1193,   1568,    -67,    987,   -428,   -351,   -825,   1060,
    },
    {
          -936,  -1123,    522,   -105,   -690,    258,   -280,    255,
           688,    855,    680,  -1607,  -1177,   -101,    324,   -542,
           883,   1233,   -293,  -1153,   -169,  -1019,   -770,   -163,
         -1565,   1487,  -1587,    -98,   -644,  -1142,    891,    238,
    },
    {
          1564,    798,  -1670,   -578,  -1329,   1519,   -389,    416,
         -1711,   -232,    -43,   1459,   1686,  -1412,   1586,  -1074,
           844,    466,    593,    139,  -1062,   -144,   1523,   1144,
          -384,   -638,    746,   -309,   -549,   -426,   -824,  -1225,
    },
    {
         -1136,   -447,   -962,   -482,  -1192,   -396,   -133,   -311,
         -1056,    -26,    323,  -1714,   1083,    557,   1191,   -776,
           333,   -365,   -917,    403,    179,  -1089,  -1230,      9,
           553,   1657,     24,    472,  -1343,  -1061,  -1046,   1323,
    },
    {
         -1677,   1589,     71,    244,   -372,   -402,  -1654,    889,
         -1072,  -1493,     66,   1298,    628,   -325,  -1148,   -683,
          1438,  -1680,   -669,    671,  -1023,    623,    637,   -148,
           509,  -1513,  -1547,  -1616,   1727,   1699,    300,  -1014,
    },
    {
         -1231,  -1163,    753,    981,   1508,    849,   -841,   -407,
         -1193,  -1568,     67,   -987,    428,    351,    825,  -1060,
           936,   1123,   -522,    105,    690,   -258,    280,   -255,
          -688,   -855,   -680,   1607,   1177,    101,   -324,    542,
    },
    {
          -883,  -1233,    293,   1153,    169,   1019,    770,    163,
          1565,  -1487,   1587,     98,    644,   1142,   -891,   -238,
         -1564,   -798,   1670,    578,   1329,  -1519,    389,   -416,
          1711,    232,     43,  -1459,  -1686,   1412,  -1586,   1074,
    },
    {
          -844,   -466,   -593,   -139,   1062,    144,  -1523,  -1144,
           384,    638,   -746,    309,    549,    426,    824,   1225,
          1136,    447,    962,    482,   1192,    396,    133,    311,
          1056,     26,   -323,   1714,  -1083,   -557,  -1191,    776,
    },
};

/*************************************************
* Name:        canonical
*
* Description: Computes the canonical representative of an integer modulo q.
*
* Arguments:   - int64_t value: input integer
*
* Returns:     an integer in {0, ..., q-1} congruent to value modulo q.
**************************************************/
static int16_t canonical(int64_t value)
{
    value %= GT864_Q;
    if (value < 0)
        value += GT864_Q;
    return (int16_t)value;
}

/*************************************************
* Name:        centered
*
* Description: Computes the centered representative of an integer modulo q.
*
* Arguments:   - int64_t value: input integer
*
* Returns:     an integer in {-1728, ..., 1728} congruent to value modulo q.
**************************************************/
static int16_t centered(int64_t value)
{
    int16_t result = canonical(value);
    if (result > GT864_Q / 2)
        result = (int16_t)(result - GT864_Q);
    return result;
}

/*************************************************
* Name:        montgomery_reduce
*
* Description: Montgomery reduction; computes value * R^-1 modulo q, where
*              R = 2^16.  This is the same reduction relation used by the
*              current NTRU+864 scalar reference.
*
* Arguments:   - int32_t value: input integer; callers keep it inside the
*                               current scalar reduction precondition
*
* Returns:     a bounded normal representative congruent to value * R^-1.
**************************************************/
static int16_t montgomery_reduce(int32_t value)
{
    int16_t quotient = (int16_t)value * NTRUPLUS_QINV;
    return (int16_t)((value - (int32_t)quotient * GT864_Q) >> 16);
}

/*************************************************
* Name:        fqmul_public
*
* Description: Multiplies a normal R^0 value by a public Montgomery-form
*              constant cR and returns the normal R^0 product ac.
*
* Arguments:   - int16_t value:             normal R^0 field representative
*              - int16_t public_montgomery: public constant cR modulo q
*
* Returns:     a bounded normal R^0 representative of value * c.
**************************************************/
static int16_t fqmul_public(int16_t value, int16_t public_montgomery)
{
    return montgomery_reduce((int32_t)value * public_montgomery);
}

/*************************************************
* Name:        fqmul_canonical
*
* Description: Clear, non-Montgomery field multiplication used only while
*              deriving public roots and inverse matrices for this reference.
*
* Returns:     the canonical product of a and b modulo q.
**************************************************/
static int16_t fqmul_canonical(int16_t a, int16_t b)
{
    return canonical((int64_t)a * b);
}

/*************************************************
* Name:        fqpow_canonical
*
* Description: Public-data exponentiation in Z_q using square-and-multiply.
*              This helper is not a production constant-time claim.
**************************************************/
static int16_t fqpow_canonical(int16_t base, int exponent)
{
    int16_t result = 1;
    while (exponent > 0) {
        if (exponent & 1)
            result = fqmul_canonical(result, base);
        base = fqmul_canonical(base, base);
        exponent >>= 1;
    }
    return result;
}

/*************************************************
* Name:        fqinv_canonical
*
* Description: Computes a public field inverse as value^(q-2) modulo q.
**************************************************/
static int16_t fqinv_canonical(int16_t value)
{
    return fqpow_canonical(value, GT864_Q - 2);
}

/*************************************************
* Name:        montgomery_encode
*
* Description: Encodes a public normal constant c as the centered
*              Montgomery-form constant cR modulo q.
**************************************************/
static int16_t montgomery_encode(int16_t value)
{
    return centered((int64_t)canonical(value) * NTRUPLUS_R);
}

/*************************************************
* Name:        centered_copy
*
* Description: Copies a coefficient vector while normalizing every entry to
*              the candidate's centered normal R^0 boundary representation.
**************************************************/
static void centered_copy(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    for (size_t i = 0; i < GT864_N; i++)
        out[i] = centered(in[i]);
}

/*************************************************
* Name:        build_legacy_to_grid
*
* Description: Derives the permutation between the current scalar cubic-leaf
*              order and the row-major GT grid by matching decoded X^3-zeta
*              labels.  No coefficient reduction or rescaling is performed.
*
* Arguments:   - mapping[legacy_leaf]: corresponding row-major GT leaf index
**************************************************/
static void build_legacy_to_grid(int mapping[GT864_POINTS])
{
    for (int pair = 0; pair < GT864_POINTS / 2; pair++) {
        for (int sign = 0; sign < 2; sign++) {
            int legacy = 2 * pair + sign;
            int16_t root_mont = sign == 0 ? zetas[GT864_POINTS / 2 + pair]
                                          : (int16_t)-zetas[GT864_POINTS / 2 + pair];
            int16_t root = canonical(montgomery_reduce(root_mont));
            mapping[legacy] = -1;
            for (int row = 0; row < GT864_ROWS; row++) {
                for (int col = 0; col < GT864_COLUMNS; col++) {
                    int16_t grid_root = canonical(montgomery_reduce(
                        gt864_roots_mont[row][col]));
                    if (grid_root == root)
                        mapping[legacy] = row * GT864_COLUMNS + col;
                }
            }
            assert(mapping[legacy] >= 0);
        }
    }
}

/*************************************************
* Name:        gt864_grid_to_legacy
*
* Description: Permutes row-major GT cubic leaves into the current scalar leaf
*              order.  This is a raw int16 permutation: it deliberately does
*              not center, reduce, or change Montgomery scale.
*
* Arguments:   - out: current scalar cubic-leaf order
*              - in:  row-major 9-by-32 GT cubic-leaf order
**************************************************/
void gt864_grid_to_legacy(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    int16_t input[GT864_N];
    int mapping[GT864_POINTS];

    for (int i = 0; i < GT864_N; i++)
        input[i] = in[i];
    build_legacy_to_grid(mapping);
    for (int legacy = 0; legacy < GT864_POINTS; legacy++) {
        for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++)
            out[legacy * GT864_LEAF_DEGREE + branch] =
                input[mapping[legacy] * GT864_LEAF_DEGREE + branch];
    }
}

/*************************************************
* Name:        gt864_legacy_to_grid
*
* Description: Inverse raw permutation from the current scalar cubic-leaf
*              order to row-major 9-by-32 GT cubic leaves.
**************************************************/
void gt864_legacy_to_grid(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    int16_t input[GT864_N];
    int mapping[GT864_POINTS];

    for (int i = 0; i < GT864_N; i++)
        input[i] = in[i];
    build_legacy_to_grid(mapping);
    for (int legacy = 0; legacy < GT864_POINTS; legacy++) {
        for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++)
            out[mapping[legacy] * GT864_LEAF_DEGREE + branch] =
                input[legacy * GT864_LEAF_DEGREE + branch];
    }
}

/*************************************************
* Name:        invert_vandermonde
*
* Description: Builds the inverse of V[column][degree]=z_column^degree over
*              Z_q from the compile-time Montgomery z table.  This slow helper
*              makes inverse reconstruction explicit and is not an optimized
*              32-point inverse transform.
*
* Arguments:   - inverse: output 32-by-32 inverse evaluation matrix
*              - z_mont:  the 32 public roots of Q(z), encoded as z*R mod q
**************************************************/
static void invert_vandermonde(
    int16_t inverse[GT864_COLUMNS][GT864_COLUMNS],
    const int16_t z_mont[GT864_COLUMNS])
{
    int16_t matrix[GT864_COLUMNS][2 * GT864_COLUMNS];

    for (int row = 0; row < GT864_COLUMNS; row++) {
        int16_t power = 1;
        for (int col = 0; col < GT864_COLUMNS; col++) {
            matrix[row][col] = power;
            power = canonical(fqmul_public(power, z_mont[row]));
            matrix[row][GT864_COLUMNS + col] = (int16_t)(row == col);
        }
    }

    for (int col = 0; col < GT864_COLUMNS; col++) {
        int pivot = col;
        while (pivot < GT864_COLUMNS && matrix[pivot][col] == 0)
            pivot++;
        assert(pivot < GT864_COLUMNS);
        if (pivot != col) {
            for (int j = 0; j < 2 * GT864_COLUMNS; j++) {
                int16_t temporary = matrix[col][j];
                matrix[col][j] = matrix[pivot][j];
                matrix[pivot][j] = temporary;
            }
        }

        int16_t pivot_inverse = fqinv_canonical(matrix[col][col]);
        for (int j = 0; j < 2 * GT864_COLUMNS; j++)
            matrix[col][j] = fqmul_canonical(matrix[col][j], pivot_inverse);

        for (int row = 0; row < GT864_COLUMNS; row++) {
            if (row == col)
                continue;
            int16_t factor = matrix[row][col];
            for (int j = 0; j < 2 * GT864_COLUMNS; j++)
                matrix[row][j] = canonical(
                    matrix[row][j] - (int64_t)factor * matrix[col][j]);
        }
    }

    for (int row = 0; row < GT864_COLUMNS; row++)
        for (int col = 0; col < GT864_COLUMNS; col++)
            inverse[row][col] = matrix[row][GT864_COLUMNS + col];
}

/*************************************************
* Name:        gt864_mont_forward
*
* Description: Computes the readable 9-by-32 Good-Thomas forward transform.
*              Input coefficients and output cubic-leaf coefficients remain
*              normal R^0 representatives; all public multiplication factors
*              are converted to Montgomery form before fqmul_public.
*
*              Stage 32 computes
*
*                T[b][s][c] = B_{b,s}(z_c)
*                            = sum_t a[3(s+9t)+b] z_c^t.
*
*              Stage 9 then computes
*
*                F[r][c][b] = sum_s T[b][s][c] y_{r,c}^s,
*                y_{r,c} = lambda_c eta^r.
*
* Arguments:   - out: row-major 9-by-32 cubic leaves; each leaf contains the
*                    three coefficients for Z_q[X]/(X^3-y_{r,c})
*              - in:  natural-order coefficients in R_q
*
* Aliasing:    out may equal in; the function first copies the input.
*
* Returns:     none.
**************************************************/
void gt864_mont_forward(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    int16_t input[GT864_N];
    int16_t stage32[GT864_LEAF_DEGREE][GT864_ROWS][GT864_COLUMNS];

    centered_copy(input, in);

    /* Stage 32: evaluate every B_{branch,residue} at each z column. */
    for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
        for (int residue = 0; residue < GT864_ROWS; residue++) {
            for (int col = 0; col < GT864_COLUMNS; col++) {
                int16_t value = 0;
                for (int degree = GT864_COLUMNS - 1; degree >= 0; degree--)
                    value = centered(fqmul_public(value, gt864_z_mont[col]) +
                                     input[GT864_LEAF_DEGREE *
                                           (residue + GT864_ROWS * degree) + branch]);
                stage32[branch][residue][col] = value;
            }
        }
    }

    /* Stage 9: combine the nine residue classes at y=lambda*eta^row. */
    for (int row = 0; row < GT864_ROWS; row++) {
        for (int col = 0; col < GT864_COLUMNS; col++) {
            for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
                int16_t value = 0;
                for (int residue = GT864_ROWS - 1; residue >= 0; residue--)
                    value = centered(fqmul_public(
                                         value, gt864_roots_mont[row][col]) +
                                     stage32[branch][residue][col]);
                out[(row * GT864_COLUMNS + col) * GT864_LEAF_DEGREE + branch] = value;
            }
        }
    }
}

/*************************************************
* Name:        gt864_mont_inverse
*
* Description: Inverts gt864_mont_forward and returns centered normal R^0
*              coefficients in natural order.
*
*              Inverse Stage 9 computes
*
*                T[b][s][c] = lambda_c^-s / 9
*                              * sum_r eta^(-rs) F[r][c][b].
*
*              Inverse Stage 32 multiplies each 32-value column vector by the
*              inverse public Vandermonde matrix to recover the coefficients
*              of B_{b,s}(z).
*
* Arguments:   - out: natural-order centered normal R^0 coefficients
*              - in:  row-major GT cubic leaves in normal R^0
*
* Aliasing:    out may equal in.
*
* Returns:     none.
**************************************************/
void gt864_mont_inverse(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    const int16_t inverse_9 = fqinv_canonical(GT864_ROWS);
    int16_t input[GT864_N];
    int16_t inverse_v[GT864_COLUMNS][GT864_COLUMNS];
    int16_t stage32[GT864_LEAF_DEGREE][GT864_ROWS][GT864_COLUMNS];

    centered_copy(input, in);
    invert_vandermonde(inverse_v, gt864_z_mont);

    /* Inverse Stage 9: undo eta^row and the column-dependent lambda twist. */
    for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
        for (int residue = 0; residue < GT864_ROWS; residue++) {
            for (int col = 0; col < GT864_COLUMNS; col++) {
                int16_t sum = 0;
                for (int row = 0; row < GT864_ROWS; row++) {
                    int exponent = (GT864_ROWS -
                                    (row * residue) % GT864_ROWS) % GT864_ROWS;
                    int16_t factor_mont = montgomery_encode(
                        fqpow_canonical(GT864_ETA, exponent));
                    sum = centered(sum + fqmul_public(
                        input[(row * GT864_COLUMNS + col) *
                              GT864_LEAF_DEGREE + branch], factor_mont));
                }
                int16_t lambda = canonical(montgomery_reduce(
                    gt864_roots_mont[0][col]));
                int16_t scale = fqmul_canonical(
                    inverse_9,
                    fqpow_canonical(fqinv_canonical(lambda), residue));
                stage32[branch][residue][col] =
                    centered(fqmul_public(sum, montgomery_encode(scale)));
            }
        }
    }

    /* Inverse Stage 32: interpolate B_{branch,residue} from its 32 values. */
    for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
        for (int residue = 0; residue < GT864_ROWS; residue++) {
            for (int degree = 0; degree < GT864_COLUMNS; degree++) {
                int16_t sum = 0;
                for (int col = 0; col < GT864_COLUMNS; col++)
                    sum = centered(sum + fqmul_public(
                        stage32[branch][residue][col],
                        montgomery_encode(inverse_v[degree][col])));
                out[GT864_LEAF_DEGREE *
                    (residue + GT864_ROWS * degree) + branch] = sum;
            }
        }
    }
}

/*************************************************
* Name:        gt864_mont_basemul
*
* Description: Multiplies corresponding cubic leaves in
*
*                Z_q[X] / (X^3 - y_{row,column}).
*
*              For a=a0+a1X+a2X^2 and b=b0+b1X+b2X^2,
*
*                c0 = a0b0 + y(a1b2+a2b1),
*                c1 = a0b1 + a1b0 + y a2b2,
*                c2 = a0b2 + a1b1 + a2b0.
*
*              The operation order and R^2 compensation match the current
*              scalar basemul so the bounded normal R^0 representatives match
*              exactly after the legacy permutation.
*
* Arguments:   - out: row-major GT cubic-leaf products
*              - a:   first row-major GT operand in normal R^0
*              - b:   second row-major GT operand in normal R^0
*
* Aliasing:    out may equal a or b.
*
* Returns:     none.
**************************************************/
void gt864_mont_basemul(int16_t out[GT864_N], const int16_t a[GT864_N],
                        const int16_t b[GT864_N])
{
    int16_t left[GT864_N];
    int16_t right[GT864_N];
    int16_t result[GT864_N];

    centered_copy(left, a);
    centered_copy(right, b);

    for (int row = 0; row < GT864_ROWS; row++) {
        for (int col = 0; col < GT864_COLUMNS; col++) {
            int offset = (row * GT864_COLUMNS + col) * GT864_LEAF_DEGREE;
            int16_t root_mont = gt864_roots_mont[row][col];
            int16_t a0 = left[offset + 0];
            int16_t a1 = left[offset + 1];
            int16_t a2 = left[offset + 2];
            int16_t b0 = right[offset + 0];
            int16_t b1 = right[offset + 1];
            int16_t b2 = right[offset + 2];
            int16_t r0 = montgomery_reduce((int32_t)a2 * b1 + (int32_t)a1 * b2);
            int16_t r1 = montgomery_reduce((int32_t)a2 * b2);

            r0 = montgomery_reduce((int32_t)r0 * root_mont + (int32_t)a0 * b0);
            r1 = montgomery_reduce((int32_t)r1 * root_mont +
                                   (int32_t)a0 * b1 + (int32_t)a1 * b0);
            int16_t r2 = montgomery_reduce((int32_t)a2 * b0 +
                                           (int32_t)a1 * b1 +
                                           (int32_t)a0 * b2);
            result[offset + 0] = montgomery_reduce((int32_t)r0 * NTRUPLUS_RSQ);
            result[offset + 1] = montgomery_reduce((int32_t)r1 * NTRUPLUS_RSQ);
            result[offset + 2] = montgomery_reduce((int32_t)r2 * NTRUPLUS_RSQ);
        }
    }
    for (int i = 0; i < GT864_N; i++)
        out[i] = result[i];
}

/*************************************************
* Name:        gt864_mont_mul
*
* Description: Reference multiplication in R_q using the complete GT path:
*
*                forward(a), forward(b), cubic basemul, inverse.
*
* Arguments:   - out: natural-order centered product in R_q
*              - a:   first natural-order operand
*              - b:   second natural-order operand
*
* Aliasing:    out may equal a or b.
*
* Returns:     none.
**************************************************/
void gt864_mont_mul(int16_t out[GT864_N], const int16_t a[GT864_N],
                    const int16_t b[GT864_N])
{
    int16_t forward_a[GT864_N];
    int16_t forward_b[GT864_N];
    int16_t product[GT864_N];

    gt864_mont_forward(forward_a, a);
    gt864_mont_forward(forward_b, b);
    gt864_mont_basemul(product, forward_a, forward_b);
    gt864_mont_inverse(out, product);
}

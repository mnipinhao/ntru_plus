#include "inverse_asm.h"
#include "base_tables.h"

#include <arm_neon.h>

#define Q 3457
#define NEG_QINV (-12929)
#define RINV (-682)            /* R^-1 mod q */

/*
 * NTRU+1152 transform-domain inversion and the R^-1 multiplication boundary.
 *
 * Written as NEON intrinsics C, following NTRU+864's phase decomposition so a
 * later gate can swap in assembly phase by phase:
 *
 *   numerator   per leaf, the quartic adjugate and the scalar norm
 *   prefix      running products over the 36 groups
 *   inverse     one 8-lane field inversion
 *   recover     walk back to each individual inverse
 *   finish      apply, with the +,-,+,- conjugation signs
 *
 * NTRU+864 splits the batch into 12 steps x 3 chains for instruction-level
 * parallelism; that is an optimization, not a correctness requirement, and is
 * left to a later gate.
 *
 * Degree 4 makes this simpler than degree 3, not harder: X^4 - zeta is a
 * quadratic tower.  With u = X^2 and u^2 = zeta, a = (a0+a2 u) + X(a1+a3 u)
 * lives in R[X]/(X^2 - u) over R = Z_q[u]/(u^2 - zeta), so inversion is two
 * nested quadratic conjugations.  Degree 3 needs a genuine cubic resultant.
 * The +,-,+,- sign pattern is that conjugation, deferred to the final scaling.
 */

typedef struct {
    int32x4_t low;
    int32x4_t high;
} wide8;

static inline wide8 multiply(int16x8_t a, int16x8_t b)
{
    wide8 out = {vmull_s16(vget_low_s16(a), vget_low_s16(b)),
                 vmull_high_s16(a, b)};
    return out;
}

static inline wide8 multiply_add(wide8 acc, int16x8_t a, int16x8_t b)
{
    acc.low = vmlal_s16(acc.low, vget_low_s16(a), vget_low_s16(b));
    acc.high = vmlal_high_s16(acc.high, a, b);
    return acc;
}

static inline wide8 multiply_sub(wide8 acc, int16x8_t a, int16x8_t b)
{
    acc.low = vmlsl_s16(acc.low, vget_low_s16(a), vget_low_s16(b));
    acc.high = vmlsl_high_s16(acc.high, a, b);
    return acc;
}

static inline int16x8_t montgomery_reduce(wide8 value)
{
    const int16x8_t q = vdupq_n_s16(Q);
    const int16x8_t neg_qinv = vdupq_n_s16(NEG_QINV);
    int16x8_t quotient = vuzp1q_s16(
        vreinterpretq_s16_s32(value.low),
        vreinterpretq_s16_s32(value.high));

    quotient = vmulq_s16(quotient, neg_qinv);
    value.low = vmlal_s16(value.low, vget_low_s16(quotient),
                          vget_low_s16(q));
    value.high = vmlal_high_s16(value.high, quotient, q);
    return vuzp2q_s16(vreinterpretq_s16_s32(value.low),
                      vreinterpretq_s16_s32(value.high));
}

static inline int16x8_t fqmul(int16x8_t a, int16x8_t b)
{
    return montgomery_reduce(multiply(a, b));
}

/*
 * D7's normalization, without touching the multiply pipe.
 *
 * The purpose is only to bring basemul_rinv's output, which G2 bounds at 2752,
 * inside NTRU+864's documented inverse input contract of 2497, so that the 864
 * bound chain holds a fortiori instead of needing re-derivation.  A centered
 * Barrett does that but costs two multiply-class instructions per vector, and
 * the multiply pipe is what bounds this kernel: the official's basemul_scale
 * issues exactly the same 52 widening multiplies and 7 muls and simply has no
 * reduction at the end.
 *
 * A single conditional subtract is enough and uses no multiply at all.  With
 * |x| <= 2752 < 1728 + q, exactly one of the three cases applies:
 *
 *     x >  1728  ->  x - q  in (-1729, -705]
 *     x < -1728  ->  x + q  in [705, 1729)
 *     otherwise  ->  |x| <= 1728
 *
 * so the output lands in [-1728, 1728], one tighter than the Barrett's
 * [-1729, 1729], and D7's contract is honoured exactly.
 */
static inline int16x8_t normalize_d7(int16x8_t a)
{
    const int16x8_t q = vdupq_n_s16(Q);
    const int16x8_t hi = vdupq_n_s16(1728);
    const int16x8_t lo = vdupq_n_s16(-1728);

    a = vsubq_s16(a, vandq_s16(vreinterpretq_s16_u16(vcgtq_s16(a, hi)), q));
    return vaddq_s16(a, vandq_s16(vreinterpretq_s16_u16(vcltq_s16(a, lo)), q));
}

/* Inverse in Z_q via the reference addition chain for exponent 3455. */
static inline int16x8_t fqinv(int16x8_t a)
{
    int16x8_t t1, t2, t3;

    t1 = fqmul(a, a);
    t2 = fqmul(t1, t1);
    t2 = fqmul(t2, t2);
    t3 = fqmul(t2, t2);
    t1 = fqmul(t1, t2);
    t2 = fqmul(t1, t3);
    t2 = fqmul(t2, t2);
    t2 = fqmul(t2, a);
    t1 = fqmul(t1, t2);
    t2 = fqmul(t2, t2);
    t2 = fqmul(t2, t2);
    t2 = fqmul(t2, t2);
    t2 = fqmul(t2, t2);
    t2 = fqmul(t2, t2);
    t2 = fqmul(t2, t2);
    t2 = fqmul(t2, t1);
    return fqmul(vdupq_n_s16(RINV), t2);
}

#define LOAD4(dst, src, off)                      \
    do {                                          \
        (dst)[0] = vld1q_s16((src) + (off));      \
        (dst)[1] = vld1q_s16((src) + (off) + 8);  \
        (dst)[2] = vld1q_s16((src) + (off) + 16); \
        (dst)[3] = vld1q_s16((src) + (off) + 24); \
    } while (0)

#define STORE4(dst, off, v)                        \
    do {                                           \
        vst1q_s16((dst) + (off), (v)[0]);          \
        vst1q_s16((dst) + (off) + 8, (v)[1]);      \
        vst1q_s16((dst) + (off) + 16, (v)[2]);     \
        vst1q_s16((dst) + (off) + 24, (v)[3]);     \
    } while (0)

/*
 * R^-1 boundary multiplication: the quartic product stopped one Montgomery
 * stage before R0, then normalized.  Same leaf algebra as basemul; only the
 * final rescale differs.
 */
/*
 * The scheduled kernel, when one is installed by dev/scripts/autogen.py.  Its
 * ABI takes the zeta table as a fourth argument and advances all four pointers,
 * so the shim restores this file's signature.  Without the define, the C below
 * is used and every gate still passes -- the assembly is an optimization, not a
 * dependency.
 */
#ifdef NTRUPLUS1152_ASM_BASEMUL_RINV
void basemul_rinv_kernel(int16_t *out, const int16_t *a, const int16_t *b,
                         const int16_t *zetas);

void basemul_rinv_asm(int16_t out[BASE_COEFFICIENTS],
                      const int16_t a[BASE_COEFFICIENTS],
                      const int16_t b[BASE_COEFFICIENTS])
{
    basemul_rinv_kernel(out, a, b, &basemul_zetas[0][0]);
}
#else
void basemul_rinv_asm(int16_t out[BASE_COEFFICIENTS],
                      const int16_t a[BASE_COEFFICIENTS],
                      const int16_t b[BASE_COEFFICIENTS])
{
    for (int group = 0; group < 36; group++) {
        int offset = 32 * group;
        int16x8_t av[4], bv[4], r[4];
        int16x8_t zeta = vld1q_s16(basemul_zetas[group]);
        wide8 cross0, cross1, cross2, acc;

        LOAD4(av, a, offset);
        LOAD4(bv, b, offset);

        /* Pre-multiply the zeta into b once, so the four output chains are
         * independent accumulations instead of cross -> reduce -> zeta ->
         * accumulate -> reduce in series.  The instruction multiset is
         * unchanged; only the dependency structure is.  Algebraically identical:
         * zeta*cross*R^-2 expands to a1*(zeta*b3*R^-1)*R^-1 + ... */
        int16x8_t bz1 = montgomery_reduce(multiply(zeta, bv[1]));
        int16x8_t bz2 = montgomery_reduce(multiply(zeta, bv[2]));
        int16x8_t bz3 = montgomery_reduce(multiply(zeta, bv[3]));

        acc = multiply(av[0], bv[0]);
        acc = multiply_add(acc, av[1], bz3);
        acc = multiply_add(acc, av[2], bz2);
        acc = multiply_add(acc, av[3], bz1);
        r[0] = montgomery_reduce(acc);

        acc = multiply(av[0], bv[1]);
        acc = multiply_add(acc, av[1], bv[0]);
        acc = multiply_add(acc, av[2], bz3);
        acc = multiply_add(acc, av[3], bz2);
        r[1] = montgomery_reduce(acc);

        acc = multiply(av[0], bv[2]);
        acc = multiply_add(acc, av[1], bv[1]);
        acc = multiply_add(acc, av[2], bv[0]);
        acc = multiply_add(acc, av[3], bz3);
        r[2] = montgomery_reduce(acc);

        acc = multiply(av[0], bv[3]);
        acc = multiply_add(acc, av[1], bv[2]);
        acc = multiply_add(acc, av[2], bv[1]);
        acc = multiply_add(acc, av[3], bv[0]);
        r[3] = montgomery_reduce(acc);

        for (int i = 0; i < 4; i++)
            r[i] = normalize_d7(r[i]);
        STORE4(out, offset, r);
    }
}
#endif

int baseinv_asm(int16_t out[BASE_COEFFICIENTS],
                const int16_t in[BASE_COEFFICIENTS])
{
    int16x8_t den[36];
    int16x8_t prefix[36];

    /* ---- numerator: quartic adjugate into out, norm into den ---- */
    for (int group = 0; group < 36; group++) {
        int offset = 32 * group;
        int16x8_t a[4], r[4];
        int16x8_t zeta = vld1q_s16(basemul_zetas[group]);
        int16x8_t t0, t1, t2;
        wide8 acc;

        LOAD4(a, in, offset);

        /* t0 = a2^2 - 2 a1 a3 ; t1 = a3^2 */
        acc = multiply(a[2], a[2]);
        acc = multiply_sub(acc, a[1], a[3]);
        acc = multiply_sub(acc, a[1], a[3]);
        t0 = montgomery_reduce(acc);
        t1 = montgomery_reduce(multiply(a[3], a[3]));

        /* t0 = a0^2 + zeta t0 ; t1 = a1^2 + zeta t1 - 2 a0 a2 */
        acc = multiply(a[0], a[0]);
        acc = multiply_add(acc, t0, zeta);
        t0 = montgomery_reduce(acc);

        acc = multiply(a[1], a[1]);
        acc = multiply_add(acc, t1, zeta);
        acc = multiply_sub(acc, a[0], a[2]);
        acc = multiply_sub(acc, a[0], a[2]);
        t1 = montgomery_reduce(acc);

        t2 = montgomery_reduce(multiply(t1, zeta));

        /* norm = t0^2 - t1 t2 */
        acc = multiply(t0, t0);
        acc = multiply_sub(acc, t1, t2);
        den[group] = montgomery_reduce(acc);

        r[0] = montgomery_reduce(multiply_add(multiply(a[0], t0), a[2], t2));
        r[1] = montgomery_reduce(multiply_add(multiply(a[3], t2), a[1], t0));
        r[2] = montgomery_reduce(multiply_add(multiply(a[2], t0), a[0], t1));
        r[3] = montgomery_reduce(multiply_add(multiply(a[1], t1), a[3], t0));
        STORE4(out, offset, r);
    }

    /* ---- 3 independent prefix chains, one inversion, 3 recover chains ---- */
    {
        const int K = 3, M = 12;
        int16x8_t cpre[3], ip[3], carry[3];

        for (int c = 0; c < K; c++)
            prefix[c * M] = den[c * M];
        for (int j = 1; j < M; j++)
            for (int c = 0; c < K; c++)
                prefix[c * M + j] = fqmul(prefix[c * M + j - 1], den[c * M + j]);

        /* the same batch inversion, one level up, over the K chain products */
        cpre[0] = prefix[M - 1];
        for (int c = 1; c < K; c++)
            cpre[c] = fqmul(cpre[c - 1], prefix[c * M + M - 1]);

        /*
         * cpre[K-1] is the product of all 36, exactly what the single-chain
         * version inverted.  Prefix values lie inside (-q,q), so only integer
         * zero represents zero; vminvq_u16 folds all eight lanes with no early
         * exit and the branch depends on public non-invertibility.
         */
        if (!vminvq_u16(vreinterpretq_u16_s16(cpre[K - 1]))) {
            for (int i = 0; i < BASE_COEFFICIENTS; i++)
                out[i] = 0;
            return 1;
        }

        {
            int16x8_t t = fqinv(cpre[K - 1]);
            for (int c = K - 1; c > 0; c--) {
                ip[c] = fqmul(cpre[c - 1], t);
                t = fqmul(t, prefix[c * M + M - 1]);
            }
            ip[0] = t;
        }

        for (int c = 0; c < K; c++)
            carry[c] = ip[c];
        for (int j = M - 1; j > 0; j--)
            for (int c = 0; c < K; c++) {
                int16x8_t di = den[c * M + j];
                den[c * M + j] = fqmul(prefix[c * M + j - 1], carry[c]);
                carry[c] = fqmul(carry[c], di);
            }
        for (int c = 0; c < K; c++)
            den[c * M] = carry[c];
    }

    /* ---- finish: apply with the +,-,+,- conjugation signs ---- */
    for (int group = 0; group < 36; group++) {
        int offset = 32 * group;
        int16x8_t pden = den[group];
        int16x8_t mden = vnegq_s16(pden);
        int16x8_t r[4];

        LOAD4(r, out, offset);
        r[0] = fqmul(r[0], pden);
        r[1] = fqmul(r[1], mden);
        r[2] = fqmul(r[2], pden);
        r[3] = fqmul(r[3], mden);
        STORE4(out, offset, r);
    }

    return 0;
}

#include "inverse_asm.h"
#include "base_tables.h"

#include <arm_neon.h>

#define Q 3457
#define NEG_QINV (-12929)
#define BARRETT_V 19412        /* ((1<<26) + Q/2) / Q */
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
 * Centered Barrett reduction into {-(q+1)/2 .. (q+1)/2}, the NEON form of the
 * reference barrett_reduce.  Used to honour decision D7: the degree-4
 * basemul_rinv output reaches 2752, above NTRU+864's documented inverse input
 * contract of 2497, and this brings it to [-1729, 1728] so that the NTRU+864
 * bound chain holds a fortiori instead of needing re-derivation.
 */
static inline int16x8_t barrett_reduce(int16x8_t a)
{
    int16x8_t t = vqdmulhq_n_s16(a, BARRETT_V);
    t = vrshrq_n_s16(t, 11);
    return vmlsq_n_s16(a, t, (int16_t)Q);
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

        cross0 = multiply(av[1], bv[3]);
        cross0 = multiply_add(cross0, av[2], bv[2]);
        cross0 = multiply_add(cross0, av[3], bv[1]);
        cross1 = multiply(av[2], bv[3]);
        cross1 = multiply_add(cross1, av[3], bv[2]);
        cross2 = multiply(av[3], bv[3]);

        acc = multiply(montgomery_reduce(cross0), zeta);
        acc = multiply_add(acc, av[0], bv[0]);
        r[0] = montgomery_reduce(acc);

        acc = multiply(montgomery_reduce(cross1), zeta);
        acc = multiply_add(acc, av[0], bv[1]);
        acc = multiply_add(acc, av[1], bv[0]);
        r[1] = montgomery_reduce(acc);

        acc = multiply(montgomery_reduce(cross2), zeta);
        acc = multiply_add(acc, av[0], bv[2]);
        acc = multiply_add(acc, av[1], bv[1]);
        acc = multiply_add(acc, av[2], bv[0]);
        r[2] = montgomery_reduce(acc);

        acc = multiply(av[3], bv[0]);
        acc = multiply_add(acc, av[2], bv[1]);
        acc = multiply_add(acc, av[1], bv[2]);
        acc = multiply_add(acc, av[0], bv[3]);
        r[3] = montgomery_reduce(acc);

        for (int i = 0; i < 4; i++)
            r[i] = barrett_reduce(r[i]);
        STORE4(out, offset, r);
    }
}

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

    /* ---- prefix, one inversion, recover ---- */
    prefix[0] = den[0];
    for (int i = 1; i < 36; i++)
        prefix[i] = fqmul(prefix[i - 1], den[i]);

    /*
     * Prefix values lie inside (-q,q), so only integer zero represents zero.
     * vminvq_u16 folds all eight lanes with no early exit, and the single
     * branch below depends on public non-invertibility, not on lane data.
     */
    if (!vminvq_u16(vreinterpretq_u16_s16(prefix[35]))) {
        for (int i = 0; i < BASE_COEFFICIENTS; i++)
            out[i] = 0;
        return 1;
    }

    {
        int16x8_t inv = fqinv(prefix[35]);
        for (int i = 35; i > 0; i--) {
            int16x8_t di = den[i];
            den[i] = fqmul(prefix[i - 1], inv);
            inv = fqmul(inv, di);
        }
        den[0] = inv;
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

#include "gate.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t rng_state = UINT64_C(0x0819e3779b97f4a7);
static unsigned control_bound, candidate_bound;

static uint32_t rng32(void)
{
    rng_state ^= rng_state << 7;
    rng_state ^= rng_state >> 9;
    return (uint32_t)rng_state;
}

static int modq(int x)
{
    x %= 3457;
    return x < 0 ? x + 3457 : x;
}

static int mulq(int a, int b) { return modq(a * b); }
static unsigned bitreverse5(unsigned x)
{
    unsigned y = 0;
    for (unsigned i = 0; i < 5; ++i) { y = (y << 1) | (x & 1U); x >>= 1; }
    return y;
}
static int powq(int a, unsigned e)
{
    int r = 1;
    while (e) { if (e & 1U) r = mulq(r, a); a = mulq(a, a); e >>= 1; }
    return r;
}

/*
 * Attribution oracle only: undo the D2 sign evaluation explicitly, then feed
 * the reconstructed quartics into the already-qualified current I0/I1
 * redeposit.  This distinguishes a QBM defect from an inverse-axis defect.
 */
static void qbm_explicit_crt_post_i1(int16_t out[GATE_WORDS],
    const int16_t *a, const int16_t *b)
{
    int16_t qbm[GATE_WORDS] __attribute__((aligned(32)));
    int16_t quartic[GATE_WORDS] __attribute__((aligned(32)));
    static const unsigned physical_to_j[32] = {
         0,  4,  2,  6, 16, 20, 18, 22,  8, 12, 10, 14, 24, 28, 26, 30,
         1,  5,  3,  7, 17, 21, 19, 23,  9, 13, 11, 15, 25, 29, 27, 31
    };
    const int mu0 = 110, w64 = 3160;
    const int inv2 = powq(2, 3455);
    d2_inverse64_qbm_asm(qbm, a, b);
    for (unsigned physical = 0; physical < 32; ++physical) {
        const unsigned group = physical >> 4, lane = physical & 15U;
        const int mu = mulq(mu0, powq(w64, physical_to_j[physical]));
        const int inv2mu = powq(mulq(2, mu), 3455);
        const int p0 = modq(qbm[physical]);
        const int m0 = modq(qbm[32 + physical]);
        const int p1 = modq(qbm[64 + physical]);
        const int m1 = modq(qbm[96 + physical]);
        quartic[64 * group + 0 * 16 + lane] = (int16_t)mulq(p0 + m0, inv2);
        quartic[64 * group + 1 * 16 + lane] = (int16_t)mulq(p1 + m1, inv2);
        quartic[64 * group + 2 * 16 + lane] = (int16_t)mulq(p0 - m0, inv2mu);
        quartic[64 * group + 3 * 16 + lane] = (int16_t)mulq(p1 - m1, inv2mu);
    }
    late_d2_redeposit_i01_asm(out, quartic);
}

static void check_hwa_to_tile4(void)
{
    int16_t h[GATE_WORDS] __attribute__((aligned(32)));
    int16_t t[GATE_WORDS] __attribute__((aligned(32)));
    for (unsigned i = 0; i < GATE_WORDS; ++i) h[i] = (int16_t)(i + 1);
    hwa_to_tile4_asm(t, h);
    for (unsigned c = 0; c < 4; ++c)
        for (unsigned q = 0; q < 32; ++q) {
            const unsigned word = 16 * (q >> 2) + 4 * (q & 3U) + c;
            if (t[word] != h[32 * c + q]) {
                fprintf(stderr, "hwa_to_tile4 mismatch c=%u q=%u word=%u want=%d have=%d\n",
                    c, q, word, h[32 * c + q], t[word]);
                exit(1);
            }
        }
}

static void diagnose_inverse(const int16_t *a, const int16_t *b)
{
    int16_t t[GATE_WORDS] __attribute__((aligned(32)));
    int16_t u[GATE_WORDS] __attribute__((aligned(32)));
    int16_t h[GATE_WORDS] __attribute__((aligned(32)));
    d2_inverse64_qbm_asm(t, a, b);
    d2_inverse64_naturalize_asm(u, t);
    d2_inverse64_inv_asm(h, u);
    int w = powq(7, 54U * 21U), inv64 = powq(64, 3455), invmu = powq(110, 3455);
    for (unsigned plane = 0; plane < 2; ++plane) {
        unsigned bad = 0;
        int x[64];
        for (unsigned k = 0; k < 64; ++k) x[k] = modq(u[64 * plane + k]);
        for (unsigned length = 2; length <= 64; length <<= 1) {
            unsigned distance = length / 2;
            for (unsigned group = 0; group < 64; group += length)
                for (unsigned z = 0; z < distance; ++z) {
                    int low = x[group + z];
                    int high = x[group + distance + z];
                    if (length != 2)
                        high = mulq(high, powq(w, (64 - z * (64 / length)) % 64));
                    x[group + z] = modq(low + high);
                    x[group + distance + z] = modq(low - high);
                }
        }
        for (unsigned j = 0; j < 64; ++j) {
            int want = mulq(x[j], inv64);
            unsigned c = plane + 2U * (j & 1U), q = j / 2U;
            if (j & 1U) want = mulq(want, invmu);
            int have = modq(h[32 * c + q]);
            if (want != have) {
                if (bad++ < 8)
                    fprintf(stderr, "inverse64 mismatch plane=%u j=%u c=%u q=%u want=%d have=%d\n",
                            plane, j, c, q, want, have);
            }
        }
        fprintf(stderr, "inverse64 plane=%u mismatches=%u\n", plane, bad);
        if (plane == 0) {
            fprintf(stderr, "observed-output-index-map:");
            for (unsigned jj = 0; jj < 16; ++jj) {
                unsigned cc = 2U * (jj & 1U), qq = jj / 2U;
                int have = modq(h[32 * cc + qq]), found = -1;
                for (unsigned z = 0; z < 64; ++z) {
                    int want = mulq(x[z], inv64);
                    if (z & 1U) want = mulq(want, invmu);
                    if (want == have) { found = (int)z; break; }
                }
                fprintf(stderr, " %d", found);
            }
            fprintf(stderr, "\n");
        }
    }
    fprintf(stderr, "inverse64 ASM matches scalar IDFT64\n");
}

static void diagnose_endpoint_relation(const int16_t *a, const int16_t *b,
    const int16_t *control)
{
    int16_t qbm[GATE_WORDS] __attribute__((aligned(32)));
    static const unsigned physical_to_k[32] = {
         0,  4,  2,  6, 16, 20, 18, 22,  8, 12, 10, 14, 24, 28, 26, 30,
         1,  5,  3,  7, 17, 21, 19, 23,  9, 13, 11, 15, 25, 29, 27, 31
    };
    int c0[32] = {0}, plus[32] = {0}, minus[32] = {0};
    const int inv2 = powq(2, 3455), inv32 = powq(32, 3455);
    const int omega32 = 1784;
    d2_inverse64_qbm_asm(qbm, a, b);
    for (unsigned physical = 0; physical < 32; ++physical) {
        const unsigned k = physical_to_k[physical];
        plus[k] = modq(qbm[physical]);
        minus[k] = modq(qbm[32 + physical]);
        c0[k] = mulq(plus[k] + minus[k], inv2);
    }
    fprintf(stderr, "endpoint scalar c0 n=0..7:\n");
    for (unsigned n = 0; n < 8; ++n) {
        int from32 = 0, from64even = 0;
        for (unsigned k = 0; k < 32; ++k) {
            const int weight = powq(omega32, (32 - (k * n & 31U)) & 31U);
            from32 = modq(from32 + c0[k] * weight);
            /* W^(-k*2n) is the same omega32 weight. */
            from64even = modq(from64even + (plus[k] + minus[k]) * weight);
        }
        from32 = mulq(from32, inv32);
        from64even = mulq(from64even, powq(64, 3455));
        const unsigned word = 16 * (n >> 2) + 4 * (n & 3U);
        fprintf(stderr, " n%u control=%d idft32=%d idft64even=%d\n",
            n, modq(control[word]), from32, from64even);
    }
}

static void run_control(int16_t *out, const int16_t *a, const int16_t *b)
{
    int16_t t0[GATE_WORDS] __attribute__((aligned(32)));
    int16_t t1[GATE_WORDS] __attribute__((aligned(32)));
    late_soa_basemul_i2_fused_asm(t0, a, b);
    control_inverse_cross3_asm(t1, t0);
    inverse32_normalize_asm(out, t1);
}

static void run_candidate(int16_t *out, const int16_t *a, const int16_t *b)
{
    int16_t t[GATE_WORDS] __attribute__((aligned(32)));
    int16_t u[GATE_WORDS] __attribute__((aligned(32)));
    int16_t h[GATE_WORDS] __attribute__((aligned(32)));
    d2_inverse64_qbm_asm(t, a, b);
    d2_inverse64_naturalize_asm(u, t);
    d2_inverse64_inv_asm(h, u);
    hwa_to_tile4_asm(out, h);
}

static void one_case(const int16_t *a, const int16_t *b, unsigned trial)
{
    int16_t control[GATE_WORDS] __attribute__((aligned(32)));
    int16_t candidate[GATE_WORDS] __attribute__((aligned(32)));
    int16_t current_i01[GATE_WORDS] __attribute__((aligned(32)));
    int16_t d2_i01[GATE_WORDS] __attribute__((aligned(32)));
    int16_t qbm[GATE_WORDS] __attribute__((aligned(32)));
    int16_t natural[GATE_WORDS] __attribute__((aligned(32)));
    static const unsigned physical_to_k[32] = {
         0,  4,  2,  6, 16, 20, 18, 22,  8, 12, 10, 14, 24, 28, 26, 30,
         1,  5,  3,  7, 17, 21, 19, 23,  9, 13, 11, 15, 25, 29, 27, 31
    };
    late_soa_basemul_i2_fused_asm(current_i01, a, b);
    qbm_explicit_crt_post_i1(d2_i01, a, b);
    for (unsigned i = 0; i < GATE_WORDS; ++i) {
        if (modq(current_i01[i]) != modq(d2_i01[i])) {
            fprintf(stderr,
                "QBM/CRT bridge mismatch trial=%u word=%u current=%d d2=%d\n",
                trial, i, current_i01[i], d2_i01[i]);
            exit(1);
        }
    }
    d2_inverse64_qbm_asm(qbm, a, b);
    d2_inverse64_naturalize_asm(natural, qbm);
    for (unsigned physical = 0; physical < 32; ++physical) {
        const unsigned r = bitreverse5(physical_to_k[physical]);
        for (unsigned plane = 0; plane < 2; ++plane) {
            if (modq(natural[64 * plane + 2 * r]) !=
                    modq(qbm[64 * plane + physical]) ||
                modq(natural[64 * plane + 2 * r + 1]) !=
                    modq(qbm[64 * plane + 32 + physical])) {
                fprintf(stderr, "naturalization mismatch trial=%u plane=%u physical=%u k=%u "
                    "plus={raw:%d,natural:%d,mods:%d/%d}@%u "
                    "minus={raw:%d,natural:%d,mods:%d/%d}\n",
                    trial, plane, physical, physical_to_k[physical],
                    qbm[64 * plane + physical], natural[64 * plane + 2 * r],
                    modq(qbm[64 * plane + physical]), modq(natural[64 * plane + 2 * r]), 2 * r,
                    qbm[64 * plane + 32 + physical], natural[64 * plane + 2 * r + 1],
                    modq(qbm[64 * plane + 32 + physical]), modq(natural[64 * plane + 2 * r + 1]));
                exit(1);
            }
        }
    }
    run_control(control, a, b);
    run_candidate(candidate, a, b);
    for (unsigned i = 0; i < GATE_WORDS; ++i) {
        unsigned ca = (unsigned)(control[i] < 0 ? -(int)control[i] : control[i]);
        unsigned da = (unsigned)(candidate[i] < 0 ? -(int)candidate[i] : candidate[i]);
        if (ca > control_bound) control_bound = ca;
        if (da > candidate_bound) candidate_bound = da;
        if (modq(control[i]) != modq(candidate[i])) {
            fprintf(stderr, "mismatch trial=%u word=%u control=%d candidate=%d\n",
                    trial, i, control[i], candidate[i]);
            fprintf(stderr, "ratios:");
            for (unsigned z = 0; z < 32; ++z) {
                int cv = modq(control[4 * z + 2]), dv = modq(candidate[4 * z + 2]);
                if (dv) fprintf(stderr, " %d", mulq(cv, powq(dv, 3455)));
            }
            fprintf(stderr, "\n");
            diagnose_endpoint_relation(a, b, control);
            diagnose_inverse(a, b);
            exit(1);
        }
    }
}

int main(void)
{
    int16_t a[GATE_WORDS] __attribute__((aligned(32)));
    int16_t b[GATE_WORDS] __attribute__((aligned(32)));
    unsigned trial = 0;
    check_hwa_to_tile4();
    for (unsigned i = 0; i < GATE_WORDS; ++i) {
        memset(a, 0, sizeof(a));
        memset(b, 0, sizeof(b));
        a[i] = 1;
        b[(37U * i + 9U) & 127U] = -1;
        one_case(a, b, trial++);
    }
    static const int16_t v[] = {0, 1, -1, 1728, -1728, 863, -863, 432};
    for (unsigned k = 0; k < 8; ++k) {
        for (unsigned i = 0; i < GATE_WORDS; ++i) {
            a[i] = v[(i + k) & 7U];
            b[i] = v[(3U * i + 2U * k) & 7U];
        }
        one_case(a, b, trial++);
    }
    for (unsigned n = 0; n < 2000; ++n) {
        for (unsigned i = 0; i < GATE_WORDS; ++i) {
            a[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
            b[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
        }
        one_case(a, b, trial++);
    }
    printf("081 executable correctness passed: trials=%u bounds={control:%u,candidate:%u}\n",
           trial, control_bound, candidate_bound);
    return 0;
}

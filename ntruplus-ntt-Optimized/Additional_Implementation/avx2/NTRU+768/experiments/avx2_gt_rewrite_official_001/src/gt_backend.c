#include "gt_backend.h"

#include <limits.h>
#include <stddef.h>
#include <string.h>

#include "gt_generated_tables.h"

enum {
    GT_PHI_CENTERED = -722,
    GT_PHI_INV_CENTERED = 723,
    GT_OMEGA96 = 675,
};

static int16_t mod_centered(int64_t x)
{
    int64_t r = x % NTRUPLUS_Q;
    if (r < 0)
        r += NTRUPLUS_Q;
    if (r > (NTRUPLUS_Q - 1) / 2)
        r -= NTRUPLUS_Q;
    return (int16_t)r;
}

static int mod_nonnegative(int64_t x)
{
    int r = (int)(x % NTRUPLUS_Q);
    return r < 0 ? r + NTRUPLUS_Q : r;
}

static int mod_pow(int base, uint64_t exponent)
{
    int result = 1;
    int x = mod_nonnegative(base);
    while (exponent != 0) {
        if (exponent & 1U)
            result = mod_nonnegative((int64_t)result * x);
        x = mod_nonnegative((int64_t)x * x);
        exponent >>= 1;
    }
    return result;
}

static size_t gt_word(size_t component, size_t degree)
{
    const size_t branch = component / 96;
    const size_t rem = component % 96;
    const size_t k3 = rem / 32;
    const size_t k32 = rem % 32;
    const size_t block32 = k32 / 16;
    const size_t lane = k32 % 16;
    const size_t batch = ((branch * 3 + k3) * 2 + block32);
    return 64 * batch + 16 * degree + lane;
}

static void range_init(gt_range_trace *trace)
{
    if (trace == NULL)
        return;
    int *p = (int *)trace;
    for (size_t i = 0; i < sizeof *trace / sizeof *p; i += 2) {
        p[i] = INT_MAX;
        p[i + 1] = INT_MIN;
    }
}

static void range_add(int *minimum, int *maximum, int value)
{
    if (minimum == NULL)
        return;
    if (value < *minimum)
        *minimum = value;
    if (value > *maximum)
        *maximum = value;
}

static void ntt32_b(int16_t out[32], const int16_t in[32],
                    gt_n32_variant variant, gt_range_trace *trace)
{
    const int omega32 = mod_pow(GT_OMEGA96, 3);
    const int omega16 = mod_nonnegative((int64_t)omega32 * omega32);
    int16_t plus[16];
    int16_t minus[16];

    for (size_t j = 0; j < 16; ++j) {
        const int p = (int)in[j] + in[j + 16];
        const int m = (int)in[j] - in[j + 16];
        range_add(trace == NULL ? NULL : &trace->split_min,
                  trace == NULL ? NULL : &trace->split_max, p);
        range_add(trace == NULL ? NULL : &trace->split_min,
                  trace == NULL ? NULL : &trace->split_max, m);
        plus[j] = variant == GT_N32_B2 ? mod_centered(p) : (int16_t)p;
        minus[j] = mod_centered((int64_t)m * gt_b_split_twist[j]);
    }

    for (size_t k = 0; k < 16; ++k) {
        int64_t even = 0;
        int64_t odd = 0;
        for (size_t j = 0; j < 16; ++j) {
            const int weight = mod_pow(omega16, j * k);
            even += (int64_t)plus[j] * weight;
            odd += (int64_t)minus[j] * weight;
        }
        out[2 * k] = mod_centered(even);
        out[2 * k + 1] = mod_centered(odd);
        range_add(trace == NULL ? NULL : &trace->ntt32_min,
                  trace == NULL ? NULL : &trace->ntt32_max, out[2 * k]);
        range_add(trace == NULL ? NULL : &trace->ntt32_min,
                  trace == NULL ? NULL : &trace->ntt32_max, out[2 * k + 1]);
    }
}

static void ntt32_c(int16_t out[32], const int16_t in[32],
                    gt_range_trace *trace)
{
    const int omega32 = mod_pow(GT_OMEGA96, 3);
    for (size_t k = 0; k < 32; ++k) {
        int64_t sum = 0;
        for (size_t n = 0; n < 32; ++n)
            sum += (int64_t)in[n] * mod_pow(omega32, n * k);
        out[k] = mod_centered(sum);
        range_add(trace == NULL ? NULL : &trace->ntt32_min,
                  trace == NULL ? NULL : &trace->ntt32_max, out[k]);
    }
}

void gt_ref_ntt_variant(poly *r, gt_n32_variant variant,
                        gt_range_trace *trace)
{
    poly input = *r;
    int16_t branch_coeffs[2][4][96];
    int16_t matrix[3][32];
    range_init(trace);

    for (size_t n = 0; n < 96; ++n) {
        for (size_t degree = 0; degree < 4; ++degree) {
            const size_t i = 4 * n + degree;
            const int low = input.coeffs[i];
            const int high = input.coeffs[i + NTRUPLUS_N / 2];
            const int top0 = low + GT_PHI_CENTERED * high;
            const int top1 = low + GT_PHI_INV_CENTERED * high;
            range_add(trace == NULL ? NULL : &trace->top_min,
                      trace == NULL ? NULL : &trace->top_max, top0);
            range_add(trace == NULL ? NULL : &trace->top_min,
                      trace == NULL ? NULL : &trace->top_max, top1);
            branch_coeffs[0][degree][n] = mod_centered(
                (int64_t)top0 * gt_preweight[0][n]);
            branch_coeffs[1][degree][n] = mod_centered(
                (int64_t)top1 * gt_preweight[1][n]);
            range_add(trace == NULL ? NULL : &trace->preweight_min,
                      trace == NULL ? NULL : &trace->preweight_max,
                      branch_coeffs[0][degree][n]);
            range_add(trace == NULL ? NULL : &trace->preweight_min,
                      trace == NULL ? NULL : &trace->preweight_max,
                      branch_coeffs[1][degree][n]);
        }
    }

    const int omega3 = mod_pow(GT_OMEGA96, 32);
    for (size_t branch = 0; branch < 2; ++branch) {
        for (size_t degree = 0; degree < 4; ++degree) {
            for (size_t n32 = 0; n32 < 32; ++n32) {
                for (size_t k3 = 0; k3 < 3; ++k3) {
                    int64_t sum = 0;
                    for (size_t n3 = 0; n3 < 3; ++n3) {
                        const size_t n = gt_input_crt[32 * n3 + n32];
                        sum += (int64_t)branch_coeffs[branch][degree][n]
                               * mod_pow(omega3, n3 * k3);
                    }
                    matrix[k3][n32] = mod_centered(sum);
                    range_add(trace == NULL ? NULL : &trace->dft3_min,
                              trace == NULL ? NULL : &trace->dft3_max,
                              matrix[k3][n32]);
                }
            }

            for (size_t k3 = 0; k3 < 3; ++k3) {
                int16_t row[32];
                if (variant == GT_N32_C)
                    ntt32_c(row, matrix[k3], trace);
                else
                    ntt32_b(row, matrix[k3], variant, trace);
                for (size_t k32 = 0; k32 < 32; ++k32) {
                    const size_t component = branch * 96 + k3 * 32 + k32;
                    r->coeffs[gt_word(component, degree)] = row[k32];
                    range_add(trace == NULL ? NULL : &trace->output_min,
                              trace == NULL ? NULL : &trace->output_max,
                              row[k32]);
                }
            }
        }
    }
}

void gt_poly_ntt_canonical(poly *r)
{
    gt_poly_ntt_avx2_b1(r);
}

void gt_poly_ntt(poly *r)
{
    gt_poly_ntt_canonical(r);
}

void gt_poly_ntt_lazy(poly *r)
{
    /* Until a lazy proof is selected, the lazy entry is conservatively
     * canonical and therefore satisfies every proposed lazy bound. */
    gt_poly_ntt_canonical(r);
}

static void quartic_mul(int16_t r[4], const int16_t a[4],
                        const int16_t b[4], int alpha)
{
    const int64_t c0 = (int64_t)a[0] * b[0] + (int64_t)alpha *
        ((int64_t)a[1] * b[3] + (int64_t)a[2] * b[2] + (int64_t)a[3] * b[1]);
    const int64_t c1 = (int64_t)a[0] * b[1] + (int64_t)a[1] * b[0] +
        (int64_t)alpha * ((int64_t)a[2] * b[3] + (int64_t)a[3] * b[2]);
    const int64_t c2 = (int64_t)a[0] * b[2] + (int64_t)a[1] * b[1] +
        (int64_t)a[2] * b[0] + (int64_t)alpha * a[3] * b[3];
    const int64_t c3 = (int64_t)a[0] * b[3] + (int64_t)a[1] * b[2] +
        (int64_t)a[2] * b[1] + (int64_t)a[3] * b[0];
    r[0] = mod_centered(c0);
    r[1] = mod_centered(c1);
    r[2] = mod_centered(c2);
    r[3] = mod_centered(c3);
}

void gt_ref_poly_basemul(poly *r, const poly *a, const poly *b)
{
    poly out;
    for (size_t component = 0; component < 192; ++component) {
        int16_t aa[4];
        int16_t bb[4];
        int16_t cc[4];
        for (size_t degree = 0; degree < 4; ++degree) {
            aa[degree] = a->coeffs[gt_word(component, degree)];
            bb[degree] = b->coeffs[gt_word(component, degree)];
        }
        quartic_mul(cc, aa, bb, gt_alpha[component]);
        for (size_t degree = 0; degree < 4; ++degree)
            out.coeffs[gt_word(component, degree)] = cc[degree];
    }
    *r = out;
}

static void quartic_pow(int16_t r[4], const int16_t a[4], int alpha,
                        uint64_t exponent)
{
    int16_t result[4] = {1, 0, 0, 0};
    int16_t base[4] = {a[0], a[1], a[2], a[3]};
    while (exponent != 0) {
        int16_t temp[4];
        if (exponent & 1U) {
            quartic_mul(temp, result, base, alpha);
            memcpy(result, temp, sizeof result);
        }
        quartic_mul(temp, base, base, alpha);
        memcpy(base, temp, sizeof base);
        exponent >>= 1;
    }
    memcpy(r, result, 4 * sizeof *r);
}

int gt_ref_poly_baseinv(poly *r, const poly *a)
{
    const uint64_t field_order = (uint64_t)NTRUPLUS_Q * NTRUPLUS_Q
                               * NTRUPLUS_Q * NTRUPLUS_Q;
    poly out;
    unsigned failure = 0;

    for (size_t component = 0; component < 192; ++component) {
        int16_t aa[4];
        int16_t inv[4];
        unsigned nonzero = 0;
        for (size_t degree = 0; degree < 4; ++degree) {
            aa[degree] = mod_centered(a->coeffs[gt_word(component, degree)]);
            nonzero |= (unsigned)(aa[degree] != 0);
        }
        failure |= nonzero ^ 1U;
        quartic_pow(inv, aa, gt_alpha[component], field_order - 2);
        for (size_t degree = 0; degree < 4; ++degree)
            out.coeffs[gt_word(component, degree)] = inv[degree];
    }

    const uint16_t success_mask = (uint16_t)(failure - 1U);
    for (size_t i = 0; i < NTRUPLUS_N; ++i)
        out.coeffs[i] = (int16_t)((uint16_t)out.coeffs[i] & success_mask);
    *r = out;
    return failure != 0;
}

void gt_ref_poly_invntt_scale(poly *r)
{
    poly frequency = *r;
    int16_t branch_coeffs[2][4][96];
    const int omega32 = mod_pow(GT_OMEGA96, 3);
    const int omega3 = mod_pow(GT_OMEGA96, 32);
    const int inv32 = mod_pow(32, NTRUPLUS_Q - 2);
    const int inv3 = mod_pow(3, NTRUPLUS_Q - 2);

    for (size_t branch = 0; branch < 2; ++branch) {
        for (size_t degree = 0; degree < 4; ++degree) {
            int16_t matrix[3][32];
            int16_t after32[3][32];
            for (size_t k3 = 0; k3 < 3; ++k3)
                for (size_t k32 = 0; k32 < 32; ++k32) {
                    const size_t component = branch * 96 + k3 * 32 + k32;
                    matrix[k3][k32] = frequency.coeffs[gt_word(component, degree)];
                }

            for (size_t k3 = 0; k3 < 3; ++k3)
                for (size_t n32 = 0; n32 < 32; ++n32) {
                    int64_t sum = 0;
                    for (size_t k32 = 0; k32 < 32; ++k32)
                        sum += (int64_t)matrix[k3][k32]
                             * mod_pow(omega32, NTRUPLUS_Q - 1 - n32 * k32);
                    after32[k3][n32] = mod_centered(sum * inv32);
                }

            for (size_t n3 = 0; n3 < 3; ++n3)
                for (size_t n32 = 0; n32 < 32; ++n32) {
                    int64_t sum = 0;
                    for (size_t k3 = 0; k3 < 3; ++k3)
                        sum += (int64_t)after32[k3][n32]
                             * mod_pow(omega3, NTRUPLUS_Q - 1 - n3 * k3);
                    const size_t n = gt_input_crt[32 * n3 + n32];
                    const int F = branch == 0 ? 2 : 22;
                    branch_coeffs[branch][degree][n] = mod_centered(
                        sum * inv3 * mod_pow(F, n));
                }
        }
    }

    const int inv_delta = mod_pow(GT_PHI_CENTERED - GT_PHI_INV_CENTERED,
                                  NTRUPLUS_Q - 2);
    for (size_t n = 0; n < 96; ++n) {
        for (size_t degree = 0; degree < 4; ++degree) {
            const int u = branch_coeffs[0][degree][n];
            const int v = branch_coeffs[1][degree][n];
            const int high = mod_centered((int64_t)(u - v) * inv_delta);
            const int low = mod_centered((int64_t)u
                                        - (int64_t)GT_PHI_CENTERED * high);
            r->coeffs[4 * n + degree] = (int16_t)low;
            r->coeffs[NTRUPLUS_N / 2 + 4 * n + degree] = (int16_t)high;
        }
    }
}

void gt_poly_tobytes(uint8_t out[NTRUPLUS_POLYBYTES], const poly *a)
{
    uint16_t ordered[NTRUPLUS_N];
    for (size_t official = 0; official < 192; ++official) {
        const size_t component = gt_official_to_gt[official];
        for (size_t degree = 0; degree < 4; ++degree) {
            const int16_t value = a->coeffs[gt_word(component, degree)];
            const uint16_t sign = (uint16_t)value >> 15;
            ordered[4 * official + degree] = (uint16_t)(
                value + (int)(sign * NTRUPLUS_Q));
        }
    }
    for (size_t i = 0; i < NTRUPLUS_N / 2; ++i) {
        const uint16_t a0 = ordered[2 * i];
        const uint16_t a1 = ordered[2 * i + 1];
        out[3 * i] = (uint8_t)a0;
        out[3 * i + 1] = (uint8_t)((a0 >> 8) | (a1 << 4));
        out[3 * i + 2] = (uint8_t)(a1 >> 4);
    }
}

int gt_poly_frombytes(poly *r, const uint8_t in[NTRUPLUS_POLYBYTES])
{
    uint16_t ordered[NTRUPLUS_N];
    unsigned failure = 0;
    for (size_t i = 0; i < NTRUPLUS_N / 2; ++i) {
        ordered[2 * i] = (uint16_t)(in[3 * i]
            | ((uint16_t)(in[3 * i + 1] & 0x0fU) << 8));
        ordered[2 * i + 1] = (uint16_t)((in[3 * i + 1] >> 4)
            | ((uint16_t)in[3 * i + 2] << 4));
        failure |= (unsigned)(ordered[2 * i] >= NTRUPLUS_Q);
        failure |= (unsigned)(ordered[2 * i + 1] >= NTRUPLUS_Q);
    }
    for (size_t official = 0; official < 192; ++official) {
        const size_t component = gt_official_to_gt[official];
        for (size_t degree = 0; degree < 4; ++degree) {
            const uint16_t value = ordered[4 * official + degree];
            const uint16_t above_center = (uint16_t)(value > 1728U);
            const int16_t centered_value = (int16_t)(value
                - (uint16_t)(NTRUPLUS_Q * above_center));
            r->coeffs[gt_word(component, degree)] = failure == 0
                ? centered_value : (int16_t)value;
        }
    }
    return failure != 0;
}

int gt_ntt_equal_canonical(const poly *a, const poly *b)
{
    uint16_t difference = 0;
    for (size_t i = 0; i < NTRUPLUS_N; ++i)
        difference |= (uint16_t)(a->coeffs[i] ^ b->coeffs[i]);
    return difference == 0;
}

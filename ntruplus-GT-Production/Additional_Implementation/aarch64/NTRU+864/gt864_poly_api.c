#include "gt864_poly_api.h"
#include "gt864_fr0_basemul.h"
#include "gt864_fr0_basemul_d1.h"
#include "gt864_fr0_inverse_asm.h"
#include "gt864_fr0_to_official_map.h"

#include <arm_neon.h>
#include <stddef.h>

void gt864_forward_poly_ntt_p41_k1_kem_only(int16_t out[864],
                                            const int16_t in[864]);

static void official_to_fr0(poly *fr0, const poly *official)
{
    for (size_t i = 0; i < NTRUPLUS_N; i++)
        fr0->coeffs[gt864_fr0_for_official[i]] = official->coeffs[i];
}

/*
 * Exact for every signed halfword: SQRDMULH(x,9) estimates x/q and leaves a
 * residue in [-3291,3291].  One masked add therefore produces [0,q-1].
 * M5R-D's closed [-25569,25569] live-out is strictly inside this domain.
 */
static int16x8_t reduce_nonnegative(int16x8_t value)
{
    const int16x8_t reciprocal = vdupq_n_s16(9);
    const int16x8_t modulus = vdupq_n_s16(NTRUPLUS_Q);
    const int16x8_t zero = vdupq_n_s16(0);
    int16x8_t quotient = vqrdmulhq_s16(value, reciprocal);
    value = vmlsq_s16(value, quotient, modulus);
    return vaddq_s16(value, vandq_s16(
        vreinterpretq_s16_u16(vcltq_s16(value, zero)), modulus));
}

static int16x8_t reduce_centered(int16x8_t value)
{
    const int16x8_t modulus = vdupq_n_s16(NTRUPLUS_Q);
    const int16x8_t half = vdupq_n_s16(NTRUPLUS_Q / 2);
    value = reduce_nonnegative(value);
    return vsubq_s16(value, vandq_s16(
        vreinterpretq_s16_u16(vcgtq_s16(value, half)), modulus));
}

static void fr0_to_official_nonnegative(poly *official, const poly *fr0)
{
    for (size_t i = 0; i < NTRUPLUS_N; i += 8) {
        int16_t gathered[8];
        for (size_t lane = 0; lane < 8; lane++)
            gathered[lane] = fr0->coeffs[gt864_fr0_for_official[i + lane]];
        vst1q_s16(official->coeffs + i,
                  reduce_nonnegative(vld1q_s16(gathered)));
    }
}

static void fr0_to_official_centered(poly *official, const poly *fr0)
{
    for (size_t i = 0; i < NTRUPLUS_N; i += 8) {
        int16_t gathered[8];
        for (size_t lane = 0; lane < 8; lane++)
            gathered[lane] = fr0->coeffs[gt864_fr0_for_official[i + lane]];
        vst1q_s16(official->coeffs + i,
                  reduce_centered(vld1q_s16(gathered)));
    }
}

static void gt_ntt(poly *r, const poly *a)
{
    gt864_forward_poly_ntt_p41_k1_kem_only(r->coeffs, a->coeffs);
}

static void gt_invntt(poly *r, const poly *a)
{
    int16_t scratch[896] __attribute__((aligned(16))) = {0};
    gt864_fr0_inverse_ntt9_asm(scratch, a->coeffs);
    gt864_fr0_inverse_finish_asm(r->coeffs, scratch);
    for (size_t i = 0; i < NTRUPLUS_N; i += 8)
        vst1q_s16(r->coeffs + i,
                  reduce_centered(vld1q_s16(r->coeffs + i)));
}

static int gt_baseinv(poly *r, const poly *a)
{
    poly official_a, official_r;
    int result;
    fr0_to_official_centered(&official_a, a);
    result = poly_baseinv(&official_r, &official_a);
    official_to_fr0(r, &official_r);
    return result;
}

static void gt_tobytes(uint8_t *r, const poly *a)
{
    poly official;
    fr0_to_official_nonnegative(&official, a);
    poly_tobytes(r, &official);
}

static void gt_frombytes(poly *r, const uint8_t *a)
{
    poly official;
    poly_frombytes(&official, a);
    official_to_fr0(r, &official);
}

#define DEFINE_SHARED_WRAPPERS(prefix)                                      \
    void prefix##_poly_ntt(poly *r, const poly *a) { gt_ntt(r, a); }       \
    void prefix##_poly_invntt(poly *r, const poly *a) { gt_invntt(r, a); } \
    int prefix##_poly_baseinv(poly *r, const poly *a)                       \
    { return gt_baseinv(r, a); }                                            \
    void prefix##_poly_tobytes(uint8_t *r, const poly *a)                   \
    { gt_tobytes(r, a); }                                                   \
    void prefix##_poly_frombytes(poly *r, const uint8_t *a)                 \
    { gt_frombytes(r, a); }

DEFINE_SHARED_WRAPPERS(gt_old)
DEFINE_SHARED_WRAPPERS(gt_d1)

#ifdef GT864_P2_EXPORT_INTERNALS
void gt_p2_official_to_fr0(poly *r, const poly *a);
void gt_p2_fr0_to_official_raw(poly *r, const poly *a);
void gt_p2_fr0_to_official_nonnegative(poly *r, const poly *a);
void gt_p2_fr0_to_official_centered(poly *r, const poly *a);
void gt_p2_normalize_nonnegative(poly *r, const poly *a);
void gt_p2_normalize_centered(poly *r, const poly *a);
void gt_p2_inverse_raw(poly *r, const poly *a);

void gt_p2_official_to_fr0(poly *r, const poly *a)
{
    official_to_fr0(r, a);
}

void gt_p2_fr0_to_official_raw(poly *r, const poly *a)
{
    for (size_t i = 0; i < NTRUPLUS_N; i++)
        r->coeffs[i] = a->coeffs[gt864_fr0_for_official[i]];
}

void gt_p2_fr0_to_official_nonnegative(poly *r, const poly *a)
{
    fr0_to_official_nonnegative(r, a);
}

void gt_p2_fr0_to_official_centered(poly *r, const poly *a)
{
    fr0_to_official_centered(r, a);
}

void gt_p2_normalize_nonnegative(poly *r, const poly *a)
{
    for (size_t i = 0; i < NTRUPLUS_N; i += 8)
        vst1q_s16(r->coeffs + i,
                  reduce_nonnegative(vld1q_s16(a->coeffs + i)));
}

void gt_p2_normalize_centered(poly *r, const poly *a)
{
    for (size_t i = 0; i < NTRUPLUS_N; i += 8)
        vst1q_s16(r->coeffs + i,
                  reduce_centered(vld1q_s16(a->coeffs + i)));
}

void gt_p2_inverse_raw(poly *r, const poly *a)
{
    int16_t scratch[896] __attribute__((aligned(16))) = {0};
    gt864_fr0_inverse_ntt9_asm(scratch, a->coeffs);
    gt864_fr0_inverse_finish_asm(r->coeffs, scratch);
}
#endif

void gt_old_poly_basemul(poly *r, const poly *a, const poly *b)
{
    gt864_fr0_basemul_neon(r->coeffs, a->coeffs, b->coeffs);
}

void gt_old_poly_basemul_add(poly *r, const poly *a, const poly *b,
                            const poly *c)
{
    gt864_fr0_basemul_add_neon(r->coeffs, a->coeffs, b->coeffs, c->coeffs);
}

void gt_d1_poly_basemul(poly *r, const poly *a, const poly *b)
{
    gt864_fr0_basemul_d1_neon(r->coeffs, a->coeffs, b->coeffs);
}

void gt_d1_poly_basemul_add(poly *r, const poly *a, const poly *b,
                           const poly *c)
{
    gt864_fr0_basemul_add_d1_neon(r->coeffs, a->coeffs, b->coeffs, c->coeffs);
}

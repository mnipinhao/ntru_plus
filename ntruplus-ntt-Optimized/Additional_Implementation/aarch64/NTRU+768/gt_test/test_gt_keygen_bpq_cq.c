#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt/keygen_bpq_cq.h"

#define NCASES 1000

int poly_baseinv_scaled_r(poly *r, const poly *a);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);
uint64_t gt_keygen_bpq_cq_abi_sentinel(gt_bpq_poly *bpq,
                                        gt_cq_poly *cq_inv,
                                        gt_cq_poly *cq_product,
                                        uint8_t *bytes,
                                        const poly *small);

static uint32_t next_u32(uint32_t *state)
{
    *state = *state * 1664525u + 1013904223u;
    return *state;
}

static void fill_small(poly *a, uint32_t *state)
{
    size_t i;

    for (i = 0; i < NTRUPLUS_N; i++)
        a->coeffs[i] = (int16_t)(next_u32(state) % 3u) - 1;
}

static int compare_bytes(const uint8_t *a, const uint8_t *b)
{
    return memcmp(a, b, NTRUPLUS_POLYBYTES) != 0;
}

int main(void)
{
    poly small_f, small_g;
    poly old_f, old_g, old_finv, old_ginv, old_h, old_hinv;
    gt_bpq_poly new_f, new_g;
    gt_cq_poly new_finv, new_ginv, new_h, new_hinv;
    uint8_t old_bytes[NTRUPLUS_POLYBYTES];
    uint8_t new_bytes[NTRUPLUS_POLYBYTES];
    uint32_t state = 1;
    uint64_t mismatches = 0;
    uint64_t invertibility_mismatches = 0;
    uint64_t abi_mask;
    int tested = 0;
    int i;

    for (i = 0; i < NCASES; i++) {
        int old_f_ret, new_f_ret, old_g_ret, new_g_ret;

        fill_small(&small_f, &state);
        fill_small(&small_g, &state);

        poly_triple(&old_f, &small_f);
        old_f.coeffs[0] += 1;
        poly_ntt(&old_f, &old_f);
        gt_keygen_blockmajor_to_bpq(&new_f, &old_f);

        poly_triple(&old_g, &small_g);
        poly_ntt(&old_g, &old_g);
        gt_keygen_blockmajor_to_bpq(&new_g, &old_g);

        poly_tobytes_gt_canonical_p1(old_bytes, &old_f);
        gt_keygen_tobytes_bpq_p1(new_bytes, &new_f);
        mismatches += compare_bytes(old_bytes, new_bytes);

        old_f_ret = poly_baseinv_scaled_r(&old_finv, &old_f);
        new_f_ret = gt_keygen_baseinv_bpq_to_cq_scaled_r(&new_finv, &new_f);
        old_g_ret = poly_baseinv_scaled_r(&old_ginv, &old_g);
        new_g_ret = gt_keygen_baseinv_bpq_to_cq_scaled_r(&new_ginv, &new_g);
        invertibility_mismatches += old_f_ret != new_f_ret;
        invertibility_mismatches += old_g_ret != new_g_ret;
        if (old_f_ret || new_f_ret || old_g_ret || new_g_ret)
            continue;

        poly_basemul_scaled_r_input(&old_h, &old_g, &old_finv);
        gt_keygen_basemul_bpq_cq_to_cq_scaled_r(
            &new_h, &new_g, &new_finv);
        poly_tobytes_gt_canonical_p1(old_bytes, &old_h);
        gt_keygen_tobytes_cq(new_bytes, &new_h);
        mismatches += compare_bytes(old_bytes, new_bytes);

        poly_basemul_scaled_r_input(&old_hinv, &old_f, &old_ginv);
        gt_keygen_basemul_bpq_cq_to_cq_scaled_r(
            &new_hinv, &new_f, &new_ginv);
        poly_tobytes_gt_canonical_p1(old_bytes, &old_hinv);
        gt_keygen_tobytes_cq(new_bytes, &new_hinv);
        mismatches += compare_bytes(old_bytes, new_bytes);
        tested++;
    }

    abi_mask = gt_keygen_bpq_cq_abi_sentinel(
        &new_f, &new_finv, &new_h, new_bytes, &small_f);
    printf("bpq_cq_cases=%d usable=%d mismatches=%llu "
           "invertibility_mismatches=%llu abi_mask=0x%llx\n",
           NCASES, tested, (unsigned long long)mismatches,
           (unsigned long long)invertibility_mismatches,
           (unsigned long long)abi_mask);
    return mismatches != 0 || invertibility_mismatches != 0 || abi_mask != 0;
}

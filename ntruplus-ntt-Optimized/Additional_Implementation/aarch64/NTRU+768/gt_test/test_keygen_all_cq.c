#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "experiments/keygen_all_cq/keygen_all_cq.h"

#define NCASES 1000

uint64_t gt_experiment_keygen_all_cq_abi_sentinel(
    gt_bpq_poly *bpq, gt_cq_poly *cq, gt_cq_poly *cq_inv,
    gt_cq_poly *cq_product, uint8_t *bytes);

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

static int16_t centered_mod_q(int16_t value)
{
    int32_t reduced = value % NTRUPLUS_Q;

    if (reduced > NTRUPLUS_Q / 2)
        reduced -= NTRUPLUS_Q;
    if (reduced < -NTRUPLUS_Q / 2)
        reduced += NTRUPLUS_Q;
    return (int16_t)reduced;
}

static uint64_t compare_cq_mod_q(const gt_cq_poly *a,
                                 const gt_cq_poly *b)
{
    uint64_t mismatches = 0;
    size_t i;

    for (i = 0; i < NTRUPLUS_N; i++)
        mismatches += centered_mod_q(a->storage.coeffs[i]) !=
                      centered_mod_q(b->storage.coeffs[i]);
    return mismatches;
}

static int max_abs_cq(const gt_cq_poly *a)
{
    int max_abs = 0;
    size_t i;

    for (i = 0; i < NTRUPLUS_N; i++) {
        int value = a->storage.coeffs[i];
        int abs_value = value < 0 ? -value : value;

        if (abs_value > max_abs)
            max_abs = abs_value;
    }
    return max_abs;
}

int main(void)
{
    poly small_f, small_g;
    poly block_f, block_g;
    gt_bpq_poly bpq_f, bpq_g;
    gt_cq_poly cq_f, cq_g;
    gt_cq_poly mixed_finv, mixed_ginv, mixed_h, mixed_hinv;
    gt_cq_poly all_cq_finv, all_cq_ginv, all_cq_h, all_cq_hinv;
    uint8_t reference_bytes[NTRUPLUS_POLYBYTES];
    uint8_t candidate_bytes[NTRUPLUS_POLYBYTES];
    uint32_t state = 1;
    uint64_t pack_mismatches = 0;
    uint64_t invertibility_mismatches = 0;
    uint64_t product_mismatches = 0;
    uint64_t product_mod_q_mismatches = 0;
    int mixed_product_max_abs = 0;
    int all_cq_product_max_abs = 0;
    uint64_t abi_mask;
    int usable = 0;
    int i;

    for (i = 0; i < NCASES; i++) {
        int mixed_f_ret, mixed_g_ret;
        int all_cq_f_ret, all_cq_g_ret;

        fill_small(&small_f, &state);
        fill_small(&small_g, &state);

        poly_triple(&block_f, &small_f);
        block_f.coeffs[0] += 1;
        poly_ntt(&block_f, &block_f);
        gt_keygen_blockmajor_to_bpq(&bpq_f, &block_f);
        gt_experiment_keygen_bpq_to_cq(&cq_f, &bpq_f);

        poly_triple(&block_g, &small_g);
        poly_ntt(&block_g, &block_g);
        gt_keygen_blockmajor_to_bpq(&bpq_g, &block_g);
        gt_experiment_keygen_bpq_to_cq(&cq_g, &bpq_g);

        poly_tobytes_gt_canonical_p1(reference_bytes, &block_f);
        gt_keygen_tobytes_cq(candidate_bytes, &cq_f);
        pack_mismatches += compare_bytes(reference_bytes, candidate_bytes);

        poly_tobytes_gt_canonical_p1(reference_bytes, &block_g);
        gt_keygen_tobytes_cq(candidate_bytes, &cq_g);
        pack_mismatches += compare_bytes(reference_bytes, candidate_bytes);

        mixed_f_ret = gt_keygen_baseinv_bpq_to_cq_scaled_r(
            &mixed_finv, &bpq_f);
        all_cq_f_ret = gt_experiment_keygen_baseinv_cq_to_cq_scaled_r(
            &all_cq_finv, &cq_f);
        mixed_g_ret = gt_keygen_baseinv_bpq_to_cq_scaled_r(
            &mixed_ginv, &bpq_g);
        all_cq_g_ret = gt_experiment_keygen_baseinv_cq_to_cq_scaled_r(
            &all_cq_ginv, &cq_g);
        invertibility_mismatches += mixed_f_ret != all_cq_f_ret;
        invertibility_mismatches += mixed_g_ret != all_cq_g_ret;
        if (mixed_f_ret || all_cq_f_ret || mixed_g_ret || all_cq_g_ret)
            continue;

        gt_keygen_tobytes_cq(reference_bytes, &mixed_finv);
        gt_keygen_tobytes_cq(candidate_bytes, &all_cq_finv);
        pack_mismatches += compare_bytes(reference_bytes, candidate_bytes);
        gt_keygen_tobytes_cq(reference_bytes, &mixed_ginv);
        gt_keygen_tobytes_cq(candidate_bytes, &all_cq_ginv);
        pack_mismatches += compare_bytes(reference_bytes, candidate_bytes);

        gt_keygen_basemul_bpq_cq_to_cq_scaled_r(
            &mixed_h, &bpq_g, &mixed_finv);
        gt_experiment_keygen_basemul_cq_cq_to_cq_scaled_r(
            &all_cq_h, &cq_g, &all_cq_finv);
        gt_keygen_tobytes_cq(reference_bytes, &mixed_h);
        gt_keygen_tobytes_cq(candidate_bytes, &all_cq_h);
        product_mismatches += compare_bytes(reference_bytes,
                                            candidate_bytes);
        product_mod_q_mismatches += compare_cq_mod_q(&mixed_h, &all_cq_h);
        if (max_abs_cq(&mixed_h) > mixed_product_max_abs)
            mixed_product_max_abs = max_abs_cq(&mixed_h);
        if (max_abs_cq(&all_cq_h) > all_cq_product_max_abs)
            all_cq_product_max_abs = max_abs_cq(&all_cq_h);

        gt_keygen_basemul_bpq_cq_to_cq_scaled_r(
            &mixed_hinv, &bpq_f, &mixed_ginv);
        gt_experiment_keygen_basemul_cq_cq_to_cq_scaled_r(
            &all_cq_hinv, &cq_f, &all_cq_ginv);
        gt_keygen_tobytes_cq(reference_bytes, &mixed_hinv);
        gt_keygen_tobytes_cq(candidate_bytes, &all_cq_hinv);
        product_mismatches += compare_bytes(reference_bytes,
                                            candidate_bytes);
        product_mod_q_mismatches += compare_cq_mod_q(&mixed_hinv,
                                                      &all_cq_hinv);
        if (max_abs_cq(&mixed_hinv) > mixed_product_max_abs)
            mixed_product_max_abs = max_abs_cq(&mixed_hinv);
        if (max_abs_cq(&all_cq_hinv) > all_cq_product_max_abs)
            all_cq_product_max_abs = max_abs_cq(&all_cq_hinv);
        usable++;
    }

    abi_mask = gt_experiment_keygen_all_cq_abi_sentinel(
        &bpq_f, &cq_f, &all_cq_finv, &all_cq_h, candidate_bytes);
    printf("keygen_all_cq_cases=%d usable=%d pack_mismatches=%llu "
           "invertibility_mismatches=%llu product_mismatches=%llu "
           "product_mod_q_mismatches=%llu mixed_max_abs=%d "
           "all_cq_max_abs=%d abi_mask=0x%llx\n",
           NCASES, usable, (unsigned long long)pack_mismatches,
           (unsigned long long)invertibility_mismatches,
           (unsigned long long)product_mismatches,
           (unsigned long long)product_mod_q_mismatches,
           mixed_product_max_abs, all_cq_product_max_abs,
           (unsigned long long)abi_mask);
    return pack_mismatches != 0 || invertibility_mismatches != 0 ||
           product_mismatches != 0 || product_mod_q_mismatches != 0 ||
           abi_mask != 0;
}

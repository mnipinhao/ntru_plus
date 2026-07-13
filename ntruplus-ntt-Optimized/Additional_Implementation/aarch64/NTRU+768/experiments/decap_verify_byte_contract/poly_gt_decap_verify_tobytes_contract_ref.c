#include <stdint.h>
#include <stddef.h>

#include "params.h"
#include "poly.h"

void gt_decap_verify_basemul_tobytes_contract_ref(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv);
void gt_decap_verify_basemul_tobytes_contract_c_candidate(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv);

static uint16_t gt_tobytes_lane_rep(int16_t coeff)
{
    uint16_t lane = (uint16_t)coeff;

    if (coeff < 0)
    {
        lane = (uint16_t)(lane + NTRUPLUS_Q);
    }

    return lane;
}

static void gt_poly_tobytes_c_exact(uint8_t out[NTRUPLUS_POLYBYTES],
                                    const poly *a)
{
    static const uint8_t public_to_memory[64] = {
        0,  8,  16, 24, 32, 40, 48, 56, 1,  9,  17, 25, 33, 41, 49, 57,
        2,  10, 18, 26, 34, 42, 50, 58, 3,  11, 19, 27, 35, 43, 51, 59,
        4,  12, 20, 28, 36, 44, 52, 60, 5,  13, 21, 29, 37, 45, 53, 61,
        6,  14, 22, 30, 38, 46, 54, 62, 7,  15, 23, 31, 39, 47, 55, 63,
    };
    size_t chunk_idx;

    for (chunk_idx = 0; chunk_idx < NTRUPLUS_N / 64; chunk_idx++)
    {
        size_t pair_idx;

        for (pair_idx = 0; pair_idx < 32; pair_idx++)
        {
            const size_t out_idx = 96 * chunk_idx + 3 * pair_idx;
            const size_t mem_base = 64 * chunk_idx;
            const uint16_t c0 = gt_tobytes_lane_rep(
                a->coeffs[mem_base + public_to_memory[2 * pair_idx + 0]]);
            const uint16_t c1 = gt_tobytes_lane_rep(
                a->coeffs[mem_base + public_to_memory[2 * pair_idx + 1]]);

            out[out_idx + 0] = (uint8_t)c0;
            out[out_idx + 1] = (uint8_t)((c0 >> 8) | (c1 << 4));
            out[out_idx + 2] = (uint8_t)(c1 >> 4);
        }
    }
}

/*
 * Reference-only contract helper for the decap verification product:
 *
 *   poly_basemul(&r2, c_minus_m2, hinv);
 *   poly_tobytes(out, &r2);
 *
 * It fixes the byte-output API for future optimized candidates.  It is not a
 * replacement for generic poly_basemul and does not expose arithmetic output.
 */
void gt_decap_verify_basemul_tobytes_contract_ref(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv)
{
    poly r2;

    poly_basemul(&r2, c_minus_m2, hinv);
    poly_tobytes(out, &r2);
}

/*
 * C-level byte-output candidate.  This is not the final optimized direct
 * arithmetic reducer: it still uses the arithmetic-correct poly_basemul result
 * as an internal temporary, then emits bytes through a C mirror of pack.s.
 * Keeping the output as bytes fixes the gated call shape for the next reducer
 * prototype without changing generic poly_basemul.
 */
void gt_decap_verify_basemul_tobytes_contract_c_candidate(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv)
{
    poly r2;

    poly_basemul(&r2, c_minus_m2, hinv);
    gt_poly_tobytes_c_exact(out, &r2);
}

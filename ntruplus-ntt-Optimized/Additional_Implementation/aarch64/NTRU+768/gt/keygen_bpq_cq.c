#include <stdint.h>
#include <string.h>

#include "gt/keygen_bpq_cq.h"

#if NTRUPLUS_N != 768
#error "The BPQ/CQ keygen backend is specialized for NTRU+768"
#endif

#define GT_KEYGEN_BPQ_GROUPS 24

/*
 * The first Stage345 block uses the physical store order selected by the
 * production NTT32 register allocation. Later blocks use linear k32 order.
 */
static const uint8_t gt_keygen_bpq_slot_for_k32[32] = {
    3, 7, 1, 0, 6, 2, 5, 4,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 27, 28, 29, 30, 31,
};

void gt_keygen_blockmajor_to_bpq(gt_bpq_poly *out_bpq,
                                 const poly *in_blockmajor)
{
    int row;
    int k32;

    for (row = 0; row < 3; row++) {
        for (k32 = 0; k32 < 32; k32++) {
            const int physical_j = (32 * row + 3 * k32) % 96;
            const int bpq_slot =
                32 * row + gt_keygen_bpq_slot_for_k32[k32];
            int16_t *dst = &out_bpq->storage.coeffs[8 * bpq_slot];
            const int16_t *src0 =
                &in_blockmajor->coeffs[4 * physical_j];
            const int16_t *src1 =
                &in_blockmajor->coeffs[384 + 4 * physical_j];

            memcpy(dst, src0, 4 * sizeof(int16_t));
            memcpy(dst + 4, src1, 4 * sizeof(int16_t));
        }
    }
}

void gt_keygen_baseinv_bpq_prepare(int16_t *numerator, int16_t *den,
                                    const int16_t *in_bpq);
int gt_keygen_baseinv_hier_k8(int16_t *den);
void gt_keygen_baseinv_cq_finish(int16_t *out_cq,
                                 const int16_t *numerator,
                                 const int16_t *den);

int gt_keygen_baseinv_bpq_to_cq_scaled_r(gt_cq_poly *out_cq,
                                          const gt_bpq_poly *in_bpq)
{
    int16_t den[GT_KEYGEN_BPQ_GROUPS * 8] __attribute__((aligned(16)));
    int16_t numerator[GT_KEYGEN_BPQ_GROUPS * 4 * 8]
        __attribute__((aligned(16)));

    gt_keygen_baseinv_bpq_prepare(numerator, den, in_bpq->storage.coeffs);
    if (gt_keygen_baseinv_hier_k8(den)) {
        memset(out_cq, 0, sizeof(*out_cq));
        return 1;
    }
    gt_keygen_baseinv_cq_finish(out_cq->storage.coeffs, numerator, den);
    return 0;
}

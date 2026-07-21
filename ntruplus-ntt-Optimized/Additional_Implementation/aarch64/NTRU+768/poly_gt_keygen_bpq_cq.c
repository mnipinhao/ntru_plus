#include <stdint.h>
#include <string.h>

#include "gt_keygen_bpq_cq.h"

#if NTRUPLUS_N != 768
#error "The BPQ/CQ keygen backend is specialized for NTRU+768"
#endif

#define GT_KEYGEN_BPQ_GROUPS 24

const int16_t gt_keygen_bpq_lambda8[GT_KEYGEN_BPQ_GROUPS][8]
    __attribute__((aligned(16))) = {
    {-183, 183, 1674, 1655, -1588, 1588, 1095, 779},
    {559, -559, -1674, -1655, -892, 892, -1095, -779},
    {-397, 397, 1059, -1059, 1221, -1221, -218, 218},
    {-223, 223, -1138, 1138, 294, -294, -732, 732},
    {242, -242, 1514, -1514, 22, -22, 1709, -1709},
    {432, -432, -1640, 1640, -275, 275, 1108, -1108},
    {437, -437, -1723, 1723, 354, -354, -1728, 1728},
    {-277, 277, -933, 933, -968, 968, 858, -858},
    {943, -943, -352, -443, 400, -400, -32, 274},
    {312, -312, 352, 443, -1543, 1543, 32, -274},
    {100, -100, -1660, 1660, -1248, 1248, -1408, 1408},
    {-1250, 1250, 8, -8, -1685, 1685, 315, -315},
    {1341, -1341, 1247, -1247, 1379, -1379, -1458, 1458},
    {-1206, 1206, -31, 31, -1681, 1681, 940, -940},
    {-1364, 1364, 1209, -1209, -124, 124, 1367, -1367},
    {-235, 235, 444, -444, 1550, -1550, -1531, 1531},
    {-760, 760, -1322, -1212, 1188, -1188, -1063, -1053},
    {-871, 871, 1322, 1212, -1022, 1022, 1063, 1053},
    {297, -297, 601, -601, 27, -27, 1626, -1626},
    {1473, -1473, 1130, -1130, 1391, -1391, 417, -417},
    {-1583, 1583, 696, -696, -1401, 1401, -251, 251},
    {774, -774, 1671, -1671, -1501, 1501, 1409, -1409},
    {927, -927, 514, -514, -230, 230, 361, -361},
    {512, -512, 489, -489, -582, 582, 673, -673},
};

void gt_keygen_baseinv_bpq_prepare(int16_t *numerator, int16_t *den,
                                    const int16_t *in_bpq);
int gt_keygen_baseinv_hier_k8(int16_t *den);
void gt_keygen_baseinv_cq_finish(int16_t *out_cq,
                                 const int16_t *numerator,
                                 const int16_t *den);

int gt_keygen_baseinv_bpq_to_cq_scaled_r(poly *out_cq,
                                          const poly *in_bpq)
{
    int16_t den[GT_KEYGEN_BPQ_GROUPS * 8] __attribute__((aligned(16)));
    int16_t numerator[GT_KEYGEN_BPQ_GROUPS * 4 * 8]
        __attribute__((aligned(16)));

    gt_keygen_baseinv_bpq_prepare(numerator, den, in_bpq->coeffs);
    if (gt_keygen_baseinv_hier_k8(den)) {
        memset(out_cq, 0, sizeof(*out_cq));
        return 1;
    }
    gt_keygen_baseinv_cq_finish(out_cq->coeffs, numerator, den);
    return 0;
}

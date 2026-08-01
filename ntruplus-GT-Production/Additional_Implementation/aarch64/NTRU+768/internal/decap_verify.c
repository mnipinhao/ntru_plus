#include <stdint.h>

#include "decap_verify.h"

void gt_decap_verify_predecoded_qsoa_to_bytes(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv_qsoa)
{
    poly result_qsoa;

    gt_decap_verify_pointwise(&result_qsoa, c_minus_m2, hinv_qsoa);
    qsoa_tobytes(out, &result_qsoa);
}

#include <stdint.h>

#include "gt/decap_backend.h"

void gt_decap_verify_to_bytes(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const uint8_t hinv_bytes[NTRUPLUS_POLYBYTES])
{
    poly hinv_qsoa;
    poly result_qsoa;

    poly_frombytes(&hinv_qsoa, hinv_bytes);
    gt_decap_verify_pointwise(&result_qsoa, c_minus_m2, &hinv_qsoa);
    poly_tobytes(out, &result_qsoa);
}

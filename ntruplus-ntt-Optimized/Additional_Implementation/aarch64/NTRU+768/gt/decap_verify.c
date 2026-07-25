#include <stdint.h>

#ifndef GT_DECAP_VERIFY_TO_BYTES_SYMBOL
#define GT_DECAP_VERIFY_TO_BYTES_SYMBOL gt_decap_verify_to_bytes
#endif
#ifndef GT_DECAP_VERIFY_POINTWISE_SYMBOL
#define GT_DECAP_VERIFY_POINTWISE_SYMBOL gt_decap_verify_pointwise
#endif

#include "gt/decap_backend.h"

void GT_DECAP_VERIFY_TO_BYTES_SYMBOL(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const uint8_t hinv_bytes[NTRUPLUS_POLYBYTES])
{
    poly hinv_qsoa;
    poly result_qsoa;

    poly_frombytes(&hinv_qsoa, hinv_bytes);
    GT_DECAP_VERIFY_POINTWISE_SYMBOL(&result_qsoa, c_minus_m2, &hinv_qsoa);
    poly_tobytes(out, &result_qsoa);
}

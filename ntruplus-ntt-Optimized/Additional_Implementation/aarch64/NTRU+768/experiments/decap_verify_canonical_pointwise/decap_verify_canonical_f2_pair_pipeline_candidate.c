#include <stdint.h>

#include "params.h"
#include "poly.h"
#include "decap_verify_canonical_pointwise.h"

void gt_decap_verify_canonical_f2_pair_pipeline_candidate(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const uint8_t hinv_bytes[NTRUPLUS_POLYBYTES])
{
    poly hinv_qsoa;
    poly result_qsoa;

    poly_frombytes(&hinv_qsoa, hinv_bytes);
    poly_basemul_decap_verify_canonical_f2_pair_pipeline(
        &result_qsoa, c_minus_m2, &hinv_qsoa);
    poly_tobytes(out, &result_qsoa);
}

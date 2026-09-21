#ifndef GT_LEGACY_VERIFY_H
#define GT_LEGACY_VERIFY_H
#include "poly.h"
/* Private decapsulation endpoint with a prevalidated QSoA h^-1 operand. */
void gt_decap_verify_predecoded_qsoa_to_bytes(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv_qsoa);

/* Legacy QSoA pointwise kernel retained for regression/ABI coverage only. */
void gt_decap_verify_pointwise(poly *out_qsoa, const poly *gt_input,
                               const poly *hinv_qsoa);
int qsoa_frombytes(poly *out,
                   const uint8_t in[NTRUPLUS_POLYBYTES]);
void qsoa_tobytes(uint8_t out[NTRUPLUS_POLYBYTES], const poly *in);

#endif

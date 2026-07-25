#ifndef GT_DECAP_BACKEND_H
#define GT_DECAP_BACKEND_H

#include <stdint.h>

#include "params.h"
#include "poly.h"

#ifndef GT_DECAP_VERIFY_TO_BYTES_SYMBOL
#define GT_DECAP_VERIFY_TO_BYTES_SYMBOL gt_decap_verify_to_bytes
#endif
#ifndef GT_DECAP_VERIFY_POINTWISE_SYMBOL
#define GT_DECAP_VERIFY_POINTWISE_SYMBOL gt_decap_verify_pointwise
#endif

/* Private decapsulation endpoint: GT NTT-domain product to canonical bytes. */
void GT_DECAP_VERIFY_TO_BYTES_SYMBOL(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const uint8_t hinv_bytes[NTRUPLUS_POLYBYTES]);

/* Internal QSoA pointwise kernel used by gt_decap_verify_to_bytes(). */
void GT_DECAP_VERIFY_POINTWISE_SYMBOL(poly *out_qsoa, const poly *gt_input,
                                      const poly *hinv_qsoa);

#endif

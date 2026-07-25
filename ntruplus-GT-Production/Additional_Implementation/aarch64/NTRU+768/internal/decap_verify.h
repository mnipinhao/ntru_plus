#ifndef NTRUPLUS768_INTERNAL_DECAP_VERIFY_H
#define NTRUPLUS768_INTERNAL_DECAP_VERIFY_H

#include <stdint.h>

#include "params.h"
#include "poly.h"

/* Private decapsulation endpoint: GT NTT-domain product to canonical bytes. */
void gt_decap_verify_to_bytes(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const uint8_t hinv_bytes[NTRUPLUS_POLYBYTES]);

/* Internal QSoA pointwise kernel used by gt_decap_verify_to_bytes(). */
void gt_decap_verify_pointwise(poly *out_qsoa, const poly *gt_input,
                               const poly *hinv_qsoa);
void qsoa_frombytes(poly *out,
                    const uint8_t in[NTRUPLUS_POLYBYTES]);
void qsoa_tobytes(uint8_t out[NTRUPLUS_POLYBYTES], const poly *in);

#endif

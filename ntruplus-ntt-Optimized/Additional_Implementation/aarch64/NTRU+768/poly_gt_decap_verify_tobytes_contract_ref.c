#include <stdint.h>

#include "params.h"
#include "poly.h"

void gt_decap_verify_basemul_tobytes_contract_ref(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv);

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

#ifndef NTRUPLUS768_INTERNAL_NTT_H
#define NTRUPLUS768_INTERNAL_NTT_H

#include <stdint.h>

#include "params.h"
#include "poly.h"

/*
 * KEM-internal Forward NTT contract.  The result is coefficient-wise
 * congruent modulo q to the reduced transform, but each signed-16 lane may
 * lie in [-27548, 27548].  Only consumers proved for that bound may call it.
 */
void gt_internal_poly_ntt_loose(poly *out, const poly *in);

/* Encap CBD/SOTP input only: each signed coefficient must be in [-2,2].
 * Bit-exact to generic loose NTT, including in-place operation.
 * Not a replacement for arbitrary/keygen inputs. */
void gt_internal_poly_ntt_encap_small(poly *out, const poly *in);

/*
 * Canonical byte boundary for the loose representation above.  This entry
 * accepts every signed-16 representative; public poly_tobytes retains its
 * already-reduced fast path.
 */
void gt_internal_poly_tobytes_from_loose(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *in);

#endif

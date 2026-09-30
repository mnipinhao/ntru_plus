#ifndef NTRUPLUS768_TEST_POLY_REFERENCE_H
#define NTRUPLUS768_TEST_POLY_REFERENCE_H

#include "../../poly.h"

/* Centers modulo q, then modulo 3; input [-3456,3456]. Exact alias allowed.
 * Test oracle (test/reference/crepmod3.S); the KEM uses the mod 3 fused into
 * poly_invntt_ternary_decap. */
void poly_crepmod3(poly *out, const poly *in);

/* Validation entries of the shared forward core in ntt.S (not called by the
 * KEM).  poly_ntt_loose: generic input, block-major output in
 * [-27548,27548].  poly_ntt_encap_small: signed [-2,2] input, bit-exact to
 * poly_ntt_loose, in-place allowed. */
void poly_ntt_loose(poly *out, const poly *in);
void poly_ntt_encap_small(poly *out, const poly *in);

#endif

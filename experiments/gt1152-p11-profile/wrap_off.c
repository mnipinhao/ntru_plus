/* Timing wrappers for the official NTRU+1152 API.
 *
 * Its shape differs from the GT package's: poly_ntt, poly_invntt_scale,
 * poly_triple and poly_crepmod3 are in-place one-argument calls, and it has a
 * poly_basemul_scale variant. id 8 carries poly_invntt_scale, the official's
 * inverse, so it lines up with the GT package's fused invntt_ternary at id 9.
 */
#include "poly.h"
#include "symmetric.h"
#include "wrap_common.h"

int poly_frombytes(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES]);
int poly_sotp_decode(uint8_t *m, const poly *a, const uint8_t *b);
int poly_baseinv(poly *r, const poly *a);

WRAP_V(0,  poly_tobytes,       (uint8_t *r, const poly *a), (r, a))
WRAP_I(3,  poly_frombytes,     (poly *r, const uint8_t *a), (r, a))
WRAP_V(4,  poly_cbd1,          (poly *r, const uint8_t *b), (r, b))
WRAP_V(5,  poly_sotp_encode,   (poly *r, const uint8_t *m, const uint8_t *b), (r, m, b))
WRAP_I(6,  poly_sotp_decode,   (uint8_t *m, const poly *a, const uint8_t *b), (m, a, b))
WRAP_V(7,  poly_ntt,           (poly *r), (r))
WRAP_V(8,  poly_invntt_scale,  (poly *r), (r))
WRAP_I(10, poly_baseinv,       (poly *r, const poly *a), (r, a))
WRAP_V(11, poly_basemul,       (poly *r, const poly *a, const poly *b), (r, a, b))
WRAP_V(12, poly_basemul_add,   (poly *r, const poly *a, const poly *b, const poly *c), (r, a, b, c))
WRAP_V(14, poly_sub,           (poly *r, const poly *a, const poly *b), (r, a, b))
WRAP_V(15, poly_triple,        (poly *r), (r))
WRAP_V(16, poly_crepmod3,      (poly *r), (r))
WRAP_V(17, hash_f,             (uint8_t *b, const uint8_t *m), (b, m))
WRAP_V(18, hash_g,             (uint8_t *b, const uint8_t *m), (b, m))
WRAP_V(20, hash_h,             (uint8_t *b, const uint8_t *m), (b, m))
WRAP_V(22, poly_basemul_scale, (poly *r, const poly *a, const poly *b), (r, a, b))

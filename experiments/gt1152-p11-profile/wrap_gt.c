/* Timing wrappers for the GT NTRU+1152 API. */
#include "poly.h"
#include "pack.h"
#include "inverse.h"
#include "symmetric.h"
#include "wrap_common.h"

WRAP_V(0,  poly_tobytes,         (uint8_t *r, const poly *a), (r, a))
WRAP_V(1,  poly_tobytes_small,   (uint8_t *r, const poly *a), (r, a))
WRAP_I(2,  poly_tobytes_compare, (const uint8_t *e, const poly *a), (e, a))
WRAP_I(3,  poly_frombytes,       (poly *r, const uint8_t *a), (r, a))
WRAP_V(4,  poly_cbd1,            (poly *r, const uint8_t *b), (r, b))
WRAP_V(5,  poly_sotp_encode,     (poly *r, const uint8_t *m, const uint8_t *b), (r, m, b))
WRAP_I(6,  poly_sotp_decode,     (uint8_t *m, const poly *a, const uint8_t *b), (m, a, b))
WRAP_V(7,  poly_ntt,             (poly *r, const poly *a), (r, a))
WRAP_V(9,  poly_invntt_ternary,  (poly *r, const poly *a), (r, a))
WRAP_I(10, poly_baseinv,         (poly *r, const poly *a), (r, a))
WRAP_V(11, poly_basemul,         (poly *r, const poly *a, const poly *b), (r, a, b))
WRAP_V(12, poly_basemul_add,     (poly *r, const poly *a, const poly *b, const poly *c), (r, a, b, c))
WRAP_V(13, poly_basemul_rinv,    (int16_t *r, const int16_t *a, const int16_t *b), (r, a, b))
WRAP_V(14, poly_sub,             (poly *r, const poly *a, const poly *b), (r, a, b))
WRAP_V(15, poly_triple,          (poly *r, const poly *a), (r, a))
WRAP_V(17, hash_f,               (uint8_t *b, const uint8_t *m), (b, m))
WRAP_V(18, hash_g,               (uint8_t *b, const uint8_t *m), (b, m))
WRAP_V(19, hash_g_fr0,           (uint8_t *b, const int16_t *c), (b, c))
WRAP_V(20, hash_h,               (uint8_t *b, const uint8_t *m), (b, m))

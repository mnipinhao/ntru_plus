#include "byte_boundary.h"
#include "poly.h"

void gt_bytes_poly_tobytes(uint8_t *out, const poly *in);
void gt_bytes_poly_frombytes(poly *out, const uint8_t *in);

/* P3B3's independently selected complete boundaries. */
void gt_bytes_poly_tobytes(uint8_t *out, const poly *in)
{
    r9_to(out, in->coeffs);
}

void gt_bytes_poly_frombytes(poly *out, const uint8_t *in)
{
    c1_from(out->coeffs, in);
}

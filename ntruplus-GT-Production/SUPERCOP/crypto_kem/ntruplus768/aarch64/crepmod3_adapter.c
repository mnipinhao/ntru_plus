#include "poly.h"
#include <string.h>

extern void official_poly_crepmod3(poly *r);

/* GT uses a two-pointer exact-alias contract; Official is in-place. */
void poly_crepmod3(poly *out, const poly *in)
{
    if (out != in)
        memcpy(out, in, sizeof(*out));
    official_poly_crepmod3(out);
}

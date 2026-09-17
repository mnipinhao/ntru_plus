#include "unpack_asm.h"
#include "poly.h"
#include "unpack.h"

int poly_frombytes(poly *out,const uint8_t *in)
{
    return frombytes_asm(out->coeffs,in);
}

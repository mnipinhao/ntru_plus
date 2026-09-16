#include "cluster_transpose_frombytes.h"
#include "poly.h"
#include "gt864_frombytes.h"

int gt864_fr0_frombytes_checked(poly *out,const uint8_t *in)
{
    return gt864_fr0_cluster_transpose_frombytes_checked_raw(out->coeffs,in);
}

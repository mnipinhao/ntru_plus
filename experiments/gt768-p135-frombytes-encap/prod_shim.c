/* P135: the landed unpack.c (built with its entry renamed new_frombytes_encap)
 * behind check.c's prototype signature, for a differential run against the
 * previous assembly decoder. */
#include "poly.h"
int new_frombytes_encap(poly *out, const uint8_t in[NTRUPLUS_POLYBYTES]);
int frombytes_encap_pairs(int16_t out[768], const uint8_t in[1152])
{
    return new_frombytes_encap((poly *)(void *)out, in);
}

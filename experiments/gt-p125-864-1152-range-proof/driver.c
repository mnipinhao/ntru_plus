/* Links the decapsulation inverse into one executable for range_interp2.py. */
#include <stdint.h>
#include "poly.h"
#include "inverse.h"
static poly m; static uint8_t scratch[POLY_INVNTT_TERNARY_SCRATCHBYTES];
int main(void){ poly_invntt_ternary(&m, &m, scratch); return m.coeffs[0]; }

/* P135: the permutation of NTRU+768's poly_frombytes_encap, from the production
 * tree.  Coefficient value i is encoded at wire position i (values < q, so
 * canonical), decoded, and each output lane is printed as (vector, lane,
 * wire coefficient). */
#include <stdio.h>
#include <stdint.h>
#include "params.h"
#include "poly.h"
int poly_frombytes_encap(poly *out, const uint8_t in[NTRUPLUS_POLYBYTES]);
int main(void){
  static uint8_t b[NTRUPLUS_POLYBYTES]; static poly g;
  for (int k = 0; k < NTRUPLUS_N / 2; k++) {           /* (a, b) -> 3 bytes */
    int a = 2 * k, c = 2 * k + 1;
    b[3*k] = a & 0xff; b[3*k+1] = (a >> 8) | ((c & 0xf) << 4); b[3*k+2] = c >> 4; }
  if (poly_frombytes_encap(&g, b)) { puts("rejected"); return 1; }
  for (int v = 0; v < NTRUPLUS_N / 8; v++) for (int l = 0; l < 8; l++) printf("%d %d %d\n", v, l, g.coeffs[8*v+l]);
  return 0; }

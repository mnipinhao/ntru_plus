/* callgrind driver: argv[1] picks one function, run 10 times after one warm call.
 * The per-address difference against mode "none" is that function's stream. */
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "params.h"
#include "poly.h"
int poly_frombytes(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES]);
void poly_tobytes_small(uint8_t *out, const poly *in);
void poly_basemul_rinv(int16_t *out, const int16_t *a, const int16_t *b);
void o_poly_tobytes(uint8_t *, const poly *); int o_poly_frombytes(poly *, const uint8_t *);
void o_poly_basemul_scale(poly *, const poly *, const poly *); void o_poly_ntt(poly *);
static poly a, b, r; static uint8_t bytes[NTRUPLUS_POLYBYTES], out[NTRUPLUS_POLYBYTES]; volatile int sink;
int main(int argc, char **argv){
  uint32_t s = 9; for (int i = 0; i < NTRUPLUS_N; i++){ s^=s<<13; s^=s>>17; s^=s<<5; a.coeffs[i] = s % 3457; s^=s<<13; s^=s>>17; s^=s<<5; b.coeffs[i] = s % 3457; }
  o_poly_tobytes(bytes, &a);
  poly f; poly_ntt(&f, &a);                     /* a forward-NTT output, as decapsulation's tobytes sees it */
  const char *m = argv[1];
  for (int k = 0; k < 10; k++) {
    if (!strcmp(m, "g_bmr")) poly_basemul_rinv(r.coeffs, a.coeffs, b.coeffs);
    if (!strcmp(m, "o_bms")) o_poly_basemul_scale(&r, &a, &b);
    if (!strcmp(m, "g_tob")) poly_tobytes(out, &f);
    if (!strcmp(m, "g_tobs")) poly_tobytes_small(out, &a);
    if (!strcmp(m, "o_tob")) o_poly_tobytes(out, &a);
    if (!strcmp(m, "g_from")) sink += poly_frombytes(&r, bytes);
    if (!strcmp(m, "o_from")) sink += o_poly_frombytes(&r, bytes);
  }
  return sink + out[0] + r.coeffs[0]; }

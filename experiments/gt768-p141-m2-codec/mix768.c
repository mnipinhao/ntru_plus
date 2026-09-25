/* P141: one call of one NTRU+768 codec / basemul_add entry point (GT or Official), chosen by argv[1],
 * after a set-up that calls none of them.  callgrind over the whole program for k and for 0 (set-up
 * only) differ by exactly that function's dynamic instruction mix (mixdiff.py); the entry points
 * share bodies (tobytes_encap_loose falls into tobytes_encap's core), so per-symbol attribution or
 * --toggle-collect cannot separate them.
 *   1 poly_tobytes_keygen_cq  2 poly_tobytes_encap_loose  3 poly_basemul_add_encap  4 poly_tobytes_encap
 *   5 o_poly_basemul_add      6 o_poly_tobytes
 *   7 poly_ntt_encap_small_lazy  8 o_poly_ntt */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "params.h"
#include "poly.h"
#include "keygen.h"
#include "encap.h"
void o_poly_ntt(poly *); void o_poly_tobytes(uint8_t *, const poly *); void o_poly_basemul_add(poly *, const poly *, const poly *, const poly *);
static uint8_t out[NTRUPLUS_POLYBYTES];
static poly a, b, c, t; static gt_cq_poly cq;
int main(int argc, char **argv){
  int k = argc > 1 ? atoi(argv[1]) : 0;
  for (int i = 0; i < NTRUPLUS_N; i++) { a.coeffs[i] = (int16_t)((i * 37) % 3457); b.coeffs[i] = (int16_t)((i * 11) % 3457);
                                         c.coeffs[i] = (int16_t)((i % 5) - 2); }
  memcpy(&cq.storage, &a, sizeof a);
  switch (k) {
  case 1: poly_tobytes_keygen_cq(out, &cq); break;
  case 2: poly_tobytes_encap_loose(out, &c); break;
  case 3: poly_basemul_add_encap(&t, &a, &b, &c); break;
  case 4: poly_tobytes_encap(out, &a); break;
  case 5: o_poly_basemul_add(&t, &a, &b, &c); break;
  case 6: o_poly_tobytes(out, &a); break;
  case 7: poly_ntt_encap_small_lazy(&t, &c); break;
  case 8: o_poly_ntt(&t); break;
  }
  return out[0] + t.coeffs[0]; }

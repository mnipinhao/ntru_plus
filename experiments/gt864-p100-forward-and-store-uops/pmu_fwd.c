/* Retired-instruction count for one kernel, isolated by an empty-mode baseline.
 * argv[1]: 0 = nothing, 1 = GT poly_ntt, 2 = Official poly_ntt,
 *          3 = GT poly_invntt_ternary, 4 = Official invntt_scale + crepmod3 */
#include <stdlib.h>
#include <stdint.h>
#include "params.h"
#include "poly.h"
void poly_ntt(poly*, const poly*);
void poly_invntt_ternary(poly*, const poly*);
void o_poly_ntt(poly*);
void o_poly_invntt_scale(poly*);
void o_poly_crepmod3(poly*);
static poly c;
volatile unsigned sink;
int main(int argc, char **argv){
  int mode = argc > 1 ? atoi(argv[1]) : 0;
  long n = argc > 2 ? atol(argv[2]) : 20000;
  for(int i=0;i<NTRUPLUS_N;i++) c.coeffs[i]=(int16_t)((i*2654435761u)%3457)-1728;
  for(long k=0;k<n;k++){
    switch(mode){
      case 1: poly_ntt(&c,&c); break;
      case 2: o_poly_ntt(&c); break;
      case 3: poly_invntt_ternary(&c,&c); break;
      case 4: o_poly_invntt_scale(&c); o_poly_crepmod3(&c); break;
      default: break;
    }
    sink += (unsigned)c.coeffs[0];
  }
  return 0;
}

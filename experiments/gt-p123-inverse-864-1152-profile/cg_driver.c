/* callgrind driver: argv[1] = 0 setup only, 1 setup + 10 GT, 2 setup + 10 Official;
 * 3 and 4 run GT and Official 2,000,000 times for perf sampling.
 * The per-address difference against mode 0 is the inverse's dynamic stream. */
#include <stdlib.h>
#include <stdint.h>
#include "params.h"
#include "poly.h"
void poly_invntt_ternary(poly*, const poly*);
void poly_ntt(poly*, const poly*);
void o_poly_invntt_scale(poly*);
void o_poly_crepmod3(poly*);
void o_poly_ntt(poly*);
static poly g, o, a, b;
volatile int sink;
int main(int argc, char **argv){
  int m = atoi(argv[1]);
  for(int i=0;i<NTRUPLUS_N;i++) g.coeffs[i]=(int16_t)((i*2654435761u)%3)-1;
  o = g; poly_ntt(&g,&g); o_poly_ntt(&o);
  long reps = m >= 3 ? 2000000 : 10; if (m >= 3) m -= 2;
  for(long r=0;r<reps;r++){
    a = g; b = o;
    if(m==1) poly_invntt_ternary(&a,&a);
    if(m==2){ o_poly_invntt_scale(&b); o_poly_crepmod3(&b); }
    sink += a.coeffs[0] + b.coeffs[0];
  }
  return 0;}

/* How often keygen's f and g candidates are non-invertible (the retry rate). */
#include <stdio.h>
#include <stdint.h>
#include "params.h"
#include "poly.h"
#include "inverse.h"
#include "symmetric.h"
#include "fips202.h"
void randombytes(uint8_t *out, size_t n);
static poly f, finv; static uint8_t buf[NTRUPLUS_N/4], coins[32];
int main(void){ int fail_f=0, fail_g=0, N=4000;
 for(int i=0;i<N;i++){ randombytes(coins,32); shake256(buf,NTRUPLUS_N/4,coins,32); poly_cbd1(&f,buf); poly_triple(&f,&f); f.coeffs[0]+=1; poly_ntt(&f,&f); fail_f+=poly_baseinv(&finv,&f);
                       randombytes(coins,32); shake256(buf,NTRUPLUS_N/4,coins,32); poly_cbd1(&f,buf); poly_triple(&f,&f); poly_ntt(&f,&f); fail_g+=poly_baseinv(&finv,&f); }
 printf("N=%d  f fails %.1f%%  g fails %.1f%%  -> expected failed baseinv calls per keygen %.3f\n", NTRUPLUS_N, 100.0*fail_f/N, 100.0*fail_g/N,
   (double)fail_f/(N-fail_f) + (double)fail_g/(N-fail_g)); return 0; }

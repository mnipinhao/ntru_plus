#include <stdlib.h>
#include <stdint.h>
#include "layout.h"
#include "params.h"
#include "poly.h"
void poly_tobytes_keygen_cq(uint8_t*, const gt_cq_poly*);
void poly_tobytes_decap(uint8_t*, const poly*);
void o_poly_tobytes(uint8_t*, const poly*);
static gt_cq_poly cq; static poly p; static uint8_t buf[NTRUPLUS_POLYBYTES];
volatile unsigned sink;
int main(int argc,char**argv){
  int m=argc>1?atoi(argv[1]):0; long n=argc>2?atol(argv[2]):20000;
  for(int i=0;i<NTRUPLUS_N;i++){p.coeffs[i]=(int16_t)(i%3457); cq.storage.coeffs[i]=p.coeffs[i];}
  for(long k=0;k<n;k++){
    switch(m){case 1: poly_tobytes_keygen_cq(buf,&cq); break;
              case 2: o_poly_tobytes(buf,&p); break;
              case 3: poly_tobytes_decap(buf,&p); break; default: break;}
    sink+=buf[0];
  }
  return 0;}

#include <stdlib.h>
#include <stdint.h>
#include "params.h"
#include "poly.h"
int poly_frombytes(poly*, const uint8_t*);
int o_poly_frombytes(poly*, const uint8_t*);
static poly p; static uint8_t buf[NTRUPLUS_POLYBYTES+64];
volatile unsigned sink;
int main(int argc,char**argv){
  int m=argc>1?atoi(argv[1]):0; long n=argc>2?atol(argv[2]):20000;
  for(size_t i=0;i<sizeof buf;i++) buf[i]=(uint8_t)(i*211u);
  for(long k=0;k<n;k++){
    switch(m){case 1: sink+=poly_frombytes(&p,buf); break;
              case 2: sink+=o_poly_frombytes(&p,buf); break; default: break;}
    sink+=(unsigned)p.coeffs[0];
  }
  return 0;}

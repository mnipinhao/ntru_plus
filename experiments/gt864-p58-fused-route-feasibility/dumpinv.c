#include <stdio.h>
#include <stdint.h>
#include "params.h"
#include "poly.h"
#include "inverse.h"
int main(int argc,char**argv){
  poly a,x; uint64_t s=88172645463325252ULL; FILE*f=fopen(argv[1],"wb");
  int tern=0;
  for(int it=0; it<20000; it++){
    for(int i=0;i<NTRUPLUS_N;i++){ s^=s<<13;s^=s>>7;s^=s<<17;
      a.coeffs[i]=(int16_t)((int)(s%4995)-2497); }   /* FR0 R^-1, |c|<=2497 */
    poly_invntt_ternary(&x,&a);
    for(int i=0;i<NTRUPLUS_N;i++) if(x.coeffs[i]<-1||x.coeffs[i]>1) tern++;
    fwrite(x.coeffs,2,NTRUPLUS_N,f);
  }
  fclose(f);
  fprintf(stderr,"  %-10s non-ternary coefficients: %d\n",argv[2],tern);
  return 0; }

/* Correctness probe for baseinv / basemul_rinv. Not a timing harness. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "inverse.h"
void ntt_asm(int16_t out[1152], const int16_t in[1152]);
static void rd(const char **p, int16_t *v, int n){
    char *e; for(int i=0;i<n;i++){ v[i]=(int16_t)strtol(*p,&e,10); *p=(*e==',')?e+1:e; } }
static void wr(const int16_t *v,int n){ for(int i=0;i<n;i++) printf("%d%c",v[i],i==n-1?'\n':','); }
int main(int argc,char**argv){
    static int16_t a[1152],b[1152],A[1152],B[1152],out[1152];
    if(argc!=3){fprintf(stderr,"usage: harness <mode> <2x1152>\n");return 2;}
    const char*p=argv[2]; rd(&p,a,1152); rd(&p,b,1152);
    ntt_asm(A,a); ntt_asm(B,b);
    const char*m=argv[1];
    int rc=0;
    if(!strcmp(m,"inv"))            rc=baseinv_asm(out,A);
    else if(!strcmp(m,"inv_alias")) { memcpy(out,A,sizeof out); rc=baseinv_asm(out,out); }
    else if(!strcmp(m,"inv_raw"))   rc=baseinv_asm(out,a);     /* arbitrary input, may fail */
    else if(!strcmp(m,"rinv"))      basemul_rinv_asm(out,A,B);
    else if(!strcmp(m,"rinv_alias")){ memcpy(out,A,sizeof out); basemul_rinv_asm(out,out,B); }
    else if(!strcmp(m,"rinv_raw"))  basemul_rinv_asm(out,a,b); /* raw 12-bit style domain */
    else {fprintf(stderr,"bad mode\n");return 2;}
    printf("%d\n",rc); wr(out,1152); return 0;
}

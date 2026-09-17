/* Differential harness: GT forward then basemul / basemul_add, plus alias
 * variants. Correctness probe only; not a timing harness. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "base.h"

void ntt_asm(int16_t out[1152], const int16_t in[1152]);

static void rd(const char **p, int16_t *v, int n){
    char *e; for (int i=0;i<n;i++){ v[i]=(int16_t)strtol(*p,&e,10); *p = (*e==',')?e+1:e; }
}
static void wr(const int16_t *v, int n){
    for (int i=0;i<n;i++) printf("%d%c", v[i], i==n-1?'\n':',');
}

int main(int argc, char **argv)
{
    static int16_t a[1152], b[1152], c[1152], A[1152], B[1152], C[1152], out[1152];
    if (argc != 3) { fprintf(stderr,"usage: harness <mode> <3x1152 values>\n"); return 2; }
    const char *p = argv[2];
    rd(&p,a,1152); rd(&p,b,1152); rd(&p,c,1152);
    ntt_asm(A,a); ntt_asm(B,b); ntt_asm(C,c);

    const char *mode = argv[1];
    if (!strcmp(mode,"mul"))            basemul_asm(out,A,B);
    else if (!strcmp(mode,"add"))       basemul_add_asm(out,A,B,C);
    else if (!strcmp(mode,"alias_a"))  { memcpy(out,A,sizeof out); basemul_asm(out,out,B); }
    else if (!strcmp(mode,"alias_b"))  { memcpy(out,B,sizeof out); basemul_asm(out,A,out); }
    else if (!strcmp(mode,"alias_aa")) { memcpy(out,A,sizeof out); basemul_asm(out,out,out); }
    else if (!strcmp(mode,"alias_addc")){ memcpy(out,C,sizeof out); basemul_add_asm(out,A,B,out); }
    else { fprintf(stderr,"bad mode\n"); return 2; }
    wr(out,1152);
    return 0;
}

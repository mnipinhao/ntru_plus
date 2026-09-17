/* Correctness probe for the NTRU+1152 codec. Not a timing harness. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "pack_asm.h"
static void rd16(const char **p, int16_t *v, int n){
    char *e; for(int i=0;i<n;i++){ v[i]=(int16_t)strtol(*p,&e,10); *p=(*e==',')?e+1:e; } }
static void rd8(const char **p, uint8_t *v, int n){
    char *e; for(int i=0;i<n;i++){ v[i]=(uint8_t)strtol(*p,&e,10); *p=(*e==',')?e+1:e; } }
int main(int argc, char **argv){
    static int16_t a[1152], out16[1152];
    static uint8_t buf[1728], exp[1728];
    if(argc!=3){fprintf(stderr,"usage: harness <mode> <data>\n");return 2;}
    const char *m=argv[1], *p=argv[2];
    if(!strcmp(m,"full")||!strcmp(m,"small")){
        rd16(&p,a,1152);
        if(!strcmp(m,"full")) tobytes_full_asm(buf,a); else tobytes_small_asm(buf,a);
        for(int i=0;i<1728;i++) printf("%d%c",buf[i],i==1727?'\n':',');
    } else if(!strcmp(m,"from")){
        rd8(&p,buf,1728);
        int rc=frombytes_asm(out16,buf);
        printf("%d\n",rc);
        for(int i=0;i<1152;i++) printf("%d%c",out16[i],i==1151?'\n':',');
    } else if(!strcmp(m,"cmp")){
        rd16(&p,a,1152); rd8(&p,exp,1728);
        printf("%d\n",tobytes_compare_asm(exp,a));
    } else {fprintf(stderr,"bad mode\n");return 2;}
    return 0;
}

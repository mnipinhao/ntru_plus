/* Probe NTRU+864's invntt16_tail_asm as a pure function: 128 scratch inputs
 * to 96 natural-order stores. Linear given fixed tables, so delta probes
 * recover the whole map. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "inverse_tables.h"
#include "inverse16_tables.h"
void invntt16_tail_asm(int16_t *out, const int16_t *scratch, long z,
                       const int16_t *stage, const int16_t *terminal);
int main(int argc,char**argv){
    static int16_t scratch[128], out[1024];
    if(argc!=2){fprintf(stderr,"usage: probe_tail <128 values>\n");return 2;}
    char*p=argv[1];
    for(int i=0;i<128;i++){ scratch[i]=(int16_t)strtol(p,&p,10); if(*p==',')p++; }
    for(int i=0;i<1024;i++) out[i]=0;
    invntt16_tail_asm(out, scratch, 0,
                      &invntt16_constants[0][0], &invntt16_tail_constants[0][0]);
    for(int i=0;i<1024;i++) printf("%d%c",out[i],i==1023?'\n':',');
    return 0;
}

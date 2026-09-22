/* Which output halfwords does each scratch lane reach?  The kernel is
 * lane-parallel, so perturbing every u at one lane v and diffing the output
 * recovers that lane's support exactly, without assuming anything about the
 * index algebra. */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "inverse_tables.h"
#include "inverse16_tables.h"
void invntt16_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_lane_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
typedef void (*K)(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
static uint64_t st=0x9E3779B97F4A7C15ull;
static int16_t rnd(void){st^=st<<13;st^=st>>7;st^=st<<17;return (int16_t)((st>>33)%2617)-1308;}
static void run(K k,int16_t*o,const int16_t*in){
    memset(o,0,896*2);
    k(o,in,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
}
int main(int c,char**v){
    K k = (c>1&&v[1][0]=='n') ? invntt16_lane_asm : invntt16_asm;
    static int16_t in[128],in2[128],a[896],b[896];
    for(int i=0;i<128;i++) in[i]=rnd();
    run(k,a,in);
    for(int lane=0;lane<8;lane++){
        memcpy(in2,in,sizeof in);
        for(int u=0;u<16;u++) in2[u*8+lane]^=0x2aa;   /* whole lane perturbed */
        run(k,b,in2);
        printf("lane %d:",lane);
        int n=0,first=-1,last=-1;
        for(int p=0;p<896;p++) if(a[p]!=b[p]){ if(first<0)first=p; last=p; n++; if(n<=6)printf(" %d",p); }
        printf("%s   (共 %d 個, %d..%d)\n",n>6?" ...":"",n,first,last);
    }
    return 0;
}

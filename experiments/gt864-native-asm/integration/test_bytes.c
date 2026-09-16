#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "p3b1_tables.h"
#include "tables.h"
#include "byte_merge_tables.h"
typedef int (*fn)(uint8_t*,const int16_t*,const void*,const void*,const void*);
int probe_bytes_full(uint8_t*,const int16_t*,const void*,const void*,const void*);
int probe_bytes_small(uint8_t*,const int16_t*,const void*,const void*,const void*);
static uint32_t state=3457;
static uint32_t rnd(void){state^=state<<13;state^=state>>17;state^=state<<5;return state;}
static void check(int ok,const char*s){if(!ok){fprintf(stderr,"FAIL %s\n",s);exit(1);}}
static int canonical(int x){x%=3457;return x<0?x+3457:x;}
static void oracle(uint8_t*out,const int16_t*in){for(int i=0;i<432;i++){
 unsigned a=canonical(in[map_f[2*i]]),b=canonical(in[map_f[2*i+1]]);
 out[3*i]=a;out[3*i+1]=(a>>8)|((b&15)<<4);out[3*i+2]=b>>4;
}}
static void one(const int16_t*in,int small){
 uint8_t memory[1296+32],expected[1296];int16_t saved[864];memcpy(saved,in,sizeof saved);
 oracle(expected,in);memset(memory,0xa5,sizeof memory);
 fn f=small?probe_bytes_small:probe_bytes_full;
 check(f(memory+16,in,p3b1_prefix,p3b1_a_fwd,gt864_byte_merge_indices)==0,"AAPCS or 656-byte wipe");
 check(!memcmp(memory+16,expected,1296),small?"small exact wire bytes":"full exact wire bytes");
 check(!memcmp(saved,in,sizeof saved),"input mutated");
 for(int j=0;j<16;j++)check(memory[j]==0xa5&&memory[1312+j]==0xa5,"output canary");
}
int main(void){
 int16_t in[864];
 for(int t=0;t<512;t++){for(int j=0;j<864;j++)in[j]=(int16_t)rnd();one(in,0);}
 for(int x=-32768;x<=32767;x++){for(int j=0;j<864;j++)in[j]=x;one(in,0);}
 for(int x=-3456;x<=3456;x++){for(int j=0;j<864;j++)in[j]=x;one(in,1);}
 for(int t=0;t<512;t++){for(int j=0;j<864;j++)in[j]=(int)(rnd()%6913)-3456;one(in,0);one(in,1);}
 puts("PASS full ToBytes 66048 cases + small ToBytes 7425 cases; 512 shared-domain differentials; exact 1296 bytes, AAPCS, input immutability, canaries, 656-byte wipe");
}

/* C tail (the declared contract) against the generated assembly tail. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "inverse_tables.h"
#include "invntt16_tail_table.h"
#define Q 3457
void invntt16_tail_asm(int16_t*, const int16_t*, long, const int16_t*, const int16_t*);
void ref_tail(int16_t*, const int16_t*, long, const int16_t*, const int16_t*);
static int16_t scratch[128], a[2048], b[2048];
static uint64_t rng=88172645463325252ull;
static int16_t r16(void){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;return (int16_t)((rng%5235)-2617);}
int main(void){
    int bad_exact=0, bad_modq=0, worst=0;
    for(int trial=0;trial<4000;trial++){
        int ext=(trial<200);
        for(int i=0;i<128;i++) scratch[i]= ext ? (int16_t)((rng^=rng<<13,rng^=rng>>7,rng^=rng<<17,rng)&1?2617:-2617) : r16();
        for(int i=0;i<2048;i++) a[i]=b[i]=-31337;
        ref_tail(a, scratch, 0, &invntt16_constants[0][0], &invntt16_tail_constants[0][0]);
        invntt16_tail_asm(b, scratch, 0, &invntt16_constants[0][0], &invntt16_tail_constants[0][0]);
        for(int k=0;k<32;k++) for(int br=0;br<4;br++){
            int i=36*k+br;
            int x=a[i], y=b[i];
            if(x!=y){ bad_exact++;
                int d=((x-y)%Q+Q)%Q;
                if(d) { if(bad_modq<6) printf("  k=%2d b=%d  C=%6d asm=%6d  diff mod q = %d\n",k,br,x,y,d);
                        bad_modq++; } }
            if(abs(y)>worst) worst=abs(y);
        }
    }
    printf("4000 trials x 128 outputs: exact mismatches %d, mod-q mismatches %d, max |asm| %d\n",
           bad_exact, bad_modq, worst);
    return bad_modq!=0;
}

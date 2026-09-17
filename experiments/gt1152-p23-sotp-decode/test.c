#include <stdio.h>
#include <stdint.h>
#include <string.h>
#define N 1152
int poly_sotp_decode(uint8_t*, const int16_t*, const uint8_t*);
static int ref(uint8_t msg[N/8], const int16_t a[N], const uint8_t buf[N/4]){
    uint8_t t1,t2,t3; uint16_t t4; uint32_t r=0; uint8_t mask;
    for(size_t i=0;i<N/8;i++){ t1=buf[i]; t2=buf[i+N/8]; t3=0;
        for(size_t j=0;j<8;j++){ t4=t2&1; t4+=a[8*i+j]; r|=t4; t4=(t4^t1)&1;
            t3^=(uint8_t)(t4<<j); t1>>=1; t2>>=1; }
        msg[i]=t3; }
    r=r>>1; r=(-(uint32_t)r)>>31; mask=(uint8_t)(r-1);
    for(size_t i=0;i<N/8;i++) msg[i]&=mask;
    return (int)r;
}
static uint64_t s=0x243F6A8885A308D3ull;
static uint64_t rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
int main(void){
    int16_t a[N]; uint8_t buf[N/4], m1[N/8], m2[N/8];
    int bad=0, fails=0, oks=0;
    for(int trial=0; trial<20000; trial++){
        int mode = trial % 4;
        for(size_t i=0;i<N/4;i++) buf[i]=(uint8_t)rnd();
        if(mode<2){
            /* a valid encoding: pick the message bit m, set a = m - b2 so that
             * t4 = m is always 0 or 1 and the decode must accept. */
            for(int i=0;i<N;i++){
                int b2=(buf[N/8 + i/8] >> (i%8)) & 1;
                int m=(int)(rnd()&1);
                a[i]=(int16_t)(m-b2);
            }
            if(mode==1){ /* one coefficient corrupted: must reject */
                int pos=(int)(rnd()%N); a[pos]=(int16_t)(a[pos]==1?-1:a[pos]+1);
                int b2=(buf[N/8+pos/8]>>(pos%8))&1;
                if((uint16_t)(a[pos]+b2)<=1) a[pos]=(int16_t)(a[pos]+2);
            }
        } else if(mode==2) for(int i=0;i<N;i++) a[i]=(int16_t)(rnd()%3)-1;
        else for(int i=0;i<N;i++) a[i]=(int16_t)((rnd()%7)-3);
        int r1=ref(m1,a,buf), r2=poly_sotp_decode(m2,a,buf);
        if(r1!=r2 || memcmp(m1,m2,N/8)){ if(bad<4) printf("  mismatch trial %d mode %d: rc %d/%d msgdiff %d\n",
            trial,mode,r1,r2,memcmp(m1,m2,N/8)!=0); bad++; }
        r1?fails++:oks++;
    }
    printf("20000 trials: mismatches %d   (accepted %d, rejected %d)\n", bad, oks, fails);
    return bad!=0;
}

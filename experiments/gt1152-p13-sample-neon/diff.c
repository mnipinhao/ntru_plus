/* Differential: NEON sampling leaves against the plain-C originals. */
#include <stdio.h>
#include <string.h>
#include "poly.h"
void poly_cbd1(poly*,const uint8_t*); void ref_poly_cbd1(poly*,const uint8_t*);
void poly_sotp_encode(poly*,const uint8_t*,const uint8_t*);
void ref_poly_sotp_encode(poly*,const uint8_t*,const uint8_t*);
int poly_sotp_decode(uint8_t*,const poly*,const uint8_t*);
int ref_poly_sotp_decode(uint8_t*,const poly*,const uint8_t*);
void poly_sub(poly*,const poly*,const poly*); void ref_poly_sub(poly*,const poly*,const poly*);
void poly_triple(poly*,const poly*); void ref_poly_triple(poly*,const poly*);
static unsigned long s=12345;
static unsigned rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return (unsigned)s;}
int main(void){
    static poly p,q1,q2,x,y; static uint8_t buf[NTRUPLUS_N/4],msg[NTRUPLUS_N/8];
    static uint8_t m1[NTRUPLUS_N/8],m2[NTRUPLUS_N/8];
    int fail=0;
    for(int t=0;t<200;t++){
        for(size_t i=0;i<sizeof buf;i++) buf[i]=(uint8_t)rnd();
        for(size_t i=0;i<sizeof msg;i++) msg[i]=(uint8_t)rnd();
        poly_cbd1(&q1,buf); ref_poly_cbd1(&q2,buf);
        if(memcmp(&q1,&q2,sizeof q1)){printf("cbd1 mismatch t=%d\n",t);fail=1;}
        poly_sotp_encode(&q1,msg,buf); ref_poly_sotp_encode(&q2,msg,buf);
        if(memcmp(&q1,&q2,sizeof q1)){printf("sotp_encode mismatch t=%d\n",t);fail=1;}
        /* decode: feed both the success shape (cbd output) and arbitrary polys */
        for(int mode=0;mode<2;mode++){
            if(mode==0) ref_poly_cbd1(&p,buf);
            else for(int i=0;i<NTRUPLUS_N;i++) p.coeffs[i]=(int16_t)(rnd()%7)-3;
            int r1=poly_sotp_decode(m1,&p,buf), r2=ref_poly_sotp_decode(m2,&p,buf);
            if(r1!=r2||memcmp(m1,m2,sizeof m1)){
                printf("sotp_decode mismatch t=%d mode=%d r=%d/%d\n",t,mode,r1,r2);fail=1;}
        }
        for(int i=0;i<NTRUPLUS_N;i++){x.coeffs[i]=(int16_t)rnd();y.coeffs[i]=(int16_t)rnd();}
        poly_sub(&q1,&x,&y); ref_poly_sub(&q2,&x,&y);
        if(memcmp(&q1,&q2,sizeof q1)){printf("sub mismatch\n");fail=1;}
        poly_triple(&q1,&x); ref_poly_triple(&q2,&x);
        if(memcmp(&q1,&q2,sizeof q1)){printf("triple mismatch\n");fail=1;}
        if(fail) return 1;
    }
    puts("PASS: 200 cases, cbd1 / sotp_encode / sotp_decode (both modes) / sub / triple");
    return 0;
}

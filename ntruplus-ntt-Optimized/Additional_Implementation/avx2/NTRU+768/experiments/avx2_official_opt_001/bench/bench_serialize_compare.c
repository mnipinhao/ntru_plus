#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "poly.h"
#include "cpucycles.h"
#include "kat/rng.h"
int official_lazy_keypair(uint8_t *,uint8_t *);
int official_lazy_enc(uint8_t *,uint8_t *,const uint8_t *);
int official_lazy_dec(uint8_t *,const uint8_t *,const uint8_t *);
int official_compare_dec(uint8_t *,const uint8_t *,const uint8_t *);
int ntruplus768_officialopt_serialize_compare(const uint8_t *,const poly *);
void ntruplus768_officialopt_ntt_caller_lazy(poly *);
enum{BANKS=16};
static poly p[BANKS];
static uint8_t wire[BANKS][1152],temp[BANKS][1152];
static uint8_t pk[BANKS][NTRUPLUS_PUBLICKEYBYTES],sk[BANKS][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct[BANKS][1152],ss[BANKS][NTRUPLUS_SSBYTES];
static volatile int sink;
static void pack_o(unsigned b){
    poly_tobytes(temp[b],&p[b]);
    uint8_t mismatch=0;
    for(int i=0;i<1152;i++) mismatch|=temp[b][i]^wire[b][i];
    sink=!!mismatch;
}
static void pack_c(unsigned b){sink=ntruplus768_officialopt_serialize_compare(wire[b],&p[b]);}
static void dec_o(unsigned b){sink=official_lazy_dec(ss[b],ct[b],sk[b]);}
static void dec_c(unsigned b){sink=official_compare_dec(ss[b],ct[b],sk[b]);}
int main(void){
    uint8_t entropy[48]={0},sample[192],saved[NTRUPLUS_SSBYTES];
    randombytes_init(entropy,NULL,256);
    for(unsigned b=0;b<BANKS;b++){
        if(official_lazy_keypair(pk[b],sk[b])||official_lazy_enc(ct[b],ss[b],pk[b]))abort();
        for(int i=0;i<192;i++)sample[i]=(uint8_t)(i*31+b*13);
        poly_cbd1(&p[b],sample);ntruplus768_officialopt_ntt_caller_lazy(&p[b]);
        poly_tobytes(wire[b],&p[b]);pack_o(b);if(sink)abort();pack_c(b);if(sink)abort();
        dec_o(b);if(sink)abort();memcpy(saved,ss[b],sizeof saved);
        dec_c(b);if(sink||memcmp(saved,ss[b],sizeof saved))abort();
    }
    cpucycles_tracesetup();
    fprintf(stderr,"preflight=pass\ncpucycles=%s persecond=%lld\n",cpucycles_implementation(),cpucycles_persecond());
    void (*ops[2][2])(unsigned)={{pack_o,pack_c},{dec_o,dec_c}};
    for(unsigned r=0;r<2;r++)for(unsigned block=0;block<8;block++)for(unsigned slot=0;slot<2;slot++){
        unsigned v=slot^(block&1);void(*run)(unsigned)=ops[r][v];
        /* Read-only inputs; identical banks and warmup, no kernel reset needed. */
        for(unsigned w=0;w<16;w++)run(w);
        for(unsigned j=0;j<64;j++){
            unsigned b=j%16;long long t=cpucycles();run(b);t=cpucycles()-t;
            printf("%u,%u,%u,%u,%lld\n",r,v,block,j,t);
        }
    }
}

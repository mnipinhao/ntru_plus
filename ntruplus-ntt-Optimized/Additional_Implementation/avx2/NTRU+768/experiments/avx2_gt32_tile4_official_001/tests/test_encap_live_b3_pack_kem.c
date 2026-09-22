#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "internal.h"
#include "kat/rng.h"

int ntruplus768_exp001_enc_derand_live_b3_pack(uint8_t *, uint8_t *,
                                                 const uint8_t *, const uint8_t *);

int main(void) {
    uint8_t entropy[48];
    uint8_t pk[NTRUPLUS_PUBLICKEYBYTES], bad_pk[NTRUPLUS_PUBLICKEYBYTES];
    uint8_t sk[NTRUPLUS_SECRETKEYBYTES], coins[NTRUPLUS_N/8];
    uint8_t control_ct[NTRUPLUS_CIPHERTEXTBYTES];
    uint8_t candidate_ct[NTRUPLUS_CIPHERTEXTBYTES];
    uint8_t control_ss[NTRUPLUS_SSBYTES], candidate_ss[NTRUPLUS_SSBYTES];
    uint8_t dec_ss[NTRUPLUS_SSBYTES], bad_ss[NTRUPLUS_SSBYTES];
    for (size_t i=0;i<sizeof entropy;i++) entropy[i]=(uint8_t)(19U+23U*i);
    randombytes_init(entropy,NULL,256);
    if(ntruplus768_keypair_impl(pk,sk)) return 1;
    for(unsigned trial=0;trial<100;trial++) {
        for(size_t i=0;i<sizeof coins;i++) coins[i]=(uint8_t)(trial*73U+i*19U);
        if(ntruplus768_enc_derand_impl(control_ct,control_ss,pk,coins) ||
           ntruplus768_exp001_enc_derand_live_b3_pack(candidate_ct,candidate_ss,pk,coins) ||
           memcmp(control_ct,candidate_ct,sizeof control_ct) ||
           memcmp(control_ss,candidate_ss,sizeof control_ss)) {
            fprintf(stderr,"valid Encap mismatch at trial %u\n",trial);
            return 1;
        }
        if(ntruplus768_dec_impl(dec_ss,candidate_ct,sk) ||
           memcmp(dec_ss,candidate_ss,sizeof dec_ss)) {
            fprintf(stderr,"valid Decap mismatch at trial %u\n",trial);
            return 1;
        }
        candidate_ct[(trial*17U)%sizeof candidate_ct] ^= 1;
        int bad_rc=ntruplus768_dec_impl(bad_ss,candidate_ct,sk);
        const uint8_t zero_ss[NTRUPLUS_SSBYTES]={0};
        if(bad_rc!=1 || memcmp(bad_ss,zero_ss,sizeof bad_ss)) {
            fprintf(stderr,"invalid CT semantics mismatch at trial %u\n",trial);
            return 1;
        }
        memcpy(bad_pk,pk,sizeof pk);
        bad_pk[3*(trial%384U)] = 0xff;
        bad_pk[3*(trial%384U)+1] |= 0x0f;
        int control_rc=ntruplus768_enc_derand_impl(control_ct,control_ss,bad_pk,coins);
        int candidate_rc=ntruplus768_exp001_enc_derand_live_b3_pack(
            candidate_ct,candidate_ss,bad_pk,coins);
        if(control_rc!=candidate_rc ||
           memcmp(control_ct,candidate_ct,sizeof control_ct) ||
           memcmp(control_ss,candidate_ss,sizeof control_ss)) {
            fprintf(stderr,"invalid PK mismatch at trial %u\n",trial);
            return 1;
        }
    }
    puts("live B3→Q24 KEM: 100 deterministic vectors, invalid PK/CT pass");
    return 0;
}

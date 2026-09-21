#include <stddef.h>
#include <stdint.h>

#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"

void ntruplus768_wire_research_forward(int16_t *, const int16_t *);
int ntruplus768_wire_research_decode(int16_t *, const uint8_t *);
void ntruplus768_wire_research_pack(uint8_t *, const int16_t *);
void ntruplus768_wire_research_muladd_1(int16_t *, const int16_t *,
    const int16_t *, const int16_t *);
void ntruplus768_wire_research_muladd_2(int16_t *, const int16_t *,
    const int16_t *, const int16_t *);

typedef struct __attribute__((aligned(64))) {
    int16_t h[NTRUPLUS_N], r[NTRUPLUS_N], m[NTRUPLUS_N];
    int16_t c[NTRUPLUS_N], work[NTRUPLUS_N];
} wire_scratch;

static void wire_forward(int16_t *out, int16_t *work, const int16_t *in) {
    ntruplus768_ntt_frontend_avx2(work,in);
    ntruplus768_wire_research_forward(out,work);
}

int ntruplus768_wire_research_enc_derand_impl(
    uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
    uint8_t ss[NTRUPLUS_SSBYTES],
    const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
    const uint8_t coins[NTRUPLUS_N/8], int two_packet)
{
    uint8_t msg[HASH_H_INBYTES], buf[HASH_H_OUTBYTES];
    wire_scratch scratch;
    if (ntruplus768_wire_research_decode(scratch.h,pk) != 0) {
        for (size_t i=0;i<NTRUPLUS_CIPHERTEXTBYTES;i++) ct[i]=0;
        secure_clear(ss,NTRUPLUS_SSBYTES);
        return 1;
    }
    for (size_t i=0;i<NTRUPLUS_N/8;i++) msg[i]=coins[i];
    hash_f(msg+NTRUPLUS_N/8,pk);
    hash_h(buf,msg);
    poly_cbd1((poly *)(void *)scratch.work,buf+NTRUPLUS_SYMBYTES);
    wire_forward(scratch.r,scratch.c,scratch.work);
    ntruplus768_wire_research_pack(ct,scratch.r);
    hash_g(ct,ct);
    poly_sotp_encode((poly *)(void *)scratch.work,msg,ct);
    wire_forward(scratch.m,scratch.c,scratch.work);
    if(two_packet)
        ntruplus768_wire_research_muladd_2(scratch.c,scratch.h,scratch.r,scratch.m);
    else
        ntruplus768_wire_research_muladd_1(scratch.c,scratch.h,scratch.r,scratch.m);
    ntruplus768_wire_research_pack(ct,scratch.c);
    for (size_t i=0;i<NTRUPLUS_SSBYTES;i++) ss[i]=buf[i];
    secure_clear(msg,sizeof msg);
    secure_clear(buf,sizeof buf);
    secure_clear(scratch.r,sizeof scratch.r);
    secure_clear(scratch.m,sizeof scratch.m);
    return 0;
}

#include <stddef.h>
#include <stdint.h>
#include "candidate.h"
#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"

typedef struct __attribute__((aligned(64))) {
	int16_t h[NTRUPLUS_N],r[NTRUPLUS_N],m[NTRUPLUS_N],c[NTRUPLUS_N];
} scratch_t;

int gt105_encap_virtual(uint8_t *ct,uint8_t *ss,const uint8_t *pk,
	const uint8_t *coins)
{
	uint8_t msg[HASH_H_INBYTES],buf[HASH_H_OUTBYTES]; scratch_t s;
	if(ntruplus768_unpack_m_avx2(s.h,pk)!=0){
		for(size_t i=0;i<NTRUPLUS_CIPHERTEXTBYTES;i++)ct[i]=0;
		secure_clear(ss,NTRUPLUS_SSBYTES);return 1;
	}
	for(size_t i=0;i<NTRUPLUS_N/8;i++)msg[i]=coins[i];
	hash_f(msg+NTRUPLUS_N/8,pk);hash_h(buf,msg);
	poly_cbd1((poly *)(void *)s.m,buf+NTRUPLUS_SYMBYTES);
	ntruplus768_ntt_frontend_avx2(s.c,s.m);ntruplus768_ntt_m_avx2(s.r,s.c);
	ntruplus768_pack_m_lazy10788_avx2(ct,s.r);hash_g(ct,ct);
	poly_sotp_encode((poly *)(void *)s.m,msg,ct);
	ntruplus768_ntt_frontend_avx2(s.c,s.m);gt103_ntt_ql2_avx2(s.m,s.c);
	gt105_b3_ql2_virtual_pack_avx2(s.c,s.h,s.r,s.m,ct);
	for(size_t i=0;i<NTRUPLUS_SSBYTES;i++)ss[i]=buf[i];
	secure_clear(msg,sizeof msg);secure_clear(buf,sizeof buf);
	secure_clear(s.r,sizeof s.r);secure_clear(s.m,sizeof s.m);return 0;
}

int gt105_encap_virtual_direct(uint8_t *ct,uint8_t *ss,const uint8_t *pk,
	const uint8_t *coins)
{
	uint8_t msg[HASH_H_INBYTES],buf[HASH_H_OUTBYTES]; scratch_t s;
	if(ntruplus768_unpack_m_avx2(s.h,pk)!=0){
		for(size_t i=0;i<NTRUPLUS_CIPHERTEXTBYTES;i++)ct[i]=0;
		secure_clear(ss,NTRUPLUS_SSBYTES);return 1;
	}
	for(size_t i=0;i<NTRUPLUS_N/8;i++)msg[i]=coins[i];
	hash_f(msg+NTRUPLUS_N/8,pk);hash_h(buf,msg);
	poly_cbd1((poly *)(void *)s.m,buf+NTRUPLUS_SYMBYTES);
	ntruplus768_ntt_frontend_avx2(s.c,s.m);ntruplus768_ntt_m_avx2(s.r,s.c);
	ntruplus768_pack_m_lazy10788_avx2(ct,s.r);hash_g(ct,ct);
	poly_sotp_encode((poly *)(void *)s.m,msg,ct);
	ntruplus768_ntt_frontend_avx2(s.c,s.m);gt103_ntt_ql2_avx2(s.m,s.c);
	gt105_b3_ql2_virtual_pack_direct_avx2(s.c,s.h,s.r,s.m,ct);
	for(size_t i=0;i<NTRUPLUS_SSBYTES;i++)ss[i]=buf[i];
	secure_clear(msg,sizeof msg);secure_clear(buf,sizeof buf);
	secure_clear(s.r,sizeof s.r);secure_clear(s.m,sizeof s.m);return 0;
}

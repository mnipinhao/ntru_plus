#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "candidate.h"
#include "internal.h"

static uint64_t state=UINT64_C(0x105b3f00d1234567);
static uint32_t rnd(void){state^=state<<13;state^=state>>7;state^=state<<17;return (uint32_t)state;}
static void pkgen(uint8_t *p){for(int i=0;i<384;i++){uint16_t a=rnd()%3457,b=rnd()%3457;p[3*i]=a;p[3*i+1]=(uint8_t)((a>>8)|(b<<4));p[3*i+2]=(uint8_t)(b>>4);}}
int main(void){
	_Alignas(64) int16_t h[768],r[768],m[768],p[768],scratch[768];
	uint8_t a[1152],b[1152],pk[1152],coins[96],ss0[32],ss1[32];
	for(int t=0;t<1000;t++){
		for(int i=0;i<768;i++){h[i]=(int16_t)((int)(rnd()%3457)-1728);r[i]=(int16_t)((int)(rnd()%3457)-1728);m[i]=(int16_t)((int)(rnd()%21577)-10788);}
		gt103_basemul_general_ql2_avx2(p,h,r);gt103_pack_ql2_sum_avx2(a,p,m);
		gt105_b3_ql2_virtual_pack_avx2(scratch,h,r,m,b);
		if(memcmp(a,b,sizeof a)){for(int i=0;i<1152;i++)if(a[i]!=b[i]){fprintf(stderr,"island mismatch test=%d byte=%d control=%u candidate=%u\n",t,i,a[i],b[i]);break;}return 1;}
		gt105_b3_ql2_virtual_pack_direct_avx2(scratch,h,r,m,b);
		if(memcmp(a,b,sizeof a))return 3;
	}
	for(int t=0;t<1000;t++){
		pkgen(pk);for(int i=0;i<96;i++)coins[i]=(uint8_t)rnd();
		if(ntruplus768_enc_derand_impl(a,ss0,pk,coins)||gt105_encap_virtual(b,ss1,pk,coins)||memcmp(a,b,sizeof a)||memcmp(ss0,ss1,sizeof ss0))return 2;
		if(gt105_encap_virtual_direct(b,ss1,pk,coins)||memcmp(a,b,sizeof a)||memcmp(ss0,ss1,sizeof ss0))return 4;
	}
	puts("PASS island=1000 full-encap=1000 byte-exact");return 0;
}

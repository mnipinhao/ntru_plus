#include "poly.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

extern void official_invntt_ct_lane_native_asm(poly *value);
static uint32_t rng = 0x4354U;
static int maximum_official;
static int maximum_candidate;
static unsigned long long representative_differences;
static uint32_t next_u32(void) { rng = 1664525U*rng + 1013904223U; return rng; }
static int congruent(int a,int b) { return (a-b)%3457 == 0; }

static int check(poly *input, const char *kind, unsigned test)
{
	poly expected=*input, actual=*input;
	poly_invntt_scale(&expected);
	official_invntt_ct_lane_native_asm(&actual);
	for(unsigned i=0;i<768;++i) {
		int official=expected.coeffs[i],candidate=actual.coeffs[i];
		if(official<0) official=-official;
		if(candidate<0) candidate=-candidate;
		if(official>maximum_official) maximum_official=official;
		if(candidate>maximum_candidate) maximum_candidate=candidate;
		if(actual.coeffs[i]!=expected.coeffs[i]) ++representative_differences;
	}
	for(unsigned i=0;i<768;++i) if(!congruent(actual.coeffs[i],expected.coeffs[i])) {
		int maxabs=0;
		for(unsigned j=0;j<768;++j) {
			int value=input->coeffs[j];
			if(value<0) value=-value;
			if(value>maxabs) maxabs=value;
		}
		fprintf(stderr,"lane-native CT mismatch kind=%s test=%u i=%u got=%d want=%d\n",
			kind,test,i,actual.coeffs[i],expected.coeffs[i]);
		fprintf(stderr,"input-maxabs=%d\n",maxabs); return 1;
	}
	return 0;
}

int main(void)
{
	poly a,b,p;
	memset(&p,0,sizeof(p)); if(check(&p,"zero",0)) return 1;
	for(unsigned round=0;round<1000;++round) {
		for(unsigned i=0;i<768;++i)
			p.coeffs[i]=(int16_t)((int)(next_u32()%7U)-3);
		if(check(&p,"arbitrary-small",round)) return 1;
	}
	for(unsigned round=0;round<10000;++round) {
		for(unsigned i=0;i<768;++i) {
			static const int multiple[4]={2,3,4,4};
			const int bound=multiple[(i&63U)/16U]*3457;
			p.coeffs[i]=(int16_t)((int)(next_u32()%(unsigned)(2*bound+1))-bound);
		}
		if(check(&p,"terminal-contract",round)) return 1;
	}
	for(unsigned round=0;round<1000;++round) {
		for(unsigned i=0;i<768;++i) {
			a.coeffs[i]=(int16_t)((int)(next_u32()%3U)-1);
			b.coeffs[i]=(int16_t)((int)(next_u32()%3U)-1);
		}
		poly_ntt(&a); poly_ntt(&b); poly_basemul_scale(&p,&a,&b);
		if(check(&p,"product",round)) return 1;
	}
	for(unsigned round=0;round<1000;++round) {
		for(unsigned i=0;i<768;++i) {
			a.coeffs[i]=(int16_t)((int)(next_u32()%7U)-3);
			b.coeffs[i]=(int16_t)((int)(next_u32()%7U)-3);
		}
		poly_ntt(&a); poly_ntt(&b); poly_basemul_scale(&p,&a,&b);
		if(check(&p,"product-pm3",round)) return 1;
	}
	printf("official-lane-native-ct=passed arbitrary=1000 contract=10000 products=2000 "
	       "maxabs-official=%d maxabs-candidate=%d representative-differences=%llu\n",
	       maximum_official,maximum_candidate,representative_differences);
	return 0;
}

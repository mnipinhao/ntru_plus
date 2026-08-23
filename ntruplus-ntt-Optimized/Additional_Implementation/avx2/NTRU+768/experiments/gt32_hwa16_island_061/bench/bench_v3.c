#define _GNU_SOURCE
#include "hwa16.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SAMPLES 41
#define COMPONENT_ITERS 4000
#define ISLAND_ITERS 1200

typedef void (*unary_fn)(int16_t *, const int16_t *);
typedef void (*binary_fn)(int16_t *, const int16_t *, const int16_t *);
static const char *const names[3] = {"m40a", "m40b", "m40c"};
static const unary_fn fwd[3] = {hwa16_v3_forward_m40a_asm,
	hwa16_v3_forward_m40b_asm, hwa16_v3_forward_m40c_asm};
static const unary_fn inv[3] = {hwa16_v3_inverse_m40a_asm,
	hwa16_v3_inverse_m40b_asm, hwa16_v3_inverse_m40c_asm};
static const binary_fn bm[3] = {hwa16_v3_basemul_m40a_asm,
	hwa16_v3_basemul_m40b_asm, hwa16_v3_basemul_m40c_asm};
static int16_t ta[128] __attribute__((aligned(32)));
static int16_t tb[128] __attribute__((aligned(32)));
static int16_t h[3][2][128] __attribute__((aligned(32)));
static int16_t hf[3][2][128] __attribute__((aligned(32)));
static int16_t tfa[128] __attribute__((aligned(32)));
static int16_t tfb[128] __attribute__((aligned(32)));
static int16_t tp[128] __attribute__((aligned(32)));
static int16_t hp[3][128] __attribute__((aligned(32)));
static int16_t out[128] __attribute__((aligned(32)));
static volatile uint64_t sink;

static uint64_t ticks(void) { unsigned aux; _mm_lfence(); uint64_t x=__rdtscp(&aux); _mm_lfence(); return x; }
static int cmp(const void *a,const void *b) { int64_t x=*(const int64_t*)a,y=*(const int64_t*)b; return (x>y)-(x<y); }
static int64_t median(int64_t *x) { qsort(x,SAMPLES,sizeof(*x),cmp); return x[SAMPLES/2]; }

static uint64_t unary(unary_fn fn,const int16_t *in,unsigned n) {
	uint64_t s=ticks(); for(unsigned i=0;i<n;++i){fn(out,in);sink+=(uint16_t)out[i&127U];} return (ticks()-s)/n;
}
static uint64_t binary(binary_fn fn,const int16_t *a,const int16_t *b,unsigned n) {
	uint64_t s=ticks(); for(unsigned i=0;i<n;++i){fn(out,a,b);sink+=(uint16_t)out[i&127U];} return (ticks()-s)/n;
}
static uint64_t island(int which,unsigned n) {
	int16_t x[128] __attribute__((aligned(32))),y[128] __attribute__((aligned(32))),z[128] __attribute__((aligned(32)));
	uint64_t s=ticks();
	for(unsigned i=0;i<n;++i){
		if(which<0){ctl_tile4_forward_asm(x,ta);ctl_tile4_forward_asm(y,tb);ctl_tile4_basemul_asm(z,x,y);ctl_tile4_inverse_asm(out,z);}
		else{fwd[which](x,h[which][0]);fwd[which](y,h[which][1]);bm[which](z,x,y);inv[which](out,z);}
		sink+=(uint16_t)out[i&127U];
	}
	return (ticks()-s)/n;
}
static void prepare(void) {
	uint64_t s=UINT64_C(0x613abcdef123456);
	for(unsigned i=0;i<128;++i){s^=s<<7;s^=s>>9;ta[i]=(int16_t)((int)(s%3457)-1728);s^=s<<7;s^=s>>9;tb[i]=(int16_t)((int)(s%3457)-1728);}
	ctl_tile4_forward_asm(tfa,ta);ctl_tile4_forward_asm(tfb,tb);ctl_tile4_basemul_asm(tp,tfa,tfb);
	for(int m=0;m<3;++m){hwa16_v3_from_tile4(h[m][0],ta,(enum hwa16_v3_mapping)m);hwa16_v3_from_tile4(h[m][1],tb,(enum hwa16_v3_mapping)m);fwd[m](hf[m][0],h[m][0]);fwd[m](hf[m][1],h[m][1]);bm[m](hp[m],hf[m][0],hf[m][1]);}
}
static void pin(void){cpu_set_t a,o;CPU_ZERO(&a);if(sched_getaffinity(0,sizeof(a),&a))return;for(int c=0;c<CPU_SETSIZE;++c)if(CPU_ISSET(c,&a)){CPU_ZERO(&o);CPU_SET(c,&o);(void)sched_setaffinity(0,sizeof(o),&o);return;}}

static int pmu(const char *variant, const char *component)
{
	int which = -2;
	if (!strcmp(variant, "tile4")) which = -1;
	for (int m = 0; m < 3; ++m)
		if (!strcmp(variant, names[m])) which = m;
	if (which == -2) return 2;
	const unsigned iters = !strcmp(component, "island") ? 300000U : 1000000U;
	if (!strcmp(component, "island")) {
		(void)island(which, iters);
	} else if (!strcmp(component, "forward")) {
		(void)unary(which < 0 ? ctl_tile4_forward_asm : fwd[which],
			which < 0 ? ta : h[which][0], iters);
	} else if (!strcmp(component, "basemul")) {
		(void)binary(which < 0 ? ctl_tile4_basemul_asm : bm[which],
			which < 0 ? tfa : hf[which][0],
			which < 0 ? tfb : hf[which][1], iters);
	} else if (!strcmp(component, "inverse")) {
		(void)unary(which < 0 ? ctl_tile4_inverse_asm : inv[which],
			which < 0 ? tp : hp[which], iters);
	} else {
		return 2;
	}
	printf("%llu\n", (unsigned long long)sink);
	return 0;
}

int main(int argc, char **argv) {
	pin();prepare();
	if (argc == 4 && !strcmp(argv[1], "--pmu"))
		return pmu(argv[2], argv[3]);
	int64_t d[3][4][SAMPLES];
	for(unsigned s=0;s<SAMPLES;++s)for(int m=0;m<3;++m){uint64_t c,v;int rev=(int)((s+(unsigned)m)&1U);
#define MEASURE(slot,ce,ve) do{if(!rev){c=(ce);v=(ve);}else{v=(ve);c=(ce);}d[m][slot][s]=(int64_t)v-(int64_t)c;}while(0)
		MEASURE(0,unary(ctl_tile4_forward_asm,ta,COMPONENT_ITERS),unary(fwd[m],h[m][0],COMPONENT_ITERS));
		MEASURE(1,binary(ctl_tile4_basemul_asm,tfa,tfb,COMPONENT_ITERS),binary(bm[m],hf[m][0],hf[m][1],COMPONENT_ITERS));
		MEASURE(2,unary(ctl_tile4_inverse_asm,tp,COMPONENT_ITERS),unary(inv[m],hp[m],COMPONENT_ITERS));
		MEASURE(3,island(-1,ISLAND_ITERS),island(m,ISLAND_ITERS));
#undef MEASURE
	}
	printf("{\"delta_tsc\":{");
	for(int m=0;m<3;++m){if(m)putchar(',');printf("\"%s\":{\"forward\":%lld,\"basemul\":%lld,\"inverse\":%lld,\"island\":%lld}",names[m],(long long)median(d[m][0]),(long long)median(d[m][1]),(long long)median(d[m][2]),(long long)median(d[m][3]));}
	printf("},\"sink\":%llu}\n",(unsigned long long)sink);return 0;
}

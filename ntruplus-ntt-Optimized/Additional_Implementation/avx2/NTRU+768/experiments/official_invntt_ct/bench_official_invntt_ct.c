#define _GNU_SOURCE
#include "official_invntt_ct.h"
#include "poly.h"

#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { CPU = 3, FIXTURES = 32, SAMPLES = 10001, WARMUP = 2048, CASES = 4 };
static poly products[FIXTURES];
static int16_t mapped[FIXTURES][768] __attribute__((aligned(32)));
static poly official_work;
static int16_t candidate_out[768] __attribute__((aligned(32)));
extern void official_f32x3_rminus1_invntt_ct_asm(int16_t out[768], const int16_t in[768]);

static uint64_t begin_tsc(void) { unsigned l,h; __asm__ volatile("lfence\n\trdtsc":"=a"(l),"=d"(h)::"memory"); return (uint64_t)h<<32|l; }
static uint64_t end_tsc(void) { unsigned l,h,c; __asm__ volatile("rdtscp\n\tlfence":"=a"(l),"=d"(h),"=c"(c)::"memory"); return (uint64_t)h<<32|l; }
static int cmp_u64(const void *a,const void *b) { uint64_t x=*(const uint64_t*)a,y=*(const uint64_t*)b; return (x>y)-(x<y); }
static int cmp_i64(const void *a,const void *b) { int64_t x=*(const int64_t*)a,y=*(const int64_t*)b; return (x>y)-(x<y); }

int main(void)
{
	static uint64_t samples[CASES][SAMPLES];
	static int64_t delta[3][SAMPLES];
	static const char *names[CASES] = {"official-gs", "adapter-only", "ct-only", "ct-common-boundary"};
	cpu_set_t affinity;
	uint32_t random_word = 0x1546U;
	CPU_ZERO(&affinity); CPU_SET(CPU,&affinity);
	if (sched_setaffinity(0,sizeof(affinity),&affinity) != 0) { perror("sched_setaffinity"); return 1; }
	for (unsigned f=0; f<FIXTURES; ++f) {
		poly a,b;
		for (unsigned i=0;i<768;++i) {
			random_word=1664525U*random_word+1013904223U; a.coeffs[i]=(int16_t)((int)(random_word%3U)-1);
			random_word=1664525U*random_word+1013904223U; b.coeffs[i]=(int16_t)((int)(random_word%3U)-1);
		}
		poly_ntt(&a); poly_ntt(&b); poly_basemul_scale(&products[f],&a,&b);
		official_ntt_to_f32x3(mapped[f], products[f].coeffs);
	}
	for (unsigned w=0;w<WARMUP;++w) {
		official_work=products[w&31U]; poly_invntt_scale(&official_work);
		official_ntt_to_f32x3(candidate_out, products[w&31U].coeffs);
		official_f32x3_rminus1_invntt_ct_asm(candidate_out, mapped[w&31U]);
		official_invntt_ct_adapter_y2(candidate_out,products[w&31U].coeffs);
	}
	for (unsigned s=0;s<SAMPLES;++s) {
		unsigned f=(17U*s+9U)&31U;
		for (unsigned p=0;p<CASES;++p) {
			unsigned k=(p+s)%CASES;
			if (k==0) official_work=products[f];
			uint64_t start=begin_tsc();
			if (k==0) poly_invntt_scale(&official_work);
			else if (k==1) official_ntt_to_f32x3(candidate_out,products[f].coeffs);
			else if (k==2) official_f32x3_rminus1_invntt_ct_asm(candidate_out,mapped[f]);
			else official_invntt_ct_adapter_y2(candidate_out,products[f].coeffs);
			samples[k][s]=end_tsc()-start;
		}
		delta[0][s]=(int64_t)samples[2][s]-(int64_t)samples[0][s];
		delta[1][s]=(int64_t)samples[3][s]-(int64_t)samples[0][s];
		delta[2][s]=(int64_t)samples[3][s]-(int64_t)samples[2][s];
	}
	for(unsigned k=0;k<CASES;++k) { qsort(samples[k],SAMPLES,sizeof(uint64_t),cmp_u64); printf("%s median=%llu p10=%llu p90=%llu\n",names[k],(unsigned long long)samples[k][SAMPLES/2],(unsigned long long)samples[k][SAMPLES/10],(unsigned long long)samples[k][9*SAMPLES/10]); }
	for(unsigned k=0;k<3;++k) { static const char *labels[3]={"ct_only_minus_gs","common_minus_gs","common_minus_ct_only"}; qsort(delta[k],SAMPLES,sizeof(int64_t),cmp_i64); printf("%s median=%lld p10=%lld p90=%lld\n",labels[k],(long long)delta[k][SAMPLES/2],(long long)delta[k][SAMPLES/10],(long long)delta[k][9*SAMPLES/10]); }
	return 0;
}

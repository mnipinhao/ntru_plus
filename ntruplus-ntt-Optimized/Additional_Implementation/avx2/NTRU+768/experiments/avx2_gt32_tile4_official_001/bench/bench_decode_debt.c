#define _GNU_SOURCE
#include <linux/perf_event.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <x86intrin.h>

#include "tile4.h"

enum { WORDS = 768, BYTES = 1152, SAMPLES = 20 };
typedef void (*bench_fn)(void);

extern int gt32_q24_decode_soa_noval_asm(int16_t *, const uint8_t *);
extern int gt32_q24_decode_wire_asm(int16_t *, const uint8_t *);
extern void gt32_q24_route_wire_to_soa_asm(int16_t *, const int16_t *);

static _Alignas(64) uint8_t encoded[BYTES];
static _Alignas(64) int16_t control_m[WORDS], candidate_m[WORDS];
static _Alignas(64) int16_t wire[WORDS], expected_wire[WORDS];
static volatile uint64_t sink;

static void encode_wire(const int16_t input[WORDS])
{
	for (unsigned pair = 0; pair < WORDS / 2; pair++) {
		const unsigned x = (unsigned)input[2 * pair];
		const unsigned y = (unsigned)input[2 * pair + 1];
		encoded[3 * pair] = (uint8_t)x;
		encoded[3 * pair + 1] = (uint8_t)(x >> 8) | (uint8_t)(y << 4);
		encoded[3 * pair + 2] = (uint8_t)(y >> 4);
	}
}

static int correctness(void)
{
	uint32_t state = UINT32_C(0xdec0de01);
	for (unsigned trial = 0; trial < 1000; trial++) {
		for (unsigned i = 0; i < WORDS; i++) {
			state = state * UINT32_C(1664525) + UINT32_C(1013904223);
			expected_wire[i] = (int16_t)(state % GT32_TILE4_Q);
		}
		encode_wire(expected_wire);
		if (gt32_q24_decode_soa_asm(control_m, encoded) != 0
			|| gt32_q24_decode_soa_noval_asm(candidate_m, encoded) != 0
			|| memcmp(control_m, candidate_m, sizeof control_m) != 0)
			return 0;
		if (gt32_q24_decode_wire_asm(wire, encoded) != 0
			|| memcmp(wire, expected_wire, sizeof wire) != 0)
			return 0;
		gt32_q24_route_wire_to_soa_asm(candidate_m, wire);
		if (memcmp(control_m, candidate_m, sizeof control_m) != 0)
			return 0;
	}
	/* D1 intentionally changes only rejection reporting, not decoded words. */
	memset(encoded, 0, sizeof encoded);
	encoded[0] = (uint8_t)GT32_TILE4_Q;
	encoded[1] = (uint8_t)(GT32_TILE4_Q >> 8);
	if (gt32_q24_decode_soa_asm(control_m, encoded) != 1
		|| gt32_q24_decode_soa_noval_asm(candidate_m, encoded) != 0
		|| memcmp(control_m, candidate_m, sizeof control_m) != 0
		|| gt32_q24_decode_wire_asm(wire, encoded) != 1)
		return 0;
	return 1;
}

static void d0(void) { sink += (unsigned)gt32_q24_decode_soa_asm(control_m, encoded); }
static void d1(void) { sink += (unsigned)gt32_q24_decode_soa_noval_asm(candidate_m, encoded); }
static void d2_unpack(void) { sink += (unsigned)gt32_q24_decode_wire_asm(wire, encoded); }
static void d2_route(void) { gt32_q24_route_wire_to_soa_asm(candidate_m, wire); sink += (uint16_t)candidate_m[0]; }
static void d2_split(void) { d2_unpack(); d2_route(); }

static uint64_t start_tsc(void) { _mm_lfence(); return __rdtsc(); }
static uint64_t stop_tsc(void) { unsigned aux; uint64_t x = __rdtscp(&aux); _mm_lfence(); return x; }
static double measure_tsc(bench_fn fn, unsigned n) { uint64_t a=start_tsc(); for(unsigned i=0;i<n;i++)fn(); return (double)(stop_tsc()-a)/n; }
static int perf_open(uint64_t config) {
	struct perf_event_attr a; memset(&a,0,sizeof a); a.type=PERF_TYPE_HARDWARE;
	a.size=sizeof a; a.config=config; a.disabled=1; a.exclude_kernel=1; a.exclude_hv=1;
	return (int)syscall(SYS_perf_event_open,&a,0,-1,-1,0UL);
}
static double measure_perf(bench_fn fn,unsigned n,int fd) {
	uint64_t x=0; ioctl(fd,PERF_EVENT_IOC_RESET,0); ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
	for(unsigned i=0;i<n;i++) fn();
	ioctl(fd,PERF_EVENT_IOC_DISABLE,0);
	if(read(fd,&x,sizeof x)!=(ssize_t)sizeof x) return 0;
	return (double)x/n;
}
static int cmp(const void *a,const void *b) { double x=*(const double*)a,y=*(const double*)b; return (x>y)-(x<y); }
static double median(double x[SAMPLES]) { double y[SAMPLES]; memcpy(y,x,sizeof y); qsort(y,SAMPLES,sizeof y[0],cmp); return .5*(y[9]+y[10]); }
static void metric(const char *region,const char *name,bench_fn fn,unsigned n,int fd) {
	double x[SAMPLES];
	for(unsigned i=0;i<SAMPLES;i++) x[i]=fd<0?measure_tsc(fn,n):measure_perf(fn,n,fd);
	printf("region=%s metric=%s value=%.3f\n",region,name,median(x));
}

int main(int argc, char **argv)
{
	const unsigned n=argc>1?(unsigned)strtoul(argv[1],NULL,0):4000;
	const unsigned cpu=argc>2?(unsigned)strtoul(argv[2],NULL,0):1;
	cpu_set_t set; CPU_ZERO(&set); CPU_SET(cpu,&set);
	if (sched_setaffinity(0,sizeof set,&set)) return 2;
	if (!correctness()) { fprintf(stderr,"correctness failed\n"); return 1; }
	for (unsigned i=0;i<WORDS;i++) expected_wire[i]=(int16_t)((37*i+11)%GT32_TILE4_Q);
	encode_wire(expected_wire);
	gt32_q24_decode_wire_asm(wire, encoded);
	for (unsigned i=0;i<100;i++) { d0(); d1(); d2_split(); }
	int cycles=perf_open(PERF_COUNT_HW_CPU_CYCLES);
	int instructions=perf_open(PERF_COUNT_HW_INSTRUCTIONS);
	printf("iterations=%u cpu=%u correctness=pass\n",n,cpu);
	bench_fn fns[]={d0,d1,d2_unpack,d2_route,d2_split};
	const char *names[]={"d0_full","d1_no_validation","d2_unpack","d2_route","d2_split"};
	for(unsigned i=0;i<5;i++) {
		metric(names[i],"tsc",fns[i],n,-1);
		metric(names[i],"core_cycles",fns[i],n,cycles);
		metric(names[i],"instructions",fns[i],n,instructions);
	}
	if (cycles >= 0)
		close(cycles);
	if (instructions >= 0)
		close(instructions);
	printf("sink=%llu\n",(unsigned long long)sink);
	return 0;
}

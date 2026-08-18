#define _GNU_SOURCE
#include <linux/perf_event.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <x86intrin.h>

#include "tile4.h"
#include "../generated/tile4_serialized_mapping.h"

enum { WORDS = GT32_TILE4_POLY_WORDS, BYTES = GT32_TILE4_SERIALIZED_BYTES,
	SAMPLES = 20 };
typedef void (*bench_fn)(void);
static _Alignas(64) int16_t input_a[WORDS], input_b[WORDS];
static _Alignas(64) uint8_t output_a[BYTES], output_b[BYTES];
static volatile uint64_t sink;

static void reference_pack(uint8_t out[BYTES], const int16_t in[WORDS]) {
	for (unsigned pair = 0; pair < WORDS / 2; pair++) {
		int x = in[gt32_tile4_serialized_to_bm_soa[2 * pair]] % GT32_TILE4_Q;
		int y = in[gt32_tile4_serialized_to_bm_soa[2 * pair + 1]] % GT32_TILE4_Q;
		if (x < 0) x += GT32_TILE4_Q;
		if (y < 0) y += GT32_TILE4_Q;
		out[3 * pair] = (uint8_t)x;
		out[3 * pair + 1] = (uint8_t)((unsigned)x >> 8)
			| (uint8_t)((unsigned)y << 4);
		out[3 * pair + 2] = (uint8_t)((unsigned)y >> 4);
	}
}

static int correctness(void) {
	uint8_t expected[BYTES];
	for (int value = -12699; value <= 12699; value++) {
		for (unsigned i = 0; i < WORDS; i++) input_a[i] = (int16_t)value;
		reference_pack(expected, input_a);
		gt32_q24_encode_soa_lazy10788_asm(output_a, input_a);
		gt32_q24_encode_soa_lazy10788_compact_c1_asm(output_b, input_a);
		if (memcmp(expected, output_a, BYTES) || memcmp(expected, output_b, BYTES)) {
			for (unsigned i = 0; i < BYTES; i++)
				if (expected[i] != output_b[i]) {
					fprintf(stderr, "compact C1 mismatch value=%d byte=%u expected=%u actual=%u\n",
						value, i, expected[i], output_b[i]);
					for (unsigned j = i & ~15U; j < (i & ~15U) + 32U; j++)
						fprintf(stderr, "%u:%u/%u%c", j, expected[j], output_b[j],
							(j & 7U) == 7U ? '\n' : ' ');
					break;
				}
			return 0;
		}
	}
	long page = sysconf(_SC_PAGESIZE);
	uint8_t *map = mmap(NULL, (size_t)(2 * page), PROT_READ | PROT_WRITE,
		MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
	if (map == MAP_FAILED || mprotect(map + page, (size_t)page, PROT_NONE)) return 0;
	uint8_t *edge = map + page - BYTES;
	gt32_q24_encode_soa_lazy10788_compact_c1_asm(edge, input_a);
	if (munmap(map, (size_t)(2 * page))) return 0;
	return 1;
}

static void control_one(void) { gt32_q24_encode_soa_lazy10788_asm(output_a, input_a); sink += output_a[0]; }
static void candidate_one(void) { gt32_q24_encode_soa_lazy10788_compact_c1_asm(output_a, input_a); sink += output_a[0]; }
static void control_two(void) { control_one(); gt32_q24_encode_soa_lazy10788_asm(output_b, input_b); sink += output_b[0]; }
static void candidate_two(void) { candidate_one(); gt32_q24_encode_soa_lazy10788_compact_c1_asm(output_b, input_b); sink += output_b[0]; }
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
static void metric(const char *region,const char *name,bench_fn a,bench_fn b,unsigned n,int fd) {
	double x[SAMPLES],y[SAMPLES],d[SAMPLES]; unsigned wins=0;
	for(unsigned i=0;i<SAMPLES;i++) { if(i&1){y[i]=fd<0?measure_tsc(b,n):measure_perf(b,n,fd);x[i]=fd<0?measure_tsc(a,n):measure_perf(a,n,fd);}else{x[i]=fd<0?measure_tsc(a,n):measure_perf(a,n,fd);y[i]=fd<0?measure_tsc(b,n):measure_perf(b,n,fd);} d[i]=y[i]-x[i]; wins+=d[i]<0; }
	printf("region=%s metric=%s control=%.3f candidate=%.3f delta=%.3f wins=%u/%u\n",region,name,median(x),median(y),median(d),wins,SAMPLES);
}
int main(int argc,char **argv) {
	unsigned n=argc>1?(unsigned)strtoul(argv[1],NULL,0):4000,cpu=argc>2?(unsigned)strtoul(argv[2],NULL,0):1;
	cpu_set_t set; CPU_ZERO(&set); CPU_SET(cpu,&set); if(sched_setaffinity(0,sizeof set,&set))return 2;
	if(!correctness())return 1;
	for(unsigned i=0;i<WORDS;i++){input_a[i]=(int16_t)((int)(37*i%21577)-10788);input_b[i]=(int16_t)((int)(61*i%25399)-12699);}
	for(unsigned i=0;i<100;i++){control_two();candidate_two();}
	int cycles=perf_open(PERF_COUNT_HW_CPU_CYCLES),instructions=perf_open(PERF_COUNT_HW_INSTRUCTIONS);
	printf("iterations=%u cpu=%u correctness=pass\n",n,cpu);
	metric("one_q24","tsc",control_one,candidate_one,n,-1); metric("one_q24","core_cycles",control_one,candidate_one,n,cycles); metric("one_q24","instructions",control_one,candidate_one,n,instructions);
	metric("two_q24","tsc",control_two,candidate_two,n,-1); metric("two_q24","core_cycles",control_two,candidate_two,n,cycles); metric("two_q24","instructions",control_two,candidate_two,n,instructions);
	if(cycles>=0) close(cycles);
	if(instructions>=0) close(instructions);
	printf("sink=%llu\n",(unsigned long long)sink);
	return 0;
}

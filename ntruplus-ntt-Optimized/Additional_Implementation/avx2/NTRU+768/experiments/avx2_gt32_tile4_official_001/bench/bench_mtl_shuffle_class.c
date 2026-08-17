#define _GNU_SOURCE
#include <errno.h>
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

#define DECLARE(name) void name(uint64_t)
DECLARE(mtl_shuffle_empty);
DECLARE(mtl_perm_1); DECLARE(mtl_perm_2); DECLARE(mtl_perm_4); DECLARE(mtl_perm_8);
DECLARE(mtl_unpackw_1); DECLARE(mtl_unpackw_2); DECLARE(mtl_unpackw_4); DECLARE(mtl_unpackw_8);
DECLARE(mtl_unpackd_1); DECLARE(mtl_unpackd_2); DECLARE(mtl_unpackd_4); DECLARE(mtl_unpackd_8);
DECLARE(mtl_unpackq_1); DECLARE(mtl_unpackq_2); DECLARE(mtl_unpackq_4); DECLARE(mtl_unpackq_8);
DECLARE(mtl_mix_base16); DECLARE(mtl_mix_free8_16); DECLARE(mtl_mix_balanced12_8);
DECLARE(mtl_mix_balanced10_12); DECLARE(mtl_mix_balanced8_12); DECLARE(mtl_mix_dependency_free);
DECLARE(mtl_mix_arith_base16); DECLARE(mtl_mix_arith_free8_16);
DECLARE(mtl_mix_arith_dependency_free);

typedef void (*kernel_t)(uint64_t);
typedef struct { const char *kind; int streams; kernel_t fn; } entry_t;
typedef struct { double tsc, cycles, instructions, ref_cycles; } sample_t;
typedef struct { int leader, instructions, ref_cycles, available; } pmu_t;

static int perf_open(uint64_t config, int group, int disabled)
{
	struct perf_event_attr attr;
	memset(&attr, 0, sizeof attr);
	attr.type = PERF_TYPE_HARDWARE;
	attr.size = sizeof attr;
	attr.config = config;
	attr.disabled = disabled != 0;
	attr.exclude_kernel = 1;
	attr.exclude_hv = 1;
	if (disabled) attr.read_format = PERF_FORMAT_GROUP;
	return (int)syscall(SYS_perf_event_open, &attr, 0, -1, group, 0UL);
}

static pmu_t pmu_open(void)
{
	pmu_t p = {-1, -1, -1, 0};
	p.leader = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1, 1);
	if (p.leader < 0) return p;
	p.instructions = perf_open(PERF_COUNT_HW_INSTRUCTIONS, p.leader, 0);
	p.ref_cycles = perf_open(PERF_COUNT_HW_REF_CPU_CYCLES, p.leader, 0);
	if (p.instructions < 0 || p.ref_cycles < 0) return p;
	p.available = 1;
	return p;
}

static sample_t measure(kernel_t fn, uint64_t iterations, pmu_t *pmu)
{
	uint64_t counts[4] = {0, 0, 0, 0};
	unsigned aux;
	sample_t s = {0, 0, 0, 0};
	if (pmu->available) {
		ioctl(pmu->leader, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
		ioctl(pmu->leader, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
	}
	_mm_lfence();
	uint64_t begin = __rdtsc();
	fn(iterations);
	uint64_t end = __rdtscp(&aux);
	_mm_lfence();
	if (pmu->available) {
		ioctl(pmu->leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
		if (read(pmu->leader, counts, sizeof counts) != (ssize_t)sizeof counts || counts[0] != 3)
			pmu->available = 0;
	}
	s.tsc = (double)(end - begin);
	if (pmu->available) {
		s.cycles = (double)counts[1];
		s.instructions = (double)counts[2];
		s.ref_cycles = (double)counts[3];
	}
	return s;
}

static int compare_double(const void *a, const void *b)
{
	double x = *(const double *)a, y = *(const double *)b;
	return (x > y) - (x < y);
}

static sample_t median_samples(sample_t *samples, int n)
{
	double t[31], c[31], i[31], r[31];
	for (int k = 0; k < n; ++k) {
		t[k] = samples[k].tsc; c[k] = samples[k].cycles;
		i[k] = samples[k].instructions; r[k] = samples[k].ref_cycles;
	}
	qsort(t, n, sizeof *t, compare_double); qsort(c, n, sizeof *c, compare_double);
	qsort(i, n, sizeof *i, compare_double); qsort(r, n, sizeof *r, compare_double);
	return (sample_t){t[n/2], c[n/2], i[n/2], r[n/2]};
}

int main(int argc, char **argv)
{
	uint64_t iterations = argc > 1 ? strtoull(argv[1], 0, 10) : 200000;
	int repeats = argc > 2 ? atoi(argv[2]) : 15;
	int cpu = argc > 3 ? atoi(argv[3]) : 1;
	if (repeats < 3 || repeats > 31 || !(repeats & 1)) return 2;
	cpu_set_t set; CPU_ZERO(&set); CPU_SET(cpu, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0) {
		fprintf(stderr, "affinity cpu %d failed: %s\n", cpu, strerror(errno)); return 2;
	}
	entry_t entries[] = {
		{"vperm2i128",1,mtl_perm_1},{"vperm2i128",2,mtl_perm_2},{"vperm2i128",4,mtl_perm_4},{"vperm2i128",8,mtl_perm_8},
		{"unpack16",1,mtl_unpackw_1},{"unpack16",2,mtl_unpackw_2},{"unpack16",4,mtl_unpackw_4},{"unpack16",8,mtl_unpackw_8},
		{"unpack32",1,mtl_unpackd_1},{"unpack32",2,mtl_unpackd_2},{"unpack32",4,mtl_unpackd_4},{"unpack32",8,mtl_unpackd_8},
		{"unpack64",1,mtl_unpackq_1},{"unpack64",2,mtl_unpackq_2},{"unpack64",4,mtl_unpackq_4},{"unpack64",8,mtl_unpackq_8}
	};
	struct { const char *name; int global, local, arithmetic; kernel_t fn; } mixes[] = {
		{"base16",16,0,0,mtl_mix_base16},
		{"free8_16",8,16,0,mtl_mix_free8_16},
		{"balanced12_8",12,8,0,mtl_mix_balanced12_8},
		{"balanced10_12",10,12,0,mtl_mix_balanced10_12},
		{"balanced8_12",8,12,0,mtl_mix_balanced8_12},
		{"dependency_free8_16",8,16,0,mtl_mix_dependency_free},
		{"arith_base16",16,0,24,mtl_mix_arith_base16},
		{"arith_free8_16",8,16,24,mtl_mix_arith_free8_16},
		{"arith_dependency_free8_16",8,16,24,mtl_mix_arith_dependency_free}
	};
	pmu_t pmu = pmu_open();
	if (!pmu.available) { fprintf(stderr, "perf_event_open failed\n"); return 3; }
	mtl_shuffle_empty(1000);
	sample_t empty_samples[31];
	for (int k=0;k<repeats;++k) empty_samples[k]=measure(mtl_shuffle_empty,iterations,&pmu);
	sample_t empty=median_samples(empty_samples,repeats);
	printf("{\"cpu\":%d,\"iterations\":%llu,\"repeats\":%d,\"results\":[",cpu,(unsigned long long)iterations,repeats);
	for (size_t e=0;e<sizeof entries/sizeof entries[0];++e) {
		entries[e].fn(1000); sample_t samples[31];
		for (int k=0;k<repeats;++k) samples[k]=measure(entries[e].fn,iterations,&pmu);
		sample_t m=median_samples(samples,repeats); double ops=(double)iterations*64.0;
		if (e) putchar(',');
		printf("{\"kind\":\"%s\",\"streams\":%d,\"core_per_op\":%.9f,\"tsc_per_op\":%.9f,\"instructions_per_op\":%.9f,\"ref_per_op\":%.9f}",
			entries[e].kind,entries[e].streams,(m.cycles-empty.cycles)/ops,(m.tsc-empty.tsc)/ops,
			(m.instructions-empty.instructions)/ops,(m.ref_cycles-empty.ref_cycles)/ops);
	}
	printf("],\"mix_results\":[");
	for (size_t e=0;e<sizeof mixes/sizeof mixes[0];++e) {
		mixes[e].fn(1000); sample_t samples[31];
		for (int k=0;k<repeats;++k) samples[k]=measure(mixes[e].fn,iterations,&pmu);
		sample_t m=median_samples(samples,repeats);
		if (e) putchar(',');
		printf("{\"name\":\"%s\",\"global\":%d,\"local\":%d,\"arithmetic\":%d,\"core_per_tile\":%.9f,\"tsc_per_tile\":%.9f,\"instructions_per_tile\":%.9f}",
			mixes[e].name,mixes[e].global,mixes[e].local,mixes[e].arithmetic,
			(m.cycles-empty.cycles)/(double)iterations,(m.tsc-empty.tsc)/(double)iterations,
			(m.instructions-empty.instructions)/(double)iterations);
	}
	puts("]}");
	return 0;
}

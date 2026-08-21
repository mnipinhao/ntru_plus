#define _GNU_SOURCE
#include <errno.h>
#include <immintrin.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#define N 768
#define POLYBYTES 1152

void ntruplus768_ntt_frontend_avx2(int16_t *, const int16_t *);
void ntruplus768_ntt_m_avx2(int16_t *, const int16_t *);
void ntruplus768_ntt_p_avx2(int16_t *, const int16_t *);
void ntruplus768_basemul_scale_m_avx2(int16_t *, const int16_t *, const int16_t *);
void ntruplus768_basemul_general_m_avx2(int16_t *, const int16_t *, const int16_t *);
void ntruplus768_invntt_m_avx2(int16_t *, const int16_t *);
void ntruplus768_invntt_tail_avx2(int16_t *, const int16_t *);
void ntruplus768_pack_m_lazy10788_avx2(uint8_t *, const int16_t *);
void poly_add(void *, const void *, const void *);
void poly_crepmod3(void *);

static int16_t coeff_a[N] __attribute__((aligned(64)));
static int16_t coeff_b[N] __attribute__((aligned(64)));
static int16_t front_a[N] __attribute__((aligned(64)));
static int16_t front_b[N] __attribute__((aligned(64)));
static int16_t m_a[N] __attribute__((aligned(64)));
static int16_t m_b[N] __attribute__((aligned(64)));
static int16_t product[N] __attribute__((aligned(64)));
static int16_t inv_stage[N] __attribute__((aligned(64)));
static int16_t work0[N] __attribute__((aligned(64)));
static int16_t work1[N] __attribute__((aligned(64)));
static uint8_t packed[POLYBYTES] __attribute__((aligned(64)));

static volatile uint64_t sink;

static uint64_t start_tsc(void)
{
	_mm_lfence();
	return __rdtsc();
}

static uint64_t stop_tsc(void)
{
	unsigned aux;
	const uint64_t value = __rdtscp(&aux);
	_mm_lfence();
	return value;
}

static int perf_open(uint64_t config)
{
	struct perf_event_attr attr;
	memset(&attr, 0, sizeof attr);
	attr.type = PERF_TYPE_HARDWARE;
	attr.size = sizeof attr;
	attr.config = config;
	attr.disabled = 1;
	attr.exclude_kernel = 1;
	attr.exclude_hv = 1;
	return (int)syscall(SYS_perf_event_open, &attr, 0, -1, -1, 0UL);
}

enum region {
	REG_FRONTEND_M,
	REG_FRONTEND_P,
	REG_NTTM_PACK,
	REG_NTTM_B3,
	REG_B3SCALE_INV,
	REG_B3GENERAL_ADD,
	REG_INVCORE_TAIL,
	REG_INVTAIL_CREP
};

static enum region parse_region(const char *name)
{
	if (strcmp(name, "frontend_m") == 0) return REG_FRONTEND_M;
	if (strcmp(name, "frontend_p") == 0) return REG_FRONTEND_P;
	if (strcmp(name, "nttm_pack") == 0) return REG_NTTM_PACK;
	if (strcmp(name, "nttm_b3") == 0) return REG_NTTM_B3;
	if (strcmp(name, "b3scale_inv") == 0) return REG_B3SCALE_INV;
	if (strcmp(name, "b3general_add") == 0) return REG_B3GENERAL_ADD;
	if (strcmp(name, "invcore_tail") == 0) return REG_INVCORE_TAIL;
	if (strcmp(name, "invtail_crep") == 0) return REG_INVTAIL_CREP;
	fprintf(stderr, "unknown region: %s\n", name);
	exit(2);
}

__attribute__((noinline))
static void run_once(enum region region)
{
	switch (region) {
	case REG_FRONTEND_M:
		ntruplus768_ntt_frontend_avx2(work0, coeff_a);
		ntruplus768_ntt_m_avx2(work1, work0);
		break;
	case REG_FRONTEND_P:
		ntruplus768_ntt_frontend_avx2(work0, coeff_a);
		ntruplus768_ntt_p_avx2(work1, work0);
		break;
	case REG_NTTM_PACK:
		ntruplus768_ntt_m_avx2(work0, front_a);
		ntruplus768_pack_m_lazy10788_avx2(packed, work0);
		break;
	case REG_NTTM_B3:
		ntruplus768_ntt_m_avx2(work0, front_a);
		ntruplus768_basemul_general_m_avx2(work1, work0, m_b);
		break;
	case REG_B3SCALE_INV:
		ntruplus768_basemul_scale_m_avx2(work0, m_a, m_b);
		ntruplus768_invntt_m_avx2(work1, work0);
		break;
	case REG_B3GENERAL_ADD:
		ntruplus768_basemul_general_m_avx2(work0, m_a, m_b);
		poly_add(work1, work0, m_a);
		break;
	case REG_INVCORE_TAIL:
		ntruplus768_invntt_m_avx2(work0, product);
		ntruplus768_invntt_tail_avx2(work1, work0);
		break;
	case REG_INVTAIL_CREP:
		memcpy(work0, inv_stage, sizeof work0);
		ntruplus768_invntt_tail_avx2(work1, work0);
		poly_crepmod3(work1);
		break;
	}
	sink += (uint16_t)work1[(unsigned)region * 73U % N] + packed[0];
}

static int compare_u64(const void *left, const void *right)
{
	const uint64_t a = *(const uint64_t *)left;
	const uint64_t b = *(const uint64_t *)right;
	return (a > b) - (a < b);
}

static double measure_tsc(enum region region, unsigned iterations)
{
	uint64_t samples[31];
	for (unsigned sample = 0; sample < 31; sample++) {
		const uint64_t begin = start_tsc();
		for (unsigned i = 0; i < iterations; i++) run_once(region);
		const uint64_t end = stop_tsc();
		samples[sample] = end - begin;
	}
	qsort(samples, 31, sizeof samples[0], compare_u64);
	return (double)samples[15] / (double)iterations;
}

static double measure_perf(enum region region, unsigned iterations,
	uint64_t config)
{
	const int fd = perf_open(config);
	uint64_t samples[15];
	if (fd < 0) return -1.0;
	for (unsigned sample = 0; sample < 15; sample++) {
		uint64_t count = 0;
		(void)ioctl(fd, PERF_EVENT_IOC_RESET, 0);
		(void)ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);
		for (unsigned i = 0; i < iterations; i++) run_once(region);
		(void)ioctl(fd, PERF_EVENT_IOC_DISABLE, 0);
		if (read(fd, &count, sizeof count) != (ssize_t)sizeof count)
			count = 0;
		samples[sample] = count;
	}
	close(fd);
	qsort(samples, 15, sizeof samples[0], compare_u64);
	return (double)samples[7] / (double)iterations;
}

static void initialize(void)
{
	uint32_t state = 1;
	for (unsigned i = 0; i < N; i++) {
		state = state * 1664525U + 1013904223U;
		coeff_a[i] = (int16_t)((int)(state % 3U) - 1);
		state = state * 1664525U + 1013904223U;
		coeff_b[i] = (int16_t)((int)(state % 3U) - 1);
	}
	ntruplus768_ntt_frontend_avx2(front_a, coeff_a);
	ntruplus768_ntt_frontend_avx2(front_b, coeff_b);
	ntruplus768_ntt_m_avx2(m_a, front_a);
	ntruplus768_ntt_m_avx2(m_b, front_b);
	ntruplus768_basemul_scale_m_avx2(product, m_a, m_b);
	ntruplus768_invntt_m_avx2(inv_stage, product);
}

int main(int argc, char **argv)
{
	if (argc != 2) {
		fprintf(stderr, "usage: %s REGION\n", argv[0]);
		return 2;
	}
	initialize();
	const enum region region = parse_region(argv[1]);
	for (unsigned i = 0; i < 200; i++) run_once(region);
	const unsigned iterations = 10000;
	const double tsc = measure_tsc(region, iterations);
	const double cycles = measure_perf(region, iterations,
		PERF_COUNT_HW_CPU_CYCLES);
	const double instructions = measure_perf(region, iterations,
		PERF_COUNT_HW_INSTRUCTIONS);
	printf("region=%s tsc=%.6f core=%.6f instructions=%.6f sink=%" PRIu64 "\n",
		argv[1], tsc, cycles, instructions, sink);
	return 0;
}

#define _GNU_SOURCE
#include "late_soa.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SAMPLES 41
#define COMPONENT_ITERS 6000U
#define FULL_ITERS 2500U

static int16_t in_a[128] __attribute__((aligned(32)));
static int16_t in_b[128] __attribute__((aligned(32)));
static int16_t aos_a[128] __attribute__((aligned(32)));
static int16_t aos_b[128] __attribute__((aligned(32)));
static int16_t soa_a[128] __attribute__((aligned(32)));
static int16_t soa_b[128] __attribute__((aligned(32)));
static int16_t tmp0[128] __attribute__((aligned(32)));
static int16_t tmp1[128] __attribute__((aligned(32)));
static int16_t tmp2[128] __attribute__((aligned(32)));
static int16_t out[128] __attribute__((aligned(32)));
static volatile uint64_t sink;

static uint64_t ticks(void)
{
	unsigned aux;
	_mm_lfence();
	const uint64_t t = __rdtscp(&aux);
	_mm_lfence();
	return t;
}

static int cmp64(const void *a, const void *b)
{
	const int64_t x = *(const int64_t *)a, y = *(const int64_t *)b;
	return (x > y) - (x < y);
}

static int64_t median(int64_t *x)
{
	qsort(x, SAMPLES, sizeof(*x), cmp64);
	return x[SAMPLES / 2];
}

static void control_bmi2(void)
{
	ctl_tile4_basemul_asm(tmp0, aos_a, aos_b);
	late_inverse_i2_asm(out, tmp0);
}

static void run_once(unsigned variant, unsigned component)
{
	if (component == 0) {
		if (variant == 2) {
			late_suffix_soa_asm(tmp0, in_a);
			late_suffix_soa_asm(tmp1, in_b);
		} else {
			late_suffix_aos_asm(tmp0, in_a);
			late_suffix_aos_asm(tmp1, in_b);
		}
		memcpy(out, tmp1, sizeof(out));
	} else if (component == 1) {
		if (variant == 0) control_bmi2();
		else if (variant == 1) late_aos_basemul_i2_fused_asm(out, aos_a, aos_b);
		else late_soa_basemul_i2_fused_asm(out, soa_a, soa_b);
	} else {
		if (variant == 0) {
			late_suffix_aos_asm(tmp0, in_a);
			late_suffix_aos_asm(tmp1, in_b);
			ctl_tile4_basemul_asm(tmp2, tmp0, tmp1);
			late_inverse_i2_asm(out, tmp2);
		} else if (variant == 1) {
			late_suffix_aos_asm(tmp0, in_a);
			late_suffix_aos_asm(tmp1, in_b);
			late_aos_basemul_i2_fused_asm(out, tmp0, tmp1);
		} else {
			late_suffix_soa_asm(tmp0, in_a);
			late_suffix_soa_asm(tmp1, in_b);
			late_soa_basemul_i2_fused_asm(out, tmp0, tmp1);
		}
	}
}

static uint64_t run(unsigned variant, unsigned component, unsigned iters)
{
	const uint64_t begin = ticks();
	for (unsigned i = 0; i < iters; ++i) {
		run_once(variant, component);
		sink += (uint16_t)out[i & 127U];
	}
	return (ticks() - begin) / iters;
}

static void prepare(void)
{
	uint64_t s = UINT64_C(0x063123456789abcd);
	for (unsigned i = 0; i < 128; ++i) {
		s ^= s << 7; s ^= s >> 9;
		in_a[i] = (int16_t)((int)(s % 3457U) - 1728);
		s ^= s << 7; s ^= s >> 9;
		in_b[i] = (int16_t)((int)(s % 3457U) - 1728);
	}
	late_suffix_aos_asm(aos_a, in_a);
	late_suffix_aos_asm(aos_b, in_b);
	late_suffix_soa_asm(soa_a, in_a);
	late_suffix_soa_asm(soa_b, in_b);
}

static void pin_first_cpu(void)
{
	cpu_set_t available, one;
	CPU_ZERO(&available);
	if (sched_getaffinity(0, sizeof(available), &available) != 0) return;
	for (int cpu = 0; cpu < CPU_SETSIZE; ++cpu) if (CPU_ISSET(cpu, &available)) {
		CPU_ZERO(&one); CPU_SET(cpu, &one);
		(void)sched_setaffinity(0, sizeof(one), &one);
		return;
	}
}

static int pmu(const char *vname, const char *cname)
{
	const unsigned variant = !strcmp(vname, "c0") ? 0U :
		(!strcmp(vname, "c1") ? 1U : 2U);
	const unsigned component = !strcmp(cname, "suffix2") ? 0U :
		(!strcmp(cname, "bmi2") ? 1U : 2U);
	const unsigned iters = component == 2 ? 1000000U : 2000000U;
	(void)run(variant, component, iters);
	printf("%llu\n", (unsigned long long)sink);
	return 0;
}
int main(int argc, char **argv)
{
	pin_first_cpu();
	prepare();
	if (argc == 4 && !strcmp(argv[1], "--pmu")) return pmu(argv[2], argv[3]);
	int64_t c1_suffix[SAMPLES], l0_suffix[SAMPLES];
	int64_t c1_bmi2[SAMPLES], l0_bmi2[SAMPLES];
	int64_t c1_full[SAMPLES], l0_full[SAMPLES];
	for (unsigned s = 0; s < SAMPLES; ++s) {
		const int reverse = (int)(s & 1U);
		for (unsigned component = 0; component < 3; ++component) {
			const unsigned iters = component == 2 ? FULL_ITERS : COMPONENT_ITERS;
			uint64_t ctl, c1, l0;
			if (!reverse) {
				ctl = run(0, component, iters);
				c1 = run(1, component, iters);
				l0 = run(2, component, iters);
			} else {
				l0 = run(2, component, iters);
				c1 = run(1, component, iters);
				ctl = run(0, component, iters);
			}
			int64_t *d1 = component == 0 ? c1_suffix :
				(component == 1 ? c1_bmi2 : c1_full);
			int64_t *dl = component == 0 ? l0_suffix :
				(component == 1 ? l0_bmi2 : l0_full);
			d1[s] = (int64_t)c1 - (int64_t)ctl;
			dl[s] = (int64_t)l0 - (int64_t)ctl;
		}
	}
	printf("{\"delta_tsc\":{\"c1\":{\"suffix2\":%lld,\"bmi2\":%lld,\"full\":%lld},"
	       "\"late\":{\"suffix2\":%lld,\"bmi2\":%lld,\"full\":%lld}},\"sink\":%llu}\n",
		(long long)median(c1_suffix), (long long)median(c1_bmi2),
		(long long)median(c1_full), (long long)median(l0_suffix),
		(long long)median(l0_bmi2), (long long)median(l0_full),
		(unsigned long long)sink);
	return 0;
}

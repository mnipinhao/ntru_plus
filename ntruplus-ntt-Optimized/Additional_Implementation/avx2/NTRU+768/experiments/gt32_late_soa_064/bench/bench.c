#define _GNU_SOURCE
#include "full_bridge.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SAMPLES 41
#define COMPONENT_ITERS 2500U
#define FULL_ITERS 900U

static int16_t fa[768] __attribute__((aligned(64)));
static int16_t fb[768] __attribute__((aligned(64)));
static int16_t aos_a[768] __attribute__((aligned(64)));
static int16_t aos_b[768] __attribute__((aligned(64)));
static int16_t soa_a[768] __attribute__((aligned(64)));
static int16_t soa_b[768] __attribute__((aligned(64)));
static int16_t post_i2[768] __attribute__((aligned(64)));
static int16_t x[768] __attribute__((aligned(64)));
static int16_t y[768] __attribute__((aligned(64)));
static int16_t z[768] __attribute__((aligned(64)));
static int16_t out[768] __attribute__((aligned(64)));
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
	const int64_t x0 = *(const int64_t *)a, x1 = *(const int64_t *)b;
	return (x0 > x1) - (x0 < x1);
}

static int64_t median(int64_t *x0)
{
	qsort(x0, SAMPLES, sizeof(*x0), cmp64);
	return x0[SAMPLES / 2];
}

static void run_once(unsigned variant, unsigned component)
{
	if (component == 0) {
		if (variant == 2) {
			gt32_tile4_attr_forward_all_bm_soa_asm(x, fa);
			gt32_tile4_attr_forward_all_bm_soa_asm(y, fb);
		} else {
			gt32_tile4_forward_all_pair_asm(x, fa);
			gt32_tile4_forward_all_pair_asm(y, fb);
		}
		memcpy(out, y, sizeof(out));
	} else if (component == 1) {
		if (variant == 0) {
			gt32_tile4_basemul_c3center_late_aos_private_asm(z, aos_a, aos_b);
			late_full_inverse_i2_asm(out, z);
		} else if (variant == 1) {
			gt32_tile4_attr_basemul_i1_stage01_fused_asm(out, aos_a, aos_b);
		} else {
			late_soa_full_basemul_i2_fused_asm(out, soa_a, soa_b);
		}
	} else if (component == 2) {
		gt32_tile4_attr_inverse_i1_cross3_asm(out, post_i2);
	} else {
		if (variant == 0) {
			gt32_tile4_forward_all_pair_asm(x, fa);
			gt32_tile4_forward_all_pair_asm(y, fb);
			gt32_tile4_basemul_c3center_late_aos_private_asm(z, x, y);
			gt32_tile4_inverse_all_pair_asm(out, z);
		} else if (variant == 1) {
			gt32_tile4_forward_all_pair_asm(x, fa);
			gt32_tile4_forward_all_pair_asm(y, fb);
			gt32_tile4_attr_basemul_i1_stage01_fused_asm(z, x, y);
			gt32_tile4_attr_inverse_i1_cross3_asm(out, z);
		} else {
			gt32_tile4_attr_forward_all_bm_soa_asm(x, fa);
			gt32_tile4_attr_forward_all_bm_soa_asm(y, fb);
			late_soa_full_basemul_i2_fused_asm(z, x, y);
			gt32_tile4_attr_inverse_i1_cross3_asm(out, z);
		}
	}
}

static uint64_t run(unsigned variant, unsigned component, unsigned iters)
{
	const uint64_t begin = ticks();
	for (unsigned i = 0; i < iters; ++i) {
		run_once(variant, component);
		sink += (uint16_t)out[i % 768U];
	}
	return (ticks() - begin) / iters;
}

static void prepare(void)
{
	int16_t a[768] __attribute__((aligned(64)));
	int16_t b[768] __attribute__((aligned(64)));
	uint64_t s = UINT64_C(0x064123456789abcd);
	for (unsigned i = 0; i < 768; ++i) {
		s ^= s << 7; s ^= s >> 9;
		a[i] = (int16_t)((int)(s % 3457U) - 1728);
		s ^= s << 7; s ^= s >> 9;
		b[i] = (int16_t)((int)(s % 3457U) - 1728);
	}
	gt32_tile4_frontend_wide_raw_asm(fa, a);
	gt32_tile4_frontend_wide_raw_asm(fb, b);
	gt32_tile4_forward_all_pair_asm(aos_a, fa);
	gt32_tile4_forward_all_pair_asm(aos_b, fb);
	gt32_tile4_attr_forward_all_bm_soa_asm(soa_a, fa);
	gt32_tile4_attr_forward_all_bm_soa_asm(soa_b, fb);
	late_soa_full_basemul_i2_fused_asm(post_i2, soa_a, soa_b);
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
	const unsigned component = !strcmp(cname, "forward2") ? 0U :
		(!strcmp(cname, "bmi2") ? 1U : (!strcmp(cname, "remaining") ? 2U : 3U));
	const unsigned iters = component == 3 ? 250000U : 500000U;
	(void)run(variant, component, iters);
	printf("%llu\n", (unsigned long long)sink);
	return 0;
}

int main(int argc, char **argv)
{
	pin_first_cpu();
	prepare();
	if (argc == 4 && !strcmp(argv[1], "--pmu")) return pmu(argv[2], argv[3]);
	int64_t c1[4][SAMPLES], late[4][SAMPLES];
	for (unsigned s = 0; s < SAMPLES; ++s) {
		const int reverse = (int)(s & 1U);
		for (unsigned component = 0; component < 4; ++component) {
			const unsigned iters = component == 3 ? FULL_ITERS : COMPONENT_ITERS;
			uint64_t ctl, v1, vl;
			if (!reverse) {
				ctl = run(0, component, iters);
				v1 = run(1, component, iters);
				vl = run(2, component, iters);
			} else {
				vl = run(2, component, iters);
				v1 = run(1, component, iters);
				ctl = run(0, component, iters);
			}
			c1[component][s] = (int64_t)v1 - (int64_t)ctl;
			late[component][s] = (int64_t)vl - (int64_t)ctl;
		}
	}
	printf("{\"delta_tsc\":{\"c1\":{\"forward2\":%lld,\"bmi2\":%lld,"
	       "\"remaining\":%lld,\"complete\":%lld},\"late\":{\"forward2\":%lld,"
	       "\"bmi2\":%lld,\"remaining\":%lld,\"complete\":%lld}},\"sink\":%llu}\n",
		(long long)median(c1[0]), (long long)median(c1[1]),
		(long long)median(c1[2]), (long long)median(c1[3]),
		(long long)median(late[0]), (long long)median(late[1]),
		(long long)median(late[2]), (long long)median(late[3]),
		(unsigned long long)sink);
	return 0;
}

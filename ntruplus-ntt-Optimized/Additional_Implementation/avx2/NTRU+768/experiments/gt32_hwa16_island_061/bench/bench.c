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

static int16_t ta[128] __attribute__((aligned(32)));
static int16_t tb[128] __attribute__((aligned(32)));
static int16_t ha[128] __attribute__((aligned(32)));
static int16_t hb[128] __attribute__((aligned(32)));
static int16_t tfa[128] __attribute__((aligned(32)));
static int16_t tfb[128] __attribute__((aligned(32)));
static int16_t hfa[128] __attribute__((aligned(32)));
static int16_t hfb[128] __attribute__((aligned(32)));
static int16_t tp[128] __attribute__((aligned(32)));
static int16_t hp[128] __attribute__((aligned(32)));
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

static uint64_t run_unary(unary_fn fn, const int16_t *input, unsigned iters)
{
	const uint64_t begin = ticks();
	for (unsigned i = 0; i < iters; ++i) {
		fn(out, input);
		sink += (uint16_t)out[i & 127U];
	}
	return (ticks() - begin) / iters;
}

static uint64_t run_binary(binary_fn fn, const int16_t *a, const int16_t *b,
	unsigned iters)
{
	const uint64_t begin = ticks();
	for (unsigned i = 0; i < iters; ++i) {
		fn(out, a, b);
		sink += (uint16_t)out[i & 127U];
	}
	return (ticks() - begin) / iters;
}

static uint64_t run_island(unsigned variant, unsigned iters)
{
	int16_t x[128] __attribute__((aligned(32)));
	int16_t y[128] __attribute__((aligned(32)));
	int16_t z[128] __attribute__((aligned(32)));
	const uint64_t begin = ticks();
	for (unsigned i = 0; i < iters; ++i) {
		if (variant == 0) {
			ctl_tile4_forward_asm(x, ta);
			ctl_tile4_forward_asm(y, tb);
			ctl_tile4_basemul_asm(z, x, y);
			ctl_tile4_inverse_asm(out, z);
		} else if (variant == 1) {
			hwa16_forward_v1_asm(x, ha);
			hwa16_forward_v1_asm(y, hb);
			hwa16_basemul_asm(z, x, y);
			hwa16_inverse_v1_asm(out, z);
		} else {
			hwa16_forward_v2_asm(x, ha);
			hwa16_forward_v2_asm(y, hb);
			hwa16_basemul_asm(z, x, y);
			hwa16_inverse_v2_asm(out, z);
		}
		sink += (uint16_t)out[i & 127U];
	}
	return (ticks() - begin) / iters;
}

static void prepare(void)
{
	uint64_t s = UINT64_C(0x061123456789abcd);
	for (unsigned i = 0; i < 128; ++i) {
		s ^= s << 7; s ^= s >> 9;
		ta[i] = (int16_t)((int)(s % 3457U) - 1728);
		s ^= s << 7; s ^= s >> 9;
		tb[i] = (int16_t)((int)(s % 3457U) - 1728);
	}
	hwa16_from_tile4(ha, ta);
	hwa16_from_tile4(hb, tb);
	ctl_tile4_forward_asm(tfa, ta);
	ctl_tile4_forward_asm(tfb, tb);
	hwa16_forward_v2_asm(hfa, ha);
	hwa16_forward_v2_asm(hfb, hb);
	ctl_tile4_basemul_asm(tp, tfa, tfb);
	hwa16_basemul_asm(hp, hfa, hfb);
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

static int pmu(const char *variant, const char *component)
{
	unsigned v = !strcmp(variant, "tile4") ? 0U :
		(!strcmp(variant, "hwa-v1") ? 1U : 2U);
	const unsigned iters = !strcmp(component, "island") ? 300000U : 1000000U;
	if (!strcmp(component, "island")) (void)run_island(v, iters);
	else if (!strcmp(component, "forward")) {
		unary_fn fn = v == 0 ? ctl_tile4_forward_asm :
			(v == 1 ? hwa16_forward_v1_asm : hwa16_forward_v2_asm);
		(void)run_unary(fn, v == 0 ? ta : ha, iters);
	} else if (!strcmp(component, "basemul")) {
		binary_fn fn = v == 0 ? ctl_tile4_basemul_asm : hwa16_basemul_asm;
		(void)run_binary(fn, v == 0 ? tfa : hfa, v == 0 ? tfb : hfb, iters);
	} else if (!strcmp(component, "inverse")) {
		unary_fn fn = v == 0 ? ctl_tile4_inverse_asm :
			(v == 1 ? hwa16_inverse_v1_asm : hwa16_inverse_v2_asm);
		(void)run_unary(fn, v == 0 ? tp : hp, iters);
	} else return 2;
	printf("%llu\n", (unsigned long long)sink);
	return 0;
}

int main(int argc, char **argv)
{
	pin_first_cpu();
	prepare();
	if (argc == 4 && !strcmp(argv[1], "--pmu")) return pmu(argv[2], argv[3]);
	int64_t f1[SAMPLES], f2[SAMPLES], b1[SAMPLES], b2[SAMPLES];
	int64_t i1[SAMPLES], i2[SAMPLES], w1[SAMPLES], w2[SAMPLES];
	for (unsigned s = 0; s < SAMPLES; ++s) {
		const int reverse = (int)(s & 1U);
		uint64_t ctl, cand;
#define PAIR(dst1,dst2,expr_ctl,expr_cand) do { \
	if (!reverse) { ctl=(expr_ctl); cand=(expr_cand); } \
	else { cand=(expr_cand); ctl=(expr_ctl); } \
	(dst1)[s]=(int64_t)cand-(int64_t)ctl; \
	if (!reverse) { ctl=(expr_ctl); cand=(expr_cand); } \
	else { cand=(expr_cand); ctl=(expr_ctl); } \
	(dst2)[s]=(int64_t)cand-(int64_t)ctl; \
} while (0)
		PAIR(f1, f2,
			run_unary(ctl_tile4_forward_asm, ta, COMPONENT_ITERS),
			run_unary(hwa16_forward_v1_asm, ha, COMPONENT_ITERS));
		/* f2 is replaced below by the V2 paired result. */
		if (!reverse) {
			ctl = run_unary(ctl_tile4_forward_asm, ta, COMPONENT_ITERS);
			cand = run_unary(hwa16_forward_v2_asm, ha, COMPONENT_ITERS);
		} else {
			cand = run_unary(hwa16_forward_v2_asm, ha, COMPONENT_ITERS);
			ctl = run_unary(ctl_tile4_forward_asm, ta, COMPONENT_ITERS);
		}
		f2[s] = (int64_t)cand - (int64_t)ctl;
		PAIR(b1, b2,
			run_binary(ctl_tile4_basemul_asm, tfa, tfb, COMPONENT_ITERS),
			run_binary(hwa16_basemul_asm, hfa, hfb, COMPONENT_ITERS));
		/* B3 is shared; report the same paired sample in both columns. */
		b2[s] = b1[s];
		PAIR(i1, i2,
			run_unary(ctl_tile4_inverse_asm, tp, COMPONENT_ITERS),
			run_unary(hwa16_inverse_v1_asm, hp, COMPONENT_ITERS));
		if (!reverse) {
			ctl = run_unary(ctl_tile4_inverse_asm, tp, COMPONENT_ITERS);
			cand = run_unary(hwa16_inverse_v2_asm, hp, COMPONENT_ITERS);
		} else {
			cand = run_unary(hwa16_inverse_v2_asm, hp, COMPONENT_ITERS);
			ctl = run_unary(ctl_tile4_inverse_asm, tp, COMPONENT_ITERS);
		}
		i2[s] = (int64_t)cand - (int64_t)ctl;
		PAIR(w1, w2, run_island(0, ISLAND_ITERS), run_island(1, ISLAND_ITERS));
		if (!reverse) { ctl=run_island(0,ISLAND_ITERS); cand=run_island(2,ISLAND_ITERS); }
		else { cand=run_island(2,ISLAND_ITERS); ctl=run_island(0,ISLAND_ITERS); }
		w2[s] = (int64_t)cand - (int64_t)ctl;
#undef PAIR
	}
	printf("{\"delta_tsc\":{\"v1\":{\"forward\":%lld,\"basemul\":%lld,\"inverse\":%lld,\"island\":%lld},"
	       "\"v2\":{\"forward\":%lld,\"basemul\":%lld,\"inverse\":%lld,\"island\":%lld}},\"sink\":%llu}\n",
		(long long)median(f1), (long long)median(b1), (long long)median(i1),
		(long long)median(w1), (long long)median(f2), (long long)median(b2),
		(long long)median(i2), (long long)median(w2), (unsigned long long)sink);
	return 0;
}


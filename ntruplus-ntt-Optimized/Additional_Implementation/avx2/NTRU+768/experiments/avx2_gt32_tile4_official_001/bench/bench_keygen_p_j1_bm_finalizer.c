#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <x86intrin.h>

#define N 768
#define B 1152

int gt32_p_baseinv_direct_avx2(int16_t *, const int16_t *);
int gt32_p_j1_baseinv_direct_avx2(int16_t *, const int16_t *);
void gt_basemul_native_asm_avx2(int16_t *, const int16_t *, const int16_t *);
void gt_basemul_native_f0_j1_e0_asm_avx2(int16_t *, const int16_t *, const int16_t *);
void gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(uint8_t *, const int16_t *);

static _Alignas(64) int16_t f[N], g[N], fi[N], gi[N], h[N], hi[N];
static _Alignas(64) uint8_t bytes[3][B];
static volatile uint64_t sink;
static uint32_t state = 7;

static uint32_t rng32(void) { state = state * 1664525u + 1013904223u; return state; }

__attribute__((noinline)) static void control(void)
{
	(void)gt32_p_baseinv_direct_avx2(fi, f);
	(void)gt32_p_baseinv_direct_avx2(gi, g);
	gt_basemul_native_asm_avx2(h, g, fi);
	gt_basemul_native_asm_avx2(hi, f, gi);
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(bytes[0], f);
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(bytes[1], h);
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(bytes[2], hi);
}

__attribute__((noinline)) static void candidate(void)
{
	(void)gt32_p_j1_baseinv_direct_avx2(fi, f);
	(void)gt32_p_j1_baseinv_direct_avx2(gi, g);
	gt_basemul_native_f0_j1_e0_asm_avx2(h, g, fi);
	gt_basemul_native_f0_j1_e0_asm_avx2(hi, f, gi);
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(bytes[0], f);
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(bytes[1], h);
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(bytes[2], hi);
}

static void run(void (*fn)(void), unsigned n)
{
	for (unsigned i = 0; i < n; i++) fn();
	sink += bytes[n % 3][n % B];
}

int main(int argc, char **argv)
{
	if (argc != 3) return 2;
	const unsigned n = (unsigned)strtoul(argv[1], 0, 0);
	void (*fn)(void) = strcmp(argv[2], "candidate") == 0 ? candidate : control;
	for (unsigned i = 0; i < N; i++) {
		f[i] = (int16_t)((int)(rng32() % 19173) - 9586);
		g[i] = (int16_t)((int)(rng32() % 19173) - 9586);
	}
	if (gt32_p_baseinv_direct_avx2(fi, f) || gt32_p_baseinv_direct_avx2(gi, g)) return 3;
	run(fn, 20);
	unsigned aux;
	_mm_lfence(); uint64_t start = __rdtsc();
	run(fn, n);
	uint64_t end = __rdtscp(&aux); _mm_lfence();
	printf("tsc_per_call=%.6f sink=%llu\n", (double)(end-start)/n,
	       (unsigned long long)sink);
	return 0;
}

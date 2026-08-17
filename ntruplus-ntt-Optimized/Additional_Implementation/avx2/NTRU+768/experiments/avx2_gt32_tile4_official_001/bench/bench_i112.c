#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#define N 768
typedef void (*pipeline_fn)(int16_t *, const int16_t *, const int16_t *);

void gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_inverse_all_pair_asm(int16_t *, const int16_t *);
void gt32_tile4_m_to_i112_asm(int16_t *, const int16_t *);
void gt32_tile4_inverse_i112_entry_asm(int16_t *, const int16_t *);
void gt32_tile4_m_to_aos_asm(int16_t *, const int16_t *);

static int16_t product[N] __attribute__((aligned(32)));
static int16_t packet[N] __attribute__((aligned(32)));
static volatile uint64_t sink;

static void control(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(product, a, b);
	gt32_tile4_inverse_all_pair_asm(out, product);
}

static void candidate(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(product, a, b);
	gt32_tile4_m_to_i112_asm(packet, product);
	gt32_tile4_inverse_i112_entry_asm(product, packet);
	gt32_tile4_m_to_aos_asm(out, product);
}

static uint64_t stamp(void)
{
	_mm_lfence();
	return __rdtsc();
}

static double measure(pipeline_fn fn, int16_t *out, const int16_t *a,
	const int16_t *b, unsigned iterations)
{
	const uint64_t begin = stamp();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, a, b);
	const uint64_t end = stamp();
	sink += (uint16_t)out[iterations & 767U];
	return (double)(end - begin) / iterations;
}

static int compare(const void *a, const void *b)
{
	const double x = *(const double *)a;
	const double y = *(const double *)b;
	return (x > y) - (x < y);
}

static double median(double v[20])
{
	qsort(v, 20, sizeof(v[0]), compare);
	return 0.5 * (v[9] + v[10]);
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 5000U;
	int16_t a[N] __attribute__((aligned(32)));
	int16_t b[N] __attribute__((aligned(32)));
	int16_t out[N] __attribute__((aligned(32)));
	double c[20], p[20];
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < N; i++) {
		a[i] = (int16_t)((int)(i % 3457U) - 1728);
		b[i] = (int16_t)((int)((7U * i + 3U) % 3457U) - 1728);
	}
	(void)measure(control, out, a, b, 100);
	(void)measure(candidate, out, a, b, 100);
	for (unsigned sample = 0; sample < 20; sample++) {
		if ((sample & 1U) == 0U) {
			c[sample] = measure(control, out, a, b, iterations);
			p[sample] = measure(candidate, out, a, b, iterations);
		} else {
			p[sample] = measure(candidate, out, a, b, iterations);
			c[sample] = measure(control, out, a, b, iterations);
		}
	}
	const double cm = median(c), pm = median(p);
	unsigned wins = 0;
	for (unsigned i = 0; i < 20; i++)
		wins += p[i] < c[i];
	printf("control %.3f\ncandidate %.3f\ndelta %+.3f\nwins %u/20\n",
		cm, pm, pm - cm, wins);
	return sink == 0xdeadbeefU ? 1 : 0;
}

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

#include "api.h"
#include "kat/rng.h"
#include "poly.h"
#include "symmetric.h"
#include "tile4.h"

enum { WORDS = GT32_TILE4_POLY_WORDS, VARIANTS = 3, REGIONS = 4, SAMPLES = 20 };
typedef int (*region_fn)(void);

static _Alignas(64) uint8_t pk[CRYPTO_PUBLICKEYBYTES];
static _Alignas(64) uint8_t sk[CRYPTO_SECRETKEYBYTES];
static _Alignas(64) uint8_t coins[NTRUPLUS_N / 8];
static _Alignas(64) poly r_input, m_input;
static _Alignas(64) poly prep_off_h, prep_off_r, r1_off_h;
static _Alignas(64) int16_t prep_gt_h[WORDS], prep_gt_r[WORDS];
static _Alignas(64) int16_t r1_gt_h[WORDS], r1_gt_h_star[WORDS];
static _Alignas(64) uint8_t r_wire[NTRUPLUS_POLYBYTES];
static _Alignas(64) uint8_t c_wire[NTRUPLUS_POLYBYTES];
static volatile uint64_t sink;

static const char *const names[VARIANTS] = { "Official", "Clean", "F14_TF1" };
static const char *const region_names[REGIONS] = {
	"R1_decode", "R2_rpath", "R3_final", "R4_island"
};
static const unsigned pair_variants[3][2] = { { 0, 1 }, { 0, 2 }, { 1, 2 } };
static const char *const pair_names[3] = { "O_C0", "O_Cstar", "C0_Cstar" };

__attribute__((noinline))
static int island_official(uint8_t *r_out, uint8_t *c_out) {
	poly h, r = r_input, m = m_input, c;
	if (poly_frombytes(&h, pk) != 0) return 1;
	poly_ntt(&r);
	poly_tobytes(r_out, &r);
	poly_ntt(&m);
	poly_basemul(&c, &h, &r);
	poly_add(&c, &c, &m);
	poly_tobytes(c_out, &c);
	return 0;
}

static void gt_forward(int16_t *out, int16_t *work, const int16_t *in,
	int f14) {
	if (f14) gt32_tile4_frontend_wide_raw_f14_asm(work, in);
	else gt32_tile4_frontend_wide_raw_asm(work, in);
	gt32_tile4_attr_forward_all_bm_soa_asm(out, work);
}

static int island_gt(uint8_t *r_out, uint8_t *c_out, int local_champion) {
	_Alignas(64) int16_t h[WORDS], r[WORDS], m[WORDS], c[WORDS], work[WORDS];
	if (gt32_q24_decode_soa_asm(h, pk) != 0) return 1;
	gt_forward(r, work, r_input.coeffs, local_champion);
	if (local_champion) gt32_q24_encode_soa_tf1_asm(r_out, r);
	else gt32_q24_encode_soa_lazy10788_asm(r_out, r);
	gt_forward(m, work, m_input.coeffs, local_champion);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(c, h, r);
	poly_add((poly *)(void *)c, (const poly *)(const void *)c,
		(const poly *)(const void *)m);
	if (local_champion) gt32_q24_encode_soa_tf1_asm(c_out, c);
	else gt32_q24_encode_soa_encap_hr_h1_asm(c_out, c);
	return 0;
}

__attribute__((noinline)) static int island_clean(uint8_t *r, uint8_t *c) {
	return island_gt(r, c, 0);
}
__attribute__((noinline)) static int island_f14_tf1(uint8_t *r, uint8_t *c) {
	return island_gt(r, c, 1);
}

__attribute__((noinline)) static int r1_official(void) {
	return poly_frombytes(&r1_off_h, pk);
}
__attribute__((noinline)) static int r1_clean(void) {
	return gt32_q24_decode_soa_asm(r1_gt_h, pk);
}
__attribute__((noinline)) static int r1_f14_tf1(void) {
	return gt32_q24_decode_soa_asm(r1_gt_h_star, pk);
}

__attribute__((noinline)) static int r2_official(void) {
	poly r = r_input;
	poly_ntt(&r);
	poly_tobytes(r_wire, &r);
	return 0;
}
static int r2_gt(int local_champion) {
	_Alignas(64) int16_t r[WORDS], work[WORDS];
	gt_forward(r, work, r_input.coeffs, local_champion);
	if (local_champion) gt32_q24_encode_soa_tf1_asm(r_wire, r);
	else gt32_q24_encode_soa_lazy10788_asm(r_wire, r);
	return 0;
}
__attribute__((noinline)) static int r2_clean(void) { return r2_gt(0); }
__attribute__((noinline)) static int r2_f14_tf1(void) { return r2_gt(1); }

__attribute__((noinline)) static int r3_official(void) {
	poly m = m_input, c;
	poly_ntt(&m);
	poly_basemul(&c, &prep_off_h, &prep_off_r);
	poly_add(&c, &c, &m);
	poly_tobytes(c_wire, &c);
	return 0;
}
static int r3_gt(int local_champion) {
	_Alignas(64) int16_t m[WORDS], c[WORDS], work[WORDS];
	gt_forward(m, work, m_input.coeffs, local_champion);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(
		c, prep_gt_h, prep_gt_r);
	poly_add((poly *)(void *)c, (const poly *)(const void *)c,
		(const poly *)(const void *)m);
	if (local_champion) gt32_q24_encode_soa_tf1_asm(c_wire, c);
	else gt32_q24_encode_soa_encap_hr_h1_asm(c_wire, c);
	return 0;
}
__attribute__((noinline)) static int r3_clean(void) { return r3_gt(0); }
__attribute__((noinline)) static int r3_f14_tf1(void) { return r3_gt(1); }

__attribute__((noinline)) static int r4_official(void) {
	return island_official(r_wire, c_wire);
}
__attribute__((noinline)) static int r4_clean(void) {
	return island_clean(r_wire, c_wire);
}
__attribute__((noinline)) static int r4_f14_tf1(void) {
	return island_f14_tf1(r_wire, c_wire);
}

static region_fn const regions[REGIONS][VARIANTS] = {
	{ r1_official, r1_clean, r1_f14_tf1 },
	{ r2_official, r2_clean, r2_f14_tf1 },
	{ r3_official, r3_clean, r3_f14_tf1 },
	{ r4_official, r4_clean, r4_f14_tf1 },
};

static uint64_t start_tsc(void) { _mm_lfence(); return __rdtsc(); }
static uint64_t stop_tsc(void) {
	unsigned aux; uint64_t value = __rdtscp(&aux); _mm_lfence(); return value;
}
static double measure_tsc(region_fn fn, unsigned iterations) {
	uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)fn();
	return (double)(stop_tsc() - begin) / iterations;
}

struct pmu_spec { const char *name; uint32_t type; uint64_t config; uint64_t config1; };
static int perf_open(const struct pmu_spec *spec, int group_fd, int disabled) {
	struct perf_event_attr attr;
	memset(&attr, 0, sizeof attr);
	attr.size = sizeof attr; attr.type = spec->type; attr.config = spec->config;
	attr.config1 = spec->config1; attr.disabled = disabled != 0;
	attr.exclude_kernel = 1; attr.exclude_hv = 1; attr.read_format = PERF_FORMAT_GROUP;
	return (int)syscall(SYS_perf_event_open, &attr, 0, -1, group_fd, 0UL);
}
static int measure_pmu(region_fn fn, unsigned iterations,
	const struct pmu_spec *specs, unsigned count, const char *label) {
	int fds[4]; uint64_t values[5];
	for (unsigned i = 0; i < count; i++) {
		fds[i] = perf_open(&specs[i], i == 0 ? -1 : fds[0], i == 0);
		if (fds[i] < 0) { perror("perf_event_open"); return 0; }
	}
	(void)ioctl(fds[0], PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
	(void)ioctl(fds[0], PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
	for (unsigned i = 0; i < iterations; i++) sink += (unsigned)fn();
	(void)ioctl(fds[0], PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
	ssize_t got = read(fds[0], values, sizeof(uint64_t) * (count + 1U));
	for (unsigned i = 0; i < count; i++) close(fds[i]);
	if (got != (ssize_t)(sizeof(uint64_t) * (count + 1U)) || values[0] != count)
		return 0;
	printf("PMU,%s", label);
	for (unsigned i = 0; i < count; i++)
		printf(",%s,%.6f", specs[i].name, (double)values[i + 1U] / iterations);
	printf("\n");
	return 1;
}

static int prepare_inputs(unsigned trial) {
	uint8_t msg[HASH_H_INBYTES], buf[HASH_H_OUTBYTES], serialized[NTRUPLUS_POLYBYTES];
	poly r;
	for (unsigned i = 0; i < sizeof coins; i++)
		coins[i] = (uint8_t)(trial * 73U + i * 37U + 11U);
	memcpy(msg, coins, sizeof coins);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf, msg);
	poly_cbd1(&r_input, buf + NTRUPLUS_SYMBYTES);
	r = r_input; poly_ntt(&r); poly_tobytes(serialized, &r); hash_g(serialized, serialized);
	poly_sotp_encode(&m_input, msg, serialized);
	return 1;
}

static int prepare_representations(void) {
	_Alignas(64) int16_t work[WORDS];
	if (poly_frombytes(&prep_off_h, pk) != 0) return 0;
	prep_off_r = r_input;
	poly_ntt(&prep_off_r);
	if (gt32_q24_decode_soa_asm(prep_gt_h, pk) != 0) return 0;
	gt_forward(prep_gt_r, work, r_input.coeffs, 0);
	return 1;
}

static int correctness(void) {
	uint8_t rr[VARIANTS][NTRUPLUS_POLYBYTES];
	uint8_t cc[VARIANTS][NTRUPLUS_POLYBYTES];
	for (unsigned trial = 0; trial < 100; trial++) {
		if (!prepare_inputs(trial) || !prepare_representations()) return 0;
		for (unsigned v = 0; v < VARIANTS; v++) {
			if (regions[0][v]() != 0 || regions[1][v]() != 0) return 0;
			memcpy(rr[v], r_wire, sizeof rr[v]);
			if (regions[2][v]() != 0) return 0;
			memcpy(cc[v], c_wire, sizeof cc[v]);
		}
		for (unsigned v = 1; v < VARIANTS; v++)
			if (memcmp(rr[0], rr[v], sizeof rr[0]) != 0
				|| memcmp(cc[0], cc[v], sizeof cc[0]) != 0) return 0;
		for (unsigned v = 0; v < VARIANTS; v++) {
			if (regions[3][v]() != 0) return 0;
			if (memcmp(rr[0], r_wire, sizeof rr[0]) != 0
				|| memcmp(cc[0], c_wire, sizeof cc[0]) != 0) return 0;
		}
	}
	return 1;
}

int main(int argc, char **argv) {
	unsigned iterations = argc > 1 ? (unsigned)strtoul(argv[1], NULL, 0) : 1000;
	unsigned cpu = argc > 2 ? (unsigned)strtoul(argv[2], NULL, 0) : 1;
	const char *mode = argc > 3 ? argv[3] : "tsc";
	cpu_set_t set; CPU_ZERO(&set); CPU_SET(cpu, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0) { perror("affinity"); return 2; }
	uint8_t entropy[48];
	for (unsigned i = 0; i < sizeof entropy; i++) entropy[i] = (uint8_t)(31U + 7U * i);
	randombytes_init(entropy, NULL, 256);
	if (crypto_kem_keypair(pk, sk) != 0 || !correctness()) {
		fprintf(stderr, "polynomial-island differential failed\n"); return 1;
	}
	prepare_inputs(1000);
	if (!prepare_representations()) return 1;
	for (unsigned warm = 0; warm < 20; warm++)
		for (unsigned region = 0; region < REGIONS; region++)
			for (unsigned v = 0; v < VARIANTS; v++)
				(void)measure_tsc(regions[region][v], 2);
	if (strncmp(mode, "pmu-", 4) == 0) {
		static const struct pmu_spec basic[] = {
			{ "cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, 0 },
			{ "instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, 0 },
			{ "branches", PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_INSTRUCTIONS, 0 },
			{ "branch_misses", PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_MISSES, 0 },
		};
		static const struct pmu_spec memory[] = {
			{ "ref_cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_REF_CPU_CYCLES, 0 },
			{ "loads", 4, 0x81d0, 0 }, { "stores", 4, 0x82d0, 0 },
		};
		static const struct pmu_spec delivery[] = {
			{ "dsb_uops", 4, 0x879, 0 }, { "mite_uops", 4, 0x479, 0 },
			{ "dsb2mite_penalty_cycles", 4, 0x261, 0 },
		};
		static const struct pmu_spec misses[] = {
			{ "frontend_dsb_miss", 4, 0x3c6, 0x11 },
			{ "itlb_read_miss", PERF_TYPE_HW_CACHE, PERF_COUNT_HW_CACHE_ITLB
				| (PERF_COUNT_HW_CACHE_OP_READ << 8)
				| (PERF_COUNT_HW_CACHE_RESULT_MISS << 16), 0 },
			{ "l1i_read_miss", PERF_TYPE_HW_CACHE, PERF_COUNT_HW_CACHE_L1I
				| (PERF_COUNT_HW_CACHE_OP_READ << 8)
				| (PERF_COUNT_HW_CACHE_RESULT_MISS << 16), 0 },
		};
		const struct pmu_spec *specs = basic; unsigned count = 4;
		if (strstr(mode, "memory")) { specs = memory; count = 3; }
		if (strstr(mode, "delivery")) { specs = delivery; count = 3; }
		if (strstr(mode, "misses")) { specs = misses; count = 3; }
		char label[96];
		for (unsigned region = 0; region < REGIONS; region++)
			for (unsigned sample = 0; sample < 8; sample++)
				for (unsigned pair = 0; pair < 3; pair++) {
					unsigned a = pair_variants[pair][0];
					unsigned b = pair_variants[pair][1];
					unsigned order[4] = { a, b, b, a };
					if (sample & 1U) {
						order[0] = b; order[1] = a;
						order[2] = a; order[3] = b;
					}
					for (unsigned slot = 0; slot < 4; slot++) {
						unsigned v = order[slot];
						snprintf(label, sizeof label,
							"sample%u|%s|%s|slot%u|%s", sample,
							region_names[region], pair_names[pair], slot,
							names[v]);
						if (!measure_pmu(regions[region][v], iterations,
							specs, count, label)) return 3;
					}
				}
		return 0;
	}
	printf("META,correctness=R1-R4-byte-exact-pass,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned region = 0; region < REGIONS; region++)
		for (unsigned sample = 0; sample < SAMPLES; sample++) {
			for (unsigned pair = 0; pair < 3; pair++) {
				unsigned a = pair_variants[pair][0];
				unsigned b = pair_variants[pair][1];
				unsigned order[4] = { a, b, b, a };
				double sum[VARIANTS] = { 0.0, 0.0, 0.0 };
				unsigned seen[VARIANTS] = { 0, 0, 0 };
				if (sample & 1U) {
					order[0] = b; order[1] = a;
					order[2] = a; order[3] = b;
				}
				for (unsigned slot = 0; slot < 4; slot++) {
					unsigned v = order[slot];
					sum[v] += measure_tsc(regions[region][v], iterations);
					seen[v]++;
				}
				printf("TSC,%s,%u,%s,%s,%.6f,%s,%.6f\n",
					region_names[region], sample, pair_names[pair],
					names[a], sum[a] / seen[a], names[b], sum[b] / seen[b]);
			}
		}
	return 0;
}

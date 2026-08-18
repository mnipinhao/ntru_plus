#define _GNU_SOURCE
#include <sched.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <x86intrin.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "api.h"
#include "kat/rng.h"
#include "tile4_kem_encap_candidate.h"

enum { SAMPLES = 20, VARIANTS = 4 };
enum { SEQUENCE_LENGTH = 8 };
typedef int (*encap_fn)(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);

static _Alignas(64) uint8_t pk[CRYPTO_PUBLICKEYBYTES];
static _Alignas(64) uint8_t sk[CRYPTO_SECRETKEYBYTES];
static _Alignas(64) uint8_t coins[NTRUPLUS_N / 8];
static _Alignas(64) uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
static _Alignas(64) uint8_t ss[CRYPTO_BYTES];
static volatile uint64_t sink;

struct pmu_spec { const char *name; uint32_t type; uint64_t config; uint64_t config1; };

static int perf_open(const struct pmu_spec *spec, int group_fd, int disabled) {
	struct perf_event_attr attr;
	memset(&attr, 0, sizeof attr);
	attr.size = sizeof attr;
	attr.type = spec->type;
	attr.config = spec->config;
	attr.config1 = spec->config1;
	attr.disabled = (uint32_t)disabled;
	attr.exclude_kernel = 1;
	attr.exclude_hv = 1;
	attr.read_format = PERF_FORMAT_GROUP;
	return (int)syscall(SYS_perf_event_open, &attr, 0, -1, group_fd, 0UL);
}

static int measure_pmu_group(encap_fn fn, unsigned iterations,
	const struct pmu_spec *specs, unsigned count, const char *label) {
	int fds[4];
	uint64_t values[5];
	if (count == 0 || count > 4) return 0;
	for (unsigned i = 0; i < count; i++) {
		fds[i] = perf_open(&specs[i], i == 0 ? -1 : fds[0], i == 0);
		if (fds[i] < 0) {
			perror("perf_event_open");
			while (i > 0) close(fds[--i]);
			return 0;
		}
	}
	(void)ioctl(fds[0], PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
	(void)ioctl(fds[0], PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)fn(ct, ss, pk, coins);
	(void)ioctl(fds[0], PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
	ssize_t got = read(fds[0], values, sizeof(uint64_t) * (count + 1U));
	for (unsigned i = 0; i < count; i++) close(fds[i]);
	if (got != (ssize_t)(sizeof(uint64_t) * (count + 1U)) || values[0] != count)
		return 0;
	printf("PMU_INTERNAL,%s", label);
	for (unsigned i = 0; i < count; i++)
		printf(",%s,%.6f", specs[i].name, (double)values[i + 1U] / iterations);
	printf("\n");
	return 1;
}

static const char *const names[VARIANTS] = { "C00", "C10_F14", "C01_TF1", "C11_F14_TF1" };
static encap_fn const variants[VARIANTS] = {
	crypto_kem_enc_derand_gt32_candidate,
	crypto_kem_enc_derand_gt32_f14_candidate,
	crypto_kem_enc_derand_gt32_tf1_candidate,
	crypto_kem_enc_derand_gt32_f14_tf1_candidate,
};

static uint64_t start_tsc(void) { _mm_lfence(); return __rdtsc(); }
static uint64_t stop_tsc(void) {
	unsigned aux; uint64_t value = __rdtscp(&aux); _mm_lfence(); return value;
}
static double measure_homogeneous(encap_fn fn, unsigned iterations) {
	uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)fn(ct, ss, pk, coins);
	return (double)(stop_tsc() - begin) / iterations;
}
static double measure_transition(encap_fn predecessor, encap_fn target,
	unsigned iterations) {
	uint64_t total = 0;
	for (unsigned i = 0; i < iterations; i++) {
		sink += (unsigned)predecessor(ct, ss, pk, coins);
		uint64_t begin = start_tsc();
		sink += (unsigned)target(ct, ss, pk, coins);
		total += stop_tsc() - begin;
	}
	return (double)total / iterations;
}
static void measure_sequence(const char *name, const unsigned order[SEQUENCE_LENGTH],
	unsigned sample) {
	printf("SEQUENCE,%s,%u", name, sample);
	for (unsigned position = 0; position < SEQUENCE_LENGTH; position++) {
		uint64_t begin = start_tsc();
		sink += (unsigned)variants[order[position]](ct, ss, pk, coins);
		uint64_t elapsed = stop_tsc() - begin;
		printf(",%u,%llu", position, (unsigned long long)elapsed);
	}
	printf("\n");
}
static void set_serialized_word(uint8_t *bytes, unsigned index, uint16_t value) {
	unsigned pair = index / 2U;
	if ((index & 1U) == 0) {
		bytes[3U * pair] = (uint8_t)value;
		bytes[3U * pair + 1U] = (uint8_t)((bytes[3U * pair + 1U] & 0xf0U)
			| (uint8_t)(value >> 8));
	} else {
		bytes[3U * pair + 1U] = (uint8_t)((bytes[3U * pair + 1U] & 0x0fU)
			| (uint8_t)(value << 4));
		bytes[3U * pair + 2U] = (uint8_t)(value >> 4);
	}
}
static int correctness(void) {
	uint8_t ref_ct[CRYPTO_CIPHERTEXTBYTES], ref_ss[CRYPTO_BYTES];
	uint8_t bad_pk[CRYPTO_PUBLICKEYBYTES];
	for (unsigned trial = 0; trial < 100; trial++) {
		for (unsigned i = 0; i < sizeof coins; i++)
			coins[i] = (uint8_t)(trial * 73U + i * 19U);
		if (variants[0](ref_ct, ref_ss, pk, coins) != 0)
			return 0;
		for (unsigned v = 1; v < VARIANTS; v++)
			if (variants[v](ct, ss, pk, coins) != 0
				|| memcmp(ct, ref_ct, sizeof ct) != 0
				|| memcmp(ss, ref_ss, sizeof ss) != 0)
				return 0;
	}
	for (unsigned slot = 0; slot < NTRUPLUS_N; slot += 97) {
		memcpy(bad_pk, pk, sizeof bad_pk);
		set_serialized_word(bad_pk, slot, NTRUPLUS_Q);
		for (unsigned v = 0; v < VARIANTS; v++)
			if (variants[v](ct, ss, bad_pk, coins) != 1)
				return 0;
	}
	return 1;
}

int main(int argc, char **argv) {
	unsigned iterations = argc > 1 ? (unsigned)strtoul(argv[1], NULL, 0) : 2000;
	unsigned cpu = argc > 2 ? (unsigned)strtoul(argv[2], NULL, 0) : 1;
	const char *mode = argc > 3 ? argv[3] : "full";
	cpu_set_t set; CPU_ZERO(&set); CPU_SET(cpu, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0) { perror("affinity"); return 2; }
	uint8_t entropy[48];
	for (unsigned i = 0; i < sizeof entropy; i++) entropy[i] = (uint8_t)(31U + 7U * i);
	randombytes_init(entropy, NULL, 256);
	if (crypto_kem_keypair(pk, sk) != 0) {
		fprintf(stderr, "keypair failed\n"); return 1;
	}
	if (strcmp(mode, "pmu-a") == 0 || strcmp(mode, "pmu-b") == 0) {
		unsigned selected = strcmp(mode, "pmu-a") == 0 ? 0U : 3U;
		for (unsigned i = 0; i < sizeof coins; i++)
			coins[i] = (uint8_t)(11U + 37U * i);
		for (unsigned warm = 0; warm < 100; warm++)
			sink += (unsigned)variants[selected](ct, ss, pk, coins);
		for (unsigned i = 0; i < iterations; i++)
			sink += (unsigned)variants[selected](ct, ss, pk, coins);
		printf("PMU,%s,iterations=%u,sink=%llu\n", mode, iterations,
			(unsigned long long)sink);
		return 0;
	}
	if (strncmp(mode, "pmu-", 4) == 0) {
		int paired = mode[strlen(mode) - 1U] == 'p';
		unsigned selected = mode[strlen(mode) - 1U] == 'a' ? 0U : 3U;
		static const struct pmu_spec basic[] = {
			{ "cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, 0 },
			{ "instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, 0 },
			{ "branches", PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_INSTRUCTIONS, 0 },
			{ "branch_misses", PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_MISSES, 0 },
		};
		static const struct pmu_spec delivery[] = {
			{ "dsb_uops", 4, 0x879, 0 },
			{ "mite_uops", 4, 0x479, 0 },
			{ "dsb2mite_penalty_cycles", 4, 0x261, 0 },
		};
		static const struct pmu_spec misses[] = {
			{ "frontend_dsb_miss", 4, 0x3c6, 0x11 },
			{ "itlb_read_miss", PERF_TYPE_HW_CACHE,
				PERF_COUNT_HW_CACHE_ITLB | (PERF_COUNT_HW_CACHE_OP_READ << 8)
				| (PERF_COUNT_HW_CACHE_RESULT_MISS << 16), 0 },
			{ "l1i_read_miss", PERF_TYPE_HW_CACHE,
				PERF_COUNT_HW_CACHE_L1I | (PERF_COUNT_HW_CACHE_OP_READ << 8)
				| (PERF_COUNT_HW_CACHE_RESULT_MISS << 16), 0 },
		};
		const struct pmu_spec *specs = basic;
		unsigned count = 4;
		if (strstr(mode, "delivery") != NULL) { specs = delivery; count = 3; }
		if (strstr(mode, "misses") != NULL) { specs = misses; count = 3; }
		for (unsigned i = 0; i < sizeof coins; i++)
			coins[i] = (uint8_t)(11U + 37U * i);
		for (unsigned warm = 0; warm < 100; warm++) {
			sink += (unsigned)variants[0](ct, ss, pk, coins);
			sink += (unsigned)variants[3](ct, ss, pk, coins);
		}
		if (paired) {
			char label[24];
			for (unsigned sample = 0; sample < 8; sample++) {
				unsigned first = (sample & 1U) == 0 ? 0U : 3U;
				unsigned second = first == 0U ? 3U : 0U;
				snprintf(label, sizeof label, "sample%u_%c", sample,
					first == 0U ? 'A' : 'B');
				if (!measure_pmu_group(variants[first], iterations, specs, count,
					label)) return 3;
				snprintf(label, sizeof label, "sample%u_%c", sample,
					second == 0U ? 'A' : 'B');
				if (!measure_pmu_group(variants[second], iterations, specs, count,
					label)) return 3;
			}
		} else {
			if (!measure_pmu_group(variants[selected], iterations, specs, count,
				selected == 0U ? "A" : "B")) return 3;
		}
		return 0;
	}
	if (!correctness()) {
		fprintf(stderr, "same-ELF differential failed\n"); return 1;
	}
	for (unsigned i = 0; i < sizeof coins; i++) coins[i] = (uint8_t)(11U + 37U * i);
	for (unsigned warm = 0; warm < 20; warm++)
		for (unsigned v = 0; v < VARIANTS; v++)
			(void)measure_homogeneous(variants[v], 4);
	printf("META,correctness=byte-exact-pass,iterations=%u,samples=%u,cpu=%u\n",
		iterations, SAMPLES, cpu);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double values[VARIANTS];
		for (unsigned step = 0; step < VARIANTS; step++) {
			unsigned v = (sample + step) % VARIANTS;
			values[v] = measure_homogeneous(variants[v], iterations);
		}
		printf("FACTORIAL,%u", sample);
		for (unsigned v = 0; v < VARIANTS; v++) printf(",%s,%.6f", names[v], values[v]);
		printf("\n");
	}
	/* A=C00, B=C11.  Each observation times only the second call. */
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double aa, ab, ba, bb;
		if ((sample & 1U) == 0) {
			aa = measure_transition(variants[0], variants[0], iterations);
			ab = measure_transition(variants[0], variants[3], iterations);
			ba = measure_transition(variants[3], variants[0], iterations);
			bb = measure_transition(variants[3], variants[3], iterations);
		} else {
			bb = measure_transition(variants[3], variants[3], iterations);
			ba = measure_transition(variants[3], variants[0], iterations);
			ab = measure_transition(variants[0], variants[3], iterations);
			aa = measure_transition(variants[0], variants[0], iterations);
		}
		printf("TRANSITION,%u,A_after_A,%.6f,B_after_A,%.6f,A_after_B,%.6f,B_after_B,%.6f\n",
			sample, aa, ab, ba, bb);
	}
	/* Position-sensitive run-length diagnostics.  A=C00 and B=C11. */
	static const unsigned seq_a[SEQUENCE_LENGTH] = { 0, 0, 0, 0, 0, 0, 0, 0 };
	static const unsigned seq_b[SEQUENCE_LENGTH] = { 3, 3, 3, 3, 3, 3, 3, 3 };
	static const unsigned seq_ab[SEQUENCE_LENGTH] = { 0, 3, 0, 3, 0, 3, 0, 3 };
	static const unsigned seq_aaaabbbb[SEQUENCE_LENGTH] = { 0, 0, 0, 0, 3, 3, 3, 3 };
	static const unsigned seq_bbbbaaaa[SEQUENCE_LENGTH] = { 3, 3, 3, 3, 0, 0, 0, 0 };
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0) {
			measure_sequence("AAAAAAAA", seq_a, sample);
			measure_sequence("BBBBBBBB", seq_b, sample);
			measure_sequence("ABABABAB", seq_ab, sample);
			measure_sequence("AAAABBBB", seq_aaaabbbb, sample);
			measure_sequence("BBBBAAAA", seq_bbbbaaaa, sample);
		} else {
			measure_sequence("BBBBAAAA", seq_bbbbaaaa, sample);
			measure_sequence("AAAABBBB", seq_aaaabbbb, sample);
			measure_sequence("ABABABAB", seq_ab, sample);
			measure_sequence("BBBBBBBB", seq_b, sample);
			measure_sequence("AAAAAAAA", seq_a, sample);
		}
	}
	printf("sink=%llu\n", (unsigned long long)sink);
	return 0;
}

#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "poly.h"
#include "tile4.h"
#include "tile4_dual_terminal.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define BYTES GT32_TILE4_SERIALIZED_BYTES
#define SAMPLES 20U

typedef void (*region_fn)(void);

typedef struct __attribute__((aligned(64))) {
	uint64_t before[4];
	int16_t words[WORDS];
	uint64_t after[4];
} guarded_words_t;

typedef struct __attribute__((aligned(64))) {
	uint64_t before[4];
	gt32_sotp_sidecar_t value;
	uint64_t after[4];
} guarded_sidecar_t;

static guarded_words_t rows;
static guarded_words_t source_m;
static guarded_words_t control_m;
static guarded_words_t s1_m;
static guarded_words_t s2_m;
static guarded_words_t control_n5;
static guarded_words_t candidate_n5;
static guarded_sidecar_t s1_sidecar;
static guarded_sidecar_t s2_sidecar;
static uint8_t sotp_buf[2 * GT32_SOTP_PLANE_BYTES]
	__attribute__((aligned(64)));
static uint8_t control_msg[GT32_SOTP_PLANE_BYTES]
	__attribute__((aligned(64)));
static uint8_t candidate_msg[GT32_SOTP_PLANE_BYTES]
	__attribute__((aligned(64)));
static volatile uint64_t sink;

static uint32_t next_random(uint32_t *state)
{
	*state = *state * UINT32_C(1664525) + UINT32_C(1013904223);
	return *state;
}

static void set_bit(uint8_t *bytes, unsigned bit, unsigned value)
{
	const uint8_t mask = (uint8_t)(1U << (bit & 7U));
	bytes[bit >> 3] = (uint8_t)((bytes[bit >> 3] & (uint8_t)~mask)
		| (uint8_t)(value != 0U ? mask : 0U));
}

static unsigned get_bit(const uint8_t *bytes, unsigned bit)
{
	return (unsigned)((bytes[bit >> 3] >> (bit & 7U)) & 1U);
}

static void encode_components(uint8_t out[BYTES], uint32_t *state)
{
	for (unsigned pair = 0; pair < WORDS / 2U; pair++) {
		const uint16_t first = (uint16_t)(next_random(state) % 3457U);
		const uint16_t second = (uint16_t)(next_random(state) % 3457U);
		out[3U * pair] = (uint8_t)first;
		out[3U * pair + 1U] = (uint8_t)((first >> 8)
			| (uint16_t)(second << 4));
		out[3U * pair + 2U] = (uint8_t)(second >> 4);
	}
}

static void initialize_guard(void *object, size_t bytes, uint64_t tag)
{
	uint64_t *const before = object;
	uint64_t *const after = (uint64_t *)((uint8_t *)object + bytes - 32U);
	for (unsigned i = 0; i < 4; i++) {
		before[i] = tag + i;
		after[i] = tag + 16U + i;
	}
}

static int guard_valid(const void *object, size_t bytes, uint64_t tag)
{
	const uint64_t *const before = object;
	const uint64_t *const after =
		(const uint64_t *)((const uint8_t *)object + bytes - 32U);
	for (unsigned i = 0; i < 4; i++)
		if (before[i] != tag + i || after[i] != tag + 16U + i)
			return 0;
	return 1;
}

static void require_equal(const char *label, const void *left,
	const void *right, size_t bytes, unsigned trial)
{
	if (memcmp(left, right, bytes) != 0) {
		fprintf(stderr, "%s mismatch at trial %u\n", label, trial);
		exit(1);
	}
}

static void make_sotp_input(const int16_t m[WORDS], uint32_t *state,
	int malformed)
{
	memset(sotp_buf, 0, sizeof sotp_buf);
	unsigned first_nonzero = WORDS;
	for (unsigned coefficient = 0; coefficient < WORDS; coefficient++) {
		const unsigned nz = m[coefficient] != 0;
		const unsigned neg = m[coefficient] < 0;
		const unsigned t2 = nz != 0U ? neg : (next_random(state) & 1U);
		const unsigned message = next_random(state) & 1U;
		set_bit(sotp_buf, coefficient, message ^ t2 ^ nz);
		set_bit(sotp_buf + GT32_SOTP_PLANE_BYTES, coefficient, t2);
		if (nz != 0U && first_nonzero == WORDS)
			first_nonzero = coefficient;
	}
	if (malformed != 0 && first_nonzero < WORDS) {
		const unsigned old = get_bit(
			sotp_buf + GT32_SOTP_PLANE_BYTES, first_nonzero);
		set_bit(sotp_buf + GT32_SOTP_PLANE_BYTES, first_nonzero, old ^ 1U);
	}
}

static void verify_sidecar(const int16_t m[WORDS],
	const gt32_sotp_sidecar_t *sidecar, unsigned trial)
{
	for (unsigned coefficient = 0; coefficient < WORDS; coefficient++) {
		const unsigned neg = get_bit(sidecar->neg, coefficient);
		const unsigned nz = get_bit(sidecar->nz, coefficient);
		if (neg != (unsigned)(m[coefficient] < 0)
			|| nz != (unsigned)(m[coefficient] != 0)) {
			fprintf(stderr,
				"sidecar mismatch trial=%u coefficient=%u value=%d neg=%u nz=%u\n",
				trial, coefficient, m[coefficient], neg, nz);
			exit(1);
		}
	}
}

static void prepare_source(uint32_t *state)
{
	uint8_t a_bytes[BYTES] __attribute__((aligned(64)));
	uint8_t b_bytes[BYTES] __attribute__((aligned(64)));
	int16_t a[WORDS] __attribute__((aligned(64)));
	int16_t b[WORDS] __attribute__((aligned(64)));
	int16_t product[WORDS] __attribute__((aligned(64)));

	encode_components(a_bytes, state);
	encode_components(b_bytes, state);
	if (gt32_q24_decode_soa_asm(a, a_bytes) != 0
		|| gt32_q24_decode_soa_asm(b, b_bytes) != 0) {
		fprintf(stderr, "canonical setup decode failed\n");
		exit(1);
	}
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(product, a, b);
	gt32_tile4_inverse_all_pair_asm(rows.words, product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(source_m.words,
		rows.words);
}

static void control_producer(void)
{
	memcpy(control_m.words, source_m.words, sizeof control_m.words);
	poly_crepmod3((poly *)(void *)control_m.words);
	sink += (uint16_t)control_m.words[37];
}

static void s1_producer(void)
{
	memcpy(s1_m.words, source_m.words, sizeof s1_m.words);
	gt32_poly_crepmod3_sidecar_s1_asm(s1_m.words, &s1_sidecar.value);
	sink += (uint16_t)s1_m.words[37];
}

static void s2_producer(void)
{
	memcpy(s2_m.words, source_m.words, sizeof s2_m.words);
	gt32_poly_crepmod3_sidecar_s2_asm(s2_m.words, &s2_sidecar.value);
	sink += (uint16_t)s2_m.words[37];
}

static void control_sotp(void)
{
	const int fail = poly_sotp_decode(control_msg,
		(const poly *)(const void *)control_m.words, sotp_buf);
	sink += control_msg[11] ^ (unsigned)fail;
}

static void s1_sotp(void)
{
	const int fail = gt32_sotp_decode_sidecar(candidate_msg,
		&s1_sidecar.value, sotp_buf);
	sink += candidate_msg[11] ^ (unsigned)fail;
}

static void s2_sotp(void)
{
	const int fail = gt32_sotp_decode_sidecar(candidate_msg,
		&s2_sidecar.value, sotp_buf);
	sink += candidate_msg[11] ^ (unsigned)fail;
}

static void control_region(void)
{
	control_producer();
	control_sotp();
}

static void s1_region(void)
{
	s1_producer();
	s1_sotp();
}

static void s2_region(void)
{
	s2_producer();
	s2_sotp();
}

static void control_n5_region(void)
{
	control_producer();
	gt32_tile4_frontend_wide_raw_asm(control_n5.words, control_m.words);
	control_sotp();
	sink += (uint16_t)control_n5.words[91];
}

static void s1_n5_region(void)
{
	s1_producer();
	gt32_tile4_frontend_wide_raw_asm(candidate_n5.words, s1_m.words);
	s1_sotp();
	sink += (uint16_t)candidate_n5.words[91];
}

static void s2_n5_region(void)
{
	s2_producer();
	gt32_tile4_frontend_wide_raw_asm(candidate_n5.words, s2_m.words);
	s2_sotp();
	sink += (uint16_t)candidate_n5.words[91];
}

static void sidecar_truth_table(void)
{
	/* Every physical coefficient lane sees each post-crep value exactly once. */
	for (unsigned phase = 0; phase < 3; phase++) {
		for (unsigned coefficient = 0; coefficient < WORDS; coefficient++)
			source_m.words[coefficient] =
				(int16_t)((int)((coefficient + phase) % 3U) - 1);
		control_producer();
		s1_producer();
		s2_producer();
		require_equal("S1 truth-table full m", s1_m.words,
			control_m.words, sizeof control_m.words, phase);
		require_equal("S2 truth-table full m", s2_m.words,
			control_m.words, sizeof control_m.words, phase);
		verify_sidecar(control_m.words, &s1_sidecar.value, phase);
		verify_sidecar(control_m.words, &s2_sidecar.value, phase);
	}
}

static unsigned correctness(void)
{
	uint32_t state = UINT32_C(0xc2a20001);
	sidecar_truth_table();
	for (unsigned trial = 0; trial < 1000; trial++) {
		prepare_source(&state);
		control_producer();
		s1_producer();
		s2_producer();
		require_equal("S1 full m", s1_m.words, control_m.words,
			sizeof control_m.words, trial);
		require_equal("S2 full m", s2_m.words, control_m.words,
			sizeof control_m.words, trial);
		verify_sidecar(control_m.words, &s1_sidecar.value, trial);
		verify_sidecar(control_m.words, &s2_sidecar.value, trial);

		gt32_tile4_frontend_wide_raw_asm(control_n5.words, control_m.words);
		gt32_tile4_frontend_wide_raw_asm(candidate_n5.words, s1_m.words);
		require_equal("S1 N5", candidate_n5.words, control_n5.words,
			sizeof control_n5.words, trial);
		gt32_tile4_frontend_wide_raw_asm(candidate_n5.words, s2_m.words);
		require_equal("S2 N5", candidate_n5.words, control_n5.words,
			sizeof control_n5.words, trial);

		for (unsigned malformed = 0; malformed < 2; malformed++) {
			make_sotp_input(control_m.words, &state, (int)malformed);
			memset(control_msg, 0xa5, sizeof control_msg);
			memset(candidate_msg, 0x5a, sizeof candidate_msg);
			const int control_fail = poly_sotp_decode(control_msg,
				(const poly *)(const void *)control_m.words, sotp_buf);
			const int s1_fail = gt32_sotp_decode_sidecar(candidate_msg,
				&s1_sidecar.value, sotp_buf);
			if (s1_fail != control_fail) {
				fprintf(stderr, "S1 failure mismatch trial=%u malformed=%u\n",
					trial, malformed);
				exit(1);
			}
			require_equal("S1 SOTP message", candidate_msg, control_msg,
				sizeof control_msg, trial);

			memset(candidate_msg, 0x5a, sizeof candidate_msg);
			const int s2_fail = gt32_sotp_decode_sidecar(candidate_msg,
				&s2_sidecar.value, sotp_buf);
			if (s2_fail != control_fail) {
				fprintf(stderr, "S2 failure mismatch trial=%u malformed=%u\n",
					trial, malformed);
				exit(1);
			}
			require_equal("S2 SOTP message", candidate_msg, control_msg,
				sizeof control_msg, trial);
		}
	}
	return 1000;
}

static uint64_t start_tsc(void)
{
	_mm_lfence();
	return __rdtsc();
}

static uint64_t stop_tsc(void)
{
	unsigned aux;
	const uint64_t result = __rdtscp(&aux);
	_mm_lfence();
	return result;
}

static double measure(region_fn fn, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned iteration = 0; iteration < iterations; iteration++)
		fn();
	return (double)(stop_tsc() - begin) / iterations;
}

static void print_gate(const char *name, region_fn control,
	region_fn candidate, unsigned iterations)
{
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double control_cycles;
		double candidate_cycles;
		if ((sample & 1U) == 0U) {
			control_cycles = measure(control, iterations);
			candidate_cycles = measure(candidate, iterations);
		} else {
			candidate_cycles = measure(candidate, iterations);
			control_cycles = measure(control, iterations);
		}
		printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n", name, sample,
			control_cycles, candidate_cycles,
			candidate_cycles - control_cycles);
	}
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0)
		perror("sched_setaffinity");

	initialize_guard(&rows, sizeof rows, UINT64_C(0x1000));
	initialize_guard(&source_m, sizeof source_m, UINT64_C(0x2000));
	initialize_guard(&control_m, sizeof control_m, UINT64_C(0x3000));
	initialize_guard(&s1_m, sizeof s1_m, UINT64_C(0x4000));
	initialize_guard(&s2_m, sizeof s2_m, UINT64_C(0x5000));
	initialize_guard(&control_n5, sizeof control_n5, UINT64_C(0x6000));
	initialize_guard(&candidate_n5, sizeof candidate_n5, UINT64_C(0x7000));
	initialize_guard(&s1_sidecar, sizeof s1_sidecar, UINT64_C(0x8000));
	initialize_guard(&s2_sidecar, sizeof s2_sidecar, UINT64_C(0x9000));
	const unsigned trials = correctness();
	if (!guard_valid(&rows, sizeof rows, UINT64_C(0x1000))
		|| !guard_valid(&source_m, sizeof source_m, UINT64_C(0x2000))
		|| !guard_valid(&control_m, sizeof control_m, UINT64_C(0x3000))
		|| !guard_valid(&s1_m, sizeof s1_m, UINT64_C(0x4000))
		|| !guard_valid(&s2_m, sizeof s2_m, UINT64_C(0x5000))
		|| !guard_valid(&control_n5, sizeof control_n5, UINT64_C(0x6000))
		|| !guard_valid(&candidate_n5, sizeof candidate_n5, UINT64_C(0x7000))
		|| !guard_valid(&s1_sidecar, sizeof s1_sidecar, UINT64_C(0x8000))
		|| !guard_valid(&s2_sidecar, sizeof s2_sidecar, UINT64_C(0x9000))) {
		fprintf(stderr, "guard corruption\n");
		return 1;
	}

	uint32_t state = UINT32_C(0x12345678);
	prepare_source(&state);
	control_producer();
	s1_producer();
	s2_producer();
	make_sotp_input(control_m.words, &state, 0);
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(control_n5_region, 1000);
		(void)measure(s1_n5_region, 1000);
		(void)measure(s2_n5_region, 1000);
	}

	printf("META,correctness=crep-sidecar-byte-exact,trials=%u,iterations=%u,samples=%u,full_m_materialized=1,n5_path=unchanged\n",
		trials, iterations, SAMPLES);
	print_gate("producer_s1", control_producer, s1_producer, iterations);
	print_gate("producer_s2", control_producer, s2_producer, iterations);
	print_gate("sotp", control_sotp, s1_sotp, iterations);
	print_gate("crep_sotp_s1", control_region, s1_region, iterations);
	print_gate("crep_sotp_s2", control_region, s2_region, iterations);
	print_gate("crep_n5_sotp_s1", control_n5_region, s1_n5_region, iterations);
	print_gate("crep_n5_sotp_s2", control_n5_region, s2_n5_region, iterations);
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}

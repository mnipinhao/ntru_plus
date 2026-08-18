#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <x86intrin.h>

#include "tile4.h"
#include "../generated/tile4_serialized_mapping.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define BYTES GT32_TILE4_SERIALIZED_BYTES
#define SAMPLES 20
#define Q GT32_TILE4_Q

typedef int (*decode_fn)(int16_t *, const uint8_t *);
typedef void (*encode_fn)(uint8_t *, const int16_t *);
typedef int (*decode3_fn)(int16_t *, int16_t *, int16_t *,
	const uint8_t *, const uint8_t *);

static int16_t scratch_soa[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

static uint32_t next_random(uint32_t *state)
{
	*state = *state * 1664525U + 1013904223U;
	return *state;
}

static void pack_reference(uint8_t out[BYTES], const int16_t in[WORDS],
	const uint16_t mapping[WORDS])
{
	for (unsigned pair = 0; pair < WORDS / 2; pair++) {
		int32_t x = in[mapping[2U * pair]];
		int32_t y = in[mapping[2U * pair + 1U]];
		if (x < 0)
			x += Q;
		if (y < 0)
			y += Q;
		if ((unsigned)x >= Q || (unsigned)y >= Q) {
			fprintf(stderr, "pack reference range failure\n");
			exit(1);
		}
		out[3U * pair] = (uint8_t)x;
		out[3U * pair + 1U] = (uint8_t)((unsigned)x >> 8)
			| (uint8_t)((unsigned)y << 4);
		out[3U * pair + 2U] = (uint8_t)((unsigned)y >> 4);
	}
}

static void pack_reference_lazy10788(uint8_t out[BYTES],
	const int16_t in[WORDS], const uint16_t mapping[WORDS])
{
	for (unsigned pair = 0; pair < WORDS / 2; pair++) {
		int32_t x = (int32_t)in[mapping[2U * pair]] % Q;
		int32_t y = (int32_t)in[mapping[2U * pair + 1U]] % Q;
		if (x < 0)
			x += Q;
		if (y < 0)
			y += Q;
		out[3U * pair] = (uint8_t)x;
		out[3U * pair + 1U] = (uint8_t)((unsigned)x >> 8)
			| (uint8_t)((unsigned)y << 4);
		out[3U * pair + 2U] = (uint8_t)((unsigned)y >> 4);
	}
}

static void fill_centered(int16_t out[WORDS], uint32_t *state,
	unsigned trial)
{
	for (unsigned i = 0; i < WORDS; i++) {
		if (trial == 0)
			out[i] = 0;
		else if (trial == 1)
			out[i] = (int16_t)((i & 1U) ? -1728 : 1728);
		else
			out[i] = (int16_t)((int32_t)(next_random(state) % Q) - 1728);
	}
}

static void malformed_slot(uint8_t bytes[BYTES], unsigned slot)
{
	const unsigned pair = slot / 2U;
	const unsigned offset = 3U * pair;
	if ((slot & 1U) == 0U) {
		bytes[offset] = (uint8_t)Q;
		bytes[offset + 1U] = (uint8_t)((bytes[offset + 1U] & 0xf0U)
			| ((unsigned)Q >> 8));
	} else {
		bytes[offset + 1U] = (uint8_t)((bytes[offset + 1U] & 0x0fU)
			| ((unsigned)Q << 4));
		bytes[offset + 2U] = (uint8_t)((unsigned)Q >> 4);
	}
}

static void require_equal(const char *label, const void *a, const void *b,
	size_t size)
{
	if (memcmp(a, b, size) != 0) {
		fprintf(stderr, "%s mismatch\n", label);
		exit(1);
	}
}

static void guard_test(void)
{
	const long page = sysconf(_SC_PAGESIZE);
	uint8_t *mapping = mmap(NULL, (size_t)(2 * page),
		PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
	int16_t output[WORDS] __attribute__((aligned(64)));
	int16_t input[WORDS] __attribute__((aligned(64))) = {0};
	if (mapping == MAP_FAILED || mprotect(mapping + page, (size_t)page,
		PROT_NONE) != 0) {
		perror("guard mapping");
		exit(1);
	}
	uint8_t *edge = mapping + page - BYTES;
	memset(edge, 0, BYTES);
	if (gt32_q24_decode_aos_asm(output, edge) != 0)
		exit(1);
	gt32_q24_encode_aos_asm(edge, input);
	gt32_q24_encode_soa_lazy10788_asm(edge, input);
	gt32_q24_encode_soa_encap_hr_h1_asm(edge, input);
	gt32_q24_encode_soa_encap_hr_sum_asm(edge, input, input);
	gt32_q24_encode_soa_encap_hr_h2_asm(edge, input);
	if (gt32_q24_encode_soa_lazy10788_verify_asm(edge, input) != 0)
		exit(1);
	if (munmap(mapping, (size_t)(2 * page)) != 0)
		exit(1);
}

static void correctness(void)
{
	int16_t aos[WORDS] __attribute__((aligned(64)));
	int16_t soa[WORDS] __attribute__((aligned(64)));
	int16_t reference[WORDS] __attribute__((aligned(64)));
	int16_t candidate[WORDS] __attribute__((aligned(64)));
	uint8_t bytes[BYTES] __attribute__((aligned(64)));
	uint8_t encoded[BYTES + 16] __attribute__((aligned(64)));
	uint8_t expected[BYTES] __attribute__((aligned(64)));
	uint8_t three_bytes[3 * BYTES] __attribute__((aligned(64)));
	int16_t c0[WORDS] __attribute__((aligned(64)));
	int16_t f0[WORDS] __attribute__((aligned(64)));
	int16_t h0[WORDS] __attribute__((aligned(64)));
	int16_t c1[WORDS] __attribute__((aligned(64)));
	int16_t f1[WORDS] __attribute__((aligned(64)));
	int16_t h1[WORDS] __attribute__((aligned(64)));
	int16_t product[WORDS] __attribute__((aligned(64)));
	int16_t message[WORDS] __attribute__((aligned(64)));
	int16_t sum[WORDS] __attribute__((aligned(64)));
	uint32_t state = UINT32_C(0x024c0dec);

	for (unsigned trial = 0; trial < 1000; trial++) {
		fill_centered(aos, &state, trial);
		pack_reference(bytes, aos, gt32_tile4_serialized_to_aos);
		if (gt32_tile4_frombytes_aos_ref(reference, bytes) != 0
			|| gt32_q24_decode_aos_asm(candidate, bytes) != 0)
			exit(1);
		require_equal("decode-aos", candidate, reference, sizeof(reference));
		if (gt32_tile4_frombytes_bm_soa_ref(reference, bytes) != 0
			|| gt32_q24_decode_soa_asm(candidate, bytes) != 0)
			exit(1);
		require_equal("decode-soa", candidate, reference, sizeof(reference));

		memset(encoded, 0xa5, sizeof(encoded));
		gt32_q24_encode_aos_asm(encoded, aos);
		require_equal("encode-aos", encoded, bytes, BYTES);
		for (unsigned i = BYTES; i < sizeof(encoded); i++)
			if (encoded[i] != 0xa5)
				exit(1);

		gt32_tile4_attr_transpose_one_asm(soa, aos);
		pack_reference(expected, soa, gt32_tile4_serialized_to_bm_soa);
		require_equal("soa-reference", expected, bytes, BYTES);
		memset(encoded, 0xa5, sizeof(encoded));
		gt32_q24_encode_soa_asm(encoded, soa);
		require_equal("encode-soa", encoded, bytes, BYTES);
		for (unsigned i = BYTES; i < sizeof(encoded); i++)
			if (encoded[i] != 0xa5)
				exit(1);
	}

	/* Encap serializer-side sum: B3-general e=0 plus N5 e=0. */
	for (unsigned trial = 0; trial < 1000; trial++) {
		for (unsigned i = 0; i < WORDS; i++) {
			const int32_t product_bound = 1911;
			const int32_t message_bound = 10788;
			product[i] = (int16_t)((int32_t)(next_random(&state)
				% (uint32_t)(2 * product_bound + 1)) - product_bound);
			message[i] = (int16_t)((int32_t)(next_random(&state)
				% (uint32_t)(2 * message_bound + 1)) - message_bound);
			sum[i] = (int16_t)((int32_t)product[i] + message[i]);
		}
		pack_reference_lazy10788(expected, sum,
			gt32_tile4_serialized_to_bm_soa);
		memset(encoded, 0xa5, sizeof(encoded));
		gt32_q24_encode_soa_encap_hr_sum_asm(encoded, product, message);
		require_equal("encode-soa-encap-sum", encoded, expected, BYTES);
		for (unsigned i = BYTES; i < sizeof(encoded); i++)
			if (encoded[i] != 0xa5)
				exit(1);
	}

	/* Exhaust the complete public lazy10788 scalar contract. */
	for (int32_t value = -10788; value <= 10788; value++) {
		for (unsigned i = 0; i < WORDS; i++)
			soa[i] = (int16_t)value;
		pack_reference_lazy10788(expected, soa,
			gt32_tile4_serialized_to_bm_soa);
		memset(encoded, 0xa5, sizeof(encoded));
		gt32_q24_encode_soa_lazy10788_asm(encoded, soa);
		require_equal("encode-soa-lazy10788-exhaustive", encoded,
			expected, BYTES);
		if (gt32_q24_encode_soa_lazy10788_verify_asm(expected, soa) != 0) {
			fprintf(stderr, "lazy10788 verify equality failed value=%d\n",
				(int)value);
			exit(1);
		}
		for (unsigned i = BYTES; i < sizeof(encoded); i++)
			if (encoded[i] != 0xa5)
				exit(1);
	}

	/* Exercise mixed lanes, every routing pattern and the full bound. */
	for (unsigned trial = 0; trial < 1000; trial++) {
		for (unsigned i = 0; i < WORDS; i++) {
			if (trial == 0)
				soa[i] = (int16_t)((i & 1U) ? -10788 : 10788);
			else if (trial == 1)
				soa[i] = (int16_t)((int32_t)(i % 7U) * Q - 10371);
			else
				soa[i] = (int16_t)((int32_t)(next_random(&state)
					% 21577U) - 10788);
		}
		memcpy(reference, soa, sizeof(reference));
		pack_reference_lazy10788(expected, soa,
			gt32_tile4_serialized_to_bm_soa);
		memset(encoded, 0xa5, sizeof(encoded));
		gt32_q24_encode_soa_lazy10788_asm(encoded, soa);
		require_equal("encode-soa-lazy10788-random", encoded, expected,
			BYTES);
		if (gt32_q24_encode_soa_lazy10788_verify_asm(expected, soa) != 0)
			exit(1);
		expected[trial % BYTES] ^= UINT8_C(1);
		if (gt32_q24_encode_soa_lazy10788_verify_asm(expected, soa) != 1)
			exit(1);
		expected[trial % BYTES] ^= UINT8_C(1);
		require_equal("encode-soa-lazy10788-nondestructive", soa,
			reference, sizeof(reference));
		for (unsigned i = BYTES; i < sizeof(encoded); i++)
			if (encoded[i] != 0xa5)
				exit(1);
	}

	/* Exhaust the typed encap B3-general + m contract. */
	for (int32_t value = -12699; value <= 12699; value++) {
		for (unsigned i = 0; i < WORDS; i++)
			soa[i] = (int16_t)value;
		pack_reference_lazy10788(expected, soa,
			gt32_tile4_serialized_to_bm_soa);
		memset(encoded, 0xa5, sizeof(encoded));
		gt32_q24_encode_soa_encap_hr_h1_asm(encoded, soa);
		require_equal("encode-soa-encap-hr-h1-exhaustive", encoded,
			expected, BYTES);
		for (unsigned i = BYTES; i < sizeof(encoded); i++)
			if (encoded[i] != 0xa5)
				exit(1);
		memset(encoded, 0xa5, sizeof(encoded));
		gt32_q24_encode_soa_encap_hr_h2_asm(encoded, soa);
		require_equal("encode-soa-encap-hr-h2-exhaustive", encoded,
			expected, BYTES);
		for (unsigned i = BYTES; i < sizeof(encoded); i++)
			if (encoded[i] != 0xa5)
				exit(1);
	}
	for (unsigned trial = 0; trial < 1000; trial++) {
		for (unsigned i = 0; i < WORDS; i++)
			soa[i] = trial == 0
				? (int16_t)((i & 1U) ? -12699 : 12699)
				: (int16_t)((int32_t)(next_random(&state) % 25399U)
					- 12699);
		memcpy(reference, soa, sizeof(reference));
		pack_reference_lazy10788(expected, soa,
			gt32_tile4_serialized_to_bm_soa);
		gt32_q24_encode_soa_encap_hr_h1_asm(encoded, soa);
		require_equal("encode-soa-encap-hr-h1-random", encoded,
			expected, BYTES);
		gt32_q24_encode_soa_encap_hr_h2_asm(encoded, soa);
		require_equal("encode-soa-encap-hr-h2-random", encoded,
			expected, BYTES);
		require_equal("encode-soa-encap-hr-nondestructive", soa,
			reference, sizeof(reference));
	}

	/* Every expected-byte position must contribute to the mismatch mask. */
	memset(soa, 0, sizeof(soa));
	memset(expected, 0, sizeof(expected));
	for (unsigned byte = 0; byte < BYTES; byte++) {
		expected[byte] = UINT8_C(1);
		if (gt32_q24_encode_soa_lazy10788_verify_asm(expected, soa) != 1) {
			fprintf(stderr, "lazy10788 verify missed byte=%u\n", byte);
			exit(1);
		}
		expected[byte] = 0;
	}

	memset(bytes, 0, sizeof(bytes));
	for (unsigned slot = 0; slot < WORDS; slot++) {
		memset(bytes, 0, sizeof(bytes));
		malformed_slot(bytes, slot);
		if (gt32_q24_decode_aos_asm(candidate, bytes) != 1
			|| gt32_q24_decode_soa_asm(reference, bytes) != 1) {
			fprintf(stderr, "malformed rejection failed slot=%u\n", slot);
			exit(1);
		}
	}
	memset(three_bytes, 0, sizeof(three_bytes));
	for (unsigned source = 0; source < 3; source++) {
		for (unsigned slot = 0; slot < WORDS; slot++) {
			memset(three_bytes, 0, sizeof(three_bytes));
			malformed_slot(three_bytes + source * BYTES, slot);
			const int r0 = gt32_tile4_frombytes3_bm_soa_semantic_asm(
				c0, f0, h0, three_bytes, three_bytes + BYTES);
			const int r1 = gt32_q24_decode3_soa_asm(
				c1, f1, h1, three_bytes, three_bytes + BYTES);
			if (r0 != 1 || r1 != r0) {
				fprintf(stderr, "decode3 rejection failed source=%u slot=%u\n",
					source, slot);
				exit(1);
			}
			require_equal("decode3-c", c1, c0, sizeof(c0));
			require_equal("decode3-f", f1, f0, sizeof(f0));
			require_equal("decode3-h", h1, h0, sizeof(h0));
		}
	}
	guard_test();
}

static int control_decode_aos(int16_t *out, const uint8_t *in)
{
	return gt32_tile4_frombytes_aos_asm(out, in);
}

static int candidate_decode_aos(int16_t *out, const uint8_t *in)
{
	return gt32_q24_decode_aos_asm(out, in);
}

static int control_decode_soa(int16_t *out, const uint8_t *in)
{
	return gt32_tile4_frombytes_bm_soa_semantic_asm(out, in);
}

static int candidate_decode_soa(int16_t *out, const uint8_t *in)
{
	return gt32_q24_decode_soa_asm(out, in);
}

static void control_encode_aos(uint8_t *out, const int16_t *in)
{
	gt32_tile4_attr_transpose_one_asm(scratch_soa, in);
	gt32_tile4_soa_tobytes_direct_asm(out, scratch_soa);
}

static void candidate_encode_aos(uint8_t *out, const int16_t *in)
{
	gt32_q24_encode_aos_asm(out, in);
}

static void control_encode_soa(uint8_t *out, const int16_t *in)
{
	gt32_tile4_soa_tobytes_direct_asm(out, in);
}

static void candidate_encode_soa(uint8_t *out, const int16_t *in)
{
	gt32_q24_encode_soa_asm(out, in);
}

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

static double measure_decode(decode_fn fn, int16_t *out, const uint8_t *in,
	unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)fn(out, in);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations % WORDS];
	return (double)(end - begin) / iterations;
}

static double measure_encode(encode_fn fn, uint8_t *out, const int16_t *in,
	unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, in);
	const uint64_t end = stop_tsc();
	sink += out[iterations % BYTES];
	return (double)(end - begin) / iterations;
}

static double measure_decode3(decode3_fn fn, int16_t *c, int16_t *f,
	int16_t *h, const uint8_t *ct, const uint8_t *sk, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)fn(c, f, h, ct, sk);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)c[iterations % WORDS];
	return (double)(end - begin) / iterations;
}

static void sample_decode(const char *name, decode_fn control,
	decode_fn candidate, int16_t *out0, int16_t *out1, const uint8_t *in,
	unsigned iterations)
{
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double c, n;
		if ((sample & 1U) == 0U) {
			c = measure_decode(control, out0, in, iterations);
			n = measure_decode(candidate, out1, in, iterations);
		} else {
			n = measure_decode(candidate, out1, in, iterations);
			c = measure_decode(control, out0, in, iterations);
		}
		printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n", name, sample,
			c, n, n - c);
	}
}

static void sample_encode(const char *name, encode_fn control,
	encode_fn candidate, uint8_t *out0, uint8_t *out1, const int16_t *in,
	unsigned iterations)
{
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double c, n;
		if ((sample & 1U) == 0U) {
			c = measure_encode(control, out0, in, iterations);
			n = measure_encode(candidate, out1, in, iterations);
		} else {
			n = measure_encode(candidate, out1, in, iterations);
			c = measure_encode(control, out0, in, iterations);
		}
		printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n", name, sample,
			c, n, n - c);
	}
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t aos[WORDS] __attribute__((aligned(64)));
	int16_t soa[WORDS] __attribute__((aligned(64)));
	int16_t out0[WORDS] __attribute__((aligned(64)));
	int16_t out1[WORDS] __attribute__((aligned(64)));
	int16_t f[WORDS] __attribute__((aligned(64)));
	int16_t h[WORDS] __attribute__((aligned(64)));
	uint8_t bytes[BYTES] __attribute__((aligned(64)));
	uint8_t sk[2 * BYTES] __attribute__((aligned(64)));
	uint8_t enc0[BYTES] __attribute__((aligned(64)));
	uint8_t enc1[BYTES] __attribute__((aligned(64)));
	uint32_t state = 1;
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	correctness();
	fill_centered(aos, &state, 3);
	pack_reference(bytes, aos, gt32_tile4_serialized_to_aos);
	memcpy(sk, bytes, BYTES);
	memcpy(sk + BYTES, bytes, BYTES);
	gt32_tile4_attr_transpose_one_asm(soa, aos);

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure_decode(control_decode_aos, out0, bytes, 1000);
		(void)measure_decode(candidate_decode_aos, out1, bytes, 1000);
		(void)measure_decode(control_decode_soa, out0, bytes, 1000);
		(void)measure_decode(candidate_decode_soa, out1, bytes, 1000);
		(void)measure_encode(control_encode_aos, enc0, aos, 1000);
		(void)measure_encode(candidate_encode_aos, enc1, aos, 1000);
	}
	printf("META,correctness=exact-pass,trials=1000,malformed=3072,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	sample_decode("decode_aos", control_decode_aos, candidate_decode_aos,
		out0, out1, bytes, iterations);
	sample_decode("decode_soa", control_decode_soa, candidate_decode_soa,
		out0, out1, bytes, iterations);
	sample_encode("encode_aos", control_encode_aos, candidate_encode_aos,
		enc0, enc1, aos, iterations);
	sample_encode("encode_soa", control_encode_soa, candidate_encode_soa,
		enc0, enc1, soa, iterations);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double c, n;
		if ((sample & 1U) == 0U) {
			c = measure_decode3(gt32_tile4_frombytes3_bm_soa_semantic_asm,
				out0, f, h, bytes, sk, iterations);
			n = measure_decode3(gt32_q24_decode3_soa_asm, out1, f, h,
				bytes, sk, iterations);
		} else {
			n = measure_decode3(gt32_q24_decode3_soa_asm, out1, f, h,
				bytes, sk, iterations);
			c = measure_decode3(gt32_tile4_frombytes3_bm_soa_semantic_asm,
				out0, f, h, bytes, sk, iterations);
		}
		printf("SAMPLE,decode3_soa,%u,%.6f,%.6f,%.6f\n", sample,
			c, n, n - c);
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}

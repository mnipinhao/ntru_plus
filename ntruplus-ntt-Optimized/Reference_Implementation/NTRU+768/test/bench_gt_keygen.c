#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "api.h"
#include "gt_keygen_native.h"
#include "gt_native_pack.h"
#include "params.h"
#include "poly.h"
#include "randombytes.h"

int ntruplus_ref_keypair_derand(
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES],
	const uint8_t f_coins[NTRUPLUS_SYMBYTES],
	const uint8_t g_coins[NTRUPLUS_SYMBYTES]);

int ntruplus_ref_enc_derand(
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);

static uint64_t deterministic_rng_state =
	UINT64_C(0x243f6a8885a308d3);
static volatile uint64_t output_sink;

#define COMPONENT_SETS 64U
#define COMPONENT_WARMUPS 1000U

static poly component_f[COMPONENT_SETS];
static poly component_g[COMPONENT_SETS];
static poly component_ref_f[COMPONENT_SETS];
static poly component_ref_g[COMPONENT_SETS];
static poly component_gt_f[COMPONENT_SETS];
static poly component_gt_g[COMPONENT_SETS];
static poly component_ref_finv[COMPONENT_SETS];
static poly component_gt_finv[COMPONENT_SETS];
static poly component_ref_output[COMPONENT_SETS];
static poly component_gt_output[COMPONENT_SETS];

static uint64_t next_u64(void)
{
	uint64_t value = deterministic_rng_state;

	value ^= value << 13;
	value ^= value >> 7;
	value ^= value << 17;
	deterministic_rng_state = value;
	return value;
}

void randombytes(uint8_t *out, size_t outlen)
{
	while (outlen != 0U) {
		const uint64_t value = next_u64();
		size_t count = outlen < sizeof(value) ? outlen : sizeof(value);

		for (size_t i = 0; i < count; i++) {
			out[i] = (uint8_t)(value >> (8U * i));
		}
		out += count;
		outlen -= count;
	}
}

static void reset_randombytes(void)
{
	deterministic_rng_state = UINT64_C(0x243f6a8885a308d3);
}

static uint16_t canonical_reference(int16_t value)
{
	int32_t reduced = (int32_t)value % NTRUPLUS_Q;

	if (reduced < 0) {
		reduced += NTRUPLUS_Q;
	}
	return (uint16_t)reduced;
}

static void production_to_native(poly *native, const poly *production)
{
	for (unsigned production_batch = 0; production_batch < 12U;
	     production_batch++) {
		for (unsigned coefficient = 0; coefficient < 4U;
		     coefficient++) {
			for (unsigned lane = 0; lane < 16U; lane++) {
				const unsigned production_quartic =
					16U * production_batch + lane;
				const unsigned native_quartic =
					gt_production_to_native_quartic[
						production_quartic];
				const unsigned production_index =
					64U * production_batch +
					16U * coefficient + lane;
				const unsigned native_index =
					64U * (native_quartic >> 4) +
					16U * coefficient +
					(native_quartic & 15U);

				native->coeffs[native_index] =
					production->coeffs[production_index];
			}
		}
	}
}

static int validate_native_pack(void)
{
	uint8_t seen[GT_NATIVE_QUARTIC_SLOTS] = {0};
	uint8_t production_bytes[NTRUPLUS_POLYBYTES];
	uint8_t native_bytes[NTRUPLUS_POLYBYTES];
#if defined(GT_HAVE_AVX2_ASM) && GT_HAVE_AVX2_ASM
	uint8_t native_asm_bytes[NTRUPLUS_POLYBYTES];
#endif
	poly production;
	poly native;
	uint32_t value_index = 0;

	for (uint32_t encoded = 0; encoded <= UINT16_MAX; encoded++) {
		const int16_t value = (int16_t)(uint16_t)encoded;
		const uint16_t got =
			gt_native_pack_canonicalize_test(value);
		const uint16_t want = canonical_reference(value);

		if (got != want) {
			fprintf(stderr,
				"native-pack canonical mismatch input=%d got=%u want=%u\n",
				value, (unsigned)got, (unsigned)want);
			return 1;
		}
	}

	for (unsigned production_slot = 0;
	     production_slot < GT_NATIVE_QUARTIC_SLOTS;
	     production_slot++) {
		const unsigned native_slot =
			gt_production_to_native_quartic[production_slot];

		if (native_slot >= GT_NATIVE_QUARTIC_SLOTS ||
		    seen[native_slot] != 0U ||
		    gt_native_to_production_quartic[native_slot] !=
			    production_slot) {
			fprintf(stderr,
				"native-pack map is not a bijection at production slot %u\n",
				production_slot);
			return 1;
		}
		seen[native_slot] = 1;
	}

	/*
	 * 86 polynomials cover all 65,536 signed-int16 bit patterns at least
	 * once while exercising every quartic coefficient position.
	 */
	for (unsigned round = 0; round < 86U; round++) {
		for (unsigned i = 0; i < NTRUPLUS_N; i++) {
			production.coeffs[i] =
				(int16_t)(uint16_t)value_index;
			value_index++;
		}
		production_to_native(&native, &production);
		poly_tobytes(production_bytes, &production);
		gt_poly_tobytes_native(native_bytes, &native);
#if defined(GT_HAVE_AVX2_ASM) && GT_HAVE_AVX2_ASM
		gt_poly_tobytes_native_asm_avx2(native_asm_bytes, &native);
#endif
		if (memcmp(production_bytes, native_bytes,
			   sizeof(production_bytes)) != 0) {
			fprintf(stderr,
				"native-pack WIRE12 mismatch round=%u\n", round);
			return 1;
		}
#if defined(GT_HAVE_AVX2_ASM) && GT_HAVE_AVX2_ASM
		if (memcmp(production_bytes, native_asm_bytes,
			   sizeof(production_bytes)) != 0) {
			fprintf(stderr,
				"native-pack AVX2 WIRE12 mismatch round=%u\n",
				round);
			return 1;
		}
#endif
	}

#if defined(GT_HAVE_AVX2_ASM) && GT_HAVE_AVX2_ASM
	uint32_t centered_index = 0;
	uint32_t l3_index = 0;

	/* Ten arrays cover all 6,913 centered representatives. */
	for (unsigned round = 0; round < 10U; round++) {
		for (unsigned i = 0; i < NTRUPLUS_N; i++) {
			const int32_t centered_value =
				(int32_t)(centered_index %
					(2U * NTRUPLUS_Q - 1U)) -
				(NTRUPLUS_Q - 1);

			production.coeffs[i] = (int16_t)centered_value;
			centered_index++;
		}
		production_to_native(&native, &production);
		poly_tobytes(production_bytes, &production);
		gt_poly_tobytes_native_centered_asm_avx2(
			native_asm_bytes, &native);
		if (memcmp(production_bytes, native_asm_bytes,
			   sizeof(production_bytes)) != 0) {
			fprintf(stderr,
				"native-pack centered mismatch round=%u\n",
				round);
			return 1;
		}
	}

	/* Twenty-seven arrays cover all 20,345 GTN-L3 representatives. */
	for (unsigned round = 0; round < 27U; round++) {
		for (unsigned i = 0; i < NTRUPLUS_N; i++) {
			const int32_t l3_value =
				(int32_t)(l3_index % 20345U) - 10172;

			production.coeffs[i] = (int16_t)l3_value;
			l3_index++;
		}
		production_to_native(&native, &production);
		poly_tobytes(production_bytes, &production);
		gt_poly_tobytes_native_l3_asm_avx2(
			native_asm_bytes, &native);
		if (memcmp(production_bytes, native_asm_bytes,
			   sizeof(production_bytes)) != 0) {
			fprintf(stderr,
				"native-pack L3 mismatch round=%u\n", round);
			return 1;
		}
	}
#endif
	return 0;
}

static void fill_coins(uint8_t *out, size_t length, uint32_t *state)
{
	for (size_t i = 0; i < length; i++) {
		uint32_t value = *state;

		value ^= value << 13;
		value ^= value >> 17;
		value ^= value << 5;
		*state = value;
		out[i] = (uint8_t)value;
	}
}

static int validate_keypair_island(void)
{
	uint8_t ref_pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t ref_sk[NTRUPLUS_SECRETKEYBYTES];
	uint8_t gt_pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t gt_sk[NTRUPLUS_SECRETKEYBYTES];
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t ss[NTRUPLUS_SSBYTES];
	uint8_t decapsulated[NTRUPLUS_SSBYTES];
	uint8_t f_coins[NTRUPLUS_SYMBYTES];
	uint8_t g_coins[NTRUPLUS_SYMBYTES];
	uint8_t enc_coins[NTRUPLUS_N / 8];
	uint32_t state = UINT32_C(0x6a09e667);
	unsigned successes = 0;
	unsigned attempts = 0;

	while (successes < 128U && attempts < 4096U) {
		int ref_status;
		int gt_status;

		fill_coins(f_coins, sizeof(f_coins), &state);
		fill_coins(g_coins, sizeof(g_coins), &state);
		ref_status = ntruplus_ref_keypair_derand(
			ref_pk, ref_sk, f_coins, g_coins);
		gt_status = ntruplus_gt_keypair_derand(
			gt_pk, gt_sk, f_coins, g_coins);
		attempts++;

		if (ref_status != gt_status) {
			fprintf(stderr,
				"keygen invertibility status mismatch attempt=%u ref=%d gt=%d\n",
				attempts, ref_status, gt_status);
			return 1;
		}
		if (ref_status != 0) {
			continue;
		}
		if (memcmp(ref_pk, gt_pk, sizeof(ref_pk)) != 0 ||
		    memcmp(ref_sk, gt_sk, sizeof(ref_sk)) != 0) {
			fprintf(stderr,
				"keygen byte mismatch success=%u attempt=%u\n",
				successes, attempts);
			return 1;
		}
		if (successes < 16U) {
			fill_coins(enc_coins, sizeof(enc_coins), &state);
			if (ntruplus_ref_enc_derand(
				    ct, ss, gt_pk, enc_coins) != 0 ||
			    crypto_kem_dec(decapsulated, ct, gt_sk) != 0 ||
			    memcmp(ss, decapsulated, sizeof(ss)) != 0) {
				fprintf(stderr,
					"native-island full KEM mismatch success=%u\n",
					successes);
				return 1;
			}
		}
		successes++;
	}

	if (successes != 128U) {
		fprintf(stderr,
			"insufficient invertible deterministic keypairs successes=%u attempts=%u\n",
			successes, attempts);
		return 1;
	}

	for (unsigned round = 0; round < 16U; round++) {
		reset_randombytes();
		deterministic_rng_state ^= (uint64_t)round + 1U;
		if (crypto_kem_keypair(ref_pk, ref_sk) != 0) {
			return 1;
		}
		reset_randombytes();
		deterministic_rng_state ^= (uint64_t)round + 1U;
		if (crypto_kem_keypair_gt(gt_pk, gt_sk) != 0 ||
		    memcmp(ref_pk, gt_pk, sizeof(ref_pk)) != 0 ||
		    memcmp(ref_sk, gt_sk, sizeof(ref_sk)) != 0) {
			fprintf(stderr,
				"public keypair stream mismatch round=%u\n", round);
			return 1;
		}
	}

	printf("native-pack: exhaustive int16 + WIRE12 layout passed\n");
	printf("keygen-island: 128 deterministic pairs + 16 full KEM/public streams passed\n");
	return 0;
}

static uint64_t checksum_bytes(const uint8_t *bytes, size_t length)
{
	uint64_t checksum = output_sink;

	for (size_t i = 0; i < length; i++) {
		checksum = (checksum << 5) ^ (checksum >> 2) ^ bytes[i];
	}
	return checksum;
}

typedef int (*keypair_fn)(unsigned char *pk, unsigned char *sk);

static int run_benchmark(keypair_fn keypair, size_t iterations,
	int full_kem)
{
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES];
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t ss[NTRUPLUS_SSBYTES];
	uint8_t decapsulated[NTRUPLUS_SSBYTES];

	reset_randombytes();
	for (size_t i = 0; i < iterations; i++) {
		if (keypair(pk, sk) != 0) {
			fprintf(stderr, "keypair failed at iteration %zu\n", i);
			return 1;
		}
		output_sink = checksum_bytes(pk, sizeof(pk));
		output_sink = checksum_bytes(sk, sizeof(sk));
		if (full_kem != 0) {
			if (crypto_kem_enc(ct, ss, pk) != 0 ||
			    crypto_kem_dec(decapsulated, ct, sk) != 0 ||
			    memcmp(ss, decapsulated, sizeof(ss)) != 0) {
				fprintf(stderr,
					"full KEM failed at iteration %zu\n", i);
				return 1;
			}
			output_sink = checksum_bytes(ct, sizeof(ct));
			output_sink = checksum_bytes(ss, sizeof(ss));
		}
	}
	printf("iterations=%zu checksum=%016llx\n", iterations,
		(unsigned long long)output_sink);
	return 0;
}

enum pack_mode {
	PACK_PRODUCTION,
	PACK_NATIVE_SCALAR,
	PACK_NATIVE_AVX2,
	PACK_NATIVE_L3,
	PACK_NATIVE_CENTERED,
};

static int run_pack_benchmark(size_t iterations, enum pack_mode mode)
{
	uint8_t packed[NTRUPLUS_POLYBYTES];
	poly input;
	poly transformed;

	for (unsigned i = 0; i < NTRUPLUS_N; i++) {
		input.coeffs[i] = (int16_t)((int)(i % 7U) - 3);
	}
	if (mode == PACK_NATIVE_CENTERED) {
		for (unsigned i = 0; i < NTRUPLUS_N; i++) {
			transformed.coeffs[i] = (int16_t)(
				(int)(i % (2U * NTRUPLUS_Q - 1U)) -
				(NTRUPLUS_Q - 1));
		}
	} else if (mode != PACK_PRODUCTION) {
		gt_poly_ntt_lazy(&transformed, &input);
	} else {
		poly_ntt(&transformed, &input);
	}
	for (size_t i = 0; i < iterations; i++) {
		if (mode == PACK_NATIVE_SCALAR) {
			gt_poly_tobytes_native(packed, &transformed);
		} else if (mode == PACK_NATIVE_AVX2) {
#if defined(GT_HAVE_AVX2_ASM) && GT_HAVE_AVX2_ASM
			gt_poly_tobytes_native_asm_avx2(
				packed, &transformed);
#else
			fprintf(stderr, "AVX2 native pack unavailable\n");
			return 1;
#endif
		} else if (mode == PACK_NATIVE_L3) {
#if defined(GT_HAVE_AVX2_ASM) && GT_HAVE_AVX2_ASM
			gt_poly_tobytes_native_l3_asm_avx2(
				packed, &transformed);
#else
			return 1;
#endif
		} else if (mode == PACK_NATIVE_CENTERED) {
#if defined(GT_HAVE_AVX2_ASM) && GT_HAVE_AVX2_ASM
			gt_poly_tobytes_native_centered_asm_avx2(
				packed, &transformed);
#else
			return 1;
#endif
		} else {
			poly_tobytes(packed, &transformed);
		}
	}
	output_sink = checksum_bytes(packed, sizeof(packed));
	printf("iterations=%zu checksum=%016llx\n", iterations,
		(unsigned long long)output_sink);
	return 0;
}

enum component_mode {
	COMPONENT_FORWARD_REF,
	COMPONENT_FORWARD_GT,
	COMPONENT_BASEINV_REF,
	COMPONENT_BASEINV_GT,
	COMPONENT_BASEMUL_REF,
	COMPONENT_BASEMUL_GT,
};

static int prepare_component_inputs(void)
{
	uint32_t state = UINT32_C(0x510e527f);

	for (unsigned set = 0; set < COMPONENT_SETS; set++) {
		unsigned attempts = 0;

		for (;;) {
			for (unsigned i = 0; i < NTRUPLUS_N; i++) {
				int32_t f_value;
				int32_t g_value;

				state ^= state << 13;
				state ^= state >> 17;
				state ^= state << 5;
				f_value = 3 * ((int32_t)(state % 3U) - 1);
				state ^= state << 13;
				state ^= state >> 17;
				state ^= state << 5;
				g_value = 3 * ((int32_t)(state % 3U) - 1);
				component_f[set].coeffs[i] = (int16_t)f_value;
				component_g[set].coeffs[i] = (int16_t)g_value;
			}
			component_f[set].coeffs[0]++;

			poly_ntt(&component_ref_f[set], &component_f[set]);
			poly_ntt(&component_ref_g[set], &component_g[set]);
			gt_poly_ntt_lazy(
				&component_gt_f[set], &component_f[set]);
			gt_poly_ntt_lazy(
				&component_gt_g[set], &component_g[set]);

			if (poly_baseinv(
				    &component_ref_finv[set],
				    &component_ref_f[set]) == 0 &&
			    gt_poly_baseinv_l3(
				    &component_gt_finv[set],
				    &component_gt_f[set]) == 0) {
				break;
			}
			attempts++;
			if (attempts == 4096U) {
				return 1;
			}
		}
	}
	return 0;
}

static int run_component_benchmark(size_t iterations,
	enum component_mode mode)
{
	uint64_t failures = 0;

	if (prepare_component_inputs() != 0) {
		fputs("could not prepare component operands\n", stderr);
		return 1;
	}

	for (unsigned i = 0; i < COMPONENT_WARMUPS; i++) {
		const unsigned set = i & (COMPONENT_SETS - 1U);

		switch (mode) {
		case COMPONENT_FORWARD_REF:
			poly_ntt(&component_ref_output[set],
				&component_f[set]);
			break;
		case COMPONENT_FORWARD_GT:
			gt_poly_ntt_lazy(&component_gt_output[set],
				&component_f[set]);
			break;
		case COMPONENT_BASEINV_REF:
			failures += (uint64_t)poly_baseinv(
				&component_ref_output[set],
				&component_ref_f[set]);
			break;
		case COMPONENT_BASEINV_GT:
			failures += (uint64_t)gt_poly_baseinv_l3(
				&component_gt_output[set],
				&component_gt_f[set]);
			break;
		case COMPONENT_BASEMUL_REF:
			poly_basemul(&component_ref_output[set],
				&component_ref_g[set],
				&component_ref_finv[set]);
			break;
		case COMPONENT_BASEMUL_GT:
			gt_poly_basemul_native(&component_gt_output[set],
				&component_gt_g[set],
				&component_gt_finv[set]);
			break;
		}
	}

	failures = 0;
	for (size_t i = 0; i < iterations; i++) {
		const unsigned set =
			(unsigned)i & (COMPONENT_SETS - 1U);

		switch (mode) {
		case COMPONENT_FORWARD_REF:
			poly_ntt(&component_ref_output[set],
				&component_f[set]);
			break;
		case COMPONENT_FORWARD_GT:
			gt_poly_ntt_lazy(&component_gt_output[set],
				&component_f[set]);
			break;
		case COMPONENT_BASEINV_REF:
			failures += (uint64_t)poly_baseinv(
				&component_ref_output[set],
				&component_ref_f[set]);
			break;
		case COMPONENT_BASEINV_GT:
			failures += (uint64_t)gt_poly_baseinv_l3(
				&component_gt_output[set],
				&component_gt_f[set]);
			break;
		case COMPONENT_BASEMUL_REF:
			poly_basemul(&component_ref_output[set],
				&component_ref_g[set],
				&component_ref_finv[set]);
			break;
		case COMPONENT_BASEMUL_GT:
			gt_poly_basemul_native(&component_gt_output[set],
				&component_gt_g[set],
				&component_gt_finv[set]);
			break;
		}
	}

	for (unsigned set = 0; set < COMPONENT_SETS; set++) {
		const poly *output =
			mode == COMPONENT_FORWARD_GT ||
			mode == COMPONENT_BASEINV_GT ||
			mode == COMPONENT_BASEMUL_GT
			? &component_gt_output[set]
			: &component_ref_output[set];

		output_sink = checksum_bytes(
			(const uint8_t *)(const void *)output,
			sizeof(*output));
	}
	printf("iterations=%zu failures=%llu checksum=%016llx\n",
		iterations, (unsigned long long)failures,
		(unsigned long long)output_sink);
	return failures != 0U;
}

static int parse_iterations(const char *text, size_t *iterations)
{
	char *end = NULL;
	unsigned long long value;

	errno = 0;
	value = strtoull(text, &end, 10);
	if (errno != 0 || end == text || *end != '\0' || value == 0U ||
	    value > (unsigned long long)SIZE_MAX) {
		return 1;
	}
	*iterations = (size_t)value;
	return 0;
}

int main(int argc, char **argv)
{
	size_t iterations = 10000U;

	if (argc == 2 && strcmp(argv[1], "validate") == 0) {
		if (validate_native_pack() != 0 ||
		    validate_keypair_island() != 0) {
			return EXIT_FAILURE;
		}
		return EXIT_SUCCESS;
	}
	if (argc == 3 && parse_iterations(argv[2], &iterations) != 0) {
		fprintf(stderr, "invalid iteration count: %s\n", argv[2]);
		return EXIT_FAILURE;
	}
	if (argc < 2 || argc > 3) {
		fprintf(stderr,
			"usage: %s validate | keygen-ref|keygen-gt|full-ref|full-gt|forward-ref|forward-gt|baseinv-ref|baseinv-gt|basemul-ref|basemul-gt|pack-ref|pack-gt-scalar|pack-gt-avx2|pack-gt-l3|pack-gt-centered [iterations]\n",
			argv[0]);
		return EXIT_FAILURE;
	}
	if (strcmp(argv[1], "keygen-ref") == 0) {
		return run_benchmark(
			crypto_kem_keypair, iterations, 0);
	}
	if (strcmp(argv[1], "keygen-gt") == 0) {
		return run_benchmark(
			crypto_kem_keypair_gt, iterations, 0);
	}
	if (strcmp(argv[1], "full-ref") == 0) {
		return run_benchmark(
			crypto_kem_keypair, iterations, 1);
	}
	if (strcmp(argv[1], "full-gt") == 0) {
		return run_benchmark(
			crypto_kem_keypair_gt, iterations, 1);
	}
	if (strcmp(argv[1], "forward-ref") == 0) {
		return run_component_benchmark(
			iterations, COMPONENT_FORWARD_REF);
	}
	if (strcmp(argv[1], "forward-gt") == 0) {
		return run_component_benchmark(
			iterations, COMPONENT_FORWARD_GT);
	}
	if (strcmp(argv[1], "baseinv-ref") == 0) {
		return run_component_benchmark(
			iterations, COMPONENT_BASEINV_REF);
	}
	if (strcmp(argv[1], "baseinv-gt") == 0) {
		return run_component_benchmark(
			iterations, COMPONENT_BASEINV_GT);
	}
	if (strcmp(argv[1], "basemul-ref") == 0) {
		return run_component_benchmark(
			iterations, COMPONENT_BASEMUL_REF);
	}
	if (strcmp(argv[1], "basemul-gt") == 0) {
		return run_component_benchmark(
			iterations, COMPONENT_BASEMUL_GT);
	}
	if (strcmp(argv[1], "pack-ref") == 0) {
		return run_pack_benchmark(iterations, PACK_PRODUCTION);
	}
	if (strcmp(argv[1], "pack-gt-scalar") == 0) {
		return run_pack_benchmark(iterations, PACK_NATIVE_SCALAR);
	}
	if (strcmp(argv[1], "pack-gt-avx2") == 0) {
		return run_pack_benchmark(iterations, PACK_NATIVE_AVX2);
	}
	if (strcmp(argv[1], "pack-gt-l3") == 0) {
		return run_pack_benchmark(iterations, PACK_NATIVE_L3);
	}
	if (strcmp(argv[1], "pack-gt-centered") == 0) {
		return run_pack_benchmark(iterations, PACK_NATIVE_CENTERED);
	}

	fprintf(stderr, "unknown mode: %s\n", argv[1]);
	return EXIT_FAILURE;
}

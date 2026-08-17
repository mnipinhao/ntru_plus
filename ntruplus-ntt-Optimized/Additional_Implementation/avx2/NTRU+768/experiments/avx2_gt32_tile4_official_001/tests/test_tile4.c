#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tile4.h"
#include "../generated/tile4_basemul_constants.h"
#include "../generated/tile4_serialized_mapping.h"

#define TEST_QINV 12929
#define TEST_RSQ 867

void ntt_gt_rowbitrevlayout(int16_t r[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS]);
int poly_frombytes(int16_t *r, const uint8_t *a);
void poly_tobytes(uint8_t *r, const int16_t *a);

static uint64_t rng_state = UINT64_C(0x6a09e667f3bcc909);

static void fail_at(const char *name, unsigned trial, size_t index,
	int16_t expected, int16_t actual);

static uint32_t random32(void)
{
	rng_state ^= rng_state << 13;
	rng_state ^= rng_state >> 7;
	rng_state ^= rng_state << 17;
	return (uint32_t)rng_state;
}

static int16_t centered(int32_t value)
{
	value %= GT32_TILE4_Q;
	if (value < 0)
		value += GT32_TILE4_Q;
	if (value > GT32_TILE4_Q / 2)
		value -= GT32_TILE4_Q;
	return (int16_t)value;
}

static int16_t test_montgomery(int16_t a, int16_t b)
{
	const int16_t low = (int16_t)(uint16_t)((uint32_t)(uint16_t)a
		* (uint32_t)(uint16_t)b * TEST_QINV);
	return (int16_t)(((int32_t)a * b >> 16)
		- ((int32_t)low * GT32_TILE4_Q >> 16));
}

static void check_basemul_scale(const int16_t *a, const int16_t *b,
	const int16_t *actual, unsigned trial)
{
	for (unsigned tile = 0; tile < GT32_TILE4_TILES; tile++) {
		for (unsigned vector = 0; vector < 8; vector++) {
			for (unsigned lane = 0; lane < 4; lane++) {
				const unsigned base = 128U * tile + 16U * vector + 4U * lane;
				const int64_t lambda = centered(test_montgomery(
					gt32_tile4_lambda_mont[tile][vector][4U * lane], 1));
				for (unsigned c = 0; c < 4; c++) {
					int64_t expected = 0;
					for (unsigned i = 0; i < 4; i++) {
						const unsigned j = (c + 4U - i) & 3U;
						const int64_t factor = i + j >= 4U ? lambda : 1;
						expected += factor * a[base + i] * b[base + j];
					}
					const int16_t want = centered((int32_t)(expected % GT32_TILE4_Q));
					const int16_t got = centered(test_montgomery(
						actual[base + c], TEST_RSQ));
					if (want != got)
						fail_at("basemul-scale-e-minus-1", trial,
							base + c, want, got);
				}
			}
		}
	}
}

static void private_soa_to_tile4(int16_t *out, const int16_t *in)
{
	static const uint8_t q_order[16] = {
		0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15
	};
	uint8_t position[16];
	for (unsigned lane = 0; lane < 16; lane++)
		position[q_order[lane]] = (uint8_t)lane;
	for (unsigned group = 0; group < 12; group++) {
		for (unsigned q = 0; q < 16; q++) {
			for (unsigned c = 0; c < 4; c++)
				out[64U * group + 4U * q + c] =
					in[64U * group + 16U * c + position[q]];
		}
	}
}

static void tile4_to_private_soa(int16_t *out, const int16_t *in)
{
	static const uint8_t q_order[16] = {
		0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15
	};
	uint8_t position[16];
	for (unsigned lane = 0; lane < 16; lane++)
		position[q_order[lane]] = (uint8_t)lane;
	for (unsigned group = 0; group < 12; group++) {
		for (unsigned q = 0; q < 16; q++) {
			for (unsigned c = 0; c < 4; c++)
				out[64U * group + 16U * c + position[q]] =
					in[64U * group + 4U * q + c];
		}
	}
}

static void fail_at(const char *name, unsigned trial, size_t index,
	int16_t expected, int16_t actual)
{
	fprintf(stderr, "%s trial=%u index=%zu expected=%d actual=%d\n",
		name, trial, index, expected, actual);
	exit(1);
}

static void compare_exact(const char *name, unsigned trial,
	const int16_t *expected, const int16_t *actual, size_t words)
{
	for (size_t i = 0; i < words; i++) {
		if (expected[i] != actual[i])
			fail_at(name, trial, i, expected[i], actual[i]);
	}
}

static void compare_mod_q(const char *name, unsigned trial,
	const int16_t *expected, const int16_t *actual, size_t words)
{
	for (size_t i = 0; i < words; i++) {
		if (centered(expected[i]) != centered(actual[i]))
			fail_at(name, trial, i, centered(expected[i]), centered(actual[i]));
	}
}

static void compare_roundtrip(const int16_t *input, const int16_t *actual,
	size_t words, unsigned trial)
{
	for (size_t i = 0; i < words; i++) {
		const int16_t expected = centered(32 * (int32_t)input[i]);
		if (centered(actual[i]) != expected)
			fail_at("roundtrip-mod-q", trial, i, expected, centered(actual[i]));
	}
}

static void compare_parent_rowbitrev(const int16_t *input,
	const int16_t *tile4, unsigned trial)
{
	int16_t parent[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));

	ntt_gt_rowbitrevlayout(parent, input);
	for (unsigned k3 = 0; k3 < 3; k3++) {
		for (unsigned branch = 0; branch < 2; branch++) {
			const unsigned tile = 2U * k3 + branch;
			for (unsigned q = 0; q < 32; q++) {
				const unsigned block = (32U * k3 + 3U * q) % 96U;
				for (unsigned coefficient = 0; coefficient < 4; coefficient++) {
					const size_t tile_word = 128U * tile + 16U * (q / 4U)
						+ 4U * (q % 4U) + coefficient;
					const size_t parent_word = 384U * branch + 4U * block
						+ coefficient;
					const int16_t expected = centered(parent[parent_word]);
					const int16_t actual = centered(tile4[tile_word]);
					if (expected != actual)
						fail_at("frozen-parent", trial, tile_word,
							expected, actual);
				}
			}
		}
	}
}

static void fill_case(int16_t *value, size_t words, unsigned trial)
{
	for (size_t i = 0; i < words; i++) {
		switch (trial) {
		case 0: value[i] = 0; break;
		case 1: value[i] = (i == 0U) ? 1 : 0; break;
		case 2: value[i] = (i & 1U) ? -1728 : 1728; break;
		case 3: value[i] = (int16_t)((int)(i % 8U) - 3); break;
		default: value[i] = (int16_t)((int)(random32() % 3457U) - 1728); break;
		}
	}
}

static int16_t crepmod3_contract(int16_t value)
{
	const int16_t v = 10923;
	value = (int16_t)(value + ((value >> 15) & 3457));
	value = (int16_t)(value - 1729);
	value = (int16_t)(value + ((value >> 15) & 3457));
	value = (int16_t)(value - 1728);
	const int16_t quotient = (int16_t)(((int32_t)v * value + 16384) >> 15);
	return (int16_t)(value - 3 * quotient);
}

static uint16_t canonical_u12(int16_t value)
{
	int32_t result = value % GT32_TILE4_Q;
	if (result < 0)
		result += GT32_TILE4_Q;
	return (uint16_t)result;
}

static void pack_tile4_aos(uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in[GT32_TILE4_POLY_WORDS])
{
	for (unsigned pair = 0; pair < 384; pair++) {
		const uint16_t first = canonical_u12(
			in[gt32_tile4_serialized_to_aos[2U * pair]]);
		const uint16_t second = canonical_u12(
			in[gt32_tile4_serialized_to_aos[2U * pair + 1U]]);
		out[3U * pair] = (uint8_t)first;
		out[3U * pair + 1U] = (uint8_t)((first >> 8)
			| (uint16_t)(second << 4));
		out[3U * pair + 2U] = (uint8_t)(second >> 4);
	}
}

static void compare_crepmod3(const char *label, unsigned trial,
	const int16_t *expected, const int16_t *actual)
{
	for (size_t i = 0; i < GT32_TILE4_POLY_WORDS; i++) {
		if (actual[i] < -5185 || actual[i] > 5185)
			fail_at(label, trial, i, 5185, actual[i]);
		const int16_t want = crepmod3_contract(expected[i]);
		const int16_t got = crepmod3_contract(actual[i]);
		if (want != got)
			fail_at(label, trial, i, want, got);
	}
}

int main(void)
{
	int16_t input[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t ref[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t got[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t inverse_ref[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t inverse_got[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t alias[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t frontend_ref[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t frontend_got[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t frontend_asm[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t full_ref[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t full_got[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t serial_got[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t private_soa[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t semantic_soa[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t general_ref[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t private_inverse[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t private_inverse_asm[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t official_decoded[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	uint8_t packed[GT32_TILE4_SERIALIZED_BYTES];
	uint8_t packed_roundtrip[GT32_TILE4_SERIALIZED_BYTES];

	for (unsigned trial = 0; trial < 1000; trial++) {
		fill_case(input, GT32_TILE4_POLY_WORDS, trial);
		/* Callsite-private e=1 producer/forward and no-repair BM contract. */
		for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++) {
			alias[i] = (int16_t)((int)((i + trial) % 3U) - 1);
			general_ref[i] = (int16_t)(-147 * alias[i]);
		}
		gt32_tile4_frontend_wide_raw_asm(frontend_ref, alias);
		gt32_tile4_frontend_wide_e1_asm(frontend_got, general_ref);
		for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++) {
			const int16_t expected = centered(-147 * (int32_t)frontend_ref[i]);
			if (centered(frontend_got[i]) != expected)
				fail_at("frontend-wide-e1", trial, i, expected,
					centered(frontend_got[i]));
		}
		gt32_tile4_forward_all_pair_asm(full_ref, frontend_ref);
		tile4_to_private_soa(private_soa, full_ref);
		for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++)
			private_soa[i] = centered(-147 * (int32_t)private_soa[i]);
		gt32_tile4_basemul_general_b2_asm(ref, full_ref, full_ref);
		gt32_tile4_basemul_e1_soa_aos_to_aos_asm(got, private_soa,
			full_ref);
		compare_mod_q("basemul-e1-soa-aos-general", trial, ref, got,
			GT32_TILE4_POLY_WORDS);
		if (trial < 100U) {
			pack_tile4_aos(packed, input);
			if (poly_frombytes(official_decoded, packed) != 0
				|| gt32_tile4_frombytes_aos_ref(alias, packed) != 0
				|| gt32_tile4_frombytes_bm_soa_ref(private_soa, packed) != 0
				|| gt32_tile4_frombytes_aos_official_bridge(got, packed) != 0
				|| gt32_tile4_frombytes_bm_soa_official_bridge(general_ref,
					packed) != 0
				|| gt32_tile4_frombytes_aos_asm(full_got, packed) != 0
				|| gt32_tile4_frombytes_bm_soa_semantic_asm(semantic_soa,
					packed) != 0
				|| gt32_tile4_frombytes_bm_soa_aos_control_asm(full_ref,
					packed) != 0) {
				fprintf(stderr, "canonical TILE4 frombytes rejected trial=%u\n", trial);
				return 1;
			}
			for (unsigned serialized = 0; serialized < 768; serialized++) {
				const unsigned aos = gt32_tile4_serialized_to_aos[serialized];
				const unsigned soa = gt32_tile4_serialized_to_bm_soa[serialized];
				const unsigned within = serialized % 128U;
				const unsigned official_word = 128U * (serialized / 128U)
					+ within / 8U + 16U * (within % 8U);
				const int16_t expected = (int16_t)canonical_u12(input[aos]);
				if (alias[aos] != expected)
					fail_at("frombytes-aos", trial, aos, expected, alias[aos]);
				if (got[aos] != expected)
					fail_at("frombytes-aos-bridge", trial, aos, expected, got[aos]);
				if (full_got[aos] != expected)
					fail_at("frombytes-aos-asm", trial, aos, expected, full_got[aos]);
				if (private_soa[soa] != expected)
					fail_at("frombytes-bm-soa", trial, soa, expected,
						private_soa[soa]);
				if (semantic_soa[soa] != expected)
					fail_at("frombytes-bm-soa-semantic-asm", trial, soa,
						expected, semantic_soa[soa]);
				if (general_ref[soa] != expected)
					fail_at("frombytes-bm-soa-bridge", trial, soa, expected,
						general_ref[soa]);
				if (full_ref[soa] != expected)
					fail_at("frombytes-bm-soa-control-asm", trial, soa,
						expected, full_ref[soa]);
				if (official_decoded[official_word] != expected)
					fail_at("frombytes-official", trial, official_word, expected,
						official_decoded[official_word]);
			}
			gt32_tile4_basemul_c3center_late_aos_private_asm(ref, alias, alias);
			gt32_tile4_basemul_scale_soa_aos_to_aos_private_asm(got,
				semantic_soa, alias);
			compare_exact("frombytes-mixed-basemul", trial, ref, got,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(got,
				semantic_soa, semantic_soa);
			compare_exact("frombytes-soa-soa-basemul", trial, ref, got,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_basemul_general_b2_asm(ref, alias, alias);
			gt32_tile4_basemul_general_soa_aos_to_aos_asm(got,
				private_soa, alias);
			compare_exact("frombytes-mixed-general-basemul", trial, ref, got,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_basemul_general_soa_soa_to_aos_asm(got,
				semantic_soa, semantic_soa);
			compare_exact("frombytes-soa-soa-general-basemul", trial, ref, got,
				GT32_TILE4_POLY_WORDS);
			tile4_to_private_soa(general_ref, ref);
			gt32_tile4_basemul_general_soa_soa_to_soa_asm(private_soa,
				semantic_soa, semantic_soa);
			compare_exact("frombytes-soa-soa-general-basemul-soa", trial,
				general_ref, private_soa, GT32_TILE4_POLY_WORDS);
			gt32_tile4_soa_to_official_words_asm(official_decoded,
				semantic_soa);
			poly_tobytes(packed_roundtrip, official_decoded);
			if (memcmp(packed, packed_roundtrip, sizeof packed) != 0) {
				fprintf(stderr,
					"correct-semantic SoA Encodeq mismatch trial=%u\n", trial);
				return 1;
			}
			if (trial == 0U) {
				packed[0] = 0x81U;
				packed[1] = (uint8_t)((packed[1] & 0xf0U) | 0x0dU);
				if (poly_frombytes(official_decoded, packed) != 1
					|| gt32_tile4_frombytes_aos_ref(alias, packed) != 1
					|| gt32_tile4_frombytes_bm_soa_ref(private_soa, packed) != 1
					|| gt32_tile4_frombytes_aos_official_bridge(got, packed) != 1
					|| gt32_tile4_frombytes_bm_soa_official_bridge(general_ref,
						packed) != 1
					|| gt32_tile4_frombytes_aos_asm(full_got, packed) != 1
					|| gt32_tile4_frombytes_bm_soa_semantic_asm(semantic_soa,
						packed) != 1
					|| gt32_tile4_frombytes_bm_soa_aos_control_asm(full_ref,
						packed) != 1) {
					fprintf(stderr, "noncanonical TILE4 frombytes accepted\n");
					return 1;
				}
			}
		}
		gt32_tile4_forward_full_ref(full_ref, input);
		gt32_tile4_inverse_all_ref(inverse_ref, full_ref);
		gt32_tile4_inverse_tail_ref_e0(full_got, inverse_ref);
		compare_mod_q("inverse-tail-e0-roundtrip", trial, input, full_got,
			GT32_TILE4_POLY_WORDS);
		for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++)
			full_ref[i] = centered((int32_t)full_ref[i] * 2775);
		gt32_tile4_inverse_all_ref(inverse_ref, full_ref);
		gt32_tile4_inverse_tail_ref_rminus1(full_got, inverse_ref);
		compare_mod_q("inverse-tail-rminus1-roundtrip", trial, input,
			full_got, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_tail_intrinsic_rminus1(general_ref, inverse_ref);
		compare_exact("inverse-tail-rminus1-intrinsic", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_tail_asm_rminus1(general_ref, inverse_ref);
		compare_exact("inverse-tail-rminus1-asm", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_tail_t1_relaxed_asm(general_ref, inverse_ref);
		compare_mod_q("inverse-tail-t1-relaxed", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("inverse-tail-t1-crepmod3", trial, full_got,
			general_ref);
		gt32_tile4_inverse_tail_t2_one_mont_asm(general_ref, inverse_ref);
		compare_exact("inverse-tail-t2-one-mont", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_tail_t3_reduced_center_asm(general_ref, inverse_ref);
		compare_exact("inverse-tail-t3-reduced-center", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_tail_t4_matrix3_asm(general_ref, inverse_ref);
		compare_exact("inverse-tail-t4-matrix3", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_tail_t3_relaxed_control_asm(general_ref, inverse_ref);
		compare_mod_q("inverse-tail-t3-relaxed-control", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("inverse-tail-t3-relaxed-crepmod3", trial, full_got,
			general_ref);
		gt32_tile4_inverse_tail_champion_private_asm(general_ref, inverse_ref);
		compare_mod_q("inverse-tail-champion-private", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("inverse-tail-champion-crepmod3", trial, full_got,
			general_ref);
		gt32_tile4_inverse_tail_t5_private_asm(general_ref, inverse_ref);
		compare_mod_q("inverse-tail-t5-private", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("inverse-tail-t5-crepmod3", trial, full_got,
			general_ref);
		gt32_tile4_inverse_tail_t6_dual_private_asm(general_ref, inverse_ref);
		compare_mod_q("inverse-tail-t6-dual-private", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("inverse-tail-t6-crepmod3", trial, full_got,
			general_ref);
		gt32_tile4_inverse_tail_t7_triple_private_asm(general_ref, inverse_ref);
		compare_mod_q("inverse-tail-t7-triple-private", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("inverse-tail-t7-crepmod3", trial, full_got,
			general_ref);
		gt32_tile4_inverse_tail_t8_renamed_private_asm(general_ref, inverse_ref);
		compare_mod_q("inverse-tail-t8-renamed-private", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("inverse-tail-t8-crepmod3", trial, full_got,
			general_ref);
		gt32_tile4_inverse_tail_t10_crepmod3_asm(general_ref, inverse_ref);
		for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++) {
			const int16_t expected = crepmod3_contract(full_got[i]);
			if (expected != general_ref[i])
				fail_at("inverse-tail-t10-crepmod3", trial, i,
					expected, general_ref[i]);
		}
		gt32_tile4_inverse_tail_t9_isolated_private_asm(general_ref, inverse_ref);
		compare_mod_q("inverse-tail-t9-isolated-private", trial, full_got,
			general_ref, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("inverse-tail-t9-crepmod3", trial, full_got,
			general_ref);
		gt32_tile4_basemul_b0(ref, input, input);
		gt32_tile4_basemul_b1(got, input, input);
		compare_exact("basemul-b1", trial, ref, got,
			GT32_TILE4_POLY_WORDS);
		check_basemul_scale(input, input, got, trial);
		gt32_tile4_basemul_wide_a1_intrinsic(got, input, input);
		compare_mod_q("basemul-wide-a1", trial, ref, got,
			GT32_TILE4_POLY_WORDS);
		check_basemul_scale(input, input, got, trial);
		gt32_tile4_basemul_k1_intrinsic(got, input, input);
		compare_mod_q("basemul-k1-outer-karatsuba", trial, ref, got,
			GT32_TILE4_POLY_WORDS);
		check_basemul_scale(input, input, got, trial);
		gt32_tile4_basemul_k2_intrinsic(got, input, input);
		compare_mod_q("basemul-k2-full-karatsuba", trial, ref, got,
			GT32_TILE4_POLY_WORDS);
		check_basemul_scale(input, input, got, trial);
		gt32_tile4_basemul_k2_asm(got, input, input);
		compare_mod_q("basemul-k2-asm", trial, ref, got,
			GT32_TILE4_POLY_WORDS);
		check_basemul_scale(input, input, got, trial);
		gt32_tile4_basemul_scale_soa_private_asm(private_soa, input, input);
		private_soa_to_tile4(got, private_soa);
		compare_exact("basemul-scale-private-soa", trial, ref, got,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_basemul_raw_soa_private_asm(alias, input, input);
		private_soa_to_tile4(got, alias);
		compare_mod_q("basemul-raw-private-soa", trial, ref, got,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_soa_private_parallel_asm(private_inverse_asm,
			alias);
		gt32_tile4_inverse_soa_private_ref(private_inverse, private_soa);
		compare_mod_q("raw-bm-to-inverse-private", trial, private_inverse,
			private_inverse_asm, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_soa_private_ref(private_inverse, private_soa);
		gt32_tile4_inverse_soa_private_asm(private_inverse_asm, private_soa);
		compare_exact("inverse-private-soa-asm", trial, private_inverse,
			private_inverse_asm, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_soa_private_parallel_asm(private_inverse_asm,
			private_soa);
		compare_exact("inverse-private-soa-parallel-asm", trial,
			private_inverse, private_inverse_asm, GT32_TILE4_POLY_WORDS);
		memcpy(alias, private_soa, sizeof(alias));
		gt32_tile4_inverse_soa_private_parallel_asm(alias, alias);
		compare_exact("inverse-private-soa-parallel-alias", trial,
			private_inverse, alias, GT32_TILE4_POLY_WORDS);
		private_soa_to_tile4(got, private_inverse);
		gt32_tile4_inverse_all_ref(general_ref, ref);
		compare_exact("inverse-private-soa-ref", trial, general_ref, got,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_basemul_general_b2_asm(got, input, input);
		for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++)
			general_ref[i] = test_montgomery(ref[i], TEST_RSQ);
		compare_mod_q("basemul-general-e0", trial, general_ref, got,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_basemul_b2_asm(got, input, input);
		compare_exact("basemul-b2-asm", trial, ref, got,
			GT32_TILE4_POLY_WORDS);
		check_basemul_scale(input, input, got, trial);
		gt32_tile4_basemul_raw_aos_private_asm(alias, input, input);
		compare_mod_q("basemul-raw-private-aos", trial, ref, alias,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_all_pair_asm(serial_got, alias);
		gt32_tile4_inverse_all_pair_asm(general_ref, got);
		compare_mod_q("raw-bm-to-inverse-aos", trial, general_ref,
			serial_got, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(private_inverse,
			serial_got);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(private_inverse_asm,
			general_ref);
		compare_mod_q("raw-bm-to-t9-aos", trial, private_inverse_asm,
			private_inverse, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("raw-bm-to-t9-crepmod3", trial,
			private_inverse_asm, private_inverse);
		gt32_tile4_basemul_wide_a1_intrinsic(alias, input, input);
		gt32_tile4_inverse_all_pair_asm(serial_got, alias);
		compare_mod_q("wide-a1-bm-to-inverse-aos", trial, general_ref,
			serial_got, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(private_inverse,
			serial_got);
		compare_mod_q("wide-a1-bm-to-t9-aos", trial,
			private_inverse_asm, private_inverse, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("wide-a1-bm-to-t9-crepmod3", trial,
			private_inverse_asm, private_inverse);
		gt32_tile4_inverse_all_pair_selective_asm(serial_got, alias);
		compare_mod_q("raw-bm-to-inverse-aos-selective", trial, general_ref,
			serial_got, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(private_inverse,
			serial_got);
		compare_mod_q("raw-bm-to-t9-aos-selective", trial,
			private_inverse_asm, private_inverse, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("raw-bm-to-t9-selective-crepmod3", trial,
			private_inverse_asm, private_inverse);
		gt32_tile4_basemul_c3center_aos_private_asm(alias, input, input);
		compare_mod_q("basemul-c3center-private-aos", trial, ref, alias,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_all_pair_asm(serial_got, alias);
		compare_mod_q("c3center-bm-to-inverse-aos", trial, general_ref,
			serial_got, GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(private_inverse,
			serial_got);
		compare_mod_q("c3center-bm-to-t9-aos", trial,
			private_inverse_asm, private_inverse, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("c3center-bm-to-t9-crepmod3", trial,
			private_inverse_asm, private_inverse);
		gt32_tile4_basemul_c3center_late_aos_private_asm(alias, input, input);
		compare_mod_q("basemul-c3center-late-private-aos", trial, ref, alias,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_all_pair_asm(serial_got, alias);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(private_inverse,
			serial_got);
		compare_mod_q("c3center-late-bm-to-t9-aos", trial,
			private_inverse_asm, private_inverse, GT32_TILE4_POLY_WORDS);
		compare_crepmod3("c3center-late-bm-to-t9-crepmod3", trial,
			private_inverse_asm, private_inverse);
		gt32_tile4_basemul_b3_late_asm(got, input, input);
		compare_exact("basemul-b3-late-asm", trial, ref, got,
			GT32_TILE4_POLY_WORDS);
		check_basemul_scale(input, input, got, trial);
		gt32_tile4_basemul_b4b_partial_asm(got, input, input);
		compare_exact("basemul-b4b-partial-asm", trial, ref, got,
			GT32_TILE4_POLY_WORDS);
		check_basemul_scale(input, input, got, trial);
		memcpy(alias, input, sizeof(alias));
		gt32_tile4_basemul_b1(alias, alias, alias);
		compare_exact("basemul-b1-alias", trial, ref, alias,
			GT32_TILE4_POLY_WORDS);
		memcpy(alias, input, sizeof(alias));
		gt32_tile4_basemul_wide_a1_intrinsic(alias, alias, alias);
		compare_mod_q("basemul-wide-a1-alias", trial, ref, alias,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_frontend_ref(frontend_ref, input);
		gt32_tile4_frontend_intrinsic(frontend_got, input);
		compare_exact("frontend", trial, frontend_ref, frontend_got,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_frontend_asm(frontend_asm, input);
		compare_exact("frontend-asm", trial, frontend_ref, frontend_asm,
			GT32_TILE4_POLY_WORDS);
		if (trial == 3U) {
			gt32_tile4_frontend_raw_asm(frontend_asm, input);
			compare_mod_q("frontend-raw", trial, frontend_ref, frontend_asm,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_frontend_fixed_raw_asm(frontend_got, input);
			compare_exact("frontend-fixed-vs-raw", trial, frontend_asm,
				frontend_got, GT32_TILE4_POLY_WORDS);
			gt32_tile4_frontend_wide_raw_asm(got, input);
			compare_exact("frontend-wide-vs-fixed", trial, frontend_got, got,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_forward_all_pair_asm(serial_got, frontend_got);
			gt32_tile4_forward_full_fixed_pair_asm(full_got, input);
			compare_exact("full-fixed-pair", trial, serial_got, full_got,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_forward_full_fixed_pair_wide_load_asm(full_got, input);
			compare_exact("full-fixed-pair-wide", trial, serial_got, full_got,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_forward_full_wide_raw_pair_asm(full_got, input);
			compare_exact("full-wide-raw-pair", trial, serial_got, full_got,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_forward_full_wide_raw_pair_align32_asm(full_got, input);
			compare_exact("full-wide-raw-pair-align32", trial, serial_got,
				full_got, GT32_TILE4_POLY_WORDS);
			gt32_tile4_forward_full_wide_raw_pair_align64_asm(full_got, input);
			compare_exact("full-wide-raw-pair-align64", trial, serial_got,
				full_got, GT32_TILE4_POLY_WORDS);
			memcpy(alias, input, sizeof(alias));
			gt32_tile4_forward_full_fixed_pair_asm(alias, alias);
			compare_exact("full-fixed-pair-alias", trial, serial_got, alias,
				GT32_TILE4_POLY_WORDS);
		}

		gt32_tile4_forward_full_ref(full_ref, input);
		gt32_tile4_forward_full_candidate(full_got, input);
		compare_exact("full-forward", trial, full_ref, full_got,
			GT32_TILE4_POLY_WORDS);
		compare_parent_rowbitrev(input, full_got, trial);
		memcpy(alias, input, sizeof(alias));
		gt32_tile4_forward_full_candidate(alias, alias);
		compare_exact("full-forward-alias", trial, full_ref, alias,
			GT32_TILE4_POLY_WORDS);

		gt32_tile4_forward_all_ref(ref, input);
		gt32_tile4_forward_all_asm(got, input);
		compare_exact("forward", trial, ref, got, GT32_TILE4_POLY_WORDS);
		gt32_tile4_forward_all_parallel_asm(serial_got, input);
		compare_exact("forward-parallel", trial, ref, serial_got,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_forward_all_pair_asm(serial_got, input);
		compare_exact("forward-pair", trial, ref, serial_got,
			GT32_TILE4_POLY_WORDS);

		gt32_tile4_inverse_all_ref(inverse_ref, ref);
		gt32_tile4_inverse_all_asm(inverse_got, got);
		compare_exact("inverse", trial, inverse_ref, inverse_got,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_all_pair_asm(serial_got, got);
		compare_exact("inverse-pair", trial, inverse_ref, serial_got,
			GT32_TILE4_POLY_WORDS);
		compare_roundtrip(input, inverse_got, GT32_TILE4_POLY_WORDS, trial);

		memcpy(alias, input, sizeof(alias));
		gt32_tile4_forward_all_asm(alias, alias);
		compare_exact("forward-alias", trial, ref, alias,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_all_asm(alias, alias);
		compare_exact("inverse-alias", trial, inverse_ref, alias,
			GT32_TILE4_POLY_WORDS);
	}

	puts("gt32-tile4: mapping=passed frontend=passed frozen-parent=passed full-forward=passed forward=passed basemul=passed inverse=passed alias=passed roundtrip=passed trials=1000");
	return 0;
}
